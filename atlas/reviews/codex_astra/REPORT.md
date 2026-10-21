# Independent replication and code review

Reviewed 2026-10-20. **The broad descriptive claim holds. The original numerical defects have now been corrected in a concurrent Claude update, and those corrections are independently verified below.** County covariates plus state reproduce a median 96.16% of crude and 97.09% of age-adjusted variation in held-out counties. Among pairs with |raw r| ≥ 0.7, the median residual covariance is 1.71% and 1.38% of the raw covariance, respectively. This does not mean that only that percentage of the correlation, real association, or causal effect remains.

## Independence and execution

I read the brief first. I built the ACS covariates, fitted all 80 outcomes, calculated 780 pairs separately for each prevalence type, and saved both insurance benchmarks before opening Claude's scripts, derived ACS file, outputs, or project memory. `PART_A_FROZEN.json` records SHA-256 hashes and the freeze time, **2026-10-20 12:05:31 UTC**. The Part A files remain unchanged.

Everything I wrote is under `reviews/codex_astra/`. I used the existing project Python, NumPy and pandas. No dependencies were installed, no credentials were accessed, and no original scripts or outputs were edited. I reproduced Claude's functions by extracting their definitions with Python's AST, without executing their top-level writes. I also independently fitted Claude's linear feature space from my raw-derived covariates; all 80 in-sample R² values agree within 1e-10. This is the independent matched-specification check, separate from merely re-executing Claude's functions.

Commands run from the project root, in order (preserve the existing frozen review before rerunning, because these overwrite generated review files):

```sh
.venv/bin/python reviews/codex_astra/replicate.py
.venv/bin/python reviews/codex_astra/compare.py
.venv/bin/python reviews/codex_astra/sensitivity.py
.venv/bin/python reviews/codex_astra/write_report.py
```

## Concurrent corrections checked

During final verification, Claude changed `scripts/covariate_test.py` and regenerated the outputs. I preserved the initial comparison and separately checked the updated snapshot saved at **2026-10-20T12:20:47.774868+00:00**. **The three numerical bugs described below are fixed in that snapshot:** pairs now use a common-sample refit, covariance shares are computed directly, and held-out DC receives the pooled-state fallback. I verified all **6,734 primary numeric output cells** against the independent matched-specification calculations within their saved rounding tolerance. The original bugs remain documented below as findings from the initial version, not unresolved defects in the updated version.

| Metric | Frozen independent | Updated Claude |
| --- | --- | --- |
| Crude median CV R² | 0.961626 | 0.961801 |
| Crude strong-pair median covariance remaining | 0.017090 | 0.017125 |
| Age-adjusted median CV R² | 0.970902 | 0.971092 |
| Age-adjusted strong-pair median covariance remaining | 0.013792 | 0.013699 |

The updated diabetes–food-insecurity partial r is **0.623479**, agreeing with the corrected matched-specification value; my frozen independently chosen covariates give **0.623695**. `updated_output_checks.csv` contains the full verification, and `updated_numeric_disagreements.csv` lists **1,871** remaining non-rounding differences from my specification, including the alternative fits and duplicated highlight/summary views. These differences reflect age/race grouping and CV seed choices, rather than the three corrected bugs. `updated_source_snapshot/` and `updated_source_hashes.json` preserve the exact updated material checked.

The updated script also removes the unsupported upper-bound/residual-component claims. Chart 2 now explicitly reports **1.2% of raw covariance remaining** and **residual r = 0.62**, and Chart 1's source headline includes state. One presentation defect remains in the inspected updated PNG: **Chart 1's longer headline is clipped at the right edge**. Wrap that title before using the chart. I did not edit the original files.

To verify the corrected version, use `.venv/bin/python reviews/codex_astra/recheck_updated.py`. The initial `compare.py` and the initial-version sections below target the originally reviewed implementation, identified by `reviewed_source_hashes.json`; rerunning that original comparison requires the original source version. The independent Part A script and its frozen results remain unchanged.

## Original-version headline comparison

