# Codex review brief: IRA negotiation study, January 2026 (pharma idea 2)

Independent replication. Work only inside `reviews/pharma_ira_codex_astra/` (create it). Do not edit other files. No em dashes. Do not accept website terms, create accounts or log in. Python: `.venv/bin/python` (pandas available). Repository root: `/Users/hari/Documents/VSC Python/US Data/.claude/worktrees/pharma-data-eae972`.

## Order matters

Do Part A with your own code and save `reviews/pharma_ira_codex_astra/replication.md` **before** opening `pharma/scripts/ira_analysis.py`, `pharma/outputs/ira/` or `pharma/ira_findings.md`.

## Data (downloaded 2026-10-20; each has a `.meta.json` sidecar with source URL and SHA-256)

- `data/raw/pharma/ira/selected_drugs_mfp.csv`: CMS Medicare Drug Price Negotiation selected drug list and Maximum Fair Prices (file dated 2026-09-21). Columns include IPAY, Selected Drug Name, NDC-11 (dashed), MFP Effective Date, Single MFP per 30 DES, NDC-9 MFP per Unit Price.
- `data/raw/pharma/partd/partd_spending_quarterly.csv`: CMS Quarterly Part D Spending by Drug (rows for "2025 (Q1-Q4)" and "2026 (Q1)"; use `Mftr_Name == "Overall"` rows).
- `data/raw/pharma/nadac/nadac_2024.csv`, `nadac_2025.csv`, `nadac_2026.csv`: NADAC weekly snapshots (`As of Date`).
- `data/raw/pharma/nadac/nadac_comparison.csv`: NADAC Comparison (old vs new rate per NDC, Percent Change, Primary Reason, Effective Date).

## Part A: replicate (definitions are fixed; implement them yourself)

Groups: an NDC or brand belongs to "IPAY 2026", "IPAY 2027" or "IPAY 2028" by the earliest IPAY it appears under in the CMS file; everything else is "Other brands".

1. **Part D spending per claim.** Map Part D `Brnd_Name` to a selected drug family when the upper-cased brand equals one of the semicolon-separated names in `Selected Drug Name` or starts with that name followed by a space (e.g. NOVOLOG FLEXPEN -> NOVOLOG). Other brands = rows whose upper-cased brand differs from the upper-cased generic name and are not selected. Sum Tot_Spndng and Tot_Clms by family and period; per-claim = spending / claims. Keep families with at least 4,000 claims in 2025 and 1,000 in 2026 Q1. Report, per group: number of families, median, 25th and 75th percentile of the per-claim % change 2025 to 2026 Q1, pooled change (total spend / total claims), share of families falling 30% or more. Report the per-family change for every IPAY 2026 family and for Linzess, plus the annualized claim change (4 x Q1 claims / 2025 claims - 1).
2. **January list-price cuts.** For each January of 2024, 2025, 2026: universe = NDCs with Classification for Rate Setting "B" in any NADAC snapshot dated in that January. Event = a NADAC Comparison row whose Primary Reason contains "WAC" with Effective Date from Dec 20 of the prior year to Jan 31. Per group: universe size, number and share of NDCs whose most negative such change is -20% or lower, number and share with any positive such change. List the selected drugs with cuts of -20% or lower (NDC count, median % change, earliest effective date).
3. **NADAC relative to MFP.** For IPAY 2026 rows with MFP Effective Date 01/01/2026, take the NDC-9 MFP per Unit Price per NDC-11. Join to NADAC by NDC-11. Ratio = NADAC per unit / MFP per unit. Per drug (first name in Selected Drug Name): median ratio across NDCs at the last 2025 snapshot and the last 2026 snapshot, with NDC counts and pricing units.

## Part B: compare and review

Then open `pharma/outputs/ira/summary.md`, the CSVs beside it and `pharma/scripts/ira_analysis.py`. List every disagreement beyond rounding and which side is right. Review the script for bugs (brand matching false positives or misses, e.g. "Other brands" containing generics or selected drugs; NDC group assignment; window edges; unit mismatches between NADAC and MFP; the year-end snapshot choice).

## Part C: check the write-up

Read `pharma/ira_findings.md`. For each numbered finding and each limit, say whether the numbers match your replication and whether the wording is supported. Check against primary sources: what the Part D Spending by Drug "gross drug cost" includes and whether 2026 PDE amounts for selected drugs reflect the MFP (statute, CMS guidance, data.cms.gov methodology); how MFP is effectuated for pharmacies (prospective vs refund, the Medicare Transaction Facilitator); whether NADAC brand rates follow WAC changes. Flag overclaims and missing caveats, and anything a health economist reviewer would object to.

## Output

`reviews/pharma_ira_codex_astra/report.md`: verdict (PASS / PASS WITH FIXES / FAIL), Part A results, Part B disagreements and bugs, Part C assessment, at most 12 findings ranked by severity with fixes and source links. Concise.
