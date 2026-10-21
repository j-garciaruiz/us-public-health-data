# Independent site review

Reviewed 2026-10-20, using the supplied brief. **Overall: FAIL pending corrections.** Site files were not modified. All input hashes remained unchanged during the review.

## Verdict per requested check

| Check | Verdict | Evidence |
| --- | --- | --- |
| 1. Number fidelity and exporter | **FAIL** | All exported arrays and findings match their CSV inputs at the exporter's declared precision. However, premature rounding changes displayed values, and the coverage statement confuses geometry with available observations. |
| 2. Claims | **FAIL** | Reconstruction, local explanations, review coverage and recommended uses need the qualifications below. |
| 3. NCHS disclosure rule | **PASS for the current site** | Every non-null published mortality observation traces to at least 10 deaths. Suppressed/missing cells have no exported observation, expectation, shrunk residual, reliability, tier or expected-death note. The exporter's purported safety assertion is nevertheless inadequate. |
| 4. Atlas behavior | **FAIL** | 336 ordinary outcome/mode/smoothing/view combinations pass the consistency checks. Overlapping outcome loads can silently display the wrong dataset. Standardized-layer extremes are mislabeled as reliable. |
| 5. Accessibility and robustness | **FAIL** | Keyboard county search works, controls have labels, and pages/data work from disk. Sorting is mouse-only; one dark-mode button fails text contrast; 320-pixel layouts overflow; file loading emits font-preload console errors. |

Tests used project Python Playwright and **Chromium headless shell 145.0.7632.6**, not installed Chrome. No uncaught JavaScript exceptions occurred. HTTP browsing produced no console errors in this run; `file://` produced the font errors documented in finding 10.

## Independently checked numbers

The audit performs **1,396,084 comparisons**, with zero mismatches against declared export precision, across **210,720 county/outcome/mode CSV rows**. County IDs, names, state labels, geometry membership, null positions, national/within-state mapping, tiers, reliability, peer counts, discrepancy flags and notes were checked. Geometry array order need not match sorted data order: the browser's FIPS lookup correctly joins them.

| Item | Independent result and rendered result |
| --- | --- |
| Big percentage | Crude-measure median CV R² = **0.962**, rendering **96%**. The static HTML fallback says **97%**. The age-adjusted CSV median is **0.9715**, consistent with the review summary's approximately 97.1% result, but it is not the series the page currently charts. |
| Maximum PLACES increment | Recomputed `max(R²_both − R²_demo)` = **0.02284560956**, or **2.284560956 percentage points**, rendering **2.3**. It is Medicare asthma in the larger-county sample. All 42 comparisons favor the demographic/state baseline over PLACES alone. |
| First chart | All **40** dot values and county counts match the crude-measure CSV. Uninsurance labels **98%, 72%, 84%** match their inputs: 0.978, 0.717 and 0.839. The benchmark counts are **2,956** and **1,485**. |
| Second chart | All **21** plotted comparison rows match the CSV's `all` sample. Both chart tables were inspected alongside their underlying exported values. |
| Caddo diabetes mortality | CSV measured **452.2534**, expected **144.7363** SMR × 100; page **452 vs 145**, or **4.5 vs 1.4** times the national age-mix expectation. |
| Iberia diabetes mortality | **38.1809 vs 165.9042** SMR × 100; page **38 vs 166**. |
| Staten Island diabetes claims | **44% vs 27.9313%**; page **44% vs 28%**. |
| Brooklyn diabetes claims | **43% vs 29.1641%**; page **43% vs 29%**. |
| Atlas size | **34 layers** = 12 actual Medicare + 12 standardized Medicare + 6 ACS + 4 mortality. Geometry has **3,144** counties; the largest usable outcome has **3,143**. |

The atlas's ordinary table rows, extremes membership/order and displayed values agree with its serialized data across all 336 tested states. Diverging domains are symmetric around zero. Measured and expected views share the same observed-data sequential domain within an outcome. Missing values are hatched, not colored as zero. Fading changes low-tier opacity to 0.28 and returns all counties to opacity 1 when disabled. Both ramps clamp their tails: sequential at the 2nd/98th percentiles, diverging at the 98th percentile of absolute difference. Legend numbers match those limits; they are not full data minima/maxima.

URL pinning, search, Escape clearing, extremes-button pinning, mouse sorting and an actual keyboard search were exercised. Standardized Medicare correctly exports tier 0, no estimated reliability, and disables smoothing/fading; its raw-difference behavior is correct apart from display rounding and the misleading extremes heading.

## Findings, most important first

### 1. High: an earlier outcome request can overwrite the currently selected outcome

