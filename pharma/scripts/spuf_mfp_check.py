"""Do Part D plans price the negotiated drugs at the Maximum Fair Price?

Reads the pricing tables of CMS's quarterly Prescription Drug Plan Formulary, Pharmacy Network
and Pricing Information files (SPUF) and compares each plan's unit cost for every NDC on the CMS
negotiation list with that NDC's MFP per unit.

Snapshots (CMS release, internal label, what it holds):
  SPUF_2025_20251009  PPUF_2025Q3  plan year 2025, before negotiated prices
  SPUF_2026_20260107  PPUF_2025Q4  plan year 2026 as of January 2026 (despite the 2025Q4 label,
                                   prices already reflect 2026 plan year; checked on Eliquis)
  SPUF_2026_20261007  PPUF_2026Q3  plan year 2026 as of the third quarter

Groups: IPAY 2026 NDCs (MFP in effect in 2026) and IPAY 2027 NDCs (MFP from 2027, so 2026 plan
prices should NOT be at the MFP: a built-in comparison).

Inputs: data/raw/pharma/spuf/<label>/pricing file PPUF_<label>.zip (fetch_spuf.py),
        data/raw/pharma/ira/selected_drugs_mfp.csv (fetch_ira_inputs.py)
Outputs: pharma/outputs/spuf/*.csv, summary.md, chart_plan_price_vs_mfp.png
"""
import io
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "pharma"
OUT = ROOT / "pharma" / "outputs" / "spuf"
SNAPSHOTS = [  # (label used in outputs, folder, description)
    ("2025 (Oct 2025 release)", "2025Q3", "plan year 2025"),
    ("2026 (Jan 2026 release)", "2025Q4", "plan year 2026, January"),
    ("2026 (Oct 2026 release)", "2026Q3", "plan year 2026, third quarter"),
]
DAYS = "30"          # 30-day supply rows (plans also report 60/90; unit costs are usually the same)
AT_MFP_TOL = 0.005   # plan unit cost within 0.5% of the MFP counts as "at the MFP"


def load_mfp():
    d = pd.read_csv(RAW / "ira" / "selected_drugs_mfp.csv", dtype=str, encoding="latin-1")
    d["NDC"] = d["NDC-11"].str.replace("-", "", regex=False)
    d["mfp_unit"] = pd.to_numeric(d["NDC-9 MFP per Unit Price"], errors="coerce")
    d["start"] = pd.to_datetime(d["MFP Effective Date"], format="%m/%d/%Y")
    d["end"] = pd.to_datetime(d["MFP End Date"], format="%m/%d/%Y").fillna(pd.Timestamp(2099, 1, 1))
    d["drug"] = d["Selected Drug Name"].str.split(";").str[0].str.strip()
    d = d.dropna(subset=["mfp_unit"])
    d = d[d.end >= d.start]  # drop superseded rows CMS keeps (end date before start)
    # MFP for the first year it applies to each NDC (2026 for IPAY 2026, 2027 for IPAY 2027).
    first = d.sort_values("start").drop_duplicates("NDC")
    first = first[first.IPAY.isin(["2026", "2027"])]
    # The 2026 MFP in effect from 2026-06-01 (Entresto Sprinkle was corrected mid-year).
    mid26 = d[(d.IPAY == "2026") & (d.start <= "2026-07-01") & (d.end >= "2026-07-01")].drop_duplicates("NDC")
    m = first[["NDC", "IPAY", "drug", "mfp_unit"]].rename(columns={"mfp_unit": "mfp_first"})
    m = m.merge(mid26[["NDC", "mfp_unit"]].rename(columns={"mfp_unit": "mfp_mid2026"}), on="NDC", how="left")
    return m


def read_pricing(folder, ndcs):
    """Stream one pricing table and keep rows for the given NDCs and 30-day supply."""
    z = RAW / "spuf" / folder / f"pricing file PPUF_{folder}.zip"
    keep = []
    with zipfile.ZipFile(z) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as fh:
            for chunk in pd.read_csv(io.TextIOWrapper(fh, encoding="latin-1"), sep="|", dtype=str,
                                     chunksize=2_000_000):
                c = chunk[(chunk.DAYS_SUPPLY == DAYS) & chunk.NDC.isin(ndcs)]
                if len(c):
                    keep.append(c)
    p = pd.concat(keep, ignore_index=True)
    p["unit_cost"] = pd.to_numeric(p.UNIT_COST, errors="coerce")
    p["plan"] = p.CONTRACT_ID + "-" + p.PLAN_ID + "-" + p.SEGMENT_ID
    p["plan_type"] = p.CONTRACT_ID.str[0].map({"S": "Stand-alone PDP"}).fillna("Medicare Advantage")
    return p.drop(columns=["UNIT_COST"])


