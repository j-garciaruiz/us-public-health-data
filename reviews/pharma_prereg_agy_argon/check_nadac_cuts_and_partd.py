import pandas as pd
import numpy as np

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["ndc11"] = mfp["NDC-11"].str.replace("-", "", regex=False).str.strip()
mfp["ndc9"] = mfp["NDC-9"].str.replace("-", "", regex=False).str.strip()
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp["unit_mfp"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
mfp["mfp_30des"] = pd.to_numeric(mfp["Single MFP per 30 DES"])

mfp_valid = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()
mfp_2026 = mfp_valid[(mfp_valid["IPAY"] == "2026") & (mfp_valid["MFP End Date"] == "12/31/2026")].copy()
mfp_2027 = mfp_valid[mfp_valid["IPAY"] == "2027"].copy()

all_ndc11 = set(mfp_valid["ndc11"].unique())
all_ndc9 = set(mfp_valid["ndc9"].unique())

# Check all nadac_comparison.csv rows for any selected drug NDCs (any percent change)
comp_chunks = []
for chunk in pd.read_csv("data/raw/pharma/nadac/nadac_comparison.csv", dtype=str, chunksize=200000):
    chunk["NDC_clean"] = chunk["NDC"].str.strip().str.zfill(11)
    chunk["ndc9"] = chunk["NDC_clean"].str[:9]
    sub = chunk[chunk["NDC_clean"].isin(all_ndc11) | chunk["ndc9"].isin(all_ndc9)].copy()
    if len(sub):
        comp_chunks.append(sub)
comp = pd.concat(comp_chunks, ignore_index=True)
comp["eff_dt"] = pd.to_datetime(comp["Effective Date"])
comp["pct_chg"] = pd.to_numeric(comp["Percent Change"])

ndc_to_drug = mfp_valid[["IPAY", "Selected Drug Name", "ndc11"]].drop_duplicates()
comp_m = comp.merge(ndc_to_drug, left_on="NDC_clean", right_on="ndc11", how="inner")

print("=== WAC Adjustments in nadac_comparison.csv since 2024 (all % changes) ===")
wac_24 = comp_m[(comp_m["eff_dt"] >= "2024-01-01") & (comp_m["Primary Reason"] == "WAC Adjustment")].copy()
print(wac_24.groupby(["IPAY", "Selected Drug Name", "Effective Date"])["pct_chg"].agg(["count", "min", "median", "max"]))

print("\n=== Any negative changes <= -5% in nadac_comparison.csv since 2024 (any reason) ===")
neg_24 = comp_m[(comp_m["eff_dt"] >= "2024-01-01") & (comp_m["pct_chg"] <= -5.0)].copy()
print(neg_24.groupby(["IPAY", "Selected Drug Name", "Effective Date", "Primary Reason", "Classification for Rate Setting"])["pct_chg"].agg(["count", "min", "median", "max"]))

# Now let's check Part D matching for IPAY 2026 and IPAY 2027
partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
partd_ov = partd[partd["Mftr_Name"] == "Overall"].copy()
partd_ov["Brnd_upper"] = partd_ov["Brnd_Name"].str.upper().str.strip()

print("\n=== Check Part D exact brand name matching vs broader brand matching ===")
for ipay, mdf in [("2026", mfp_2026), ("2027", mfp_2027)]:
    print(f"\n--- IPAY {ipay} ---")
    for sname in mdf["Selected Drug Name"].unique():
        exact_brands = [b.strip().upper() for b in sname.split(";")]
        # Prefix matches (excluding NovoLog Mix)
        prefixes = [b.split()[0] for b in exact_brands]
        pattern = "|".join([f"^{p}\\b" for p in set(prefixes)])
        sub_broad = partd_ov[partd_ov["Brnd_upper"].str.contains(pattern, regex=True, na=False)]
        sub_broad = sub_broad[~sub_broad["Brnd_upper"].str.contains("NOVOLOG MIX", na=False)]
        sub_exact = partd_ov[partd_ov["Brnd_upper"].isin(exact_brands)]
        
        b_exact = sorted(sub_exact["Brnd_Name"].unique().tolist())
        b_broad = sorted(sub_broad["Brnd_Name"].unique().tolist())
        if b_exact != b_broad:
            print(f"  DIFF for {sname}:")
            print(f"    Exact: {b_exact}")
            print(f"    Broad: {b_broad}")
            for label, sub in [("Exact", sub_exact), ("Broad", sub_broad)]:
                s25 = sub[sub["Year"] == "2025 (Q1-Q4)"]["Tot_Spndng"].sum()
                c25 = sub[sub["Year"] == "2025 (Q1-Q4)"]["Tot_Clms"].sum()
                s26 = sub[sub["Year"] == "2026 (Q1)"]["Tot_Spndng"].sum()
                c26 = sub[sub["Year"] == "2026 (Q1)"]["Tot_Clms"].sum()
                p25 = s25 / c25
                p26 = s26 / c26
                chg = (p26 / p25 - 1.0) * 100
                print(f"      {label}: 2025={p25:,.2f} (clms={c25:,}), 2026Q1={p26:,.2f} (clms={c26:,}), chg={chg:+.2f}%")
        else:
            s25 = sub_exact[sub_exact["Year"] == "2025 (Q1-Q4)"]["Tot_Spndng"].sum()
            c25 = sub_exact[sub_exact["Year"] == "2025 (Q1-Q4)"]["Tot_Clms"].sum()
            s26 = sub_exact[sub_exact["Year"] == "2026 (Q1)"]["Tot_Spndng"].sum()
            c26 = sub_exact[sub_exact["Year"] == "2026 (Q1)"]["Tot_Clms"].sum()
            p25 = s25 / c25
            p26 = s26 / c26
            chg = (p26 / p25 - 1.0) * 100
            print(f"  SAME for {sname}: {b_exact} | 2025={p25:,.2f}, 2026Q1={p26:,.2f}, chg={chg:+.2f}%")
