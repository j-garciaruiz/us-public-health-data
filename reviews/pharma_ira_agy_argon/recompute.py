"""Independent blind recompute and sensitivity verification for the IRA January 2026 study.

Computes:
  - Part (a) & Fixed Quantity 1: Medicare Part D gross spending per claim (2024 annual, 2025 Q1-Q4,
    and 2026 Q1) across IPAY 2026, IPAY 2027, IPAY 2028, and Other brand-name comparators.
  - Part (b) & Fixed Quantity 2: WAC-based NADAC changes (Primary Reason == "WAC Adjustment")
    of 20% or more since 2024 for Eliquis, Jardiance, Farxiga, NovoLog/Fiasp, Januvia, and comparators.
  - Part (c) & Fixed Quantity 3: Median NADAC per unit divided by 2026 MFP per unit (MFP Effective Date
    01/01/2026 and 06/01/2026 sensitivity) at the last 2025 (12/31/2025) and last 2026 (10/21/2026)
    NADAC snapshots.
"""
import numpy as np
import pandas as pd

# Load datasets
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv")
partd_q = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
partd_a = pd.read_csv("data/raw/pharma/partd/partd_spending_annual.csv")
n24 = pd.read_csv("data/raw/pharma/nadac/nadac_2024.csv", dtype={"NDC": str})
n25 = pd.read_csv("data/raw/pharma/nadac/nadac_2025.csv", dtype={"NDC": str})
n26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype={"NDC": str})
comp = pd.read_csv("data/raw/pharma/nadac/nadac_comparison.csv", dtype={"NDC": str}, low_memory=False)

mfp["ndc11_clean"] = mfp["NDC-11"].str.replace("-", "", regex=False)
ov_q = partd_q[partd_q["Mftr_Name"] == "Overall"].copy()
ov_a = partd_a[partd_a["Mftr_Name"] == "Overall"].copy()

# ==============================================================================
# PART 1A & FIXED QUANTITY 1: PART D SPENDING PER CLAIM (2025 vs 2026 Q1)
# ==============================================================================

ipay2026_families = {
    "Eliquis": ["Eliquis"],
    "Enbrel": ["Enbrel", "Enbrel Mini", "Enbrel Sureclick"],
    "Entresto": ["Entresto", "Entresto Sprinkle"],
    "Farxiga": ["Farxiga"],
    "Imbruvica": ["Imbruvica"],
    "Januvia": ["Januvia"],
    "Jardiance": ["Jardiance"],
    "NovoLog / Fiasp (all 7)": [
        "Novolog", "Novolog Flexpen", "Novolog Penfill",
        "Fiasp", "Fiasp Flextouch", "Fiasp Penfill", "Fiasp Pumpcart",
    ],
    "Stelara": ["Stelara"],
    "Xarelto": ["Xarelto"],
}

ipay2027_families = {
    "Austedo": ["Austedo", "Austedo XR", "Austedo XR Titration Kt(Wk1-4)"],
    "Breo Ellipta": ["Breo Ellipta"],
    "Calquence": ["Calquence"],
    "Ibrance": ["Ibrance"],
    "Janumet": ["Janumet", "Janumet XR"],
    "Linzess": ["Linzess"],
    "Ofev": ["Ofev"],
    "Otezla": ["Otezla", "Otezla XR"],
    "Ozempic / Rybelsus / Wegovy": ["Ozempic", "Rybelsus", "Wegovy"],
    "Pomalyst": ["Pomalyst"],
    "Tradjenta": ["Tradjenta"],
    "Trelegy Ellipta": ["Trelegy Ellipta"],
    "Vraylar": ["Vraylar"],
    "Xifaxan": ["Xifaxan"],
    "Xtandi": ["Xtandi"],
}

ipay2028_families = {
    "Anoro Ellipta": ["Anoro Ellipta"],
    "Biktarvy": ["Biktarvy"],
    "Botox": ["Botox"],
    "Cimzia": ["Cimzia", "Cimzia (2 Pack)"],
    "Cosentyx": [
        "Cosentyx", "Cosentyx (2 Syringes)", "Cosentyx Sensoready (2 Pens)",
        "Cosentyx Sensoready Pen", "Cosentyx Syringe", "Cosentyx Unoready Pen",
    ],
    "Entyvio": ["Entyvio", "Entyvio Pen"],
    "Erleada": ["Erleada"],
    "Kisqali": ["Kisqali"],
    "Lenvima": ["Lenvima"],
    "Orencia": ["Orencia", "Orencia Clickject"],
    "Rexulti": ["Rexulti"],
    "Trulicity": ["Trulicity"],
    "Verzenio": ["Verzenio"],
    "Xeljanz": ["Xeljanz", "Xeljanz XR"],
    "Xolair": ["Xolair"],
}


