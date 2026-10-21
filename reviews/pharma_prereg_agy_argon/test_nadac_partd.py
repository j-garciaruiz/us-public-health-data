import pandas as pd
import numpy as np

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["ndc11"] = mfp["NDC-11"].str.replace("-", "", regex=False).str.strip()
mfp["ndc9"] = mfp["NDC-9"].str.replace("-", "", regex=False).str.strip()
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp["unit_mfp"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
mfp["mfp_30des"] = pd.to_numeric(mfp["Single MFP per 30 DES"])

mfp_valid = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()
mfp_2026 = mfp_valid[(mfp_valid["IPAY"] == "2026") & (mfp_valid["MFP End Date"] == "12/31/2026")].copy()
mfp_2027 = mfp_valid[mfp_valid["IPAY"] == "2027"].copy()
mfp_2026_cont = mfp_valid[(mfp_valid["IPAY"] == "2026") & (mfp_valid["MFP Effective Date"] == "01/01/2027")].copy()

print("=== ITEM 4: Six continuing 2026 drugs (2027 MFP per 30 days vs 2026) ===")
cont_26 = mfp_2026[["Selected Drug Name", "mfp_30des"]].drop_duplicates().rename(columns={"mfp_30des": "mfp_2026"})
cont_27 = mfp_2026_cont[["Selected Drug Name", "mfp_30des"]].drop_duplicates().rename(columns={"mfp_30des": "mfp_2027"})
cont = cont_26.merge(cont_27, on="Selected Drug Name")
cont["diff"] = cont["mfp_2027"] - cont["mfp_2026"]
cont["pct_chg"] = (cont["mfp_2027"] / cont["mfp_2026"] - 1.0) * 100
print(cont.to_string(index=False))

u26 = mfp_2026[["Selected Drug Name", "ndc11", "unit_mfp"]].rename(columns={"unit_mfp": "u26"})
u27 = mfp_2026_cont[["Selected Drug Name", "ndc11", "unit_mfp"]].rename(columns={"unit_mfp": "u27"})
um = u26.merge(u27, on=["Selected Drug Name", "ndc11"])
um["u_pct"] = (um["u27"] / um["u26"] - 1.0) * 100
print("\nUnit MFP pct change summary for continuing 2026 drugs:")
print(um.groupby("Selected Drug Name")["u_pct"].agg(["min", "median", "max"]))

print("\n=== ITEM 3: NADAC analysis ===")
all_ndc11 = set(mfp_valid["ndc11"].unique())
all_ndc9 = set(mfp_valid["ndc9"].unique())

nadac_chunks = []
for chunk in pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype=str, chunksize=200000):
    chunk["NDC_clean"] = chunk["NDC"].str.strip().str.zfill(11)
    chunk["ndc9"] = chunk["NDC_clean"].str[:9]
    sub = chunk[chunk["NDC_clean"].isin(all_ndc11) | chunk["ndc9"].isin(all_ndc9)].copy()
    if len(sub):
        nadac_chunks.append(sub)
nadac = pd.concat(nadac_chunks, ignore_index=True)
nadac["as_of_dt"] = pd.to_datetime(nadac["As of Date"])
nadac["eff_dt"] = pd.to_datetime(nadac["Effective Date"])
nadac["nadac_unit"] = pd.to_numeric(nadac["NADAC Per Unit"])

print("NADAC As of Dates:", sorted(nadac["As of Date"].unique(), key=lambda x: pd.to_datetime(x)))
max_as_of = nadac["as_of_dt"].max()
print("Latest As of Date in nadac_2026.csv:", max_as_of)

nadac_latest = nadac[nadac["as_of_dt"] == max_as_of].copy()
print("Classifications in nadac_latest:", nadac_latest["Classification for Rate Setting"].value_counts(dropna=False))

print("\n--- IPAY 2027 drugs in latest NADAC snapshot ---")
m27_11 = mfp_2027.merge(nadac_latest, left_on="ndc11", right_on="NDC_clean", how="inner")
m27_11["ratio"] = m27_11["nadac_unit"] / m27_11["unit_mfp"]

ndc9_27 = mfp_2027[["Selected Drug Name", "ndc9", "unit_mfp"]].drop_duplicates()
m27_9 = ndc9_27.merge(nadac_latest, on="ndc9", how="inner")
m27_9["ratio"] = m27_9["nadac_unit"] / m27_9["unit_mfp"]

