"""Build the project report: one self-contained HTML page (pharma/report/index.html).

Reads only reviewed outputs (pharma/outputs/ira, spuf, prereg_2027) and the template
pharma/report/template.html; embeds the chart data as JSON. Rerun after any analysis update.
"""
import json
import subprocess
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTS = ROOT / "pharma" / "outputs"
REPORT = ROOT / "pharma" / "report"

# Review verdicts per piece (reports in reviews/). Update when a review lands.
REVIEWS = [
    ("Source catalog and NADAC starter numbers", "PASS WITH FIXES", "PASS WITH FIXES"),
    ("Findings 1 to 3 (Part D, list prices, NADAC)", "PASS WITH FIXES, follow-up confirmed 8,542 comparisons", "PASS WITH FIXES"),
    ("Finding 4 (1.5 million plan-price rows)", "PASS WITH FIXES", "PASS WITH FIXES"),
    ("Literature review and full-text round", "PASS WITH FIXES (two rounds)", "not run"),
    ("Plain-language explainer", "fact-checked, fixes applied", "not run"),
    ("2027 pre-registration baseline", "__CODEX_PREREG__", "__AGY_PREREG__"),
    ("This page", "PASS WITH FIXES; 2,491 embedded values matched; 14 wording fixes applied", "not run"),
]


def pct(v, d=0):
    s = f"{abs(v) * 100:.{d}f}%"
    return ("+" if v > 0 else "−" if v < 0 else "") + s


CODEX_PREREG = "PASS WITH FIXES (221 numbers reproduced)"
AGY_PREREG = "PASS WITH FIXES; 6 findings held up, 5 claims did not (wrong source values)"