**Location:** `site/assets/atlas.js:251–260`, especially 255–257; also change handler at 70.

Reproduction: delay `atlas_acs_vision_difficulty.js` by one second, select vision difficulty, then immediately select actual Medicare diabetes. The final selector and title say diabetes, but Caddo shows **5.5% measured / 4.7% expected**, the ACS vision data, including `MOE +/- 0.54`. Correct Medicare diabetes values are **29.0% / 29.7%**. The map, table, details and extremes all consume the shared stale `data` variable. This fails silently, without a JavaScript exception.

**Fix:** capture the requested outcome ID and a monotonically increasing request token before awaiting the load. Commit the returned data, hide loading status and render only if both still match the current selection/request. Ignore stale failures too. Hide stale tooltips and prevent old data being rendered against the new metadata while a request is pending. Add a regression test that deliberately resolves two outcome requests in reverse order.

### 2. High: the reconstruction headline omits state and the text implies an exact rerun of PLACES

**Location:** `site/index.html:45–50`; `site/assets/index.js:21–25,60–61`.

“Rebuilt from demographics” drops the state term that substantially improves fit. “Those same inputs” implies replication of CDC's individual-level multilevel/poststratification model; these are approximate county covariates and state indicators. “Recovers almost every map” is stronger than a high median R². The live headline also silently uses crude rather than age-adjusted measures.

**Exact replacement heading:** “Demographics and state reproduce most variation in published PLACES estimates”.

**Exact replacement paragraph:** “Across 40 crude-prevalence measures, county demographic covariates plus state indicators reproduce a median 96.2% of variation in held-out counties. This approximates the inputs to PLACES; it does not rerun CDC's model or show that the underlying health differences are artificial. Census-measured uninsurance is less predictable in this comparison, partly because of sampling error.”

Label the big caption and chart explicitly as crude prevalence, and change the HTML fallback to 96%. If the intended headline is the reviewed age-adjusted result, switch the chart and bound statistic together to that series. CDC's methodology includes survey information and state/county random effects, not demographics alone. [CDC methodology](https://www.cdc.gov/places/methodology/index.html)

### 3. High: the Louisiana example invents adjacency and implies an identified recording mechanism

**Location:** `site/assets/index.js:153,159`; introductory atlas explanation in `site/index.html:26`.

Caddo and Iberia are not neighboring parishes; their topology has no shared boundary arcs. Their large difference does not establish that death certificates are recorded differently. Likewise the NYC example cannot identify how much diagnosis intensity or coding explains. The review summaries permit these as possible explanations, not empirical decompositions of the residuals.

**Exact replacement for the end of the Louisiana paragraph:** “Iberia Parish, elsewhere in Louisiana, records 38 against 166 expected. The contrast could reflect differences in disease, certification practices or other factors; this analysis does not distinguish them.”

**Exact replacement for the NYC closing sentence:** “Disease, access to care, beneficiary composition and diagnosis or coding practices may all contribute; this analysis does not separate them.”

**Add beside the atlas introduction:** “Differences are descriptive comparisons with model predictions, not estimates of preventable disease or county performance.”

### 4. Medium: rounding during export changes displayed numbers before final formatting

**Location:** `scripts/export_site_data.py:97–107`; `site/assets/atlas.js:44–50`; `site/assets/common.js:53–57`.

The exporter rounds mortality values to one decimal and other values to two; the browser then rounds again and computes raw differences from the rounded operands. Native D3 formatting of the source CSV values versus the serialized values produces **20,309 differing observed/expected/shrunk display cells**, counting county-mode rows, plus **10,676 differing raw-difference displays**. These are small last-digit errors, not failed FIPS joins or major statistical disagreements.

For Coffee County, Alabama, actual arthritis in national mode, the CSV has measured 42, expected **36.5508**, raw difference **5.4492**. Direct formatting gives **36.6%** and **+5.4 pts**; the site displays **36.5%** and **+5.5 pts**. The latter is reproducible in county details and propagates to other readouts. Intermediate rounding also creates artificial ties in rankings.

**Fix:** export the available CSV precision for observation, expectation and shrunk difference, plus the CSV's raw `difference` explicitly. Round only at the final display boundary, and rank using the retained values. Check details, tooltips, tables and extremes against formatted CSV values, rather than merely against the serialized arrays.

### 5. Medium: the process narrative exceeds the documented scope of independent review

**Location:** `site/index.html:94–99`.

“Every number”, “each analysis” and “every one was fixed” describe a comprehensive independent clearance that the artifacts do not establish. The earlier expected-vs-observed Codex report explicitly excludes the four mortality comparisons added during that review. The atlas review reused existing covariates and CMS extracts. Review summaries retain spatial/temporal validation and uncertainty limitations. A summary saying fixes were applied is not evidence that every current page value was independently rebuilt from raw sources and reverified.

