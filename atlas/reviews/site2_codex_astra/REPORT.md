# Focused verification of site fixes

Reviewed 2026-10-20. **11 findings fixed; 7 partly fixed; none wholly unchanged. Further corrections are needed before treating the site audit as closed.** These counts refer to the original 18 findings, including their overlaps, not 18 independent defects.

The original reverse-load race and atlas rounding errors are fixed. The regenerated mortality exports pass the disclosure check. Remaining issues include a loading-time table exception, worse dark-button contrast, rounding in the project-page comparison chart, and several qualifications in the copy.

Only review artifacts were written in `reviews/site2_codex_astra/`. The main test pass had stable input hashes. A later concurrent change added a two-line embedded-data shortcut in `site/assets/common.js`; I identified the exact change and reran the loading and file-mode checks against it. Their verdicts are unchanged. The other previously hashed inputs remained unchanged, and I made no site edits. Browser: project Playwright **1.58.0**, **Chromium headless shell 145.0.7632.6**, with normal browser security. No real Chrome was used.

## Status of all original findings

C refers to `reviews/site_codex_astra/REPORT.md`; A refers to `reviews/site_agy_argon/REPORT.md`. “Fixed” assesses the original defect, not every possible behavior in that component.

| ID | Original finding | Status | Current evidence and remaining work |
|---|---|---|---|
| C1 | Earlier outcome request overwrites the selected outcome | **Fixed** | `atlas.js:260–276` checks request tokens and clears the shared data while loading. Delaying vision difficulty by one second, then choosing Medicare diabetes, leaves the selector, title and Caddo values correctly on diabetes: **29.0% / 29.7%**. A stale failed request also leaves the current result intact. A separate table interaction during loading still throws, finding N1 below. |
| C2 | Reconstruction headline omits state and implies an exact PLACES rerun | **Fixed** | `index.html:44–49` now says demographics **plus state**, identifies **40 crude-prevalence measures**, uses **96%** in both fallback and rendered headline, gives **96.2%** in the paragraph, and explicitly disclaims rerunning CDC's model or proving artificial health differences. CSV median independently recomputed as **0.962**. |
| C3 | Louisiana adjacency and unsupported recording/coding explanation | **Fixed** | `index.js:155,161` now says “elsewhere in Louisiana” and treats disease, care, certification, beneficiary composition and coding as possible contributors that the analysis does not separate. `index.html:64` disclaims preventable disease and performance interpretations. Rendered Caddo/Iberia and NYC values remain correct. |
| C4 | Premature rounding changes atlas displays and raw differences | **Fixed** | `export_site_data.py:107–121` retains four-decimal CSV precision and exports `raw`; `atlas.js:47` consumes it. **855,168** numeric/null comparisons and **768,478** non-null native-D3 display comparisons across all 34 layers and both modes found **zero mismatches**. Coffee County now shows **36.6% expected / +5.4 pts** in details, tooltip and table. Project-page rounding is a separate remaining occurrence, N2. |
| C5 | Independent-review narrative exceeds documented scope | **Partly fixed** | `index.html:94,97` now limits reconstruction to each review's stated scope. However, line 99 still says “Documented problems were corrected”; no review reports or summaries are linked, and site verification is not distinguished from analysis replication. See N6. |
| C6 | Prediction and usage guidance lacks metric/population/method qualifiers | **Partly fixed** | The 0.8/2.3 sample distinction, Medicare Advantage covariate, direct-source comparability, Poisson model and approximate Medicare uncertainty are present. The prediction paragraph still calls R² “prediction accuracy” in unspecified “points” and says “all counties.” See N3. The revised usage advice is materially more defensible; CDC's FAQ supports planning uses and cautions about intervention evaluation and overall-health ranking. |
| C7 | Geometry coverage and reliability labels overpromise | **Fixed** | Recomputed coverage is **2,909–3,143 counties**, **34 layers / 22 distinct outcomes**. The rendered card says “layers,” gives the observed-data range, and exempts standardized Medicare from reliability. All 12 standardized layers render “Largest raw differences (reliability not estimated).” State mode now says state indicators, rather than only in-state comparisons. |
| C8 | NCHS assertion does not enforce the death-count rule | **Partly fixed** | The actual guard at `export_site_data.py:62–68` now joins FIPS/cause, requires at least 10 deaths, an explicit false suppression flag and a non-null observation. It rejects synthetic zero, every count 1–9, suppressed rows, missing counts/flags/matches and missing observations; 10 passes. **Positive infinity still passes**, so the requested finite-count check is incomplete. Add `np.isfinite(chk["deaths"])` to the predicate. This is a synthetic robustness defect, **not a current disclosure**. |
| C9 | Mouse-only sorting and dark-button contrast | **Partly fixed** | Six native header buttons now support Tab, Enter and Space, retain focus and update `aria-sort`. All six keys sorted **3,106 rows** correctly in both directions. The dark CTA now uses white on **#86b6ef**, only **2.110:1**, worse than the former 4.415:1. `site.css:107–108` contains an inaccurate comment claiming #1c5cab in both themes; the dark token overrides it. Set `.btn-primary { background: #1c5cab; color: #fff; }` or an equivalently tested button-specific token: **6.628:1**. |
| C10 | 320-pixel overflow and file-mode font errors | **Fixed** | Both pages have `scrollWidth === innerWidth` at **320, 390, 768, 1024 and 1440 pixels**. Both `file://` pages render 3,144 county paths with **zero console errors/warnings and zero page exceptions**; atlas outcome switching also passes. Unconditional preloads are gone. |
| A1 | Static 97% becomes 96%; crude/adjusted series unclear | **Fixed** | Static and rendered headlines are **96%**. Caption, paragraph and chart identify crude prevalence; paragraph shows **96.2%**. Same evidence as C2. |
| A2 | Louisiana geography, unit switching and causal attribution | **Fixed** | The card explains the mortality index and 100 baseline, removes adjacency, and explicitly leaves competing explanations unresolved (`index.js:153–155`). Caddo **452 vs 145**, Iberia **38 vs 166**, and Caddo **4.5 times** agree with the CSV. |
| A3 | 2.3-point gain is outside the plotted sample; MA covariate omitted | **Fixed** | `index.html:57` separates **0.8** in the plotted sample from **2.3** in larger counties; `index.js:137` and the paragraph include Medicare Advantage share. Recomputed maxima are **0.7929708** and **2.2845610** percentage points of R². The metric and coverage wording still need the C6/N3 correction. |
| A4 | County/reliability/outcome counts and hero-map smoothing mislabeled | **Partly fixed** | Coverage, reliability exception, “34 layers” and “smoothed difference” are corrected. The hero caption still gives no mortality-index unit; “Diabetes deaths” can be read as counts. See N5. |
| A5 | Reconstruction heading omits state; PLACES effects and missing-state coverage omitted | **Partly fixed** | The principal reconstruction overclaim is fixed, including the explicit approximation/rerun disclaimer. However, measure-dependent coverage is still absent from the narrative; chart 1 uses **2,299–3,143 counties**, and “all counties” elsewhere is not national completeness. N3 supplies exact scope wording. There is no need to restore the second reviewer's stronger “rebuild nearly every map” suggestion. |
| A6 | Uses, meaning of expected, and NYC example mislead practitioners | **Fixed** | State comparisons were removed from the use list. Direct estimates must match outcome, population, period and precision. Both pages reject performance interpretations. The NYC card identifies Original Medicare, MA enrollment and competing explanations. The method describes prediction using other counties, rather than a clinical target. |
| A7 | CDC shortcodes and unexplained statistical jargon | **Fixed** | All **40** chart-1 measures have readable labels in the rendered table and tooltips. Held-out prediction and smoothing now have plain-language explanations; technical terms are secondary. “Centering step” remains technical but is confined to the historical bug list, not the explanation readers need to interpret the results. |
| A8 | Widows and weak heading breaks | **Partly fixed** | The hero and previously flagged last-word widows are resolved at the five tested widths. The new finding-1 heading ends a line in **“the”** at 1440/1024/768/390 pixels, and in **“and” / “the”** at 320. The Caddo heading breaks after **“in”** at 320. No em dashes found in page HTML or application JS/CSS. Exact, tested replacements are in N7. |

