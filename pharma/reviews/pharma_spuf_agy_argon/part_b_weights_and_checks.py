import pandas as pd
import numpy as np
import zipfile

df30 = pd.read_pickle("/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch/spuf_matched_30d.pkl")
mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
mfp_df["MFP_UNIT"] = pd.to_numeric(mfp_df["NDC-9 MFP per Unit Price"], errors="coerce")
mfp_df["EFF"] = pd.to_datetime(mfp_df["MFP Effective Date"])
mfp_df["END"] = pd.to_datetime(mfp_df["MFP End Date"])
valid_mfp = mfp_df[mfp_df["END"].isna() | (mfp_df["END"] >= mfp_df["EFF"])].copy()

ipay26 = valid_mfp[valid_mfp["IPAY"] == "2026"]
early26 = ipay26[(ipay26["EFF"] <= "2026-01-15") & (ipay26["END"].isna() | (ipay26["END"] >= "2026-01-15"))].copy()
late26 = ipay26[(ipay26["EFF"] <= "2026-10-01") & (ipay26["END"].isna() | (ipay26["END"] >= "2026-10-01"))].copy()
ipay27 = valid_mfp[(valid_mfp["IPAY"] == "2027") & (valid_mfp["EFF"] == "2027-01-01")].copy()

lookup_rows = []
for rel, src in [("2025Q3", late26), ("2025Q4", early26), ("2026Q3", late26)]:
    tmp = src[["IPAY", "Selected Drug Name", "NDC-11", "NDC11", "MFP_UNIT"]].copy()
    tmp["RELEASE"] = rel
    lookup_rows.append(tmp)
for rel in ["2025Q3", "2025Q4", "2026Q3"]:
    tmp = ipay27[["IPAY", "Selected Drug Name", "NDC-11", "NDC11", "MFP_UNIT"]].copy()
    tmp["RELEASE"] = rel
    lookup_rows.append(tmp)
lookup = pd.concat(lookup_rows, ignore_index=True)

m = df30.merge(lookup, left_on=["NDC", "RELEASE"], right_on=["NDC11", "RELEASE"], how="inner")
m["RATIO"] = m["UNIT_COST"] / m["MFP_UNIT"]
m["DRUG_SHORT"] = m["Selected Drug Name"].str.split(";").str[0].str.strip()
m["PLAN_SEG"] = m["CONTRACT_ID"] + "|" + m["PLAN_ID"] + "|" + m["SEGMENT_ID"]
m["PLAN_NOSEG"] = m["CONTRACT_ID"] + "|" + m["PLAN_ID"]
m["AT_MFP"] = ((m["RATIO"] - 1.0).abs() <= 0.005).astype(float)
m["BELOW_MFP"] = (m["RATIO"] < 0.995).astype(float)
m["ABOVE_MFP"] = (m["RATIO"] > 1.005).astype(float)

# 1. Check if UNIT_COST ever varies across SEGMENT_ID within (CONTRACT_ID, PLAN_ID, NDC, RELEASE)
seg_var = m.groupby(["RELEASE", "CONTRACT_ID", "PLAN_ID", "NDC"])["UNIT_COST"].nunique()
print("Max distinct UNIT_COST across segments within (CONTRACT_ID, PLAN_ID, NDC):", seg_var.max())
print("Count of (RELEASE, CONTRACT_ID, PLAN_ID, NDC) with >1 UNIT_COST across segments:", (seg_var > 1).sum())

# Compare unweighted plan-segment rows vs deduplicated (CONTRACT_ID, PLAN_ID, NDC) rows
m_noseg = m.drop_duplicates(subset=["RELEASE", "CONTRACT_ID", "PLAN_ID", "NDC"])
print("\n=== DEDUPLICATED (CONTRACT_ID, PLAN_ID, NDC) SUMMARY ===")
for (ipay, rel), grp in m_noseg.groupby(["IPAY", "RELEASE"]):
    print(f"IPAY {ipay} {rel}: rows={len(grp):,}, plans={grp['PLAN_NOSEG'].nunique():,}, med={grp['RATIO'].median():.4f}, at={grp['AT_MFP'].mean()*100:.2f}%, below={grp['BELOW_MFP'].mean()*100:.2f}%, above={grp['ABOVE_MFP'].mean()*100:.2f}%")

# 2. Check county counts per plan-segment in plan information
county_counts = {}
for rel in ["2025Q3", "2025Q4", "2026Q3"]:
    with zipfile.ZipFile(f"data/raw/pharma/spuf/{rel}/plan information  PPUF_{rel}.zip") as z:
        with z.open(z.namelist()[0]) as f:
            pi = pd.read_csv(f, sep="|", dtype=str, encoding="latin1")
    pi["PLAN_SEG"] = pi["CONTRACT_ID"] + "|" + pi["PLAN_ID"] + "|" + pi["SEGMENT_ID"]
    pi["IS_PDP"] = pi["CONTRACT_ID"].str.startswith("S")
    cc = pi.groupby(["PLAN_SEG", "IS_PDP"])["COUNTY_CODE"].nunique().reset_index(name="N_COUNTIES")
    print(f"\n{rel} mean counties per plan-segment by IS_PDP:")
    print(cc.groupby("IS_PDP")["N_COUNTIES"].describe())
    county_counts[rel] = cc.set_index("PLAN_SEG")["N_COUNTIES"].to_dict()

