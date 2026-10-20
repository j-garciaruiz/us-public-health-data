#!/usr/bin/env python3
"""Explore raw data files for Task 1 and Task 2 (without touching outputs/ or scripts/)."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

# 1. Inspect MMD prevalence
mmd = pd.read_csv(RAW / "mmd_prevalence_2023.csv", dtype={"fips": str})
print("=== MMD PREVALENCE 2023 ===")
print("Columns:", mmd.columns.tolist())
print("fltr values:", mmd["fltr"].value_counts(dropna=False).to_dict())
print("Conditions & PLACES mapping:")
print(mmd[["condition_code", "condition", "places_measure", "fltr"]].drop_duplicates().to_string(index=False))
mmd_f2 = mmd[mmd["fltr"] == 2]
print("\nfltr=2 rate summary by condition (including 0s and NAs):")
for cond, grp in mmd_f2.groupby("condition"):
    n_tot = len(grp)
    n_na = grp["rate"].isna().sum()
    n_zero = (grp["rate"] == 0).sum()
    n_pos = (grp["rate"] > 0).sum()
    print(f"  {cond:25s}: total={n_tot}, na={n_na}, zero={n_zero}, >0={n_pos}, min_pos={grp.loc[grp['rate']>0, 'rate'].min()}, max={grp['rate'].max()}")
    # Also check rate_raw when rate==0 or rate is NA
    z_raw = grp.loc[grp["rate"] == 0, "rate_raw"].value_counts(dropna=False).to_dict()
    na_raw = grp.loc[grp["rate"].isna(), "rate_raw"].value_counts(dropna=False).to_dict()
    if z_raw or na_raw:
        print(f"     when rate==0, rate_raw={z_raw}; when rate is NA, rate_raw={na_raw}")

# 2. Inspect Medicare GV county 2023
gv = pd.read_csv(RAW / "medicare_gv_county_2023.csv", dtype={"fips": str})
print("\n=== MEDICARE GV 2023 ===")
print("Rows:", len(gv), "Unique fips:", gv["fips"].nunique())
for col in ["BENES_TOTAL_CNT", "BENES_OM_CNT", "BENES_MA_CNT"]:
    n_star = (gv[col] == "*").sum()
    n_na = gv[col].isna().sum()
    print(f"  {col}: '*'={n_star}, NA={n_na}")

# Check relationship between BENES_TOTAL_CNT, BENES_OM_CNT, BENES_MA_CNT
gv_num = gv.copy()
for col in ["BENES_TOTAL_CNT", "BENES_OM_CNT", "BENES_MA_CNT"]:
    gv_num[col] = pd.to_numeric(gv_num[col], errors="coerce")
gv_valid = gv_num.dropna(subset=["BENES_TOTAL_CNT", "BENES_OM_CNT", "BENES_MA_CNT"])
diff_tot = (gv_valid["BENES_OM_CNT"] + gv_valid["BENES_MA_CNT"]) - gv_valid["BENES_TOTAL_CNT"]
print("  (OM + MA) - TOTAL summary on non-suppressed:", diff_tot.describe().to_dict())
ratio_ma_tot = (gv_valid["BENES_MA_CNT"] / gv_valid["BENES_TOTAL_CNT"]).describe().to_dict()
ratio_ma_om_ma = (gv_valid["BENES_MA_CNT"] / (gv_valid["BENES_OM_CNT"] + gv_valid["BENES_MA_CNT"])).describe().to_dict()
print("  MA / TOTAL:", ratio_ma_tot)
print("  MA / (OM + MA):", ratio_ma_om_ma)

# 3. Inspect ACS disability 2023
dis = pd.read_csv(RAW / "acs_disability_2023.csv", dtype={"fips": str})
print("\n=== ACS DISABILITY 2023 ===")
print("Rows:", len(dis), "Columns:", dis.columns.tolist())
print(dis.describe().to_string())

# 4. Inspect WONDER files
print("\n=== WONDER NATIONAL AGE 2018-2024 ===")
with open(RAW / "wonder" / "national_age_2018_2024.txt", "r", encoding="utf-8") as f:
    lines = []
    for line in f:
        if line.startswith('"---"'):
            break
        lines.append(line)
from io import StringIO
nat_df = pd.read_csv(StringIO("".join(lines)), sep="\t", dtype=str)
print(nat_df.to_string(index=False))

print("\n=== WONDER COUNTY CAUSE 2018-2024 ===")
with open(RAW / "wonder" / "county_cause_2018_2024.txt", "r", encoding="utf-8") as f:
    c_lines = []
    for line in f:
        if line.startswith('"---"'):
            break
        c_lines.append(line)
cty_df = pd.read_csv(StringIO("".join(c_lines)), sep="\t", dtype=str)
print("Rows:", len(cty_df), "Unique County Codes:", cty_df["County Code"].nunique())
for cause, grp in cty_df.groupby("UCD - ICD-10 113 Cause List Code"):
    n_supp = (grp["Deaths"] == "Suppressed").sum()
    n_miss_pop = (grp["Population"].isin(["Suppressed", "Missing", "Not Applicable"])).sum()
    d_num = pd.to_numeric(grp["Deaths"], errors="coerce")
    p_num = pd.to_numeric(grp["Population"], errors="coerce")
    print(f"  {cause}: rows={len(grp)}, suppressed_deaths={n_supp}, non_numeric_pop={n_miss_pop}, sum_unsuppressed_deaths={d_num.sum():.0f}, sum_pop={p_num.sum():.0f}")

# Check unusual FIPS codes in WONDER vs ACS B01001 vs PLACES
b01_fips = set()
with open(RAW / "acs_sf" / "acsdt5y2023-b01001.dat", "r", encoding="utf-8") as f:
    hdr = f.readline()
    for line in f:
        if line.startswith("0500000US"):
            b01_fips.add(line.split("|")[0][-5:])
wonder_fips = set(cty_df["County Code"].dropna().unique())
places = pd.read_csv(RAW / "places_county_2025.csv", dtype={"countyfips": str})
places_fips = set(places["countyfips"].str.zfill(5).unique())
acs_cov = pd.read_csv(RAW / "acs_county_2023.csv", dtype={"fips": str})
acs_fips = set(acs_cov["fips"].str.zfill(5).unique())

print("\n=== FIPS CODE DIFFERENCES ===")
print("In WONDER but not ACS B01001:", sorted(wonder_fips - b01_fips))
print("In ACS B01001 (50 states+DC) but not WONDER:", sorted([x for x in (b01_fips - wonder_fips) if not x.startswith("72")]))
print("In WONDER but not PLACES:", sorted(wonder_fips - places_fips))
print("In PLACES but not WONDER:", sorted(places_fips - wonder_fips))
for fips_code in sorted((wonder_fips - b01_fips) | (places_fips - wonder_fips)):
    w_rows = cty_df[cty_df["County Code"] == fips_code][["County", "County Code", "Population"]].drop_duplicates()
    if len(w_rows) > 0:
        print("  WONDER row:", w_rows.to_dict(orient="records"))
    else:
        print("  Not in WONDER:", fips_code)