## Targeted verification evidence

Reproduce from the project root:

```sh
.venv/bin/python reviews/site2_codex_astra/verify.py
.venv/bin/python reviews/site2_codex_astra/followup.py
.venv/bin/python reviews/site2_codex_astra/loader_recheck.py
```

- [`results.json`](results.json) records numeric comparisons, the actual-guard synthetic tests, current mortality eligibility, race success/failure tests, the pending-table exception, layouts, console checks, all 68 outcome/mode text captures and index tooltips.
- [`loader_recheck_results.json`](loader_recheck_results.json) records the concurrent two-line loader change and the successful rerun of the reverse-load/stale-failure and file-mode checks; the pending-table exception remains reproducible.
- [`followup_results.json`](followup_results.json) records contrast ratios, independently recomputed headline statistics, all six keyboard sorts in both directions and proposed heading line breaks.
- [`index_visible_text.txt`](index_visible_text.txt) contains the rendered index, including both expanded chart tables. I read this in full, all generated tooltip text, the HTML/JS alternatives for narrow screens, and the atlas lede, labels and every outcome's about panel. Copy issues found in that pass are below.
- Screenshots include [`index_320.png`](index_320.png), [`atlas_1440.png`](atlas_1440.png), [`atlas_320.png`](atlas_320.png) and [`index_dark.png`](index_dark.png). Heading assertions also use actual DOM text-range positions after fonts load.

