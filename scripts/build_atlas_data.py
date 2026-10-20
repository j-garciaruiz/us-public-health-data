"""Atlas data: observed vs demographic expectation, county by county.

Separate from scripts/expected_vs_observed.py, which compares PLACES with
measured outcomes on a common county panel. Here PLACES is NOT required:
every county with an observed value and covariates gets an expectation
(Codex review, reviews/eo_codex_astra/REPORT.md, finding 8 and code audit).

expected = cross-fitted (10-fold) prediction of the SAME observed outcome from
county demographics (age, sex, race/ethnicity, education, adults below 150%
of poverty) and state, plus Medicare Advantage share for Medicare outcomes.
It is an empirical peer comparator, not a target, an equitable rate, or the
amount of disease demographics cause. difference = observed - expected.

Layers
- medicare_actual (main) and medicare_std: recorded diagnoses among Original
  Medicare beneficiaries, 2023, CMS Mapping Medicare Disparities.
- acs: reported difficulty, civilian noninstitutionalized adults 18+, ACS 2019-2023.
- mortality: standardized mortality ratio x 100, CDC WONDER 2018-2024. Counties
  with 9 or fewer deaths are suppressed by WONDER and have no value (NCHS rule:
  such counts are never published).

Reliability flags
- Medicare: CMS denominator band `dencat` (assumed by documented order:
  1 = 11-499, 2 = 500-999, 3 = 1,000-4,999, 4 = 5,000-9,999, 5 = 10,000+).
  `source_discrepancy` marks counties where the Geographic Variation file has
  >= 5,000 Original Medicare beneficiaries but MMD reports band 1-2 (e.g.
  Kenai Peninsula, AK). Zeros are dropped (ambiguous: suppression or rounding).
- ACS: adults 18+ in the county (margins of error not yet propagated).
- Mortality: expected deaths.
PLACES (age-adjusted where available) is attached only as context.

Output: outputs/atlas/atlas_county_long.csv
"""

import os

import numpy as np
import pandas as pd

OUT = "outputs/atlas"
os.makedirs(OUT, exist_ok=True)

