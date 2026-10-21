import pandas as pd

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv")
mfp["ndc11_clean"] = mfp["NDC-11"].str.replace("-", "", regex=False)

nadac25 = pd.read_csv("data/raw/pharma/nadac/nadac_2025.csv", dtype={"NDC": str})
nadac26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype={"NDC": str})

# Convert As of Date to datetime to find last snapshots
nadac25["as_of_dt"] = pd.to_datetime(nadac25["As of Date"])
nadac26["as_of_dt"] = pd.to_datetime(nadac26["As of Date"])

last_25_dt = nadac25["as_of_dt"].max()
last_26_dt = nadac26["as_of_dt"].max()
print("Last 2025 As of Date:", last_25_dt, "Last 2026 As of Date:", last_26_dt)

n25_last = nadac25[nadac25["as_of_dt"] == last_25_dt].copy()
n26_last = nadac26[nadac26["as_of_dt"] == last_26_dt].copy()

mfp_2026 = mfp[(mfp["IPAY"] == 2026) & (mfp["MFP Effective Date"] == "01/01/2026")].copy()
print("Total rows in mfp_2026 (IPAY==2026 & Eff==01/01/2026):", len(mfp_2026))
print("Unique NDC-11 in mfp_2026:", mfp_2026["NDC-11"].nunique())

# Check duplicate NDC-11 in mfp_2026
dups = mfp_2026[mfp_2026.duplicated(subset=["NDC-11"], keep=False)]
print("\nDuplicate NDC-11 rows in mfp_2026:")
print(dups[["Selected Drug Name", "NDC-11", "MFP Effective Date", "MFP End Date", "NDC-9 MFP per Unit Price", "Type of Update", "Remarks"]].to_string())

# Merge with n25_last and n26_last
m = mfp_2026.drop_duplicates(subset=["NDC-11"]).merge(
    n25_last[["NDC", "NDC Description", "NADAC Per Unit", "Pricing Unit", "Effective Date", "Classification for Rate Setting"]],
    left_on="ndc11_clean", right_on="NDC", how="left"
).merge(
    n26_last[["NDC", "NADAC Per Unit", "Pricing Unit", "Effective Date"]],
    left_on="ndc11_clean", right_on="NDC", how="left", suffixes=("_2025", "_2026")
)
m["ratio_2025"] = m["NADAC Per Unit_2025"] / m["NDC-9 MFP per Unit Price"]
m["ratio_2026"] = m["NADAC Per Unit_2026"] / m["NDC-9 MFP per Unit Price"]

matched = m[m["NADAC Per Unit_2025"].notna() | m["NADAC Per Unit_2026"].notna()]
print("\n=== Matched IPAY 2026 NDCs in last 2025 / last 2026 NADAC snapshots ===")
print(matched[["Selected Drug Name", "NDC-11", "NDC Description", "Pricing Unit_2025", "Classification for Rate Setting", "NDC-9 MFP per Unit Price", "NADAC Per Unit_2025", "NADAC Per Unit_2026", "ratio_2025", "ratio_2026"]].to_string())
