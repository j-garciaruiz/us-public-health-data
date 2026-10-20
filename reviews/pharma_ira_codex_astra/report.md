# Independent review: IRA negotiation study

**Verdict: PASS WITH FIXES.** The stipulated calculations replicate. The study needs corrected drug classification and narrower economic interpretation before circulation. In particular, its current mapping changes whether nine or all ten selected families cross the 30% decline threshold.

Completed 2026-10-20. [Part A](replication.md) was saved at 18:06:44 UTC **before** opening the original script, outputs or findings. All available raw-file sidecar hashes passed; the selected-drug CSV also matches its ZIP member byte for byte. Work was confined to this review directory. No commits.

## Part A: independent results under the fixed definitions

These are the requested definitions, including their classification defects identified below. Percentages are percentage changes unless labeled as shares. Full precision, claims, spending and source hashes are in [replication.md](replication.md), the adjacent CSVs and [provenance.json](provenance.json).

### Part D spending per claim

Families satisfy at least 4,000 claims in 2025 and 1,000 in 2026 Q1. Pooled changes use those same families.

| Group | Families | Median | P25 | P75 | Pooled | Share falling ≥30% |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IPAY 2026 | 10 | -63.69% | -68.08% | -57.58% | -61.66% | 90.00% |
| IPAY 2027 | 15 | +2.37% | +0.78% | +3.55% | +4.28% | 6.67% |
| IPAY 2028 | 15 | +1.71% | +0.01% | +3.87% | +13.22% | 0.00% |
| Other brands | 1,088 | +0.29% | -3.90% | +3.47% | +7.19% | 1.75% |

| Family | 2025 $/claim | 2026 Q1 $/claim | Change | Annualized claim change¹ |
| --- | ---: | ---: | ---: | ---: |
| Eliquis | 912.31 | 399.01 | -56.26% | -1.34% |
| Enbrel | 8,681.63 | 2,536.74 | -70.78% | +1.03% |
| Entresto | 1,077.56 | 323.74 | -69.96% | -86.50% |
| Farxiga | 997.75 | 328.97 | -67.03% | -30.45% |
| Imbruvica | 16,055.46 | 9,646.30 | -39.92% | -12.63% |
| Januvia | 556.08 | 214.01 | -61.51% | -5.54% |
| Jardiance | 1,091.19 | 386.83 | -64.55% | +0.13% |
| NovoLog | 291.85 | 208.94 | -28.41% | +38.63% |
| Stelara | 26,682.00 | 8,424.82 | -68.43% | -43.77% |
| Xarelto | 1,006.21 | 374.04 | -62.83% | -9.95% |
| Linzess | 843.43 | 429.99 | -49.02% | -3.68% |

¹ `100 × (4 × Q1 claims / full-year 2025 claims − 1)`, a run-rate comparison, not an observed annual change.

### January WAC-related NADAC events

Universe: distinct NDCs classified B in any January snapshot. Windows include December 20 through January 31. Cuts use each NDC's minimum change; increases require any positive change.

| January | Group | Universe | Cuts ≤-20% | Cut share | Any increase | Increase share |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2024 | IPAY 2026 | 63 | 3 | 4.76% | 58 | 92.06% |
| 2024 | IPAY 2027 | 63 | 0 | 0.00% | 55 | 87.30% |
| 2024 | IPAY 2028 | 20 | 0 | 0.00% | 20 | 100.00% |
| 2024 | Other brands | 1,572 | 57 | 3.63% | 786 | 50.00% |
| 2025 | IPAY 2026 | 67 | 13 | 19.40% | 47 | 70.15% |
| 2025 | IPAY 2027 | 70 | 15 | 21.43% | 42 | 60.00% |
| 2025 | IPAY 2028 | 30 | 0 | 0.00% | 30 | 100.00% |
| 2025 | Other brands | 2,327 | 5 | 0.21% | 929 | 39.92% |
| 2026 | IPAY 2026 | 69 | 21 | 30.43% | 13 | 18.84% |
| 2026 | IPAY 2027 | 67 | 3 | 4.48% | 36 | 53.73% |
| 2026 | IPAY 2028 | 33 | 1 | 3.03% | 21 | 63.64% |
| 2026 | Other brands | 2,198 | 33 | 1.50% | 836 | 38.03% |

