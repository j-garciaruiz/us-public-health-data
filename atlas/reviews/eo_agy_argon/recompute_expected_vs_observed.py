#!/usr/bin/env python3
"""Independent computation of county mortality SMRs (Task 1) and PLACES vs observed outcomes (Task 2).

Author: Antigravity (Gemini 4 Argon High)
Date: 2026-10-20
"""

import argparse
from io import StringIO
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent

COV_COLS_ALL = [
    "age_18_24",
    "age_25_34",
    "age_35_44",
    "age_45_54",
    "age_55_64",
    "age_65_74",
    "age_75p",
    "male",
    "nh_white",
    "nh_black",
    "nh_aian",
    "nh_asian",
    "nh_nhpi",
    "hispanic",
    "nh_other_multi",
    "edu_lt_hs",
    "edu_hs",
    "edu_some_college",
    "edu_ba_plus",
    "pov150_adults",
]

COV_COLS_DROP1 = [
    "age_25_34",
    "age_35_44",
    "age_45_54",
    "age_55_64",
    "age_65_74",
    "age_75p",
    "male",
    "nh_black",
    "nh_aian",
    "nh_asian",
    "nh_nhpi",
    "hispanic",
    "nh_other_multi",
    "edu_lt_hs",
    "edu_hs",
    "edu_some_college",
    "pov150_adults",
]


def load_b01001_age_bins() -> pd.DataFrame:
    """Load ACS 2019-2023 B01001 county age counts mapped to WONDER 10-year age bins."""
    with open(RAW / "acs_sf" / "acsdt5y2023-b01001.dat", "r", encoding="utf-8") as f:
        header = f.readline().strip().split("|")
        rows = [line.strip().split("|") for line in f if line.startswith("0500000US")]
    b01 = pd.DataFrame(rows, columns=header)
    b01["fips"] = b01["GEO_ID"].str[-5:]
    b01 = b01.set_index("fips")
    for c in b01.columns:
        if c != "GEO_ID":
            b01[c] = b01[c].astype(float)

    age_bins_b01 = {
        "0-4": ([3], [27]),
        "5-14": ([4, 5], [28, 29]),
        "15-24": ([6, 7, 8, 9, 10], [30, 31, 32, 33, 34]),
        "25-34": ([11, 12], [35, 36]),
        "35-44": ([13, 14], [37, 38]),
        "45-54": ([15, 16], [39, 40]),
        "55-64": ([17, 18, 19], [41, 42, 43]),
        "65-74": ([20, 21, 22], [44, 45, 46]),
        "75-84": ([23, 24], [47, 48]),
        "85+": ([25], [49]),
    }

    b01_ages = pd.DataFrame(index=b01.index)
    for k, (m_idx, f_idx) in age_bins_b01.items():
        b01_ages[k] = sum(b01[f"B01001_E{i:03d}"] for i in m_idx) + sum(
            b01[f"B01001_E{i:03d}"] for i in f_idx
        )
    b01_ages["acs_total_pop"] = b01["B01001_E001"]
    return b01_ages


