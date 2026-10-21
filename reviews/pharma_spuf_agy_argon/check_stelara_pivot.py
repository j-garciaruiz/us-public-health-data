import pandas as pd

df30 = pd.read_pickle("/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch/spuf_matched_30d.pkl")
st = df30[df30["NDC"].str.startswith("57894")].copy()
st["PLAN_KEY"] = st["CONTRACT_ID"] + "|" + st["PLAN_ID"] + "|" + st["SEGMENT_ID"]

for rel in ["2025Q3", "2025Q4", "2026Q3"]:
    print(f"\n=== STELARA PIVOT IN {rel} ===")
    piv = st[st["RELEASE"] == rel].pivot(index="PLAN_KEY", columns="NDC", values="UNIT_COST")
    print("Columns present:", list(piv.columns))
    print("Total plans:", len(piv))
    if "57894044001" in piv.columns and "57894044003" in piv.columns:
        both = piv.dropna(subset=["57894044001", "57894044003"]).copy()
        both["ratio_03_to_01"] = both["57894044003"] / both["57894044001"]
        print("Ratio of 57894044003 to 57894044001 across plans:")
        print(both["ratio_03_to_01"].describe())
        print("Sample rows of pivot:")
        print(both.head(10).to_string())
    # Also check unique values of each column
    for c in piv.columns:
        s = piv[c].dropna()
        print(f"  {c}: n={len(s)}, min={s.min():.4f}, p5={s.quantile(0.05):.4f}, med={s.median():.4f}, p95={s.quantile(0.95):.4f}, max={s.max():.4f}")
        print("    top 5 values:", s.round(4).value_counts().head(5).to_dict())
