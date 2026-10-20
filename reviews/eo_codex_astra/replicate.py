"""Independent analysis. Writes only to this review folder. No Claude imports."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FEATURES = (
    [f"age_{x}" for x in ["18_24", "25_34", "35_44", "45_54", "55_64"]]
    + ["female_adult"]
    + [f"race_{x}" for x in ["black", "aian", "asian", "nhpi", "other", "multi", "hispanic"]]
    + ["edu_less_hs", "edu_hs", "edu_some_college", "poverty150_adult"]
)
SEED = 20261020

def read(path, key):
    d = pd.read_csv(ROOT / path, dtype={key: str}).rename(columns={key: "fips"})
    d.fips = d.fips.str.zfill(5)
    return d

def load():
    c = read("reviews/codex_astra/covariates.csv", "countyfips")
    p = read("data/raw/places_county_2025.csv", "countyfips")
    g = read("data/raw/medicare_gv_county_2023.csv", "fips")
    a = read("data/raw/acs_disability_2023.csv", "fips")
    m = read("data/raw/mmd_prevalence_2023.csv", "fips")
    for d in [c, p, g, a]:
        assert not d.fips.duplicated().any()
    assert not m.duplicated(["fips", "condition", "fltr"]).any()
    for col in ["BENES_OM_CNT", "BENES_MA_CNT", "BENES_TOTAL_CNT"]:
        g[col] = pd.to_numeric(g[col], errors="coerce")
    # Do not impute suppressed counts as zero.
    g["ma_share"] = g.BENES_MA_CNT / (g.BENES_MA_CNT + g.BENES_OM_CNT)
    base = p.merge(c, on="fips", validate="one_to_one")
    base = base.merge(g, on="fips", how="left", validate="one_to_one")
    base = base.merge(a, on="fips", how="left", validate="one_to_one")
    base = base.sort_values("fips").reset_index(drop=True)
    return base, m

def folds(n, seed=SEED):
    f = np.empty(n, int)
    for k, idx in enumerate(np.array_split(np.random.default_rng(seed).permutation(n), 10)):
        f[idx] = k
    return f

def design(d, features, state=True):
    v = d[features].to_numpy(float)
    v = (v-v.mean(0)) / np.where(v.std(0)>0, v.std(0), 1)
    s = pd.get_dummies(d.stateabbr, dtype=float).to_numpy() if state else np.ones((len(d), 1))
    return np.column_stack([s, v]), s.shape[1]

def fit_cv(x, y, ids, ns, state=True):
    y = np.asarray(y)
    beta, _, rank, _ = np.linalg.lstsq(x, y, rcond=None)
    fit = x @ beta
    pred = np.empty_like(y)
    for k in range(10):
        tr, te = ids != k, ids == k
        b = np.linalg.lstsq(x[tr], y[tr], rcond=None)[0]
        if state:
            missing = x[tr, :ns].sum(0) == 0
            b[:ns][missing] = np.average(b[:ns], axis=0, weights=x[tr, :ns].sum(0))
        pred[te] = x[te] @ b
    r2 = 1 - ((y-pred)**2).sum(axis=0) / ((y-y.mean(axis=0))**2).sum(axis=0)
    return r2, y-fit, pred, rank

def evaluate(d, features, seed=SEED):
    ids = folds(len(d), seed)
    y = d.observed.to_numpy(float)
    x, ns = design(d, features)
    b, e, oof, rank = fit_cv(x, y, ids, ns)
    xp, _ = design(d, ["places"], state=False)
    p, _, poof, _ = fit_cv(xp, y, ids, 1, state=False)
    xb, ns = design(d, features + ["places"])
    both, _, boof, _ = fit_cv(xb, y, ids, ns)
    _, ep, _, _ = fit_cv(x, d.places.to_numpy(float), ids, ns)
    x0, ns0 = design(d, FEATURES)
    _, e0, _, _ = fit_cv(x0, d[["observed", "places"]].to_numpy(float), ids, ns0)
    result = dict(n=len(d), raw_r=np.corrcoef(y, d.places)[0,1],
                  cv_demo=float(b), cv_places=float(p), cv_both=float(both),
                  gain=float(both-b), partial_r=np.corrcoef(e, ep)[0,1],
                  partial_r_no_ma=np.corrcoef(e0.T)[0,1], rank=rank,
                  rmse_demo=float(np.mean((y-oof)**2)**.5),
                  rmse_both=float(np.mean((y-boof)**2)**.5))
    predictions = pd.DataFrame(dict(fips=d.fips, fold=ids, observed=y, places=d.places,
                                   expected_oof=oof, augmented_oof=boof,
                                   places_oof=poof, residual_oof=y-oof))
    return result, predictions

def panels(base, m):
    pairs = m.dropna(subset=["places_measure"])[["condition", "places_measure"]].drop_duplicates()
    assert len(pairs) == 11
    for row in pairs.itertuples(index=False):
        for fltr in [1,2]:
            obs = m.loc[(m.condition==row.condition)&(m.fltr==fltr), ["fips","rate"]].rename(columns={"rate":"observed"})
            # 0 is a UI no-data code, verified separately from the CMS client.
            obs.observed = obs.observed.where(obs.observed>0)
            for typ in ["crudeprev","adjprev"]:
                d = base.merge(obs, on="fips", validate="one_to_one")
                d["places"] = d[f"{row.places_measure}_{typ}"]
                for sample, limit in [("all",0), ("large",5000)]:
                    valid = d[FEATURES+["ma_share","observed","places"]].notna().all(axis=1)
                    if limit:
                        valid &= d.BENES_OM_CNT.ge(limit)
                    sub = d.loc[valid].reset_index(drop=True)
                    key = dict(source="Medicare", condition=row.condition, measure=row.places_measure,
                               fltr=fltr, places_type=typ, sample=sample)
                    yield key, sub, FEATURES+["ma_share"]
    for measure in ["hearing","vision","cognition","mobility","selfcare","indeplive"]:
        for typ in ["crudeprev","adjprev"]:
            d = base.copy()
            d["observed"], d["places"] = d[f"acs_{measure}"], d[f"{measure}_{typ}"]
            for sample, limit in [("all",0), ("large",20000)]:
                valid = d[FEATURES+["observed","places"]].notna().all(axis=1) & d.adult_population.ge(limit)
                yield dict(source="ACS", condition=measure, measure=measure, fltr=0,
                           places_type=typ, sample=sample), d.loc[valid].reset_index(drop=True), FEATURES

def main():
    base, m = load()
    results, predictions = [], []
    for key, d, features in panels(base, m):
        stats, pred = evaluate(d, features)
        results.append({**key, **stats})
        predictions.append(pred.assign(**key))
    result = pd.DataFrame(results)
    assert len(result) == 112
    result.to_csv(HERE/"independent_results.csv", index=False)
    pd.concat(predictions, ignore_index=True).to_csv(HERE/"independent_predictions.csv", index=False)
    m.groupby(["condition","fltr"]).rate.agg(n="size", zeros=lambda s: s.eq(0).sum(),
                                            min="min", max="max").to_csv(HERE/"raw_rate_audit.csv")
    pd.DataFrame({"mmd_only_fips":sorted(set(m.fips)-set(base.fips))}).to_csv(HERE/"mmd_unmatched_fips.csv",index=False)
    paths = [HERE/"replicate.py", HERE/"independent_results.csv", HERE/"independent_predictions.csv"]
    paths += [ROOT/p for p in ["reviews/codex_astra/covariates.csv","data/raw/places_county_2025.csv",
              "data/raw/medicare_gv_county_2023.csv","data/raw/mmd_prevalence_2023.csv",
              "data/raw/acs_disability_2023.csv"]]
    (HERE/"PART_A_FROZEN.json").write_text(json.dumps(dict(
        frozen_utc=datetime.now(timezone.utc).isoformat(), seed=SEED, result_rows=len(result),
        excluded_scripts_unopened=True, features=FEATURES,
        hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2))
    print(result[(result.places_type=="crudeprev")&(result.fltr<2)].to_string(index=False))

if __name__ == "__main__":
    main()
