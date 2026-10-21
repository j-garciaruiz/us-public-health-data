"""Focused read-only audit; every write is confined to this review directory."""
import ast
import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CAUSE = {"GR113-046": "diabetes", "GR113-054": "heart",
         "GR113-070": "stroke", "GR113-082": "clrd"}
NAMES = {"diabetes": "Diabetes deaths", "heart": "Heart disease deaths",
         "stroke": "Cerebrovascular deaths", "clrd": "Chronic lower respiratory deaths"}
results = {}


def read(path, **kw):
    return pd.read_csv(ROOT / path, **kw)


def wonder(path):
    text = (ROOT / path).read_text().split('"---"')[0]
    return pd.read_csv(io.StringIO(text), sep="\t", dtype=str).dropna(how="all")


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=lambda x: x.item() if hasattr(x, "item") else str(x)) + "\n")


files = [p for p in (ROOT / "outputs").rglob("*") if p.is_file()]
inputs = files + [ROOT / p for p in (
    "scripts/build_atlas_data.py", "scripts/build_mortality_smr.py",
    "scripts/fetch_observed_outcomes.py", "data/raw/wonder_county_smr.csv",
    "data/raw/acs_disability_2023.csv", "data/raw/acs_county_2023.csv",
    "data/raw/medicare_gv_county_2023.csv", "data/raw/mmd_prevalence_2023.csv",
    "data/raw/places_county_2025.csv", "data/raw/wonder/county_cause_2018_2024.txt",
    "data/raw/wonder/national_age_2018_2024.txt", "data/raw/acs_sf/acsdt5y2023-b01001.dat")]
manifest = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size,
             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]
dump("input_manifest.json", manifest)

ct = wonder("data/raw/wonder/county_cause_2018_2024.txt")
nt = wonder("data/raw/wonder/national_age_2018_2024.txt")
ct["fips"] = ct["County Code"].replace({"02270": "02158", "46113": "46102"})
ct["cause"] = ct["UCD - ICD-10 113 Cause List Code"].map(CAUSE)
ct["deaths"] = pd.to_numeric(ct.Deaths, errors="coerce")
ct["py"] = pd.to_numeric(ct.Population, errors="coerce")
ct = ct.dropna(subset=["cause"])
nt["cause"] = nt["UCD - ICD-10 113 Cause List Code"].map(CAUSE)
nt["deaths"] = pd.to_numeric(nt.Deaths, errors="coerce")
nt["pop"] = pd.to_numeric(nt.Population, errors="coerce")
smr = read("data/raw/wonder_county_smr.csv", dtype={"fips": str})
atlas = read("outputs/atlas/atlas_county_long.csv", dtype={"fips": str})
summary = read("outputs/atlas/atlas_summary.csv")
small = ct[ct.deaths.isna() | ct.deaths.le(9)][["fips", "cause"]]
joined = small.merge(smr, on=["fips", "cause"])
bad_raw = int(joined.smr.notna().sum())
am = atlas[atlas.layer.eq("mortality")].copy()
am["cause"] = am.outcome.map({v: k for k, v in NAMES.items()})
bad_atlas = len(am.merge(small, on=["fips", "cause"]))
legacy = read("outputs/expected_vs_observed/observed_minus_expected_by_county.csv", dtype={"fips": str})
legacy_leaks = {}
for cause in NAMES:
    candidates = [c for c in legacy if c == "smr_" + cause]
    for col in candidates:
        rows = legacy[legacy.fips.isin(small.loc[small.cause.eq(cause), "fips"])]
        legacy_leaks[col] = int(rows[col].notna().sum())
results["suppression"] = {"raw_rows_checked": len(joined), "raw_smr_violations": bad_raw,
                          "atlas_violations": bad_atlas, "legacy_columns": list(legacy.columns),
                          "legacy_leaks": legacy_leaks,
                          "output_files": [str(p.relative_to(ROOT)) for p in files]}

