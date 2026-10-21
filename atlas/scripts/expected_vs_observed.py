"""Expected vs observed: does PLACES tell us anything about measured county
health beyond what demographics already predict?

Expected: county demographics + state (the ingredients PLACES is built from),
optionally plus the PLACES estimate itself.
Observed: directly measured county outcomes.
  - Medicare claims prevalence, Original Medicare beneficiaries, 2023,
    age-standardized (CMS Mapping Medicare Disparities). Different population
    from PLACES (adults 18+ vs mostly 65+ Medicare FFS), so the question is
    whether PLACES ranks counties the way claims do, not whether levels match.
  - ACS 2019-2023 disability by type, adults 18+ (survey, not modeled).
  - CDC WONDER deaths 2018-2024 as standardized mortality ratios (x100;
    indirect age standardization, atlas/scripts/build_mortality_smr.py). Counties
    with 9 or fewer deaths are suppressed and never published.

For each pair, with 10-fold cross-validation on the counties both share:
  r_raw            correlation of PLACES with the observed outcome
  cv_r2_demo       observed ~ demographics + state (+ Medicare Advantage share
                   for Medicare outcomes, because claims cover only Original
                   Medicare and its share varies by county)
  cv_r2_places     observed ~ PLACES alone
  cv_r2_demo_places observed ~ demographics + state + PLACES
  gain             cv_r2_demo_places - cv_r2_demo: what PLACES adds
  partial_r        PLACES vs observed after removing demographics + state
Repeated for larger counties only (>= 5,000 Original Medicare beneficiaries,
>= 20,000 adults for ACS, >= 100 expected deaths for WONDER), where sampling noise in the observed rate is smaller.

Per-county observed-minus-expected residuals (the atlas layer) are saved too.
Outputs in atlas/outputs/expected_vs_observed/.
"""

# Paths in this script are relative to the repository root; anchor there so it
# runs from any working directory (atlas/scripts/<this file> -> repo root).
import os as _os
from pathlib import Path as _Path
_os.chdir(_Path(__file__).resolve().parents[2])

import os

import numpy as np
import pandas as pd

OUT = "atlas/outputs/expected_vs_observed"
os.makedirs(OUT, exist_ok=True)

