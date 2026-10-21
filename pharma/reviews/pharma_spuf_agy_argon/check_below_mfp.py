import pandas as pd

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

lookup_rows = []
for rel, src in [("2025Q3", late26), ("2025Q4", early26), ("2026Q3", late26)]:
    tmp = src[["IPAY", "Selected Drug Name", "NDC-11", "NDC11", "MFP_UNIT"]].copy()
    tmp["RELEASE"] = rel
    lookup_rows.append(tmp)
lookup = pd.concat(lookup_rows, ignore_index=True)

m = df30.merge(lookup, left_on=["NDC", "RELEASE"], right_on=["NDC11", "RELEASE"], how="inner")
m["RATIO"] = m["UNIT_COST"] / m["MFP_UNIT"]

for rel in ["2025Q4", "2026Q3"]:
    print(f"\n=== BELOW MFP (< 0.995) IN {rel} BY DRUG AND NDC ===")
    sub = m[(m["RELEASE"] == rel) & (m["RATIO"] < 0.995)]
    print(sub.groupby(["Selected Drug Name", "NDC-11", "MFP_UNIT"]).agg(
        rows=("RATIO", "count"),
        min_ratio=("RATIO", "min"),
        med_ratio=("RATIO", "median"),
        max_ratio=("RATIO", "max"),
        top_ratios=("RATIO", lambda s: s.round(4).value_counts().head(3).to_dict())
    ).reset_index().to_string(index=False))

print("\n=== DISTRIBUTION OF RATIO AROUND 1.0 FOR ALL IPAY 2026 IN 2025Q4 AND 2026Q3 ===")
for rel in ["2025Q4", "2026Q3"]:
    s = m[m["RELEASE"] == rel]["RATIO"]
    for tol in [0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.02]:
        w = ((s - 1).abs() <= tol).mean() * 100
        b = (s < 1 - tol).mean() * 100
        a = (s > 1 + tol).mean() * 100
        print(f"  {rel} tol={tol*100:.2f}%: within={w:.2f}%, below={b:.2f}%, above={a:.2f}% (n_above={(s > 1 + tol).sum()}, n_below={(s < 1 - tol).sum()})")
