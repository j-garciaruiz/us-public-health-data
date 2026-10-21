import pandas as pd
import numpy as np

# Load 30-day SPUF rows
df30 = pd.read_pickle("/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch/spuf_matched_30d.pkl")

# Load MFP file
mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
mfp_df["MFP_UNIT"] = pd.to_numeric(mfp_df["NDC-9 MFP per Unit Price"], errors="coerce")
mfp_df["EFF"] = pd.to_datetime(mfp_df["MFP Effective Date"])
mfp_df["END"] = pd.to_datetime(mfp_df["MFP End Date"])

valid_mfp = mfp_df[mfp_df["END"].isna() | (mfp_df["END"] >= mfp_df["EFF"])].copy()

# Build MFP lookup per (NDC11, RELEASE) for IPAY 2026 and 2027
# IPAY 2026:
# - 2025Q3: late 2026 MFP (corrected 2026 value for Entresto Sprinkle, i.e., effective 2026-06-01..2026-12-31)
# - 2025Q4: early 2026 MFP (in effect Jan 2026, i.e., effective 2026-01-01..2026-05-31)
# - 2026Q3: late 2026 MFP (in effect Oct 2026, i.e., effective 2026-06-01..2026-12-31)
# IPAY 2027:
# - all releases: 2027 MFP (effective 2027-01-01)

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
m["PLAN_KEY_SEG"] = m["CONTRACT_ID"] + "|" + m["PLAN_ID"] + "|" + m["SEGMENT_ID"]
m["PLAN_KEY_NOSEG"] = m["CONTRACT_ID"] + "|" + m["PLAN_ID"]
m["PLAN_TYPE"] = np.where(m["CONTRACT_ID"].str.startswith("S"), "PDP", "MA-PD / Other")

print("=== CHECK ENTRESTO SPRINKLE IN SPUF ===")
print(m[m["NDC-11"].isin(["00078-1231-20", "00078-1238-20"])].groupby(["RELEASE", "NDC-11"])["UNIT_COST"].describe())

print("\n=== CHECK BOUNDARY CASES NEAR 0.5% (|RATIO - 1| between 0.0049 and 0.0051) ===")
near = m[(m["RATIO"] - 1.0).abs().between(0.0049, 0.0051)]
print(f"Rows with |ratio - 1| in [0.0049, 0.0051]: {len(near)}")
if len(near) > 0:
    print(near[["RELEASE", "IPAY", "Selected Drug Name", "NDC-11", "UNIT_COST", "MFP_UNIT", "RATIO"]].drop_duplicates())

def summarize(df_sub):
    n_rows = len(df_sub)
    n_plans_seg = df_sub["PLAN_KEY_SEG"].nunique()
    n_plans_noseg = df_sub["PLAN_KEY_NOSEG"].nunique()
    n_contracts = df_sub["CONTRACT_ID"].nunique()
    n_ndcs = df_sub["NDC"].nunique()
    med = df_sub["RATIO"].median()
    p5 = df_sub["RATIO"].quantile(0.05)
    p95 = df_sub["RATIO"].quantile(0.95)
    within = ((df_sub["RATIO"] >= 0.995) & (df_sub["RATIO"] <= 1.005)).mean() * 100
    below = (df_sub["RATIO"] < 0.995).mean() * 100
    above = (df_sub["RATIO"] > 1.005).mean() * 100
    n_above = int((df_sub["RATIO"] > 1.005).sum())
    n_below = int((df_sub["RATIO"] < 0.995).sum())
    n_within = int(((df_sub["RATIO"] >= 0.995) & (df_sub["RATIO"] <= 1.005)).sum())
    return pd.Series({
        "rows": n_rows,
        "plans_seg": n_plans_seg,
        "plans_noseg": n_plans_noseg,
        "contracts": n_contracts,
        "ndcs": n_ndcs,
        "median": med,
        "p5": p5,
        "p95": p95,
        "within_pct": within,
        "below_pct": below,
        "above_pct": above,
        "n_within": n_within,
        "n_below": n_below,
        "n_above": n_above,
    })

print("\n=== SUMMARY BY IPAY AND RELEASE ===")
res_ipay = m.groupby(["IPAY", "RELEASE"], as_index=False).apply(summarize, include_groups=False)
print(res_ipay.to_string(index=False))

print("\n=== SUMMARY BY IPAY 2026 SPLIT BY PDP (S*) VS MA-PD ===")
res_pdp = m[m["IPAY"] == "2026"].groupby(["RELEASE", "PLAN_TYPE"], as_index=False).apply(summarize, include_groups=False)
print(res_pdp.to_string(index=False))

print("\n=== SUMMARY BY DRUG AND RELEASE (IPAY 2026) ===")
res_drug26 = m[m["IPAY"] == "2026"].groupby(["Selected Drug Name", "RELEASE"], as_index=False).apply(summarize, include_groups=False)
print(res_drug26.to_string(index=False))

print("\n=== SUMMARY BY DRUG AND RELEASE (IPAY 2027) ===")
res_drug27 = m[m["IPAY"] == "2027"].groupby(["Selected Drug Name", "RELEASE"], as_index=False).apply(summarize, include_groups=False)
print(res_drug27.to_string(index=False))

print("\n=== IPAY 2026 NDCs PRICED ABOVE MFP (> 0.5%, i.e., RATIO > 1.005) IN 2026 RELEASES ===")
above26 = m[(m["IPAY"] == "2026") & (m["RELEASE"].isin(["2025Q4", "2026Q3"])) & (m["RATIO"] > 1.005)]
print(above26.groupby(["RELEASE", "Selected Drug Name", "NDC-11", "NDC", "MFP_UNIT"]).agg(
    rows=("RATIO", "count"),
    plans_seg=("PLAN_KEY_SEG", "nunique"),
    plans_noseg=("PLAN_KEY_NOSEG", "nunique"),
    min_unit_cost=("UNIT_COST", "min"),
    median_unit_cost=("UNIT_COST", "median"),
    max_unit_cost=("UNIT_COST", "max"),
    min_ratio=("RATIO", "min"),
    median_ratio=("RATIO", "median"),
    max_ratio=("RATIO", "max"),
).reset_index().to_string(index=False))
