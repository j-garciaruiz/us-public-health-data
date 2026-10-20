import pandas as pd
import numpy as np

partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv")

ov = partd[partd["Mftr_Name"] == "Overall"].copy()
p25 = ov[ov["Year"] == "2025 (Q1-Q4)"].copy()
p26 = ov[ov["Year"] == "2026 (Q1)"].copy()

merged = p25.merge(p26, on=["Brnd_Name", "Gnrc_Name"], suffixes=("_2025", "_2026"), how="inner")
merged["spc_2025_calc"] = merged["Tot_Spndng_2025"] / merged["Tot_Clms_2025"]
merged["spc_2026_calc"] = merged["Tot_Spndng_2026"] / merged["Tot_Clms_2026"]
merged["pct_chg_calc"] = (merged["spc_2026_calc"] / merged["spc_2025_calc"] - 1) * 100
merged["pct_chg_col"] = (merged["Avg_Spnd_Per_Clm_2026"] / merged["Avg_Spnd_Per_Clm_2025"] - 1) * 100

# Identify brand vs generic in Part D
merged["is_brand_neq"] = merged["Brnd_Name"].str.strip().str.upper() != merged["Gnrc_Name"].str.strip().str.upper()

# Collect all Brnd_Name rows that match IPAY 2026, 2027, 2028
def get_ipay_brnds(ipay, mode="prefix"):
    sub = mfp[mfp["IPAY"] == ipay]
    parts = []
    for s in sub["Selected Drug Name"].unique():
        parts.extend([p.strip() for p in s.split(";")])
    if mode == "exact":
        return set(ov[ov["Brnd_Name"].str.upper().isin([p.upper() for p in parts])]["Brnd_Name"].unique())
    else:
        return set(ov[ov["Brnd_Name"].str.upper().str.startswith(tuple(p.upper() for p in parts))]["Brnd_Name"].unique())

b26_pref = get_ipay_brnds(2026, "prefix")
b26_exact = get_ipay_brnds(2026, "exact")
b27_pref = get_ipay_brnds(2027, "prefix")
b28_pref = get_ipay_brnds(2028, "prefix")
b_all_ira = b26_pref | b27_pref | b28_pref

vol = merged[(merged["Tot_Clms_2025"] >= 4000) & (merged["Tot_Clms_2026"] >= 1000)].copy()

print("=== Median % change across other brand-name drugs (Tot_Clms_2025 >= 4000 & Tot_Clms_2026 >= 1000) ===")
configs = [
    ("is_brand (Brnd!=Gnrc), excl IPAY 2026 (prefix)", vol[vol["is_brand_neq"] & (~vol["Brnd_Name"].isin(b26_pref))]),
    ("is_brand (Brnd!=Gnrc), excl IPAY 2026 (exact)", vol[vol["is_brand_neq"] & (~vol["Brnd_Name"].isin(b26_exact))]),
    ("is_brand (Brnd!=Gnrc), excl IPAY 2026/2027/2028 (prefix)", vol[vol["is_brand_neq"] & (~vol["Brnd_Name"].isin(b_all_ira))]),
    ("All Overall rows (incl generics), excl IPAY 2026 (prefix)", vol[~vol["Brnd_Name"].isin(b26_pref)]),
    ("All Overall rows (incl generics), excl IPAY 2026/2027/2028", vol[~vol["Brnd_Name"].isin(b_all_ira)]),
    ("is_brand & Tot_Mftr_2025==1, excl IPAY 2026 (prefix)", vol[vol["is_brand_neq"] & (vol["Tot_Mftr_2025"] == 1) & (~vol["Brnd_Name"].isin(b26_pref))]),
    ("is_brand & Tot_Mftr_2025==1, excl IPAY 2026/2027/2028", vol[vol["is_brand_neq"] & (vol["Tot_Mftr_2025"] == 1) & (~vol["Brnd_Name"].isin(b_all_ira))]),
]
for label, df_sub in configs:
    print(f"{label:62s} | N={len(df_sub):4d} | Median(calc): {df_sub['pct_chg_calc'].median():+6.2f}% | Median(col): {df_sub['pct_chg_col'].median():+6.2f}% | Mean(calc): {df_sub['pct_chg_calc'].mean():+6.2f}% | IQR: [{df_sub['pct_chg_calc'].quantile(0.25):+6.2f}%, {df_sub['pct_chg_calc'].quantile(0.75):+6.2f}%]")