# Reconstruct the complete expected-death calculation independently.
sf = read("data/raw/acs_sf/acsdt5y2023-b01001.dat", sep="|", dtype=str)
sf = sf[sf.GEO_ID.str.startswith("0500000US")].copy()
sf.index = sf.GEO_ID.str[-5:]
cells = [[3], [4, 5], [6, 7, 8, 9, 10], [11, 12], [13, 14],
         [15, 16], [17, 18, 19], [20, 21, 22], [23, 24], [25]]
ages = np.column_stack([sf[[f"B01001_E{i:03}" for i in cc + [x + 24 for x in cc]]].astype(float).sum(axis=1) for cc in cells])
shares = pd.DataFrame(ages / ages.sum(axis=1)[:, None], index=sf.index)
codes = [["1", "1-4"], ["5-14"], ["15-24"], ["25-34"], ["35-44"],
         ["45-54"], ["55-64"], ["65-74"], ["75-84"], ["85+"]]
reconciliations = []
for cause in NAMES:
    nn = nt[nt.cause.eq(cause) & nt["Ten-Year Age Groups Code"].ne("NS")]
    rr = [nn[nn["Ten-Year Age Groups Code"].isin(cc)] for cc in codes]
    rates = np.array([r.deaths.sum() / r["pop"].sum() for r in rr])
    sub = ct[ct.cause.eq(cause) & ct.fips.isin(sf.index) & ct.py.notna()].copy()
    base = shares.loc[sub.fips].values @ rates * sub.py.values
    unmatched = ct[ct.cause.eq(cause) & ~ct.fips.isin(sf.index)]
    target = nn.deaths.sum() - unmatched.deaths.sum()
    expected = pd.Series(base * target / base.sum(), index=sub.fips)
    saved = smr[smr.cause.eq(cause)].set_index("fips")
    reconciliations.append({
        "cause": cause, "matched_counties": len(saved), "national_known_age_numeric_sum": nn.deaths.sum(),
        "national_suppressed_age_cells": int(nn.deaths.isna().sum()),
        "unmatched_all_age_deaths": unmatched.deaths.sum(),
        "unmatched_suppressed_cells": int(unmatched.deaths.isna().sum()),
        "target": target, "saved_expected_sum": saved.expected.sum(),
        "scale": target / base.sum(),
        "max_expected_error": (saved.expected - expected).abs().max(),
        "unmatched_fips": ",".join(sorted(unmatched.fips.unique())),
        "raw_numeric_max_smr_error": (saved.smr - saved.observed / expected).abs().max()})
pd.DataFrame(reconciliations).to_csv(OUT / "mortality_reconciliation.csv", index=False)
results["mapping"] = {"new_codes_rows": smr.fips.isin(["02158", "46102"]).sum(),
                      "old_codes_rows": smr.fips.isin(["02270", "46113"]).sum(),
                      "ct_or_valdez_rows": (smr.fips.str.startswith("09") | smr.fips.eq("02261")).sum(),
                      "max_expected_error": max(x["max_expected_error"] for x in reconciliations)}

acs = read("data/raw/acs_county_2023.csv", dtype={"fips": str}).set_index("fips")
places = read("data/raw/places_county_2025.csv", dtype={"countyfips": str}).set_index("countyfips")
states = places.stateabbr
dis = read("data/raw/acs_disability_2023.csv", dtype={"fips": str}).set_index("fips")
gv = read("data/raw/medicare_gv_county_2023.csv", dtype={"fips": str}).set_index("fips")
mmd = read("data/raw/mmd_prevalence_2023.csv", dtype={"fips": str})
om = pd.to_numeric(gv.BENES_OM_CNT, errors="coerce")
ma = pd.to_numeric(gv.BENES_MA_CNT, errors="coerce")
extra = ma / (ma + om)
features = ["age_25_34", "age_35_44", "age_45_54", "age_55_64", "age_65_74", "age_75p",
            "male", "nh_black", "nh_aian", "nh_asian", "nh_nhpi", "nh_other_multi",
            "hispanic", "edu_lt_hs", "edu_some_college", "edu_ba_plus", "pov150_adults"]
