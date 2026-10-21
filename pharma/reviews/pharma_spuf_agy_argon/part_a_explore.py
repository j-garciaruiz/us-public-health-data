import pandas as pd
import numpy as np

mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
mfp_df["MFP_UNIT"] = pd.to_numeric(mfp_df["NDC-9 MFP per Unit Price"], errors="coerce")
mfp_df["EFF"] = pd.to_datetime(mfp_df["MFP Effective Date"])
mfp_df["END"] = pd.to_datetime(mfp_df["MFP End Date"])

# Filter out invalid rows where END < EFF
valid_mfp = mfp_df[mfp_df["END"].isna() | (mfp_df["END"] >= mfp_df["EFF"])].copy()

print("Valid rows count by IPAY and EFF:")
print(valid_mfp.groupby(["IPAY", "MFP Effective Date", "MFP End Date"], dropna=False).size())

# Check for each release what MFP applies to IPAY 2026 and IPAY 2027:
# For IPAY 2026:
# - 2025Q3 (2025 baseline): 2026 MFP, using corrected 2026-06-01 value for Entresto Sprinkle (i.e. price in effect on 2026-06-01..2026-12-31)
# - 2025Q4 (Jan 2026 release, applies in Q1 2026, e.g. 2026-01-01..2026-05-31): MFP in effect on 2026-01-15
# - 2026Q3 (Oct 2026 release, applies in Q4 2026, e.g. 2026-06-01..2026-12-31): MFP in effect on 2026-10-01
# For IPAY 2027:
# - Use the 2027 MFP (MFP Effective Date == 01/01/2027)

for ipay in ["2026", "2027"]:
    sub = valid_mfp[valid_mfp["IPAY"] == ipay]
    print(f"\nIPAY {ipay}: unique valid NDC11 = {sub['NDC11'].nunique()}")
    if ipay == "2026":
        # Check date ranges in 2026
        early26 = sub[(sub["EFF"] <= "2026-01-15") & (sub["END"].isna() | (sub["END"] >= "2026-01-15"))]
        late26 = sub[(sub["EFF"] <= "2026-10-01") & (sub["END"].isna() | (sub["END"] >= "2026-10-01"))]
        print(f"  Early 2026 rows: {len(early26)}, unique NDC11: {early26['NDC11'].nunique()}")
        print(f"  Late 2026 rows: {len(late26)}, unique NDC11: {late26['NDC11'].nunique()}")
        diff = early26.merge(late26, on="NDC11", suffixes=("_early", "_late"))
        diff_prices = diff[diff["MFP_UNIT_early"] != diff["MFP_UNIT_late"]]
        print("  NDCs with different early vs late 2026 MFP:")
        print(diff_prices[["NDC-11_early", "Selected Drug Name_early", "MFP_UNIT_early", "MFP_UNIT_late"]])
    else:
        y27 = sub[sub["EFF"] == "2027-01-01"]
        print(f"  2027 rows: {len(y27)}, unique NDC11: {y27['NDC11'].nunique()}")
