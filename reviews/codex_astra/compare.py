"""Part B: run ONLY after PART_A_FROZEN.json exists. Writes only here.

Uses AST to load Claude's function definitions, without running its top-level
output-writing code. Independently recomputes on common pair samples.
"""
import ast
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from replicate import HERE, ROOT, FEATURES, design, regression, pair_stats

FROZEN = json.loads((HERE / "PART_A_FROZEN.json").read_text())
assert all(hashlib.sha256((HERE / f).read_bytes()).hexdigest() == h
           for f, h in FROZEN["files_sha256"].items())
SOURCE = ROOT / "outputs/covariate_test"
source_paths = [ROOT / "scripts/fetch_acs_county.py", ROOT / "scripts/covariate_test.py",
                ROOT / "data/raw/acs_county_2023.csv"] + sorted(SOURCE.glob("*"))
source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in source_paths if p.is_file()}

places = pd.read_csv(ROOT / "data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places.countyfips.str.zfill(5)
acs = pd.read_csv(ROOT / "data/raw/acs_county_2023.csv", dtype={"fips": str})
df = places.merge(acs, on="fips", how="inner", validate="one_to_one")
states = pd.get_dummies(df.stateabbr, prefix="st", drop_first=True, dtype=float)
measures = [c.removesuffix("_adjprev") for c in places if c.endswith("_adjprev")]
tree = ast.parse((ROOT / "scripts/covariate_test.py").read_text())
nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
         or (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "COMPOSITION"
                                                 for t in node.targets))]
env = dict(np=np, pd=pd, itertools=itertools, df=df, states=states, MEASURES=measures)
exec(compile(ast.Module(body=nodes, type_ignores=[]), "claude_definitions_readonly", "exec"), env)
composition = env["COMPOSITION"]

# Independently construct every original covariate from frozen raw-derived inputs.
owncov = pd.read_csv(HERE / "covariates.csv", dtype={"countyfips": str}).set_index("countyfips")
age = pd.read_csv(HERE / "B01001_county_estimates.csv", dtype={"countyfips": str}).set_index("countyfips")
derived = {}
for c in ["18_24", "25_34", "35_44", "45_54", "55_64"]:
    derived["age_"+c] = owncov["age_"+c]
derived["age_65_74"] = age[[f"B01001_E{i:03}" for i in [20, 21, 22, 44, 45, 46]]].sum(axis=1) / owncov.adult_population
derived["age_75p"] = age[[f"B01001_E{i:03}" for i in [23, 24, 25, 47, 48, 49]]].sum(axis=1) / owncov.adult_population
derived["male"] = 1-owncov.female_adult
derived["adults"] = owncov.adult_population
for c in ["white", "black", "aian", "asian", "nhpi"]:
    derived["nh_"+c] = owncov["race_"+c]
derived["nh_other_multi"] = owncov.race_other + owncov.race_multi
derived["hispanic"] = owncov.race_hispanic
for old, new in {"edu_lt_hs": "edu_less_hs", "edu_hs": "edu_hs",
                 "edu_some_college": "edu_some_college", "edu_ba_plus": "edu_ba_plus",
                 "pov150_adults": "poverty150_adult"}.items():
    derived[old] = owncov[new]
derived["acs_uninsured_19_64"] = owncov.acs_uninsured_19_64 / 100
derived = pd.DataFrame(derived)
acsi = acs.set_index("fips").sort_index()
covcheck = []
for c in acsi:
    difference = (acsi[c] - derived[c]).abs()
    covcheck.append(dict(variable=c, n=len(difference), max_abs_difference=difference.max(),
                         disagreements_above_1e_12=int((difference > 1e-12).sum())))
pd.DataFrame(covcheck).to_csv(HERE / "covariate_comparison.csv", index=False)
assert set(acsi.index) == set(derived.index)
assert max(r["max_abs_difference"] for r in covcheck) < 1e-12

own = pd.read_csv(HERE / "analysis_data.csv", dtype={"countyfips": str})
own_r2 = pd.read_csv(HERE / "measure_r2.csv").set_index("measure")
own_pairs = pd.read_csv(HERE / "pair_correlations.csv")
disagreements, reproduction_checks, comparisons, attribution, bench = [], [], [], [], []
audit_rank = []


def cell(file, key, metric, independent, claude, cause, tolerance=.0005000001):
    if abs(independent-claude) > tolerance:
        disagreements.append(dict(file=file, key=key, metric=metric, independent=independent,
                                  claude=claude, delta=independent-claude, cause=cause))


