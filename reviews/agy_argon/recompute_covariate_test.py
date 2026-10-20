#!/usr/bin/env python3
"""Independent recomputation and methodological diagnostics for the PLACES covariate test.

Author: Antigravity (Gemini 4 Argon High)
Date: 2026-10-20
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = Path(__file__).resolve().parent


def verify_acs_csv_against_raw_sf() -> dict:
    """Verify data/raw/acs_county_2023.csv against the 5 raw ACS 5-year summary files."""
    acs = pd.read_csv(DATA_RAW / "acs_county_2023.csv", dtype={"fips": str}).set_index("fips")

    def load_county_rows(table_id: str) -> pd.DataFrame:
        path = DATA_RAW / "acs_sf" / f"acsdt5y2023-{table_id}.dat"
        with open(path, "r", encoding="utf-8") as f:
            header = f.readline().strip().split("|")
            rows = []
            for line in f:
                if line.startswith("0500000US"):
                    parts = line.strip().split("|")
                    rows.append(parts)
        df_raw = pd.DataFrame(rows, columns=header)
        df_raw["fips"] = df_raw["GEO_ID"].str[-5:]
        return df_raw.set_index("fips")

    b01 = load_county_rows("b01001")
    b03 = load_county_rows("b03002")
    b15 = load_county_rows("b15003")
    b17 = load_county_rows("b17024")
    b27 = load_county_rows("b27010")

    # Convert estimate and MOE columns needed to float
    for df_t in (b01, b03, b15, b17, b27):
        for c in df_t.columns:
            if c != "GEO_ID":
                df_t[c] = df_t[c].astype(float)

    rebuilt = pd.DataFrame(index=acs.index)

    # B01001: Sex by age (adults 18+)
    m_18p = sum(b01[f"B01001_E{i:03d}"] for i in range(7, 26))
    f_18p = sum(b01[f"B01001_E{i:03d}"] for i in range(31, 50))
    adults = m_18p + f_18p

    age_groups = {
        "age_18_24": ([7, 8, 9, 10], [31, 32, 33, 34]),
        "age_25_34": ([11, 12], [35, 36]),
        "age_35_44": ([13, 14], [37, 38]),
        "age_45_54": ([15, 16], [39, 40]),
        "age_55_64": ([17, 18, 19], [41, 42, 43]),
        "age_65_74": ([20, 21, 22], [44, 45, 46]),
        "age_75p": ([23, 24, 25], [47, 48, 49]),
    }
    for col, (m_idx, f_idx) in age_groups.items():
        num = sum(b01[f"B01001_E{i:03d}"] for i in m_idx) + sum(
            b01[f"B01001_E{i:03d}"] for i in f_idx
        )
        rebuilt[col] = num / adults

    rebuilt["male"] = m_18p / adults
    rebuilt["adults"] = adults

    # B03002: Hispanic origin by race (total population universe)
    tot_pop = b03["B03002_E001"]
    rebuilt["nh_white"] = b03["B03002_E003"] / tot_pop
    rebuilt["nh_black"] = b03["B03002_E004"] / tot_pop
    rebuilt["nh_aian"] = b03["B03002_E005"] / tot_pop
    rebuilt["nh_asian"] = b03["B03002_E006"] / tot_pop
    rebuilt["nh_nhpi"] = b03["B03002_E007"] / tot_pop
    rebuilt["hispanic"] = b03["B03002_E012"] / tot_pop
    rebuilt["nh_other_multi"] = (b03["B03002_E008"] + b03["B03002_E009"]) / tot_pop

    # B15003: Educational attainment (25+ population universe)
    tot_25p = b15["B15003_E001"]
    rebuilt["edu_lt_hs"] = sum(b15[f"B15003_E{i:03d}"] for i in range(2, 17)) / tot_25p
    rebuilt["edu_hs"] = (b15["B15003_E017"] + b15["B15003_E018"]) / tot_25p
    rebuilt["edu_some_college"] = (
        b15["B15003_E019"] + b15["B15003_E020"] + b15["B15003_E021"]
    ) / tot_25p
    rebuilt["edu_ba_plus"] = sum(b15[f"B15003_E{i:03d}"] for i in range(22, 26)) / tot_25p

    # B17024: Age by ratio of income to poverty level (adults 18+ in poverty universe)
    adult_pov_starts = [41, 54, 67, 80, 93, 106, 119]
    pov_denom = sum(b17[f"B17024_E{s:03d}"] for s in adult_pov_starts)
    pov_num = sum(
        sum(b17[f"B17024_E{s + k:03d}"] for k in range(1, 6)) for s in adult_pov_starts
    )
    rebuilt["pov150_adults"] = pov_num / pov_denom

    # B27010: Health insurance coverage by age (19-64 civilian noninstitutionalized)
    unins_denom = b27["B27010_E018"] + b27["B27010_E034"]
    unins_num = b27["B27010_E033"] + b27["B27010_E050"]
    rebuilt["acs_uninsured_19_64"] = unins_num / unins_denom

    # Compute standard error of acs_uninsured_19_64 from 90% MOEs (MOE = 1.645 * SE)
    moe_num2 = b27["B27010_M033"] ** 2 + b27["B27010_M050"] ** 2
    moe_den2 = b27["B27010_M018"] ** 2 + b27["B27010_M034"] ** 2
    p_unins = rebuilt["acs_uninsured_19_64"]
    rad = moe_num2 - (p_unins**2) * moe_den2
    rad = np.where(rad < 0, moe_num2 + (p_unins**2) * moe_den2, rad)
    se_unins = (np.sqrt(rad) / unins_denom) / 1.645

    max_diffs = {}
    for col in acs.columns:
        diff = np.max(np.abs(acs[col].to_numpy(float) - rebuilt[col].to_numpy(float)))
        max_diffs[col] = float(diff)

    return {
        "n_counties_checked": int(len(acs)),
        "max_abs_diff_by_column": max_diffs,
        "overall_max_abs_diff": float(max(max_diffs.values())),
        "se_unins_series": pd.Series(se_unins, index=b27.index),
    }


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


def build_design_matrix(
    df_sub: pd.DataFrame,
    include_state: bool = True,
    drop_first: bool = False,
    include_age: bool = True,
) -> np.ndarray:
    """Build OLS design matrix with intercept, county covariates, and optional state FEs."""
    cols = COV_COLS_DROP1 if drop_first else COV_COLS_ALL
    if not include_age:
        cols = [c for c in cols if not c.startswith("age_")]
    parts = [np.ones((len(df_sub), 1)), df_sub[cols].to_numpy(float)]
    if include_state:
        st = pd.get_dummies(
            df_sub["stateabbr"], drop_first=drop_first, dtype=float
        ).to_numpy()
        parts.append(st)
    return np.hstack(parts)


def ols_fit(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Return (yhat, resid, r2, adj_r2) using SVD least squares."""
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    resid = y - yhat
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    n = len(y)
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / (n - rank)
    return yhat, resid, r2, adj_r2


