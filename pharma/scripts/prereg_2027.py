"""Pre-registered expectations for the 2027 negotiation cycle (written 2026-10-20, before any 2027 data).

Rule tested on the 2026 cohort: once the MFP binds, a drug's gross Part D spending per claim falls by
about 1/r - 1, where r is the plan unit price divided by the coming MFP in the last plan pricing file
before the MFP starts (finding 4's ratio). This script
  1. checks that rule on the ten 2026 drugs (Oct 2025 file ratio vs the measured 2025 -> 2026 Q1 change),
  2. applies it to the fifteen 2027 drugs (Oct 2026 file ratio) and to the group at fixed claim mix,
  3. records the pharmacy-side baseline (NADAC per unit / 2027 MFP per unit, and list-price cuts since 2024),
  4. records the baseline for the four drugs whose MFP ends on 2026-12-31 (Entresto, Stelara, Xarelto,
     NovoLog/Fiasp) and for the six that continue with inflation-adjusted 2027 MFPs.

Inputs: outputs of ira_analysis.py and spuf_mfp_check.py; data/raw/pharma (fetch_nadac.py, fetch_ira_inputs.py).
Outputs: pharma/outputs/prereg_2027/*.csv, baseline.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ira_analysis import CUT, load_ira, load_nadac  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "pharma"
OUTS = ROOT / "pharma" / "outputs"
OUT = OUTS / "prereg_2027"
LEAVING = ["ENTRESTO", "STELARA", "XARELTO", "NOVOLOG"]

# Gabriel et al. 2026, JMCP 32(5):530, Table 1: MFP discount off estimated 2022 US net price.
# CMS fact sheet (2025-11-25): MFP discount off 2024 list price. Pomalyst net price not estimable.
GABRIEL_OFF_NET = {"AUSTEDO": .15, "BREO ELLIPTA": .58, "CALQUENCE": .36, "IBRANCE": .35, "JANUMET": .43,
                   "LINZESS": .44, "OFEV": .40, "OTEZLA": .26, "OZEMPIC": .36, "POMALYST": np.nan,
                   "TRADJENTA": .60, "TRELEGY ELLIPTA": .43, "VRAYLAR": .23, "XIFAXAN": .54, "XTANDI": .26}
CMS_OFF_LIST_2024 = {"AUSTEDO": .38, "BREO ELLIPTA": .83, "CALQUENCE": .40, "IBRANCE": .50, "JANUMET": .85,
                     "LINZESS": .75, "OFEV": .50, "OTEZLA": .65, "OZEMPIC": .71, "POMALYST": .60,
                     "TRADJENTA": .84, "TRELEGY ELLIPTA": .73, "VRAYLAR": .44, "XIFAXAN": .63, "XTANDI": .48}


def spuf_ratios():
    r = pd.read_csv(OUTS / "spuf" / "ratio_by_drug.csv")
    r = r.pivot_table(index=["IPAY", "drug"], columns="snapshot", values="median_ratio").reset_index()
    r.columns.name = None
    return r.rename(columns={"2025 (Oct 2025 release)": "r_oct2025", "2026 (Jan 2026 release)": "r_jan2026",
                             "2026 (Oct 2026 release)": "r_oct2026"})


def calibration(pc, r):
    c = r[r.IPAY == 2026][["drug", "r_oct2025"]].merge(
        pc[pc.group == "IPAY 2026"][["drug", "Tot_Clms_2025", "per_claim_2025", "per_claim_2026Q1", "chg_per_claim"]],
        on="drug")
    c["predicted"] = 1 / c.r_oct2025 - 1
    c["error_pp"] = 100 * (c.chg_per_claim - c.predicted)
    # Structural cases: Entresto lost most claims to generics in 2026 (claims -86%); the CMS NovoLog
    # entry pools NovoLog (cut in 2024) and Fiasp, whose plan-file ratios differ.
    c["structural"] = c.drug.isin(["ENTRESTO", "NOVOLOG"])
    return c


def fixed_mix(df, w, old, new):
    return (df[w] * df[new]).sum() / (df[w] * df[old]).sum() - 1


def nadac_2027(ira, nadac):
    m = ira[(ira.IPAY == "2027")].dropna(subset=["mfp_unit"])[["ndc11", "drug", "mfp_unit"]].drop_duplicates("ndc11")
    x = nadac.merge(m, left_on="NDC", right_on="ndc11")
    x = x[x["Classification for Rate Setting"].str.startswith("B")]
    last = x[x.as_of == x.as_of.max()].copy()
    last["ratio"] = last.nadac / last.mfp_unit
    out = last.groupby("drug").agg(nadac_ndcs=("NDC", "nunique"), nadac_to_mfp2027=("ratio", "median"))
    # Large WAC-based list-price cuts on these NDCs since 2024 (NADAC Comparison file).
    comp = pd.read_csv(RAW / "nadac" / "nadac_comparison.csv", dtype=str)
    comp["eff"] = pd.to_datetime(comp["Effective Date"], format="%m/%d/%Y")
    comp["pct"] = pd.to_numeric(comp["Percent Change"])
    w = comp[comp["Primary Reason"].str.contains("WAC", na=False) & (comp.pct <= CUT)].merge(m, left_on="NDC", right_on="ndc11")
    cuts = (w.groupby("drug").agg(cut_dates=("eff", lambda s: ", ".join(sorted({d.date().isoformat() for d in s}))),
                                  median_cut_pct=("pct", "median")))
    return out.join(cuts), x.as_of.max()


def leaving_and_continuing(ira, r, pc):
    d = ira.copy()
    d["start"] = pd.to_datetime(d["MFP Effective Date"], format="%m/%d/%Y")
    d["end"] = pd.to_datetime(d["MFP End Date"], format="%m/%d/%Y")
    m26 = d[(d.IPAY == "2026") & (d.start.dt.year == 2026) & ~(d.end < d.start)]
    # 2027 rows of deselected NDCs carry an end date before their start (superseded); drop them.
    m27 = d[(d.IPAY == "2026") & (d.start.dt.year == 2027) & ~(d.end < d.start)]
    a = m26.sort_values("start").groupby("drug").mfp_30.last().rename("mfp30_2026")
    b = m27.groupby("drug").mfp_30.first().rename("mfp30_2027")
    ends = m26.groupby("drug").end.max().dt.date.rename("mfp_2026_end")
    t = pd.concat([a, b, ends], axis=1).reset_index()
    t["status_2027"] = np.where(t.drug.isin(LEAVING), "leaves (MFP ends 2026-12-31)", "continues")
    t["mfp30_change"] = t.mfp30_2027 / t.mfp30_2026 - 1
    t = t.merge(r[r.IPAY == 2026][["drug", "r_oct2025", "r_oct2026"]], on="drug", how="left")
    t = t.merge(pc[pc.group == "IPAY 2026"][["drug", "per_claim_2025", "per_claim_2026Q1"]], on="drug", how="left")
    nd = pd.read_csv(OUTS / "ira" / "nadac_to_mfp_by_drug.csv")[["drug", "ratio_dec2025", "ratio_latest"]]
    nd = nd.rename(columns={"ratio_dec2025": "nadac_to_mfp_dec2025", "ratio_latest": "nadac_to_mfp_latest"})
    # The NADAC table splits the CMS NovoLog entry into NovoLog and Fiasp; keep both rows (Agy review fix).
    fiasp = t[t.drug == "NOVOLOG"].assign(drug="FIASP")
    t = pd.concat([t, fiasp], ignore_index=True).merge(nd, on="drug", how="left")
    # Leaving drugs: if plan prices return to the list-based level, the brand's plan price moves from the
    # 2026 MFP to roughly NADAC (which tracks WAC for brands): expected per-unit factor = NADAC / 2026 MFP.
    t["factor_if_list_returns"] = np.where(t.status_2027.str.startswith("leaves"), t.nadac_to_mfp_latest, np.nan)
    return t


def md(df, pct=(), ratio=(), money=()):
    df = df.copy()
    for c in pct:
        df[c] = df[c].map(lambda v: "" if pd.isna(v) else f"{v:+.0%}" if c.startswith(("pred", "chg", "real", "mfp30_ch"))
                          else f"{v:.0%}")
    for c in ratio:
        df[c] = df[c].map(lambda v: "" if pd.isna(v) else f"{v:.2f}")
    for c in money:
        df[c] = df[c].map(lambda v: "" if pd.isna(v) else f"{v:,.2f}" if c.startswith("mfp30") else f"{v:,.0f}")
    df = df.fillna("")
    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(str(v) for v in row) + " |" for row in df.values)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pc = pd.read_csv(OUTS / "ira" / "partd_per_claim_by_drug.csv")
    r = spuf_ratios()
    ira, _ = load_ira()

    # 1. Calibration on the 2026 cohort.
    c = calibration(pc, r)
    c.to_csv(OUT / "calibration_2026.csv", index=False)
    clean = c[~c.structural]
    max_err = clean.error_pp.abs().max()
    fm_real = fixed_mix(c, "Tot_Clms_2025", "per_claim_2025", "per_claim_2026Q1")
    c["pc_pred"] = c.per_claim_2025 * (1 + c.predicted)
    fm_pred = fixed_mix(c, "Tot_Clms_2025", "per_claim_2025", "pc_pred")

    # 2. Predictions for the 2027 cohort.
    p = r[r.IPAY == 2027][["drug", "r_oct2025", "r_jan2026", "r_oct2026"]].merge(
        pc[pc.group == "IPAY 2027"][["drug", "Tot_Clms_2026Q1", "Tot_Spndng_2026Q1", "per_claim_2026Q1", "chg_per_claim"]],
        on="drug")
    p["predicted"] = 1 / p.r_oct2026 - 1
    p["pc_2027Q1_pred"] = p.per_claim_2026Q1 * (1 + p.predicted)
    p["gabriel_off_net"] = p.drug.map(GABRIEL_OFF_NET)
    p["cms_off_list_2024"] = p.drug.map(CMS_OFF_LIST_2024)
    nd, nadac_date = nadac_2027(ira, load_nadac([2026]))
    p = p.merge(nd.reset_index(), on="drug", how="left")
    p = p.sort_values("predicted")
    p.to_csv(OUT / "predictions_2027.csv", index=False)
    fm27 = fixed_mix(p, "Tot_Clms_2026Q1", "per_claim_2026Q1", "pc_2027Q1_pred")
    gross_q = (p.Tot_Spndng_2026Q1 * -p.predicted).sum()

    # 3. Drugs leaving and continuing.
    t = leaving_and_continuing(ira, r, pc)
    t.to_csv(OUT / "ipay2026_in_2027.csv", index=False)

    lines = [
        "# Baseline numbers for the 2027 pre-registration",
        "",
        f"Generated by `pharma/scripts/prereg_2027.py` on data available 2026-10-20 (NADAC to {nadac_date.date()}). "
        "The expectations themselves are in `pharma/prereg_2027.md`.",
        "",
        "## 1. Calibration: the rule on the 2026 drugs",
        "",
        "Predicted change = 1/r - 1 with r = median plan unit price / 2026 MFP in the October 2025 plan pricing file; "
        "realized = gross Part D spending per claim, 2025 vs 2026 Q1.",
        "",
        md(c[["drug", "r_oct2025", "predicted", "chg_per_claim", "error_pp", "structural"]]
           .rename(columns={"chg_per_claim": "realized"}).round({"error_pp": 1}),
           pct=["predicted", "realized"], ratio=["r_oct2025"]),
        "",
        f"Largest absolute error outside the two structural cases: {max_err:.1f} points "
        f"(mean {clean.error_pp.mean():+.1f}). Fixed 2025 mix, all ten: predicted {fm_pred:+.1%}, realized {fm_real:+.1%}.",
        "",
        "## 2. The fifteen 2027 drugs",
        "",
        md(p[["drug", "r_oct2026", "predicted", "per_claim_2026Q1", "pc_2027Q1_pred", "chg_per_claim",
              "nadac_to_mfp2027", "cut_dates", "gabriel_off_net", "cms_off_list_2024"]]
           .rename(columns={"chg_per_claim": "chg_2025_to_2026Q1"}),
           pct=["predicted", "chg_2025_to_2026Q1", "gabriel_off_net", "cms_off_list_2024"],
           ratio=["r_oct2026", "nadac_to_mfp2027"], money=["per_claim_2026Q1", "pc_2027Q1_pred"]),
        "",
        f"Group at fixed 2026 Q1 claim mix: predicted change in gross spending per claim {fm27:+.1%}. "
        f"Gross Part D spending removed at 2026 Q1 volumes: ${gross_q / 1e9:.2f} billion a quarter "
        f"(2026 Q1 gross spending on the fifteen: ${p.Tot_Spndng_2026Q1.sum() / 1e9:.2f} billion).",
        "",
        f"Median NADAC / 2027 MFP (brand NDCs, {nadac_date.date()}): {p.nadac_to_mfp2027.median():.2f}; "
        f"median plan-file ratio (October 2026): {p.r_oct2026.median():.2f}.",
        "",
        "## 3. The ten 2026 drugs in 2027",
        "",
        md(t[["drug", "status_2027", "mfp30_2026", "mfp30_2027", "mfp30_change", "r_oct2025", "r_oct2026",
              "nadac_to_mfp_dec2025", "nadac_to_mfp_latest", "factor_if_list_returns", "per_claim_2025", "per_claim_2026Q1"]],
           pct=["mfp30_change"], ratio=["r_oct2025", "r_oct2026", "nadac_to_mfp_dec2025", "nadac_to_mfp_latest",
                                        "factor_if_list_returns"],
           money=["mfp30_2026", "mfp30_2027", "per_claim_2025", "per_claim_2026Q1"]),
        "",
    ]
    (OUT / "baseline.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
