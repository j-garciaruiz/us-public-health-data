import pandas as pd
import numpy as np

print("=== 2. SPEARMAN CORRELATION ON 2026 CALIBRATION ===")
cal = pd.read_csv("pharma/outputs/prereg_2027/calibration_2026.csv")
print(cal.columns.tolist())
pcol = "predicted"
rcol = "chg_per_claim"
rho_all = cal[pcol].rank().corr(cal[rcol].rank())
cal8 = cal[~cal["drug"].isin(["ENTRESTO", "NOVOLOG"])]
rho_8 = cal8[pcol].rank().corr(cal8[rcol].rank())
print(f"Spearman rho (all 10): {rho_all:.4f}")
print(f"Spearman rho (8 excluding Entresto & NovoLog): {rho_8:.4f}")

print("\n=== 3. SIBLING BRANDS IN LATEST NADAC 2026 ===")
nadac26 = pd.read_csv("data/raw/pharma/nadac/nadac_2026.csv", dtype=str)
nadac26["ndc11"] = nadac26["NDC"].str.strip().str.zfill(11)
nadac26["as_of_dt"] = pd.to_datetime(nadac26["As of Date"])
latest_all = nadac26[nadac26["as_of_dt"] == nadac26["as_of_dt"].max()]
for sib in ["JENTADUETO", "ANORO", "INCRUSE", "ARNUITY", "SYNJARDY", "XIGDUO", "QTERN", "TRIJARDY", "GLYXAMBI", "WEGOVY", "RYBELSUS", "OZEMPIC", "MOUNJARO", "ZEPBOUND", "TRULICITY"]:
    m = latest_all[latest_all["NDC Description"].str.upper().str.contains(sib, na=False)]
    print(f"  {sib:12s}: {len(m):3d} NDCs in latest NADAC (B={(m['Classification for Rate Setting']=='B').sum()}, G={(m['Classification for Rate Setting']=='G').sum()})")

print("\n=== 4. IPAY 2028 COHORT IN PART D 2026 Q1 & 2025 ===")
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp_valid = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()

partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
ov = partd[partd["Mftr_Name"] == "Overall"].copy()
ov["brnd_upper"] = ov["Brnd_Name"].str.upper().str.strip()
m28_names = mfp_valid[mfp_valid["IPAY"] == "2028"]["Selected Drug Name"].unique()
print("IPAY 2028 Selected Drug Names:", len(m28_names), sorted(m28_names))
tot_c25, tot_s25, tot_c26, tot_s26 = 0, 0, 0, 0
for sname in sorted(m28_names):
    parts = [p.strip().upper() for p in sname.split(";")]
    mask = pd.Series(False, index=ov.index)
    for p in parts:
        mask = mask | (ov["brnd_upper"] == p) | (ov["brnd_upper"].str.startswith(p + " "))
    sub25 = ov[mask & (ov["Year"] == "2025 (Q1-Q4)")]
    sub26 = ov[mask & (ov["Year"] == "2026 (Q1)")]
    s25, c25 = sub25["Tot_Spndng"].sum(), sub25["Tot_Clms"].sum()
    s26, c26 = sub26["Tot_Spndng"].sum(), sub26["Tot_Clms"].sum()
    pc25 = s25 / c25 if c25 > 0 else 0
    pc26 = s26 / c26 if c26 > 0 else 0
    chg = (pc26 / pc25 - 1) * 100 if pc25 > 0 else np.nan
    if sname != "TRADJENTA":
        tot_c25 += c25; tot_s25 += s25; tot_c26 += c26; tot_s26 += s26
    print(f"  {parts[0]:18s}: c26={c26:10,.0f}, s26=${s26:13,.0f}, pc25=${pc25:9,.2f}, pc26=${pc26:9,.2f}, chg={chg:+6.2f}%")
print(f"Total IPAY 2028 (excl Tradjenta): c26={tot_c26:,.0f}, s26=${tot_s26:,.0f}")
