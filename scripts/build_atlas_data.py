"""Atlas data: observed vs demographic expectation, county by county.

Separate from scripts/expected_vs_observed.py, which compares PLACES with
measured outcomes on a common panel. Here PLACES is NOT required: every county
with an observed value and covariates gets an expectation. Design follows the
Codex and Agy reviews (reviews/eo_codex_astra/REPORT.md finding 8;
reviews/eo_agy_argon/REPORT.md findings 7-8 and bugs 3-5).

Two expectation modes
- national (default): observed ~ county demographics (age, sex, race/ethnicity,
  education, adults below 150% of poverty), plus Medicare Advantage share for
  Medicare outcomes. Answers "compared with demographically similar counties
  anywhere in the US". State differences (policy, care, environment) stay
  visible on the map.
- within_state: adds state effects, so each state averages zero and the map
  shows counties that differ from similar counties in their own state.
The expectation is an empirical peer comparator, not a target, an equitable
rate, or the amount of disease that demographics cause.

Expected values are cross-fitted: the average of 10 repetitions of 10-fold
cross-validation, so no county is predicted by a model that saw it and the
value does not hinge on one random split. State effects use one indicator per
state with no separate intercept; a held-out county whose state has no
training counties (DC, or a small state whose counties all fall in one fold)
gets the training-weighted average state effect.

Shrinkage (empirical Bayes): raw difference r = observed - expected. With
sampling variance s2 per county and between-county variance
tau2 (see below), reliability lambda = tau2 / (tau2 + s2) and
the shrunk difference is lambda * r. Tiers: 1 if lambda >= 0.75, 2 if
0.40-0.75, 3 below 0.40 (show muted or grey).
  s2 for mortality (SMR x 100): 100 * expected_smr / expected_deaths (Poisson)
  s2 for Medicare (%): p(100 - p) / n + 1/12 (binomial plus whole-percent
     rounding). n is APPROXIMATE: Original Medicare count from the Geographic
     Variation file clipped to the CMS denominator band of the MMD cell
     (1: 11-499, 2: 500-999, 3: 1,000-4,999, 4: 5,000-9,999, 5: 10,000+;
     band codes assumed by documented order). Codex warned that GV counts are
     not the exact MMD denominator; clipping to the band limits the damage.
  s2 for ACS (%): (MOE / 1.645)^2 from the Census margins of error.
  tau2 is estimated by DerSimonian-Laird (precision-weighted moments).

Suppression: WONDER counts of 9 or fewer (zero included) have no SMR and never
appear. Medicare zeros are dropped (ambiguous: suppression or rounding).

Output: outputs/atlas/atlas_county_long.csv
"""

import os

import numpy as np
import pandas as pd

OUT = "outputs/atlas"
os.makedirs(OUT, exist_ok=True)
SEED, REPEATS, FOLDS = 20261020, 10, 10

