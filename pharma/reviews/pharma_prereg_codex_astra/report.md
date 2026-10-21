# Codex independent review: 2027 pharmaceutical preregistration

**Verdict: PASS WITH FIXES.** The baseline arithmetic replicates. The preregistration needs amendments to make its outcome rules unambiguous, especially P1's semaglutide exception and P3's qualitative claims. Do not interpret this verdict as a pass of the predictions themselves: no 2027 plan pricing outcomes were accessed.

Review date: 2026-10-20, America/New_York. Registration reviewed: `b24d4c8`, dated 2026-10-20T20:56:27-04:00. Reviewer: Codex, assigned Astra review. All review work is confined to `reviews/pharma_prereg_codex_astra/`. No commits, logins, website-term acceptance, or dataset downloads were performed.

## Independence and replication record

I wrote and ran `replicate.py` directly against local raw files, then saved `replication.md` before opening `pharma/prereg_2027.md`, any author script, or anything under `pharma/outputs/`. The Part A timestamp is 2026-10-21T01:00:14Z, which is 2026-10-20 in the working time zone. Part A used six raw files: the two permitted pricing archives, the MFP CSV, Part D quarterly spending, and the two NADAC CSVs. The frozen replication note mistakenly calls these seven; the enumerated inputs and code are correct.

After Part A, `check_comparison.py` reconciled 221 numeric cells against the author's outputs. The largest difference was $0.00000000000091, floating-point noise. `extended_checks.py` then independently reread the three local historical pricing archives, including **2025Q4, which contains plan-year 2026**, and the local 2025 NADAC file. All 75 drug-by-snapshot medians, row counts, within-MFP shares, and above-MFP shares agreed, as did December 2025 NADAC ratios. Neither script can select a 2027 plan-pricing archive. The input and reviewed-file hashes are in `review_manifest.json`.

## Part A: independently computed numbers

The rule is `1 / median(UNIT_COST / MFP_unit) - 1`, using all matched 30-day plan x segment x NDC rows with equal row weight. Superseded MFP rows are excluded; the corrected June 2026 Entresto Sprinkle MFP is used. Part D uses `Mftr_Name == Overall` and pools the selected brand families, including Enbrel devices, Fiasp Pumpcart and Austedo XR titration kits, but excluding NovoLog Mix and InPen supplies. Exact names are in `brand_mapping.csv`.

Fixed claim mix is a price index: `sum(baseline_claims * new_per_claim) / sum(baseline_claims * old_per_claim) - 1`. Equivalently, percentage changes receive baseline spending weights. Error is realized minus predicted, in percentage points. Every spending number below is gross.

## 2026 calibration

| Drug | r | Prediction % | Realized % | Error pp | 2025 $/claim | 2026Q1 $/claim | Matched rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ELIQUIS | 2.403119 | -58.3874 | -56.2640 | 2.1234 | 912.3142 | 399.0101 | 16721 |
| ENBREL | 3.438480 | -70.9174 | -70.7804 | 0.1370 | 8681.6348 | 2536.7401 | 23983 |
| ENTRESTO | 2.180282 | -54.1344 | -69.9562 | -15.8218 | 1077.5611 | 323.7403 | 25511 |
| FARXIGA | 3.173218 | -68.4862 | -67.0293 | 1.4569 | 997.7509 | 328.9655 | 10978 |
| IMBRUVICA | 1.722669 | -41.9505 | -39.9189 | 2.0317 | 16055.4616 | 9646.3037 | 29665 |
| JANUVIA | 2.707961 | -63.0718 | -61.5138 | 1.5580 | 556.0755 | 214.0121 | 16404 |
| JARDIANCE | 2.966900 | -66.2948 | -64.5499 | 1.7449 | 1091.1936 | 386.8292 | 11248 |
| NOVOLOG | 1.989688 | -49.7409 | -30.4241 | 19.3168 | 293.8035 | 204.4164 | 19089 |
| STELARA | 3.120436 | -67.9532 | -68.4251 | -0.4719 | 26682.0038 | 8424.8196 | 13446 |
| XARELTO | 2.837117 | -64.7529 | -62.8271 | 1.9259 | 1006.2108 | 374.0380 | 32674 |


Fixed 2025 claim mix: predicted -62.184889%; realized -61.374450%. Mean absolute drug-level error 4.6588 pp; maximum 19.3168 pp.