Current mortality exports were joined independently to the raw WONDER county/cause extract, with the Alaska and South Dakota FIPS renames. Eligible published observations: **2,909 diabetes, 3,118 heart disease, 2,995 cerebrovascular, 3,025 lower respiratory**. Minimum supporting published count: **10** in each layer. Ineligible slots have no observation, expectation, raw/shrunk residual, reliability, tier, discrepancy flag or expected-death note. No small count was reconstructed or copied into this report. The governing [NCHS restriction](https://wonder.cdc.gov/datause.html) covers rates as well as counts of nine or fewer.

## New findings and remaining copy corrections

Seven items below, including residual wording from the original findings. Existing contrast and finite-count fixes are specified in the status table and are not counted again.

### N1. Medium: opening the table while an outcome loads throws an exception

**Location:** `site/assets/atlas.js:207–212,266,287`.

After loading the initial map, delay `atlas_acs_vision_difficulty.js` by one second, select it, then open “All counties as a table” before it resolves. `load()` sets `data = null`; the disclosure's `toggle` listener calls `table()`, which calls `val()` without a guard. Chromium reports **`Cannot read properties of null (reading 'nat')`**. The table recovers when the request completes, so this is not a persistent wrong-data display or the original overwrite race.

**Correction:** guard the table's loading state, clear or explicitly mark stale table content, and defer table rendering until the current request commits. While pending, use **“Loading the selected outcome. The table will appear when it is ready.”** Exercise opening and sorting an already-open table while a request is pending.

### N2. Low: the project-page chart/table still double-rounds two visible values

**Location:** `scripts/export_site_data.py:178`; `site/assets/index.js:129–131,141`.

The atlas fix does not extend to `places_vs_observed`, which still uses `.round(4)` before D3 formats percentages. The current all-counties chart/table/tooltip display:

| Cell, PLACES-alone R² | CSV | Current display | Correct direct CSV display |
|---|---:|---:|---:|
| High blood pressure, Medicare | 0.5524566870225895 | 55.3% | **55.2%** |
| Depression, Medicare | 0.0804897859312213 | 8.1% | **8.0%** |

A third mismatch, **55.5% instead of 55.4%** for the larger-sample depression baseline, exists in serialized data but is not currently plotted. These are last-digit errors, not changes to the substantive result.

**Correction:** serialize those source R² values without intermediate rounding; format only in the browser. Exact displayed replacements are **55.2%** and **8.0%**. The 0.8/2.3 headline maxima remain correct.

### N3. Medium: name R² and qualify the comparison samples

**Location:** `site/index.html:57`; `site/assets/index.js:74,97,139`; narrative beside chart 1.

“Prediction accuracy” and “points” do not identify the statistic. “Across all counties” is also too broad: these comparisons use matched complete cases, not every US county. The first chart has measure-specific geographic coverage, and its uninsurance benchmark compares PLACES ages 18–64 with ACS ages 19–64.

**Replace the finding-2 paragraph with:**

> Across 21 recorded outcomes, demographics plus state, and Medicare Advantage share for Medicare, predict held-out county values better than PLACES alone. Adding PLACES increases cross-validated R², the share of county variation predicted, by at most 0.8 percentage points in the full available samples shown below and 2.3 percentage points in the restricted samples.

**Add immediately below:**

> Each comparison includes counties with all required data. The restricted samples require at least 5000 Original Medicare beneficiaries, 20,000 adults for Census outcomes, or 100 expected deaths for mortality outcomes.

Those thresholds come directly from `expected_vs_observed.py:164–172`; the mortality restriction concerns expected deaths, not population size.

**Replace chart 2's axis caption with:** “Share of county variation predicted in held-out counties (cross-validated R²; full available samples)”. Use **“Census, full available sample”** and **“Census-measured uninsurance, full available sample”** in chart 1's corresponding tooltip and table row.

**Add to the chart-1 explanation:**

> Coverage varies by measure, from 2,299 to 3,143 counties; these results describe counties with available data. The uninsurance comparison uses PLACES ages 18–64 and Census ages 19–64.

This keeps the supported reconstruction finding while exposing its scope. CDC's [methodology](https://www.cdc.gov/places/methodology/index.html) also identifies survey information and county/state random effects; the site's new “approximates” disclaimer appropriately avoids claiming their exact reproduction.

### N4. Low: atlas model labels still omit or overgeneralize inputs and coverage

**Location:** `site/atlas.html:24,40–44`; `site/assets/atlas.js:18,128`; `site/assets/index.js:167`.

The lede and layer-card sentence still describe the prediction as demographics alone; Medicare uses MA share too. The about panel states that covariate for actual Medicare but omits it for standardized Medicare. “Estimated across all states” is literally inaccurate for mortality, which excludes Connecticut. “CMS does not publish” is broader than the verified limitation of the extract used here.

**Replace the atlas lede with:**

> Each county's recorded value is compared with a model prediction from county demographics, plus Medicare Advantage share for Medicare and optional state indicators. Differences are descriptive, not estimates of preventable disease or county performance.

The short mode buttons can remain if accompanied by **“Both modes also include Medicare Advantage share for Medicare outcomes.”** Show that sentence only for Medicare.

**Replace the third example's expected-value sentence with:**

> Predictions use county demographics, plus Medicare Advantage share for Medicare, with or without state indicators.

**Replace the national-mode sentence template with:**

> Expected from [the existing covariate list], using models fit on other available counties without state indicators.

**Replace the standardized-Medicare caveat with:**

> Recorded diagnoses, age-standardized by CMS. The extract used here lacks the age-specific inputs needed to estimate uncertainty, so reliability is not estimated and differences are not smoothed. The prediction model includes Medicare Advantage share.

### N5. Low: mortality and difference labels should identify the displayed quantity

**Location:** `site/index.html:36`; `site/assets/atlas.js:133–139,211`.

The hero's smoothing correction is welcome, but “Diabetes deaths” still lacks units. In the atlas, the title says “measured minus expected” and the table says “Difference” even when those views show the smoothed residual; the county details separately use “Difference” for the raw residual. The values are correct, but the same label names different quantities.

**Replace the hero caption with:**

> Diabetes mortality, 2018–2024: smoothed difference from the model prediction, in mortality-index points (SMR × 100).

**Add a short explanation:**

> For measured and predicted values, an index of 100 represents national age-specific death rates applied to the county's age mix. A difference of zero means the measured and predicted indices match.

For the atlas, use **“[Outcome]: smoothed difference from expected”** when smoothing is on, and **“[Outcome]: measured minus expected”** otherwise. Change the table column to **“Smoothed difference”** or **“Raw difference”** accordingly, and the corresponding county-detail raw row to **“Raw difference”**. In mortality mode, replace “Points of the mortality ratio” with **“Mortality-index points (SMR × 100)”**.

### N6. Low: review completion is still too categorical and its evidence inaccessible from the page

**Location:** `site/index.html:94,99`.

The scoped reconstruction wording is now sound. However, “Documented problems were corrected” still implies closure of all findings, which this verification does not support. The page refers readers to reports without linking them. Its three listed limitations also do not exhaust the review summaries, which retain validation, coverage and uncertainty limitations.

**Replace the Correct description with:**

> The reviews led to the corrections illustrated below. Remaining implementation and methodological limitations are documented in the review reports.

**Add beside the process description:**

> Statistical replication and website verification are separate checks. Each report states the data, calculations and interface behavior it examined.

Link the two analysis `REVIEW_SUMMARY.md` files and the site review reports through paths included in the eventual site or repository delivery. Do not claim public availability until those links resolve in that delivery. The historical examples of bugs caught are supported by the existing review records.

### N7. Low: two heading breaks still violate the typography rule

**Location:** `site/index.html:48`; `site/assets/index.js:154`.

Actual font-loaded layouts, rather than static guesses, show the weak breaks recorded under A8. These replacements were tested temporarily in the browser at **320, 390, 768, 1024 and 1440 pixels**, with no lone last word, weak terminal word or page overflow:

```html
<h2 id="f1-title">Demographics + state<br>explain most<br>PLACES variation</h2>
<h3>Diabetes deaths:<br>Caddo&nbsp;Parish, Louisiana</h3>
```

The site files were not changed. The rest of the targeted headings passed the sampled line-break checks.

## Shortcuts taken

- This was a focused fix verification, not a new statistical replication or full site review. I compared all atlas observation/expectation/raw/shrunk arrays with the existing CSV and independently checked raw WONDER disclosure eligibility; I did not refit the models or rerun the previous 336-state interaction matrix.
- The actual exporter guard was extracted by AST and executed in memory with synthetic rows. The exporter itself was not run, because it writes outside the authorized review folder. The synthetic infinity case is not evidence of any unsafe current mortality cell.
- Actual county detail/tooltip/table formatting was spot-checked with Coffee County; every atlas numeric display value was additionally compared through browser-native D3. Keyboard sorts covered all six columns in both directions on one 3,106-row layer, not every layer.
- Browser testing used Chromium headless shell only. The concurrent embedded-data shortcut was checked on the requested multi-file pages, including repeated cached outcome switches; this review does not certify a separate single-file build. Five viewport widths, computed contrast and real keyboard events do not constitute a full WCAG or screen-reader audit. The file-mode console check covered initial loading and one outcome switch, not an extended offline session.
- Copy was checked against current files, CSVs, review records and relevant official CDC pages. The publisher DOI page returned 403; the cited paper's title/authors/year were corroborated by the CDC FAQ and local literature record, without rereading the paper.
- No site edits, deployments, Git commits, external messages or additional reviewer delegations were made. Reproduction scripts, results and screenshots remain inside the assigned folder. All test browser instances and the temporary local HTTP server were closed.
