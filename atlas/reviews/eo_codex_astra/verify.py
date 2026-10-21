"""Final result integrity checks, independent scoring from saved predictions."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd
from replicate import HERE,ROOT

frozen=json.loads((HERE/"PART_A_FROZEN.json").read_text())
frozen_checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen["hashes"].items()}
assert all(frozen_checks.values())
reviewed=json.loads((HERE/"reviewed_sources.json").read_text())
reviewed_checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in reviewed["sha256"].items()}
snapshot_checks={p:hashlib.sha256((HERE/"reviewed_snapshot"/p.split("/")[-1]).read_bytes()).hexdigest()==h for p,h in reviewed["sha256"].items()}
assert all(snapshot_checks.values())
old_metrics=pd.read_csv(HERE/"reviewed_snapshot/places_vs_observed.csv").set_index(["outcome","sample"])
now_metrics=pd.read_csv(ROOT/"outputs/expected_vs_observed/places_vs_observed.csv").set_index(["outcome","sample"])
pd.testing.assert_frame_equal(old_metrics,now_metrics.loc[old_metrics.index,old_metrics.columns])
old_residuals=pd.read_csv(HERE/"reviewed_snapshot/observed_minus_expected_by_county.csv",dtype={"fips":str}).set_index("fips")
now_residuals=pd.read_csv(ROOT/"outputs/expected_vs_observed/observed_minus_expected_by_county.csv",dtype={"fips":str}).set_index("fips")
for col in old_residuals.columns:
    pd.testing.assert_series_equal(old_residuals[col].dropna().sort_index(),
                                   now_residuals[col].dropna().sort_index())
current_snap=HERE/"current_scope_recheck"
current_snap.mkdir(exist_ok=True)
for name in ["scripts/expected_vs_observed.py","outputs/expected_vs_observed/places_vs_observed.csv",
             "outputs/expected_vs_observed/observed_minus_expected_by_county.csv"]:
    (current_snap/Path(name).name).write_bytes((ROOT/name).read_bytes())

r=pd.read_csv(HERE/"independent_results.csv")
p=pd.read_csv(HERE/"independent_predictions.csv",dtype={"fips":str})
keys=["source","condition","measure","fltr","places_type","sample"]
assert len(r)==112 and not r.duplicated(keys).any()
errors=[]
for key,d in p.groupby(keys):
    mask=np.ones(len(r),bool)
    for col,v in zip(keys,key): mask &= r[col].eq(v)
    row=r[mask].iloc[0]
    assert len(d)==row.n and not d.fips.duplicated().any()
    assert set(d.fold)==set(range(10))
    y=d.observed.to_numpy()
    sst=np.dot(y-y.mean(),y-y.mean())
    for pred,stat in [("expected_oof","cv_demo"),("places_oof","cv_places"),("augmented_oof","cv_both")]:
        e=y-d[pred].to_numpy()
        errors.append(abs(1-np.dot(e,e)/sst-row[stat]))
    assert np.max(np.abs(d.residual_oof-(d.observed-d.expected_oof)))<1e-10
    assert abs(row.gain-(row.cv_both-row.cv_demo))<1e-10
assert max(errors)<1e-12
assert (r.cv_demo>r.cv_places).all()

c=pd.read_csv(HERE/"matched_spec_checks.csv")
rc=pd.read_csv(HERE/"saved_residual_checks.csv")
assert len(c)==238 and c.matched_error.abs().max()<1e-9
assert rc.n.sum()==49778 and rc.max_abs_error.max()<1e-8
acs=pd.read_csv(HERE/"acs_live_checks.csv")
assert len(acs)==6 and (acs.n==3222).all() and acs.max_abs_error.max()<1e-10
cms=pd.read_csv(HERE/"cms_denominator_categories.csv",dtype={"fips":str})
m=pd.read_csv(ROOT/"data/raw/mmd_prevalence_2023.csv",dtype={"fips":str})
x=cms.merge(m,on=["fips","fltr"],suffixes=("_live","_original"))
x=x[x.condition_name.eq(x.condition)]
assert len(x)==71302 and (x.rate_live==x.rate_original).all()
text=(HERE/"REPORT.md").read_text()
assert "\u2014" not in text
partc=text.split("## Part C:")[1].split("## Verdict")[0]
assert len(re.findall(r"(?m)^[1-8]\. \*\*",partc))==8
assert "## Shortcuts taken" in text
assert not re.search(r"turn\d+(search|view)",text)
checks=dict(
    checked_utc=datetime.now(timezone.utc).isoformat(),
    part_a_hashes_unchanged=frozen_checks,
    reviewed_snapshots_match=snapshot_checks,
    current_reviewed_sources_still_match=reviewed_checks,
    current_requested_17_pairs_and_residuals_unchanged=True,
    independent_result_rows=len(r),independent_prediction_rows=len(p),
    max_independent_rescore_error=max(errors),
    claude_matched_cells=len(c),claude_max_statistic_error=c.matched_error.abs().max(),
    claude_residual_cells=int(rc.n.sum()),claude_max_residual_error=rc.max_abs_error.max(),
    acs_rates_verified=int(acs.n.sum()),cms_rates_verified=len(x),
    non_rounding_differences=len(pd.read_csv(HERE/"disagreements_beyond_rounding.csv")),
    methods_findings=8,report_words=len(text.split()),
    report_sha256=hashlib.sha256(text.encode()).hexdigest())
(HERE/"final_verification.json").write_text(json.dumps(checks,indent=2))
print(json.dumps({k:v for k,v in checks.items() if not isinstance(v,dict)},indent=2))