## 2027 cohort

| Drug | r | Prediction % | 2026Q1 $/claim | 2026Q1 claims | Gross removed, $m | Matched rows |
| --- | --- | --- | --- | --- | --- | --- |
| AUSTEDO | 1.683888 | -40.6136 | 8526.2792 | 74006 | 256.270351 | 50856 |
| BREO ELLIPTA | 5.685312 | -82.4108 | 535.2629 | 477136 | 210.471624 | 16120 |
| CALQUENCE | 1.674388 | -40.2767 | 14579.4461 | 49197 | 288.890507 | 5496 |
| IBRANCE | 2.015165 | -50.3763 | 15771.6047 | 43602 | 346.424347 | 21984 |
| JANUMET | 3.626331 | -72.4239 | 563.3744 | 230272 | 93.955080 | 23252 |
| LINZESS | 1.986037 | -49.6485 | 429.9901 | 670465 | 143.133190 | 16488 |
| OFEV | 2.125468 | -52.9515 | 13550.6618 | 51721 | 371.112802 | 3918 |
| OTEZLA | 3.239055 | -69.1268 | 5485.2146 | 62840 | 238.273765 | 18970 |
| OZEMPIC | 3.628883 | -72.4433 | 1417.5089 | 3358770 | 3449.088584 | 33030 |
| POMALYST | 2.701133 | -62.9785 | 23154.1226 | 21372 | 311.649007 | 9508 |
| TRADJENTA | 6.015458 | -83.3762 | 806.0406 | 292530 | 196.593534 | 5018 |
| TRELEGY ELLIPTA | 3.810245 | -73.7550 | 932.0863 | 1656431 | 1138.730003 | 10877 |
| VRAYLAR | 1.938442 | -48.4122 | 1559.8591 | 210833 | 159.213013 | 32976 |
| XIFAXAN | 3.253426 | -69.2632 | 3030.6940 | 111610 | 234.286681 | 8565 |
| XTANDI | 1.977230 | -49.4242 | 13812.7064 | 90089 | 615.021165 | 16488 |


Fixed 2026Q1 claim mix change: -63.400073%. Gross spending removed at Q1 volumes: $8,053,113,653.13, from $12,702,057,381.95 to $4,648,943,728.82.

## NADAC snapshot 2026-10-21

Only brand-classified NDCs in the latest global snapshot are used. Each NDC has equal weight. WAC cuts use Effective Date, Percent Change <= -20, and Primary Reason containing WAC.

| 2027 drug | NADAC/MFP | NDCs | WAC cuts since 2024 (date: range %) |
| --- | --- | --- | --- |
| AUSTEDO | 1.657543 | 12 | None |
| BREO ELLIPTA | 5.650074 | 5 | None |
| JANUMET | 3.635445 | 15 | 2025-01-01: -42.41 to -42.41 |
| LINZESS | 1.980967 | 3 | 2026-01-01: -50.27 to -50.26 |
| OTEZLA | 3.170688 | 4 | None |
| OZEMPIC | 3.595390 | 22 | None |
| TRADJENTA | 6.009500 | 3 | None |
| TRELEGY ELLIPTA | 3.804924 | 4 | None |
| VRAYLAR | 1.883633 | 10 | None |


Deselected 2026 drugs, NADAC / 2026 MFP:

| Drug | NADAC/MFP | NDCs |
| --- | --- | --- |
| ENTRESTO | 2.215230 | 8 |
| FIASP | 0.994848 | 4 |
| NOVOLOG | 0.996529 | 3 |
| STELARA | 3.322268 | 2 |
| XARELTO | 2.840470 | 19 |


The six IPAY 2027 drugs without a matched brand NADAC in the latest snapshot are Calquence, Ibrance, Ofev, Pomalyst, Xifaxan and Xtandi. Missing means unavailable, not zero. The median across the nine drug-level NADAC ratios is 3.595390.

## Six continuing 2026 drugs

| Drug | 2026 MFP / 30 days | 2027 MFP / 30 days | Change % |
| --- | --- | --- | --- |
| ELIQUIS | 231.00 | 237.25 | 2.705628 |
| ENBREL | 2355.00 | 2418.70 | 2.704883 |
| FARXIGA | 178.50 | 183.33 | 2.705882 |
| IMBRUVICA | 9319.00 | 9571.07 | 2.704904 |
| JANUVIA | 113.00 | 116.06 | 2.707965 |
| JARDIANCE | 197.00 | 202.33 | 2.705584 |


