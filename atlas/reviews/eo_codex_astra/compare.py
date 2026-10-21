"""Post-freeze independent matched-specification audit, no Claude execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd
from replicate import HERE, ROOT, FEATURES, load, panels, evaluate

LABELS = dict(diabetes="Diabetes", copd="COPD", depression="Depression",
              hypertension="High blood pressure", ischemic_heart_disease="Coronary heart disease",
              stroke_tia="Stroke", asthma="Asthma", obesity="Obesity", arthritis="Arthritis",
              hyperlipidemia="High cholesterol", cancer_4_sites="Cancer",
              hearing="Hearing disability", vision="Vision disability", cognition="Cognitive disability",
              mobility="Mobility disability", selfcare="Self-care disability",
              indeplive="Independent-living disability")
METRICS = dict(n="n", raw_r="r_raw", cv_demo="cv_r2_demo", cv_places="cv_r2_places",
               cv_both="cv_r2_demo_places", gain="gain", partial_r="partial_r")
MATCHED = (
    ["age_25_34","age_35_44","age_45_54","age_55_64","age_65_74","age_75p","female_adult"]
    + ["race_black","race_aian","race_asian","race_nhpi","race_other_multi","race_hispanic"]
    + ["edu_less_hs","edu_some_college","edu_ba_plus","poverty150_adult"]
)

def matched_base(base):
    age = pd.read_csv(ROOT/"reviews/codex_astra/B01001_county_estimates.csv",
                      dtype={"countyfips":str}).rename(columns={"countyfips":"fips"})
    # Raw-derived sums, not Claude's derived age columns.
    age["age_65_74_count"] = age[[f"B01001_E{i:03}" for i in [20,21,22,44,45,46]]].sum(axis=1)
    b = base.merge(age[["fips","age_65_74_count"]],on="fips",validate="one_to_one")
    b["age_65_74"] = b.age_65_74_count/b.adult_population
    b["age_75p"] = b.age_65_plus-b.age_65_74
    b["race_other_multi"] = b.race_other+b.race_multi
    return b

def selected(key):
    return ((key["source"]=="Medicare" and key["fltr"]==2 and key["places_type"]=="adjprev")
            or (key["source"]=="ACS" and key["places_type"]=="crudeprev"))

def main():
    sources = [ROOT/"scripts/expected_vs_observed.py", ROOT/"scripts/fetch_observed_outcomes.py"]
    sources += list((ROOT/"outputs/expected_vs_observed").glob("*.csv"))
    snap = HERE/"reviewed_snapshot"
    snap.mkdir(exist_ok=True)
    for s in sources:
        (snap/s.name).write_bytes(s.read_bytes())
    (HERE/"reviewed_sources.json").write_text(json.dumps(dict(
        read_utc=datetime.now(timezone.utc).isoformat(),
        sha256={str(s.relative_to(ROOT)):hashlib.sha256(s.read_bytes()).hexdigest() for s in sources}),indent=2))
    base, m = load()
    b = matched_base(base)
    primary = pd.read_csv(HERE/"independent_results.csv")
    claude = pd.read_csv(snap/"places_vs_observed.csv").set_index(["outcome","sample"])
    cr = pd.read_csv(snap/"observed_minus_expected_by_county.csv",dtype={"fips":str}).set_index("fips")
    comparisons, discrepancies, checks, residual_checks = [], [], [], []
    for key, d, _ in panels(b, m):
        if not selected(key):
            continue
        features = MATCHED+(["ma_share"] if key["source"]=="Medicare" else [])
        result, pred = evaluate(d, features)
        c = claude.loc[(LABELS[key["condition"]], "larger" if key["sample"]=="large" else "all")]
        mask = np.ones(len(primary),bool)
        for k,v in key.items():
            mask &= primary[k].eq(v)
        own = primary.loc[mask].iloc[0]
        row = {**key, "outcome":LABELS[key["condition"]]}
        for metric, cm in METRICS.items():
            delta = float(own[metric]-c[cm])
            row.update({metric+"_independent":own[metric], metric+"_claude":c[cm],
                        metric+"_matched":result[metric]})
            checks.append({**key, "metric":metric, "matched_error":result[metric]-c[cm]})
            if abs(delta)>(0 if metric=="n" else .0005):
                discrepancies.append({**key, "metric":metric, "independent":own[metric],
                    "claude":c[cm], "difference":delta,
                    "cause":"age65+ split vs combined; other and multiracial separate vs combined"})
        comparisons.append(row)
        if key["sample"]=="all":
            col = ("mc_" if key["source"]=="Medicare" else "acs_")+key["condition"]
            saved = cr[col].dropna()
            new = pred.set_index("fips").residual_oof
            assert set(saved.index)==set(new.index)
            residual_checks.append(dict(condition=key["condition"], n=len(new),
                                       max_abs_error=float((new-saved).abs().max())))
    pd.DataFrame(comparisons).to_csv(HERE/"comparison.csv",index=False)
    pd.DataFrame(discrepancies).to_csv(HERE/"disagreements_beyond_rounding.csv",index=False)
    ck = pd.DataFrame(checks)
    ck.to_csv(HERE/"matched_spec_checks.csv",index=False)
    rc = pd.DataFrame(residual_checks)
    rc.to_csv(HERE/"saved_residual_checks.csv",index=False)
    assert ck.matched_error.abs().max()<1e-9
    assert rc.max_abs_error.max()<1e-8
    print("matched cells",len(ck),"max error",ck.matched_error.abs().max())
    print("residuals",rc.n.sum(),"max error",rc.max_abs_error.max())
    print(pd.DataFrame(discrepancies).groupby("metric").size())

if __name__=="__main__":
    main()
