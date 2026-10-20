#!/usr/bin/env python3
"""Verify exact decomposition of differences between our independent recomputation and outputs/expected_vs_observed/places_vs_observed.csv."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path("/Users/hari/.gemini/antigravity-cli/brain/5c0d75a6-5a8a-411d-9863-4546aaa291ce/scratch")

their_pvo = pd.read_csv(ROOT / "outputs/expected_vs_observed/places_vs_observed.csv")
our_canon = pd.read_csv(ROOT / "reviews/eo_agy_argon/recomputed_places_vs_observed.csv")
our_all = pd.read_csv(SCRATCH / "recomputed_places_vs_observed_all_variants.csv")

# Also check if we run our exact eval_pair on their mortality SMR (with 0s included) using seed=42 vs seed=20261020
places = pd.read_csv(ROOT / "data/raw/places_county_2025.csv", dtype={"countyfips": str})
places["fips"] = places["countyfips"].str.zfill(5)
acs = pd.read_csv(ROOT / "data/raw/acs_county_2023.csv", dtype={"fips": str})
dis = pd.read_csv(ROOT / "data/raw/acs_disability_2023.csv", dtype={"fips": str})
gv = pd.read_csv(ROOT / "data/raw/medicare_gv_county_2023.csv", dtype={"fips": str})
mmd = pd.read_csv(ROOT / "data/raw/mmd_prevalence_2023.csv", dtype={"fips": str})
smr = pd.read_csv(ROOT / "data/raw/wonder_county_smr.csv", dtype={"fips": str})
smr_wide = (100 * smr.pivot_table(index="fips", columns="cause", values="smr")).add_prefix("smr_")
smr_exp = smr.pivot_table(index="fips", columns="cause", values="expected").add_prefix("exp_")

gv["om"] = pd.to_numeric(gv["BENES_OM_CNT"], errors="coerce")
gv["ma"] = pd.to_numeric(gv["BENES_MA_CNT"], errors="coerce")
gv["ma_share"] = gv["ma"] / (gv["ma"] + gv["om"])

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

name_to_obs = {
    "Diabetes": ("medicare", "diabetes", "diabetes_adjprev", "mc_diabetes"),
    "COPD": ("medicare", "copd", "copd_adjprev", "mc_copd"),
    "Depression": ("medicare", "depression", "depression_adjprev", "mc_depression"),
    "High blood pressure": ("medicare", "hypertension", "bphigh_adjprev", "mc_hypertension"),
    "Coronary heart disease": ("medicare", "ischemic_heart_disease", "chd_adjprev", "mc_ischemic_heart_disease"),
    "Stroke": ("medicare", "stroke_tia", "stroke_adjprev", "mc_stroke_tia"),
    "Asthma": ("medicare", "asthma", "casthma_adjprev", "mc_asthma"),
    "Obesity": ("medicare", "obesity", "obesity_adjprev", "mc_obesity"),
    "Arthritis": ("medicare", "arthritis", "arthritis_adjprev", "mc_arthritis"),
    "High cholesterol": ("medicare", "hyperlipidemia", "highchol_adjprev", "mc_hyperlipidemia"),
    "Cancer": ("medicare", "cancer_4_sites", "cancer_adjprev", "mc_cancer_4_sites"),
    "Hearing disability": ("disability", "acs_hearing", "hearing_crudeprev", "acs_hearing"),
    "Vision disability": ("disability", "acs_vision", "vision_crudeprev", "acs_vision"),
    "Cognitive disability": ("disability", "acs_cognition", "cognition_crudeprev", "acs_cognition"),
    "Mobility disability": ("disability", "acs_mobility", "mobility_crudeprev", "acs_mobility"),
    "Self-care disability": ("disability", "acs_selfcare", "selfcare_crudeprev", "acs_selfcare"),
    "Independent-living disability": ("disability", "acs_indeplive", "indeplive_crudeprev", "acs_indeplive"),
    "Diabetes deaths (SMR)": ("mortality", "diabetes", "diabetes_adjprev", "smr_diabetes"),
    "Heart disease deaths (SMR)": ("mortality", "heart_disease", "chd_adjprev", "smr_heart"),
    "Stroke deaths (SMR)": ("mortality", "stroke", "stroke_adjprev", "smr_stroke"),
    "Chronic lower respiratory deaths (SMR)": ("mortality", "copd", "copd_adjprev", "smr_clrd"),
}

# Print summary of differences by domain
for dom in ["medicare", "disability", "mortality"]:
    sub_t = their_pvo[their_pvo["source"].map({"medicare": "medicare", "acs": "disability", "wonder": "mortality"}) == dom]
    print(f"\n=== DOMAIN: {dom.upper()} ===")
    for _, r in sub_t.iterrows():
        _, obs_name, _, _ = name_to_obs[r["outcome"]]
        s_label = "all" if r["sample"] == "all" else "large"
        c = our_canon[(our_canon["domain"] == dom) & (our_canon["observed_outcome"] == obs_name) & (our_canon["subset"] == s_label)].iloc[0]
        if dom == "medicare":
            v = c
        elif dom == "disability":
            v = our_all[(our_all["domain"] == dom) & (our_all["observed_outcome"] == obs_name) & (our_all["subset"] == s_label) & (our_all["places_type"] == "crudeprev")].iloc[0]
        else:
            v = our_all[(our_all["domain"] == dom) & (our_all["observed_outcome"] == obs_name) & (our_all["subset"] == s_label) & (our_all["places_type"] == "adjprev") & (our_all["variant"] == "wpop_unmapped_fips")].iloc[0]
        print(
            f"  {r['outcome']:38s} ({r['sample']:6s}): "
            f"n={int(r['n'])} vs canon {int(c['n'])} (var {int(v['n'])}) | "
            f"r_raw={r['r_raw']:.4f} vs canon {c['raw_r']:.4f} (var {v['raw_r']:.4f}) | "
            f"cv_demo={r['cv_r2_demo']:.4f} vs canon {c['cv_r2_demo_state']:.4f} (var {v['cv_r2_demo_state']:.4f}) | "
            f"gain={r['gain']:.4f} vs canon {c['cv_r2_gain']:.4f} (var {v['cv_r2_gain']:.4f}) | "
            f"part_r={r['partial_r']:.4f} vs canon {c['partial_r']:.4f} (var {v['partial_r']:.4f})"
        )
