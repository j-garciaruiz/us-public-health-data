#!/usr/bin/env python3
"""Explore SMR construction details and Task 2 datasets."""

from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

# Load B01001
with open(RAW / "acs_sf" / "acsdt5y2023-b01001.dat", "r", encoding="utf-8") as f:
    header = f.readline().strip().split("|")
    rows = [line.strip().split("|") for line in f if line.startswith("0500000US")]
b01 = pd.DataFrame(rows, columns=header)
b01["fips"] = b01["GEO_ID"].str[-5:]
b01 = b01.set_index("fips")
for c in b01.columns:
    if c != "GEO_ID":
        b01[c] = b01[c].astype(float)

# Map B01001 to 10 age bins matching WONDER (combining <1 and 1-4 into 0-4)
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
b01_ages["total"] = b01["B01001_E001"]
print("Max diff between sum of 10 age bins and B01001_E001:", (b01_ages.drop(columns="total").sum(axis=1) - b01_ages["total"]).abs().max())

# Load WONDER national_age_2018_2024.txt
with open(RAW / "wonder" / "national_age_2018_2024.txt", "r", encoding="utf-8") as f:
    lines = [line for line in f if not line.startswith('"---"') and "\t" in line]
nat = pd.read_csv(StringIO("".join(lines)), sep="\t", dtype=str)
nat["Deaths_num"] = pd.to_numeric(nat["Deaths"], errors="coerce").fillna(0.0)
nat["Pop_num"] = pd.to_numeric(nat["Population"], errors="coerce")
nat["Rate_given"] = pd.to_numeric(nat["Crude Rate"], errors="coerce")

# Map WONDER age groups to our 10 bins
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
nat_binned = nat_valid.groupby(["UCD - ICD-10 113 Cause List Code", "age_bin"], as_index=False)[["Deaths_num", "Pop_num"]].sum()
nat_binned["rate_exact"] = nat_binned["Deaths_num"] / nat_binned["Pop_num"]

# Compare national population by age (WONDER 2018-2024 vs 7 * ACS 2019-2023 50 states + DC)
b01_50dc = b01_ages[~b01_ages.index.str.startswith("72")].copy()
wonder_pop_by_age = nat_binned[nat_binned["UCD - ICD-10 113 Cause List Code"] == "GR113-054"].set_index("age_bin")["Pop_num"]
acs7_pop_by_age = b01_50dc.drop(columns="total").sum(axis=0) * 7.0
pop_comp = pd.DataFrame({
    "wonder_pop_2018_2024": wonder_pop_by_age,
    "acs_2019_2023_x7": acs7_pop_by_age,
    "ratio_acs7_to_wonder": acs7_pop_by_age / wonder_pop_by_age,
})
print("\n=== NATIONAL POPULATION BY AGE: WONDER (2018-2024) vs 7 * ACS (2019-2023, 50 states+DC) ===")
print(pop_comp.to_string())
print(f"Total WONDER pop: {wonder_pop_by_age.sum():,.0f} vs 7*ACS: {acs7_pop_by_age.sum():,.0f} (ratio={acs7_pop_by_age.sum()/wonder_pop_by_age.sum():.6f})")

# Load WONDER county_cause_2018_2024.txt
with open(RAW / "wonder" / "county_cause_2018_2024.txt", "r", encoding="utf-8") as f:
    c_lines = []
    for line in f:
        if line.startswith('"---"'):
            break
        c_lines.append(line)
cty = pd.read_csv(StringIO("".join(c_lines)), sep="\t", dtype=str)
cty["Deaths_num"] = pd.to_numeric(cty["Deaths"], errors="coerce")
cty["Pop_num"] = pd.to_numeric(cty["Population"], errors="coerce")

# Check national reconciliation of deaths & expected deaths across the 4 causes
print("\n=== NATIONAL OBSERVED vs EXPECTED DEATHS BY CAUSE ===")
for cause in ["GR113-046", "GR113-054", "GR113-070", "GR113-082"]:
    nat_c = nat[nat["UCD - ICD-10 113 Cause List Code"] == cause]
    nat_known_age_deaths = nat_c[nat_c["Ten-Year Age Groups Code"] != "NS"]["Deaths_num"].sum()
    nat_ns_deaths = nat_c[nat_c["Ten-Year Age Groups Code"] == "NS"]["Deaths_num"].sum()
    nat_tot_deaths = nat_known_age_deaths + nat_ns_deaths

    rates = nat_binned[nat_binned["UCD - ICD-10 113 Cause List Code"] == cause].set_index("age_bin")["rate_exact"]
    exp_county_acs7 = (b01_50dc[rates.index] * 7.0) @ rates

    cty_c = cty[cty["UCD - ICD-10 113 Cause List Code"] == cause].copy()
    obs_unsupp = cty_c["Deaths_num"].sum()
    n_supp = cty_c["Deaths"].eq("Suppressed").sum()

    # Remap 46113 -> 46102 and 02270 -> 02158 in cty_c
    cty_c["fips_mapped"] = cty_c["County Code"].replace({"46113": "46102", "02270": "02158"})
    cty_c["exp_acs7"] = cty_c["fips_mapped"].map(exp_county_acs7)

    # Also check expected deaths using WONDER county Population * ACS age shares
    b01_shares = b01_50dc[rates.index].div(b01_50dc["total"], axis=0)
    rate_per_person_county = b01_shares @ rates
    cty_c["exp_wonder_pop"] = cty_c["Pop_num"] * cty_c["fips_mapped"].map(rate_per_person_county)

    print(f"Cause {cause}:")
    print(f"  Nat deaths (known age): {nat_known_age_deaths:,.0f} | NS: {nat_ns_deaths:,.0f} | Total: {nat_tot_deaths:,.0f}")
    print(f"  Sum of expected across all 3,144 ACS counties (7*ACS): {exp_county_acs7.sum():,.1f} (ratio to nat known age = {exp_county_acs7.sum()/nat_known_age_deaths:.5f})")
    print(f"  County unsuppressed deaths sum: {obs_unsupp:,.0f} (missing from nat total = {nat_tot_deaths - obs_unsupp:,.0f} across {n_supp} suppressed counties, avg={(nat_tot_deaths - obs_unsupp)/n_supp:.2f}/county)")
    valid_both = cty_c.dropna(subset=["Deaths_num", "exp_acs7"])
    print(f"  Matched unsuppressed counties (n={len(valid_both)}): sum(obs)={valid_both['Deaths_num'].sum():,.0f}, sum(exp_acs7)={valid_both['exp_acs7'].sum():,.1f} (obs/exp={valid_both['Deaths_num'].sum()/valid_both['exp_acs7'].sum():.5f})")
    valid_wpop = cty_c.dropna(subset=["Deaths_num", "exp_wonder_pop"])
    print(f"  Matched unsuppressed w/ WONDER pop (n={len(valid_wpop)}): sum(obs)={valid_wpop['Deaths_num'].sum():,.0f}, sum(exp_wpop)={valid_wpop['exp_wonder_pop'].sum():,.1f} (obs/exp={valid_wpop['Deaths_num'].sum()/valid_wpop['exp_wonder_pop'].sum():.5f})")