label = {"diabetes": "Diabetes", "copd": "COPD", "depression": "Depression",
         "hypertension": "Hypertension", "ischemic_heart_disease": "Ischemic heart disease",
         "stroke_tia": "Stroke or TIA", "asthma": "Asthma", "obesity": "Obesity (recorded)",
         "arthritis": "Rheumatoid arthritis or osteoarthritis", "hyperlipidemia": "Hyperlipidemia (recorded)",
         "cancer_4_sites": "Cancer: breast, colorectal, prostate or lung",
         "chronic_kidney_disease": "Chronic kidney disease"}
dislabel = dict(zip(["hearing", "vision", "cognition", "mobility", "selfcare", "indeplive"],
                   ["Hearing difficulty", "Vision difficulty", "Cognitive difficulty",
                    "Ambulatory difficulty", "Self-care difficulty", "Independent-living difficulty"]))
bands = {1: (11, 499), 2: (500, 999), 3: (1000, 4999), 4: (5000, 9999), 5: (10000, np.inf)}
specs = []
for flt, layer in [(1, "medicare_actual"), (2, "medicare_std")]:
    for cond, rows in mmd[mmd.fltr.eq(flt) & mmd.rate.gt(0)].groupby("condition"):
        rows = rows.set_index("fips")
        lower = rows.dencat.map(lambda b: bands[b][0])
        upper = rows.dencat.map(lambda b: bands[b][1])
        n = np.minimum(np.maximum(om.reindex(rows.index).fillna(lower), lower), upper)
        specs.append((layer, label[cond], rows.rate, n, rows.dencat))
for key, name in dislabel.items():
    specs.append(("acs", name, dis["acs_" + key].dropna(), dis["acs_" + key + "_moe"], None))
for cause, name in NAMES.items():
    s = smr[smr.cause.eq(cause) & smr.smr.notna()].set_index("fips")
    specs.append(("mortality", name, s.smr * 100, s.expected, None))


def independent_predict(y, medicare, within):
    ix = y.index.intersection(acs.index).intersection(states.index)
    x = acs.loc[ix, features].copy()
    if medicare:
        x["ma_share"] = extra.reindex(ix)
    x = x.dropna()
    st = states.loc[x.index]
    # Independent equivalent parameterization: demean within training states,
    # then estimate common slopes; use weighted mean intercept for unseen states.
    xx, yy = x.to_numpy(), y.loc[x.index].to_numpy()
    rng = np.random.default_rng(20261020)
    predictions, seen = [], []
    fallback = 0
    for repeat in range(10):
        perm = rng.permutation(len(yy))
        pred = np.full(len(yy), np.nan)
        counts = np.zeros(len(yy), int)
        for test in np.array_split(perm, 10):
            train = np.flatnonzero(~np.isin(np.arange(len(yy)), test))
            assert not np.intersect1d(train, test).size
            xtr, ytr = xx[train], yy[train]
            if within:
                train_states = st.iloc[train].to_numpy()
                unique = np.unique(train_states)
                xm = {s: xtr[train_states == s].mean(axis=0) for s in unique}
                ym = {s: ytr[train_states == s].mean() for s in unique}
                xd = xtr - np.stack([xm[s] for s in train_states])
                yd = ytr - np.array([ym[s] for s in train_states])
                beta = np.linalg.lstsq(xd, yd, rcond=None)[0]
                intercept = {s: ym[s] - xm[s] @ beta for s in unique}
                mean_intercept = np.mean([intercept[s] for s in train_states])
                pred[test] = xx[test] @ beta + [intercept.get(s, mean_intercept) for s in st.iloc[test]]
                fallback += sum(s not in intercept for s in st.iloc[test])
            else:
                beta = np.linalg.lstsq(np.column_stack([np.ones(len(train)), xtr]), ytr, rcond=None)[0]
                pred[test] = beta[0] + xx[test] @ beta[1:]
            counts[test] += 1
        assert (counts == 1).all()
        predictions.append(pred)
        seen.append(counts)
    return pd.Series(np.mean(predictions, axis=0), index=x.index), np.std(predictions, axis=0, ddof=1), fallback


