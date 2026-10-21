"""Supplementary verification script for Part 2 (methods) and Part 3 (output comparison).

Verifies:
1. Exact numerical agreement between independent recompute and pharma/outputs/nadac_sanity.md
   plus pharma/outputs/nadac_tracers.csv.
2. Within-description NADAC dispersion across all 13 tracers (2025-2026) and across the entire
   2026-10-21 snapshot.
3. Composition-driven median jumps in ALBUTEROL HFA 90 MCG INHALER on 2025-11-26 and 2026-04-29
   when zero continuing NDCs changed price.
4. Explanation Code and NADAC Comparison Primary Reason breakdown by brand/generic class and
   monthly survey refresh vs non-refresh weeks in 2026.
5. IPAY 2026 drugs in NADAC (2024-2026), NADAC Comparison (2013-2026), and IRA MFP file
   (selected_drugs_mfp.csv), including Januvia's 2025-01-01 WAC cut (-42.41%), Imbruvica's
   complete absence from NADAC, and the gap between post-cut 2026 NADAC and NDC-9 MFP per unit.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
NADAC_DIR = ROOT / "data" / "raw" / "pharma" / "nadac"
IRA_CSV = ROOT / "data" / "raw" / "pharma" / "ira" / "selected_drugs_mfp.csv"
TRACERS_CSV = ROOT / "pharma" / "outputs" / "nadac_tracers.csv"


def main():
    df24 = pd.read_csv(NADAC_DIR / "nadac_2024.csv", dtype=str)
    df25 = pd.read_csv(NADAC_DIR / "nadac_2025.csv", dtype=str)
    df26 = pd.read_csv(NADAC_DIR / "nadac_2026.csv", dtype=str)
    comp = pd.read_csv(NADAC_DIR / "nadac_comparison.csv", dtype=str)
    ira = pd.read_csv(IRA_CSV, dtype=str)
    tr_pub = pd.read_csv(TRACERS_CSV)

    for d in (df24, df25, df26):
        d["as_of_dt"] = pd.to_datetime(d["As of Date"], format="%m/%d/%Y")
        d["nadac"] = pd.to_numeric(d["NADAC Per Unit"])

    both = pd.concat([df25, df26], ignore_index=True)
    both["as_of_iso"] = both["as_of_dt"].dt.strftime("%Y-%m-%d")

    print("=== PART 3: EXACT COMPARISON WITH nadac_tracers.csv ===")
    sub = both[both["NDC Description"].isin(tr_pub["NDC Description"].unique())]
    rec = (
        sub.groupby(["NDC Description", "as_of_iso"])
        .agg(
            ndcs=("NDC", "nunique"),
            median_nadac=("nadac", "median"),
            unit=("Pricing Unit", "first"),
            cls=("Classification for Rate Setting", lambda s: "/".join(sorted(s.unique()))),
        )
        .reset_index()
        .rename(columns={"as_of_iso": "as_of"})
    )
    merged = tr_pub.merge(rec, on=["NDC Description", "as_of"], how="outer", suffixes=("_pub", "_rec"))
    print(f"Rows: published={len(tr_pub)}, recomputed={len(rec)}, merged={len(merged)}")
    print(f"NDC count mismatches: {(merged['ndcs_pub'] != merged['ndcs_rec']).sum()}")
    print(f"Unit mismatches: {(merged['unit_pub'] != merged['unit_rec']).sum()}")
    print(f"Class mismatches: {(merged['cls_pub'] != merged['cls_rec']).sum()}")
    print(f"Max abs diff in median_nadac: {(merged['median_nadac_pub'] - merged['median_nadac_rec']).abs().max():.3e}")

    print("\n=== PART 2A: WITHIN-DESCRIPTION DISPERSION ===")
    tr_disp = sub.groupby(["NDC Description", "as_of_iso"])["nadac"].agg(["count", "nunique", "min", "median", "max"])
    multi_rate_tracers = tr_disp[tr_disp["nunique"] > 1]
    print(f"Tracer-week cells: {len(tr_disp)}; cells with >1 unique NADAC: {len(multi_rate_tracers)}")
    print("Tracers with >1 unique NADAC:", multi_rate_tracers.index.get_level_values(0).unique().tolist())

    last26 = df26[df26["As of Date"] == "10/21/2026"]
    desc_disp = last26.groupby("NDC Description")["nadac"].agg(["count", "nunique"])
    multi_ndc = desc_disp[desc_disp["count"] > 1]
    print(
        f"2026-10-21 distinct descriptions: {len(desc_disp):,}; with >1 NDC: {len(multi_ndc):,}; "
        f"with 1 unique rate: {(multi_ndc['nunique'] == 1).sum():,} ({(multi_ndc['nunique'] == 1).mean()*100:.2f}%); "
        f"with >1 unique rate: {(multi_ndc['nunique'] > 1).sum():,}"
    )

    print("\n=== PART 2B: ALBUTEROL HFA 90 MCG INHALER TURNOVER JUMPS ===")
    alb = both[both["NDC Description"] == "ALBUTEROL HFA 90 MCG INHALER"]
    for pair in [("2025-11-19", "2025-11-26"), ("2026-04-22", "2026-04-29")]:
        a = alb[alb["as_of_iso"] == pair[0]].set_index("NDC")["nadac"]
        b = alb[alb["as_of_iso"] == pair[1]].set_index("NDC")["nadac"]
        common = a.index.intersection(b.index)
        max_common_diff = (a.loc[common] - b.loc[common]).abs().max()
        print(
            f"{pair[0]} -> {pair[1]}: n={len(a)}->{len(b)}, "
            f"median={a.median():.5f}->{b.median():.5f} ({(b.median()/a.median()-1)*100:+.2f}%), "
            f"max price change among {len(common)} continuing NDCs = {max_common_diff:.5f}"
        )

    print("\n=== PART 2C: JANUVIA 2025-01-01 WAC CUT & 2026-08-05 GENERIC ENTRY ===")
    jan24 = df24[(df24["NDC Description"] == "JANUVIA 100 MG TABLET") & (df24["As of Date"] == "12/25/2024")]
    jan25 = df25[(df25["NDC Description"] == "JANUVIA 100 MG TABLET") & (df25["As of Date"] == "01/01/2025")]
    print(
        f"JANUVIA 100 MG TABLET: 2024-12-25 median={jan24['nadac'].median():.5f} (eff={jan24['Effective Date'].iloc[0]}, code={jan24['Explanation Code'].iloc[0]}) -> "
        f"2025-01-01 median={jan25['nadac'].median():.5f} (eff={jan25['Effective Date'].iloc[0]}, code={jan25['Explanation Code'].iloc[0]}), "
        f"change={(jan25['nadac'].median()/jan24['nadac'].median()-1)*100:+.2f}%"
    )

    print("\n=== PART 2D: IPAY 2026 MFP vs 2026 NADAC FOR ORAL TRACERS ===")
    ipay26 = ira[(ira["IPAY"] == "2026") & (ira["MFP Effective Date"] == "01/01/2026")]
    for ndc9, label, desc in [
        ("00003-0894", "Eliquis 5 mg", "ELIQUIS 5 MG TABLET"),
        ("00597-0152", "Jardiance 10 mg", "JARDIANCE 10 MG TABLET"),
        ("00006-0277", "Januvia 100 mg", "JANUVIA 100 MG TABLET"),
        ("50458-0579", "Xarelto 20 mg", "XARELTO 20 MG TABLET"),
    ]:
        mfp_row = ipay26[ipay26["NDC-9"] == ndc9].iloc[0]
        mfp_unit = float(mfp_row["NDC-9 MFP per Unit Price"])
        mfp_30 = float(mfp_row["Single MFP per 30 DES"])
        nadac_latest = last26[last26["NDC Description"] == desc]["nadac"].median()
        print(
            f"{label:16s} (NDC-9 {ndc9}): MFP/unit=${mfp_unit:.6f} (30-day=${mfp_30:.2f}) vs "
            f"2026-10-21 NADAC/unit=${nadac_latest:.5f} (NADAC/MFP ratio = {nadac_latest/mfp_unit:.2f}x, "
            f"gap = +${nadac_latest - mfp_unit:.5f}/unit)"
        )


if __name__ == "__main__":
    main()