for drug in mfp_2027["Selected Drug Name"].unique():
    d11_all = m27_11[m27_11["Selected Drug Name"] == drug]
    d11_b = d11_all[d11_all["Classification for Rate Setting"] == "B"]
    d9_b = m27_9[(m27_9["Selected Drug Name"] == drug) & (m27_9["Classification for Rate Setting"] == "B")]
    print(f"  {drug[:30]:30s} | NDC11(B): n={len(d11_b):2d}, med={d11_b['ratio'].median() if len(d11_b) else np.nan:.4f} | NDC11(all): n={len(d11_all):2d}, classes={d11_all['Classification for Rate Setting'].unique().tolist()} | NDC9(B): n={len(d9_b):2d}, med={d9_b['ratio'].median() if len(d9_b) else np.nan:.4f}")
    for _, r in d11_all.iterrows():
        print(f"      NDC={r['NDC_clean']} ({r['NDC Description']}) class={r['Classification for Rate Setting']} nadac={r['nadac_unit']} mfp={r['unit_mfp']} ratio={r['ratio']:.4f}")

print("\n--- Four deselected IPAY 2026 drugs in latest NADAC snapshot ---")
m26_11 = mfp_2026.merge(nadac_latest, left_on="ndc11", right_on="NDC_clean", how="inner")
m26_11["ratio"] = m26_11["nadac_unit"] / m26_11["unit_mfp"]
for drug in ["ENTRESTO; ENTRESTO SPRINKLE", "STELARA", "XARELTO", "NOVOLOG; NOVOLOG FLEXPEN; NOVOLOG PENFILL; FIASP; FIASP FLEXTOUCH; FIASP PENFILL"]:
    d11_all = m26_11[m26_11["Selected Drug Name"] == drug]
    d11_b = d11_all[d11_all["Classification for Rate Setting"] == "B"]
    print(f"  {drug[:45]:45s} | NDC11(B): n={len(d11_b):2d}, med={d11_b['ratio'].median() if len(d11_b) else np.nan:.4f} | NDC11(all): n={len(d11_all):2d}, med={d11_all['ratio'].median() if len(d11_all) else np.nan:.4f}")
    for _, r in d11_all.iterrows():
        print(f"      NDC={r['NDC_clean']} ({r['NDC Description']}) class={r['Classification for Rate Setting']} nadac={r['nadac_unit']} mfp={r['unit_mfp']} ratio={r['ratio']:.4f}")

print("\n--- All IPAY 2026 drugs in latest NADAC snapshot ---")
for drug in mfp_2026["Selected Drug Name"].unique():
    d11_all = m26_11[m26_11["Selected Drug Name"] == drug]
    d11_b = d11_all[d11_all["Classification for Rate Setting"] == "B"]
    print(f"  {drug[:45]:45s} | NDC11(B): n={len(d11_b):2d}, med={d11_b['ratio'].median() if len(d11_b) else np.nan:.4f} | NDC11(all): n={len(d11_all):2d}, med={d11_all['ratio'].median() if len(d11_all) else np.nan:.4f}")

print("\n--- nadac_comparison.csv since 2024 for IPAY 2026 and IPAY 2027 NDCs ---")
comp_chunks = []
for chunk in pd.read_csv("data/raw/pharma/nadac/nadac_comparison.csv", dtype=str, chunksize=200000):
    chunk["NDC_clean"] = chunk["NDC"].str.strip().str.zfill(11)
    chunk["ndc9"] = chunk["NDC_clean"].str[:9]
    sub = chunk[chunk["NDC_clean"].isin(all_ndc11) | chunk["ndc9"].isin(all_ndc9)].copy()
    if len(sub):
        comp_chunks.append(sub)
comp = pd.concat(comp_chunks, ignore_index=True)
comp["eff_dt"] = pd.to_datetime(comp["Effective Date"])
comp["pct_chg"] = pd.to_numeric(comp["Percent Change"])
comp_2024 = comp[comp["eff_dt"] >= "2024-01-01"].copy()

ndc_to_drug = mfp_valid[["IPAY", "Selected Drug Name", "ndc11", "ndc9"]].drop_duplicates()
comp_m11 = comp_2024.merge(ndc_to_drug[["IPAY", "Selected Drug Name", "ndc11"]].drop_duplicates(), left_on="NDC_clean", right_on="ndc11", how="inner")
print("Primary reasons in comp_m11:", comp_m11["Primary Reason"].value_counts(dropna=False))
print("\nAll cuts <= -15% in comp_m11 since 2024:")
cuts = comp_m11[comp_m11["pct_chg"] <= -15.0].sort_values(["IPAY", "Selected Drug Name", "eff_dt", "NDC_clean"])
for _, r in cuts.iterrows():
    print(f"  [{r['IPAY']}] {r['Selected Drug Name'][:25]:25s} | {r['Effective Date']} | NDC={r['NDC_clean']} ({r['NDC Description']}) | class={r['Classification for Rate Setting']} | old={r['Old NADAC Per Unit']} -> new={r['New NADAC Per Unit']} ({r['pct_chg']:.2f}%) | reason={r['Primary Reason']}")
