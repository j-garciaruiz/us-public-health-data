"""How much of the PLACES county correlations survive after removing the model's inputs?

PLACES builds every measure from the same ingredients: age, sex,
race/ethnicity, education, county poverty (<150% FPL) and state/county random
effects. Two measures built from the same ingredients will correlate across
counties even if nothing else links them (Kong & Zhang 2020, AJPH).

Test: regress each PLACES measure on county versions of those inputs plus
state fixed effects. Report how much of each measure's county-to-county
variation the inputs reproduce (in-sample and 10-fold cross-validated R2),
and, for every pair of measures, the correlation of the residuals (partial r)
and the share of the raw covariance left in the residuals, both computed on
the counties the two measures share.

What this shows, and what it does not (see atlas/reviews/codex_astra/REPORT.md):
it measures how far the PUBLISHED estimates can be reconstructed from
demographics plus state. It does not show that the underlying health
relationships are spurious, that demographics alone explain the state
component, or what the residual is made of (county random effect,
approximation error and timing differences cannot be separated here).

Benchmark: PLACES lack of insurance (ages 18-64) vs a directly measured ACS
uninsurance rate (19-64), run through the same procedure.

Outputs in atlas/outputs/covariate_test/.
"""

# Paths in this script are relative to the repository root; anchor there so it
# runs from any working directory (atlas/scripts/<this file> -> repo root).
import os as _os
from pathlib import Path as _Path
_os.chdir(_Path(__file__).resolve().parents[2])

import itertools
import os

import numpy as np
import pandas as pd

OUT = "atlas/outputs/covariate_test"
os.makedirs(OUT, exist_ok=True)