| January | Selected family | IPAY | Cut NDCs | Median change | Earliest cut date |
| --- | --- | ---: | ---: | ---: | --- |
| 2024 | NovoLog | 2026 | 3 | -75.00% | 2024-01-01 |
| 2025 | Januvia | 2026 | 13 | -42.41% | 2025-01-01 |
| 2025 | Janumet | 2027 | 15 | -42.41% | 2025-01-01 |
| 2026 | Eliquis | 2026 | 6 | -43.00% | 2026-01-01 |
| 2026 | Farxiga | 2026 | 5 | -37.00% | 2026-01-01 |
| 2026 | Jardiance | 2026 | 6 | -44.39% | 2026-01-01 |
| 2026 | NovoLog | 2026 | 4 | -75.00% | 2026-01-01 |
| 2026 | Linzess | 2027 | 3 | -50.27% | 2026-01-01 |
| 2026 | Xeljanz | 2028 | 1 | -25.00% | 2026-01-01 |

### NADAC / 2026 MFP per unit

Snapshot medians are unweighted across matched NDCs, not pharmacies or claims. The final available dates are 2025-12-31 and 2026-10-21, the latter being the file's label despite retrieval on October 20.

| Family | 2025-12-31 ratio | NDCs | 2026-10-21 ratio | NDCs | NADAC units |
| --- | ---: | ---: | ---: | ---: | --- |
| Eliquis | 2.3383 | 6 | 1.3310 | 6 | EA |
| Enbrel | 3.3964 | 4 | 3.5683 | 4 | ML |
| Entresto | 2.1561 | 7 | 2.2183 | 8 | EA |
| Farxiga | 3.1653 | 7 | 1.9949 | 7 | EA |
| Imbruvica | unavailable | 0 | unavailable | 0 | unavailable |
| Januvia | 2.7008 | 13 | 2.6986 | 13 | EA |
| Jardiance | 2.9637 | 6 | 1.6469 | 6 | EA |
| NovoLog | 1.9998 | 10 | 0.9970 | 10 | ML |
| Stelara | 3.1624 | 2 | 3.3223 | 2 | ML |
| Xarelto | 2.7793 | 19 | 2.8405 | 19 | EA and ML |

## Part B: disagreements and script audit

**No numerical disagreements beyond floating-point rounding under the fixed definitions.** [Automated comparisons](comparison_checks.json) cover all six CSVs: 1,128 family rows, four Part D group rows, 12 January group rows, 83 cut-event summaries, 855 weekly ratios and ten endpoint summaries. Imbruvica's missing counts are displayed as zero here and blank in the original; both indicate no matches. Neither side has an arithmetic correction to make.

The implementation correctly preserves NDC zeroes, uses earliest IPAY, includes both window endpoints, deduplicates January universes and selects the actual final snapshots. There are no cross-IPAY NDC conflicts in these inputs. There are no repeated qualifying cut events per NDC/window, so the original event-row median currently equals the specified median of NDC minima.

Both existing chart images were visually inspected; their plotted patterns agree with the replicated CSVs. Their titles and comparator labels inherit the interpretation and classification issues below.

The mapping defects below are shared by the prescribed definitions and the original script. Part A deliberately retains them; [the sensitivity calculation](novolog_sensitivity.csv) is separate.

## Ranked findings and fixes

1. **High: NovoLog Mix is a false-positive selected drug.** `family()` accepts every name beginning `NOVOLOG `, including `NOVOLOG MIX 70-30` and its FlexPen. Their NDC products are absent from the CMS selected list; the [official label](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1861fcee-7673-4afe-a206-08fa05c0add2) identifies the premixed product and its distinct NDCs. Removing only those two names changes NovoLog from **-28.41% to -30.42%**, with claims 1,920,477 → 678,635. Then **10/10**, rather than 9/10, families fall at least 30%; pooled change becomes -61.69%. **Fix:** use a reviewed explicit alias crosswalk, exclude Mix, and regenerate all affected claims. This sensitivity does not resolve the omissions in item 3.

2. **High: “Other brands” is not a verified brand comparator.** Name inequality admits Abacavir versus Abacavir Sulfate, Albuterol Sulfate HFA versus Albuterol Sulfate, and Alprazolam ER versus Alprazolam. It also admits supplies such as Advocate Pen Needles. These are visible in [the mapping](partd_mapping.csv). **Fix:** obtain a product-level brand classification, exclude supplies and harmonize family aggregation, then rerun. Until then, label the group “unselected products with differing brand/generic name strings.” Its 1,088 count and +0.29% median cannot be presented as clean brand-only estimates.

