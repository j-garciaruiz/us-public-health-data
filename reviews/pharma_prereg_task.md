# Review brief: pre-registered 2027 expectations for Medicare drug price negotiation (2026-10-20)

Independent check of a pre-registration. Work only in your own folder: Codex in `reviews/pharma_prereg_codex_astra/`, Agy in `reviews/pharma_prereg_agy_argon/`. No em dashes. Do not commit. Do not accept website terms or log in. Python: `.venv/bin/python` (pandas available); keep your code in your folder.

**Hard rule:** do NOT download, open or query any 2027 plan pricing data (the CMS monthly Prescription Drug Plan Formulary, Pharmacy Network and Pricing release for contract year 2027, posted 2026-10-08, or any later file). Those files are the out-of-sample test of the predictions; looking at them would spoil it. Also do not download any other new data; everything needed is local.

## Order matters
Do Part A with your own code and save `replication.md` in your folder BEFORE opening `pharma/scripts/prereg_2027.py`, `pharma/outputs/prereg_2027/`, `pharma/scripts/ira_analysis.py`, `pharma/scripts/spuf_mfp_check.py` or anything in `pharma/outputs/`.

## Data (all local)
- `data/raw/pharma/spuf/<label>/pricing file PPUF_<label>.zip`: CMS quarterly plan pricing files, pricing table pipe-delimited (CONTRACT_ID, PLAN_ID, SEGMENT_ID, NDC, DAYS_SUPPLY, UNIT_COST). Label `2025Q3` = release of 2025-10-09, plan year 2025 prices. Label `2026Q3` = release of 2026-10-07, plan year 2026 prices. (`2025Q4` = release of 2026-01-07, already plan year 2026.)
- `data/raw/pharma/ira/selected_drugs_mfp.csv`: CMS selected drugs and Maximum Fair Prices (IPAY 2026, 2027, 2028; NDC-11 dashed; "NDC-9 MFP per Unit Price"; "Single MFP per 30 DES"; effective and end dates; rows whose end date precedes their start are superseded).
- `data/raw/pharma/partd/partd_spending_quarterly.csv`: Medicare Quarterly Part D Spending by Drug (use `Mftr_Name == "Overall"` rows; Year values "2025 (Q1-Q4)" and "2026 (Q1)").
- `data/raw/pharma/nadac/nadac_2026.csv`, `nadac_comparison.csv`: NADAC weekly rates and the comparison file with the reason for each change.
- Sources for the benchmark numbers: `literature/ira_fulltext/text/paper_9.txt` (Gabriel et al. 2026, JMCP, Table 1) and `paper_10.txt` (Li et al. 2026); CMS IPAY 2027 fact sheet https://www.cms.gov/files/document/fact-sheet-negotiated-prices-ipay-2027.pdf (reading a public web page is fine; it is not 2027 outcome data).

## Part A: replicate the baseline
1. **The rule.** For each IPAY 2026 drug: r = median over plan x NDC rows (30-day supply) of UNIT_COST / MFP per unit in the 2025Q3 file (use the 2026 MFP; for Entresto Sprinkle the value corrected from 2026-06-01). Predicted change = 1/r − 1. Realized = gross Part D spending per claim, 2025 full year vs 2026 Q1, pooling the Part D brand rows of each selected drug (all brand names listed in "Selected Drug Name"; NovoLog Mix is not selected). Report predicted, realized and the error for each of the ten drugs, and both at fixed 2025 claim mix.
2. **The 2027 cohort.** For each IPAY 2027 drug: r from the 2026Q3 file against the 2027 MFP; predicted change; 2026 Q1 per-claim spending; the group change at fixed 2026 Q1 claim mix; gross spending removed at 2026 Q1 volumes.
3. **NADAC.** Latest snapshot in `nadac_2026.csv`: median NADAC per unit / 2027 MFP per unit over brand-classified NDCs of each IPAY 2027 drug; WAC-based cuts of 20% or more on those NDCs since 2024 (comparison file); for the four IPAY 2026 drugs whose MFP ends 2026-12-31 (Entresto, Stelara, Xarelto, NovoLog and Fiasp separately), NADAC / 2026 MFP.
4. **The six continuing 2026 drugs:** 2027 MFP per 30 days vs 2026.

## Part B: compare and review
Then open `pharma/prereg_2027.md`, `pharma/scripts/prereg_2027.py` and `pharma/outputs/prereg_2027/baseline.md`. Report every numeric disagreement beyond rounding and which side is right. Review:
- Is each prediction (P1 to P5) falsifiable as written, with a clear pass/fail? Are the bands too loose to be informative or too tight to be fair, given the calibration?
- Is the 1/r − 1 rule sound for 2027 (baseline period, January 2027 list-price changes, mix shifts, semaglutide's pooled rows and Wegovy's separate MFP, generic pomalidomide, formulation switches)? Any risk not recorded?
- Are the factual statements correct against sources: Gabriel and CMS discounts per drug, the $245 semaglutide agreement, the four deselected drugs and their end date, Tradjenta's renegotiation for 2028, the 2026 base rate of list-price cuts (5 of 10 between 2025-12-20 and 2026-02-28; 6 of 10 since 2024)?
- Does the document ever imply net savings from gross data?

## Output
`report.md` in your folder: verdict (PASS / PASS WITH FIXES / FAIL), Part A numbers, Part B disagreements and method findings (at most 10, ranked, each with a concrete fix). Do not edit anything outside your folder.