def build_mortality_smr(b01_ages: pd.DataFrame, out_dir: Path) -> tuple[pd.DataFrame, dict]:
    """Task 1: Build county SMRs by indirect age standardization and run construction checks."""
    with open(RAW / "wonder" / "national_age_2018_2024.txt", "r", encoding="utf-8") as f:
        n_lines = []
        for line in f:
            if line.startswith('"---"'):
                break
            n_lines.append(line)
    nat = pd.read_csv(StringIO("".join(n_lines)), sep="\t", dtype=str)
    nat["Deaths_num"] = pd.to_numeric(nat["Deaths"], errors="coerce").fillna(0.0)
    nat["Pop_num"] = pd.to_numeric(nat["Population"], errors="coerce")

    age_map_wonder = {
        "1": "0-4",
        "1-4": "0-4",
        "5-14": "5-14",
        "15-24": "15-24",
        "25-34": "25-34",
        "35-44": "35-44",
        "45-54": "45-54",
        "55-64": "55-64",
        "65-74": "65-74",
        "75-84": "75-84",
        "85+": "85+",
    }
    nat_valid = nat[nat["Ten-Year Age Groups Code"].isin(age_map_wonder.keys())].copy()
    nat_valid["age_bin"] = nat_valid["Ten-Year Age Groups Code"].map(age_map_wonder)
    nat_binned = nat_valid.groupby(
        ["UCD - ICD-10 113 Cause List Code", "age_bin"], as_index=False
    )[["Deaths_num", "Pop_num"]].sum()
    nat_binned["nat_rate"] = nat_binned["Deaths_num"] / nat_binned["Pop_num"]

    with open(RAW / "wonder" / "county_cause_2018_2024.txt", "r", encoding="utf-8") as f:
        c_lines = []
        for line in f:
            if line.startswith('"---"'):
                break
            c_lines.append(line)
    cty = pd.read_csv(StringIO("".join(c_lines)), sep="\t", dtype=str)
    # Never output or expose suppressed counts (which appear as "Suppressed" anyway);
    # enforce strict > 9 check on numeric deaths as an extra safety guard.
    cty["Deaths_num"] = pd.to_numeric(cty["Deaths"], errors="coerce")
    cty.loc[cty["Deaths_num"] <= 9, "Deaths_num"] = np.nan
    cty["wonder_pop_7yr"] = pd.to_numeric(cty["Population"], errors="coerce")

    cause_meta = {
        "GR113-046": ("diabetes", "diabetes"),
        "GR113-054": ("heart_disease", "chd"),
        "GR113-070": ("stroke", "stroke"),
        "GR113-082": ("copd", "copd"),
    }

    age_cols = list(age_bins_order := ["0-4", "5-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75-84", "85+"])
    b01_50dc = b01_ages[~b01_ages.index.str.startswith("72")].copy()
    b01_shares = b01_50dc[age_cols].div(b01_50dc["acs_total_pop"], axis=0)

    # Remap 1-to-1 legacy FIPS codes in WONDER:
    # 46113 (Shannon County, SD) -> 46102 (Oglala Lakota County, SD)
    # 02270 (Wade Hampton Census Area, AK) -> 02158 (Kusilvak Census Area, AK)
    cty["fips_mapped"] = cty["County Code"].replace({"46113": "46102", "02270": "02158"})

    smr_rows = []
    reconciliation_diag = {}

    for cause_code, (cause_name, places_measure) in cause_meta.items():
        rates = (
            nat_binned[nat_binned["UCD - ICD-10 113 Cause List Code"] == cause_code]
            .set_index("age_bin")
            .loc[age_cols, "nat_rate"]
        )
        # Expected deaths per person-year for each county based on its ACS age shares
        exp_rate_per_py = b01_shares @ rates
        # Method A: county person-years = 7 * ACS B01001 population
        exp_deaths_acs7 = (b01_50dc[age_cols] * 7.0) @ rates
        # Method C: internal ACS standardization (national deaths / (7 * national ACS pop by age))
        nat_deaths_by_age = (
            nat_binned[nat_binned["UCD - ICD-10 113 Cause List Code"] == cause_code]
            .set_index("age_bin")
            .loc[age_cols, "Deaths_num"]
        )
        rates_acs_denom = nat_deaths_by_age / (b01_50dc[age_cols].sum(axis=0) * 7.0)
        exp_deaths_acs_internal = (b01_50dc[age_cols] * 7.0) @ rates_acs_denom

        sub_c = cty[cty["UCD - ICD-10 113 Cause List Code"] == cause_code].copy()
        sub_c["cause_code"] = cause_code
        sub_c["cause"] = cause_name
        sub_c["places_measure"] = places_measure

        # Map expected deaths (both with 46113/02270 remapped and unmapped)
        sub_c["exp_acs7_mapped"] = sub_c["fips_mapped"].map(exp_deaths_acs7)
        sub_c["exp_acs7_unmapped"] = sub_c["County Code"].map(exp_deaths_acs7)
        sub_c["exp_wpop_mapped"] = sub_c["wonder_pop_7yr"] * sub_c["fips_mapped"].map(exp_rate_per_py)
        sub_c["exp_wpop_unmapped"] = sub_c["wonder_pop_7yr"] * sub_c["County Code"].map(exp_rate_per_py)
        sub_c["exp_acs_internal_mapped"] = sub_c["fips_mapped"].map(exp_deaths_acs_internal)

        sub_c["smr_acs7_mapped"] = sub_c["Deaths_num"] / sub_c["exp_acs7_mapped"]
        sub_c["smr_acs7_unmapped"] = sub_c["Deaths_num"] / sub_c["exp_acs7_unmapped"]
        sub_c["smr_wpop_mapped"] = sub_c["Deaths_num"] / sub_c["exp_wpop_mapped"]
        sub_c["smr_wpop_unmapped"] = sub_c["Deaths_num"] / sub_c["exp_wpop_unmapped"]
        sub_c["smr_acs_internal_mapped"] = sub_c["Deaths_num"] / sub_c["exp_acs_internal_mapped"]

        smr_rows.append(sub_c)

        nat_c = nat[nat["UCD - ICD-10 113 Cause List Code"] == cause_code]
        nat_known = float(nat_c[nat_c["Ten-Year Age Groups Code"] != "NS"]["Deaths_num"].sum())
        nat_ns = float(nat_c[nat_c["Ten-Year Age Groups Code"] == "NS"]["Deaths_num"].sum())
        ct_deaths = float(sub_c[sub_c["County Code"].str.startswith("09")]["Deaths_num"].sum())
        valdez_deaths = float(sub_c[sub_c["County Code"] == "02261"]["Deaths_num"].sum())

        valid_m = sub_c.dropna(subset=["Deaths_num", "exp_acs7_mapped"])
        reconciliation_diag[cause_code] = {
            "cause": cause_name,
            "places_measure": places_measure,
            "nat_known_age_deaths": nat_known,
            "nat_not_stated_age_deaths": nat_ns,
            "nat_total_deaths": nat_known + nat_ns,
            "sum_expected_all_3144_acs_counties_acs7": float(exp_deaths_acs7.sum()),
            "ratio_expected_acs7_to_nat_known": float(exp_deaths_acs7.sum() / nat_known),
            "sum_obs_unsuppressed_all_wonder_counties": float(sub_c["Deaths_num"].sum()),
            "n_suppressed_wonder_counties": int(sub_c["Deaths"].eq("Suppressed").sum()),
            "implied_suppressed_deaths_total": float((nat_known + nat_ns) - sub_c["Deaths_num"].sum()),
            "ct_legacy_counties_obs_deaths": ct_deaths,
            "valdez_cordova_02261_obs_deaths": valdez_deaths,
            "n_matched_unsuppressed_mapped": int(len(valid_m)),
            "matched_sum_obs": float(valid_m["Deaths_num"].sum()),
            "matched_sum_exp_acs7": float(valid_m["exp_acs7_mapped"].sum()),
            "matched_obs_over_exp_acs7": float(valid_m["Deaths_num"].sum() / valid_m["exp_acs7_mapped"].sum()),
            "matched_sum_exp_wpop": float(valid_m["exp_wpop_mapped"].sum()),
            "matched_obs_over_exp_wpop": float(valid_m["Deaths_num"].sum() / valid_m["exp_wpop_mapped"].sum()),
        }

    smr_df = pd.concat(smr_rows, ignore_index=True)
    # Save public-safe SMR table (never saving any count <= 9; suppressed rows have NA for Deaths_num and SMR)
    save_cols = [
        "fips_mapped",
        "County Code",
        "County",
        "cause_code",
        "cause",
        "places_measure",
        "Deaths_num",
        "wonder_pop_7yr",
        "exp_acs7_mapped",
        "exp_wpop_mapped",
        "smr_acs7_mapped",
        "smr_wpop_mapped",
        "smr_acs7_unmapped",
        "smr_wpop_unmapped",
    ]
    smr_df[save_cols].to_csv(out_dir / "recomputed_smr.csv", index=False)
    return smr_df, reconciliation_diag


