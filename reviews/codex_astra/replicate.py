"""Independent Part A. Reads only raw summary files and raw PLACES.

Run from project root: .venv/bin/python reviews/codex_astra/replicate.py
Only writes alongside this file. No Claude implementation/output imports.
"""
from pathlib import Path
import hashlib
import io
import itertools
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TABLES = ["B01001", "B03002", "B15003", "B17024", "B27010"]
SEED = 20261020
FEATURES = (
    [f"age_{x}" for x in ["18_24", "25_34", "35_44", "45_54", "55_64"]]
    + ["female_adult"]
    + [f"race_{x}" for x in ["black", "aian", "asian", "nhpi", "other", "multi", "hispanic"]]
    + ["edu_less_hs", "edu_hs", "edu_some_college", "poverty150_adult"]
)
SELECTED = [("diabetes", "foodinsecu"), ("diabetes", "lacktrpt"),
            ("chd", "csmoking"), ("obesity", "lpa"), ("bphigh", "stroke"),
            ("depression", "loneliness")]


def read_counties(table):
    path = ROOT / "data/raw/acs_sf" / f"acsdt5y2023-{table.lower()}.dat"
    # Filter literal county GEO_ID prefix before parsing large all-geography files.
    with path.open() as f:
        header = next(f)
        lines = [line for line in f if line.startswith("0500000US")]
    df = pd.read_csv(io.StringIO(header + "".join(lines)), sep="|", dtype={"GEO_ID": str})
    df["countyfips"] = df.GEO_ID.str[-5:]
    assert not df.countyfips.duplicated().any()
    df = df.set_index("countyfips")
    keep = [c for c in df if c.startswith(f"{table}_E")]
    df = df[keep].apply(pd.to_numeric, errors="coerce")
    # Negative ACS special codes are missing, never legitimate count estimates.
    df = df.mask(df < 0)
    df.to_csv(HERE / f"{table}_county_estimates.csv")
    return df


def build_covariates():
    tables = {t: read_counties(t) for t in TABLES}
    d = pd.DataFrame(index=tables["B01001"].index)
    mapping = []

    def count(table, cells):
        return tables[table][[f"{table}_E{i:03}" for i in cells]].sum(axis=1, min_count=len(cells))

    def share(name, table, numerator, denominator, universe):
        d[name] = count(table, numerator) / count(table, denominator).replace(0, np.nan)
        mapping.append(dict(variable=name, table=table,
                            numerator=",".join(f"{i:03}" for i in numerator),
                            denominator=",".join(f"{i:03}" for i in denominator),
                            universe=universe))

    male = list(range(7, 26))
    female = list(range(31, 50))
    adult = male + female
    d["adult_population"] = count("B01001", adult)
    d["total_population"] = count("B01001", [1])
    bands = {"18_24": list(range(7, 11)), "25_34": [11, 12],
             "35_44": [13, 14], "45_54": [15, 16], "55_64": [17, 18, 19],
             "65_plus": list(range(20, 26))}
    for name, cells in bands.items():
        share(f"age_{name}", "B01001", cells + [i + 24 for i in cells], adult, "18+")
        # Joint age-sex shares, saved for a feasible richer-model sensitivity.
        share(f"male_age_{name}", "B01001", cells, adult, "18+")
        share(f"female_age_{name}", "B01001", [i + 24 for i in cells], adult, "18+")
    share("female_adult", "B01001", female, adult, "18+")
    for name, cell in zip(["white", "black", "aian", "asian", "nhpi", "other", "multi", "hispanic"],
                          [3, 4, 5, 6, 7, 8, 9, 12]):
        share("race_" + name, "B03002", [cell], [1], "All ages; non-Hispanic except Hispanic")
    for name, cells in {"less_hs": list(range(2, 17)), "hs": [17, 18],
                        "some_college": [19, 20, 21], "ba_plus": [22, 23, 24, 25]}.items():
        share("edu_" + name, "B15003", cells, [1], "25+")
    age_totals = [41, 54, 67, 80, 93, 106, 119]
    poor = [i + j for i in age_totals for j in range(1, 6)]
    d["poverty_universe_adult"] = count("B17024", age_totals)
    share("poverty150_adult", "B17024", poor, age_totals, "18+ with poverty status determined")
    d["insurance_universe_19_64"] = count("B27010", [18, 34])
    d["uninsured_count_19_64"] = count("B27010", [33, 50])
    share("acs_uninsured_19_64", "B27010", [33, 50], [18, 34],
          "Civilian noninstitutionalized population 19-64")
    # Keep the benchmark in percentage points, as with PLACES.
    d["acs_uninsured_19_64"] *= 100
    for cols in [[f"age_{b}" for b in bands],
                 [f"race_{r}" for r in ["white", "black", "aian", "asian", "nhpi", "other", "multi", "hispanic"]],
                 [f"edu_{e}" for e in ["less_hs", "hs", "some_college", "ba_plus"]]]:
        assert np.allclose(d[cols].sum(axis=1, min_count=len(cols)).dropna(), 1)
    assert d[FEATURES].dropna().ge(0).all().all()
    assert d[FEATURES].dropna().le(1).all().all()
    pd.DataFrame(mapping).to_csv(HERE / "variable_mapping.csv", index=False)
    d.to_csv(HERE / "covariates.csv")
    return d.reset_index()