# 3. Get Part D claims, beneficiaries, and spending by drug for IPAY 2026 from partd_spending_quarterly.csv
pq = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv", dtype=str)
pq = pq[pq["Mftr_Name"] == "Overall"].copy()
for col in ["Tot_Benes", "Tot_Clms", "Tot_Spndng"]:
    pq[col] = pd.to_numeric(pq[col], errors="coerce").fillna(0.0)

# Map Brand Names to IPAY 2026 drugs
brand_map = {
    "Eliquis": "ELIQUIS",
    "Enbrel": "ENBREL",
    "Entresto": "ENTRESTO",
    "Entresto Sprinkle": "ENTRESTO",
    "Farxiga": "FARXIGA",
    "Imbruvica": "IMBRUVICA",
    "Januvia": "JANUVIA",
    "Jardiance": "JARDIANCE",
    "Novolog": "NOVOLOG",
    "Novolog Flexpen": "NOVOLOG",
    "Novolog Penfill": "NOVOLOG",
    "Fiasp": "NOVOLOG",
    "Fiasp Flextouch": "NOVOLOG",
    "Fiasp Penfill": "NOVOLOG",
    "Fiasp Pumpcart": "NOVOLOG",
    "Stelara": "STELARA",
    "Ustekinumab": "STELARA",
    "Xarelto": "XARELTO",
}
pq["DRUG_SHORT"] = pq["Brnd_Name"].str.strip().map(brand_map)
pq26 = pq.dropna(subset=["DRUG_SHORT"]).groupby(["Year", "DRUG_SHORT"])[["Tot_Benes", "Tot_Clms", "Tot_Spndng"]].sum().reset_index()
print("\n=== PART D UTILIZATION AND SPENDING BY IPAY 2026 DRUG ===")
for yr in ["2025 (Q1-Q4)", "2026 (Q1)"]:
    sub = pq26[pq26["Year"] == yr].copy()
    sub["clm_share"] = sub["Tot_Clms"] / sub["Tot_Clms"].sum() * 100
    sub["spnd_share"] = sub["Tot_Spndng"] / sub["Tot_Spndng"].sum() * 100
    print(f"\nYear {yr}:")
    print(sub.to_string(index=False))

# Compare unweighted vs equal-drug-weighted vs 2025-claim-weighted vs 2026Q1-claim-weighted vs 2025-spending-weighted for IPAY 2026
drug_stats = m[m["IPAY"] == "2026"].groupby(["RELEASE", "DRUG_SHORT"]).agg(
    rows=("RATIO", "count"),
    med_ratio=("RATIO", "median"),
    at_mfp=("AT_MFP", "mean"),
    below_mfp=("BELOW_MFP", "mean"),
    above_mfp=("ABOVE_MFP", "mean"),
).reset_index()

w25 = pq26[pq26["Year"] == "2025 (Q1-Q4)"].set_index("DRUG_SHORT")
w26 = pq26[pq26["Year"] == "2026 (Q1)"].set_index("DRUG_SHORT")

print("\n=== IPAY 2026 WEIGHTING COMPARISON (AT / BELOW / ABOVE MFP %) ===")
for rel in ["2025Q3", "2025Q4", "2026Q3"]:
    ds = drug_stats[drug_stats["RELEASE"] == rel].set_index("DRUG_SHORT")
    ds["row_share"] = ds["rows"] / ds["rows"].sum()
    ds["clm25_w"] = w25["Tot_Clms"] / w25["Tot_Clms"].sum()
    ds["clm26_w"] = w26["Tot_Clms"] / w26["Tot_Clms"].sum()
    ds["spnd25_w"] = w25["Tot_Spndng"] / w25["Tot_Spndng"].sum()
    ds["spnd26_w"] = w26["Tot_Spndng"] / w26["Tot_Spndng"].sum()
    ds["eq_w"] = 0.1
    print(f"\nRelease {rel}:")
    for wname, wcol in [
        ("Unweighted plan-NDC rows", "row_share"),
        ("Equal weight across 10 drugs", "eq_w"),
        ("2025 Part D claim-weighted", "clm25_w"),
        ("2026 Q1 Part D claim-weighted", "clm26_w"),
        ("2025 Part D spending-weighted", "spnd25_w"),
        ("2026 Q1 Part D spending-weighted", "spnd26_w"),
    ]:
        at_v = (ds["at_mfp"] * ds[wcol]).sum() * 100
        bel_v = (ds["below_mfp"] * ds[wcol]).sum() * 100
        abv_v = (ds["above_mfp"] * ds[wcol]).sum() * 100
        print(f"  {wname:34s}: At MFP={at_v:6.2f}% | Below={bel_v:6.2f}% | Above={abv_v:6.2f}%")

# Also check if we exclude unbranded Ustekinumab (57894044001, 57894044003, 57894044101) in 2025Q4 and 2026Q3
m26_brand_st = m[(m["IPAY"] == "2026") & (~m["NDC"].isin(["57894044001", "57894044003", "57894044101"]))]
print("\n=== IPAY 2026 EXCLUDING UNBRANDED USTEKINUMAB (57894-0440-*, 57894-0441-*) ===")
for rel, grp in m26_brand_st.groupby("RELEASE"):
    print(f"  {rel}: rows={len(grp):,}, at={grp['AT_MFP'].mean()*100:.2f}%, below={grp['BELOW_MFP'].mean()*100:.2f}%, above={grp['ABOVE_MFP'].mean()*100:.2f}% (n_above={int(grp['ABOVE_MFP'].sum())})")