acs = pd.read_csv("data/raw/acs_county_2023.csv", dtype={"fips": str}).set_index("fips")
places = pd.read_csv("data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places["countyfips"].str.zfill(5)
places = places.set_index("fips")
state = places["stateabbr"]  # every county incl. KY/PA; Loving County, TX is absent from PLACES
dis = pd.read_csv("data/raw/acs_disability_2023.csv", dtype={"fips": str}).set_index("fips")
gv = pd.read_csv("data/raw/medicare_gv_county_2023.csv", dtype={"fips": str}).set_index("fips")
om = pd.to_numeric(gv["BENES_OM_CNT"], errors="coerce")
ma = pd.to_numeric(gv["BENES_MA_CNT"], errors="coerce")
ma_share = ma / (ma + om)
mmd = pd.read_csv("data/raw/mmd_prevalence_2023.csv", dtype={"fips": str})
smr = pd.read_csv("data/raw/wonder_county_smr.csv", dtype={"fips": str})

COMPOSITION = (
    ["age_25_34", "age_35_44", "age_45_54", "age_55_64", "age_65_74", "age_75p", "male"]
    + ["nh_black", "nh_aian", "nh_asian", "nh_nhpi", "nh_other_multi", "hispanic"]
    + ["edu_lt_hs", "edu_some_college", "edu_ba_plus", "pov150_adults"]
)
BAND = {1: (11, 499), 2: (500, 999), 3: (1000, 4999), 4: (5000, 9999), 5: (10000, np.inf)}


def design(rows, extra, within_state):
    X = acs.loc[rows, COMPOSITION].copy()
    if extra is not None:
        X["extra"] = extra.reindex(rows)
    if within_state:
        st = pd.get_dummies(state.loc[rows], prefix="st", dtype=float)  # all states, no intercept
        X = pd.concat([X, st], axis=1)
    else:
        X.insert(0, "const", 1.0)
    return X


def cross_fit(y, extra=None, within_state=False):
    rows = y.index.intersection(acs.index).intersection(state.index)
    X = design(rows, extra, within_state).dropna()
    yv, Xv = y.loc[X.index].astype(float).values, X.values
    stc = np.array([c.startswith("st_") for c in X.columns])
    preds = np.zeros(len(yv))
    rng = np.random.default_rng(SEED)
    for _ in range(REPEATS):
        idx = rng.permutation(len(yv))
        pred = np.empty(len(yv))
        for f in np.array_split(idx, FOLDS):
            tr = np.setdiff1d(idx, f)
            beta, *_ = np.linalg.lstsq(Xv[tr], yv[tr], rcond=None)
            Xf = Xv[f].copy()
            if stc.any():
                unseen = stc & (Xv[tr].sum(axis=0) == 0)
                hit = (Xf[:, unseen] == 1).any(axis=1) if unseen.any() else np.zeros(len(f), bool)
                Xf[np.ix_(hit, stc)] = Xv[tr][:, stc].mean(axis=0)
            pred[f] = Xf @ beta
        preds += pred / REPEATS
    return pd.Series(preds, index=X.index)


def shrink(obs, exp, s2):
    """Empirical Bayes shrinkage; tau2 by DerSimonian-Laird (precision-weighted
    moments), which unlike var(r) - mean(s2) is not dominated by a few tiny
    counties with enormous margins of error."""
    r = obs - exp
    w = 1 / s2
    q = float((w * r**2).sum())
    tau2 = max(0.0, (q - (len(r) - 1)) / float(w.sum() - (w**2).sum() / w.sum()))
    lam = tau2 / (tau2 + s2)
    tier = np.where(lam >= 0.75, 1, np.where(lam >= 0.40, 2, 3))
    return r, lam * r, lam, tier, tau2


LABELS = {
    "diabetes": "Diabetes", "copd": "COPD", "depression": "Depression",
    "hypertension": "Hypertension", "ischemic_heart_disease": "Ischemic heart disease",
    "stroke_tia": "Stroke or TIA", "asthma": "Asthma", "obesity": "Obesity (recorded)",
    "arthritis": "Rheumatoid arthritis or osteoarthritis", "hyperlipidemia": "Hyperlipidemia (recorded)",
    "cancer_4_sites": "Cancer: breast, colorectal, prostate or lung", "chronic_kidney_disease": "Chronic kidney disease",
}
PLACES_COL = {r.condition: r.places_measure for r in mmd.drop_duplicates("condition").itertuples()}
frames, summary = [], []


def add(layer, outcome, obs, s2_fn, note, extra=None, places_ctx=None, discrepancy=None):
    for mode in ("national", "within_state"):
        exp = cross_fit(obs, extra, within_state=(mode == "within_state"))
        o = obs.loc[exp.index]
        s2 = s2_fn(o, exp)
        r, rs, lam, tier, tau2 = shrink(o, exp, s2)
        frames.append(pd.DataFrame({
            "layer": layer, "outcome": outcome, "mode": mode, "observed": o, "expected": exp,
            "difference": r, "difference_shrunk": rs, "reliability": lam, "tier": tier,
            "reliability_note": note.reindex(exp.index),
            "source_discrepancy": discrepancy.reindex(exp.index).fillna(False) if discrepancy is not None else False,
            "places_context": places_ctx.reindex(exp.index) if places_ctx is not None else np.nan,
        }))
        summary.append({"layer": layer, "outcome": outcome, "mode": mode, "counties": len(exp),
                        "ky_pa": int(state.reindex(exp.index).isin(["KY", "PA"]).sum()),
                        "sd_raw": r.std(), "sd_shrunk": rs.std(), "tau": np.sqrt(tau2),
                        "tier1": int((tier == 1).sum()), "tier3": int((tier == 3).sum())})


# Medicare: actual (main) and age-standardized views
for fltr, layer in [(1, "medicare_actual"), (2, "medicare_std")]:
    sub = mmd[(mmd["fltr"] == fltr) & (mmd["rate"] > 0)]
    for cond, g in sub.groupby("condition"):
        g = g.set_index("fips")
        band = g["dencat"].astype(int)
        lo, hi = band.map(lambda b: BAND[b][0]), band.map(lambda b: BAND[b][1])
        n = om.reindex(g.index).fillna(lo).clip(lower=lo, upper=hi)
        n = n.where(np.isfinite(n), lo)
        disc = (om.reindex(g.index) >= 5000) & (band <= 2)
        note = "CMS band " + band.astype(str) + ", approx n " + n.round(0).astype(int).astype(str)
        pm = PLACES_COL.get(cond)
        add(layer, LABELS[cond], g["rate"],
            lambda o, e, n=n: o * (100 - o) / n.reindex(o.index) + 1 / 12,
            note, extra=ma_share,
            places_ctx=places[f"{pm}_adjprev"] if isinstance(pm, str) else None, discrepancy=disc)

# ACS disability (crude, adults 18+)
for col, name, pm in [("acs_hearing", "Hearing difficulty", "hearing"), ("acs_vision", "Vision difficulty", "vision"),
                      ("acs_cognition", "Cognitive difficulty", "cognition"), ("acs_mobility", "Ambulatory difficulty", "mobility"),
                      ("acs_selfcare", "Self-care difficulty", "selfcare"), ("acs_indeplive", "Independent-living difficulty", "indeplive")]:
    moe = dis[f"{col}_moe"]
    add("acs", name, dis[col].dropna(), lambda o, e, moe=moe: (moe.reindex(o.index) / 1.645) ** 2,
        "MOE +/- " + moe.round(2).astype(str), places_ctx=places[f"{pm}_crudeprev"])

# Mortality: SMR x 100 (suppressed counties have no SMR)
for cause, name, pm in [("diabetes", "Diabetes deaths", "diabetes"), ("heart", "Heart disease deaths", "chd"),
                        ("stroke", "Cerebrovascular deaths", "stroke"), ("clrd", "Chronic lower respiratory deaths", "copd")]:
    g = smr[(smr["cause"] == cause) & smr["smr"].notna()].set_index("fips")
    E = g["expected"]
    add("mortality", name, 100 * g["smr"], lambda o, e, E=E: 100 * e.clip(lower=1) / E.reindex(o.index),
        E.round(0).astype(int).astype(str) + " expected deaths", places_ctx=places[f"{pm}_adjprev"])

atlas = pd.concat(frames)
atlas.index.name = "fips"
atlas["state"] = state.reindex(atlas.index).values
cols = ["fips", "state", "layer", "outcome", "mode", "observed", "expected", "difference",
        "difference_shrunk", "reliability", "tier", "reliability_note", "source_discrepancy", "places_context"]
atlas = atlas.reset_index()[cols]
assert not ((atlas["layer"] == "mortality") & atlas["observed"].isna()).any()
atlas.round(4).to_csv(f"{OUT}/atlas_county_long.csv", index=False)
s = pd.DataFrame(summary)
s.round(3).to_csv(f"{OUT}/atlas_summary.csv", index=False)
print(s.round(2).to_string(index=False))
