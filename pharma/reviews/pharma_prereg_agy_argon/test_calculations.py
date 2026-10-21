import zipfile
import pandas as pd
import numpy as np

# Load MFP table
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["ndc11"] = mfp["NDC-11"].str.replace("-", "", regex=False).str.strip()
mfp["ndc9"] = mfp["NDC-9"].str.replace("-", "", regex=False).str.strip()
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp["unit_mfp"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
mfp["mfp_30des"] = pd.to_numeric(mfp["Single MFP per 30 DES"])

# Filter out superseded rows (end_dt < eff_dt)
mfp_valid = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()

# IPAY 2026 active in 2026 (using 2026-06-01 corrected value for Entresto Sprinkle -> end_dt == 2026-12-31)
mfp_2026 = mfp_valid[(mfp_valid["IPAY"] == "2026") & (mfp_valid["MFP End Date"] == "12/31/2026")].copy()
print("mfp_2026 count:", len(mfp_2026), "unique ndc11:", mfp_2026["ndc11"].nunique(), "unique ndc9:", mfp_2026["ndc9"].nunique())

# IPAY 2027 active in 2027 (IPAY == 2027)
mfp_2027 = mfp_valid[mfp_valid["IPAY"] == "2027"].copy()
print("mfp_2027 count:", len(mfp_2027), "unique ndc11:", mfp_2027["ndc11"].nunique(), "unique ndc9:", mfp_2027["ndc9"].nunique())

# Load SPUF 2025Q3 and 2026Q3
def load_spuf(label):
    zpath = f"data/raw/pharma/spuf/{label}/pricing file PPUF_{label}.zip"
    with zipfile.ZipFile(zpath) as zf:
        fname = [n for n in zf.namelist() if n.endswith(".txt")][0]
        with zf.open(fname) as f:
            df = pd.read_csv(f, sep="|", dtype={"CONTRACT_ID": str, "PLAN_ID": str, "SEGMENT_ID": str, "NDC": str, "DAYS_SUPPLY": int, "UNIT_COST": float})
    df["ndc9"] = df["NDC"].str[:9]
    return df

spuf_25q3 = load_spuf("2025Q3")
spuf_26q3 = load_spuf("2026Q3")
print("spuf_25q3 rows:", len(spuf_25q3), "spuf_26q3 rows:", len(spuf_26q3))

# Check DAYS_SUPPLY == 30 matching on NDC-11 vs NDC-9
for label, spuf_df, mfp_df in [("2026 cohort (2025Q3)", spuf_25q3, mfp_2026), ("2027 cohort (2026Q3)", spuf_26q3, mfp_2027)]:
    print(f"\n=== {label} ===")
    s30 = spuf_df[spuf_df["DAYS_SUPPLY"] == 30].copy()
    m11 = s30.merge(mfp_df[["Selected Drug Name", "ndc11", "unit_mfp"]], left_on="NDC", right_on="ndc11", how="inner")
    m11["ratio"] = m11["UNIT_COST"] / m11["unit_mfp"]
    
    ndc9_map = mfp_df[["Selected Drug Name", "ndc9", "unit_mfp"]].drop_duplicates()
    m9 = s30.merge(ndc9_map, on="ndc9", how="inner")
    m9["ratio"] = m9["UNIT_COST"] / m9["unit_mfp"]
    
    for drug in mfp_df["Selected Drug Name"].unique():
        d11 = m11[m11["Selected Drug Name"] == drug]
        d9 = m9[m9["Selected Drug Name"] == drug]
        r11 = d11["ratio"].median()
        r9 = d9["ratio"].median()
        p11 = (1.0 / r11 - 1.0) * 100
        p9 = (1.0 / r9 - 1.0) * 100
        print(f"  {drug[:35]:35s} | NDC11: n={len(d11):5d}, r={r11:.4f}, pred={p11:+.2f}% | NDC9: n={len(d9):5d}, r={r9:.4f}, pred={p9:+.2f}%")
