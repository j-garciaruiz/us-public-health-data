import zipfile
import pandas as pd
import numpy as np

# 1. Load and clean selected_drugs_mfp.csv
mfp = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp["ndc11"] = mfp["NDC-11"].str.replace("-", "", regex=False).str.strip()
mfp["ndc9"] = mfp["NDC-9"].str.replace("-", "", regex=False).str.strip()
mfp["eff_dt"] = pd.to_datetime(mfp["MFP Effective Date"])
mfp["end_dt"] = pd.to_datetime(mfp["MFP End Date"])
mfp["unit_mfp"] = pd.to_numeric(mfp["NDC-9 MFP per Unit Price"])
mfp["mfp_30des"] = pd.to_numeric(mfp["Single MFP per 30 DES"])

# Exclude superseded rows (end_dt < eff_dt)
mfp_valid = mfp[~(mfp["end_dt"] < mfp["eff_dt"])].copy()

# IPAY 2026 active MFPs for 2026 (with Entresto Sprinkle corrected from 2026-06-01 -> MFP End Date == 12/31/2026)
mfp_2026 = mfp_valid[(mfp_valid["IPAY"] == "2026") & (mfp_valid["MFP End Date"] == "12/31/2026")].copy()
# IPAY 2026 continuing MFPs for 2027 (MFP Effective Date == 01/01/2027)
mfp_2026_cont = mfp_valid[(mfp_valid["IPAY"] == "2026") & (mfp_valid["MFP Effective Date"] == "01/01/2027")].copy()
# IPAY 2027 active MFPs for 2027
mfp_2027 = mfp_valid[mfp_valid["IPAY"] == "2027"].copy()

# 2. Load SPUF 2025Q3 and 2026Q3 (30-day supply)
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

spuf_25q3 = load_spuf_30("2025Q3", set(mfp_2026["ndc11"].unique()))
spuf_26q3 = load_spuf_30("2026Q3", set(mfp_2027["ndc11"].unique()))

# 3. Load Part D quarterly spending (Mftr_Name == 'Overall')
partd = pd.read_csv("data/raw/pharma/partd/partd_spending_quarterly.csv")
partd_ov = partd[partd["Mftr_Name"] == "Overall"].copy()
partd_ov["Brnd_upper"] = partd_ov["Brnd_Name"].str.upper().str.strip()

def get_partd_stats(sname, mode="broad"):
    exact_brands = [b.strip().upper() for b in sname.split(";")]
    if mode == "exact":
        sub = partd_ov[partd_ov["Brnd_upper"].isin(exact_brands)]
    else:
        prefixes = [b.split()[0] for b in exact_brands]
        pattern = "|".join([f"^{p}\\b" for p in set(prefixes)])
        sub = partd_ov[partd_ov["Brnd_upper"].str.contains(pattern, regex=True, na=False)]
        sub = sub[~sub["Brnd_upper"].str.contains("NOVOLOG MIX", na=False)]
    y25 = sub[sub["Year"] == "2025 (Q1-Q4)"]
    y26 = sub[sub["Year"] == "2026 (Q1)"]
    c25, s25 = y25["Tot_Clms"].sum(), y25["Tot_Spndng"].sum()
    c26, s26 = y26["Tot_Clms"].sum(), y26["Tot_Spndng"].sum()
    p25 = s25 / c25 if c25 else np.nan
    p26 = s26 / c26 if c26 else np.nan
    realized = (p26 / p25 - 1.0) if (c25 and c26) else np.nan
    return {
        "brands": sorted(sub["Brnd_Name"].unique().tolist()),
        "clms_2025": c25, "spnd_2025": s25, "spc_2025": p25,
        "clms_2026q1": c26, "spnd_2026q1": s26, "spc_2026q1": p26,
        "realized": realized
    }

# Compute Part A.1: IPAY 2026 drugs
m26 = spuf_25q3.merge(mfp_2026[["Selected Drug Name", "ndc11", "unit_mfp", "mfp_30des"]], left_on="NDC", right_on="ndc11", how="inner")
m26["ratio"] = m26["UNIT_COST"] / m26["unit_mfp"]

