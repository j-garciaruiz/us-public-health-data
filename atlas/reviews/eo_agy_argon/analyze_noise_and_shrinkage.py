#!/usr/bin/env python3
"""Quantify Poisson sampling noise in county SMRs and binomial/claims noise in MMD prevalence."""

import json
from pathlib import Path
import numpy as np
import pandas as pd

SCRATCH = Path("/Users/hari/.gemini/antigravity-cli/brain/5c0d75a6-5a8a-411d-9863-4546aaa291ce/scratch")


def main() -> None:
    smr = pd.read_csv(SCRATCH / "recomputed_smr.csv", dtype={"fips_mapped": str, "County Code": str})
    out = {}
    for cause, grp in smr.groupby("cause"):
        valid = grp.dropna(subset=["Deaths_num", "exp_acs7_mapped", "smr_acs7_mapped"]).copy()
        for label, sub in [("all", valid), ("exp_ge_100", valid[valid["exp_acs7_mapped"] >= 100.0])]:
            O = sub["Deaths_num"].to_numpy(float)
            E = sub["exp_acs7_mapped"].to_numpy(float)
            Y = sub["smr_acs7_mapped"].to_numpy(float)
            var_y = float(np.var(Y, ddof=1))
            # Exact unbiased estimator of Poisson variance of O/E is O / E^2 (and null approx is 1/E)
            mean_noise_var_obs = float(np.mean(O / (E**2)))
            mean_noise_var_null = float(np.mean(1.0 / E))
            noise_share_obs = mean_noise_var_obs / var_y
            noise_share_null = mean_noise_var_null / var_y
            ceiling_obs = max(0.0, 1.0 - noise_share_obs)
            # Moment estimator of true between-county SMR variance tau^2:
            tau2 = max(0.0, var_y - mean_noise_var_obs)
            # Empirical Bayes shrinkage factor B_i = E_i / (E_i + 1/tau^2)
            eb_weights = E / (E + (1.0 / tau2)) if tau2 > 0 else np.zeros_like(E)
            out[f"{cause}_{label}"] = {
                "n": int(len(sub)),
                "median_expected_deaths": float(np.median(E)),
                "min_expected_deaths": float(np.min(E)),
                "var_smr": var_y,
                "mean_poisson_noise_var_O_E2": mean_noise_var_obs,
                "mean_poisson_noise_var_1_E": mean_noise_var_null,
                "poisson_noise_share_of_var": noise_share_obs,
                "reliability_ceiling_r2": ceiling_obs,
                "estimated_tau2": tau2,
                "median_eb_weight": float(np.median(eb_weights)),
                "p10_eb_weight": float(np.percentile(eb_weights, 10)),
            }
    with open(SCRATCH / "smr_noise_diagnostics.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
