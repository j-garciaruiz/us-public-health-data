# Codex independent review of finding 4

**Verdict: PASS WITH FIXES.** The calculation is correct for the supplied files and the requested estimand. The independently written replication matches all **1,508,521 plan-segment-NDC rows**, including their unit costs, MFP denominators and ratios. All **783 summary-statistic cells** agree beyond floating-point noise, and all three above-MFP NDC summaries agree. Finding 4 contains two factual errors and overstates what reported plan pricing can establish. Correct the prose before treating the finding as cleared.

Reviewer: Codex, assigned Astra review. Date: 2026-10-20. No delegation, commits, source edits, login, or website-terms acceptance. This report is the independent Codex review, not a claim that the separate Agy review has finished.

## Independence and reproducibility

`replicate.py` was written and run on the raw ZIPs and CMS price CSV before opening `pharma/scripts/spuf_mfp_check.py`, anything in `pharma/outputs/spuf/`, or finding 4. `replication.md` and the Part A manifest were saved at **2026-10-20 23:50:59 UTC**. Only then were the author files opened. `compare.py` subsequently checked every matched row and all reported numeric summaries. See `numeric_comparison.csv`, `row_comparison.json`, and `reviewed_files_sha256.json` for the comparisons and reviewed-version hashes.

The raw pricing scans read 55,793,833, 53,249,171 and 54,052,371 rows respectively. All three were scanned in full. Retained records have DAYS_SUPPLY=30, a selected IPAY 2026 or 2027 NDC, and a valid applicable MFP. There are no duplicate contract-plan-segment-NDC keys, missing/negative/zero unit costs, or selected-NDC candidate rows without an applicable MFP in these inputs. There are **144 valid IPAY 2026 NDCs and 160 valid IPAY 2027 NDCs** in each lookup, many of which do not appear in a given pricing file. Counts below describe observed proxy NDCs, not all marketed packages or dispensed prescriptions.

The live CMS September 21 selected-drug CSV was also downloaded into `sources/` and is byte-identical to the supplied raw CSV. Pricing ZIPs were checked locally and hashed, not downloaded again.

## Part A: independently replicated numbers

### Which plan year is each release?

| Folder label | CMS release specified in brief | Plan year | Applicable IPAY 2026 denominator |
|---|---|---|---|
| 2025Q3 | SPUF_2025_20251009 | 2025 | Corrected 2026 MFP, as requested for baseline |
| 2025Q4 | SPUF_2026_20260107 | 2026 | MFP effective January 1, 2026 |
| 2026Q3 | SPUF_2026_20261007 | 2026 | MFP effective after June 1, 2026 |

