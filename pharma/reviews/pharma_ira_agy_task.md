# Agy review brief: IRA negotiation study, January 2026 (pharma idea 2)

Methods review with an independent recompute. Your working directory is the repository root. Write only inside `reviews/pharma_ira_agy_argon/` (create it); do not edit other files. No em dashes. Do not accept website terms, create accounts or log in. Python: `.venv/bin/python` (pandas available); keep your code in your folder.

## Order matters

Do Part 1 and save `reviews/pharma_ira_agy_argon/recompute.md` **before** opening `pharma/scripts/ira_analysis.py`, `pharma/outputs/ira/`, `pharma/ira_findings.md` or `reviews/pharma_ira_codex_astra/`.

## Question and data

The first ten Medicare negotiated prices (Maximum Fair Prices, MFPs) took effect on 2026-01-01. Question: what changed in January 2026 in (a) Medicare Part D spending per claim, (b) manufacturer list prices (WAC), (c) pharmacy acquisition cost relative to the MFP, for the negotiated drugs compared with drugs selected for 2027/2028 and other brands?

Data (each with a `.meta.json` sidecar):
- `data/raw/pharma/ira/selected_drugs_mfp.csv`: CMS selected drug list and MFPs (IPAY 2026, 2027, 2028; NDC-11; MFP per unit and per 30-day supply).
- `data/raw/pharma/partd/partd_spending_quarterly.csv`: CMS Quarterly Part D Spending by Drug, 2025 (Q1-Q4) and 2026 (Q1).
- `data/raw/pharma/nadac/nadac_2024.csv`, `nadac_2025.csv`, `nadac_2026.csv`: NADAC weekly snapshots.
- `data/raw/pharma/nadac/nadac_comparison.csv`: NADAC rate changes with Primary Reason (e.g. "WAC Adjustment", "Survey Rate").

## Part 1: your own design and numbers (blind)

Design your own approach to each of (a), (b), (c) and compute it. Then also compute these fixed quantities for comparability:
1. Gross Part D spending per claim, 2025 vs 2026 Q1, for each of the ten IPAY 2026 drugs (sum all brand-name rows of each drug family, `Mftr_Name == "Overall"`), and the median change across other brand-name drugs with at least 4,000 claims in 2025 and 1,000 in 2026 Q1.
2. For Eliquis, Jardiance, Farxiga, NovoLog and Januvia: date and size of every WAC-based NADAC change of 20% or more since 2024.
3. For the IPAY 2026 drugs: median NADAC per unit divided by the 2026 MFP per unit (NDC-9 MFP per Unit Price, rows with MFP Effective Date 01/01/2026), at the last 2025 and last 2026 NADAC snapshot.

## Part 2: methods (most important)

- Is comparing 2025 full-year with 2026 Q1 per-claim spending sound? What biases (seasonality, days supply, generic and biosimilar entry, preliminary Q1 data, the 2025 Part D redesign) and how would you fix them with public data?
- Are drugs selected for 2027 and 2028 a good comparison group? Better alternatives?
- Does gross Part D spending for selected drugs in 2026 reflect the MFP? Check the statute and CMS guidance on the Part D negotiated price for selected drugs and on MFP effectuation (prospective vs retrospective refund, Medicare Transaction Facilitator).
- Are NADAC per unit and the CMS "NDC-9 MFP per Unit Price" on the same unit basis (EA, ML, GM)? Any NDCs where they are not?
- What explanations besides the MFP fit the January 2026 list-price cuts (Medicaid AMP rebate cap removal in 2024, 340B, PBM dynamics, launch of generics)? What would distinguish them?

## Part 3: compare

Only after `recompute.md` is saved, read `pharma/outputs/ira/summary.md` and `pharma/ira_findings.md` and report numeric disagreements beyond rounding and any statement in the findings that your analysis does not support.

## Output

`reviews/pharma_ira_agy_argon/REPORT.md`: verdict (PASS / PASS WITH FIXES / FAIL), your numbers, the comparison, at most 10 methods findings ranked by importance, each with the fix and a primary-source link.
