import pandas as pd
import zipfile

df30 = pd.read_pickle("/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch/spuf_matched_30d.pkl")
mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
mfp_df["MFP_UNIT"] = pd.to_numeric(mfp_df["NDC-9 MFP per Unit Price"], errors="coerce")
mfp_df["MFP_30DES"] = pd.to_numeric(mfp_df["Single MFP per 30 DES"], errors="coerce")
mfp_df["EFF"] = pd.to_datetime(mfp_df["MFP Effective Date"])
mfp_df["END"] = pd.to_datetime(mfp_df["MFP End Date"])
valid_mfp = mfp_df[mfp_df["END"].isna() | (mfp_df["END"] >= mfp_df["EFF"])].copy()

# Get NADAC descriptions and Pricing Unit across 2024, 2025, 2026
nadac_frames = []
for fn in ["nadac_2024.csv", "nadac_2025.csv", "nadac_2026.csv"]:
    dn = pd.read_csv(f"data/raw/pharma/nadac/{fn}", dtype=str, usecols=["NDC", "NDC Description", "Pricing Unit"]).drop_duplicates("NDC")
    nadac_frames.append(dn)
nadac_info = pd.concat(nadac_frames, ignore_index=True).drop_duplicates("NDC")

# Get formulary quantity limits
with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/basic drugs formulary file  PPUF_2026Q3.zip") as z:
    with z.open(z.namelist()[0]) as f:
        df_form = pd.read_csv(f, sep="|", dtype=str, encoding="latin1")
        df_form["NDC11"] = df_form["NDC"].str.zfill(11)
        form_info = df_form[df_form["QUANTITY_LIMIT_YN"] == "Y"].groupby("NDC11").agg(
            ql_amt=("QUANTITY_LIMIT_AMOUNT", lambda s: s.mode().iloc[0] if len(s.mode()) else ""),
            ql_days=("QUANTITY_LIMIT_DAYS", lambda s: s.mode().iloc[0] if len(s.mode()) else "")
        ).reset_index()

# Summarize each NDC present in SPUF for IPAY 2026 and 2027
late26 = valid_mfp[(valid_mfp["IPAY"] == "2026") & (valid_mfp["EFF"] <= "2026-10-01") & (valid_mfp["END"].isna() | (valid_mfp["END"] >= "2026-10-01"))]
y27 = valid_mfp[(valid_mfp["IPAY"] == "2027") & (valid_mfp["EFF"] == "2027-01-01")]
ref_mfp = pd.concat([late26, y27], ignore_index=True)
ref_mfp["IMPLIED_UNITS_PER_30DES"] = ref_mfp["MFP_30DES"] / ref_mfp["MFP_UNIT"]

spuf_ndc = df30.groupby(["NDC", "RELEASE"]).agg(
    n=("UNIT_COST", "count"),
    med_cost=("UNIT_COST", "median"),
    min_cost=("UNIT_COST", "min"),
    max_cost=("UNIT_COST", "max")
).unstack("RELEASE")
spuf_ndc.columns = [f"{a}_{b}" for a, b in spuf_ndc.columns]
spuf_ndc = spuf_ndc.reset_index()

merged = ref_mfp.merge(spuf_ndc, left_on="NDC11", right_on="NDC", how="inner")
merged = merged.merge(nadac_info, left_on="NDC11", right_on="NDC", how="left")
merged = merged.merge(form_info, on="NDC11", how="left")

for ipay in ["2026", "2027"]:
    print(f"\n==================== IPAY {ipay} NDC UNIT BASIS CHECK ====================")
    sub = merged[merged["IPAY"] == ipay].sort_values(["Selected Drug Name", "NDC-11"])
    cols = ["Selected Drug Name", "NDC-11", "NDC Description", "Pricing Unit", "MFP_30DES", "MFP_UNIT", "IMPLIED_UNITS_PER_30DES", "ql_amt", "ql_days", "med_cost_2025Q3", "med_cost_2025Q4", "med_cost_2026Q3"]
    print(sub[cols].to_string(index=False))
