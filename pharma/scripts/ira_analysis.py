"""IRA negotiation and drug prices: what changed in January 2026 (pharma idea 2).

Descriptive only. Three questions:
  1. List prices: did manufacturers cut WAC on negotiated drugs, and is that unusual
     compared with other brands and earlier Januaries? (NADAC Comparison, "WAC Adjustment" rows)
  2. Pharmacy acquisition price vs the negotiated price: NADAC per unit relative to the
     2026 Maximum Fair Price (MFP) per unit, NDC by NDC, weekly.
  3. Medicare Part D: gross spending per claim, 2025 full year vs 2026 Q1, for negotiated
     drugs vs drugs negotiated for 2027/2028 (MFP not yet in effect) vs other brands.

Inputs (fetch first): fetch_nadac.py 2024 2025 2026 --comparison; fetch_ira_inputs.py
Outputs: pharma/outputs/ira/*.csv, *.png, summary.md
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "pharma"
OUT = ROOT / "pharma" / "outputs" / "ira"
GROUPS = ["IPAY 2026", "IPAY 2027", "IPAY 2028", "Other brands"]
# Part D brand names that start with a selected name but are different products whose NDCs are not
# on the CMS selected list (NovoLog Mix 70/30 is premixed insulin aspart protamine). Reviewed 2026-10-20.
NOT_SELECTED = ("NOVOLOG MIX",)
# Part D rows that are supplies, not drugs (generic-name keywords); excluded from the comparator.
SUPPLY = r"NEEDL|SYRING|LANCET|TEST STRIP|DIAGNOSTIC|GLUCOSE|SENSOR|SUPPL|SWAB|ALCOHOL PREP"
CUT = -20.0  # a WAC cut of 20% or more counts as a large list-price cut
DISPLAY = {"NOVOLOG": "NovoLog", "FIASP": "Fiasp"}
# The CMS "NOVOLOG" entry covers two brands priced very differently; NADAC tables and the chart split them.
SPLIT_BY_PRODUCT = {"NOVOLOG"}


def label(drug):
    return DISPLAY.get(drug, drug.title())


def load_ira():
    d = pd.read_csv(RAW / "ira" / "selected_drugs_mfp.csv", dtype=str, encoding="latin-1")
    d["ndc11"] = d["NDC-11"].str.replace("-", "", regex=False)
    d["mfp_unit"] = pd.to_numeric(d["NDC-9 MFP per Unit Price"], errors="coerce")
    d["mfp_30"] = pd.to_numeric(d["Single MFP per 30 DES"], errors="coerce")
    d["drug"] = d["Selected Drug Name"].str.split(";").str[0].str.strip()
    # One group per NDC: the earliest price applicability year it was selected for.
    grp = d.sort_values("IPAY").drop_duplicates("ndc11")[["ndc11", "IPAY", "drug"]]
    grp["group"] = "IPAY " + grp.IPAY
    return d, grp


def load_nadac(years):
    cols = ["NDC Description", "NDC", "NADAC Per Unit", "Pricing Unit", "Classification for Rate Setting", "As of Date"]
    frames = []
    for y in years:
        f = pd.read_csv(RAW / "nadac" / f"nadac_{y}.csv", dtype=str, usecols=cols)
        frames.append(f)
    n = pd.concat(frames, ignore_index=True)
    n["as_of"] = pd.to_datetime(n["As of Date"], format="%m/%d/%Y")
    n["nadac"] = pd.to_numeric(n["NADAC Per Unit"])
    return n.drop(columns=["As of Date", "NADAC Per Unit"])


def wac_january(nadac, grp):
    """Share of brand NDCs with a large WAC cut effective in each January window."""
    comp = pd.read_csv(RAW / "nadac" / "nadac_comparison.csv", dtype=str)
    comp["eff"] = pd.to_datetime(comp["Effective Date"], format="%m/%d/%Y")
    comp["pct"] = pd.to_numeric(comp["Percent Change"])
    wac = comp[comp["Primary Reason"].str.contains("WAC", na=False)]

    rows, events = [], []
    for year, window in [(y, w) for y in (2024, 2025, 2026) for w in ("Dec 20-Jan 31", "Dec 20-Feb 28")]:
        lo = pd.Timestamp(year - 1, 12, 20)
        hi = pd.Timestamp(year, 1, 31) if window == "Dec 20-Jan 31" else pd.Timestamp(year, 2, 28)
        # Universe: NDCs priced as brands (class B) in any January snapshot of that year.
        jan = nadac[(nadac.as_of.dt.year == year) & (nadac.as_of.dt.month == 1)
                    & (nadac["Classification for Rate Setting"] == "B")]
        uni = pd.DataFrame({"NDC": jan.NDC.unique()}).merge(grp, left_on="NDC", right_on="ndc11", how="left")
        uni["group"] = uni["group"].fillna("Other brands")
        w = wac[(wac.eff >= lo) & (wac.eff <= hi)]
        # Largest cut and largest increase per NDC within the window.
        w_min = w.groupby("NDC").pct.min()
        w_max = w.groupby("NDC").pct.max()
        uni["cut"] = uni.NDC.map(w_min).le(CUT)
        uni["any_increase"] = uni.NDC.map(w_max).gt(0)
        for g in GROUPS:
            u = uni[uni.group == g]
            rows.append({"january": year, "window": window, "group": g, "brand_ndcs": len(u),
                         "ndcs_with_wac_cut_ge_20pct": int(u.cut.sum()),
                         "share_cut": u.cut.mean() if len(u) else float("nan"),
                         "ndcs_with_wac_increase": int(u.any_increase.sum()),
                         "share_increase": u.any_increase.mean() if len(u) else float("nan")})
        # One event per NDC and window: its most negative WAC-based change.
        ev = w.sort_values("pct").drop_duplicates("NDC")
        ev = ev[ev.NDC.isin(uni.NDC)].merge(uni[["NDC", "group", "drug"]], on="NDC")
        ev = ev[ev.pct <= CUT]
        ev["january"] = year
        if window == "Dec 20-Feb 28":
            events.append(ev)
    ev = pd.concat(events)
    # Product names (first word of the NADAC description) show which brands within a family moved.
    ev["product"] = ev["NDC Description"].str.split().str[0]
    # For non-selected brands, name the product by its NADAC description.
    ev["drug"] = ev["drug"].fillna(ev["NDC Description"])
    ev_sum = (ev.groupby(["january", "group", "drug"])
              .agg(products=("product", lambda s: "/".join(sorted(s.unique()))),
                   ndcs=("NDC", "nunique"), median_pct=("pct", "median"),
                   effective=("eff", lambda s: s.min().date().isoformat()))
              .reset_index().sort_values(["january", "group", "median_pct"]))
    return pd.DataFrame(rows), ev_sum


def nadac_vs_mfp(nadac, ira):
    """Weekly NADAC per unit divided by the 2026 MFP per unit, per NDC, for IPAY 2026 drugs."""
    # MFP rows in effect during 2026 (CMS corrects some mid-year, e.g. Entresto Sprinkle from 2026-06-01).
    m = ira[(ira.IPAY == "2026")].dropna(subset=["mfp_unit"]).copy()
    m["start"] = pd.to_datetime(m["MFP Effective Date"], format="%m/%d/%Y")
    m["end"] = pd.to_datetime(m["MFP End Date"], format="%m/%d/%Y").fillna(pd.Timestamp(2099, 1, 1))
    # Drop superseded rows whose end date precedes their start (CMS keeps them, e.g. Xarelto "End Date" rows).
    m = m[(m.start.dt.year == 2026) & (m.end >= m.start)][["ndc11", "drug", "mfp_unit", "start", "end"]].drop_duplicates()
    m26 = m.sort_values("start").drop_duplicates("ndc11")  # NDC list and first 2026 MFP
    x = nadac.merge(m, left_on="NDC", right_on="ndc11")
    # Use the MFP in effect on the snapshot date; snapshots before 2026 use each NDC's earliest 2026 MFP.
    first_start = x.groupby("NDC").start.transform("min")
    pre = x.as_of < pd.Timestamp(2026, 1, 1)
    x = x[(pre & (x.start == first_start)) | (~pre & (x.as_of >= x.start) & (x.as_of <= x.end))].copy()
    assert not x.duplicated(["NDC", "as_of"]).any()
    x["ratio"] = x.nadac / x.mfp_unit
    product = x["NDC Description"].str.split().str[0]
    x["drug"] = x.drug.where(~x.drug.isin(SPLIT_BY_PRODUCT) | ~product.isin(["NOVOLOG", "FIASP"]), product)
    x_all = x
    # Main measure: brand-classified NDCs. Unbranded and authorized-generic NDCs on the CMS list
    # (insulin aspart, dapagliflozin) carry generic NADAC rates and their own MFPs; kept as sensitivity.
    x = x[x["Classification for Rate Setting"].str.startswith("B")]
    weekly = x.groupby(["drug", "as_of"]).agg(ndcs=("NDC", "nunique"), median_ratio=("ratio", "median")).reset_index()
    last25 = x[x.as_of == x[x.as_of.dt.year == 2025].as_of.max()]
    last26 = x[x.as_of == x[x.as_of.dt.year == 2026].as_of.max()]
    both = last26[last26.NDC.isin(last25.NDC)]  # constant-NDC sensitivity
    by_drug = (x_all.groupby("drug").agg(mfp_ndcs_in_nadac=("NDC", "nunique")).join(
        last25.groupby("drug").agg(ndcs_dec2025=("NDC", "nunique"), ratio_dec2025=("ratio", "median"))).join(
        last26.groupby("drug").agg(ndcs_latest=("NDC", "nunique"), ratio_latest=("ratio", "median"),
                                   unit=("Pricing Unit", lambda s: "/".join(sorted(s.unique()))))).join(
        both.groupby("drug").agg(ratio_latest_same_ndcs=("ratio", "median"))).join(
        x_all[x_all.as_of == last25.as_of.max()].groupby("drug").agg(ratio_dec2025_all_ndcs=("ratio", "median"))).join(
        x_all[x_all.as_of == last26.as_of.max()].groupby("drug").agg(ratio_latest_all_ndcs=("ratio", "median")))
        .reset_index())
    return weekly, by_drug, last26.as_of.max(), last25.as_of.max()


def partd_per_claim(ira):
    """Gross Part D spending per claim, 2025 (full year) vs 2026 Q1, by drug family and group."""
    q = pd.read_csv(RAW / "partd" / "partd_spending_quarterly.csv", dtype=str)
    q = q[q.Mftr_Name == "Overall"].copy()
    for c in ("Tot_Clms", "Tot_Spndng"):
        q[c] = pd.to_numeric(q[c], errors="coerce")
    q["period"] = q.Year.map({"2025 (Q1-Q4)": "2025", "2026 (Q1)": "2026Q1"})
    q["B"] = q.Brnd_Name.str.upper().str.strip()

    # Brand names in the IRA file ("NOVOLOG; NOVOLOG FLEXPEN; ...") -> drug family.
    names = []
    for _, r in ira.drop_duplicates(["IPAY", "Selected Drug Name"]).iterrows():
        for nm in r["Selected Drug Name"].split(";"):
            names.append((nm.strip().upper(), r["drug"], "IPAY " + r["IPAY"]))
    names = pd.DataFrame(names, columns=["name", "drug", "group"]).sort_values("group").drop_duplicates("name")

    def family(b):
        if b.startswith(NOT_SELECTED):
            return (None, None)
        hits = names[(names.name == b) | names.name.map(lambda n: b.startswith(n + " "))]
        return (hits.iloc[0].drug, hits.iloc[0].group) if len(hits) else (None, None)

    # Active ingredients of every selected drug; unbranded or authorized-generic rows of these
    # ingredients are kept out of the comparator (their selected/unselected status is not resolvable
    # from drug-level rows).
    comps = []
    for ing in ira["Active Ingredient Name or Active Moiety Name"].dropna().str.upper().unique():
        ing = ing.replace(", HUMAN", "").replace("SACUBITRILAT", "SACUBITRIL")
        comps.append([c.strip() for c in ing.replace("/", ";").split(";") if c.strip()])

    comp_sets = [frozenset(cs) for cs in comps]

    def selected_ingredient(g):
        # Exact ingredient set (so combinations such as empagliflozin/metformin stay in the comparator,
        # and remibrutinib is not mistaken for ibrutinib).
        parts = frozenset(x.strip() for x in g.replace(";", "/").split("/") if x.strip())
        return parts in comp_sets

    fam = {b: family(b) for b in q.B.unique()}
    q["drug"] = q.B.map(lambda b: fam[b][0])
    q["group"] = q.B.map(lambda b: fam[b][1])
    # Other brands (name-based): brand string differs from the generic string, the brand's first word
    # is not part of the generic name (drops "Abacavir" vs "Abacavir Sulfate", "Alprazolam ER"),
    # not a supply, and not a selected ingredient.
    G = q.Gnrc_Name.str.upper().str.strip()
    first = q.B.str.extract(r"^([A-Z0-9]+)", expand=False).fillna("")
    first_in_generic = [f in g.replace("/", " ").replace(",", " ").replace("-", " ").split() for f, g in zip(first, G)]
    other = (q.drug.isna() & (q.B != G) & ~pd.Series(first_in_generic, index=q.index)
             & ~G.str.contains(SUPPLY, regex=True) & ~G.map(selected_ingredient))
    q.loc[other, "drug"] = q.loc[other, "Brnd_Name"]
    q.loc[other, "group"] = "Other brands"
    q = q.dropna(subset=["drug"])

    agg = q.groupby(["group", "drug", "period"])[["Tot_Clms", "Tot_Spndng"]].sum().unstack("period")
    agg.columns = [f"{a}_{b}" for a, b in agg.columns]
    agg = agg.reset_index()
    agg["per_claim_2025"] = agg.Tot_Spndng_2025 / agg.Tot_Clms_2025
    agg["per_claim_2026Q1"] = agg.Tot_Spndng_2026Q1 / agg.Tot_Clms_2026Q1
    agg["chg_per_claim"] = agg.per_claim_2026Q1 / agg.per_claim_2025 - 1
    agg["claims_2026Q1_x4_vs_2025"] = 4 * agg.Tot_Clms_2026Q1 / agg.Tot_Clms_2025 - 1
    # Keep drug families present in both periods with enough volume to be stable.
    keep = (agg.Tot_Clms_2025 >= 4000) & (agg.Tot_Clms_2026Q1 >= 1000)
    agg = agg[keep]
    grp = agg.groupby("group").apply(lambda g: pd.Series({
        "drug_families": len(g),
        "median_pct_change": g.chg_per_claim.median(),
        "p25": g.chg_per_claim.quantile(0.25), "p75": g.chg_per_claim.quantile(0.75),
        "pooled_pct_change": (g.Tot_Spndng_2026Q1.sum() / g.Tot_Clms_2026Q1.sum())
        / (g.Tot_Spndng_2025.sum() / g.Tot_Clms_2025.sum()) - 1,
        "share_falling_30pct_or_more": (g.chg_per_claim <= -0.30).mean(),
        # Fixed 2025 claim weights: within-drug price change without shifts in drug mix.
        "fixed_weight_pct_change": (g.Tot_Clms_2025 * g.per_claim_2026Q1).sum()
        / (g.Tot_Clms_2025 * g.per_claim_2025).sum() - 1,
    }), include_groups=False).reindex(GROUPS).reset_index()
    return agg, grp


def chart_ratio(weekly, path, mfp_start):
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ends = []
    for drug, g in weekly.groupby("drug"):
        g = g[g.ndcs > 0].sort_values("as_of")
        line, = ax.plot(g.as_of, g.median_ratio, lw=1.6)
        ends.append((g.median_ratio.iloc[-1], label(drug), line.get_color(), g.as_of.iloc[-1]))
    # Direct labels at the right end, nudged apart when lines finish close together.
    ends.sort()
    placed = []
    for y, name, color, x in ends:
        yy = max(y, placed[-1] + 0.09) if placed else y
        placed.append(yy)
        ax.annotate(name, (x, y), xytext=(x + pd.Timedelta(days=8), yy), fontsize=8.5, color=color, va="center")
    ax.set_xlim(right=weekly.as_of.max() + pd.Timedelta(days=75))
    ax.axhline(1, color="black", lw=1, ls="--")
    ax.axvline(mfp_start, color="grey", lw=0.8)
    ax.text(mfp_start, ax.get_ylim()[1], " MFP in effect", va="top", fontsize=9, color="grey")
    ax.set_ylabel("NADAC per unit / MFP per unit (median across brand NDCs)")
    ax.set_title("Average pharmacy acquisition cost relative to the negotiated price,\nMedicare's first ten negotiated drugs",
                 loc="left", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Source: CMS NADAC weekly files 2025–2026; CMS negotiation file (2026-09-21). 1.0 = NADAC equals "
             "the MFP in effect.\nBrand-classified retail NDCs; NovoLog and Fiasp share one CMS entry. "
             "No NADAC matched Imbruvica.", fontsize=7.5, color="grey")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def chart_partd(agg, grp, path):
    fig, ax = plt.subplots(figsize=(9, 6))
    sel = agg[agg.group.isin(["IPAY 2026", "IPAY 2027"])].sort_values(["group", "chg_per_claim"])
    oth = agg[agg.group == "Other brands"].chg_per_claim
    lo, hi = oth.quantile(0.25), oth.quantile(0.75)
    ax.axvspan(lo * 100, hi * 100, color="lightgrey", alpha=0.6, lw=0)
    ax.axvline(oth.median() * 100, color="grey", lw=1)
    colors = {"IPAY 2026": "#00B5B4", "IPAY 2027": "#1B2A4A"}
    ys = range(len(sel))
    ax.scatter(sel.chg_per_claim * 100, list(ys), c=sel.group.map(colors), s=28, zorder=3)
    ax.set_yticks(list(ys))
    ax.set_yticklabels(["NovoLog, Fiasp" if d == "NOVOLOG" else label(d) for d in sel.drug], fontsize=8)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Change in gross Part D spending per claim, 2025 to 2026 Q1 (%)")
    ax.set_title("Change in Part D gross spending per claim, negotiated drugs and comparison groups",
                 loc="left", fontsize=12)
    for g, c in colors.items():
        ax.scatter([], [], c=c, s=28, label=f"{g} (MFP from Jan {g[-4:]})")
    ax.fill_between([], [], color="lightgrey", label=f"Other brands, middle half (median {oth.median():+.0%})")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Source: CMS Quarterly Part D Spending by Drug (2025 Q1–Q4; 2026 Q1, preliminary). Gross spending, "
             "before manufacturer rebates.\nDrug families with 4,000+ claims in 2025 and 1,000+ in 2026 Q1. "
             "Linzess (2027 group) cut its list price in January 2026.", fontsize=7.5, color="grey")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def md(df, pct_cols=(), money_cols=(), ratio_cols=()):
    out = df.copy()
    for c in pct_cols:
        out[c] = out[c].map(lambda v: "" if pd.isna(v) else f"{v:+.1%}")
    for c in money_cols:
        out[c] = out[c].map(lambda v: "" if pd.isna(v) else f"${v:,.0f}")
    for c in ratio_cols:
        out[c] = out[c].map(lambda v: "" if pd.isna(v) else f"{v:.2f}")
    cols = list(out.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in out.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,}" if isinstance(v, int) else str(v)) for v in r) + " |")
    return "\n".join(lines)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ira, grp = load_ira()
    nadac = load_nadac([2024, 2025, 2026])

    jan, events = wac_january(nadac, grp)
    jan.to_csv(OUT / "wac_january_by_group.csv", index=False)
    events.to_csv(OUT / "wac_cut_events.csv", index=False)

    weekly, by_drug, last26, last25 = nadac_vs_mfp(nadac[nadac.as_of.dt.year >= 2025], ira)
    weekly.to_csv(OUT / "nadac_to_mfp_weekly.csv", index=False)
    by_drug.to_csv(OUT / "nadac_to_mfp_by_drug.csv", index=False)
    chart_ratio(weekly, OUT / "chart_nadac_vs_mfp.png", pd.Timestamp(2026, 1, 1))

    agg, pgrp = partd_per_claim(ira)
    agg.to_csv(OUT / "partd_per_claim_by_drug.csv", index=False)
    pgrp.to_csv(OUT / "partd_per_claim_by_group.csv", index=False)
    chart_partd(agg, pgrp, OUT / "chart_partd_per_claim.png")

    sel26 = agg[agg.group == "IPAY 2026"][["drug", "Tot_Clms_2025", "Tot_Clms_2026Q1", "per_claim_2025",
                                            "per_claim_2026Q1", "chg_per_claim", "claims_2026Q1_x4_vs_2025"]]
    ev26 = events[events.group.isin(["IPAY 2026", "IPAY 2027", "IPAY 2028"])]
    evo = (events[(events.group == "Other brands") & (events.january == 2026)]
           .groupby("products").agg(ndcs=("ndcs", "sum"), median_pct=("median_pct", "median"),
                                    effective=("effective", "min")).reset_index().sort_values("ndcs", ascending=False))
    fall_o = agg[(agg.group == "Other brands") & (agg.chg_per_claim <= -0.30)][["drug", "Tot_Clms_2025", "chg_per_claim"]]
    fall_o = fall_o.astype({"Tot_Clms_2025": int}).sort_values("chg_per_claim")
    jan_t = jan.assign(january=jan.january.astype(str), share_cut=jan.share_cut.map(lambda v: f"{v:.1%}"),
                       share_increase=jan.share_increase.map(lambda v: f"{v:.1%}"))
    text = [
        "# IRA negotiation and drug prices, January 2026: summary tables",
        "",
        "Generated by `pharma/scripts/ira_analysis.py`. Descriptive only; see `pharma/ira_findings.md` for interpretation.",
        "",
        f"## 1. Large WAC-related NADAC cuts early in the year, share of brand NDCs (cut of {abs(CUT):.0f}% or more, "
        "from NADAC Comparison rows whose primary reason mentions WAC; two effective-date windows)",
        "",
        md(jan_t),
        "",
        "Cuts on selected drugs (Dec 20 to Feb 28 window, all years):",
        "",
        md(ev26.assign(january=ev26.january.astype(str), median_pct=ev26.median_pct.map(lambda v: f"{v:.1f}%"))),
        "",
        "Cuts on other brands in 2026 (Dec 20 to Feb 28 window), by product:",
        "",
        md(evo.assign(median_pct=evo.median_pct.map(lambda v: f"{v:.1f}%"))),
        "",
        f"## 2. NADAC per unit relative to the 2026 MFP per unit (IPAY 2026 drugs; snapshots {last25.date()} and {last26.date()})",
        "",
        "Main columns: brand-classified NDCs, MFP in effect on the snapshot date. `_all_ndcs` columns add the unbranded"
        " and authorized-generic NDCs on the CMS list.",
        "",
        md(by_drug.astype({"ndcs_dec2025": "Int64", "ndcs_latest": "Int64"}),
           ratio_cols=["ratio_dec2025", "ratio_latest", "ratio_latest_same_ndcs", "ratio_dec2025_all_ndcs", "ratio_latest_all_ndcs"]),
        "",
        "## 3. Gross Part D spending per claim, 2025 vs 2026 Q1",
        "",
        md(pgrp.astype({"drug_families": int}).assign(share_falling_30pct_or_more=pgrp.share_falling_30pct_or_more.map(lambda v: f"{v:.0%}")),
           pct_cols=["median_pct_change", "p25", "p75", "pooled_pct_change", "fixed_weight_pct_change"]),
        "",
        "`pooled` lets the drug mix change; `fixed_weight` holds 2025 claim shares fixed (within-drug change only).",
        "",
        "Other brands falling 30% or more per claim:",
        "",
        md(fall_o, pct_cols=["chg_per_claim"]),
        "",
        "IPAY 2026 drug families:",
        "",
        md(sel26.astype({"Tot_Clms_2025": int, "Tot_Clms_2026Q1": int}), pct_cols=["chg_per_claim", "claims_2026Q1_x4_vs_2025"], money_cols=["per_claim_2025", "per_claim_2026Q1"]),
        "",
    ]
    (OUT / "summary.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()