3. **High: selected-product coverage differs between the Part D and NDC analyses.** The CMS selected file contains authorized-generic NDCs, including dapagliflozin `66993-0457-30` and insulin aspart FlexPen `73070-0103-15`. The name matcher drops Dapagliflozin and Insulin Aspart when both names are equal, but puts Insulin Aspart FlexPen in Other brands. The latter contributes 647,806 claims in 2025 and 68,844 in Q1. Penfill is similarly misassigned before failing the volume threshold. **Fix:** reconcile manufacturer/product names to the [CMS NDC list](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices). Where aggregate rows mix eligible and ineligible NDCs, report that unresolved scope rather than adding every same-ingredient generic.

4. **High: explain why gross PDE spending can already reflect MFP.** Gross cost includes ingredient cost, dispensing fees, sales tax and applicable vaccine administration fees, across plan and beneficiary payments, before manufacturer rebates ([quarterly methodology, p. 1](https://data.cms.gov/sites/default/files/2025-12/QDD_PTD_RQ2503_Methodology_508.pdf)). However, [SSA §1860D-2(d)(1)(D), as enacted](https://www.govinfo.gov/content/pkg/PLAW-117publ169/html/PLAW-117publ169.htm), caps selected-drug negotiated payment prices at MFP plus dispensing fees. [CMS DDPS edit 883](https://www.cms.gov/files/document/january-2026-updates-drug-data-processing-system-g.pdf) flags ingredient cost above unit MFP × quantity; it is informational, not an automatic rejection. **Fix:** say the decline is consistent with MFP-based payment rules. Gross does not mean the MFP reduction is absent, nor does this aggregate identify its causal contribution or prove universal compliance.

5. **High: NADAC gaps do not measure realized pharmacy losses or refund receivables.** The finding's headline overstates what the benchmark proves. Manufacturers can provide MFP prospectively or retrospectively; the MTF Data Module exchanges claim information, while its Payment Module is optional. Default refunds use WAC minus MFP, not NADAC minus MFP, subject to appropriate alternatives. The 14-day window starts at MTF transmission to the manufacturer and concerns payment transmission, not receipt after dispensing ([CMS final guidance, §§40.4–40.4.4, pp. 209–252](https://www.cms.gov/files/document/ipay-2028-final-guidance.pdf)). **Fix:** describe an invoice-benchmark gap before any retrospective refund. Cash-flow estimates require eligible quantities, actual acquisition/payment/refund dates, channel and 340B handling. Per-unit gaps multiplied directly by claim counts have the wrong units.

6. **Medium: WAC events and NADAC movements are partly the same measurement process.** Brand NADAC rates are adjusted by the percentage change in published prices and subsequently validated against surveys ([NADAC methodology, p. 23](https://www.medicaid.gov/medicaid-chip-program-information/by-topics/prescription-drugs/ful-nadac-downloads/nadacmethodology.pdf)). The Comparison file reports changes in **NADAC**, with WAC as the reason, rather than a separate WAC price series. **Fix:** retain the supported WAC-related interpretation, label it precisely, and avoid treating the two NADAC analyses as independent corroboration. Qualify “rare” as an NDC-weighted description of this changing universe; NDCs are not independent manufacturer decisions.

7. **Medium: net savings are not identified.** Confidential rebate changes, quantity changes and program financing prevent the claim that realized Medicare net savings necessarily equal a smaller version of this gross percentage decline. **Fix:** say “These data do not estimate net savings.” If context is needed, CMS estimated 22% aggregate net savings under a **2023 counterfactual**, not observed 2026 savings ([CMS fact sheet](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026)). Narrow “CMS does not publish net prices” to the absence of drug-level net spending in this dataset.

8. **Medium: mix and seasonality remain hypotheses, not decompositions.** The claim declines replicate, but fewer brand claims do not prove a changed patient base or quantify the mix contribution to spending per claim. Generic competition is documented for Entresto in Q3 2025 ([Novartis 20-F](https://www.sec.gov/Archives/edgar/data/1114448/000111444826000004/nvs-20251231.htm)); Stelara biosimilars were launched in 2025 ([manufacturer announcement](https://www.fresenius-kabi.com/news/continuing-biopharma-growth-with-us-and-eu-launch-of-ustekinumab-biosimilar)). **Fix:** replace the asserted compositional contribution with “may reflect mix and substitution.” A near-zero comparator median does not rule out seasonality, especially with item 2; pooled comparator spending rises 7.19%. Use earlier matched quarters and fixed product/quantity comparisons. Later-selected drugs are not validated untreated controls.

9. **Medium: units and changing NDC coverage need an auditable check.** No actual unit mismatch was demonstrated. CMS uses EA/ML/GM billing units ([guidance, p. 307](https://www.cms.gov/files/document/medicare-drug-price-negotiation-final-guidance-ipay-2027-and-manufacturer-effectuation-mfp-2026-2027.pdf)); NADAC uses those categories too. But the supplied MFP file and [layout definitions](https://www.cms.gov/files/zip/final-mfp-file-layout-definition-documents.zip) do not provide an explicit per-NDC unit field. **Fix:** document billing-unit concordance, especially injections and suspension. Xarelto's mixed EA/ML entries are not inherently erroneous because division precedes aggregation. Report unweighted NDC medians and coverage: 74 versus 75 NDCs, including Entresto's 7 → 8. Add a constant-NDC sensitivity. Change Imbruvica's explanation to “no matched NADAC observations”; absence alone does not establish its cause.

10. **Low: harden two currently harmless code paths.** `wac_january()` computes event-row medians rather than first reducing to one minimum per NDC; `nadac_vs_mfp()` selects the maximum year in all input data for “latest,” rather than explicitly restricting to 2026. **Fix:** reduce events by NDC/window before summarizing, restrict endpoint years and assert unique NDC/date keys and unique applicable MFP values. Current results remain correct. Label the October 21 snapshot as supplied, not as an October 20 observation.

11. **Low: qualify future work and selection labels.** The annual Part D file alone cannot supply an earlier Q1 baseline; use archived quarterly releases. Spending per dosage unit reduces days-supply variation but still mixes strengths/forms and requires standardization. A 2027 study can prospectively register remaining outcomes, while acknowledging already inspected 2026 results. Call the 2028 cohort “selected for negotiation,” rather than already negotiated: its MFP fields are empty in the supplied file, consistent with the [CMS selection chronology](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices).

## Part C: disposition of every finding and limit

| Write-up item | Numerical check | Wording assessment |
| --- | --- | --- |
| Finding 1 | All reported numbers match the fixed-rule replication. | Revise for findings 1–4 and 8 above. “Did not fall” is true of group medians, not every comparison drug. Linzess's timing matches, but causation is not isolated. |
| Finding 2 | All percentages and dates match. | Supported as WAC-related NADAC changes within the specified windows and retail NDC universe; add item 6's measurement caveat. |
| Finding 3 | All ratios match; the starting range rounds to 2.0–3.4. | Replace the actual-cost headline and unsupported distribution explanation, per items 5 and 9. It compares December with October, not just January. Januvia is essentially flat, with a tiny decline. |
| Gross, not net | Gross definition is correct; no net estimate was computed. | Remove the categorical net-saving inference; distinguish ordinary rebates from MFP-based payment. |
| Preliminary quarter | Three-month extraction statement is supported. | Retain. The [current CMS dataset page](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-quarterly-part-d-spending-by-drug) says extraction changed to three months from July 2026 and warns about revisions. This supersedes the older methodology PDF's six-month timing. Both periods here come from the quarterly file. |
| Mix, not only price | Entresto -86.50%, Stelara -43.77%, Farxiga -30.45% reproduce. | Retain as possible explanations, not a measured decomposition or patient-level result. |
| Full year vs one quarter | Period labels are correct. | Retain the limitation; remove reassurance based solely on the comparator median. |
| NADAC coverage and units | Retail coverage and chosen MFP dates are correct; unit equality is not fully verified. | Add unweighted NDC coverage, invoice-benchmark/refund distinction and explicit unit validation. |
| Not causal | No causal or out-of-pocket estimate was produced. | Supported and essential. Add anticipation, comparator contamination and selection into later cohorts. |

**Shortcuts taken:** no commercial NDC billing-unit database was obtained, so unit concordance remains partially verified. No clean brand-only comparator or claim-level causal estimate was manufactured from these aggregate files. These limits do not affect the fixed-definition replication.