def build_X(
    df_sub: pd.DataFrame,
    extra_cols: list[str] | None = None,
    include_state: bool = True,
    drop_first: bool = False,
) -> np.ndarray:
    """Build design matrix for OLS / CV."""
    parts = [np.ones((len(df_sub), 1))]
    cov_cols = COV_COLS_DROP1 if drop_first else COV_COLS_ALL
    if include_state:
        parts.append(df_sub[cov_cols].to_numpy(float))
        st = pd.get_dummies(df_sub["stateabbr"], drop_first=drop_first, dtype=float).to_numpy()
        parts.append(st)
    if extra_cols:
        parts.append(df_sub[extra_cols].to_numpy(float))
    return np.hstack(parts)


def kfold_cv_r2(
    X: np.ndarray, y: np.ndarray, k: int = 10, seed: int = 42, mode: str = "pooled"
) -> float:
    """Compute 10-fold CV R2 (either pooled out-of-fold or mean across folds)."""
    n = len(y)
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    folds = np.array_split(idx, k)
    yhat_oof = np.zeros(n)
    fold_r2s = []
    for f in folds:
        tr = np.setdiff1d(np.arange(n), f)
        beta, _, _, _ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
        pred = X[f] @ beta
        yhat_oof[f] = pred
        ss_res_f = float(np.sum((y[f] - pred) ** 2))
        ss_tot_f = float(np.sum((y[f] - np.mean(y[f])) ** 2))
        fold_r2s.append(1.0 - ss_res_f / ss_tot_f)
    if mode == "mean_fold":
        return float(np.mean(fold_r2s))
    ss_res = float(np.sum((y - yhat_oof) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot


def ols_resid_and_r2(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    beta, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    r2 = 1.0 - float(np.sum(resid**2)) / float(np.sum((y - np.mean(y)) ** 2))
    return resid, r2


def eval_pair(
    df_sub: pd.DataFrame,
    obs_col: str,
    places_col: str,
    extra_demo_cols: list[str] | None = None,
    seed: int = 42,
    drop_first: bool = False,
) -> dict:
    """Evaluate a single (observed, PLACES) pair on the shared non-missing sample."""
    req_cols = [obs_col, places_col, "stateabbr"] + COV_COLS_ALL + (extra_demo_cols or [])
    sub = df_sub.dropna(subset=req_cols).copy()
    y = sub[obs_col].to_numpy(float)
    p = sub[places_col].to_numpy(float)

    raw_r = float(np.corrcoef(y, p)[0, 1])

    X_demo = build_X(sub, extra_cols=extra_demo_cols, include_state=True, drop_first=drop_first)
    X_places = np.column_stack([np.ones(len(sub)), p])
    X_both = build_X(
        sub,
        extra_cols=(extra_demo_cols or []) + [places_col],
        include_state=True,
        drop_first=drop_first,
    )

    cv_demo = kfold_cv_r2(X_demo, y, k=10, seed=seed, mode="pooled")
    cv_places = kfold_cv_r2(X_places, y, k=10, seed=seed, mode="pooled")
    cv_both = kfold_cv_r2(X_both, y, k=10, seed=seed, mode="pooled")
    cv_gain = cv_both - cv_demo

    # Also compute with seed=0 and mean_fold for sensitivity check
    cv_demo_s0 = kfold_cv_r2(X_demo, y, k=10, seed=0, mode="pooled")
    cv_places_s0 = kfold_cv_r2(X_places, y, k=10, seed=0, mode="pooled")
    cv_both_s0 = kfold_cv_r2(X_both, y, k=10, seed=0, mode="pooled")

    e_y, r2_in_demo = ols_resid_and_r2(X_demo, y)
    e_p, r2_in_places_on_demo = ols_resid_and_r2(X_demo, p)
    _, r2_in_places = ols_resid_and_r2(X_places, y)
    _, r2_in_both = ols_resid_and_r2(X_both, y)

    partial_r = float(np.corrcoef(e_y, e_p)[0, 1])

    # Also check partial_r if PLACES is residualized only on demographics+state (without MA share)
    if extra_demo_cols:
        X_demo_no_extra = build_X(sub, extra_cols=None, include_state=True, drop_first=drop_first)
        e_p_no_extra, _ = ols_resid_and_r2(X_demo_no_extra, p)
        partial_r_p_no_extra = float(np.corrcoef(e_y, e_p_no_extra)[0, 1])
    else:
        partial_r_p_no_extra = partial_r

    return {
        "n": int(len(sub)),
        "raw_r": raw_r,
        "cv_r2_demo_state": cv_demo,
        "cv_r2_places_alone": cv_places,
        "cv_r2_demo_state_places": cv_both,
        "cv_r2_gain": cv_gain,
        "partial_r": partial_r,
        "partial_r_p_no_extra": partial_r_p_no_extra,
        "insample_r2_demo_state": r2_in_demo,
        "insample_r2_places_alone": r2_in_places,
        "insample_r2_demo_state_places": r2_in_both,
        "insample_r2_gain": r2_in_both - r2_in_demo,
        "insample_r2_places_explained_by_demo": r2_in_places_on_demo,
        "cv_r2_demo_state_seed0": cv_demo_s0,
        "cv_r2_places_alone_seed0": cv_places_s0,
        "cv_r2_demo_state_places_seed0": cv_both_s0,
        "cv_r2_gain_seed0": cv_both_s0 - cv_demo_s0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    b01_ages = load_b01001_age_bins()
    smr_df, reconciliation_diag = build_mortality_smr(b01_ages, out_dir)

    # Load base PLACES and ACS covariates
    places = pd.read_csv(RAW / "places_county_2025.csv", dtype={"countyfips": str})
    places["fips"] = places["countyfips"].str.zfill(5)
    acs_cov = pd.read_csv(RAW / "acs_county_2023.csv", dtype={"fips": str})
    acs_cov["fips"] = acs_cov["fips"].str.zfill(5)
    base = places.merge(acs_cov, on="fips", how="inner")

    # Load Medicare GV 2023
    gv = pd.read_csv(RAW / "medicare_gv_county_2023.csv", dtype={"fips": str})
    gv["fips"] = gv["fips"].str.zfill(5)
    for c in ["BENES_TOTAL_CNT", "BENES_OM_CNT", "BENES_MA_CNT"]:
        gv[c] = pd.to_numeric(gv[c], errors="coerce")
    gv["ma_share_om_ma"] = gv["BENES_MA_CNT"] / (gv["BENES_OM_CNT"] + gv["BENES_MA_CNT"])
    gv["ma_share_total"] = gv["BENES_MA_CNT"] / gv["BENES_TOTAL_CNT"]

    # Load MMD 2023 (fltr == 2)
    mmd = pd.read_csv(RAW / "mmd_prevalence_2023.csv", dtype={"fips": str})
    mmd["fips"] = mmd["fips"].str.zfill(5)
    mmd_f2 = mmd[(mmd["fltr"] == 2) & (mmd["places_measure"].notna())].copy()

    # Load ACS disability 2023
    dis = pd.read_csv(RAW / "acs_disability_2023.csv", dtype={"fips": str})
    dis["fips"] = dis["fips"].str.zfill(5)

    results_rows = []

    # 1. 11 Medicare conditions vs PLACES
    med_df = base.merge(
        gv[["fips", "BENES_TOTAL_CNT", "BENES_OM_CNT", "BENES_MA_CNT", "ma_share_om_ma", "ma_share_total"]],
        on="fips",
        how="left",
    )
    med_pairs = (
        mmd_f2[["condition", "places_measure"]]
        .drop_duplicates()
        .sort_values("condition")
        .to_dict(orient="records")
    )

    for pair in med_pairs:
        cond = pair["condition"]
        pm = pair["places_measure"]
        c_df = mmd_f2[mmd_f2["condition"] == cond][["fips", "rate"]].rename(columns={"rate": "obs_rate"})
        # Treat 0 as suppressed (and also record if 0 is kept in a variant)
        c_df["obs_rate_pos"] = c_df["obs_rate"].where(c_df["obs_rate"] > 0, np.nan)
        m_merged = med_df.merge(c_df, on="fips", how="inner")

        for places_suffix in ["adjprev", "crudeprev"]:
            p_col = f"{pm}_{places_suffix}"
            for ma_col, ma_label in [("ma_share_om_ma", "MA/(OM+MA)"), ("ma_share_total", "MA/TOTAL")]:
                for zero_rule, y_col in [("drop_zero", "obs_rate_pos"), ("keep_zero", "obs_rate")]:
                    for sub_name, sub_df in [
                        ("all", m_merged),
                        ("large", m_merged[m_merged["BENES_OM_CNT"] >= 5000]),
                    ]:
                        stats = eval_pair(sub_df, y_col, p_col, extra_demo_cols=[ma_col], seed=42)
                        results_rows.append(
                            {
                                "domain": "medicare",
                                "observed_outcome": cond,
                                "places_measure": pm,
                                "places_type": places_suffix,
                                "variant": f"{ma_label}_{zero_rule}",
                                "subset": sub_name,
                                **stats,
                            }
                        )

    # 2. 6 ACS disability types vs PLACES
    dis_merged = base.merge(dis, on="fips", how="inner")
    dis_pairs = [
        ("acs_hearing", "hearing"),
        ("acs_vision", "vision"),
        ("acs_cognition", "cognition"),
        ("acs_mobility", "mobility"),
        ("acs_selfcare", "selfcare"),
        ("acs_indeplive", "indeplive"),
    ]
    for obs_col, pm in dis_pairs:
        for places_suffix in ["adjprev", "crudeprev"]:
            p_col = f"{pm}_{places_suffix}"
            for sub_name, sub_df in [
                ("all", dis_merged),
                ("large", dis_merged[dis_merged["adults"] >= 20000]),
            ]:
                stats = eval_pair(sub_df, obs_col, p_col, extra_demo_cols=None, seed=42)
                results_rows.append(
                    {
                        "domain": "disability",
                        "observed_outcome": obs_col,
                        "places_measure": pm,
                        "places_type": places_suffix,
                        "variant": "standard",
                        "subset": sub_name,
                        **stats,
                    }
                )

    # 3. 4 Mortality causes vs PLACES
    mort_causes = [
        ("GR113-046", "diabetes", "diabetes"),
        ("GR113-054", "heart_disease", "chd"),
        ("GR113-070", "stroke", "stroke"),
        ("GR113-082", "copd", "copd"),
    ]
    for cause_code, cause_name, pm in mort_causes:
        sub_smr = smr_df[smr_df["cause_code"] == cause_code].copy()
        for fips_mode, fips_col in [("mapped_fips", "fips_mapped"), ("unmapped_fips", "County Code")]:
            m_smr = base.merge(sub_smr, left_on="fips", right_on=fips_col, how="inner")
            for smr_mode, smr_col, exp_col in [
                ("acs7", f"smr_acs7_{fips_mode.split('_')[0]}", f"exp_acs7_{fips_mode.split('_')[0]}"),
                ("wpop", f"smr_wpop_{fips_mode.split('_')[0]}", f"exp_wpop_{fips_mode.split('_')[0]}"),
            ]:
                for places_suffix in ["adjprev", "crudeprev"]:
                    p_col = f"{pm}_{places_suffix}"
                    for sub_name, sub_df in [
                        ("all", m_smr),
                        ("large", m_smr[m_smr[exp_col] >= 100.0]),
                    ]:
                        stats = eval_pair(sub_df, smr_col, p_col, extra_demo_cols=None, seed=42)
                        results_rows.append(
                            {
                                "domain": "mortality",
                                "observed_outcome": cause_name,
                                "places_measure": pm,
                                "places_type": places_suffix,
                                "variant": f"{smr_mode}_{fips_mode}",
                                "subset": sub_name,
                                **stats,
                            }
                        )

    res_df = pd.DataFrame(results_rows)
    res_df.to_csv(out_dir / "recomputed_places_vs_observed_all_variants.csv", index=False)

    # Filter to primary canonical specification:
    # - PLACES adjprev (plus crudeprev for disability in a check)
    # - Medicare: MA/(OM+MA) with 0 treated as suppressed (drop_zero)
    # - Disability: standard
    # - Mortality: acs7_mapped_fips (and wpop_mapped_fips)
    canonical_mask = (
        ((res_df["domain"] == "medicare") & (res_df["places_type"] == "adjprev") & (res_df["variant"] == "MA/(OM+MA)_drop_zero"))
        | ((res_df["domain"] == "disability") & (res_df["places_type"] == "adjprev") & (res_df["variant"] == "standard"))
        | ((res_df["domain"] == "mortality") & (res_df["places_type"] == "adjprev") & (res_df["variant"] == "acs7_mapped_fips"))
    )
    canon_df = res_df[canonical_mask].copy()
    canon_df.to_csv(out_dir / "recomputed_places_vs_observed.csv", index=False)

    dom_summary = {}
    for (dom, sub_name), grp in canon_df.groupby(["domain", "subset"]):
        dom_summary[f"{dom}_{sub_name}"] = {
            col: {
                "median": float(grp[col].median()),
                "mean": float(grp[col].mean()),
                "min": float(grp[col].min()),
                "max": float(grp[col].max()),
            }
            for col in [
                "n",
                "raw_r",
                "cv_r2_demo_state",
                "cv_r2_places_alone",
                "cv_r2_demo_state_places",
                "cv_r2_gain",
                "partial_r",
            ]
        }

    summary = {
        "task1_reconciliation": reconciliation_diag,
        "canonical_summary_by_domain_and_subset": dom_summary,
    }
    with open(out_dir / "recomputed_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Saved recomputed_smr.csv, recomputed_places_vs_observed.csv, and recomputed_summary.json.")
    cols_print = [
        "domain",
        "observed_outcome",
        "places_measure",
        "subset",
        "n",
        "raw_r",
        "cv_r2_demo_state",
        "cv_r2_places_alone",
        "cv_r2_demo_state_places",
        "cv_r2_gain",
        "partial_r",
    ]
    print(canon_df[cols_print].to_string(index=False))


if __name__ == "__main__":
    main()
