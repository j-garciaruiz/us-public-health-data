import pandas as pd

df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
sub26 = df[df["IPAY"] == "2026"].copy()

print("=== Rows where End Date < Effective Date ===")
for idx, r in sub26.iterrows():
    eff = pd.to_datetime(r["MFP Effective Date"])
    end = pd.to_datetime(r["MFP End Date"]) if pd.notna(r["MFP End Date"]) else pd.Timestamp.max
    if end < eff:
        print(f"Row {idx}: NDC={r['NDC-11']} | Drug={r['Selected Drug Name']} | Eff={r['MFP Effective Date']} | End={r['MFP End Date']} | Price={r['NDC-9 MFP per Unit Price']} | Type={r['Type of Update']} | Remarks={r['Remarks']}")

print("\n=== Check per NDC-11 in IPAY 2026: what rows exist? ===")
for ndc, grp in sub26.groupby("NDC-11"):
    if len(grp) != 2 or not set(grp["MFP Effective Date"]) == {"01/01/2026", "01/01/2027"}:
        print(f"\nNDC {ndc} ({grp['Selected Drug Name'].iloc[0]}):")
        for _, r in grp.iterrows():
            print(f"  Eff={r['MFP Effective Date']} | End={r['MFP End Date']} | Price={r['NDC-9 MFP per Unit Price']} | Type={r['Type of Update']} | Remarks={r['Remarks']}")