CMS specifies that the first year in the outer SPUF filename is the contract year and the final date is the posting date. The raw sample formulary CONTRACT_YEAR fields separately corroborate 2025, 2026 and 2026 (`sample_contract_years.csv`). Release dates are not claim-service dates. [CMS SPUF methodology, p. 1](https://data.cms.gov/sites/default/files/2025-10/cf6b8476-ca42-48c6-9fc4-281b08c6ea87/Methodology-SPUF-2026.pdf).

Eliquis 5 mg, NDC 00003-0894-21, provides an independent price check:

| release | plan_year | rows | min_cost | median_cost | max_cost | mfp | median_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2025Q3 | 2025 | 5631 | 8.815900 | 10.052100 | 35.417500 | 4.145072 | 2.425072 |
| 2025Q4 | 2026 | 5514 | 3.423000 | 4.145100 | 4.145100 | 4.145072 | 1.000007 |
| 2026Q3 | 2026 | 5496 | 3.407900 | 4.145100 | 4.145100 | 4.145072 | 1.000007 |

MFP selection uses start <= reference date <= end, with blank end dates open-ended. Seventy impossible intervals are excluded: 11 starting in 2026 but ending in 2025, and 59 starting in 2027 but ending in 2026. The two Entresto Sprinkle NDCs use $1.229167 initially in 2026, then $5.521349 (00078-1231-20) and $5.648068 (00078-1238-20) from June 1. The baseline uses those corrected amounts, as the brief requires. IPAY 2027 always uses the January 2027 MFP and is explicitly a future benchmark. The author's date handling produces exactly the same denominators for these files.

### Group and plan-type results

All ratios are UNIT_COST / NDC-9 MFP per Unit Price. Percentages are percentages of unweighted rows. `within_pct` uses [0.995, 1.005], `below_pct` means <0.995, and `above_pct` means >1.005. These three categories partition the data. Plans use the full CONTRACT_ID + PLAN_ID + SEGMENT_ID key. Percentiles use linear interpolation. Keeping six decimals here is for reproducibility, not a claim of substantive precision.

| release | plan_year | IPAY | rows | plans | ndcs | median | p05 | p95 | within_pct | below_pct | above_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025Q3 | 2025 | 2026 | 199719 | 5631 | 49 | 2.767328 | 1.591325 | 3.972206 | 1.095539 | 1.494600 | 97.409861 |
| 2025Q3 | 2025 | 2027 | 307519 | 5631 | 66 | 2.524532 | 1.582369 | 5.738937 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2026 | 2026 | 232267 | 5514 | 46 | 1.000000 | 0.995324 | 1.000027 | 92.747571 | 4.949046 | 2.303384 |
| 2025Q4 | 2026 | 2027 | 289411 | 5514 | 65 | 2.525414 | 1.575377 | 5.684188 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2026 | 2026 | 206059 | 5496 | 44 | 1.000000 | 0.985453 | 1.000007 | 91.285991 | 8.714009 | 0.000000 |
| 2026Q3 | 2026 | 2027 | 273546 | 5496 | 71 | 2.111995 | 1.644901 | 5.686542 | 0.000000 | 0.000000 | 100.000000 |

IPAY 2026 split by S contracts (PDP) and H/R contracts (MA):

| release | type | rows | plans | ndcs | median | p05 | p95 | within_pct | below_pct | above_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025Q3 | MA | 183883 | 5157 | 49 | 2.769324 | 1.594844 | 3.981205 | 1.087104 | 1.559687 | 97.353208 |
| 2025Q3 | PDP | 15836 | 474 | 44 | 2.698723 | 1.553910 | 3.533787 | 1.193483 | 0.738823 | 98.067694 |
| 2025Q4 | MA | 217034 | 5147 | 46 | 1.000000 | 0.995411 | 1.000027 | 92.764267 | 4.930564 | 2.305169 |
| 2025Q4 | PDP | 15233 | 367 | 46 | 1.000000 | 0.994131 | 1.000027 | 92.509683 | 5.212368 | 2.277949 |
| 2026Q3 | MA | 192526 | 5129 | 44 | 1.000000 | 0.986785 | 1.000007 | 91.438040 | 8.561960 | 0.000000 |
| 2026Q3 | PDP | 13533 | 367 | 44 | 1.000000 | 0.961391 | 1.000007 | 89.122885 | 10.877115 | 0.000000 |

### Every IPAY 2026 NDC above the tolerance in a 2026 release

| release | drug | NDC | above_rows | all_rows_for_ndc | mfp | min_unit_cost | max_unit_cost | median_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025Q4 | STELARA | 57894044001 | 138 | 4662 | 8979.645026 | 9117.894500 | 23047.162500 | 1.137483 |
| 2025Q4 | STELARA | 57894044003 | 5170 | 5170 | 8979.645026 | 16083.047900 | 69141.453400 | 2.470604 |
| 2025Q4 | STELARA | 57894044101 | 42 | 4662 | 8980.144587 | 18207.176700 | 23047.162500 | 2.027493 |

These are **5,350 rows across three NDCs** in the January release. There are **zero** rows above 1.005 in the October release. The median ratios in this exception table are among above-threshold rows, not all rows of the NDC.

### Every drug and release

Names in this table use the first name of the CMS selected-drug group to match the author's labels. The full CMS names are retained in `drugs.csv` and `replication.md`; for example, NOVOLOG includes Fiasp, and OZEMPIC includes Rybelsus and Wegovy. All ten IPAY 2026 groups and all fifteen IPAY 2027 groups are present in every release.

| release | IPAY | drug | rows | plans | ndcs | median | p05 | p95 | within_pct | below_pct | above_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025Q3 | 2026 | ELIQUIS | 16721 | 5631 | 3 | 2.403119 | 2.275956 | 2.599014 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2026 | ENBREL | 23983 | 4801 | 5 | 3.438480 | 3.238332 | 4.051696 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2026 | ENTRESTO | 25511 | 5631 | 5 | 2.180282 | 2.082393 | 2.391007 | 0.000000 | 0.011760 | 99.988240 |
| 2025Q3 | 2026 | FARXIGA | 10978 | 5474 | 4 | 3.173218 | 2.689647 | 3.477483 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2026 | IMBRUVICA | 29665 | 5631 | 6 | 1.722669 | 1.578778 | 1.909663 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2026 | JANUVIA | 16404 | 5468 | 3 | 2.707961 | 2.331876 | 4.685859 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2026 | JARDIANCE | 11248 | 5624 | 2 | 2.966900 | 2.506794 | 3.281391 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2026 | NOVOLOG | 19089 | 3576 | 9 | 1.989688 | 0.971047 | 4.126283 | 11.462099 | 15.579653 | 72.958248 |
| 2025Q3 | 2026 | STELARA | 13446 | 4478 | 6 | 3.120436 | 2.912907 | 3.401891 | 0.000000 | 0.059497 | 99.940503 |
| 2025Q3 | 2026 | XARELTO | 32674 | 5631 | 6 | 2.837117 | 2.706634 | 3.087878 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | AUSTEDO | 55269 | 5304 | 12 | 1.632129 | 1.548518 | 1.848948 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | BREO ELLIPTA | 16557 | 5528 | 5 | 5.727692 | 5.493436 | 6.329514 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | CALQUENCE | 11203 | 5631 | 2 | 1.610269 | 1.453625 | 1.801713 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | IBRANCE | 33786 | 5631 | 6 | 2.020859 | 1.894436 | 2.302707 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | JANUMET | 27325 | 5465 | 5 | 3.640824 | 3.095539 | 6.092861 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | LINZESS | 16893 | 5631 | 3 | 4.002203 | 3.862652 | 4.430966 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | OFEV | 11252 | 5631 | 2 | 2.083568 | 1.938106 | 2.310959 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | OTEZLA | 14582 | 3649 | 4 | 3.129066 | 2.924484 | 3.531684 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | OZEMPIC | 33208 | 5592 | 11 | 3.473564 | 3.343492 | 3.842970 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | POMALYST | 22524 | 5631 | 4 | 2.637842 | 2.452422 | 3.064566 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | TRADJENTA | 5477 | 5477 | 1 | 6.015977 | 5.143445 | 6.681175 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | TRELEGY ELLIPTA | 11090 | 5545 | 2 | 3.709252 | 3.590416 | 4.106743 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | VRAYLAR | 22524 | 5631 | 4 | 1.846032 | 1.753698 | 2.179117 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | XIFAXAN | 8936 | 5631 | 2 | 2.825651 | 2.668707 | 3.338397 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q3 | 2027 | XTANDI | 16893 | 5631 | 3 | 1.938457 | 1.789923 | 2.241736 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2026 | ELIQUIS | 16542 | 5514 | 3 | 1.000007 | 0.999983 | 1.000007 | 99.981864 | 0.018136 | 0.000000 |
| 2025Q4 | 2026 | ENBREL | 27570 | 5514 | 5 | 1.000000 | 1.000000 | 1.000000 | 99.981864 | 0.018136 | 0.000000 |
| 2025Q4 | 2026 | ENTRESTO | 12252 | 5514 | 5 | 1.000027 | 0.999945 | 1.000027 | 99.649037 | 0.350963 | 0.000000 |
| 2025Q4 | 2026 | FARXIGA | 22056 | 5514 | 4 | 1.000001 | 0.999984 | 1.000001 | 99.918390 | 0.081610 | 0.000000 |
| 2025Q4 | 2026 | IMBRUVICA | 33084 | 5514 | 6 | 1.000000 | 0.999999 | 1.000000 | 99.981864 | 0.018136 | 0.000000 |
| 2025Q4 | 2026 | JANUVIA | 16542 | 5514 | 3 | 1.000004 | 0.999978 | 1.000004 | 99.981864 | 0.018136 | 0.000000 |
| 2025Q4 | 2026 | JARDIANCE | 11028 | 5514 | 2 | 1.000003 | 0.999989 | 1.000003 | 99.981864 | 0.018136 | 0.000000 |
| 2025Q4 | 2026 | NOVOLOG | 33084 | 5514 | 6 | 0.999996 | 0.993281 | 1.000002 | 93.220288 | 6.779712 | 0.000000 |
| 2025Q4 | 2026 | STELARA | 28988 | 5170 | 6 | 1.000000 | 0.806149 | 2.525319 | 49.989651 | 31.554436 | 18.455913 |
| 2025Q4 | 2026 | XARELTO | 31121 | 5514 | 6 | 1.000001 | 0.999979 | 1.000035 | 99.919668 | 0.080332 | 0.000000 |
| 2025Q4 | 2027 | AUSTEDO | 50664 | 4872 | 12 | 1.599022 | 1.543717 | 1.722143 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | BREO ELLIPTA | 15918 | 5305 | 5 | 5.683732 | 5.378990 | 6.144074 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | CALQUENCE | 5514 | 5514 | 1 | 1.627663 | 1.508556 | 1.746799 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | IBRANCE | 33084 | 5514 | 6 | 2.001730 | 1.884961 | 2.136415 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | JANUMET | 26250 | 5250 | 5 | 3.634290 | 3.458116 | 6.078740 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | LINZESS | 16542 | 5514 | 3 | 3.991984 | 3.836305 | 4.278713 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | OFEV | 11028 | 5514 | 2 | 2.047822 | 1.929987 | 2.151185 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | OTEZLA | 13088 | 3275 | 4 | 3.067093 | 2.901152 | 3.239893 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | OZEMPIC | 32121 | 5463 | 11 | 3.459383 | 3.325596 | 3.682582 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | POMALYST | 22056 | 5514 | 4 | 2.622647 | 2.452422 | 2.763345 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | TRADJENTA | 5035 | 5035 | 1 | 6.014080 | 5.715409 | 6.437816 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | TRELEGY ELLIPTA | 10913 | 5514 | 2 | 3.698368 | 3.524279 | 3.989575 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | VRAYLAR | 22056 | 5514 | 4 | 1.827612 | 1.751545 | 1.948630 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | XIFAXAN | 8600 | 5514 | 2 | 2.803499 | 2.668029 | 2.972942 | 0.000000 | 0.000000 | 100.000000 |
| 2025Q4 | 2027 | XTANDI | 16542 | 5514 | 3 | 1.920723 | 1.776304 | 2.079849 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2026 | ELIQUIS | 16488 | 5496 | 3 | 1.000007 | 0.999983 | 1.000007 | 99.981805 | 0.018195 | 0.000000 |
| 2026Q3 | 2026 | ENBREL | 27480 | 5496 | 5 | 1.000000 | 1.000000 | 1.000000 | 99.981805 | 0.018195 | 0.000000 |
| 2026Q3 | 2026 | ENTRESTO | 12171 | 5496 | 5 | 0.999991 | 0.999988 | 1.000006 | 99.958919 | 0.041081 | 0.000000 |
| 2026Q3 | 2026 | FARXIGA | 6324 | 3162 | 2 | 1.000001 | 0.999984 | 1.000001 | 99.968374 | 0.031626 | 0.000000 |
| 2026Q3 | 2026 | IMBRUVICA | 32976 | 5496 | 6 | 1.000000 | 0.939999 | 1.000000 | 65.644711 | 34.355289 | 0.000000 |
| 2026Q3 | 2026 | JANUVIA | 14844 | 4948 | 3 | 1.000004 | 0.999978 | 1.000004 | 100.000000 | 0.000000 | 0.000000 |
| 2026Q3 | 2026 | JARDIANCE | 10992 | 5496 | 2 | 1.000003 | 0.999989 | 1.000003 | 99.981805 | 0.018195 | 0.000000 |
| 2026Q3 | 2026 | NOVOLOG | 32520 | 5496 | 6 | 0.999996 | 0.991282 | 1.000002 | 87.223247 | 12.776753 | 0.000000 |
| 2026Q3 | 2026 | STELARA | 21366 | 3642 | 6 | 1.000000 | 0.811009 | 1.000000 | 88.608069 | 11.391931 | 0.000000 |
| 2026Q3 | 2026 | XARELTO | 30898 | 5496 | 6 | 1.000003 | 0.999979 | 1.000035 | 99.932034 | 0.067966 | 0.000000 |
| 2026Q3 | 2027 | AUSTEDO | 50856 | 4879 | 12 | 1.683888 | 1.600352 | 1.834838 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | BREO ELLIPTA | 16120 | 5373 | 5 | 5.685312 | 5.368151 | 6.154807 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | CALQUENCE | 5496 | 5496 | 1 | 1.674388 | 1.554202 | 1.805565 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | IBRANCE | 21984 | 5496 | 4 | 2.015165 | 1.589684 | 2.188570 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | JANUMET | 23252 | 5232 | 5 | 3.626331 | 3.433333 | 4.158455 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | LINZESS | 16488 | 5496 | 3 | 1.986037 | 1.897636 | 2.151948 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | OFEV | 3918 | 1959 | 2 | 2.125468 | 1.968447 | 2.225703 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | OTEZLA | 18970 | 3257 | 6 | 3.239055 | 3.056511 | 3.422229 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | OZEMPIC | 33030 | 5445 | 15 | 3.628883 | 3.434426 | 3.884339 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | POMALYST | 9508 | 2377 | 4 | 2.701133 | 2.562672 | 2.897504 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | TRADJENTA | 5018 | 5018 | 1 | 6.015458 | 5.670014 | 6.499033 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | TRELEGY ELLIPTA | 10877 | 5496 | 2 | 3.810245 | 3.596353 | 4.110765 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | VRAYLAR | 32976 | 5496 | 6 | 1.938442 | 1.839245 | 2.061984 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | XIFAXAN | 8565 | 5496 | 2 | 3.253426 | 3.107599 | 3.526561 | 0.000000 | 0.000000 | 100.000000 |
| 2026Q3 | 2027 | XTANDI | 16488 | 5496 | 3 | 1.977230 | 1.829263 | 2.156980 | 0.000000 | 0.000000 | 100.000000 |

## Part B: ranked findings and fixes

### 1. High priority: reported average prices are not observed point-of-sale payments

**Location:** `pharma/ira_findings.md:33`, heading and last sentence. The assertion that these are the prices plans actually pay at the point of sale exceeds the evidence. SPUF UNIT_COST is a reported average across in-area retail pharmacies for a specified supply category, keyed to a proxy NDC. It is not a claim, the plan-funded portion of a claim, a patient payment, or a complete net expenditure measure. It does not list a separate price for every package and pharmacy. January is the publication of a 2026 schedule, not verification of every transaction beginning January 1. The narrow result, that reported unit prices cluster at the MFP, is strongly supported. All 40 drug-by-plan-type medians in the two 2026 releases round to 1.000 (`drug_plan_type_medians.csv`), so the statement that the pattern spans all ten drugs and both plan types is supported at that aggregate level.

**Fix:** use “Reported Part D retail unit prices cluster at the MFP in the 2026 pricing files.” Replace the final sentence with “This directly checks reported plan unit-price schedules against the MFP; it does not establish realized claim payments or net savings.” [CMS 2026 record layout, pricing file, p. 15](https://data.cms.gov/sites/default/files/2025-10/83da019f-fa24-483e-87de-cc089780a6a5/SPUFRecordLayout-2026.pdf).

### 2. High priority: the 2027 comparison median did not stay at 2.5 in both releases

**Location:** `pharma/ira_findings.md:33`. January is **2.525414**, October **2.111995**, a **16.37% decrease** in the pooled median ratio. Calling both 2.5 is not rounding. The script and summary table are right; the prose is wrong. Every 2027 row remains above 1.005, but stability does not follow. Linzess's drug median falls from approximately 3.992 to 1.986, and the observed NDC/plan mix also changes.

**Fix:** “The IPAY 2027 group remained above its future MFP, with median ratios of 2.525 in January and 2.112 in October.” Also replace the summary generator's prediction that the gap “will close next year” with “measures the gap to the future 2027 MFP.” An upper bound need not produce equality, and a future dataset has not been observed. Evidence: `groups.csv`, `drugs.csv`, and the matching author tables. [CMS selected drugs and negotiated prices](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices).

### 3. High priority: three exception NDCs, and disappearance does not establish correction of every row

**Location:** `pharma/ira_findings.md:33`. The assertion that “only” one product exceeded the MFP contradicts both independent replication and `above_mfp_2026.csv`. NDCs 57894-0440-03, 57894-0440-01 and 57894-0441-01 contribute 5,170, 138 and 42 rows respectively. The largest accounts for **96.64%**, not 100%, of exceptions. These are unbranded ustekinumab presentations included in CMS's STELARA group; the label need not mean the branded product.

The 0.5 mL vial's January median ratio is 2.470604. Of its 5,170 January above-threshold plan-NDC pairs, only 3,642 reappear in October; all are at or below the threshold. The other 1,528 are absent. All 138 and 42 exceptions for the other NDCs reappear at or below the threshold. `exception_followthrough.csv` documents this. Therefore “none observed above in October” is justified, while “corrected” is not established for every January row or as a cause of the change.

**Fix:** enumerate all three NDCs, describe the dominant one as an unbranded 45 mg/0.5 mL vial in the STELARA group, and say “No above-threshold observations remain in the October file.” Do not infer improper actual payments from these reported-price anomalies. [Manufacturer billing guide, pp. 23 and 35](https://asset.jnjwithme.com/document/ustekinumab-billing-and-coding-guide.pdf).

### 4. Medium priority: clarify fees, cost sharing and point-of-sale rebates

**Location:** `pharma/ira_findings.md:37`. Excluding dispensing fees from UNIT_COST is correct. The phrase “say nothing about rebates” is too broad: CMS explicitly directs sponsors to submit unit costs net of rebates and concessions applied at the point of sale; those amounts are not separately identified. Off-invoice/retrospective rebates and the plan's final net cost are not measured. Dispensing fees are separate fields in the pharmacy network file, while beneficiary copays and coinsurance are in separate benefit files. The drug unit cost is not reduced to the plan-paid amount by subtracting patient cost sharing.

**Fix:** “Unit costs exclude separately reported dispensing fees and incorporate concessions applied at the point of sale; they do not identify rebate amounts, final net plan spending, or beneficiary out-of-pocket costs.” The statutory ceiling is MFP **plus dispensing fees** for the negotiated price, so comparing ingredient unit cost with per-unit MFP is conceptually appropriate. [CMS 2026 pricing guidelines, pp. 14, 17 and 22–23, in this ZIP](https://www.cms.gov/files/zip/2026-pricing-data-guidelines-calendar.zip); [CMS final negotiation guidance, p. 196](https://www.cms.gov/files/document/medicare-drug-price-negotiation-final-guidance-ipay-2027-and-manufacturer-effectuation-mfp-2026-2027.pdf).

### 5. Medium priority: unit basis passes, but document it and retain the injectable anomaly

Both systems use NDC-specific NCPDP billing units, including EA, ML and GM, rather than a universal “pill” or “package.” DAYS_SUPPLY=30 selects a price schedule; it does not make UNIT_COST a 30-day total. Likewise the single drug-level MFP per 30-day equivalent supply is not the denominator used here. CMS's NDC-9 per-unit MFP is the appropriate denominator. The NCPDP unit requirement is explicit in the [2026 pricing guidelines, p. 14](https://www.cms.gov/files/zip/2026-pricing-data-guidelines-calendar.zip), and the MFP calculation uses dispensing quantities in [final guidance, sections 60.2 and 60.5](https://www.cms.gov/files/document/medicare-drug-price-negotiation-final-guidance-ipay-2027-and-manufacturer-effectuation-mfp-2026-2027.pdf).

Concrete checks:

- Eliquis 00003-0894-21 is compared per tablet: January median $4.1451 versus MFP $4.145072.
- Fiasp vial 00169-3201-11 is compared per mL: $6.9569 versus $6.956927. Fiasp FlexTouch 00169-3204-15 is also per mL: $8.9570 versus $8.956984 in January. Multiplying by 100 insulin units/mL, 3 mL per pen or 15 mL per carton would change one side's basis incorrectly. The [manufacturer's Fiasp presentation information](https://www.novomedlink.com/diabetes/products/treatments/fiasp/resources/for-pharmacists.html) and [CMS contractor NDC crosswalk](https://www.dmepdac.com/palmetto/PDAC_files.nsf/F/PDAC2025-10-05XWalk.pdf/%24FILE/2025-10-05XWalk.pdf) distinguish package, mL and therapeutic units.
- Enbrel's five observed NDCs all have January and October median ratios effectively 1.000 (`injectable_unit_checks.csv`). Liquid injectables use ML, while an EA-coded powder vial must retain its own billing basis; do not assume every injectable has the same physical unit.
- The manufacturer explicitly specifies **ML 0.5** for one 45 mg vial of 57894-0440-03. Its $8,979.645026 MFP is per mL; on a 0.5 mL basis it is $4,489.822513. January's $22,185.1436 median per mL becomes $11,092.5718 per vial, leaving the ratio **2.470604 unchanged**. The same NDC is effectively 1.000 in October. A package conversion does not erase the discrepancy. In January the vial price is approximately three times the same-plan 0.5 mL syringe's unit price for 4,547 of 4,662 paired plans. That is a reporting-pattern diagnostic, not proof of a valid threefold unit conversion or a specific cause. [Manufacturer guide, p. 35](https://asset.jnjwithme.com/document/ustekinumab-billing-and-coding-guide.pdf).

**Fix:** add a short explicit billing-unit note and retain these NDC checks with the analysis. No unit-conversion correction to the computed ratios is warranted by the evidence inspected. An exhaustive independent product-master audit of every observed NDC was not performed.

### 6. Medium priority: unweighted rows measure schedules, not patients, prescriptions or dollars

The existing unweighted qualifier is necessary and correct. However, the pooled percentage gives more influence to plans with more observed NDCs and to drugs with more package/product codes, with no regard to enrollment or use. In October, PDP contributes only **6.57% of rows**; its within-band share is 89.122885%, versus 91.438040% in MA. Holding within-type composition fixed, increasing PDP's weight lowers the overall within-band share. That alone cannot establish the effect of actual enrollment weights because enrollment varies within each type and the drug mix is unequal.

Two independently computed sensitivities show the choice of estimand:

| release | unweighted_rows_pct | equal_plan_pct | equal_drug_pct |
| --- | --- | --- | --- |
| 2025Q3 | 1.095539 | 1.070440 | 1.146210 |
| 2025Q4 | 92.747571 | 92.864018 | 94.260636 |
| 2026Q3 | 91.285991 | 91.439395 | 94.128077 |

`equal_plan_pct` first averages each plan-segment's observed NDC indicators, then gives each plan-segment equal weight. `equal_drug_pct` first averages within each CMS drug group and then gives each drug group equal weight. Neither is enrollment-weighted.

**Fix:** keep the current result as an unweighted schedule-level statistic. For beneficiary exposure, join date-matched [CMS monthly plan enrollment](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-advantagepart-d-contract-and-enrollment-data/monthly-enrollment-plan), handle suppressed counts, and reconcile the enrollment key with pricing segments without replicating each plan's full enrollment across its segments. First define a fixed drug/NDC basket or a within-plan summary; then weight that summary by enrollment. Simply attaching enrollment to every NDC also weights plans by their NDC counts. Prescription or spending effects additionally require actual utilization/quantity or expenditure weights. Actual enrollment-weighted shares were not estimated here, so their numerical change remains unknown. Within this observed October sample, zero above 1.005 remains zero under any nonnegative weights.

### 7. Medium priority: the 2027 group is a useful benchmark, not a causal control

It is reasonable to compare 2026 prices with the future MFP of selected 2027 drugs as a check that the entire database was not mechanically normalized to one. All its observed ratios remain above 1.005. It is not a randomized, therapeutically matched or demonstrably parallel-trending control: selection, price changes before implementation, generic competition and composition can differ. The present study therefore supports a descriptive contrast, not a treatment-effect estimate. The wider document's “Not causal” limitation is appropriate and should also govern finding 4.

The changing sample matters. IPAY 2026 observed NDCs decline from 49 to 46 to 44, and observed plan counts also change. In a common contract-plan-segment-NDC panel present in all three releases, the result remains:

| release | IPAY | rows | plans | ndcs | median | within_pct | above_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2025Q3 | 2026 | 130733 | 4368 | 44 | 2.774982 | 1.366143 | 96.817942 |
| 2025Q3 | 2027 | 188404 | 4368 | 60 | 2.504596 | 0.000000 | 100.000000 |
| 2025Q4 | 2026 | 130733 | 4368 | 44 | 1.000000 | 98.729472 | 0.003060 |
| 2025Q4 | 2027 | 188404 | 4368 | 60 | 2.452422 | 0.000000 | 100.000000 |
| 2026Q3 | 2026 | 130733 | 4368 | 44 | 1.000000 | 92.007374 | 0.000000 |
| 2026Q3 | 2027 | 188404 | 4368 | 60 | 2.085909 | 0.000000 | 100.000000 |

The common panel preserves the near-one 2026 median, but January's within-band fraction is **98.729472%**, versus **92.747571%** in the full cross-section. It retains only four January above-threshold observations because the unbranded ustekinumab products were rarely observed in the 2025 baseline. This sensitivity is evidence of composition, not a reason to discard the full-sample exceptions. The common 2027 panel still declines from 2.452422 to 2.085909 across 2026, so its pooled decline is not solely caused by changing membership.

**Fix:** call it a future-price comparison group, report the declining medians correctly, and include the fixed-panel sensitivity. Do not call it a causal counterfactual or infer a guaranteed future convergence to exact equality.

### 8. Lower priority: 0.5% is a sensible descriptive band, not literal equality or a compliance allowance

Four-decimal SPUF unit costs and six-decimal MFPs will differ slightly after rounding. A symmetric 0.5% band is defensible for describing clustering, but much wider than numeric rounding: for a $8,980 unit it permits about $44.90 either side. Label “within 0.5%” consistently rather than turning it into exact “at.” In October, 101,228 rows are arithmetically above ratio 1, but the maximum ratio is only **1.000034611**, about **0.00346%** above; none exceed even 1.0001. They are consistent with four-decimal rounding, not substantive excesses.

Sensitivity for IPAY 2026, percentages within the stated band:

| Release | ±0.01% | ±0.1% | ±0.5% | ±1% |
|---|---:|---:|---:|---:|
| 2025Q3 | 0.017525 | 0.207792 | 1.095539 | 1.761475 |
| 2025Q4 | 91.508049 | 92.047084 | 92.747571 | 93.434280 |
| 2026Q3 | 88.777971 | 89.702949 | 91.285991 | 94.589414 |

**Fix:** define below/above as outside the band, write “none more than 0.5% above,” and retain `tolerance.csv`. For a strict equality audit, compare each UNIT_COST with its MFP rounded to four decimal places using an absolute rounding bound. Do not imply CMS legally permits 0.5% excess pricing. The broad empirical result survives much tighter tolerances.

## Suggested replacement for finding 4

**4. Reported Part D retail unit prices cluster at the MFP in the 2026 pricing files.** For observed products in the ten IPAY 2026 drug groups, the median reported unit-cost/MFP ratio fell from 2.767 in the 2025 plan-year file to 1.000 in both 2026 releases. In the January 2026 release, 92.7% of unweighted plan-segment-NDC rows were within 0.5% of the applicable MFP, 4.9% were more than 0.5% below and 2.3% were more than 0.5% above. In the October release, the corresponding shares were 91.3%, 8.7% and 0%. Drug-group medians were near one in both stand-alone PDP and Medicare Advantage plans. January's 5,350 above-threshold rows involved three unbranded ustekinumab NDCs in the STELARA group, predominantly the 45 mg/0.5 mL vial 57894-0440-03; no above-threshold observations remain in October. For IPAY 2027 drugs, whose MFPs were not yet effective, median ratios to their future MFP were 2.525 in January and 2.112 in October. These are reported average in-area retail unit prices for 30-day supply schedules, not observed claim payments, patient costs or net savings.

**Limits:** Rows are unweighted and use observed proxy NDCs rather than a fixed utilization basket. UNIT_COST excludes separate dispensing fees and incorporates concessions applied at the point of sale, without identifying rebate amounts or final net plan spending. Below and above refer to the 0.5% band. The January release's internal 2025Q4 label denotes 2026 plan prices. MFP denominators are date-specific, including the June Entresto Sprinkle correction; the 2025 comparison uses the corrected 2026 benchmark.

## Shortcuts taken

Actual enrollment weights and transaction-level claims were not acquired or estimated; they are not necessary to reproduce the specified unweighted analysis, and no claim about their numerical outcomes is made. Unit verification combined authoritative NCPDP rules with targeted insulin and injectable checks rather than a complete product-master audit. The supplied pricing ZIPs were not downloaded again; their hashes are preserved, contract years were corroborated, and the MFP source was checked against the live official download. The existing chart was not visually reviewed because the task asks for the script, tables and finding; every statistic supplied to its plotted medians and percentiles was verified. All writes are confined to this review folder.