**Exact replacement introduction:** “Independent Codex and Agy reviews reconstructed specified analyses and checked their methods. Their findings led to corrections in county matching, suppression, prediction and smoothing; the review summaries describe the scope and remaining limitations.”

**Replace the Replicate description:** “Codex independently reconstructed the analyses within each review's stated scope, then audited the implementation.”

**Replace the Fix description:** “Documented implementation findings were corrected; unresolved methodological limitations are listed below.”

Link the relevant review summaries, and identify this site audit separately from raw-data replication. The listed historical bug examples, including four negative expectations and the approximately 1.9% covariance bound, are supported by the review record; it is the universal completion claim that fails.

### 6. Medium: prediction and usage guidance need scope, metric and population qualifiers

**Location:** `site/index.html:57–58,69–89,131–133`.

The 2.3 value is correct, but “accuracy” should identify cross-validated R² and the tested outcomes. Medicare models include Medicare Advantage share. The page's blanket avoidance of demographic regression and ranking individual measures goes beyond these tests; CDC warns about interpretation and disallows overall-health ranking, while allowing comparisons of individual measures. Planning/needs assessment is a supported intended use, not something this reconstruction study validated. Claims and deaths are not substitutes for adult self-reported prevalence merely because they are measured.

**Replace the second finding's subtitle:** “In these 21 outcome comparisons, demographics plus state, and Medicare Advantage share for Medicare, predict the recorded outcomes better than PLACES alone. Adding PLACES increases cross-validated R² by at most 2.3 percentage points across the 42 outcome-sample comparisons.”

