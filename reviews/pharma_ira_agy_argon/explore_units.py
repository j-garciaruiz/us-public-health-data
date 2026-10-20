import pandas as pd
import numpy as np

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv")
mfp["ndc11_clean"] = mfp["NDC-11"].str.replace("-", "", regex=False)
mfp["implied_units_per_30d"] = mfp["Single MFP per 30 DES"] / mfp["NDC-9 MFP per Unit Price"]

n24 = pd.read_csv("data/raw/pharma/nadac/nadac_2024.csv", dtype={"NDC": str})
n25 = pd.read_csv("data/raw/pharma/nadac/nadac_2025.csv", dtype={"NDC": str})
n26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype={"NDC": str})
all_n = pd.concat([n24, n25, n26], ignore_index=True)
all_n["as_of_dt"] = pd.to_datetime(all_n["As of Date"])
latest_n = all_n.sort_values("as_of_dt").groupby("NDC", as_index=False).last()

m = mfp[mfp["IPAY"].isin([2026, 2027]) & mfp["MFP Effective Date"].isin(["01/01/2026", "06/01/2026", "01/01/2027"])].copy()
# Keep 01/01/2026 and 06/01/2026 for IPAY 2026, and 01/01/2027 for IPAY 2027
m = m[((m["IPAY"] == 2026) & m["MFP Effective Date"].isin(["01/01/2026", "06/01/2026"])) | ((m["IPAY"] == 2027) & (m["MFP Effective Date"] == "01/01/2027"))]
m = m.merge(latest_n[["NDC", "NDC Description", "NADAC Per Unit", "Pricing Unit", "Classification for Rate Setting"]], left_on="ndc11_clean", right_on="NDC", how="left")
m["ratio"] = m["NADAC Per Unit"] / m["NDC-9 MFP per Unit Price"]

print("=== All unique NDC-9s in IPAY 2026 and 2027 with implied units per 30-day supply and NADAC match ===")
ndc9_summary = m.groupby(["IPAY", "Selected Drug Name", "NDC-9", "MFP Effective Date", "MFP End Date", "Type of Update"], dropna=False, as_index=False).agg(
    n_ndc11=("NDC-11", "nunique"),
    sample_ndc11=("NDC-11", "first"),
    ndc_desc=("NDC Description", "first"),
    pricing_unit=("Pricing Unit", "first"),
    mfp_30d=("Single MFP per 30 DES", "first"),
    mfp_unit=("NDC-9 MFP per Unit Price", "first"),
    implied_30d_units=("implied_units_per_30d", "first"),
    nadac_unit=("NADAC Per Unit", "median"),
    ratio=("ratio", "median")
)
print(ndc9_summary.to_string())
