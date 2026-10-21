#!/usr/bin/env python3
"""Compare independent numbers against outputs/expected_vs_observed/ and scripts/."""

import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path("/Users/hari/.gemini/antigravity-cli/brain/5c0d75a6-5a8a-411d-9863-4546aaa291ce/scratch")

# 1. Compare wonder_county_smr.csv with our recomputed SMRs
their_smr = pd.read_csv(ROOT / "data" / "raw" / "wonder_county_smr.csv", dtype={"fips": str})
our_smr = pd.read_csv(SCRATCH / "recomputed_smr.csv", dtype={"fips_mapped": str, "County Code": str})

cause_map = {"diabetes": "diabetes", "heart": "heart_disease", "stroke": "stroke", "clrd": "copd"}
their_smr["cause_our"] = their_smr["cause"].map(cause_map)

m_smr = their_smr.merge(
    our_smr,
    left_on=["fips", "cause_our"],
    right_on=["fips_mapped", "cause"],
    how="outer",
    suffixes=("_theirs", "_ours"),
)

print("=== 1. SMR COMPARISON ===")
print("Their rows:", len(their_smr), "Our rows:", len(our_smr))
in_ours_not_theirs = m_smr[m_smr["fips"].isna()][["fips_mapped", "County Code", "County", "cause_ours", "Deaths_num", "wonder_pop_7yr"]].drop_duplicates()
print("In ours/WONDER but dropped in their wonder_county_smr.csv:")
print(in_ours_not_theirs.groupby(["fips_mapped", "County Code", "County"], dropna=False)["wonder_pop_7yr"].first().to_string())

both_smr = m_smr.dropna(subset=["expected", "exp_wpop_mapped"]).copy()
print("Max abs diff in expected (their expected vs our exp_wpop_mapped):", (both_smr["expected"] - both_smr["exp_wpop_mapped"]).abs().max())
print("Max abs diff in expected (their expected vs our exp_acs7_mapped):", (both_smr["expected"] - both_smr["exp_acs7_mapped"]).abs().max())
both_pos = both_smr.dropna(subset=["smr", "smr_wpop_mapped"])
print("Max abs diff in SMR on positive deaths (their smr vs our smr_wpop_mapped):", (both_pos["smr"] - both_pos["smr_wpop_mapped"]).abs().max())

# Check zero-death counties in their_smr
zero_deaths = their_smr[their_smr["observed"] == 0]
print("Counties with observed == 0 in their_smr by cause:", zero_deaths.groupby("cause").size().to_dict())

# 2. Compare places_vs_observed.csv with our variants
their_pvo = pd.read_csv(ROOT / "outputs" / "expected_vs_observed" / "places_vs_observed.csv")
our_all = pd.read_csv(SCRATCH / "recomputed_places_vs_observed_all_variants.csv")

print("\n=== 2. PLACES_VS_OBSERVED COMPARISON ===")
# Match each row of their_pvo to our primary canonical table AND to the matching variant in our_all
our_canon = pd.read_csv(ROOT / "reviews" / "eo_agy_argon" / "recomputed_places_vs_observed.csv")

name_to_obs = {
    "Diabetes": ("medicare", "diabetes"),
    "COPD": ("medicare", "copd"),
    "Depression": ("medicare", "depression"),
    "High blood pressure": ("medicare", "hypertension"),
    "Coronary heart disease": ("medicare", "ischemic_heart_disease"),
    "Stroke": ("medicare", "stroke_tia"),
    "Asthma": ("medicare", "asthma"),
    "Obesity": ("medicare", "obesity"),
    "Arthritis": ("medicare", "arthritis"),
    "High cholesterol": ("medicare", "hyperlipidemia"),
    "Cancer": ("medicare", "cancer_4_sites"),
    "Hearing disability": ("disability", "acs_hearing"),
    "Vision disability": ("disability", "acs_vision"),
    "Cognitive disability": ("disability", "acs_cognition"),
    "Mobility disability": ("disability", "acs_mobility"),
    "Self-care disability": ("disability", "acs_selfcare"),
    "Independent-living disability": ("disability", "acs_indeplive"),
    "Diabetes deaths (SMR)": ("mortality", "diabetes"),
    "Heart disease deaths (SMR)": ("mortality", "heart_disease"),
    "Stroke deaths (SMR)": ("mortality", "stroke"),
    "Chronic lower respiratory deaths (SMR)": ("mortality", "copd"),
}

comp_rows = []
for _, r in their_pvo.iterrows():
    dom, obs_name = name_to_obs[r["outcome"]]
    sub = "all" if r["sample"] == "all" else "large"
    c_row = our_canon[(our_canon["domain"] == dom) & (our_canon["observed_outcome"] == obs_name) & (our_canon["subset"] == sub)].iloc[0]

    # Also find the variant in our_all where disability uses crudeprev and mortality uses wpop
    if dom == "medicare":
        v_row = our_all[(our_all["domain"] == dom) & (our_all["observed_outcome"] == obs_name) & (our_all["subset"] == sub) & (our_all["places_type"] == "adjprev") & (our_all["variant"] == "MA/(OM+MA)_drop_zero")].iloc[0]
    elif dom == "disability":
        v_row = our_all[(our_all["domain"] == dom) & (our_all["observed_outcome"] == obs_name) & (our_all["subset"] == sub) & (our_all["places_type"] == "crudeprev") & (our_all["variant"] == "standard")].iloc[0]
    else:
        v_row = our_all[(our_all["domain"] == dom) & (our_all["observed_outcome"] == obs_name) & (our_all["subset"] == sub) & (our_all["places_type"] == "adjprev") & (our_all["variant"] == "wpop_unmapped_fips")].iloc[0]

    comp_rows.append({
        "outcome": r["outcome"],
        "domain": dom,
        "sample": r["sample"],
        "n_theirs": int(r["n"]),
        "n_canon": int(c_row["n"]),
        "n_matched_var": int(v_row["n"]),
        "r_raw_theirs": r["r_raw"],
        "r_raw_canon": c_row["raw_r"],
        "r_raw_var": v_row["raw_r"],
        "cv_demo_theirs": r["cv_r2_demo"],
        "cv_demo_canon": c_row["cv_r2_demo_state"],
        "cv_demo_var": v_row["cv_r2_demo_state"],
        "cv_places_theirs": r["cv_r2_places"],
        "cv_places_canon": c_row["cv_r2_places_alone"],
        "cv_places_var": v_row["cv_r2_places_alone"],
        "cv_both_theirs": r["cv_r2_demo_places"],
        "cv_both_canon": c_row["cv_r2_demo_state_places"],
        "cv_both_var": v_row["cv_r2_demo_state_places"],
        "gain_theirs": r["gain"],
        "gain_canon": c_row["cv_r2_gain"],
        "gain_var": v_row["cv_r2_gain"],
        "partial_r_theirs": r["partial_r"],
        "partial_r_canon": c_row["partial_r"],
        "partial_r_var": v_row["partial_r"],
    })

comp_df = pd.DataFrame(comp_rows)
print(comp_df.to_string(index=False))
comp_df.to_csv(SCRATCH / "comparison_table.csv", index=False)