def main():
    note = REPORT / "prereg_note.html"  # hand-written summary of the registration amendments
    amendments_html = note.read_text() if note.exists() else ""
    codex_prereg, agy_prereg = CODEX_PREREG, AGY_PREREG
    pc = pd.read_csv(OUTS / "ira" / "partd_per_claim_by_drug.csv")
    f1 = pc[pc.group.isin(["IPAY 2026", "IPAY 2027"])]
    f1 = [dict(drug=r.drug, group=r.group, pc2025=r.per_claim_2025, pc2026=r.per_claim_2026Q1,
               chg=r.chg_per_claim, claims2025=r.Tot_Clms_2025) for r in f1.itertuples()]
    g = pd.read_csv(OUTS / "ira" / "partd_per_claim_by_group.csv")
    groups = [dict(group=r.group, n=int(r.drug_families), median=r.median_pct_change, p25=r.p25, p75=r.p75,
                   fixed=r.fixed_weight_pct_change, share30=r.share_falling_30pct_or_more) for r in g.itertuples()]
    gfix = dict(zip(g.group, g.fixed_weight_pct_change))
    ten = pc[pc.group == "IPAY 2026"].chg_per_claim

    wj = pd.read_csv(OUTS / "ira" / "wac_january_by_group.csv")
    f2 = [dict(january=int(r.january), window=r.window, group=r.group, n=int(r.brand_ndcs),
               cut=int(r.ndcs_with_wac_cut_ge_20pct), share=r.share_cut, inc=r.share_increase) for r in wj.itertuples()]
    ev = pd.read_csv(OUTS / "ira" / "wac_cut_events.csv")
    cuts = ev[ev.group.str.startswith("IPAY")].to_dict("records")

    wk = pd.read_csv(OUTS / "ira" / "nadac_to_mfp_weekly.csv")
    f3 = [dict(drug=r.drug, date=r.as_of, ratio=round(r.median_ratio, 4), ndcs=int(r.ndcs)) for r in wk.itertuples()]

    rd = pd.read_csv(OUTS / "spuf" / "ratio_by_drug.csv")
    f4 = [dict(IPAY=str(r.IPAY), drug=r.drug, snapshot=r.snapshot, ratio=r.median_ratio, at=r.share_at_mfp)
          for r in rd.itertuples()]
    rg = pd.read_csv(OUTS / "spuf" / "ratio_by_group.csv")
    sw = pd.read_csv(OUTS / "spuf" / "sensitivity_weights_panel.csv").set_index("snapshot").claims_2025
    rg26 = rg[rg.IPAY == 2026]
    f4g = [dict(snapshot=r.snapshot, rows=r.plan_ndc_rows, median=r.median_ratio, at=r.share_at_mfp,
                below=r.share_below_mfp, above=r.share_above_mfp, weighted=sw.get(r.snapshot)) for r in rg26.itertuples()]
    jan = rg26[rg26.snapshot.str.contains("Jan 2026")].iloc[0]

    cal = pd.read_csv(OUTS / "prereg_2027" / "calibration_2026.csv")
    cal_rows = [dict(drug=r.drug, r=r.r_oct2025, pred=r.predicted, real=r.chg_per_claim, err=r.error_pp,
                     structural=bool(r.structural)) for r in cal.itertuples()]
    w = cal.Tot_Clms_2025
    fm_real = (w * cal.per_claim_2026Q1).sum() / (w * cal.per_claim_2025).sum() - 1
    fm_pred = (w * cal.per_claim_2025 * (1 + cal.predicted)).sum() / (w * cal.per_claim_2025).sum() - 1
    pr = pd.read_csv(OUTS / "prereg_2027" / "predictions_2027.csv")
    nz = lambda v: None if pd.isna(v) else float(v)
    pred = [dict(drug=r.drug, r=r.r_oct2026, pred=r.predicted, pc=r.per_claim_2026Q1, nadac=nz(r.nadac_to_mfp2027),
                 gab=nz(r.gabriel_off_net), cms=r.cms_off_list_2024) for r in pr.itertuples()]
    fm27 = (pr.Tot_Clms_2026Q1 * pr.pc_2027Q1_pred).sum() / (pr.Tot_Clms_2026Q1 * pr.per_claim_2026Q1).sum() - 1
    grossq = (pr.Tot_Spndng_2026Q1 * -pr.predicted).sum()
    sema = pr.loc[pr.drug == "OZEMPIC", "Tot_Spndng_2026Q1"].sum() / pr.Tot_Spndng_2026Q1.sum()

    commit = subprocess.run(["git", "log", "--format=%h", "-1", "--", "pharma/prereg_2027.md"], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()
    first = subprocess.run(["git", "log", "--format=%h", "--diff-filter=A", "--", "pharma/prereg_2027.md"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip().splitlines()
    reg_commit = first[-1] if first else commit

    data = dict(f1=f1, groups=groups, f2=f2, cuts=cuts, f3=f3, f4=f4, f4g=f4g, cal=cal_rows, pred=pred)
    rows = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td></tr>" for a, b, c in REVIEWS)
    rows = rows.replace("__CODEX_PREREG__", escape(codex_prereg)).replace("__AGY_PREREG__", escape(agy_prereg))
    sub = {
        "__UPDATED__": date.today().isoformat(),
        "__F1_MEDIAN__": pct(ten.median()), "__F1_MIN__": pct(ten.max()), "__F1_MAX__": pct(ten.min()),
        "__G26__": pct(gfix["IPAY 2026"]), "__G27__": pct(gfix["IPAY 2027"], 1), "__G28__": pct(gfix["IPAY 2028"], 1),
        "__GOTH__": pct(gfix["Other brands"], 1),
        "__F4_JAN__": f"{jan.share_at_mfp * 100:.1f}%", "__F4_W__": f"{sw[jan.snapshot] * 100:.1f}%",
        "__PREREG_COMMIT__": reg_commit,
        "__CAL_MAE__": f"{cal.error_pp.abs().mean():.1f}", "__CAL_FMP__": pct(fm_pred, 1), "__CAL_FMR__": pct(fm_real, 1),
        "__G27_PRED__": pct(fm27, 1), "__GROSSQ__": f"${grossq / 1e9:.1f} billion", "__SEMA_SHARE__": f"{sema * 100:.0f}%",
        "__REVIEW_ROWS__": rows, "__AMEND_HTML__": amendments_html,
    }
    html = (REPORT / "template.html").read_text()
    for k, v in sub.items():
        html = html.replace(k, v)
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"), default=float))
    left = [t for t in sub if t in html]
    assert not left, left
    (REPORT / "index.html").write_text(html)
    print(f"wrote {REPORT / 'index.html'} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