rows_26 = []
for sname in mfp_2026["Selected Drug Name"].unique():
    d = m26[m26["Selected Drug Name"] == sname]
    r = d["ratio"].median()
    pred = 1.0 / r - 1.0
    st_broad = get_partd_stats(sname, mode="broad")
    st_exact = get_partd_stats(sname, mode="exact")
    rows_26.append({
        "drug": sname,
        "n_rows": len(d),
        "n_ndc": d["NDC"].nunique(),
        "mfp_30des": d["mfp_30des"].iloc[0],
        "r": r,
        "pred": pred,
        **{f"broad_{k}": v for k, v in st_broad.items()},
        **{f"exact_{k}": v for k, v in st_exact.items()},
    })
df26 = pd.DataFrame(rows_26)
df26["err_broad_real_minus_pred"] = df26["broad_realized"] - df26["pred"]
df26["err_broad_pred_minus_real"] = df26["pred"] - df26["broad_realized"]
df26["err_exact_real_minus_pred"] = df26["exact_realized"] - df26["pred"]

print("=== PART A.1: IPAY 2026 Calibration ===")
for mode in ["broad", "exact"]:
    print(f"\n--- Mode: {mode} ---")
    for _, row in df26.iterrows():
        print(f"{row['drug'][:35]:35s} | n={row['n_rows']:5d} | r={row['r']:.4f} | pred={row['pred']*100:+.2f}% | spc25=${row[f'{mode}_spc_2025']:,.2f} | spc26Q1=${row[f'{mode}_spc_2026q1']:,.2f} | real={row[f'{mode}_realized']*100:+.2f}% | err(R-P)={(row[f'{mode}_realized']-row['pred'])*100:+.2f} pp | brands={row[f'{mode}_brands']}")
    # Fixed 2025 claim mix:
    # 1) Total spending change holding 2025 claims fixed (= spending-weighted average of % changes)
    tot_s25 = df26[f"{mode}_spnd_2025"].sum()
    tot_c25 = df26[f"{mode}_clms_2025"].sum()
    pred_spend_wt = (df26[f"{mode}_spnd_2025"] * df26["pred"]).sum() / tot_s25
    real_spend_wt = (df26[f"{mode}_spnd_2025"] * df26[f"{mode}_realized"]).sum() / tot_s25
    # Wait: also check fixed 2025 claim mix on group per-claim spending:
    # Group per-claim spending in 2025 is sum(c25 * spc25)/sum(c25) = tot_s25 / tot_c25.
    # At fixed 2025 claim mix, group per-claim spending in 2026Q1 is sum(c25 * spc26Q1)/sum(c25).
    # Notice that (sum(c25 * spc26Q1)/sum(c25)) / (tot_s25 / tot_c25) - 1 == sum(c25 * spc25 * (spc26Q1/spc25 - 1)) / tot_s25 == real_spend_wt!
    # 2) Claim-weighted average of % changes: sum(c25 * chg) / sum(c25)
    pred_clm_wt = (df26[f"{mode}_clms_2025"] * df26["pred"]).sum() / tot_c25
    real_clm_wt = (df26[f"{mode}_clms_2025"] * df26[f"{mode}_realized"]).sum() / tot_c25
    # 3) Raw pooled group per-claim spending change (unfixed mix): (sum(s26)/sum(c26)) / (sum(s25)/sum(c25)) - 1
    raw_spc25 = tot_s25 / tot_c25
    raw_spc26 = df26[f"{mode}_spnd_2026q1"].sum() / df26[f"{mode}_clms_2026q1"].sum()
    raw_real_chg = raw_spc26 / raw_spc25 - 1.0
    print(f"  [Fixed 2025 claim mix -> group per-claim spending (spend-weighted % chg)]: Pred={pred_spend_wt*100:+.2f}%, Real={real_spend_wt*100:+.2f}%, Diff(R-P)={(real_spend_wt-pred_spend_wt)*100:+.2f} pp")
    print(f"  [Claim-count-weighted average of drug % changes]:                         Pred={pred_clm_wt*100:+.2f}%, Real={real_clm_wt*100:+.2f}%, Diff(R-P)={(real_clm_wt-pred_clm_wt)*100:+.2f} pp")
    print(f"  [Unweighted mean across 10 drugs]:                                        Pred={df26['pred'].mean()*100:+.2f}%, Real={df26[f'{mode}_realized'].mean()*100:+.2f}%, MAE={(df26[f'{mode}_realized']-df26['pred']).abs().mean()*100:.2f} pp")
    print(f"  [Raw unfixed group per-claim spending]: 2025=${raw_spc25:,.2f} -> 2026Q1=${raw_spc26:,.2f} ({raw_real_chg*100:+.2f}%)")

