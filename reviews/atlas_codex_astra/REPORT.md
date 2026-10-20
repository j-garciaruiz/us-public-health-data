# Focused verification of atlas fixes

**2026-10-20. Verdict: the suppression, geography mapping, ACS MOE and cross-fitting fixes pass. The current reliability-colored atlas is not cleared for mapping until findings 1–3 are resolved.** Five findings follow. No source scripts or production outputs were changed.

## Pass/fail by requested check

| Check | Verdict | Evidence |
| --- | --- | --- |
| 1. County-cause mortality suppression and recovery through `outputs/` | **PASS for the current files** | All 485 matched restricted county-cause cells have missing SMR; none appears in the mortality atlas. Their four mortality columns in the legacy residual export are also missing. The 16-file output inventory contains no restricted death counts or county mortality values from which those counts can be recovered. |
| 2. Renames, unmatched geographies and expected-death rescaling | **PASS mapping and numerical rescaling; FAIL unqualified exact-total wording** | Both renamed counties have four cause rows under their new codes. Old codes, Connecticut and Valdez-Cordova are absent. All expected deaths independently reproduce to within `7.28e-12`. Totals reconcile to the implemented numeric target below, subject to finding 5. |
| 3. ACS disability proportion MOEs | **PASS, as the documented Census approximation** | Thirty live API checks, five counties × six tables, reproduce rates within `1.78e-15` and MOEs within `2.22e-16` percentage points. |
| 4a. Repeated cross-fitting, full state indicators, unseen-state fallback, KY/PA | **PASS implementation** | Independently reproduced all 68 specifications and 210,720 rows. Every county receives ten predictions, each from a fit excluding that county. Every specification includes all 187 KY/PA counties. Finding 4 concerns interpretation and exported labels. |
| 4b. DerSimonian–Laird tau² and EB reliability | **FAIL tau²; PASS downstream arithmetic conditional on its inputs** | The implemented Q omits weighted centering. Correcting Q alone changes 1,122 row-level tier assignments. Given the implemented tau² and variances, reliability, shrinkage and tiers reproduce. Findings 1–3 concern invalid or inadequately supported inputs to that arithmetic. |
| 4c. Medicare approximate denominator | **PASS documented clipping and disclosure** | All 148,910 Medicare row notes match independently calculated GV counts clipped to the MMD band. The standardized-rate variance remains defective as an uncertainty estimate, finding 3. |
| 5. Remaining material bugs or misleading labels | **FAIL mapping readiness** | Five findings below, including four impossible negative mortality expectations with near-perfect reported reliability. |

## Verification evidence

This was a targeted fix verification, not another review of the full PLACES analysis. I read the previous reports, fix summary and current code before writing the independent calculations; this was **not a blinded replication**.

The independent cross-fitting calculation used training-state demeaning to estimate the within-state model, then reconstructed state intercepts and the training-county-weighted intercept fallback. This is algebraically equivalent to the full-dummy, no-intercept design but uses a different implementation. Across 6,800 fits, train/test disjointness and exactly one prediction per county per repetition were asserted. A separate synthetic singleton-first-state test exercised the audited functions themselves: all three state indicators were present, no intercept was present, and changing that county's own outcome by 1,000 did not change its prediction.

Maximum errors against the rounded atlas export were below `0.00005` for expected values, reliability and shrunk differences. There were **zero tier mismatches**, **zero duplicate county/layer/outcome/mode keys**, and all **476 summary cells** reproduced within their three-decimal rounding tolerance (`0.0005`). Matching the existing output verifies implementation, not the validity of its statistical assumptions.

### Mortality suppression and geography

The scan covered hidden/ignored files under `outputs/` as well as tracked files: ten CSVs, four text/Markdown files and two PNGs. I checked the mortality atlas and legacy residual columns against the restricted keys from WONDER. The other outputs contain PLACES/ACS comparisons or aggregate model statistics; neither PNG contains county mortality counts. This verdict applies to the current `outputs/` snapshot, not historical Git versions or other review directories. No individual restricted counts or restricted county-cause values are reproduced in this report.

`02270 → 02158` and `46113 → 46102` both work. The unmatched set is exactly `02261` plus Connecticut's eight old county codes `09001`–`09015`. Each cause has 3,133 matched county rows, including suppressed rows for the expected-death denominator. No unmatched county-cause row has a suppressed count in this input.

| Cause | Numeric known-age national sum | Unmatched all-age deaths | Target and exported expected sum | Rescaling factor |
| --- | ---: | ---: | ---: | ---: |
| Diabetes | 668,898* | 5,282 | 663,616* | 1.013972410 |
| Heart disease | 4,774,099 | 48,680 | 4,725,419 | 1.013534632 |
| Cerebrovascular | 1,115,838 | 10,399 | 1,105,439 | 1.016675747 |
| Chronic lower respiratory | 1,049,826 | 8,954 | 1,040,872 | 1.018031984 |