def kfold_cv_r2(
    X: np.ndarray, y: np.ndarray, k: int = 5, seed: int = 42
) -> float:
    """Compute out-of-fold R-squared for shuffled K-fold cross-validation."""
    n = len(y)
    rng = np.random.default_rng(seed)
    idx = np.arange(n)
    rng.shuffle(idx)
    folds = np.array_split(idx, k)
    yhat_oof = np.zeros(n)
    for f in folds:
        tr = np.setdiff1d(np.arange(n), f)
        beta, _, _, _ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
        yhat_oof[f] = X[f] @ beta
    ss_res = float(np.sum((y - yhat_oof) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot


def main() -> None:
    # 1. Verify ACS county CSV against raw summary files
    acs_verification = verify_acs_csv_against_raw_sf()
    se_unins_series = acs_verification.pop("se_unins_series")

    # 2. Load PLACES and merge with ACS covariates
    places = pd.read_csv(DATA_RAW / "places_county_2025.csv", dtype={"countyfips": str})
    places["countyfips"] = places["countyfips"].str.zfill(5)
    acs = pd.read_csv(DATA_RAW / "acs_county_2023.csv", dtype={"fips": str})
    acs["fips"] = acs["fips"].str.zfill(5)
    acs["se_uninsured_19_64"] = acs["fips"].map(se_unins_series)

    df = places.merge(acs, left_on="countyfips", right_on="fips", how="inner")

    # 3. Task 2(a): R-squared across all 40 age-adjusted (and 40 crude) measures
    measures = sorted(
        [c.replace("_adjprev", "") for c in places.columns if c.endswith("_adjprev")]
    )
    measure_rows = []
    residuals_sep = {"adjprev": {}, "crudeprev": {}}

    for suffix in ("adjprev", "crudeprev"):
        for m in measures:
            col = f"{m}_{suffix}"
            sub = df.dropna(subset=[col]).copy()
            y = sub[col].to_numpy(float)

            X_full = build_design_matrix(sub, include_state=True, drop_first=False)
            X_drop1 = build_design_matrix(sub, include_state=True, drop_first=True)
            X_cov = build_design_matrix(sub, include_state=False, drop_first=True)
            X_noage = build_design_matrix(
                sub, include_state=True, drop_first=False, include_age=False
            )
            X_state = np.hstack(
                [
                    np.ones((len(sub), 1)),
                    pd.get_dummies(sub["stateabbr"], drop_first=True, dtype=float).to_numpy(),
                ]
            )

            _, resid, r2_in, adj_r2 = ols_fit(X_full, y)
            _, _, r2_cov, _ = ols_fit(X_cov, y)
            _, _, r2_state, _ = ols_fit(X_state, y)
            _, _, r2_noage, _ = ols_fit(X_noage, y)

            cv5_full = kfold_cv_r2(X_full, y, k=5, seed=42)
            cv10_full = kfold_cv_r2(X_full, y, k=10, seed=42)
            cv5_drop1 = kfold_cv_r2(X_drop1, y, k=5, seed=42)
            cv10_drop1 = kfold_cv_r2(X_drop1, y, k=10, seed=42)
            cv5_cov = kfold_cv_r2(X_cov, y, k=5, seed=42)
            cv5_noage = kfold_cv_r2(X_noage, y, k=5, seed=42)

            # Logit-scale CV5 R2 evaluated on original prevalence scale
            p_val = y / 100.0
            z_logit = np.log(p_val / (1.0 - p_val))
            rng = np.random.default_rng(42)
            idx = np.arange(len(y))
            rng.shuffle(idx)
            folds = np.array_split(idx, 5)
            yhat_logit = np.zeros(len(y))
            for f in folds:
                tr = np.setdiff1d(np.arange(len(y)), f)
                b_l, _, _, _ = np.linalg.lstsq(X_full[tr], z_logit[tr], rcond=None)
                yhat_logit[f] = 100.0 / (1.0 + np.exp(-(X_full[f] @ b_l)))
            cv5_logit = 1.0 - float(np.sum((y - yhat_logit) ** 2)) / float(
                np.sum((y - np.mean(y)) ** 2)
            )

            residuals_sep[suffix][m] = pd.Series(resid, index=sub.index)

            measure_rows.append(
                {
                    "type": suffix,
                    "measure": m,
                    "n_counties": len(sub),
                    "r2_insample": r2_in,
                    "adj_r2_insample": adj_r2,
                    "cv5_r2": cv5_full,
                    "cv10_r2": cv10_full,
                    "cv5_r2_drop1": cv5_drop1,
                    "cv10_r2_drop1": cv10_drop1,
                    "r2_cov_only": r2_cov,
                    "cv5_r2_cov_only": cv5_cov,
                    "r2_state_only": r2_state,
                    "r2_no_age": r2_noage,
                    "cv5_r2_no_age": cv5_noage,
                    "cv5_r2_logit_link": cv5_logit,
                }
            )

    measures_df = pd.DataFrame(measure_rows)
    measures_df.to_csv(OUT_DIR / "recomputed_measures_r2.csv", index=False)

    adj_df = measures_df[measures_df["type"] == "adjprev"]
    crude_df = measures_df[measures_df["type"] == "crudeprev"]

    # 4. Task 2(b): Pairwise correlations and covariance shares (especially diabetes ~ foodinsecu)
    def compute_pair_stats(m1: str, m2: str, suffix: str) -> dict:
        c1, c2 = f"{m1}_{suffix}", f"{m2}_{suffix}"
        sub = df.dropna(subset=[c1, c2]).copy()
        y1 = sub[c1].to_numpy(float)
        y2 = sub[c2].to_numpy(float)

        # Method A: Separate regression on each measure's full available sample, then intersect
        e1_sep = residuals_sep[suffix][m1].loc[sub.index].to_numpy(float)
        e2_sep = residuals_sep[suffix][m2].loc[sub.index].to_numpy(float)

        # Method B: Pairwise regression on the common sample
        X_common = build_design_matrix(sub, include_state=True, drop_first=False)
        _, e1_pair, r2_1_pair, _ = ols_fit(X_common, y1)
        _, e2_pair, r2_2_pair, _ = ols_fit(X_common, y2)

        # Method C: Covariates only (no state FE) on common sample
        X_cov = build_design_matrix(sub, include_state=False, drop_first=False)
        _, e1_cov, _, _ = ols_fit(X_cov, y1)
        _, e2_cov, _, _ = ols_fit(X_cov, y2)

        # Method D: Logit scale on common sample
        z1 = np.log((y1 / 100.0) / (1.0 - y1 / 100.0))
        z2 = np.log((y2 / 100.0) / (1.0 - y2 / 100.0))
        _, e1_logit, _, _ = ols_fit(X_common, z1)
        _, e2_logit, _, _ = ols_fit(X_common, z2)

        raw_r = float(np.corrcoef(y1, y2)[0, 1])
        partial_r_sep = float(np.corrcoef(e1_sep, e2_sep)[0, 1])
        partial_r_pair = float(np.corrcoef(e1_pair, e2_pair)[0, 1])
        partial_r_cov_only = float(np.corrcoef(e1_cov, e2_cov)[0, 1])
        partial_r_logit = float(np.corrcoef(e1_logit, e2_logit)[0, 1])

        cov_raw = float(np.cov(y1, y2, ddof=1)[0, 1])
        cov_resid_sep = float(np.cov(e1_sep, e2_sep, ddof=1)[0, 1])
        cov_resid_pair = float(np.cov(e1_pair, e2_pair, ddof=1)[0, 1])
        cov_share_remaining = cov_resid_pair / cov_raw
        cov_share_explained = 1.0 - cov_share_remaining

        return {
            "pair": f"{m1}~{m2}",
            "type": suffix,
            "n_common": int(len(sub)),
            "raw_r": raw_r,
            "partial_r_separate_fit": partial_r_sep,
            "partial_r_pairwise_fit": partial_r_pair,
            "partial_r_cov_only_no_state": partial_r_cov_only,
            "partial_r_logit_scale": partial_r_logit,
            "cov_raw": cov_raw,
            "cov_resid_separate": cov_resid_sep,
            "cov_resid_pairwise": cov_resid_pair,
            "cov_share_remaining": cov_share_remaining,
            "cov_share_explained": cov_share_explained,
        }

    diab_food_adj = compute_pair_stats("diabetes", "foodinsecu", "adjprev")
    diab_food_crude = compute_pair_stats("diabetes", "foodinsecu", "crudeprev")

    # Compute all 780 pairs for adjprev to summarize overall correlation attenuation
    all_pairs_adj = []
    for i in range(len(measures)):
        for j in range(i + 1, len(measures)):
            all_pairs_adj.append(compute_pair_stats(measures[i], measures[j], "adjprev"))
    pairs_df = pd.DataFrame(all_pairs_adj)
    pairs_df.to_csv(OUT_DIR / "recomputed_all_pairs_adjprev.csv", index=False)

    strong_pairs_70 = pairs_df[pairs_df["raw_r"].abs() >= 0.70]
    strong_pairs_50 = pairs_df[pairs_df["raw_r"].abs() >= 0.50]

    # 5. Task 2(c): Uninsurance benchmark (PLACES access2_crudeprev vs ACS acs_uninsured_19_64)
    def eval_uninsurance_subset(sub_df: pd.DataFrame, subset_label: str) -> dict:
        res = {"subset": subset_label, "n": int(len(sub_df))}
        for col, label in [
            ("access2_crudeprev", "places_access2_crude"),
            ("access2_adjprev", "places_access2_adj"),
            ("acs_uninsured_19_64", "acs_uninsured_19_64"),
        ]:
            s = sub_df.dropna(subset=[col]).copy()
            y = s[col].to_numpy(float)
            if col == "acs_uninsured_19_64":
                y = y * 100.0  # percentage points (scale invariant for R2/corr, matches PLACES units)
            X_full = build_design_matrix(s, include_state=True, drop_first=False)
            X_drop1 = build_design_matrix(s, include_state=True, drop_first=True)
            X_cov = build_design_matrix(s, include_state=False, drop_first=False)
            X_noage = build_design_matrix(
                s, include_state=True, drop_first=False, include_age=False
            )

            _, resid, r2_in, adj_r2 = ols_fit(X_full, y)
            _, _, r2_cov, _ = ols_fit(X_cov, y)
            _, _, r2_noage, _ = ols_fit(X_noage, y)

            cv5 = kfold_cv_r2(X_full, y, k=5, seed=42)
            cv10 = kfold_cv_r2(X_full, y, k=10, seed=42)
            cv5_drop1 = kfold_cv_r2(X_drop1, y, k=5, seed=42)
            cv5_cov = kfold_cv_r2(X_cov, y, k=5, seed=42)
            cv5_noage = kfold_cv_r2(X_noage, y, k=5, seed=42)

            entry = {
                "n": int(len(s)),
                "r2_insample": r2_in,
                "adj_r2_insample": adj_r2,
                "cv5_r2": cv5,
                "cv10_r2": cv10,
                "cv5_r2_drop1": cv5_drop1,
                "r2_cov_only": r2_cov,
                "cv5_r2_cov_only": cv5_cov,
                "r2_no_age": r2_noage,
                "cv5_r2_no_age": cv5_noage,
            }

            if col == "acs_uninsured_19_64":
                se_pp = s["se_uninsured_19_64"].to_numpy(float) * 100.0
                var_y = float(np.var(y, ddof=1))
                mean_se2 = float(np.mean(se_pp**2))
                reliability = 1.0 - mean_se2 / var_y
                entry["var_pct_pts2"] = var_y
                entry["mean_sampling_err_var_pct_pts2"] = mean_se2
                entry["sampling_noise_share_of_var"] = mean_se2 / var_y
                entry["reliability_ceiling_r2"] = reliability
                entry["disattenuated_insample_r2"] = r2_in / reliability
                entry["disattenuated_cv5_r2"] = cv5 / reliability

            res[label] = entry

        # Also correlation between PLACES access2_crudeprev and ACS acs_uninsured_19_64 on common rows
        s_both = sub_df.dropna(subset=["access2_crudeprev", "acs_uninsured_19_64"]).copy()
        y_pl = s_both["access2_crudeprev"].to_numpy(float)
        y_ac = s_both["acs_uninsured_19_64"].to_numpy(float) * 100.0
        X_b = build_design_matrix(s_both, include_state=True, drop_first=False)
        _, e_pl, _, _ = ols_fit(X_b, y_pl)
        _, e_ac, _, _ = ols_fit(X_b, y_ac)
        X_b_cov = build_design_matrix(s_both, include_state=False, drop_first=False)
        _, e_pl_c, _, _ = ols_fit(X_b_cov, y_pl)
        _, e_ac_c, _, _ = ols_fit(X_b_cov, y_ac)

        cov_raw = float(np.cov(y_pl, y_ac, ddof=1)[0, 1])
        cov_res = float(np.cov(e_pl, e_ac, ddof=1)[0, 1])
        res["places_vs_acs_correlation"] = {
            "n_common": int(len(s_both)),
            "raw_r": float(np.corrcoef(y_pl, y_ac)[0, 1]),
            "partial_r_with_state_fe": float(np.corrcoef(e_pl, e_ac)[0, 1]),
            "partial_r_cov_only": float(np.corrcoef(e_pl_c, e_ac_c)[0, 1]),
            "cov_share_remaining": cov_res / cov_raw,
            "cov_share_explained": 1.0 - cov_res / cov_raw,
        }
        return res

    df_common_unins = df.dropna(subset=["access2_crudeprev", "acs_uninsured_19_64"]).copy()
    benchmark_results = {
        "common_all_counties_n2956": eval_uninsurance_subset(
            df_common_unins, "Common counties with non-missing PLACES access2 (n=2956)"
        ),
        "common_acs_adults_ge_20k_n1485": eval_uninsurance_subset(
            df_common_unins[df_common_unins["adults"] >= 20000],
            "Common counties with ACS adults >= 20,000 (n=1485)",
        ),
        "common_places_adults_ge_20k_n1495": eval_uninsurance_subset(
            df_common_unins[df_common_unins["totalpop18plus"] >= 20000],
            "Common counties with PLACES totalpop18plus >= 20,000 (n=1495)",
        ),
        "all_merged_counties_n3143": eval_uninsurance_subset(
            df, "All 3,143 merged counties (n=2956 for PLACES, n=3143 for ACS)"
        ),
        "all_merged_acs_adults_ge_20k_n1589": eval_uninsurance_subset(
            df[df["adults"] >= 20000],
            "All merged counties with ACS adults >= 20,000 (n=1485 for PLACES, n=1589 for ACS)",
        ),
    }

    summary = {
        "acs_verification": acs_verification,
        "task_2a_40_adjprev_measures": {
            "median_cv5_r2": float(adj_df["cv5_r2"].median()),
            "mean_cv5_r2": float(adj_df["cv5_r2"].mean()),
            "min_cv5_r2": float(adj_df["cv5_r2"].min()),
            "max_cv5_r2": float(adj_df["cv5_r2"].max()),
            "median_cv10_r2": float(adj_df["cv10_r2"].median()),
            "median_cv5_r2_drop1": float(adj_df["cv5_r2_drop1"].median()),
            "median_insample_r2": float(adj_df["r2_insample"].median()),
            "mean_insample_r2": float(adj_df["r2_insample"].mean()),
            "median_adj_r2": float(adj_df["adj_r2_insample"].median()),
            "median_cov_only_r2": float(adj_df["r2_cov_only"].median()),
            "mean_cov_only_r2": float(adj_df["r2_cov_only"].mean()),
            "median_cv5_cov_only_r2": float(adj_df["cv5_r2_cov_only"].median()),
            "median_state_only_r2": float(adj_df["r2_state_only"].median()),
            "median_cv5_no_age_r2": float(adj_df["cv5_r2_no_age"].median()),
            "median_cv5_logit_link_r2": float(adj_df["cv5_r2_logit_link"].median()),
        },
        "task_2a_40_crudeprev_measures": {
            "median_cv5_r2": float(crude_df["cv5_r2"].median()),
            "mean_cv5_r2": float(crude_df["cv5_r2"].mean()),
            "median_insample_r2": float(crude_df["r2_insample"].median()),
            "median_cov_only_r2": float(crude_df["r2_cov_only"].median()),
        },
        "task_2b_diabetes_foodinsecu": {
            "adjprev": diab_food_adj,
            "crudeprev": diab_food_crude,
        },
        "task_2b_all_780_adjprev_pairs_summary": {
            "n_pairs_total": int(len(pairs_df)),
            "median_abs_raw_r": float(pairs_df["raw_r"].abs().median()),
            "median_abs_partial_r_sep": float(
                pairs_df["partial_r_separate_fit"].abs().median()
            ),
            "median_abs_partial_r_pair": float(
                pairs_df["partial_r_pairwise_fit"].abs().median()
            ),
            "n_pairs_abs_raw_r_ge_070": int(len(strong_pairs_70)),
            "strong_ge_070_median_abs_raw_r": float(
                strong_pairs_70["raw_r"].abs().median()
            ),
            "strong_ge_070_median_abs_partial_r_sep": float(
                strong_pairs_70["partial_r_separate_fit"].abs().median()
            ),
            "strong_ge_070_median_cov_share_remaining": float(
                strong_pairs_70["cov_share_remaining"].median()
            ),
            "n_pairs_abs_raw_r_ge_050": int(len(strong_pairs_50)),
            "strong_ge_050_median_abs_raw_r": float(
                strong_pairs_50["raw_r"].abs().median()
            ),
            "strong_ge_050_median_abs_partial_r_sep": float(
                strong_pairs_50["partial_r_separate_fit"].abs().median()
            ),
            "strong_ge_050_median_cov_share_remaining": float(
                strong_pairs_50["cov_share_remaining"].median()
            ),
            "n_pairs_negative_cov_share_remaining": int(
                (pairs_df["cov_share_remaining"] < 0).sum()
            ),
            "n_pairs_cov_share_remaining_gt_1": int(
                (pairs_df["cov_share_remaining"] > 1).sum()
            ),
        },
        "task_2c_uninsurance_benchmark": benchmark_results,
    }

    with open(OUT_DIR / "recomputed_numbers.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Saved recomputed numbers to", OUT_DIR / "recomputed_numbers.json")


if __name__ == "__main__":
    main()