def summarize_families(fdict, label):
    rows = []
    for dname, brnds in fdict.items():
        brnds_a = brnds + [b + "*" for b in brnds]
        a24 = ov_a[ov_a["Brnd_Name"].isin(brnds_a)]
        q25 = ov_q[(ov_q["Brnd_Name"].isin(brnds)) & (ov_q["Year"] == "2025 (Q1-Q4)")]
        q26 = ov_q[(ov_q["Brnd_Name"].isin(brnds)) & (ov_q["Year"] == "2026 (Q1)")]

        c24, s24, u24 = a24["Tot_Clms_2024"].sum(), a24["Tot_Spndng_2024"].sum(), a24["Tot_Dsg_Unts_2024"].sum()
        c25, s25 = q25["Tot_Clms"].sum(), q25["Tot_Spndng"].sum()
        c26, s26 = q26["Tot_Clms"].sum(), q26["Tot_Spndng"].sum()

        spc24 = s24 / c24 if c24 else np.nan
        upc24 = u24 / c24 if c24 else np.nan
        spc25 = s25 / c25 if c25 else np.nan
        spc26 = s26 / c26 if c26 else np.nan
        chg_24_25 = (spc25 / spc24 - 1) * 100 if (c24 and c25) else np.nan
        chg_25_26 = (spc26 / spc25 - 1) * 100 if (c25 and c26) else np.nan
        vol_ann_chg = (4 * c26 / c25 - 1) * 100 if c25 else np.nan
        rows.append({
            "Group": label,
            "Drug": dname,
            "Clms_2025": c25,
            "Clms_2026Q1": c26,
            "SPC_2024": spc24,
            "SPC_2025": spc25,
            "SPC_2026Q1": spc26,
            "Chg_24_25_%": chg_24_25,
            "Chg_25_26Q1_%": chg_25_26,
            "Ann_Clm_Chg_%": vol_ann_chg,
            "UPC_2024": upc24,
        })
    return pd.DataFrame(rows)


df_26 = summarize_families(ipay2026_families, "IPAY 2026")
df_27 = summarize_families(ipay2027_families, "IPAY 2027")
df_28 = summarize_families(ipay2028_families, "IPAY 2028")

print("=== FIXED QUANTITY 1: IPAY 2026 Family Summary ===")
print(df_26.to_string(index=False))
print(f"IPAY 2026 Median Chg_25_26Q1_%: {df_26['Chg_25_26Q1_%'].median():+.2f}%, Mean: {df_26['Chg_25_26Q1_%'].mean():+.2f}%")
print(f"IPAY 2027 Median Chg_25_26Q1_%: {df_27['Chg_25_26Q1_%'].median():+.2f}%, Mean: {df_27['Chg_25_26Q1_%'].mean():+.2f}%")
print(f"IPAY 2028 Median Chg_25_26Q1_%: {df_28['Chg_25_26Q1_%'].median():+.2f}%, Mean: {df_28['Chg_25_26Q1_%'].mean():+.2f}%")

# Other brand-name drugs comparator variants
q25_all = ov_q[ov_q["Year"] == "2025 (Q1-Q4)"].set_index(["Brnd_Name", "Gnrc_Name"])
q26_all = ov_q[ov_q["Year"] == "2026 (Q1)"].set_index(["Brnd_Name", "Gnrc_Name"])
m_partd = q25_all.join(q26_all, lsuffix="_2025", rsuffix="_2026", how="inner").reset_index()
m_partd["spc_25"] = m_partd["Tot_Spndng_2025"] / m_partd["Tot_Clms_2025"]
m_partd["spc_26"] = m_partd["Tot_Spndng_2026"] / m_partd["Tot_Clms_2026"]
m_partd["pct_chg"] = (m_partd["spc_26"] / m_partd["spc_25"] - 1) * 100
m_partd["is_brand"] = m_partd["Brnd_Name"].str.upper() != m_partd["Gnrc_Name"].str.upper()

sel26_rows = set(sum(ipay2026_families.values(), [])) | {"Novolog Mix 70-30", "Novolog Mix 70-30 Flexpen"}
sel27_rows = set(sum(ipay2027_families.values(), []))
sel28_rows = set(sum(ipay2028_families.values(), [])) | {"Kisqali Femara Co-Pack"}

