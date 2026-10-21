# Review brief: do Part D plans price the negotiated drugs at the MFP? (2026-10-20)

Independent check of "finding 4". Work only in your own folder: Codex in `reviews/pharma_spuf_codex_astra/`, Agy in `reviews/pharma_spuf_agy_argon/`. No em dashes. Do not commit. Do not accept website terms or log in. Python: `.venv/bin/python` (pandas available); keep your code in your folder.

## Order matters
Do Part A with your own code and save `replication.md` in your folder BEFORE opening `pharma/scripts/spuf_mfp_check.py`, `pharma/outputs/spuf/` or the "4." finding in `pharma/ira_findings.md`.

## Data
- `data/raw/pharma/spuf/<label>/pricing file PPUF_<label>.zip`: CMS quarterly Prescription Drug Plan Formulary, Pharmacy Network and Pricing Information files (SPUF), pricing table only (pipe-delimited: CONTRACT_ID, PLAN_ID, SEGMENT_ID, NDC, DAYS_SUPPLY, UNIT_COST). Labels: `2025Q3` (release SPUF_2025_20251009), `2025Q4` (release SPUF_2026_20260107), `2026Q3` (release SPUF_2026_20261007). Each folder has `release.meta.json` or can be traced to these CMS URLs, plus sample files and plan information.
- `data/raw/pharma/ira/selected_drugs_mfp.csv`: CMS selected drug list and Maximum Fair Prices (IPAY 2026, 2027, 2028; NDC-11 dashed; "NDC-9 MFP per Unit Price"; MFP effective and end dates; some rows have an end date before their start date).

## Part A: replicate
1. Establish which plan year each release's prices belong to (do not assume from the label). Hint: compare Eliquis 5 mg NDC 00003089421 across files.
2. For every NDC on the CMS list with IPAY 2026 or 2027, take 30-day-supply rows. Ratio = UNIT_COST / MFP per unit. For IPAY 2026 use the MFP in effect at the time the release's prices apply (note Entresto Sprinkle's MFP was corrected from 2026-06-01; for a 2025 baseline use the corrected 2026 value). For IPAY 2027 use the 2027 MFP (not yet in effect in 2026).
3. Per group (IPAY) and release, and per drug and release: plan-NDC rows, plans, NDCs, median ratio, 5th and 95th percentiles, share within 0.5% of the MFP, share below, share above. Also split IPAY 2026 by stand-alone PDP (contract ID starting with S) vs Medicare Advantage.
4. List IPAY 2026 NDCs priced above the MFP (more than 0.5%) in the 2026 releases, with row counts.

## Part B: compare and review
Then open the script, `pharma/outputs/spuf/summary.md` and finding 4 in `pharma/ira_findings.md`. Report every disagreement beyond rounding and which side is right. Review methods: is unit cost on the same unit basis as the MFP per unit (EA/ML/GM; check insulin, injectables, Stelara 57894-0440-03); is a 0.5% tolerance sensible; does the comparison group make sense; what do plan unit costs include or exclude (dispensing fees, cost sharing); is unweighted plan-NDC counting misleading and how would enrollment weights change it; is the wording of finding 4 supported?

## Output
`report.md` in your folder: verdict (PASS / PASS WITH FIXES / FAIL), Part A numbers, Part B disagreements and method findings (at most 10, ranked, with fixes and primary-source links where relevant).