acs = pd.read_csv("data/raw/acs_county_2023.csv", dtype={"fips": str}).set_index("fips")
places = pd.read_csv("data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places["countyfips"].str.zfill(5)
places = places.set_index("fips")
state = pd.Series(
    {f: s for f, s in zip(places.index, places["stateabbr"])}
)  # PLACES lists every county with its state, including KY/PA
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


def cv_expected(y, extra=None, k=10, seed=20261020):
    rows = y.index.intersection(acs.index).intersection(state.index)
    X = acs.loc[rows, COMPOSITION].copy()
    if extra is not None:
        X["extra"] = extra.reindex(rows)
    st = pd.get_dummies(state.loc[rows], prefix="st", drop_first=True, dtype=float)
    X = pd.concat([pd.Series(1.0, index=rows, name="const"), X, st], axis=1).dropna()
    yv = y.loc[X.index].astype(float).values
    Xv = X.values
    stc = np.array([c.startswith("st_") for c in X.columns])
    idx = np.random.default_rng(seed).permutation(len(yv))
    pred = np.empty(len(yv))
    for f in np.array_split(idx, k):
        tr = np.setdiff1d(idx, f)
        beta, *_ = np.linalg.lstsq(Xv[tr], yv[tr], rcond=None)
        Xf = Xv[f].copy()
        unseen = stc & (Xv[tr].sum(axis=0) == 0)
        if unseen.any():
            hit = (Xf[:, unseen] == 1).any(axis=1)
            Xf[np.ix_(hit, stc)] = Xv[tr][:, stc].mean(axis=0)
        pred[f] = Xf @ beta
    return pd.Series(pred, index=X.index)


LABELS = {
    "diabetes": "Diabetes", "copd": "COPD", "depression": "Depression",
    "hypertension": "Hypertension", "ischemic_heart_disease": "Ischemic heart disease",
    "stroke_tia": "Stroke or TIA", "asthma": "Asthma", "obesity": "Obesity (recorded)",
    "arthritis": "Rheumatoid arthritis or osteoarthritis", "hyperlipidemia": "Hyperlipidemia (recorded)",
    "cancer_4_sites": "Cancer: breast, colorectal, prostate or lung", "chronic_kidney_disease": "Chronic kidney disease",
}
PLACES_COL = {r.condition: r.places_measure for r in mmd.drop_duplicates("condition").itertuples()}

frames = []
# Medicare layers
for fltr, layer in [(1, "medicare_actual"), (2, "medicare_std")]:
    sub = mmd[(mmd["fltr"] == fltr) & (mmd["rate"] > 0)]
    for cond, g in sub.groupby("condition"):
        g = g.set_index("fips")
        exp = cv_expected(g["rate"], extra=ma_share)
        pm = PLACES_COL.get(cond)
        frames.append(pd.DataFrame({
            "layer": layer, "outcome": LABELS[cond], "observed": g.loc[exp.index, "rate"],
            "expected": exp, "reliability": g.loc[exp.index, "dencat"].astype("Int64").astype(str),
            "source_discrepancy": (om.reindex(exp.index) >= 5000) & (g.loc[exp.index, "dencat"] <= 2),
            "places_context": places[f"{pm}_adjprev"].reindex(exp.index) if isinstance(pm, str) else np.nan,
        }))
# ACS disability
for col, name, pm in [("acs_hearing", "Hearing difficulty", "hearing"), ("acs_vision", "Vision difficulty", "vision"),
                      ("acs_cognition", "Cognitive difficulty", "cognition"), ("acs_mobility", "Ambulatory difficulty", "mobility"),
                      ("acs_selfcare", "Self-care difficulty", "selfcare"), ("acs_indeplive", "Independent-living difficulty", "indeplive")]:
    y = dis[col].dropna()
    exp = cv_expected(y)
    frames.append(pd.DataFrame({
        "layer": "acs", "outcome": name, "observed": y.loc[exp.index], "expected": exp,
        "reliability": acs.loc[exp.index, "adults"].astype(int).astype(str) + " adults",
        "source_discrepancy": False, "places_context": places[f"{pm}_crudeprev"].reindex(exp.index),
    }))
# Mortality (SMR x 100); suppressed counties have no SMR
for cause, name, pm in [("diabetes", "Diabetes deaths", "diabetes"), ("heart", "Heart disease deaths", "chd"),
                        ("stroke", "Cerebrovascular deaths", "stroke"), ("clrd", "Chronic lower respiratory deaths", "copd")]:
    g = smr[(smr["cause"] == cause) & smr["smr"].notna()].set_index("fips")
    y = 100 * g["smr"]
    exp = cv_expected(y)
    frames.append(pd.DataFrame({
        "layer": "mortality", "outcome": name, "observed": y.loc[exp.index], "expected": exp,
        "reliability": g.loc[exp.index, "expected"].round(0).astype(int).astype(str) + " expected deaths",
        "source_discrepancy": False, "places_context": places[f"{pm}_adjprev"].reindex(exp.index),
    }))

atlas = pd.concat(frames)
atlas.index.name = "fips"
atlas["difference"] = atlas["observed"] - atlas["expected"]
atlas["state"] = state.reindex(atlas.index).values
atlas = atlas.reset_index()[["fips", "state", "layer", "outcome", "observed", "expected", "difference",
                             "reliability", "source_discrepancy", "places_context"]]
atlas.round(3).to_csv(f"{OUT}/atlas_county_long.csv", index=False)
print(atlas.groupby(["layer", "outcome"]).agg(counties=("fips", "size"),
      ky_pa=("state", lambda s: s.isin(["KY", "PA"]).sum()),
      sd_diff=("difference", "std"), flagged=("source_discrepancy", "sum")).round(2).to_string())