These are descriptive gross price predictions, without a causal or net-savings interpretation.

### WAC-cut base-rate reconciliation

The local NADAC Comparison file supports **4 of 10** selected drugs with a WAC-related cut of at least 20% in 2025-12-20 through 2026-02-28: Eliquis −43.00%, Jardiance −44.39%, Farxiga −37.00%, and Fiasp −75.00%, all on 2026-01-01. Since 2024 it supports **5 of 10**, adding Januvia's −42.41% cut on 2025-01-01. NovoLog's −75% cut on 2024-01-01 is in the same selected-drug family as Fiasp, so does not add a sixth family.

**The author's 5/10 and 6/10 are correct when external WAC evidence is included.** Imbruvica has no matched NADAC. [NCPA's notice](https://ncpa.org/wac-decreases-coming-take-action-now) supplies the 2025-12-22 date; [46brooklyn's original WAC analysis](https://dev-46brooklyn.squarespace.com/news/2025-year-in-review-and-2026-early-look-n84h9t) reports a 41.5% decrease in December 2025. The two sources together support its inclusion. This is a source-coverage difference, not a numerical error in the preregistration. It should be explicit because P3's future count is NADAC-only.

## Part B: numerical and factual reconciliation

**No substantive numerical disagreement was found in the computed baseline tables.** Predicted and realized drug-level changes, errors, per-claim spending, group changes, gross dollars removed, matched NADAC ratios, and the six inflation adjustments all agree beyond displayed rounding. The independent calibration gives eight errors within 2.1234 pp, with Entresto at −15.8218 pp and NovoLog/Fiasp at +19.3168 pp. The all-ten mean absolute error is 4.6588 pp; the eight-drug mean absolute error is 1.4312 pp. The aggregate error is +0.8104 pp.

| Factual claim | Independent check |
| --- | --- |
| Gabriel discounts by drug | All 14 estimable percentages match Table 1 of local `literature/ira_fulltext/text/paper_9.txt`, lines 273–628. Pomalyst is not estimable. The reported median 38% is correct. These estimates use 2022 net prices; the semaglutide estimate excludes Wegovy utilization, as explained at lines 1799–1812. |
| CMS discounts by drug | All 15 match page 2 of the [CMS IPAY 2027 fact sheet](https://www.cms.gov/files/document/fact-sheet-negotiated-prices-ipay-2027.pdf). They compare against 2024 WAC. The Janumet and Linzess explanation is consistent with their independently observed later WAC cuts. |
| Li et al. | Local `paper_10.txt`, Table 2, concerns modeled initial offers, not final MFPs or observed spending. It cannot independently validate the 1/r forecast. No incorrect Li number appears in the preregistration. |
| $245 semaglutide agreement | The [White House announcement](https://www.whitehouse.gov/fact-sheets/2025/11/fact-sheet-president-donald-j-trump-announces-major-developments-in-bringing-most-favored-nation-pricing-to-american-patients/) states $245 for Ozempic and Wegovy. The cited [KFF commentary](https://www.kff.org/quick-insights/understanding-the-trump-administrations-negotiated-drug-prices-for-medicare/) did describe the interaction as unclear on 2025-11-26. That historical statement does not establish how $245 enters Part D plan unit prices; see finding 1. |
| Wegovy has a separate package price | Confirmed: the CMS fact sheet gives $276.78 for the example Ozempic pen and Rybelsus pack, versus $385.63 for the example Wegovy pack. The replication correctly uses NDC-specific MFPs, rather than dividing every product by $274. |
| Four deselected drugs | Local valid MFP rows end on 2026-12-31, with superseded 2027 rows excluded. The [CMS selected-drugs page](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices) confirms removal on 2027-01-01 for Entresto, Stelara, Xarelto and the NovoLog/Fiasp family. |
| Tradjenta renegotiation | Confirmed by the [CMS January 2026 announcement](https://www.cms.gov/newsroom/press-releases/cms-announces-selection-drugs-third-cycle-medicare-drug-price-negotiation-program-including-first): renegotiated prices take effect in 2028. Keep Tradjenta in the IPAY 2027 treatment group, not the 2028 comparator. |
| Generic pomalidomide already present | Confirmed locally: the Overall row has 3700 claims and $46,888,635.64 of spending in 2026 Q1, separately from Pomalyst. |
| January 2026 P1 calibration | Independently replicated: 92.7476% of rows at MFP, 99.6505% weighted by 2025 drug-family claims, all ten medians within 0.5%. Stelara alone exceeds the 5% above-MFP cutoff, at 18.4559% of its rows. |
| Net-savings interpretation | No direct inference of net savings from the computed gross series. The text explicitly rules it out. Its universal gross-versus-net sentence and CMS benchmark qualification still need the corrections in finding 8. |

## Ranked findings and concrete fixes

### 1. High: P1's semaglutide exception overrides its primary test and assigns a cause the data cannot identify

**Location:** `pharma/prereg_2027.md:19–23`.

P1 requires every drug's median to lie in [0.995, 1.005], yet a semaglutide median anywhere below 0.95 is excused as the $245 agreement. That includes prices far below $245 and says nothing about how the exception affects the pooled 90% or claim-weighted 97% requirements. A lower price can comply with an MFP ceiling while failing a prediction that prices equal that ceiling.

The [CMS GLP-1 Bridge FAQ](https://www.cms.gov/medicare/coverage/prescription-drug-coverage/medicare-glp-1-bridge), updated 2026-07-13, says the Bridge runs outside Part D coverage/payment through December 2027 and that BALANCE is not launching in Part D in 2027. Thus the agreement's existence does not establish that its price will replace the MFP in these plan-price data. This is a channel distinction, not evidence that a lower Part D price is impossible.

**Fix:** retain the literal P1 equality test and score it unchanged, including semaglutide. Register a separate alternative-price analysis, specifying affected products, package/quantity conversion, expected ratio and tolerance. Below-MFP observations are descriptive evidence, not proof of the agreement's causal role. State separately whether all prices satisfy the ceiling and whether they equal it. Any exception must explicitly define its effect on every aggregate denominator.

### 2. High: freeze the scoring contract before opening the held-out release

**Location:** P1, P4, and scoring table, lines 17–23, 69–72, 78–86.

The first monthly CY2027 release and the January quarterly release both appear as tests without an explicit primary-versus-follow-up rule. P1 says all plan-product rows, while the calibration script filters to 30-day supply. P4 says brand products, while the existing SPUF matcher includes all listed NDCs, including unbranded products. NovoLog and Fiasp must be split for P4 despite their shared CMS family. Missing brand rows, withdrawn NDCs, revised MFPs, and conflicting subtests have no fixed handling.

**Fix:** name the 2026-10-08 monthly CY2027 release as the primary P1/P4 pricing test if that is the intention, and January as a separately scored replication, never a replacement. Freeze the NDC/MFP lookup and brand-only roster; define the unit as plan x segment x NDC at `DAYS_SUPPLY=30`; retain full-precision comparisons. Define claim-weighted coverage as `sum(claims_i * within_share_i) / sum(claims_i)`. Publish a subtest scorecard, with pass/fail/not-evaluable and an explicit rule for any overall P1–P5 verdict. Missing products must not silently disappear from denominators or count as passes. Apply this through a dated amendment because the registration commit already exists.

### 3. High: parts of P3 cannot be scored as written

**Location:** lines 60–63.

“More likely” assigns neither probabilities nor a comparison statistic. The sibling statement starts with all manufacturers but names tests only for Boehringer and GSK. It does not say how large a sibling cut must be. “Drugs that cut stay at or above” specifies neither the evaluation date nor whether every weekly observation must satisfy the condition. A single drug can contain several NDCs, formulations and brands; a count based on any NDC and one based on a majority of NDCs can disagree.

**Fix:** register each clause separately. For example, define a family cut as at least one frozen, brand-classified selected NDC with `Primary Reason` containing WAC and `Percent Change <= -20` during the inclusive window, counted once per family. Define “where” as a strictly higher cut proportion among Tradjenta/Breo/Trelegy than Vraylar/Austedo, or mark it exploratory. Limit the sibling test to the named pairs, specify a ≥20% WAC threshold and identical effective date, and mark it not evaluable if no triggering cut occurs. For the gap test, specify the final June snapshot, median over eligible NDCs, treatment of later cuts and missing rates, and exactly which seven or nine families are tested.

### 4. Medium: the 1/r rule is a useful forecast, but its aggregate target and calibration must be described more carefully

**Location:** lines 11–13, 27, 49–54.

An equal-row median unit-price ratio is not algebraically the change in gross dollars per claim. The latter also depends on quantity, strength, days supplied, plan mix and within-family formulation mix, plus noningredient components. The raw quarterly spending file has no quantity or days-supply adjustment. October plan prices are a point in time; the outcome denominator is a full-year spending average.

The semaglutide, pomalidomide and Austedo risks are already recorded correctly. The missing general risk is that these composition changes can affect every family, including P5's six continuing drugs. A January 2027 WAC cut is not an extra multiplicative discount on top of MFP if plan prices still land at MFP. If it brings a relevant price below MFP, the equality assumption fails. January 2026 Linzess changes are already largely present in the October 2026 reference, but Q1 versus full-year mix can still differ.

The eight-drug 2.1 pp statement is accurate after rounding, but those eight were selected after observing the two large misses. The full calibration MAE is 4.66 pp and its Spearman correlation is **0.7212**, below P2's proposed 0.8. The two outliers represent only **6.54% of baseline spending**, helping the group index look accurate; semaglutide alone is **37.48%** of the 2027 cohort's Q1 spending and **42.83%** of predicted dollars removed.

**Fix:** call this an unfit, descriptive forecast with stated stable-composition assumptions, rather than implying the trimmed error is its general predictive accuracy. Keep all 15 in the primary test and retain the preregistered bands; do not widen them after outcomes. Report MAE, all drug errors, exact ranks and the aggregate separately. Flag the rank criterion as more demanding than the historical calibration. Add prespecified brand-specific and matched-product sensitivities where the local data permit, without substituting them for the primary outcome. Describe Entresto's generic displacement as a plausible contributor, not a proven explanation for its per-claim residual: fewer claims alone does not establish changed cost per remaining claim.

### 5. Medium: P2's group forecast and comparison groups need fixed weights and membership rules

**Location:** lines 50, 53; `prereg_2027.py` fixed-mix calculation.

The published −63.4001% uses **2026 Q1** spending weights, whereas the text says fixed **2026** claim mix and compares 2026 full year with 2027 Q1. Once full-year per-claim prices and claims become available, these are different indices. The $8.053 billion is an illustrative reduction at Q1 prices and volumes, not an unconditional forecast of each 2027 quarter. “Other brands” also relies on heuristic exclusions and minimum-volume filters in the old analysis; it is not a naturally fixed control population. Related-brand cuts are explicitly predicted in P3 and can contaminate that comparator.

**Fix:** specify the weight period exactly. One consistent scoring choice is to retain Q1 claim weights for both observed and predicted full-year-denominator indices, then mechanically compute the predicted index as `sum(Q1_claims * FY2026_per_claim * prediction_i) / sum(Q1_claims * FY2026_per_claim)`. Precommit whether the ±5 pp group test remains centered on the fixed −63% headline or on that mechanically updated index; report the other as a sensitivity. Freeze comparator names, exclusions and minimum-volume/missingness rules. Keep Tradjenta out of the 2028 comparator and report named sibling drugs separately. Label $8.053 billion as a fixed-Q1-volume illustration.

### 6. Medium: P3's count band is broad, while its exact MFP floor is stricter than its own evidence

**Location:** lines 58–63.

Two to five cuts out of seven excludes only the extremes. As a scale check, under independent 50% cut probabilities, that interval has 87.5% probability; manufacturer clustering makes that model illustrative, not a fitted probability. The “stay at or above MFP” floor, however, would reject the cited Fiasp precedent: its independently calculated NADAC/MFP is **0.994848**. NADAC is an acquisition-cost benchmark, not a contractual floor.

**Fix:** keep the count interval as a coarse descriptive forecast and add prespecified family-level probabilities or explicitly call the location clause exploratory. Use an economically justified tolerance around the floor, for example 0.98 if chosen before outcomes, or retain 1.00 as a deliberately strict hypothesis and acknowledge that the Fiasp calibration fails it. Do not present the exact floor as established by the 2026 examples.

### 7. Medium: P4 is a falsifiable hypothesis about price rebound, not a consequence established by deselection

**Location:** lines 67–72.

Ending an MFP obligation does not mechanically force a return to the old list-related price. A plan can negotiate a low price without a WAC cut, change brand coverage, or have too few surviving brand claims for a stable comparison. NADAC can remain high despite negotiated plan discounts. Therefore the proposed WAC-cut explanation is one possible failure mechanism, not an exhaustive test of why P4 fails. A 50% increase per claim additionally depends on surviving users and quantities, not just per-unit prices.

**Fix:** replace “plans go back” with an explicit forecast conditional on the hypothesized contracting response. Keep the ≥1.5 pricing ratio and ≥50% spending thresholds as distinct tests. Predefine handling of dropped brands and low volumes. A WAC cut, continued plan discounting, coverage loss and compositional change should be separately reported mechanisms; none should rescue a failed primary threshold.

### 8. Low: qualify the net benchmarks and the universal comparison, and cite the mixed-source cut counts

**Location:** lines 52, 58.

The calculated gross falls exceed Gabriel's estimated net discounts for all **14 estimable drugs**, not all 15: Pomalyst has no estimate. They also use different periods, populations and weights, so the ordering is not a mathematical guarantee merely because list exceeds net. The [CMS fact sheet](https://www.cms.gov/files/document/fact-sheet-negotiated-prices-ipay-2027.pdf) supports 44%/$12 billion excluding Coverage Gap Discount Program spending and 36%/$8.5 billion including it. The preregistration omits that material qualification. The WAC counts are correct only after adding external Imbruvica evidence, as reconciled above.

**Fix:** say “The predicted gross decline exceeds the published net discount for each of the 14 drugs with an estimable net benchmark; these are different estimands.” Label Gabriel's benchmark as estimated 2022 net prices. Give both CMS definitions. Cite NCPA plus 46brooklyn for Imbruvica and distinguish the 4/10 local NADAC count from the 5/10 combined-source count. Preserve the existing statement that the gross series cannot test net savings.

## P1–P5 scoring and band judgment

| Prediction | Falsifiable now? | Judgment on the proposed bands |
| --- | --- | --- |
| P1 | Numerical clauses are clear individually; the semaglutide exception and primary-release rule prevent an unambiguous combined score. | ±0.5% is stringent but appropriate for reported schedule prices, given the independent 2026 calibration. The 90% pooled and 97% claim-weighted targets are plausible. Freeze population and exception handling. |
| P2 | Drug hit count, aggregate band and rank threshold are testable once the group weights and conjunction rule are fixed; comparator membership must be frozen. | Twelve of fifteen within ±5 pp is defensible as a forecasting target, not an estimated confidence band. The aggregate ±5 pp is broad against the old 0.81 pp group error but more defensible given semaglutide's weight. Spearman ≥0.8 is tighter than the all-ten calibration of 0.7212. |
| P3 | Count can be made testable; “where,” siblings and gap persistence need the definitions in finding 3. | Count 2–5 is weakly informative. The no-cut ratio ≥1.5 is a meaningful directional threshold. The cut-drug floor 1.0 is unnecessarily exact relative to acquisition-cost variability and its own Fiasp example. |
| P4 | The ≥1.5, 0.9–1.2 and ≥50% clauses are testable once brand membership, split insulin families and missingness are fixed. | These are strong directional forecasts without a prior deselection calibration. Keep failures as failures and label mechanism explanations separately. |
| P5 | Yes at the per-drug level, using the stated full-year 2026 versus 2027 Q1 comparison. A joint score needs an explicit all-six rule and missingness policy. | −3% to +6% around a 2.7% MFP increase allows roughly −5.7/+3.3 pp of composition drift. It is plausible but not empirically calibrated for six continuing drugs; report each result without post hoc exclusions. |

## Completion and limits

The requested independent baseline and review are complete. Reproducible calculations, the frozen Part A note, numeric comparisons and raw-input hashes are beside this report. The registration already exists, so fixes should be recorded as amendments before any held-out pricing file is opened. I did not edit the registration or any source file.

**Shortcuts taken:** public policy pages and published analyses were read for factual verification, but no new dataset was fetched. The Imbruvica cut magnitude is verified against 46brooklyn's published analysis, not its underlying licensed WAC database. The proposed monthly-release parser and future scoring logic were reviewed conceptually, not executed against 2027 prices, as required. No clinical, utilization or causal explanation was independently established from claims-level data, which are not supplied here.