for kind in ["adjprev", "crudeprev"]:
    original_r2, original_pairs, original_resid = env["analyse"](kind)
    original_r2.to_csv(HERE / f"claude_reproduced_r2_{kind}.csv", index=False)
    original_pairs.to_csv(HERE / f"claude_reproduced_pairs_{kind}.csv", index=False)
    sr = pd.read_csv(SOURCE / f"r2_by_measure_{kind}.csv").set_index("measure")
    sp = pd.read_csv(SOURCE / f"pairs_{kind}.csv").set_index(["a", "b"])
    for m, row in original_r2.set_index("measure").iterrows():
        for metric in sr.columns:
            reproduction_checks.append(dict(file=f"r2_by_measure_{kind}.csv", key=m, metric=metric,
                                             abs_difference=abs(row[metric]-sr.loc[m, metric])))
        o = own_r2.loc[f"{m}_{kind}"]
        for metric, original_metric in [("n", "n_counties"), ("r2_in_sample", "inputs_plus_state"),
                                        ("r2_cv_pooled", "inputs_plus_state_cv")]:
            cell(f"r2_by_measure_{kind}.csv", m, original_metric, o[metric], sr.loc[m, original_metric],
                 "Age/race grouping" if metric != "r2_cv_pooled"
                 else "Age/race grouping; CV seed and unseen-state treatment",
                 tolerance=0 if metric == "n" else .0005000001)
        comparisons.append(dict(kind=kind, measure=m, independent_r2=o.r2_in_sample,
                                claude_r2=row.inputs_plus_state, independent_cv=o.r2_cv_pooled,
                                claude_cv=row.inputs_plus_state_cv))
        rows = df.index[df[f"{m}_{kind}"].notna()]
        X = env["design"](rows)
        rank = np.linalg.matrix_rank(X.to_numpy())
        audit_rank.append(dict(kind=kind, measure=m, n=len(rows), columns=X.shape[1],
                               rank=rank, residual_df=len(rows)-rank,
                               partial_correlation_test_df_if_used=len(rows)-rank-1))
    cache = {}
    op = own_pairs[own_pairs.kind == kind].copy()
    op["key"] = op.apply(lambda r: "|".join(sorted([r.measure_a, r.measure_b])), axis=1)
    op = op.set_index("key")
    for _, row in original_pairs.iterrows():
        a, b = row.a, row.b
        pair_key = "|".join(sorted([a, b]))
        for metric in ["n", "raw_r", "partial_r", "share_beyond_inputs"]:
            reproduction_checks.append(dict(file=f"pairs_{kind}.csv", key=pair_key, metric=metric,
                                             abs_difference=abs(row[metric]-sp.loc[(a,b), metric])))
        columns = [f"{m}_{kind}" for m in [a, b]]
        rows = df.index[df[columns].notna().all(axis=1)]
        key = tuple(rows)
        if key not in cache:
            X = env["design"](rows).to_numpy()
            avail = [m for m in measures if df.loc[rows, f"{m}_{kind}"].notna().all()]
            Y = df.loc[rows, [f"{m}_{kind}" for m in avail]].to_numpy(float)
            B = np.linalg.lstsq(X, Y, rcond=None)[0]
            cache[key] = (avail, Y, Y-X@B, X@B)
        avail, Y, E, F = cache[key]
        idx = [avail.index(a), avail.index(b)]
        corrected = pair_stats(Y[:,idx], E[:,idx], F[:,idx])
        # Direct covariance of Claude's existing residuals on the intersection:
        # isolates the cross-sample variance-scaling error from the refit effect.
        r_old = np.column_stack([original_resid[m].loc[rows] for m in [a,b]])
        direct_old_share = np.cov(r_old.T)[0,1] / np.cov(Y[:,idx].T)[0,1]
        attribution.append(dict(kind=kind, pair=pair_key, n=len(rows),
                                raw_r=row.raw_r,
                                claude_partial=row.partial_r,
                                common_sample_partial=corrected["partial_r"],
                                independent_partial=op.loc[pair_key, "partial_r"],
                                partial_refit_effect=corrected["partial_r"]-row.partial_r,
                                partial_grouping_effect=op.loc[pair_key,"partial_r"]-corrected["partial_r"],
                                claude_share=row.share_beyond_inputs,
                                original_residual_direct_share=direct_old_share,
                                common_sample_share=corrected["covariance_share_remaining"],
                                independent_share=op.loc[pair_key,"covariance_share_remaining"],
                                share_scaling_error=row.share_beyond_inputs-direct_old_share,
                                share_refit_effect=corrected["covariance_share_remaining"]-direct_old_share))
        for metric, original_metric in [("n", "n"), ("raw_r", "raw_r"), ("partial_r", "partial_r"),
                                        ("covariance_share_remaining", "share_beyond_inputs")]:
            mixed = len(original_resid[a]) != len(original_resid[b])
            cause = "Age/race grouping"
            if mixed and metric == "partial_r":
                cause += "; Claude does not refit both outcomes on their intersection sample"
            if mixed and metric == "covariance_share_remaining":
                cause += "; cross-sample R2 scaling and no pairwise refit"
            cell(f"pairs_{kind}.csv", pair_key, original_metric, op.loc[pair_key,metric],
                 sp.loc[(a,b),original_metric], cause, tolerance=0 if metric == "n" else .0005000001)

