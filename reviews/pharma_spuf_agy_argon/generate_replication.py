import pandas as pd
import numpy as np

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
m["PLAN_KEY_SEG"] = m["CONTRACT_ID"] + "|" + m["PLAN_ID"] + "|" + m["SEGMENT_ID"]
m["PLAN_KEY_NOSEG"] = m["CONTRACT_ID"] + "|" + m["PLAN_ID"]

# Check H only vs H+R for Medicare Advantage
m26 = m[m["IPAY"] == "2026"].copy()
for rel in ["2025Q3", "2025Q4", "2026Q3"]:
    sub_h = m26[(m26["RELEASE"] == rel) & (m26["CONTRACT_ID"].str.startswith("H"))]
    sub_hr = m26[(m26["RELEASE"] == rel) & (~m26["CONTRACT_ID"].str.startswith("S"))]
    sub_r = m26[(m26["RELEASE"] == rel) & (m26["CONTRACT_ID"].str.startswith("R"))]
    print(f"{rel} H-only rows={len(sub_h)}, R-only rows={len(sub_r)}, H+R rows={len(sub_hr)}")
    for label_sub, s in [("H+R (non-S)", sub_hr), ("H only", sub_h), ("R only", sub_r)]:
        w = ((s["RATIO"] >= 0.995) & (s["RATIO"] <= 1.005)).mean() * 100
        b = (s["RATIO"] < 0.995).mean() * 100
        a = (s["RATIO"] > 1.005).mean() * 100
        print(f"  {label_sub}: plans_seg={s['PLAN_KEY_SEG'].nunique()}, plans_noseg={s['PLAN_KEY_NOSEG'].nunique()}, ndcs={s['NDC'].nunique()}, med={s['RATIO'].median():.4f}, p5={s['RATIO'].quantile(0.05):.4f}, p95={s['RATIO'].quantile(0.95):.4f}, within={w:.2f}%, below={b:.2f}%, above={a:.2f}%")

print("\n=== ALL STELARA NDCs ACROSS RELEASES ===")
st = m26[m26["Selected Drug Name"] == "STELARA"]
print(st.groupby(["RELEASE", "NDC-11", "MFP_UNIT"]).agg(
    rows=("RATIO", "count"),
    med_cost=("UNIT_COST", "median"),
    med_ratio=("RATIO", "median"),
    p5_ratio=("RATIO", lambda x: x.quantile(0.05)),
    p95_ratio=("RATIO", lambda x: x.quantile(0.95)),
    n_within=("RATIO", lambda x: ((x >= 0.995) & (x <= 1.005)).sum()),
    n_below=("RATIO", lambda x: (x < 0.995).sum()),
    n_above=("RATIO", lambda x: (x > 1.005).sum()),
).reset_index().to_string(index=False))