vol_filter = (m_partd["Tot_Clms_2025"] >= 4000) & (m_partd["Tot_Clms_2026"] >= 1000)
b_no26 = m_partd[vol_filter & m_partd["is_brand"] & (~m_partd["Brnd_Name"].isin(sel26_rows))]
b_no_all_sel = m_partd[vol_filter & m_partd["is_brand"] & (~m_partd["Brnd_Name"].isin(sel26_rows | sel27_rows | sel28_rows))]
b_single_src = b_no26[b_no26["Tot_Mftr_2025"] == 1]

print("\n=== Other Brand-Name Drugs Variants (Clms_2025 >= 4,000 & Clms_2026Q1 >= 1,000) ===")
for name, sub in [
    ("Brnd != Gnrc, excl. IPAY 2026", b_no26),
    ("Brnd != Gnrc, excl. IPAY 2026/27/28", b_no_all_sel),
    ("Single-source Brnd != Gnrc (Tot_Mftr == 1), excl. IPAY 2026", b_single_src),
]:
    print(f"  {name}: N={len(sub)}, Median={sub['pct_chg'].median():+.2f}%, Mean={sub['pct_chg'].mean():+.2f}%")

# ==============================================================================
# PART 1B & FIXED QUANTITY 2: WAC-BASED NADAC CHANGES >= 20% SINCE 2024
# ==============================================================================

wac_comp = comp[comp["Primary Reason"] == "WAC Adjustment"].copy()
wac_comp["abs_pct"] = wac_comp["Percent Change"].abs()
wac_ge20 = wac_comp[wac_comp["abs_pct"] >= 20.0].copy()

target_patterns = ["ELIQUIS", "JARDIANCE", "FARXIGA", "NOVOLOG", "FIASP", "JANUVIA"]
pat_regex = "|".join(target_patterns)
fq2 = wac_ge20[wac_ge20["NDC Description"].str.contains(pat_regex, case=False, na=False)].copy()

print("\n=== FIXED QUANTITY 2: WAC-Based NADAC Changes >= 20% Since 2024 ===")
print(
    fq2.groupby(["Effective Date", "Start Date", "End Date", "NDC Description", "Percent Change"])
    .agg(n_ndcs=("NDC", "nunique"), old_nadac=("Old NADAC Per Unit", "first"), new_nadac=("New NADAC Per Unit", "first"))
    .reset_index()
    .to_string(index=False)
)

# ==============================================================================
# PART 1C & FIXED QUANTITY 3: MEDIAN NADAC PER UNIT / 2026 MFP PER UNIT
# ==============================================================================

mfp_2026 = mfp[(mfp["IPAY"] == 2026) & (mfp["MFP Effective Date"] == "01/01/2026")].copy()
mfp_2026["mfp_unit"] = pd.to_numeric(mfp_2026["NDC-9 MFP per Unit Price"], errors="coerce")
mfp_2026["drug_short"] = mfp_2026["Selected Drug Name"].str.split(";").str[0].str.strip()
mfp_dedup = mfp_2026.drop_duplicates(subset=["ndc11_clean"]).copy()

last25 = n25[n25["As of Date"] == "12/31/2025"].copy()
last26 = n26[n26["As of Date"] == "10/21/2026"].copy()

m25 = last25.merge(mfp_dedup, left_on="NDC", right_on="ndc11_clean", how="inner")
m25["ratio"] = m25["NADAC Per Unit"] / m25["mfp_unit"]

m26 = last26.merge(mfp_dedup, left_on="NDC", right_on="ndc11_clean", how="inner")
m26["ratio"] = m26["NADAC Per Unit"] / m26["mfp_unit"]

fq3 = (
    mfp_dedup.groupby("drug_short")
    .agg(mfp_ndcs=("ndc11_clean", "nunique"))
    .join(m25.groupby("drug_short").agg(ndcs_2025=("NDC", "nunique"), med_ratio_2025=("ratio", "median")))
    .join(m26.groupby("drug_short").agg(ndcs_2026=("NDC", "nunique"), med_ratio_2026=("ratio", "median")))
    .reset_index()
)

print("\n=== FIXED QUANTITY 3: Median NADAC Per Unit / 2026 MFP Per Unit (12/31/2025 vs 10/21/2026) ===")
print(fq3.to_string(index=False))