checks, shrinkrows, fallbacks, bounds, summarychecks = [], [], [], [], []
for layer, outcome, y, precision, band in specs:
    for mode in ["national", "within_state"]:
        pred, split_sd, fallback = independent_predict(y, layer.startswith("medicare"), mode == "within_state")
        saved = atlas[atlas.layer.eq(layer) & atlas.outcome.eq(outcome) & atlas["mode"].eq(mode)].set_index("fips")
        assert set(saved.index) == set(pred.index), (layer, outcome, mode, "support")
        saved = saved.loc[pred.index]
        obs = y.loc[pred.index]
        if layer.startswith("medicare"):
            s2 = obs * (100 - obs) / precision.reindex(pred.index) + 1 / 12
            correct_note = "CMS band " + band.reindex(pred.index).astype(int).astype(str) + ", approx n " + precision.reindex(pred.index).round().astype(int).astype(str)
            assert (saved.reliability_note == correct_note).all()
        elif layer == "acs":
            s2 = (precision.reindex(pred.index) / 1.645) ** 2
        else:
            s2 = 100 * pred.clip(lower=1) / precision.reindex(pred.index)
        assert np.isfinite(s2).all() and s2.gt(0).all()
        r = obs - pred
        w = 1 / s2
        center = np.average(r, weights=w)
        c = w.sum() - np.square(w).sum() / w.sum()
        tau_code = max(0, (np.dot(w, r ** 2) - (len(r) - 1)) / c)
        tau_dl = max(0, (np.dot(w, (r - center) ** 2) - (len(r) - 1)) / c)
        lam_code = tau_code / (tau_code + s2)
        lam_dl = tau_dl / (tau_dl + s2)
        tier = lambda v: np.where(v >= .75, 1, np.where(v >= .40, 2, 3))
        ss = summary[summary.layer.eq(layer) & summary.outcome.eq(outcome) & summary["mode"].eq(mode)].iloc[0]
        metrics = {"counties": len(pred), "ky_pa": int(states.loc[pred.index].isin(["KY", "PA"]).sum()),
                   "sd_raw": r.std(), "sd_shrunk": (lam_code * r).std(), "tau": np.sqrt(tau_code),
                   "tier1": int((tier(lam_code) == 1).sum()), "tier3": int((tier(lam_code) == 3).sum())}
        for metric, value in metrics.items():
            summarychecks.append(dict(layer=layer, outcome=outcome, mode=mode, metric=metric,
                                      calculated=value, saved=ss[metric], error=abs(value-ss[metric])))
        checks.append(dict(layer=layer, outcome=outcome, mode=mode, n=len(pred),
                           ky_pa=int(states.loc[pred.index].isin(["KY", "PA"]).sum()),
                           expected_max_error=float((saved.expected - pred).abs().max()),
                           observed_max_error=float((saved.observed - obs).abs().max()),
                           reliability_max_error=float((saved.reliability - lam_code).abs().max()),
                           shrunk_max_error=float((saved.difference_shrunk - lam_code * r).abs().max()),
                           tier_errors=int((saved.tier != tier(lam_code)).sum()),
                           fallback_count=fallback, max_split_sd=float(max(split_sd))))
        shrinkrows.append(dict(layer=layer, outcome=outcome, mode=mode, weighted_residual_mean=center,
                               tau2_code=tau_code, tau2_DL=tau_dl,
                               inflation_percent=100 * (tau_code / tau_dl - 1) if tau_dl else np.nan,
                               tier_changes=int((tier(lam_dl) != tier(lam_code)).sum()),
                               max_lambda_change=float((lam_code - lam_dl).abs().max())))
        for fips in pred.index[(pred < 0) | ((pred > 100) & (layer != "mortality"))]:
            bounds.append(dict(layer=layer, outcome=outcome, mode=mode, fips=fips,
                               expected=pred[fips], observed=obs[fips], reliability=lam_code[fips],
                               difference_shrunk=(r * lam_code)[fips]))
        if mode == "within_state":
            for st, rows in r.groupby(states.loc[r.index]):
                fallbacks.append(dict(layer=layer, outcome=outcome, state=st, n=len(rows), mean_difference=rows.mean()))
    print(f"Checked {layer}: {outcome}", flush=True)