ob = pd.read_csv(HERE / "benchmark.csv")
sb = pd.read_csv(SOURCE / "benchmark_uninsurance.csv").set_index("sample")
for label, threshold in [("all counties", 0), (">=20k adults", 20000)]:
    rows = df.index[(df.adults > 0 if threshold == 0 else df.adults >= threshold)
                    & df.access2_crudeprev.notna() & df.acs_uninsured_19_64.notna()]
    x = env["design"](rows)
    yp, ya = df.loc[rows,"access2_crudeprev"], df.loc[rows,"acs_uninsured_19_64"]*100
    rp, r2p = env["resid_r2"](yp,x); ra, r2a = env["resid_r2"](ya,x)
    original = dict(n=len(rows),raw_r=np.corrcoef(yp,ya)[0,1],partial_r=np.corrcoef(rp,ra)[0,1],
                    r2_places_on_inputs=r2p,r2_acs_direct_on_inputs=r2a,
                    cv_r2_places=env["cv_r2"](yp,x), cv_r2_acs_direct=env["cv_r2"](ya,x))
    bench.append(dict(sample=label, **original))
    oo = ob[ob.adult_threshold == threshold].iloc[0]
    mapping = {"n":"n","raw_r":"raw_r","partial_r":"partial_r",
               "r2_places_on_inputs":"access2_crudeprev_r2_in_sample",
               "r2_acs_direct_on_inputs":"acs_uninsured_19_64_r2_in_sample",
               "cv_r2_places":"access2_crudeprev_r2_cv_pooled",
               "cv_r2_acs_direct":"acs_uninsured_19_64_r2_cv_pooled"}
    for metric, ourmetric in mapping.items():
        reproduction_checks.append(dict(file="benchmark_uninsurance.csv", key=label, metric=metric,
                                         abs_difference=abs(original[metric]-sb.loc[label,metric])))
        cell("benchmark_uninsurance.csv", label, metric, oo[ourmetric], sb.loc[label, metric],
             "Age/race grouping" + ("; CV seed and unseen-state treatment" if metric.startswith("cv") else ""),
             tolerance=0 if metric == "n" else .0005000001)

pd.DataFrame(disagreements).to_csv(HERE / "numeric_disagreements.csv", index=False)
pd.DataFrame(comparisons).to_csv(HERE / "r2_comparison.csv", index=False)
pd.DataFrame(attribution).to_csv(HERE / "pair_disagreement_attribution.csv", index=False)
pd.DataFrame(bench).to_csv(HERE / "claude_reproduced_benchmark.csv", index=False)
pd.DataFrame(audit_rank).to_csv(HERE / "rank_audit.csv", index=False)
checks = pd.DataFrame(reproduction_checks)
checks.to_csv(HERE / "claude_output_reproduction_checks.csv", index=False)
assert checks.abs_difference.max() <= .0005000001
assert all(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h for f,h in source_hashes.items())
(HERE / "reviewed_source_hashes.json").write_text(json.dumps(source_hashes, indent=2))
print("All source numeric tables reproduced within rounding:", checks.shape, checks.abs_difference.max())
print("Independent discrepancies exceeding +/- .0005:", len(disagreements))
print(pd.DataFrame(disagreements).groupby(["file","metric"]).size().to_string())
att = pd.DataFrame(attribution)
for k,g in att.groupby("kind"):
    print(k,"max partial refit effect",g.partial_refit_effect.abs().max(),
          "max share scaling error",g.share_scaling_error.abs().max())
print(pd.DataFrame(bench).to_string(index=False))
