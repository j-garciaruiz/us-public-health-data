import zipfile
import pandas as pd
import numpy as np

mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["ndc11"] = mfp["NDC-11"].str.replace("-", "", regex=False).str.strip().str.zfill(11)
mfp["ndc9"] = mfp["NDC-9"].str.replace("-", "", regex=False).str.strip().str.zfill(9)
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp["unit_mfp"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
mfp["mfp_30des"] = pd.to_numeric(mfp["Single MFP per 30 DES"])
mfp["drug_short"] = mfp["Selected Drug Name"].str.split(";").str[0].str.strip()
mfp_valid = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()
m27 = mfp_valid[mfp_valid["IPAY"] == "2027"].copy()

# Load latest NADAC to get NDC Description and B/G classification
nadac26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype=str)
nadac26["ndc11"] = nadac26["NDC"].str.strip().str.zfill(11)
nadac26["as_of_dt"] = pd.to_datetime(nadac26["As of Date"])
latest_nadac = nadac26[nadac26["as_of_dt"] == nadac26["as_of_dt"].max()][["ndc11", "NDC Description", "Classification for Rate Setting"]].drop_duplicates("ndc11")

def load_spuf_30(label, ndc_set):
    zpath = f"data/raw/pharma/spuf/{label}/pricing file PPUF_{label}.zip"
    chunks = []
    with zipfile.ZipFile(zpath) as zf:
        fname = [n for n in zf.namelist() if n.endswith(".txt")][0]
        with zf.open(fname) as f:
            for chunk in pd.read_csv(f, sep="|", dtype={"CONTRACT_ID": str, "PLAN_ID": str, "SEGMENT_ID": str, "NDC": str, "DAYS_SUPPLY": int, "UNIT_COST": float}, chunksize=1000000):
                sub = chunk[(chunk["DAYS_SUPPLY"] == 30) & (chunk["NDC"].isin(ndc_set))].copy()
                if len(sub):
                    chunks.append(sub)
    return pd.concat(chunks, ignore_index=True)

spuf30 = load_spuf_30("2026Q3", set(m27["ndc11"].unique()))
j = spuf30.merge(m27[["ndc11", "drug_short", "unit_mfp"]].drop_duplicates("ndc11"), left_on="NDC", right_on="ndc11")
j = j.merge(latest_nadac, on="ndc11", how="left")
j["ratio"] = j["UNIT_COST"] / j["unit_mfp"]
j["sub_brand"] = j["NDC Description"].str.extract(r"^([A-Z]+(?:\s+XR|\s+ELLIPTA)?)")[0].fillna("UNKNOWN")

print("=== 1. SUB-BRAND SPUF RATIOS IN 2026Q3 ===")
for drug in ["OZEMPIC", "JANUMET", "AUSTEDO", "BREO ELLIPTA"]:
    sub = j[j["drug_short"] == drug]
    print(f"\nDrug: {drug} (overall median={sub['ratio'].median():.4f}, n={len(sub)})")
    for (sb, cls), g in sub.groupby(["sub_brand", "Classification for Rate Setting"], dropna=False):
        print(f"  {str(sb):18s} (Class={cls}): n={len(g):6d}, unit_mfp={np.round(g['unit_mfp'].unique(), 4)}, median_r={g['ratio'].median():.4f}, 1/r-1={(1/g['ratio'].median()-1)*100:.2f}%")

print("\n=== 2. SPEARMAN CORRELATION ON 2026 CALIBRATION ===")
cal = pd.read_csv("pharma/outputs/prereg_2027/calibration_2026.csv")
rho_all = cal["predicted"].corr(cal["realized"], method="spearman")
cal8 = cal[~cal["drug"].isin(["ENTRESTO", "NOVOLOG"])]
rho_8 = cal8["predicted"].corr(cal8["realized"], method="spearman")
print(f"Spearman rho (all 10): {rho_all:.4f}")
print(f"Spearman rho (8 excluding Entresto & NovoLog): {rho_8:.4f}")

print("\n=== 3. SIBLING BRANDS IN LATEST NADAC 2026 ===")
latest_all = nadac26[nadac26["as_of_dt"] == nadac26["as_of_dt"].max()]
for sib in ["JENTADUETO", "ANORO", "INCRUSE", "ARNUITY", "SYNJARDY", "XIGDUO", "QTERN", "TRIJARDY", "GLYXAMBI", "WEGOVY", "RYBELSUS", "MOUNJARO", "ZEPBOUND", "TRULICITY"]:
    m = latest_all[latest_all["NDC Description"].str.upper().str.contains(sib, na=False)]
    print(f"  {sib:12s}: {len(m):3d} NDCs in latest NADAC")

print("\n=== 4. IPAY 2028 COHORT IN PART D 2026 Q1 ===")
partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
q1 = partd[(partd["Mftr_Name"] == "Overall") & (partd["Year"] == "2026 (Q1)")].copy()
q1["brnd_upper"] = q1["Brnd_Name"].str.upper().str.strip()
m28_names = mfp_valid[mfp_valid["IPAY"] == "2028"]["Selected Drug Name"].unique()
tot_c, tot_s = 0, 0
for sname in sorted(m28_names):
    parts = [p.strip().upper() for p in sname.split(";")]
    mask = pd.Series(False, index=q1.index)
    for p in parts:
        mask = mask | (q1["brnd_upper"] == p) | (q1["brnd_upper"].str.startswith(p + " "))
    sub = q1[mask]
    spend = sub["Tot_Spndng"].sum()
    claims = sub["Tot_Clms"].sum()
    pc = spend / claims if claims > 0 else 0
    if sname != "TRADJENTA":
        tot_c += claims
        tot_s += spend
    print(f"  {parts[0]:18s}: claims={claims:10,.0f}, spend=${spend:14,.2f}, per_claim=${pc:10,.2f}")
print(f"Total IPAY 2028 (excl Tradjenta): claims={tot_c:,.0f}, spend=${tot_s:,.2f}")