pd.DataFrame(checks).to_csv(OUT / "atlas_replication_checks.csv", index=False)
pd.DataFrame(shrinkrows).to_csv(OUT / "dl_comparison.csv", index=False)
pd.DataFrame(bounds).to_csv(OUT / "out_of_bounds_expectations.csv", index=False)
pd.DataFrame(fallbacks).to_csv(OUT / "within_state_means.csv", index=False)
pd.DataFrame(summarychecks).to_csv(OUT / "summary_replication_checks.csv", index=False)

# Execute only function definitions, never the script's top-level mutations.
module = ast.parse((ROOT / "scripts/build_atlas_data.py").read_text())
namespace = {"np": np, "pd": pd}
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in ["shrink", "cross_fit", "design"]], type_ignores=[]), "<audited-functions>", "exec"), namespace)
unit_tau = namespace["shrink"](pd.Series([5., 5., 5.]), pd.Series([0., 0., 0.]), pd.Series([1., 1., 1.]))[-1]
results["shrink_unit_constant_residual"] = {"implemented_tau2": unit_tau, "standard_DL_tau2": 0.}
# A singleton alphabetical first state exercises the old omitted-reference bug.
toy_ix = pd.Index([f"{i:05}" for i in range(30)])
toy_x = pd.DataFrame({"x": np.linspace(-2, 2, 30)}, index=toy_ix)
toy_st = pd.Series(["AK"] + ["CA"] * 14 + ["TX"] * 15, index=toy_ix)
toy_y = 2 * toy_x.x + toy_st.map({"AK": 99., "CA": 3., "TX": 7.})
namespace.update(acs=toy_x, state=toy_st, COMPOSITION=["x"], REPEATS=10, FOLDS=10, SEED=20261020)
toy_pred = namespace["cross_fit"](toy_y, within_state=True)
perturbed = toy_y.copy()
perturbed.iloc[0] += 1000
toy_pred2 = namespace["cross_fit"](perturbed, within_state=True)
results["unseen_state_unit"] = {"singleton_prediction_unchanged_after_own_y_changed":
                                bool(abs(toy_pred.iloc[0] - toy_pred2.iloc[0]) < 1e-9),
                                "has_intercept": "const" in namespace["design"](toy_ix, None, True).columns,
                                "all_state_dummy_columns": [c for c in namespace["design"](toy_ix, None, True).columns if c.startswith("st_")]}
results["atlas"] = {"rows": len(atlas), "specifications": len(checks),
                    "duplicates": int(atlas.duplicated(["fips", "layer", "outcome", "mode"]).sum()),
                    "max_expected_error": max(c["expected_max_error"] for c in checks),
                    "max_reliability_error": max(c["reliability_max_error"] for c in checks),
                    "max_shrunk_error": max(c["shrunk_max_error"] for c in checks),
                    "tier_errors": sum(c["tier_errors"] for c in checks),
                    "tier_changes_DL": sum(c["tier_changes"] for c in shrinkrows),
                    "out_of_bounds": len(bounds)}
dump("verification_results.json", results)
changed = [m["path"] for m in manifest if hashlib.sha256((ROOT / m["path"]).read_bytes()).hexdigest() != m["sha256"]]
dump("input_changes_during_review.json", changed)
print(json.dumps(results["atlas"], indent=2), flush=True)