def summarize(df, keys):
    def f(g):
        r = g.ratio
        return pd.Series({
            "plan_ndc_rows": len(g), "plans": g.plan.nunique(), "ndcs": g.NDC.nunique(),
            "median_ratio": r.median(), "p05": r.quantile(0.05), "p95": r.quantile(0.95),
            "share_at_mfp": ((r - 1).abs() <= AT_MFP_TOL).mean(),
            "share_below_mfp": (r < 1 - AT_MFP_TOL).mean(),
            "share_above_mfp": (r > 1 + AT_MFP_TOL).mean(),
        })
    return df.groupby(keys).apply(f, include_groups=False).reset_index()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mfp = load_mfp()
    ndcs = set(mfp.NDC)
    frames = []
    for label, folder, desc in SNAPSHOTS:
        p = read_pricing(folder, ndcs).merge(mfp, on="NDC")
        p["snapshot"] = label
        # IPAY 2026: the January file is compared with the MFP in effect in January; the 2025 baseline
        # and the October file with the MFP in effect mid-2026 (CMS corrected Entresto Sprinkle from June).
        ref = (p.mfp_first if folder == "2025Q4" else p.mfp_mid2026).fillna(p.mfp_first)
        p["mfp_ref"] = ref.where(p.IPAY == "2026", p.mfp_first)
        p["ratio"] = p.unit_cost / p.mfp_ref
        frames.append(p)
        print(f"{label}: {len(p):,} rows, {p.plan.nunique():,} plans, {p.NDC.nunique()} NDCs")
    allp = pd.concat(frames, ignore_index=True)
    allp.to_csv(OUT / "plan_prices_selected_ndcs.csv.gz", index=False)

    order = [s[0] for s in SNAPSHOTS]
    by_group = summarize(allp, ["IPAY", "snapshot"])
    by_group["snapshot"] = pd.Categorical(by_group.snapshot, order)
    by_group = by_group.sort_values(["IPAY", "snapshot"])
    by_drug = summarize(allp, ["IPAY", "drug", "snapshot"])
    by_drug["snapshot"] = pd.Categorical(by_drug.snapshot, order)
    by_drug = by_drug.sort_values(["IPAY", "drug", "snapshot"])
    by_type = summarize(allp[allp.IPAY == "2026"], ["plan_type", "snapshot"])
    by_group.to_csv(OUT / "ratio_by_group.csv", index=False)
    by_drug.to_csv(OUT / "ratio_by_drug.csv", index=False)
    by_type.to_csv(OUT / "ratio_by_plan_type_ipay2026.csv", index=False)
    sens = sensitivities(allp, order)
    sens.to_csv(OUT / "sensitivity_weights_panel.csv", index=False)

    # Rows priced above the MFP in 2026: which drugs and NDCs.
    above = allp[(allp.IPAY == "2026") & (allp.snapshot != order[0]) & (allp.ratio > 1 + AT_MFP_TOL)]
    above_sum = (above.groupby(["snapshot", "drug", "NDC"])
                 .agg(rows=("plan", "size"), median_ratio=("ratio", "median"), max_ratio=("ratio", "max"))
                 .reset_index().sort_values("rows", ascending=False))
    above_sum.to_csv(OUT / "above_mfp_2026.csv", index=False)

    chart(by_drug, order)
    write_summary(by_group, by_drug, by_type, above_sum, sens)


def sensitivities(allp, order):
    """Share of IPAY 2026 rows within the tolerance under other weightings, and in a fixed panel.

    unweighted: plan-segment x NDC rows (the headline measure; drugs with more NDCs count more).
    equal_drug: share within each drug family, then a simple mean across the ten families.
    claims_2025 / spending_2025: drug-family shares weighted by 2025 Part D claims or gross spending
      (Quarterly Part D Spending by Drug; built by ira_analysis.py).
    fixed_panel: unweighted, restricted to plan-segment x NDC pairs present in all three releases.
    """
    d = allp[allp.IPAY == "2026"].copy()
    d["within"] = (d.ratio - 1).abs() <= AT_MFP_TOL
    w = pd.read_csv(ROOT / "pharma" / "outputs" / "ira" / "partd_per_claim_by_drug.csv")
    w = w[w.group == "IPAY 2026"].set_index("drug")
    key = d.plan + "|" + d.NDC
    in_all = key.groupby(d.snapshot).apply(set)
    panel = set.intersection(*in_all.values)
    rows = []
    for snap in order:
        x = d[d.snapshot == snap]
        by_drug = x.groupby("drug").within.mean()
        rows.append({
            "snapshot": snap,
            "unweighted": x.within.mean(),
            "equal_drug": by_drug.mean(),
            "claims_2025": (by_drug * w.Tot_Clms_2025.reindex(by_drug.index)).sum() / w.Tot_Clms_2025.reindex(by_drug.index).sum(),
            "spending_2025": (by_drug * w.Tot_Spndng_2025.reindex(by_drug.index)).sum() / w.Tot_Spndng_2025.reindex(by_drug.index).sum(),
            "fixed_panel": x[(x.plan + "|" + x.NDC).isin(panel)].within.mean(),
            "fixed_panel_rows": int((x.plan + "|" + x.NDC).isin(panel).sum()),
        })
    return pd.DataFrame(rows)


