import pandas as pd
import zipfile

mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
target_ndcs = set(mfp_df["NDC11"].dropna().unique())

nadac26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype=str)
m_nadac = nadac26[nadac26["NDC"].isin(target_ndcs)].drop_duplicates(subset=["NDC", "NDC Description", "Pricing Unit"])
print(f"Matched {len(m_nadac)} unique (NDC, desc, unit) in NADAC 2026:")
for _, r in m_nadac.sort_values("NDC").iterrows():
    print(f"  {r['NDC']} | {r['NDC Description']} | Unit={r['Pricing Unit']} | NADAC={r['NADAC Per Unit']}")

print("\n=== Check basic drugs formulary file PPUF_2026Q3.zip for Stelara and other selected drugs ===")
with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/basic drugs formulary file  PPUF_2026Q3.zip") as z:
    with z.open(z.namelist()[0]) as f:
        df_form = pd.read_csv(f, sep="|", dtype=str, encoding="latin1")
        print("Formulary columns:", list(df_form.columns))
        df_form["NDC11"] = df_form["NDC"].str.zfill(11)
        m_form = df_form[df_form["NDC11"].isin(target_ndcs) | df_form["NDC"].isin(target_ndcs)]
        print("Matched formulary rows:", len(m_form))
        print(m_form.drop_duplicates("NDC")[["NDC", "TIER_LEVEL_VALUE", "QUANTITY_LIMIT_YN", "QUANTITY_LIMIT_AMOUNT", "QUANTITY_LIMIT_DAYS"]].to_string(index=False))