**Replace the usage heading:** “Using PLACES with its limitations”. Keep planning and needs assessment, citing CDC. Replace the regression bullet with “Interpreting associations with demographic inputs or other PLACES measures as independent evidence without accounting for how the estimates were modeled.” Replace the ranking bullet with “Treating modeled differences as precise rankings of overall county health.” Keep the warning against evaluating local interventions from PLACES alone. [CDC FAQs](https://www.cdc.gov/places/faqs/index.html)

**Replace the measured-source advice:** “Prefer suitable direct local estimates when they measure the same outcome, population and period with adequate precision. Claims and mortality can provide complementary evidence, but are not interchangeable with adult prevalence estimates.”

**Replace the method's expected-value bullet:** “Expected values use cross-fitted regression on county demographics, with optional state indicators and Medicare Advantage share for Medicare; mortality uses Poisson regression.” Clarify smoothing with: “Empirical Bayes smoothing uses source-specific uncertainty estimates; Medicare denominators are approximate, and age-standardized Medicare is not smoothed.”

### 7. Medium: availability and reliability labels promise more than the data provide

**Location:** `site/assets/index.js:163–165`; `scripts/export_site_data.py:150–151`; `site/atlas.html:76`; `site/assets/atlas.js:186–198`.

The 3,144 count is geometry coverage. Loving County, Texas (48301), has no observations in any exported outcome; actual layer coverage ranges from 2,909 to 3,143. “Each ... a reliability rating” fails for all 12 standardized Medicare layers. Their extremes include tier-0 counties while the heading says “reliable counties”. Also, “only within the county's own state” overstates a pooled model with state effects and a documented fallback when no state peer exists.

**Replace the atlas example:** “34 outcome layers cover up to 3,143 counties, depending on the source. Compare measured values with predictions from demographics, with or without state indicators. Reliability is shown where it can be estimated; age-standardized Medicare has no reliability estimate.”

**Fix:** calculate available-county coverage from the observed rows, retaining 3,144 separately as map coverage. For standardized Medicare, change the extremes heading to “Largest raw differences; reliability not estimated” or withhold rankings until uncertainty is available. For other layers, “Largest differences, high or moderate estimated reliability” accurately describes the tier filter.

### 8. Medium: the exporter's stated NCHS assertion does not enforce the death-count rule

**Location:** `scripts/export_site_data.py:15–16,55–58`.

The only mortality assertion requires `observed` to be non-null. Executing that exact assertion on a synthetic zero mortality observation passes. It never checks the underlying death count or suppression flag. This is **not a current disclosure**: the independently checked inputs and all current site assets pass suppression, including the expected-death notes that could otherwise permit `SMR / 100 × expected deaths` reconstruction.

**Fix:** join mortality rows to the suppression-aware count source using canonical FIPS and cause; require a finite count of at least 10 and `suppressed == False` before exporting any observation, expectation, residual or expected-death note. Reject unsafe input rather than trusting a non-null SMR. Test zero, counts 1–9, suppressed and missing counts. Do not include forbidden counts in public failure artifacts.

### 9. Medium: keyboard sorting and one text-contrast combination fail basic accessibility

**Location:** `site/assets/atlas.js:216–220`; `site/assets/site.css:108`.

All six sortable headers are click-only `<th>` elements with `tabIndex = -1` and no buttons. Actual Tab traversal reaches the scrolling container but cannot activate a sort. Other native controls, keyboard search and the table disclosure work. County/plot hover interactions lack keyboard handlers, but the search/details route and chart data tables provide alternative access to values.

The dark-theme “Open the atlas” button uses white 16-pixel text on `#2a78d6`, measured contrast **4.415:1**, below 4.5:1. Other sampled visible text combinations passed the basic light/dark check.

**Fix:** put a native button inside each sortable header, attach the existing sort handler to it, and keep `aria-sort` on the header. Use `#1c5cab` or another verified darker background for the dark-mode CTA while retaining white text. Verify with keyboard-only operation and contrast measurement.

### 10. Low: narrow layouts overflow, and disk mode emits avoidable font errors

**Location:** `site/assets/site.css:89–96,148–153`; `site/assets/index.css:99`; `site/index.html:8`; `site/atlas.html:8`.

At a 320-pixel viewport, the project page is **336 pixels** wide and the atlas **332 pixels** wide because the nonwrapping brand and navigation exceed the header. At 390 and 1,440 pixels, no page overflow was found.

Both pages and outcome switching work over `file://`, but the unconditional crossorigin font preload emits a CORS error, `net::ERR_FAILED`, and an unused-preload credentials warning. These are resource errors, not JavaScript exceptions.

**Fix:** let the header wrap or stack at narrow widths and ensure the index-specific navigation gap does not override that breakpoint. Add the font preload only on HTTP(S), or remove the optional preload and let the CSS font request/fallback handle disk viewing. Recheck 320-pixel reflow and both file URLs without disabling browser security.

## Mortality disclosure coverage

I joined exported mortality slots to the raw WONDER county/cause extract, independently accounting for **02270 → 02158** and **46113 → 46102**. Published counts were eligible in all four layers: diabetes **2,909**, heart disease **3,118**, cerebrovascular **2,995**, lower respiratory **3,025**; the smallest supporting count in each was **10**. Missing/suppressed cells had no mortality-derived export values or expected-death notes. No suppressed count was reconstructed.

The check included every file under `site/`, not just visible controls: the 34 outcome scripts, findings, both geometry copies, HTML/JS/CSS, vendor/font assets, and the design log/reference image. The design image is a generated composition reference, not an additional mortality dataset. The site contains expected-death notes only for eligible published mortality cells. The applicable rule covers rates based on nine or fewer deaths as well as counts. [NCHS data-use restrictions](https://wonder.cdc.gov/datause.html)

## Reproduction and retained evidence

Run from the project root:

```sh
.venv/bin/python reviews/site_codex_astra/audit_data.py
.venv/bin/python reviews/site_codex_astra/browser_audit.py
.venv/bin/python reviews/site_codex_astra/supplemental.py
```

`data_results.json` records CSV/export comparisons. `browser_results.json` records all 336 states, interactions, race reproduction, contrast and console messages. `supplemental_results.json` and the two `d3_*_rounding_discrepancies.csv` files preserve native-browser rounding and layout results. The earlier `rounding_discrepancies.csv` is a Python diagnostic; the D3 files are authoritative for browser formatting. `suppression_guard.json` demonstrates the weak exporter guard. Screenshots, input hashes and final verification are retained in this folder.

## Shortcuts taken

- This is a site-to-reviewed-output audit, not another fit of all statistical models from raw inputs. I recomputed displayed aggregates and checked every exported array against the CSVs; raw WONDER counts were checked separately for disclosure eligibility.
- Full table/extremes/legend/hatching checks cover all 336 ordinary states. Tooltip interaction, keyboard flow, failure timing and disk loading use targeted cases rather than every possible event ordering. The reverse-load race uses a deliberate one-second delay.
- Accessibility testing is a focused Chromium keyboard, labels, computed-color and layout audit, not a screen-reader or full WCAG conformance certification. Contrast sampling excludes hidden content and does not certify every antialiased chart mark.
- Only Chromium headless shell was exercised. File-mode functionality passed despite font-preload warnings; Safari, Firefox, real mobile devices and an offline cache were not tested.
- No site fixes, deployments, Git commits or changes outside the assigned review folder were made. No additional model was asked to approve this independent review leg.