Claude's figures below are unrounded reconstructions of the originally reviewed implementation, verified against the saved three-decimal CSVs. Independent figures are the frozen Part A specification. “Strong” means |raw r| ≥ 0.7, classified before rounding.

| Metric | Independent | Claude |
| --- | --- | --- |
| Crude: Median in-sample R² | 0.964389 | 0.964111 |
| Crude: Median 10-fold CV R² | 0.961626 | 0.961926 |
| Crude: Median absolute partial r | 0.171569 | 0.171188 |
| Crude: Pairs with \|raw r\| ≥ 0.7 | 201 | 201 |
| Crude: Of those, \|partial r\| ≥ 0.7 | 46 | 45 |
| Crude: Median covariance share remaining, strong pairs | 0.017090 | 0.017870 |
| Crude: Maximum covariance share remaining, strong pairs | 0.042780 | 0.042427 |
| Age-adjusted: Median in-sample R² | 0.973474 | 0.973504 |
| Age-adjusted: Median 10-fold CV R² | 0.970902 | 0.971159 |
| Age-adjusted: Median absolute partial r | 0.158916 | 0.160210 |
| Age-adjusted: Pairs with \|raw r\| ≥ 0.7 | 279 | 279 |
| Age-adjusted: Of those, \|partial r\| ≥ 0.7 | 65 | 65 |
| Age-adjusted: Median covariance share remaining, strong pairs | 0.013792 | 0.013683 |
| Age-adjusted: Maximum covariance share remaining, strong pairs | 0.037866 | 0.037997 |

All 40 measures have CV R² above 0.5 in both prevalence forms. The independent ranges are **0.730081–0.984157 crude** and **0.726172–0.984451 age-adjusted**. These are equally weighted county regressions, not population-weighted national variance shares.

The insurance comparison uses 2,956 counties in the first sample and 1,485 with at least 20,000 ACS adults:

| Sample / metric | Independent | Claude |
| --- | --- | --- |
| All available: raw r | 0.717227 | 0.717227 |
| All available: partial r | 0.111296 | 0.108482 |
| All available: PLACES CV R² | 0.978178 | 0.978383 |
| All available: ACS CV R² | 0.718861 | 0.716863 |
| ≥20,000 ACS adults: raw r | 0.800029 | 0.800029 |
| ≥20,000 ACS adults: partial r | 0.239288 | 0.243180 |
| ≥20,000 ACS adults: PLACES CV R² | 0.979554 | 0.978872 |
| ≥20,000 ACS adults: ACS CV R² | 0.838449 | 0.838454 |

The independent insurance in-sample R² values are 0.979682 for PLACES and 0.740049 for ACS in all available counties, and 0.981716 and 0.856271 in the larger-county subset. Full precision is in `benchmark.csv`.

## The six requested age-adjusted pairs

The corrected-refit column holds Claude's covariates constant, isolating the common-sample error from my different age/race grouping.

| Age-adjusted pair | n | Raw r (both) | Independent partial r | Claude partial r | Claude covariates, corrected refit | Independent covariance left | Claude covariance left |
| --- | --- | --- | --- | --- | --- | --- | --- |
| diabetes ~ foodinsecu | 2299 | 0.936594 | 0.623695 | 0.605910 | 0.623479 | 1.213% | 1.251% |
| diabetes ~ lacktrpt | 2299 | 0.913555 | 0.612534 | 0.595123 | 0.612379 | 1.278% | 1.319% |
| chd ~ csmoking | 2956 | 0.920998 | 0.666578 | 0.662749 | 0.662749 | 1.566% | 1.540% |
| obesity ~ lpa | 2956 | 0.745582 | 0.264343 | 0.264937 | 0.264937 | 2.766% | 2.773% |
| bphigh ~ stroke | 2956 | 0.870227 | 0.293700 | 0.292809 | 0.292809 | 0.824% | 0.821% |
| depression ~ loneliness | 2299 | 0.050481 | 0.293131 | 0.292611 | 0.292960 | 42.679% | 41.438% |

