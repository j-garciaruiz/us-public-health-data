import pandas as pd

for fn in ["nadac_2024.csv", "nadac_2025.csv", "nadac_2026.csv", "nadac_comparison.csv"]:
    df = pd.read_csv(f"data/raw/pharma/nadac/{fn}", dtype=str)
    st = df[df["NDC"].str.startswith("57894", na=False)]
    print(f"=== {fn} (rows={len(st)}) ===")
    if len(st):
        print(st.drop_duplicates(subset=["NDC", "NDC Description"]).to_string(index=False))

for fn in ["partd_spending_annual.csv", "partd_spending_quarterly.csv"]:
    df = pd.read_csv(f"data/raw/pharma/partd/{fn}", dtype=str)
    st = df[df["Gnrc_Name"].str.contains("USTEKINUMAB", case=False, na=False) | df["Brnd_Name"].str.contains("STELARA|USTEKINUMAB", case=False, na=False)]
    print(f"\n=== {fn} USTEKINUMAB/STELARA ===")
    print(st.to_string(index=False))
