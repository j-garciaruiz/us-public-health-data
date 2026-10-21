import pandas as pd

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv")
mfp["ndc11_clean"] = mfp["NDC-11"].str.replace("-", "", regex=False)

comp = pd.read_csv("data/raw/pharma/nadac/nadac_comparison.csv", dtype={"NDC": str}, low_memory=False)
comp["eff_dt"] = pd.to_datetime(comp["Effective Date"])
comp["end_dt"] = pd.to_datetime(comp["End Date"])
comp24 = comp[(comp["eff_dt"] >= "2024-01-01") | (comp["end_dt"] >= "2024-01-01")].copy()

for ipay in [2027, 2028]:
    print(f"\n=== IPAY {ipay} WAC Adjustments since 2024 ===")
    sub_mfp = mfp[mfp["IPAY"] == ipay]
    ndcs = set(sub_mfp["ndc11_clean"])
    # Also match by drug name keywords
    names = []
    for s in sub_mfp["Selected Drug Name"].unique():
        names.extend([p.strip() for p in s.split(";")])
    mask = comp24["NDC"].isin(ndcs) | comp24["NDC Description"].str.upper().str.startswith(tuple(n.upper() for n in names), na=False)
    wac = comp24[mask & (comp24["Primary Reason"] == "WAC Adjustment")].sort_values(["NDC Description", "eff_dt", "NDC"])
    # Summarize by NDC Description, Effective Date, Start Date, End Date, Percent Change
    summary = wac.groupby(["NDC Description", "Start Date", "End Date", "Effective Date", "Percent Change"], as_index=False).agg(
        n_ndc=("NDC", "nunique"),
        old_med=("Old NADAC Per Unit", "median"),
        new_med=("New NADAC Per Unit", "median")
    )
    print(summary.to_string())

print("\n=== All Brand (Classification == 'B') WAC Adjustments <= -20% in 2026 across ENTIRE NADAC Comparison ===")
b_cuts_26 = comp24[(comp24["Classification for Rate Setting"] == "B") & (comp24["Primary Reason"] == "WAC Adjustment") & (comp24["eff_dt"] >= "2025-12-01") & (comp24["Percent Change"] <= -20)]
print(b_cuts_26.groupby(["NDC Description", "Start Date", "End Date", "Effective Date", "Percent Change"], as_index=False).agg(n_ndc=("NDC", "nunique"), old_med=("Old NADAC Per Unit", "median"), new_med=("New NADAC Per Unit", "median")).to_string())