def design(df, features=FEATURES, state=True):
    # All state indicators and no intercept span the ordinary intercept + FE space.
    c = df[features].to_numpy(float)
    c = (c - c.mean(0)) / np.where(c.std(0) > 0, c.std(0), 1)
    s = pd.get_dummies(df.stateabbr, dtype=float).to_numpy() if state else np.ones((len(df), 1))
    return np.column_stack([s, c]), s.shape[1]


def r2(y, pred):
    return 1 - np.sum((y - pred) ** 2, axis=0) / np.sum((y - y.mean(axis=0)) ** 2, axis=0)


def fold_ids(n, seed=SEED):
    ids = np.empty(n, dtype=int)
    for k, idx in enumerate(np.array_split(np.random.default_rng(seed).permutation(n), 10)):
        ids[idx] = k
    return ids


def regression(df, ys, features=FEATURES, state=True):
    x, ns = design(df, features, state)
    y = df[ys].to_numpy(float)
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    fit = x @ beta
    resid = y - fit
    assert np.max(np.abs(x.T @ resid)) < 1e-6
    ids = fold_ids(len(df))
    oof = np.empty_like(y)
    folds, unseen = [], []
    for k in range(10):
        tr, te = ids != k, ids == k
        # Scaling on all data is an invertible reparameterization of unpenalized
        # OLS. Refitting train scaling is unnecessary and cannot change predictions.
        b, _, train_rank, _ = np.linalg.lstsq(x[tr], y[tr], rcond=None)
        pred = x[te] @ b
        missing_state = x[tr, :ns].sum(0) == 0
        bad = x[te, :ns][:, missing_state].sum(1) > 0
        if np.any(bad):
            # No state coefficient is identifiable for a singleton state (DC).
            # Prespecified fallback: training-population-of-counties weighted
            # mean state intercept, plus the fitted covariate contribution.
            intercept = np.average(b[:ns], axis=0, weights=x[tr, :ns].sum(0))
            pred[bad] += intercept
            unseen.extend(df.loc[te].loc[bad, "countyfips"].tolist())
        oof[te] = pred
        scores = r2(y[te], pred)
        for j, measure in enumerate(ys):
            folds.append(dict(measure=measure, fold=k, n_train=int(tr.sum()),
                              n_test=int(te.sum()), train_rank=int(train_rank), r2=float(scores[j])))
    ins, cv = r2(y, fit), r2(y, oof)
    records = []
    for j, measure in enumerate(ys):
        records.append(dict(measure=measure, n=len(df), design_columns=x.shape[1],
                            rank=int(rank), residual_df=len(df)-int(rank),
                            r2_in_sample=float(ins[j]), r2_cv_pooled=float(cv[j]),
                            r2_cv_mean_fold=float(np.mean([z["r2"] for z in folds if z["measure"] == measure])),
                            cv_unseen_state_count=len(unseen)))
    return records, resid, fit, oof, folds, ids


def pair_stats(y, e, fit):
    raw = np.corrcoef(y.T)[0, 1]
    partial = np.corrcoef(e.T)[0, 1]
    raw_cov = np.cov(y.T, ddof=1)[0, 1]
    residual_cov = np.cov(e.T, ddof=1)[0, 1]
    fitted_cov = np.cov(fit.T, ddof=1)[0, 1]
    assert abs(raw_cov - residual_cov - fitted_cov) < 1e-8
    return dict(raw_r=float(raw), partial_r=float(partial),
                raw_covariance=float(raw_cov), residual_covariance=float(residual_cov),
                covariance_share_remaining=float(residual_cov/raw_cov) if abs(raw_cov) > 1e-12 else np.nan,
                fitted_covariance=float(fitted_cov))


