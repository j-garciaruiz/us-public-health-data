# Verdict: PASS WITH FIXES

The underlying reported calculations pass this check. The HTML does not yet faithfully summarize the registration: it changes semaglutide's failure threshold, obscures the scope of P4, omits other registered tests, and incompletely describes the scoring amendments. Several background and interpretation statements also exceed their evidence. Correct the wording before circulating the page as fully checked.

Reviewed `pharma/report/index.html`, its template, build script and amendment fragment on 2026-10-20. All changes and review artifacts are confined to `reviews/pharma_report_codex_astra/`. No 2027 plan pricing or outcome data were opened or downloaded. Published MFP benchmarks, preregistered predictions, historical outputs through 2026 and source-catalog metadata were permitted inputs. No commits were made.

## Ranked findings

### 1. High: the patient description incorrectly puts premiums under the out-of-pocket cap

**Location:** Background, player table, Patient row (`template.html:183`).

**Problem:** “Pays premium, deductible and copay or coinsurance, up to an annual cap” implies the $2,000/$2,100 cap includes premiums and all prescription spending. It applies to qualifying out-of-pocket spending for covered Part D medicines; premiums are separate.

**Evidence:** `literature/ira_fulltext/text/paper_2.txt:37–45` explicitly excludes premiums. The [CMS 2026 benefit description](https://www.cms.gov/newsroom/fact-sheets/2026-medicare-advantage-part-d-advance-notice-fact-sheet) confirms the $2,100 threshold. The amounts themselves are correct.

**Exact replacement:**

> Pays a separate premium, plus any deductible and copayments or coinsurance. Qualifying out-of-pocket spending on covered Part D medicines is capped at $2,000 in 2025 and $2,100 in 2026; premiums do not count toward the cap.

### 2. High: Amendment 1 changes semaglutide's registered equality tolerance

**Location:** Looking ahead, Amendment 1 (`prereg_note.html:2`).

**Problem:** “A semaglutide median below the MFP is a fail of P1” changes the lower threshold from 0.995 to 1.000. For example, 0.998 passes the registration but fails this sentence. It also fails to state the upper limit.

**Evidence:** `pharma/prereg_2027.md`, P1 and Amendment 1, “P1, semaglutide”: the interval is 0.995–1.005, and the withdrawn exception concerns a ratio below 0.95. The ceiling check is separate from equality.

**Exact replacement of the sentence beginning “The semaglutide escape clause”:**

> The semaglutide exception is withdrawn: its median ratio must lie between 0.995 and 1.005, inclusive, just like every other 2027 drug. A ratio below 0.995 or above 1.005 fails the equality test. Compliance with the MFP ceiling is reported separately. Medicare's $50-copay GLP-1 Bridge operates outside Part D coverage and payment through 2027.

The Bridge context is supported by [CMS's program description](https://www.cms.gov/medicare/coverage/prescription-drug-coverage/medicare-glp-1-bridge).

### 3. High: P4 broadens the spending-rise prediction and loses the NovoLog/Fiasp band

**Location:** Looking ahead, prediction table, P4 row (`template.html:341`).

**Problem:** After naming all four departing families, “brand spending per claim rises at least 50%” reads as applying to all of them. The registered rise applies only to Entresto, Xarelto and Stelara. “Stay near it” omits NovoLog and Fiasp's explicit 0.9–1.2 band. The page also omits Amendment 1's evaluability threshold and its warning that deselection does not force a price rebound.

**Evidence:** `pharma/prereg_2027.md`, P4; Amendment 1, “P4, a hypothesis, not a consequence”; Amendment 2, “P4 and P5 baselines.”

**Exact replacement for the P4 expectation cell:**

> This tests a return to higher prices; deselection does not require it. For brand Entresto, Xarelto and Stelara separately, the median plan-price ratio is at least 1.5 times the 2026 MFP, and gross spending per claim rises at least 50% from full-year 2026 to 2027 Q1. NovoLog and Fiasp are tested separately for plan-price ratios of 0.9–1.2 times the 2026 MFP; the 50% spending-rise prediction does not apply to them. Unbranded products are excluded. A brand with no plan-price rows or fewer than 1,000 claims in 2027 Q1 is not evaluable. Failure of a threshold remains a failure even if a possible mechanism is identified.

### 4. Medium: the P1 and P3 summaries omit registered tests entirely

**Location:** Looking ahead, prediction table, P1 and P3 rows.

**Problem:** P1 omits the per-drug limit on above-MFP rows. P3 omits the same-day sibling test and the strict 1.00 gap floor for drugs with a cut. Its June endpoint is absent. None of these appears elsewhere in the rendered page, so readers cannot reconstruct all the registered clauses.

**Evidence:** `pharma/prereg_2027.md`, P1 and P3; Amendment 1, “P3, definitions.”

**Exact replacement for the P1 expectation cell:**

> Each of the 15 drugs has a median plan-price/MFP ratio of 0.995–1.005. At least 90% of all plan-product rows, and at least 97% after weighting drug-specific shares by 2026 Q1 claims, are within 0.5% of their own MFP. No drug has more than 5% of rows above 1.005 times its MFP. Each of the six continuing drugs also has a median ratio of 0.995–1.005 against its inflation-adjusted 2027 MFP, approximately 2.7% above its 2026 MFP.

**Exact replacement for the P3 expectation cell:**

> Of the seven NADAC-covered families without an earlier cut, 2–5 have a WAC-based NADAC reduction of at least 20%, effective from 2026-12-20 through 2027-02-28 inclusive. A family counts once if at least one eligible brand NDC meets the rule. A Tradjenta cut must coincide with a Jentadueto cut; a Breo or Trelegy cut must coincide with a cut to Anoro, Incruse or Arnuity. The sibling cut must also be WAC-based and at least 20%, on the same effective date; without a triggering cut, that test is not evaluable. In the last June 2027 NADAC snapshot, each family's median brand-NDC ratio to its 2027 MFP must be at least 1.5 without a family cut and at least 1.00 with one. A 0.98 floor is a sensitivity only. The comparison of cut frequencies across the named high- and low-ratio groups is exploratory, without pass/fail scoring.

### 5. Medium: the scoring amendment summary does not specify the registered estimand and subsets

**Location:** Looking ahead, P2/P5 rows, prediction caption and both amendment paragraphs.

**Problem:** “Fixed claim mix” omits the fixed **2026 Q1** weights and **full-year 2026** denominator. The $8.1 billion illustration lacks Amendment 1's explicit non-forecast qualification. “A 2028 comparator without drugs that cut list prices” expands Amendment 2 beyond the specified WAC-based, at-least-20%, dated window. The fragment omits the restored $178.50 Farxiga value and describes the Fiasp fix as a row being dropped, rather than a previously omitted row being restored. The primary release should be defined by its content, with January stated as an expectation.

**Evidence:** `pharma/prereg_2027.md`, Amendment 1, “Scoring contract” and “P2, weights and comparators”; Amendment 2. Recalculated group prediction is −63.400073%, and the Q1 illustration is $8.053114 billion. Thus the chart's rounded **−63.4%** and **$8.1 billion** are valid, not arithmetic discrepancies. Xifaxan's 2.80-to-3.25 increase is about 16%; a smaller decline against a full-year baseline is directionally consistent with the amendment. “Understate” should describe that different baseline, not imply the registered estimand is wrong.

**Exact replacement/additional scoring paragraph:**

> The primary plan-price test uses the first CMS release containing plan-year 2027 unit prices, expected in January 2027; later releases are replications. Rows are contract × plan × segment × NDC with a 30-day supply, evaluated at full precision against the frozen 2026-10-20 MFP file after dropping superseded rows. P2 fixes each drug's weight at its 2026 Q1 claim count: the observed group index is sum(Q1 2026 claims × 2027 Q1 spending per claim) / sum(Q1 2026 claims × full-year 2026 spending per claim) − 1. Its registered pass interval remains −68% to −58%. Recomputing the predicted index with the full-year 2026 per-claim baseline is a sensitivity. The approximately $8.1 billion gross reduction holds both 2026 Q1 prices and volumes fixed; it is not a forecast of 2027 spending. P4 and P5 also compare full-year 2026 with 2027 Q1, with Q1-to-Q1 results reported separately.

**Exact replacement for Amendment 2's “Applied” sentence:**

> Applied: the missing Fiasp row was restored and Farxiga's 2026 MFP was corrected to $178.50. Five sensitivities were specified: a Q4-only 2026 baseline for all 15 drugs, calculated by subtracting Q3 year-to-date spending and claims from Q4 year-to-date totals; separate Ozempic and Wegovy results, while keeping the pooled semaglutide prediction primary; brand-only plan-price shares, while retaining every listed NDC against its own MFP in P1; a 2026 Q1 baseline for P4 and P5; and a 2028 comparator excluding drugs with WAC-based cuts of at least 20% effective from 2026-12-20 through 2027-02-28. Xifaxan's ratio rose from 2.80 to 3.25 during 2026, so its decline against the full-year baseline is expected to be smaller than the registered October-based prediction of −69%. Trulicity accounts for 42% and Anoro Ellipta for 13% of the 2028 comparator's 2026 Q1 claims.

### 6. Medium: the pharmacy explanation guarantees recovery of a gap that was not measured

**Location:** Background, negotiation-program paragraph; Finding 3 callout.

**Problem:** “Made whole” and “refunded the difference” imply realized, complete reimbursement of the invoice-cost/MFP gap. This study does not measure acquisition costs or refunds for individual eligible transactions. The default basis is WAC minus MFP, not NADAC minus MFP. The MTF payment service is optional; not every refund passes through it.

**Evidence:** `pharma/ira_findings.md`, Finding 3; [CMS final guidance, sections 40.4–40.4.4](https://www.cms.gov/files/document/ipay-2028-final-guidance.pdf); [CMS MTF fact sheet](https://www.cms.gov/files/document/pharmacy-dispensing-entity-mtf-fact-sheet.pdf). CMS's operational average of refunds sent within 21 days is supported, but it is not a guarantee for each pharmacy.

**Exact replacement in Background:**

> Manufacturers can provide access to the MFP prospectively or through retrospective refunds. The default refund uses WAC minus MFP, with permitted alternatives. The MTF exchanges claim data and offers an optional payment service. CMS reports that refunds were being sent to designated bank accounts within 21 days of service on average; this does not establish that every pharmacy recovered its actual costs.

**Exact replacement for the first two sentences of the Finding 3 callout:**

> This is a gap between an invoice benchmark and the MFP, not a measured pharmacy loss or refund receivable. Manufacturers must provide MFP access for eligible transactions, but these data do not show actual refund amounts, receipt dates or acquisition costs for those transactions.

### 7. Medium: the calibration explanation promotes plausible mechanisms to established causes

**Location:** Looking ahead, rule paragraph and calibration caption.

**Problem:** “The two misses have known causes” says more than the descriptive analysis establishes, especially “Entresto lost most claims to generics.” Brand claims fell, but the analysis does not trace patient switches or decompose the prediction error. The eight-of-ten result also needs to say the two cases were identified after observing the misses.

**Evidence:** `pharma/ira_findings.md`, mix and noncausal limitations; `pharma/prereg_2027.md`, Amendment 1, “P2, honest calibration.” The all-ten MAE, fixed-mix comparisons and 0.72 rank correlation are reproduced correctly.

**Exact replacement for the calibration description:**

> Applied retrospectively to the 2026 drugs, the rule missed by at most 2.1 percentage points for eight of ten. The two large misses were identified after examining the results: Entresto's brand claims fell sharply after generic entry, and the NovoLog family pools differently priced NovoLog and Fiasp products. These are plausible explanations, not an identified decomposition of the errors. Across all ten, mean absolute error was 4.7 points; the fixed-2025-claim-mix prediction was −62.2%, compared with −61.4% observed.

**Exact replacement caption:**

> Hollow points mark the two cases flagged after examining the calibration errors. Both remain in the all-ten error summaries. All 15 drugs remain in the primary 2027 test.

### 8. Medium: “Ozempic” labels present pooled semaglutide results as a single brand's result

**Location:** Hero chart, plan-price chart, prediction chart, their tooltips, and “All fifteen” table.

**Problem:** The displayed Ozempic row includes pooled Part D spending for Ozempic, Rybelsus and Wegovy. The October plan-price prediction is also a pooled family result, distinct from the brand-specific values cited in Amendment 2. The registration states this explicitly, but the HTML does not explain its Ozempic label. NovoLog's pooled scope is explained in Finding 1, but its chart labels could likewise be explicit.

**Evidence:** `pharma/prereg_2027.md`, P2 known risks and Amendment 2; `predictions_2027.csv`, OZEMPIC row. Pooled ratio is approximately 3.63 and prediction −72.4%; Ozempic-only ratio is 3.66 and prediction −72.7%, while Wegovy is 3.33 and −69.9%. Rybelsus has no October plan-price rows.

**Exact replacements:** Use **“Semaglutide (pooled)”** for `OZEMPIC` labels and **“NovoLog/Fiasp”** for pooled `NOVOLOG` labels. Add beside the relevant charts/table:

> Semaglutide spending pools Ozempic, Rybelsus and Wegovy. The October 2026 plan-price ratio pools the observed Ozempic and Wegovy rows; Rybelsus has no rows in that file. The pooled prediction remains primary. NovoLog/Fiasp spending combines those two brands.

Do not rename the separate NADAC-only NovoLog series to NovoLog/Fiasp: that chart already has distinct NovoLog and Fiasp lines.

### 9. Medium: several literature summaries omit consequential population or outcome qualifiers

**Location:** “What others have found” table, discount, patient, access and pharmacy rows.

**Problem:** The discounts lack their net-price years and international **list-price** qualifier. The $685/$470 model is for people without low-income subsidies, not all patients. “Access fell” does not identify Zheng's formulary-coverage outcome. The >85% loss is projected margin/revenue net of acquisition cost on the **selected drugs in 2027**, not an 85% decline in all long-term-care pharmacy margins.

**Evidence:** `paper_4.txt`, Methods/Results; `paper_9.txt`, Methods/Results; `paper_2.txt`, Methods/Findings; `paper_11.txt:399–414,569–570`; `paper_16.txt`, executive summary. Zheng's original [article](https://doi.org/10.1093/haschl/qxag171) reports enrollment-weighted coverage of 59 brands in 16 classes, from 47.4% to 35.6% in PDPs; the checked full text is saved as `zheng_fulltext.txt`. The numerical magnitudes are correct.

**Exact replacement for the discount cell:**

> Round-one MFPs were 8%–42% below estimated 2021 US net prices (Wouters et al.). For the 14 round-two drugs with estimable net prices, MFPs were a median 38% below estimated 2022 US net prices, with a 15%–60% range. Across the round-two drugs, MFPs were a median 108% above average purchasing-power-adjusted 2025 list prices in 19 reference countries (Gabriel et al.). These are benchmark comparisons, not measured net savings in 2026 or 2027.

**Exact replacement for the patient cell:**

> For beneficiaries without low-income subsidies, a model using 2026 plan designs estimated average annual out-of-pocket reductions across six drugs of $685 in stand-alone plans and $470 in Medicare Advantage plans. In the model, users of Stelara, Imbruvica and Enbrel reached the $2,100 cap with either price scenario. These are modeled comparisons, not observed patient savings (Castle et al., Annals).

**Exact replacement for the Zheng sentence:**

> Across 59 non-selected brands in 16 competitive classes, enrollment-weighted formulary coverage fell 11.8 percentage points in stand-alone plans, from 47.4% in 2024 to 35.6% in 2026. This measures coverage, not realized treatment access or a causal effect of negotiation (Zheng et al.).

**Exact replacement for the pharmacy cell:**

> NCPA reports pharmacy owners' refund delays. Bhardwaj et al. project a reduction exceeding 85% in long-term-care pharmacies' revenue net of acquisition cost on selected drugs in 2027 under their reimbursement assumptions. Courtemanche projects lower net revenue from the 340B program. These are survey reports and projections, not measured financial losses.

### 10. Medium: “none were above” silently substitutes a tolerance test for the literal ceiling

**Location:** Finding 4 prose; table columns “Below” and “Above.”

**Problem:** Above/below categories use a ±0.5% tolerance, not literal comparisons with 1.000. The sentence “By October 2026, none were above” is therefore too strong. The findings file itself notes a maximum approximately 0.003% above, attributed to rounding.

**Evidence:** `pharma/ira_findings.md`, Finding 4; `pharma/outputs/spuf/summary.md`; the displayed shares match `ratio_by_group.csv` exactly.

**Exact replacement:**

> In January, 92.7% of observed plan-product ratios were within 0.5% of the MFP, 4.9% were below 0.995 and 2.3% exceeded 1.005. All rows exceeding 1.005 were unbranded ustekinumab products grouped with Stelara. By October, no ratio exceeded 1.005; the maximum was only about 0.003% above 1.000, consistent with rounding.

Rename the table columns **“Below 0.995”** and **“Above 1.005.”**

### 11. Low: the NADAC chart caption implies the MFP was in force during 2025

**Location:** Finding 3 chart subtitle and caption.

**Problem:** The chart starts in January 2025, while the caption says “MFP in effect on each date.” Before 2026, the denominator is the future 2026 MFP, not an effective price. “A value of 1 means pharmacies buy at the negotiated price” also turns a median of invoice benchmarks into a statement about individual transactions.

**Evidence:** `pharma/scripts/ira_analysis.py:124–127` uses each NDC's earliest valid 2026 MFP before 2026; after that it uses the date-valid MFP. The embedded series correctly ranges from 2025-01-01 to 2026-10-21 and remains within the plotted y-axis.

**Exact replacement subtitle:**

> Median NADAC/MFP ratio across each drug's brand NDCs. A value of 1 means the median invoice benchmark equals the MFP; it does not establish any individual pharmacy's acquisition cost. Pick a drug to highlight.

**Exact replacement caption:**

> NADAC weekly files joined by NDC to the CMS MFP file. The 2025 observations use each NDC's earliest valid 2026 MFP as a future-price benchmark. From 2026, the denominator is the MFP effective on the snapshot date, including the Entresto Sprinkle correction from 2026-06-01. No NADAC observations match Imbruvica.

### 12. Low: the cut-event table claims completeness beyond its source coverage

**Location:** Finding 2, “Every large cut in the three groups of selected drugs.”

**Problem:** The table has only the nine selected-family events captured by the NADAC windows. It cannot include Imbruvica's independently documented cut, which the adjacent prose correctly reports. “Every” overstates its coverage. The table also always uses the longer window, even when the chart is switched to January only.

**Evidence:** `wac_cut_events.csv`; `ira_analysis.py:94–100`, which retains event rows for the December 20–February 28 window; [NCPA's notice](https://ncpa.org/wac-decreases-coming-take-action-now) and the literature review for Imbruvica.

**Exact replacement heading:**

> Large WAC-based cuts captured by NADAC in the selected-drug groups

**Exact added caption:**

> This table uses the December 20–February 28 windows labeled 2024, 2025 and 2026, independently of the chart's window selector. It includes products classified as brands in a January snapshot. It excludes cuts without NADAC coverage, including Imbruvica's 2025-12-22 cut.

### 13. Low: rounded tooltip endpoints are labeled as exact pass boundaries

**Location:** Registered-predictions chart tooltips (`chartPred()` in the template).

**Problem:** The bars use the unrounded prediction ±0.05, but the tooltip rounds both bounds to whole percentages and calls them “pass.” Tradjenta displays “pass −88% to −78%,” while its plotted bounds are −88.376162% to −78.376162%. An observed −78.1% is inside the displayed interval but outside the plotted interval. This is a reporting precision problem, not a failure of the bar geometry.

**Evidence:** `predictions_2027.csv`, TRADJENTA row; `render_checks.json`, `tooltips.chartPred`; `template.html`, tooltip interpolation in `chartPred()`.

**Exact replacement tooltip pattern:**

> Predicted {prediction to one decimal}%. Scoring tolerance: ±5 percentage points around the unrounded prediction. Approximate displayed bounds: {lower to one decimal}% to {upper to one decimal}%.

For Tradjenta this becomes:

> Predicted −83.4%. Scoring tolerance: ±5 percentage points around the unrounded prediction. Approximate displayed bounds: −88.4% to −78.4%.

Keep the statement that the cohort clause requires at least 12 of 15 drugs to meet the band.

### 14. Low: the page overstates verification and blurs two dates

**Location:** Hero verification line; “How it was checked”; Background Medicare row; preregistration opening paragraph.

**Problem:** “Every number was independently replicated ... from the raw files” includes external literature figures and operational claims that were source-checked rather than replicated from the original study data. “All fixes are applied” is too broad given the report defects above. The Background row says negotiation began in 2026, although the first prices were negotiated in 2024. “Before opening any 2027 file” should refer to plan-pricing/outcome files, because the work deliberately used published 2027 MFP benchmarks.

**Evidence:** The verification table itself distinguishes raw-data work from literature fact-checks and identifies pieces without an Agy review. Earlier review reports support the 8,542 comparisons, 1,508,521 matched pricing rows and 221 preregistration values. The [CMS first-round announcement](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026) dates the agreement to 2024 and effect to 2026. Registration commit `b24d4c8` is confirmed, timestamp 2026-10-20T20:56:27-04:00.

**Exact replacement hero verification sentence:**

> The project's data analyses were independently replicated from the raw files; cited research and policy claims were checked against their sources. The verification section describes the scope of each review.

**Exact replacement opening and closing claims in the verification paragraph:**

> Codex independently recomputed the project's analysis outputs from raw files before reviewing the analysis code and wording. Agy recomputed headline figures and reviewed methods. Literature findings were checked against publications, not independently re-created from their underlying study data. The table records the reviews completed for each component; those reviews do not by themselves certify every later summary sentence.

**Exact replacement Medicare row:**

> Pays most Part D costs through the plans and negotiates prices for selected drugs; the first negotiated prices took effect in 2026.

**Exact replacement registration phrase:**

> before examining any plan-year 2027 pricing or outcome data

## Checks that passed and remaining boundaries

- **Embedded values:** 2,491 numeric or categorical comparisons passed against the designated output CSVs, including all 950 weekly NADAC records, 75 plan-price drug/snapshot records, 25 spending records, 24 cut-window/group records, nine selected-family cut rows, ten calibration rows and 15 prediction rows. `numeric_audit.json` records the comparisons, recomputed aggregates and reviewed-file hashes. This is output-to-page verification, not a new raw-data replication.
- **Registration arithmetic:** All 15 point predictions, displayed ratios, Gabriel discounts and CMS list-price discounts agree with the baseline. Recomputed all-ten MAE is 4.6588 points, Spearman correlation 0.7212, calibration fixed-mix prediction −62.1849% versus −61.3745% observed, and the 2027 fixed-Q1-mix prediction −63.4001%. The 37% semaglutide spending share is a valid whole-percent rounding of 37.4828%. The 0.8 rank threshold, 12-of-15 rule, ±5-point tolerance and −68% to −58% group interval remain intact in the main table. Findings 2–5 identify the omissions and misstatements elsewhere.
- **Interpretation:** The page repeatedly and correctly says its spending results are gross, not net, and its design is noncausal. It does not calculate net savings from the 45% rebate share. The CMS and Jeon numbers are correctly distinguished as external counterfactual/projection benchmarks. Findings 6–9 address narrower overstatements that survive those general disclaimers.
- **Charts:** All six rendered without JavaScript errors. Data values fit their axes. Finding 1 uses signed percentage change; Finding 2 uses product shares and the selected window; Finding 3 uses weekly per-NDC benchmark ratios; Finding 4 uses a log axis and the correct three snapshot labels; calibration uses predicted x and observed y; prediction bars use ±5 percentage points, not confidence intervals. Screenshots are saved beside this report. Both window controls, all ten NADAC selectors, sortable-table headers and theme switching executed. Findings 8 and 10–13 concern labeling and interpretation, rather than corrupted chart data.
- **Links:** All six data/source links returned HTTP 200. CMS catalog metadata confirms both CMS data landing pages. Medicaid metadata confirms that the supplied NADAC UUID is the 2026 dataset; “NADAC Comparison” is plain text, not a second link. If made clickable, its verified catalog identifier is `a217613c-12bc-5137-8b3a-ada0e4dad1ff`. All 13 DOI identities match the stated authors/topics, confirmed through Crossref metadata, with the six initial rate-limit failures resolved in a follow-up. Several publisher destinations returned HTTP 403, so universal unauthenticated full-text access is not established; these are not demonstrated broken DOIs. See `link_audit.json`, `doi_metadata_followup.json`, `catalog_metadata.json` and `cms_metadata.json`.
- **Other source checks:** The MedPAC rebate share, NCPA refund-survey magnitude, CMS average refund timing, statutory-program dates as summarized, list-cut dates, main literature magnitudes and preregistration commit are supported by the reviewed sources. Claims framed as results of the scoping scan remain scan findings, not proof that no other study exists.

**Shortcuts taken:** This review reconciled the page with the existing reviewed outputs instead of repeating the prior raw-data replications. DOI identity was verified through registry metadata where publisher access was blocked. The browser render blocked all network requests, so it could not retrieve prohibited data. Desktop charts were visually inspected; a 390-pixel automated probe detected horizontal page overflow, but this fact-check did not perform a mobile redesign or a comprehensive accessibility audit. No source-page edits were made because the task limits writes to the review folder.
