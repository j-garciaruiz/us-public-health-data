import zipfile
import pandas as pd
import numpy as np

# 1. Inspect selected_drugs_mfp.csv in detail
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["ndc11_clean"] = mfp["NDC-11"].str.replace("-", "", regex=False)
mfp["ndc9_clean"] = mfp["NDC-9"].str.replace("-", "", regex=False)
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp["unit_mfp"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
mfp["mfp_30des"] = pd.to_numeric(mfp["Single MFP per 30 DES"])

print("=== Superseded rows (end_dt < eff_dt) ===")
superseded = mfp[mfp["end_dt"] < mfp["eff_dt"]]
print(superseded[["IPAY", "Selected Drug Name", "NDC-11", "MFP Effective Date", "MFP End Date", "Type of Update", "Remarks"]].drop_duplicates())

print("\n=== Non-superseded IPAY 2026 rows by Selected Drug Name, eff_dt, end_dt, Type of Update ===")
valid_mfp = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()
print(valid_mfp[valid_mfp["IPAY"] == "2026"].groupby(
    ["Selected Drug Name", "MFP Effective Date", "MFP End Date", "Type of Update", "Single MFP per 30 DES"], dropna=False
).size())

print("\n=== Non-superseded IPAY 2027 rows by Selected Drug Name, eff_dt, end_dt, Type of Update ===")
print(valid_mfp[valid_mfp["IPAY"] == "2027"].groupby(
    ["Selected Drug Name", "MFP Effective Date", "MFP End Date", "Type of Update", "Single MFP per 30 DES"], dropna=False
).size())

# Check Entresto Sprinkle specifically
print("\n=== Entresto rows in selected_drugs_mfp.csv ===")
print(mfp[mfp["Selected Drug Name"].str.contains("ENTRESTO")][
    ["NDC-9", "NDC-11", "MFP Effective Date", "MFP End Date", "Single MFP per 30 DES", "NDC-9 MFP per Unit Price", "As of Date", "Type of Update", "Remarks"]
].to_string())

# 2. Check Part D brand rows for IPAY 2026 and IPAY 2027 drugs
partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
partd_ov = partd[partd["Mftr_Name"] == "Overall"].copy()

print("\n=== Part D Overall rows matching any selected drug name or active ingredient ===")
all_selected_26_27 = valid_mfp[valid_mfp["IPAY"].isin(["2026", "2027"])][["IPAY", "Selected Drug Name", "Active Ingredient Name or Active Moiety Name"]].drop_duplicates()
for _, row in all_selected_26_27.iterrows():
    ipay = row["IPAY"]
    sname = row["Selected Drug Name"]
    ingr = row["Active Ingredient Name or Active Moiety Name"]
    brands = [b.strip() for b in sname.split(";")]
    # Find exact or prefix matches in Brnd_Name
    pattern = "|".join([b.split()[0] for b in brands])
    sub = partd_ov[partd_ov["Brnd_Name"].str.upper().str.contains(pattern, na=False)]
    print(f"\n[{ipay}] {sname} ({ingr}):")
    for bname, grp in sub.groupby("Brnd_Name"):
        y25 = grp[grp["Year"] == "2025 (Q1-Q4)"]
        y26 = grp[grp["Year"] == "2026 (Q1)"]
        c25 = y25["Tot_Clms"].values[0] if len(y25) else 0
        s25 = y25["Tot_Spndng"].values[0] if len(y25) else 0
        a25 = y25["Avg_Spnd_Per_Clm"].values[0] if len(y25) else 0
        c26 = y26["Tot_Clms"].values[0] if len(y26) else 0
        s26 = y26["Tot_Spndng"].values[0] if len(y26) else 0
        a26 = y26["Avg_Spnd_Per_Clm"].values[0] if len(y26) else 0
        print(f"  Brnd_Name='{bname}' | Gnrc='{grp['Gnrc_Name'].iloc[0]}' | 2025: clms={c25}, spnd={s25:,.2f}, avg={a25} (calc={s25/c25 if c25 else 0:.2f}) | 2026Q1: clms={c26}, spnd={s26:,.2f}, avg={a26} (calc={s26/c26 if c26 else 0:.2f})")