def main():
    cov = build_covariates()
    p = pd.read_csv(ROOT / "data/raw/places_county_2025.csv", dtype={"countyfips": str})
    p.countyfips = p.countyfips.str.zfill(5)
    assert not p.countyfips.duplicated().any()
    audit = p[["countyfips", "stateabbr", "countyname"]].merge(cov, on="countyfips", how="outer",
                                                              validate="one_to_one", indicator=True)
    audit[["countyfips", "stateabbr", "countyname", "_merge"]].to_csv(HERE / "join_audit.csv", index=False)
    d = p.merge(cov, on="countyfips", how="left", validate="one_to_one").sort_values("countyfips").reset_index(drop=True)
    d.to_csv(HERE / "analysis_data.csv", index=False)
    measures = sorted(c for c in p if c.endswith(("_crudeprev", "_adjprev")))
    assert len(measures) == 80
    validx = d[FEATURES].notna().all(axis=1)
    patterns = {}
    for m in measures:
        mask = (validx & d[m].notna()).to_numpy()
        patterns.setdefault(mask.tobytes(), (mask, []))[1].append(m)
    rows, folds, predictions = [], [], []
    for mask, ms in patterns.values():
        sub = d.loc[mask].reset_index(drop=True)
        rr, e, fitted, oof, ff, ids = regression(sub, ms)
        rows.extend(rr); folds.extend(ff)
        for j, m in enumerate(ms):
            predictions.append(pd.DataFrame(dict(countyfips=sub.countyfips, measure=m, observed=sub[m],
                                                 fitted=fitted[:, j], residual=e[:, j], oof_prediction=oof[:, j],
                                                 cv_fold=ids)))
    pd.DataFrame(rows).to_csv(HERE / "measure_r2.csv", index=False)
    pd.DataFrame(folds).to_csv(HERE / "cv_folds.csv", index=False)
    pd.concat(predictions).to_csv(HERE / "predictions.csv", index=False)
    # Fit each outcome on each intersection sample once, then form pair statistics.
    cache = {}
    pairs = []
    for suffix in ["crudeprev", "adjprev"]:
        ms = [m for m in measures if m.endswith("_" + suffix)]
        for a, b in itertools.combinations(ms, 2):
            mask = (validx & d[a].notna() & d[b].notna()).to_numpy()
            key = mask.tobytes()
            if key not in cache:
                sub = d.loc[mask]
                available = [m for m in measures if sub[m].notna().all()]
                x, _ = design(sub)
                y = sub[available].to_numpy(float)
                beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
                cache[key] = (available, y, y-x@beta, x@beta, rank)
            available, y, e, fitted, rank = cache[key]
            idx = [available.index(a), available.index(b)]
            pairs.append(dict(kind=suffix, measure_a=a.removesuffix("_"+suffix),
                              measure_b=b.removesuffix("_"+suffix), n=int(mask.sum()), rank=int(rank),
                              residual_df=int(mask.sum()-rank),
                              **pair_stats(y[:, idx], e[:, idx], fitted[:, idx])))
    pairdf = pd.DataFrame(pairs)
    pairdf.to_csv(HERE / "pair_correlations.csv", index=False)
    selected = pairdf[(pairdf.kind == "adjprev") & pairdf.apply(
        lambda r: any({r.measure_a, r.measure_b} == set(pair) for pair in SELECTED), axis=1)]
    selected.to_csv(HERE / "selected_pairs.csv", index=False)
    assert len(selected) == 6 and len(pairdf) == 1560
    benchmarks = []
    for threshold in [0, 20000]:
        sub = d[validx & d[["acs_uninsured_19_64", "access2_crudeprev"]].notna().all(axis=1)
                & (d.adult_population >= threshold)].reset_index(drop=True)
        ys = ["access2_crudeprev", "acs_uninsured_19_64"]
        rr, e, fitted, oof, ff, ids = regression(sub, ys)
        stats = pair_stats(sub[ys].to_numpy(float), e, fitted)
        benchmarks.append(dict(adult_threshold=threshold, n=len(sub), **stats,
                               **{f'{r["measure"]}_{k}': r[k] for r in rr
                                  for k in ["r2_in_sample", "r2_cv_pooled", "r2_cv_mean_fold"]}))
        pd.DataFrame(ff).to_csv(HERE / f"benchmark_cv_folds_{threshold}.csv", index=False)
    pd.DataFrame(benchmarks).to_csv(HERE / "benchmark.csv", index=False)
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), seed=SEED,
                   features=FEATURES, places_counties=len(p), acs_counties=len(cov),
                   complete_covariates=int(validx.sum()),
                   unmatched_places=audit.loc[audit._merge == "left_only", "countyfips"].tolist(),
                   covariate_missing_counties=d.loc[~validx, "countyfips"].tolist(),
                   outcome_missing={m: int(d[m].isna().sum()) for m in measures},
                   cv_definition="1-SSE(all held-out predictions)/SST(full analysis sample); 10 shuffled folds",
                   covariance_share="cov(residual_a,residual_b)/cov(observed_a,observed_b), same pairwise sample and n-1 divisor",
                   adult_cutoff_source="ACS B01001 adult_population, not PLACES population",
                   pair_counts=pairdf.groupby("kind").size().to_dict())
    (HERE / "part_a_summary.json").write_text(json.dumps(summary, indent=2))
    # Freeze the independent artifacts BEFORE any Part B inspection.
    files = [HERE / "replicate.py"] + sorted(HERE.glob("*.csv")) + sorted(HERE.glob("*metadata.json"))
    manifest = {str(f.relative_to(HERE)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    (HERE / "PART_A_FROZEN.json").write_text(json.dumps(
        dict(frozen_utc=datetime.now(timezone.utc).isoformat(), files_sha256=manifest), indent=2))
    print(json.dumps(summary, indent=2))
    print(pd.DataFrame(rows).groupby(pd.DataFrame(rows).measure.str.endswith("_adjprev"))[
        ["r2_in_sample", "r2_cv_pooled"]].median().to_string())
    print(pd.DataFrame(benchmarks).to_string(index=False))
    print(selected.to_string(index=False))


if __name__ == "__main__":
    main()