# ---- data -------------------------------------------------------------
places = pd.read_csv("data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places["countyfips"].str.zfill(5)
acs = pd.read_csv("data/raw/acs_county_2023.csv", dtype={"fips": str})
dis = pd.read_csv("data/raw/acs_disability_2023.csv", dtype={"fips": str})
gv = pd.read_csv("data/raw/medicare_gv_county_2023.csv", dtype={"fips": str})
mmd = pd.read_csv("data/raw/mmd_prevalence_2023.csv", dtype={"fips": str})
smr = pd.read_csv("data/raw/wonder_county_smr.csv", dtype={"fips": str})
smr_wide = (100 * smr.pivot_table(index="fips", columns="cause", values="smr")).add_prefix("smr_")
smr_exp = smr.pivot_table(index="fips", columns="cause", values="expected").add_prefix("exp_")

gv["om"] = pd.to_numeric(gv["BENES_OM_CNT"], errors="coerce")
gv["ma"] = pd.to_numeric(gv["BENES_MA_CNT"], errors="coerce")
gv["ma_share"] = gv["ma"] / (gv["ma"] + gv["om"])

# Age-standardized claims prevalence (fltr=2); 0 marks suppressed cells
mmd = mmd[mmd["fltr"] == 2].copy()
mmd.loc[mmd["rate"] == 0, "rate"] = np.nan
mmd_wide = mmd.pivot_table(index="fips", columns="condition", values="rate").add_prefix("mc_")

df = (
    places.merge(acs, on="fips")
    .merge(dis, on="fips", how="left")
    .merge(gv[["fips", "om", "ma_share"]], on="fips", how="left")
    .merge(mmd_wide, left_on="fips", right_index=True, how="left")
    .merge(smr_wide, left_on="fips", right_index=True, how="left")
    .merge(smr_exp, left_on="fips", right_index=True, how="left")
    .set_index("fips")
)
print("counties:", len(df))

COMPOSITION = (
    ["age_25_34", "age_35_44", "age_45_54", "age_55_64", "age_65_74", "age_75p", "male"]
    + ["nh_black", "nh_aian", "nh_asian", "nh_nhpi", "nh_other_multi", "hispanic"]
    + ["edu_lt_hs", "edu_some_college", "edu_ba_plus", "pov150_adults"]
)

PAIRS = [
    # (label, PLACES column, observed column, source)
    ("Diabetes", "diabetes_adjprev", "mc_diabetes", "medicare"),
    ("COPD", "copd_adjprev", "mc_copd", "medicare"),
    ("Depression", "depression_adjprev", "mc_depression", "medicare"),
    ("High blood pressure", "bphigh_adjprev", "mc_hypertension", "medicare"),
    ("Coronary heart disease", "chd_adjprev", "mc_ischemic_heart_disease", "medicare"),
    ("Stroke", "stroke_adjprev", "mc_stroke_tia", "medicare"),
    ("Asthma", "casthma_adjprev", "mc_asthma", "medicare"),
    ("Obesity", "obesity_adjprev", "mc_obesity", "medicare"),
    ("Arthritis", "arthritis_adjprev", "mc_arthritis", "medicare"),
    ("High cholesterol", "highchol_adjprev", "mc_hyperlipidemia", "medicare"),
    ("Cancer", "cancer_adjprev", "mc_cancer_4_sites", "medicare"),
    ("Hearing disability", "hearing_crudeprev", "acs_hearing", "acs"),
    ("Vision disability", "vision_crudeprev", "acs_vision", "acs"),
    ("Cognitive disability", "cognition_crudeprev", "acs_cognition", "acs"),
    ("Mobility disability", "mobility_crudeprev", "acs_mobility", "acs"),
    ("Self-care disability", "selfcare_crudeprev", "acs_selfcare", "acs"),
    ("Independent-living disability", "indeplive_crudeprev", "acs_indeplive", "acs"),
    ("Diabetes deaths (SMR)", "diabetes_adjprev", "smr_diabetes", "wonder"),
    ("Heart disease deaths (SMR)", "chd_adjprev", "smr_heart", "wonder"),
    ("Stroke deaths (SMR)", "stroke_adjprev", "smr_stroke", "wonder"),
    ("Chronic lower respiratory deaths (SMR)", "copd_adjprev", "smr_clrd", "wonder"),
]


# ---- helpers ----------------------------------------------------------
def design(rows, extra=()):
    X = pd.concat(
        [
            pd.Series(1.0, index=rows, name="const"),
            df.loc[rows, COMPOSITION + list(extra)],
            pd.get_dummies(df.loc[rows, "stateabbr"], prefix="st", drop_first=True, dtype=float),
        ],
        axis=1,
    ).astype(float)
    return X.loc[:, (X.std() > 0) | (X.columns == "const")]


def cv_predict(y, X, k=10, seed=20261020):
    """Held-out predictions; an unseen state gets the training-weighted mean state effect."""
    idx = np.random.default_rng(seed).permutation(len(y))
    pred = np.empty(len(y))
    Xv, yv = X.values, y.values
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
    return pd.Series(pred, index=y.index)


def r2(y, pred):
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def resid(y, X):
    beta, *_ = np.linalg.lstsq(X.values, y.values, rcond=None)
    return y - X.values @ beta


def evaluate(label, pcol, ocol, source, rows):
    extra = ["ma_share"] if source == "medicare" else []
    sub = df.loc[rows, [pcol, ocol] + COMPOSITION + extra + ["stateabbr"]].dropna()
    rows = sub.index
    y, p = sub[ocol].astype(float), sub[pcol].astype(float)
    Xd = design(rows, extra)
    Xdp = Xd.assign(places=p)
    Xp = pd.DataFrame({"const": 1.0, "places": p}, index=rows)
    pred_demo = cv_predict(y, Xd)
    out = {
        "outcome": label, "source": source, "n": len(rows),
        "r_raw": np.corrcoef(p, y)[0, 1],
        "cv_r2_demo": r2(y, pred_demo),
        "cv_r2_places": r2(y, cv_predict(y, Xp)),
        "cv_r2_demo_places": r2(y, cv_predict(y, Xdp)),
        "partial_r": np.corrcoef(resid(p, Xd), resid(y, Xd))[0, 1],
    }
    out["gain"] = out["cv_r2_demo_places"] - out["cv_r2_demo"]
    return out, y - pred_demo


results, residuals = [], {}
for label, pcol, ocol, source in PAIRS:
    if source == "medicare":
        big = df["om"] >= 5000
    elif source == "wonder":  # reliability of an SMR depends on expected deaths
        big = df["exp_" + ocol.split("_", 1)[1]] >= 100
    else:
        big = df["adults"] >= 20000
    for sample, rows in {"all": df.index, "larger": df.index[big.fillna(False)]}.items():
        res, obs_minus_exp = evaluate(label, pcol, ocol, source, rows)
        res["sample"] = sample
        results.append(res)
        if sample == "all":
            residuals[ocol] = obs_minus_exp

res = pd.DataFrame(results)
res.to_csv(f"{OUT}/places_vs_observed.csv", index=False)
cols = ["outcome", "n", "r_raw", "cv_r2_demo", "cv_r2_places", "cv_r2_demo_places", "gain", "partial_r"]
for s in ["all", "larger"]:
    print(f"\n=== sample: {s} ===")
    print(res.loc[res["sample"] == s, cols].round(3).to_string(index=False))

pd.DataFrame(residuals).to_csv(f"{OUT}/observed_minus_expected_by_county.csv")