Depression–loneliness is not a strong raw association. Its small denominator makes the covariance fraction much larger and less stable than those for the five other examples. Residual correlation can increase after adjustment.

## Part A construction and sample accounting

The primary independent design has 17 composition columns: five of six adult age shares (18–24, 25–34, 35–44, 45–54, 55–64, with 65+ omitted), adult female share, seven of eight mutually exclusive race/ethnicity shares (non-Hispanic White omitted), three of four education shares, and adult poverty below 150% FPL. State indicators include an intercept-equivalent span. The age bands are an explicit approximation, not a verified claim about every outcome's exact CDC coding.

* **B01001:** adults are male cells 007–025 plus female cells 031–049; every age and sex share uses that adult denominator.
* **B03002:** use cells 003–009 and 012 divided by 001. Hispanic is any race; the other seven categories are non-Hispanic. This table is all ages.
* **B15003:** less than high school = 002–016; high school/GED = 017–018; some college/associate = 019–021; bachelor's or higher = 022–025, all over 001. Its universe is 25+.
* **B17024:** adult denominator = 041 + 054 + 067 + 080 + 093 + 106 + 119. For each of these seven totals, sum the next five cells for income-to-poverty ratios below 1.50. This is the population with poverty status determined, not all B01001 adults.
* **B27010:** uninsured 19–64 = 100 × (033 + 050) / (018 + 034). Its universe is civilian noninstitutionalized residents. The PLACES comparison covers 18–64, so the one-year age mismatch is real. [Census B27010 labels](https://api.census.gov/data/2023/acs/acs5/groups/B27010.json), [CDC insurance definition](https://www.cdc.gov/places/measure-definitions/prevention.html).

The full cell mapping and denominators are in `variable_mapping.csv`; all five official Census metadata responses are saved. Source labels were retrieved directly from the Census API without a key.

All **3,143 PLACES FIPS match** an ACS row; there are no duplicate FIPS or missing covariates. ACS contains 3,222 counties/equivalents; the 79 extra rows are Puerto Rico's 78 municipalities and FIPS 48301 (Loving County, Texas), which is absent from the supplied PLACES file. No PLACES county is lost in the join.

There are three outcome supports:

| Measures | Count | Counties per outcome | Design rank | Residual df |
| --- | --- | --- | --- | --- |
| Most 2023 measures | 28 | 2,956 | 66 | 2,890 |
| Colon screening, dental visits, mammography, short sleep, all teeth lost | 5 | 3,143 | 68 | 3,075 |
| Seven health-related social-needs measures | 7 | 2,299 | 57 | 2,242 |

Kentucky (120 counties) and Pennsylvania (67) are missing for the 28-measure group, directly in the PLACES source. The seven social-needs measures additionally lack Texas, Tennessee, Florida, South Dakota, Colorado, Washington, Oregon, Wyoming and Vermont. The five older-year measures have full county coverage. “All counties” in the benchmark therefore means all **available matched outcome counties**, not every US county.

OLS uses complete observations for each outcome. Each pair is refitted on its own common sample. CV uses 10 shuffled folds, seed 20261020, with one held-out prediction per county and pooled R² = 1 − total prediction SSE / full-sample SST. `cv_folds.csv` also supplies fold-specific scores. State effects cannot be learned for singleton Washington, DC when held out; I explicitly substitute the training-county-weighted mean state intercept. This is an assumption, not an estimated DC effect.

The covariance fraction is calculated directly as cov(e₁,e₂) / cov(y₁,y₂), using the same counties and n−1 divisor for both. I checked cov(y₁,y₂) = cov(fitted₁,fitted₂) + cov(e₁,e₂) numerically for every pair. This signed ratio can be negative or greater than one; I do not clip it. Ratios with near-zero raw covariance should not be interpreted as percentages of an association.

## Every original-version numerical disagreement

`all_numeric_disagreements.csv` lists **2,065 differing reported cells**, including duplicate highlight and summary views, with source file, row key, metric, both values, signed difference and cause. A three-decimal number is treated as rounding-compatible when the difference is at most 0.0005; summary fields use their actual display precision. Counts are compared exactly. This is the exhaustive list, not a sample of disagreements.

| Source output | Metric | Differences beyond rounding |
| --- | --- | --- |
| benchmark_uninsurance.csv | cv_r2_acs_direct | 1 |
| benchmark_uninsurance.csv | cv_r2_places | 1 |
| benchmark_uninsurance.csv | partial_r | 2 |
| benchmark_uninsurance.csv | r2_acs_direct_on_inputs | 1 |
| highlight_pairs_adjprev.csv | partial_r | 9 |
| highlight_pairs_adjprev.csv | share_beyond_inputs | 3 |
| pairs_adjprev.csv | partial_r | 603 |
| pairs_adjprev.csv | share_beyond_inputs | 234 |
| pairs_crudeprev.csv | partial_r | 683 |
| pairs_crudeprev.csv | share_beyond_inputs | 389 |
| r2_by_measure_adjprev.csv | flexible_plus_state | 7 |
| r2_by_measure_adjprev.csv | inputs_only | 24 |
| r2_by_measure_adjprev.csv | inputs_plus_state | 5 |
| r2_by_measure_adjprev.csv | inputs_plus_state_cv | 16 |
| r2_by_measure_crudeprev.csv | flexible_plus_state | 19 |
| r2_by_measure_crudeprev.csv | inputs_only | 29 |
| r2_by_measure_crudeprev.csv | inputs_plus_state | 13 |
| r2_by_measure_crudeprev.csv | inputs_plus_state_cv | 20 |
| summary.txt | cv_min | 1 |
| summary.txt | sign_flips | 2 |
| summary.txt | strong_remaining_count | 1 |
| summary.txt | strong_share_max | 1 |
| summary.txt | strong_share_median | 1 |

The core table comparison contributes 1,968 cells; the state-only/inputs-only/flexible comparisons contribute another 79. The additional rows are duplicated highlights and summary aggregates. There are **no disagreements in county counts or raw correlations beyond rounding**, and no raw ACS covariate mapping disagreement above 1e-12. All 6,734 numeric cells in the five primary source tables across prevalence types and the benchmark reproduce within their saved rounding tolerance.

The causes are separated in `pair_disagreement_attribution.csv` and the other audit CSVs:

1. **Different legitimate feature spaces.** Claude splits 65–74 from 75+ and combines non-Hispanic “other” with multiracial; I initially combine 65+ and keep the race categories separate. Both have 17 composition columns. Female versus male and omitted education categories are equivalent linear reparameterizations and are not causes of disagreement. Nonlinear transformations do depend on the chosen reference categories. The post-freeze expanded age/race sensitivity uses both finer choices.
2. **Common-sample fitting and variance scaling bugs.** These affect 371 of the 780 pairs in each prevalence type because the three outcome supports differ. The matched-covariate refit and direct covariance isolate these errors from feature choices.
3. **CV setup.** My seed is 20261020; Claude's is 0. Both datasets are in FIPS order. There is also the explicit versus implicit unseen-state handling described below. The R² definition itself agrees.

## Original bugs and code findings

The line numbers and defects in this section refer to the initial source version. Items 1–3 are fixed in the verified updated snapshot; the numerical inconsistency and wording in item 4 are corrected there, with the remaining title-clipping issue noted above.

**1. Pairwise residuals use different estimation samples.** In `scripts/covariate_test.py:92–106`, each outcome is residualized on its own support; lines 114–118 then intersect the residual series without refitting. This is not the requested partial correlation conditional on the common-sample design. With Claude's features held fixed, age-adjusted diabetes–food insecurity changes from **0.605910 to 0.623479**, and diabetes–transport barriers from **0.595123 to 0.612379**. The largest changes are access2–food insecurity: **0.359145 to 0.421293 crude**, and **0.352894 to 0.405620 age-adjusted**. Both outcomes must be regressed on the same X on the intersection counties. My pair CSV already implements that correction.

**2. The covariance-share identity is applied across incompatible samples.** Lines 123–126 use per-outcome R² from different county sets, whereas raw and partial correlations use the intersection. The identity

`partial_r × sqrt((1 − R²_a) × (1 − R²_b)) / raw_r`

is valid with common-sample OLS and the same variance convention, but not with those mixed R² values. Holding Claude's features constant, depression–loneliness changes from **0.414381 to 0.426051**; crude access2–food insecurity changes from **0.009335 to 0.011954**. The largest absolute error is **0.280727** for crude CHD–loneliness, whose raw r is only 0.003567. Compute the covariance ratio directly. For these nested supports, the direct covariance of the existing intersected residuals already equals the refitted residual covariance to numerical precision: the refit changes their variances and thus their correlation. The error in the reported covariance fraction comes from the cross-sample scaling, not from a changed covariance numerator.

**3. Singleton-state CV is silently reference-dependent.** Lines 48 and 76–85 predefine state dummies with Alabama omitted. In DC's test fold, its dummy has no training observations, so least squares sets its coefficient to zero and uses Alabama's effect. Changing the reference state would change this held-out prediction without changing any estimable fit. In age-adjusted cholesterol screening, DC is observed at **90.2**, predicted at **82.310** under Claude's coding and **87.316** under the pooled-state fallback; changing just that prediction raises CV R² from **0.977265 to 0.980487**. This slightly understates some scores; it does not overturn the headline. `singleton_state_cv_audit.csv` enumerates all 80 outcomes and also scores them without the DC test error.

**4. The chart and pair CSV use inconsistent calculations, and the chart's wording overclaims.** `scripts/covariate_charts.py:84–101` correctly refits the diabetes–food-insecurity pair on its common counties, giving residual r **0.623479** and covariance remaining **1.211%**. The saved pair CSV instead gives 0.606 and 0.013. The chart's displayed 1.2% is correct for covariance, but “the link is the model's inputs” implies a causal conclusion this analysis cannot establish. Label it “1.2% of raw covariance remains,” show the residual r, and use a headline such as “County covariates and state reproduce most of the diabetes–food insecurity covariance.” The first chart's displayed 98%, 73% and 72% are rounding-compatible with the replication; its “from demographics” headline should explicitly include state effects.

**Checks that passed.** The age, sex, race, education, adult-poverty and B27010 cell mappings are correct in Claude's fetch script; the saved 22 covariate/count columns agree with independent construction across all 3,222 rows. FIPS padding and the join are correct for this release. All current designs have full column rank (57, 66 or 68). There is no degrees-of-freedom bug in the reported descriptive correlations or ordinary R²: using n or n−1 consistently cancels in the relevant ratios. A partial-correlation t test, if later added, would require df = n − rank(X) − 1, not n−2. No such test is currently reported. Do not use an n−rank(X) residual-variance correction inside the descriptive covariance decomposition.

**Hardening, not a demonstrated current numerical defect.** `fetch_acs_county.py:51,79–124` does not mask negative Census special codes and uses sums that can silently skip missing cells; `covariate_test.py:35,93–102` does not validate one-to-one joins or missing predictors. The current county estimates are complete and valid, so these did not affect this run. My extraction masks negative counts, requires all contributing cells and checks unique FIPS and compositional totals.

## Methods judgment: eight findings, in priority order

1. **Fair as a descriptive reconstruction test; insufficient as a test that associations are artifacts.** Very high held-out predictability is direct evidence that these published county estimates largely lie in the space spanned by demographic shares, poverty and state. It cannot separate true health disparities associated with those inputs from dependence introduced by estimation. An observed outcome can also be highly predictable. The insurance benchmark is useful context, not a calibration converting PLACES R² into an “artificial” proportion. The general caution is consistent with [Kong and Zhang's discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC7204458/); the numerical verdict here comes from this replication.

2. **Covariance remaining and correlation remaining answer different questions.** A residual cloud can have little absolute spread and still exhibit a substantial correlation. Here 65/279 strong age-adjusted pairs remain above |partial r| = 0.7, and diabetes–food insecurity retains r = 0.624. Report covariance shares alongside residual correlations and outcome residual standard deviations. The claim that “most strong correlations” are reproduced is supported in the covariance sense and by most falling below the 0.7 threshold, not by every residual association disappearing.

3. **State fixed effects absorb more than demographic composition.** They capture outcome-associated state differences, including policies, healthcare systems and other real contextual variation. Treating all of that as the named demographic inputs overstates what demographics alone explain. In the replication, covariates alone have median CV R² of **0.845660 crude / 0.829083 adjusted**, compared with **0.961626 / 0.970902** including state. State-only medians are **0.427823 / 0.500779**. These overlapping predictions are not additive causal variance components.

4. **The reconstruction is not the original poststratification model.** Marginal shares discard joint composition; all-age race and education 25+ mismatch adult predictors; ACS five-year populations differ from the annual population counts used for county predictions. Outcome-specific eligibility also matters (for example mammography and teeth loss). CDC specifies individual predictors, contextual poverty and random effects, with predictor inclusion depending on the outcome, rather than one identical fitted regression for all 40 measures. These approximations can understate reconstructibility, but proxy adjustment can also absorb real contextual signal. Neither residual variance nor partial correlation is a proven upper bound on “beyond-input” association. [CDC methodology](https://www.cdc.gov/places/methodology/index.html).

5. **Nonlinearity modestly matters; in-sample flexible fit is not adequate evidence.** The original prediction step is logistic and aggregated; linear regression of county percentages is an approximation. I tested logit-outcome regression with predictions transformed back before scoring, richer age-sex cells, and squares/interactions. The table below shows genuine 10-fold CV, not only training improvement. These alternatives leave the main conclusion intact. They are sensitivity analyses, not a recreation of CDC's fitted multilevel model.

6. **County shrinkage can make model estimates easier to reconstruct, without making the remainder a pure county effect.** County random effects with weak local survey support are expected to be shrunk, so the remaining county-specific signal can be small by design. OLS residuals also include approximation error, population-vintage differences, rounding and unrecovered shared structure; the fitted component can absorb correlated county effects. The available files do not identify the amount of shrinkage or decompose those sources. The original Claude version's “mostly the county random effect” and “upper bound” language in `covariate_test.py:10–14` was unverified and is removed from the updated version.

7. **The direct benchmark has sampling noise and imperfect alignment.** Restricting to ≥20,000 adults raises ACS CV R² from **0.718861 to 0.838449**, while PLACES stays near 0.98; this is consistent with small-county noise contributing to the gap, although sample composition changes too. ACS is a survey estimate, not ground truth, and shares its data source with the covariates. Ages 19–64 versus 18–64, survey universes, question wording and 2019–2023 versus 2023 timing differ. ACS margins of error and their covariance with predictors are not propagated here. A reliability-aware comparison and multiple direct outcomes would be stronger.

8. **Validation and generalization must match the target.** Random county folds mostly test new counties within observed states and can benefit from nearby demographic similarity. The exact 40-measure summary mixes three geographic supports and two survey vintages; it is not a complete US-wide comparison. Use a common 2,299-county panel as a sensitivity, repeat folds, and add spatial blocks within states. A leave-state-out test needs a defined unseen-state prediction rule and answers a different question. Sampling/model uncertainty and spatial dependence should be included before inferential claims, rankings or significance tests. CDC documents the mixed BRFSS vintages and cautions on interpreting these estimates in regression. [CDC FAQs](https://www.cdc.gov/places/faqs/index.html).

Post-freeze tests already run:

| Specification | Crude median CV R² | Age-adjusted median CV R² |
| --- | --- | --- |
| Primary linear | 0.961626 | 0.970902 |
| Covariates only | 0.845660 | 0.829083 |
| State only | 0.427823 | 0.500779 |
| Seven age bands, separate race categories | 0.961669 | 0.971010 |
| Six age bands × sex | 0.961755 | 0.971327 |
| All 38 adult age-sex cells | 0.961570 | 0.971183 |
| Squares and poverty interactions | 0.961100 | 0.976215 |
| OLS on logit outcome, inverse prediction | 0.962984 | 0.975069 |

The full native B01001 sensitivity uses all 38 adult sex-by-age cells, omitting one share, plus the race, education and poverty covariates. Its benchmark CV R² is 0.978094 for PLACES versus 0.725167 for ACS in all available counties, and 0.979570 versus 0.833003 in the larger-county subset. More detailed demographic representation does not eliminate the benchmark gap. These are supplementary results; they do not replace the frozen independent baseline.

## Stronger feasible test

With the existing files, use common-support pairwise refits, retain both covariance and correlation metrics, compare state-only, composition-only and combined predictions, and use the native age-sex cells plus a prespecified nonlinear model. Choose model complexity inside training folds, not from the reported test scores. Repeat and spatially block CV; assess cross-fitted residual correlations as a robustness check while keeping them separate from the exact in-sample covariance decomposition. Use the B27010 count margins of error to examine benchmark reliability, clearly stating the assumptions needed for sums and ratios, and report population strata rather than relying on a single cutoff. Several representation and nonlinearity steps are implemented above; nested/spatial validation and uncertainty propagation remain follow-up analyses.

The more decisive algorithmic test would require CDC's fitted coefficients, joint poststratification populations and county/state effect estimates (or suitable restricted geocoded BRFSS data). Regenerate each estimate with and without the county effect, holding everything else fixed, and compare that decomposition with direct county estimates where reliable. Those ingredients are not in the supplied files, so the present analysis cannot identify an exact mechanical share caused by MRP.

## Verdict

**Yes, with precise wording:** in the available county samples, county-level approximations to the PLACES predictors **plus state fixed effects** reproduce most of the variation in every published measure and most of the raw covariance among strongly correlated measures. Independent cross-validation and the corrected pairwise calculations support that conclusion, and the implementation bugs do not reverse it. The evidence does **not** establish that the underlying health relationships are spurious, that demographics alone explain the state component, or that residual associations vanish. The defensible claim concerns reconstruction of published estimates and covariance, not a causal attribution of real county health variation to the estimation algorithm.

## Deliverables and verification

* `replicate.py`, `covariates.csv`, `variable_mapping.csv`, the five county-estimate extracts and five Census metadata files: independent extraction and provenance.
* `measure_r2.csv`, `cv_folds.csv`, `predictions.csv`: all 80 outcome fits, held-out predictions, residuals and sample/rank information.
* `pair_correlations.csv`, `selected_pairs.csv`, `benchmark.csv`: all 1,560 within-type pairs, the six requested pairs and both benchmark samples.
* `all_numeric_disagreements.csv`: every non-rounding disagreement in comparable numerical output cells; `headline_comparison.csv` and `summary_comparison.csv` provide the aggregates.
* `pair_disagreement_attribution.csv`, `covariate_comparison.csv`, `rank_audit.csv`, `matched_spec_independent_checks.csv`, `claude_output_reproduction_checks.csv`, `singleton_state_cv_audit.csv`: causes and reproducibility checks.
* `sensitivity_r2.csv`, `sensitivity_benchmark.csv`: all supplementary specifications and benchmark results.
* `PART_A_FROZEN.json`, `reviewed_source_hashes.json`, run logs, and `final_verification.json`: preserved independence, source identity and completion checks.

**Shortcuts taken:** the primary model uses six broad age bands; a post-freeze sensitivity uses all 38 available adult age-sex cells. Exact outcome-specific CDC predictor coding and fitted random effects were unavailable, so this is an empirical reconstruction rather than a rerun of PLACES. CV uses one prespecified partition per specification; repeated/spatial CV, ACS uncertainty propagation and a full common-support 40-measure rerun were not performed. No confidence intervals or causal significance claims are made. I left original artifacts untouched under the write-only-in-review-folder instruction; their concurrent changes are separately snapshotted and verified.