def chart(by_drug, order):
    d = by_drug[by_drug.IPAY == "2026"]
    drugs = sorted(d.drug.unique())
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = {order[0]: "#9aa5b1", order[1]: "#00B5B4", order[2]: "#1B2A4A"}
    for i, drug in enumerate(drugs):
        for j, snap in enumerate(order):
            r = d[(d.drug == drug) & (d.snapshot == snap)]
            if len(r):
                y = i + (j - 1) * 0.22
                ax.plot([r.p05.iloc[0], r.p95.iloc[0]], [y, y], color=colors[snap], lw=1.4)
                ax.scatter(r.median_ratio, y, color=colors[snap], s=26, zorder=3,
                           label=snap if i == 0 else None)
    ax.axvline(1, color="black", ls="--", lw=1)
    ax.set_yticks(range(len(drugs)))
    ax.set_yticklabels(["NovoLog, Fiasp" if x == "NOVOLOG" else x.title() for x in drugs], fontsize=9)
    ax.set_xlabel("Plan unit cost / Maximum Fair Price per unit (median, 5th to 95th percentile)")
    ax.set_title("Reported Part D plan prices moved to the negotiated price in January 2026", loc="left", fontsize=12)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Source: CMS Prescription Drug Plan Formulary, Pharmacy Network and Pricing files (30-day "
             "supply rows, unweighted plan-NDC pairs);\nCMS negotiation file (2026-09-21). 1.0 = plan unit cost "
             "equals the MFP.", fontsize=7.5, color="grey")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "chart_plan_price_vs_mfp.png", dpi=200)
    plt.close(fig)


def md(df, pct=(), ratio=()):
    out = df.copy()
    for c in pct:
        out[c] = out[c].map(lambda v: "" if pd.isna(v) else f"{v:.1%}")
    for c in ratio:
        out[c] = out[c].map(lambda v: "" if pd.isna(v) else f"{v:.3f}")
    for c in ("plan_ndc_rows", "plans", "ndcs", "rows"):
        if c in out:
            out[c] = out[c].map(lambda v: f"{int(v):,}")
    cols = list(out.columns)
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(str(v) for v in r) + " |" for r in out.itertuples(index=False)])


def write_summary(by_group, by_drug, by_type, above_sum, sens):
    pc = ["share_at_mfp", "share_below_mfp", "share_above_mfp"]
    rc = ["median_ratio", "p05", "p95"]
    text = [
        "# Part D plan prices vs the Maximum Fair Price",
        "",
        "Generated by `pharma/scripts/spuf_mfp_check.py`. Ratio = plan unit cost (30-day supply) / MFP per unit. "
        "For IPAY 2026 drugs the MFP is in effect from 2026-01-01; for IPAY 2027 drugs it starts 2027-01-01, so "
        "their 2026 ratios measure the gap to the future 2027 MFP. Counts are plan-segment x NDC pairs "
        "(\"plans\" are contract-plan-segments), unweighted; \"at the MFP\" = within "
        f"{AT_MFP_TOL:.1%}. UNIT_COST is the plan's reported average retail unit price for the NDC, in NCPDP "
        "billing units (EA/ML/GM) like the MFP per unit; it excludes dispensing fees (reported separately) and "
        "includes concessions applied at the point of sale, but shows no rebate amounts, net plan spending or "
        "patient cost sharing. SPUF lists one proxy NDC per drug concept, so only some of the CMS list's NDCs "
        "appear, and the proxy can change between releases.",
        "",
        "## By group",
        "",
        md(by_group, pc, rc),
        "",
        "## Sensitivity: share of IPAY 2026 prices within the tolerance under other weights",
        "",
        md(sens, pct=["unweighted", "equal_drug", "claims_2025", "spending_2025", "fixed_panel"]),
        "",
        "## IPAY 2026 drugs by plan type",
        "",
        md(by_type, pc, rc),
        "",
        "## By drug",
        "",
        md(by_drug, pc, rc),
        "",
        "## IPAY 2026 plan prices above the MFP in 2026 (top 20 NDCs by rows)",
        "",
        md(above_sum.head(20), ratio=["median_ratio", "max_ratio"]),
        "",
    ]
    (OUT / "summary.md").write_text("\n".join(text))
    print("\n".join(text[:30]))


if __name__ == "__main__":
    main()
