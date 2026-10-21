# Pharma track: notes for assistants

US public pharmaceutical data (pricing, utilization, spending, access) for Johnattan's US job-search portfolio. Started 2026-10-20 in a side session (branch `claude/pharma-data-eae972`, merged into master the same day). All work lives in `pharma/`, `literature/ira_*`, `data/raw/pharma/` (git-ignored) and `reviews/pharma_*`; it never touches the atlas files.

## ⏯ Resume here (2026-10-20, evening)

**State:** catalog, IRA study (four findings), literature review, explainer and voice notes are done and merged into master (`f240037`). Added on branch `claude/pharma-data-eae972` (not yet merged into master; the main checkout's master may be in use by the atlas session):
- **2027 pre-registration** `prereg_2027.md`, registered in commit `b24d4c8` before any 2027 outcome data existed; Amendments 1 (Codex) and 2 (Agy) fix the scoring contract without changing any registered number. Baseline: `scripts/prereg_2027.py` -> `outputs/prereg_2027/`.
- **Project report** `report/index.html`: one self-contained interactive page (findings, charts, context, predictions, verification). Built by `scripts/build_report.py` from `report/template.html` + `report/prereg_note.html`; rebuild after any change. Codex fact-checked it (PASS WITH FIXES, all 14 fixes applied).

**Next action:** merge this branch into master when the main checkout is free. Then score P1 and P4 on the first quarterly plan pricing release with plan-year 2027 prices (expected January 2027; the monthly CY2027 series posted 2026-10-08 has no pricing table); P3 from NADAC January to June 2027; P2, P4 spending and P5 when 2027 Q1 Part D quarterly spending appears (about July 2027). Score each clause as pass, fail or not evaluable exactly as Amendments 1 and 2 define.

**Do not:** open any plan-year 2027 pricing data before scoring is set up exactly as registered; edit a registered number (new decisions go in a dated amendment).

**Open items:** EPIC Act status (congress.gov bot check; Johnattan's browser); BRG effectuation report (dead link); Merck D.D.C. and Fifth Circuit PhRMA opinions (advocacy summaries only); idea 1 (US vs LAC prices) parked; optional Agy review of the literature review and explainer.

**Reviewer note (Johnattan, 2026-10-20):** weigh Argon less than Astra or Opus. In the pre-registration review Agy got the data replication right but listed wrong Gabriel values, cited a nonexistent band and file, and invented Li et al. figures; verify every Argon claim before use.

## Files

| Path | What |
|---|---|
| `README.md` | Source catalog (checked live 2026-10-20), pitfalls, project ideas |
| `ira_findings.md` | The IRA study: four findings, limits, literature context |
| `explainer_medicare_drug_pricing.md` | Plain-language guide: supply chain, prices and rebates, negotiation rules and timeline, who gains from list-price cuts, PBMs, every paper summarized |
| `scripts/fetch_nadac.py`, `summarize_nadac.py` | NADAC weekly files and sanity summary |
| `scripts/fetch_ira_inputs.py`, `ira_analysis.py` | CMS MFP file, Part D quarterly/annual spending; findings 1–3 |
| `scripts/fetch_spuf.py`, `spuf_mfp_check.py` | Plan pricing files (SPUF); finding 4 |
| `outputs/` | Summaries, CSVs, charts (`outputs/ira/`, `outputs/spuf/`) |
| `prereg_2027.md`, `scripts/prereg_2027.py` | 2027 pre-registration and its baseline (`outputs/prereg_2027/`) |
| `report/index.html`, `scripts/build_report.py` | Project report, one interactive HTML page |
| `voice_note/` | Scripts of the two voice notes (audio git-ignored) |
| `../literature/ira_negotiation_literature_review.md` | Literature and grey-literature review; notes in `../literature/ira_notes/`, wishlist with Harvard LibKey links |
| `../literature/ira_fulltext/MANIFEST.md` | 18 papers + 5 grey documents read in full (PDFs and text git-ignored) |

## Findings (one line each)

1. Gross Part D spending per claim, 2025 vs 2026 Q1: median −64% for the ten drugs (all ≥30% down); comparison groups about +1% at fixed mix. Gross, not net (rebates were ~45%; Jeon et al. project ~9% net).
2. List-price (WAC) cuts on 2026-01-01: Eliquis −43%, Jardiance −44%, Farxiga −37%, Fiasp −75%; Imbruvica 2025-12-22; Januvia 2025-01-01; related non-selected brands cut the same day.
3. NADAC stays 2.2–3.6x the MFP for Januvia, Xarelto, Entresto, Stelara, Enbrel; a benchmark gap, not a measured receivable.
4. Reported plan prices (SPUF) at the MFP from January 2026: median 2.77x MFP in 2025, 1.000 in 2026; 92.7%/91.3% within 0.5% (99.7%/99.5% claim-weighted); none above by October.

## Decisions and data facts (do not relitigate)

- Gross vs net: never infer net savings from rebate shares; cite Jeon et al. and CMS estimates as projections on their own baselines.
- MFP ceiling: at least 25% off non-FAMP, at least 60% for drugs 16+ years past approval (or the net price if lower). Plan payment is capped at MFP plus dispensing fees.
- Medicare inflation penalties (BMS on Eliquis) and the Medicaid-linked 340B ceiling are separate mechanisms.
- SPUF release labels: `SPUF_2026_20260107` is labeled PPUF_2025Q4 but holds plan-year 2026 prices; `SPUF_2025_20251009` (PPUF_2025Q3) is the pre-MFP baseline. Each release is ~2.5 GB; keep only pricing/plan tables.
- CMS MFP file: drop rows whose end date precedes their start (superseded); Entresto Sprinkle MFP corrected from 2026-06-01; NovoLog Mix is not on the list.
- NADAC Comparison file records why a rate changed (WAC adjustment vs survey); brand NADAC follows WAC changes.
- Part D quarterly file: no dosage units; "Other brands" comparator is name-based (hyphenated generics and supplies excluded).
- Disk filled to zero once on 2026-10-20 (space used outside this repo); check `df -h` before large downloads.