places = pd.read_csv("data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places["countyfips"].str.zfill(5)
acs = pd.read_csv("data/raw/acs_county_2023.csv", dtype={"fips": str})

df = places.merge(acs, on="fips", how="inner")
print(f"PLACES counties {len(places)}, ACS counties {len(acs)}, joined {len(df)}")
unmatched = sorted(set(places["fips"]) - set(acs["fips"]))
print("PLACES counties without ACS match:", unmatched[:10], len(unmatched))

MEASURES = [c[: -len("_adjprev")] for c in places.columns if c.endswith("_adjprev")]

# Model inputs, one category dropped per set to avoid collinearity
COMPOSITION = (
    ["age_25_34", "age_35_44", "age_45_54", "age_55_64", "age_65_74", "age_75p", "male"]
    + ["nh_black", "nh_aian", "nh_asian", "nh_nhpi", "nh_other_multi", "hispanic"]
    + ["edu_lt_hs", "edu_some_college", "edu_ba_plus", "pov150_adults"]
)
states = pd.get_dummies(df["stateabbr"], prefix="st", drop_first=True, dtype=float)


def design(rows, use_comp=True, use_state=True, flexible=False):
    parts = [pd.Series(1.0, index=rows, name="const")]
    if use_comp:
        comp = df.loc[rows, COMPOSITION]
        parts.append(comp)
        if flexible:
            parts.append((comp**2).add_suffix("_sq"))
            parts.append(
                comp[["edu_lt_hs", "edu_ba_plus", "nh_black", "hispanic", "nh_aian"]]
                .mul(df.loc[rows, "pov150_adults"], axis=0)
                .add_suffix("_x_pov")
            )
    if use_state:
        parts.append(states.loc[rows])
    X = pd.concat(parts, axis=1).astype(float)
    return X.loc[:, X.std() > 0].assign(const=1.0)


def resid_r2(y, X):
    beta, *_ = np.linalg.lstsq(X.values, y.values, rcond=None)
    res = y.values - X.values @ beta
    r2 = 1 - res.var() / y.values.var()
    return pd.Series(res, index=y.index), r2


def cv_r2(y, X, k=10, seed=0):
    """Out-of-sample R2 (k-fold), to rule out overfitting by ~70 parameters.

    A held-out county whose state has no training counties (only DC can do
    this) gets the training-county-weighted average state effect, instead of
    silently inheriting the reference state's effect.
    """
    idx = np.random.default_rng(seed).permutation(len(y))
    pred = np.empty(len(y))
    Xv, yv = X.values.copy(), y.values
    st = np.array([c.startswith("st_") for c in X.columns])
    for f in np.array_split(idx, k):
        tr = np.setdiff1d(idx, f)
        beta, *_ = np.linalg.lstsq(Xv[tr], yv[tr], rcond=None)
        Xf = Xv[f].copy()
        unseen = st & (Xv[tr].sum(axis=0) == 0)
        if unseen.any():
            hit = (Xf[:, unseen] == 1).any(axis=1)
            Xf[np.ix_(hit, st)] = Xv[tr][:, st].mean(axis=0)
        pred[f] = Xf @ beta
    return 1 - ((yv - pred) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()


def analyse(kind):
    """kind = 'adjprev' (age-adjusted) or 'crudeprev'."""
    cols = {m: f"{m}_{kind}" for m in MEASURES}
    r2_rows, resid = [], {}
    for m, c in cols.items():
        y = pd.to_numeric(df[c], errors="coerce").dropna()
        rows = y.index
        out = {"measure": m, "n_counties": len(rows)}
        for label, kw in {
            "state_only": dict(use_comp=False),
            "inputs_only": dict(use_state=False),
            "inputs_plus_state": dict(),
            "flexible_plus_state": dict(flexible=True),
        }.items():
            r, r2 = resid_r2(y, design(rows, **kw))
            out[label] = r2
            if label == "inputs_plus_state":
                resid[m] = r
                out["inputs_plus_state_cv"] = cv_r2(y, design(rows))
        r2_rows.append(out)
    r2 = pd.DataFrame(r2_rows).sort_values("inputs_plus_state", ascending=False)

    pairs = []
    for a, b in itertools.combinations(MEASURES, 2):
        ya = pd.to_numeric(df[cols[a]], errors="coerce")
        yb = pd.to_numeric(df[cols[b]], errors="coerce")
        common = ya.dropna().index.intersection(yb.dropna().index)
        ya, yb = ya[common], yb[common]
        raw = np.corrcoef(ya, yb)[0, 1]
        # Refit both measures on the SAME counties (Codex review, bug 1)
        X = design(common)
        ra, _ = resid_r2(ya, X)
        rb, _ = resid_r2(yb, X)
        part = np.corrcoef(ra, rb)[0, 1]
        # Residual covariance as a share of raw covariance, computed directly
        # on the common sample (Codex review, bug 2)
        share = np.cov(ra, rb)[0, 1] / np.cov(ya, yb)[0, 1]
        pairs.append({
            "a": a, "b": b, "n": len(common), "raw_r": raw, "partial_r": part,
            "cov_share_remaining": share,
        })
    pairs = pd.DataFrame(pairs)
    return r2, pairs, resid


summary_lines = []
for kind in ["adjprev", "crudeprev"]:
    r2, pairs, resid = analyse(kind)
    r2.round(3).to_csv(f"{OUT}/r2_by_measure_{kind}.csv", index=False)
    pairs.round(3).to_csv(f"{OUT}/pairs_{kind}.csv", index=False)
    if kind == "adjprev":
        resid_adj = resid
    s = (
        f"\n=== {kind} ===\n"
        f"R2 of measures on inputs + state: median {r2.inputs_plus_state.median():.2f} "
        f"(range {r2.inputs_plus_state.min():.2f}-{r2.inputs_plus_state.max():.2f}); "
        f"inputs only median {r2.inputs_only.median():.2f}; state only median {r2.state_only.median():.2f}; "
        f"flexible median {r2.flexible_plus_state.median():.2f}; "
        f"out-of-sample (10-fold) median {r2.inputs_plus_state_cv.median():.3f} "
        f"(min {r2.inputs_plus_state_cv.min():.3f})\n"
        f"Pairs: {len(pairs)}; median |raw r| {pairs.raw_r.abs().median():.2f}, "
        f"median |partial r| {pairs.partial_r.abs().median():.2f}; "
        f"pairs with |raw r|>=0.7: {(pairs.raw_r.abs()>=0.7).sum()}, "
        f"of those with |partial r|>=0.7: {((pairs.raw_r.abs()>=0.7)&(pairs.partial_r.abs()>=0.7)).sum()}; "
        f"sign flips: {(np.sign(pairs.raw_r)!=np.sign(pairs.partial_r)).sum()}; "
        f"share of raw covariance remaining, pairs |raw r|>=0.7: median "
        f"{pairs.loc[pairs.raw_r.abs()>=0.7,'cov_share_remaining'].median():.3f}, max "
        f"{pairs.loc[pairs.raw_r.abs()>=0.7,'cov_share_remaining'].max():.3f}\n"
    )
    print(s)
    summary_lines.append(s)
    print(r2.round(2).to_string(index=False))

# Highlighted pairs (age-adjusted)
pairs = pd.read_csv(f"{OUT}/pairs_adjprev.csv")
HIGHLIGHT = [
    ("diabetes", "foodinsecu"), ("diabetes", "lacktrpt"), ("chd", "csmoking"),
    ("obesity", "lpa"), ("access2", "diabetes"), ("depression", "loneliness"),
    ("depression", "mhlth"), ("copd", "csmoking"), ("obesity", "diabetes"),
    ("foodinsecu", "foodstamp"), ("bphigh", "stroke"), ("casthma", "copd"),
]
key = pairs.set_index(["a", "b"])
hl = []
for a, b in HIGHLIGHT:
    row = key.loc[(a, b)] if (a, b) in key.index else key.loc[(b, a)]
    hl.append({"pair": f"{a} ~ {b}", **row.to_dict()})
hl = pd.DataFrame(hl)
hl.round(3).to_csv(f"{OUT}/highlight_pairs_adjprev.csv", index=False)
print("\nHighlighted pairs (age-adjusted):\n", hl.round(2).to_string(index=False))

# Benchmark: PLACES access2 vs directly measured ACS uninsurance
bench = []
for label, mask in {
    "all counties": df["adults"] > 0,
    ">=20k adults": df["adults"] >= 20_000,
}.items():
    rows = df.index[mask & df["access2_crudeprev"].notna() & df["acs_uninsured_19_64"].notna()]
    yp = df.loc[rows, "access2_crudeprev"].astype(float)
    ya = df.loc[rows, "acs_uninsured_19_64"].astype(float) * 100
    X = design(rows)
    rp, r2p = resid_r2(yp, X)
    ra, r2a = resid_r2(ya, X)
    cvp, cva = cv_r2(yp, X), cv_r2(ya, X)
    bench.append({
        "sample": label, "n": len(rows),
        "raw_r": np.corrcoef(yp, ya)[0, 1], "partial_r": np.corrcoef(rp, ra)[0, 1],
        "r2_places_on_inputs": r2p, "r2_acs_direct_on_inputs": r2a,
        "cv_r2_places": cvp, "cv_r2_acs_direct": cva,
    })
bench = pd.DataFrame(bench)
bench.round(3).to_csv(f"{OUT}/benchmark_uninsurance.csv", index=False)
print("\nBenchmark (crude PLACES access2 vs ACS direct uninsured 19-64):\n", bench.round(2).to_string(index=False))

with open(f"{OUT}/summary.txt", "w") as f:
    f.writelines(summary_lines)