*Diabetes excludes one suppressed national age cell by treating it as zero. These are implemented numeric totals, not independently established exact death totals. See finding 5.

### ACS MOEs

Live queries used the authorized key from `.env` in memory only; it was neither printed nor saved. For each B18102–B18107 group, independent metadata selection identified eight adult numerator cells and eight adult denominator cells. With numerator `A`, denominator `B`, `p=A/B`, and component MOEs combined in quadrature:

`MOE_percent = 100 × sqrt(MOE_A² − p² × MOE_B²) / B`.

The code correctly substitutes a plus sign when the radicand is negative and converts the 90% MOE to SE with `/1.645`. This follows the [Census derived-estimate guidance, chapter 8](https://www.census.gov/content/dam/Census/library/publications/2018/acs/acs_general_handbook_2018_ch08.pdf). It remains an approximation to covariance-aware survey variance.

The five checked counties were Autauga (01001), Kusilvak (02158), DC (11001), Jefferson, Kentucky (21111), and Philadelphia (42101). For example, independently reconstructed ambulatory difficulty was:

| County | Percentage | 90% MOE, percentage points |
| --- | ---: | ---: |
| Autauga | 11.360436 | 1.137631 |
| Kusilvak | 7.605751 | 1.210797 |
| DC | 6.704129 | 0.325883 |
| Jefferson, KY | 9.074232 | 0.295141 |
| Philadelphia | 11.036671 | 0.277598 |

### Medicare denominator handling

The implementation matches `n = clip(GV Original Medicare count, band lower, band upper)`, with the documented lower-bound fallback. Missing MA/OM information can still exclude a county through the model's MA-share covariate. The code retains the denominator approximation in every exported note and conservatively excludes zero-coded rates.

For Kenai Peninsula (02122), actual diabetes retains `CMS band 1, approx n 499` and `source_discrepancy=True`. Its national reliability is 0.6875, tier 2. The broader discrepancy flag deliberately detects only `OM ≥ 5000` with band 1 or 2; it is not an exhaustive detector of every GV/band disagreement. Band ranges agree with [CMS technical documentation, section 8](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/Mapping-Technical-Documentation.pdf). The numeric code-to-band ordering remains the script's disclosed assumption.

## Findings, in priority order

### 1. High: impossible negative mortality expectations receive near-perfect reliability

**Location:** `scripts/build_atlas_data.py:99–108, 186`.

Unconstrained OLS exports four negative expected SMR×100 values. The variance calculation floors the prediction at **1 on the SMR×100 scale**, equivalent to SMR 0.01, while the exported expected value remains negative. This produces tiny Poisson variances and very high reliability for invalid predictions.

| FIPS | Outcome / mode | Observed SMR×100 | Expected SMR×100 | Reliability |
| --- | --- | ---: | ---: | ---: |
| 51610 | Diabetes / national | 47.5842 | −3.0683 | 0.995096 |
| 35028 | Diabetes / within-state | 46.0560 | −18.9592 | 0.997413 |
| 06085 | Lower respiratory / national | 40.0753 | −4.7539 | 0.999985 |
| 12119 | Lower respiratory / national | 53.8124 | −0.3238 | 0.999939 |

For 06085, the resulting shrunk difference is +44.8285 despite an impossible expectation. These are all tier 1. No ACS or Medicare expectation was outside 0–100 in this snapshot.

**Required fix:** use a positive-support mortality expectation model with a coherent variance calculation, or withhold invalid predictions and flag them until that model is available. Clipping only the variance input does not repair the expectation. Recompute downstream tau², reliability and tiers after resolving this.

### 2. High: tau² is not the advertised DerSimonian–Laird estimator

**Location:** `scripts/build_atlas_data.py:117–121`.

The code computes `Q = Σwᵢrᵢ²`. Standard DL requires

`r̄w = Σwᵢrᵢ / Σwᵢ`

`Q = Σwᵢ(rᵢ − r̄w)²`

`tau² = max(0, [Q − (k−1)] / [Σwᵢ − Σwᵢ²/Σwᵢ])`.

The missing correction is `(Σwᵢrᵢ)²/Σwᵢ`, also explicit in the [statsmodels DL implementation](https://www.statsmodels.org/stable/_modules/statsmodels/stats/meta_analysis.html#combine_effects). OLS residuals are not guaranteed to have zero inverse-variance-weighted mean, especially after cross-fitting.

Holding predictions and sampling variances fixed:

| Outcome / mode | Current tau² | Centered DL tau² | Inflation | Changed tiers |
| --- | ---: | ---: | ---: | ---: |
| Lower respiratory mortality / national | 1,176.1056 | 830.5449 | 41.61% | 347 |
| ACS vision / national | 0.483074 | 0.415428 | 16.28% | 230 |
| ACS hearing / national | 0.877905 | 0.778792 | 12.73% | 185 |

There are **1,122 changed tier assignments** over all 68 specifications, counting each county/outcome/mode row separately. A minimal test with residuals `[5,5,5]` and variances `[1,1,1]` gives current tau²=36.5; standard DL gives zero heterogeneity.

**Required fix:** implement centered DL if retaining that name. If a fixed-zero prior mean is intended instead, derive and document its own moment estimator; the current zero-centered Q combined with DL's estimated-mean degrees of freedom and denominator mixes two estimators. Decide the shrinkage target coherently. The `lambda = tau²/(tau²+s²)` and `lambda*r` arithmetic itself is correct for the stated zero-target model.

### 3. Medium: age-standardized Medicare reliability uses an inappropriate binomial variance

**Location:** `scripts/build_atlas_data.py:156–171`.

Both actual and standardized layers use `p(100−p)/n + 1/12`. Clipping the approximate denominator is an improvement for the actual-rate heuristic, but does not make an age-standardized rate a single binomial proportion.

CMS defines its standardized prevalence as an age-weighted combination of age-specific rates ([technical documentation, section 6 and appendix A.2.10](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/Mapping-Technical-Documentation.pdf)). Even with independent age groups, its variance requires squared standardization weights and age-specific variances, not the standardized `p` and total `n`.

This affects **74,402 exported standardized-layer rows**. The note discloses approximate `n` but not this additional variance assumption.

**Required fix:** obtain age-specific uncertainty inputs or avoid presenting standardized-layer shrinkage/tiering as calibrated EB reliability. A clearly named heuristic with an explicit limitation is possible; the actual layer's proxy denominators and rounding term also remain approximations, not exact uncertainty estimates.

### 4. Medium: “within-state” overpromises zero centering and hides fallback support

**Location:** `scripts/build_atlas_data.py:13–14, 102–107, 143–148`.

The statement “each state averages zero” is false for cross-fitted predictions. For example, Delaware's within-state cerebrovascular mortality residual averages **−1.5743 SMR×100 points**. DC's within-state lower respiratory residual is **+24.2304**.

The unseen-state fallback is implemented correctly, but DC has no within-state training peer. Its expected value uses a national training-county-weighted state intercept. The CSV does not say when that fallback was used; `source_discrepancy` refers to something else.

**Required fix:** describe this mode as “demographics plus state effects, estimated out of fold,” remove the zero-average guarantee, and export a fallback/support flag or repetition count for the map tooltip. Also make units explicit in the map contract: mortality `observed`, `expected` and differences are **SMR×100 / SMR-index points**, not death counts or prevalence percentage points.

### 5. Low: rescaling is numerically correct but not an exact matched known-age reconciliation

**Location:** `scripts/build_mortality_smr.py:37, 95–102`.

The numeric target is reproduced exactly. However, one suppressed national age-specific diabetes cell is replaced with zero. Therefore the diabetes sum is a sum of available numeric known-age counts, not the complete national known-age total.

There is also an age-universe mismatch: the national subtotal excludes unknown-age deaths, while the subtracted unmatched county totals include all ages. If unmatched counties contain unknown-age deaths, those are subtracted from an already known-age national base. The supplied county-by-cause file cannot resolve that allocation. I did not attempt to infer any suppressed count.

**Required fix:** label the current scaling as an approximation with these two qualifications, or obtain compatible, disclosure-safe national and unmatched known-age totals. The data do support the implemented arithmetic; they do not establish an exact complete known-age calibration or an exactly centered national observed/expected ratio.

## Reproduction and retained evidence

Run from the project root:

```sh
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python reviews/atlas_codex_astra/verify.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python reviews/atlas_codex_astra/verify_acs.py
```

Evidence in this folder includes `verification_results.json`, `mortality_reconciliation.csv`, `atlas_replication_checks.csv`, `summary_replication_checks.csv`, `dl_comparison.csv`, `out_of_bounds_expectations.csv`, `within_state_means.csv`, and `acs_live_spotchecks.csv`. Public Census responses and metadata are retained without request keys. `input_manifest.json` records source/output hashes; `input_changes_during_review.json` is empty, confirming those files were unchanged during the numerical audit.

## Shortcuts taken

- Live ACS verification sampled five counties across all six tables, as requested, rather than downloading the full national tables again. None of the 30 selected cells needed the negative-radicand fallback; that branch was verified against the formula in source code and Census guidance, not a live triggering case.
- Reused the supplied covariates and source extracts. Mortality expectations and every atlas prediction were independently rebuilt, but the earlier demographic extraction and all CMS rates were not re-audited. Numeric CMS band codes retain the existing disclosed ordering assumption.
- The mortality disclosure check covers the current 16 files in `outputs/`, including the two rendered charts, not historical copies elsewhere. No suppressed count was reconstructed.
- The 1,122 DL tier changes isolate the centering error while retaining the current variances. They are not a final corrected atlas because mortality support and standardized Medicare uncertainty also need resolution.
- No spatial, future-period, causal or uncertainty-coverage validation was added. No fixes were applied outside this review folder, and no Git commit was made because it would write outside the authorized folder.