# Compute Part A.2: IPAY 2027 cohort
m27 = spuf_26q3.merge(mfp_2027[["Selected Drug Name", "ndc11", "unit_mfp", "mfp_30des"]], left_on="NDC", right_on="ndc11", how="inner")
m27["ratio"] = m27["UNIT_COST"] / m27["unit_mfp"]

rows_27 = []
for sname in mfp_2027["Selected Drug Name"].unique():
    d = m27[m27["Selected Drug Name"] == sname]
    r = d["ratio"].median()
    pred = 1.0 / r - 1.0
    st_broad = get_partd_stats(sname, mode="broad")
    st_exact = get_partd_stats(sname, mode="exact")
    rows_27.append({
        "drug": sname,
        "n_rows": len(d),
        "n_ndc": d["NDC"].nunique(),
        "mfp_30des": d["mfp_30des"].iloc[0],
        "r": r,
        "pred": pred,
        **{f"broad_{k}": v for k, v in st_broad.items()},
        **{f"exact_{k}": v for k, v in st_exact.items()},
    })
df27 = pd.DataFrame(rows_27)

print("\n=== PART A.2: IPAY 2027 Cohort ===")
for mode in ["broad", "exact"]:
    print(f"\n--- Mode: {mode} ---")
    df27[f"{mode}_removed_q1"] = -df27["pred"] * df27[f"{mode}_spnd_2026q1"]
    df27[f"{mode}_proj_spc_2027"] = df27[f"{mode}_spc_2026q1"] * (1.0 + df27["pred"])
    for _, row in df27.iterrows():
        print(f"{row['drug'][:30]:30s} | n={row['n_rows']:5d} | r={row['r']:.4f} | pred={row['pred']*100:+.2f}% | spc26Q1=${row[f'{mode}_spc_2026q1']:,.2f} | clms26Q1={row[f'{mode}_clms_2026q1']:9,d} | spnd26Q1=${row[f'{mode}_spnd_2026q1']/1e6:8.2f}M | rem_Q1=${row[f'{mode}_removed_q1']/1e6:8.2f}M")
    tot_s26q1 = df27[f"{mode}_spnd_2026q1"].sum()
    tot_c26q1 = df27[f"{mode}_clms_2026q1"].sum()
    tot_rem_q1 = df27[f"{mode}_removed_q1"].sum()
    grp_chg_spend_wt = (df27[f"{mode}_spnd_2026q1"] * df27["pred"]).sum() / tot_s26q1
    grp_chg_clm_wt = (df27[f"{mode}_clms_2026q1"] * df27["pred"]).sum() / tot_c26q1
    base_grp_spc = tot_s26q1 / tot_c26q1
    proj_grp_spc = (tot_s26q1 - tot_rem_q1) / tot_c26q1
    print(f"  Total 2026 Q1 claims: {tot_c26q1:,}, Total 2026 Q1 spending: ${tot_s26q1:,.2f} (${tot_s26q1/1e9:.4f}B)")
    print(f"  Group per-claim spending (2026 Q1): ${base_grp_spc:,.2f} -> Projected 2027 at fixed 2026 Q1 claim mix: ${proj_grp_spc:,.2f}")
    print(f"  Group change at fixed 2026 Q1 claim mix (spend-weighted): {grp_chg_spend_wt*100:+.2f}%")
    print(f"  Claim-count-weighted average of drug % changes:           {grp_chg_clm_wt*100:+.2f}%")
    print(f"  Unweighted mean / median across 15 drugs:                 {df27['pred'].mean()*100:+.2f}% / {df27['pred'].median()*100:+.2f}%")
    print(f"  Gross spending removed at 2026 Q1 volumes (1 quarter):    ${tot_rem_q1:,.2f} (${tot_rem_q1/1e9:.4f}B)")
    print(f"  Gross spending removed annualized (x4):                   ${tot_rem_q1*4:,.2f} (${tot_rem_q1*4/1e9:.4f}B)")
