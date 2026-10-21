import pandas as pd
import zipfile

df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
print("Columns in selected_drugs_mfp.csv:", list(df.columns))
print("Non-null XREF NDC-11:", df["XREF NDC-11"].dropna().tolist())
print("Non-null HCPCS Code:", df["HCPCS Code"].dropna().unique().tolist())

# Check all IPAY 2026 and 2027 drugs and NDC counts
for ipay in ["2026", "2027"]:
    sub = df[df["IPAY"] == ipay]
    print(f"\nIPAY {ipay} drugs ({sub['Selected Drug Name'].nunique()}):")
    for drug, grp in sub.groupby("Selected Drug Name"):
        ndcs_all = grp["NDC-11"].nunique()
        # Exclude rows where End Date < Effective Date
        valid_rows = []
        for _, r in grp.iterrows():
            eff = pd.to_datetime(r["MFP Effective Date"])
            end = pd.to_datetime(r["MFP End Date"]) if pd.notna(r["MFP End Date"]) else pd.Timestamp.max
            if end >= eff:
                valid_rows.append(r)
        vdf = pd.DataFrame(valid_rows)
        ndcs_valid = vdf["NDC-11"].nunique() if len(vdf) else 0
        print(f"  {drug}: total NDC-11={ndcs_all}, valid (End>=Eff) NDC-11={ndcs_valid}")
