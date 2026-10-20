# Independent review: PLACES versus directly observed county outcomes

Reviewed 2026-10-20. **The narrow prediction claim is supported; an absence-of-information claim is not.** Demographic composition plus state, with Medicare Advantage share for Medicare, beats PLACES alone for every one of the 17 pairs in both samples. Adding PLACES usually improves held-out R² only slightly. Some positive increments persist across repeated folds, especially larger-county asthma, hypertension, hyperlipidemia, and ACS mobility. The present residual export is an exploratory layer, not a publication-ready measure of excess disease or county performance.

## Independence, scope and execution

I completed and froze the independent results at **2026-10-20T12:23:00.828051+00:00**, before opening `scripts/expected_vs_observed.py`, `scripts/fetch_observed_outcomes.py`, or `outputs/expected_vs_observed/`. The project instruction file `CLAUDE.md` was read first and exposed its short headline conclusion; the analysis was therefore implementation-independent, not fully blinded to the claimed direction. I reused my previously independently constructed `reviews/codex_astra/covariates.csv`, as authorized, and did not import Claude's analysis functions. The pre-existing review report was background.

Part A includes **112 specifications**: 11 Medicare conditions × two MMD filters × two PLACES prevalence forms × two sample sizes, plus six ACS disabilities × two PLACES forms × two sample sizes. `independent_results.csv` contains every requested statistic at full precision. `independent_predictions.csv` preserves every county's fold, observed value, PLACES value, held-out predictions, and residual. The paired age-standardized Medicare and crude ACS specifications provide the direct comparison with Claude below. Medicare actual versus PLACES crude is also printed below. The cross-form comparisons and ACS versus age-adjusted PLACES are supplementary CSV rows.

All writes stayed inside `reviews/eo_codex_astra/`. The existing project Python, NumPy and pandas were used; no packages were installed. The existing Census key was used in memory for the authorized source verification and was not printed or saved. No original code or outputs were changed. No commit was made because the instruction confines writes to this folder.

Commands, run from the project root:

```sh
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/replicate.py
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/compare.py
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/verify_sources.py
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/sensitivity.py
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/audit.py
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/write_report.py
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python reviews/eo_codex_astra/verify.py
```

The saved `gv_county_counts_live.csv` came from an additional direct public CMS query recorded in `gv_query_provenance.json`; `audit.py` verifies it against the supplied counts.

While this review was running, the shared implementation and outputs were expanded with four WONDER mortality comparisons. A final scope check confirms that **all 34 requested Medicare/ACS result rows and all their nonmissing residuals remain unchanged**. The tables and code line references here refer to the preserved initial `reviewed_snapshot/`; `current_scope_recheck/` preserves the later version. The new mortality analysis was outside this request and was not reviewed.

## Part A: independent methods and results

The primary model is unweighted county-level OLS. **D** means demographic composition plus state fixed effects, and also MA/(MA+OM) for Medicare; **P** means the corresponding PLACES percentage. Every model within a row uses exactly the same complete counties and the same ten folds. Counties are ordered by FIPS, shuffled with NumPy's default RNG and seed 20261020, then split into ten groups. R² is pooled over all held-out predictions, `1 − SSE/SST`, not an average of fold-specific R². A negative gain is retained.

The independent composition variables are five adult age shares, with 65+ as the reference; female adult share; seven mutually exclusive race/ethnicity shares, with non-Hispanic White as the reference; three education shares; and the proportion of adults below 150% FPL. Race is all ages and education is 25+, as in the available ACS tables. My 65+ band is combined and my non-Hispanic other and multiracial categories are separate. Claude splits 65–74 from 75+ and combines other/multiracial. These feature spaces have the same number of columns but are not identical.

State indicators include the intercept-equivalent span. For a held-out state absent from training, the prediction uses the training-county-weighted mean state intercept. This is an explicit fallback, not an estimated local state effect. Continuous standardization is an invertible OLS reparameterization and does not introduce target leakage. All sample joins check uniqueness. Medicare `*` counts become missing; they are never filled with zero. Zero-coded MMD rates are excluded as ambiguous. The larger samples use the requested GV Original Medicare count ≥5,000 or B01001 adult population ≥20,000.

Partial correlations residualize **both** observed and PLACES on the same design and common counties. The main comparison tables condition on D, including MA for Medicare, matching Claude. A separate table below provides the literally requested demographics-plus-state-only partial correlations; both versions are in `independent_results.csv`. Partial r is an in-sample descriptive statistic, distinct from the held-out R² gain.

The headline independent results, using Claude's outcome forms:

| Source | Sample | Baseline CV R² range | Median gain | Gain range |
| --- | --- | --- | --- | --- |
| Medicare | all | 0.3599–0.7860 | 0.0046 | -0.0001–0.0078 |
| Medicare | large | 0.2929–0.8065 | 0.0054 | -0.0008–0.0235 |
| ACS | all | 0.4007–0.6363 | -0.0001 | -0.0008–0.0029 |
| ACS | large | 0.5221–0.7762 | 0.0023 | -0.0005–0.0088 |


Here an R² gain of 0.01 means one percentage point of county outcome variance, not a one-point increase in disease prevalence. The outcome and RMSE units are prevalence percentage points. All counties means all available matched counties, not a complete national panel.

### Numbers versus Claude: all available counties

I = independent Part A; C = Claude's saved output. Counts, raw correlations and PLACES-only CV scores agree; those columns are shown once. Medicare uses MMD `fltr=2` versus PLACES age-adjusted prevalence. ACS uses direct crude disability prevalence versus PLACES crude prevalence.

| Outcome | n, both | Raw r, both | CV D, I / C | CV P, both | CV D+P, I / C | Gain, I / C | Partial r, I / C |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Diabetes | 2917 | 0.7096 | 0.7246 / 0.7278 | 0.5029 | 0.7324 / 0.7357 | 0.0078 / 0.0079 | 0.1657 / 0.1683 |
| COPD | 2915 | 0.6190 | 0.5809 / 0.5786 | 0.3822 | 0.5865 / 0.5846 | 0.0056 / 0.0060 | 0.1229 / 0.1252 |
| Depression | 2911 | 0.2853 | 0.4247 / 0.4262 | 0.0805 | 0.4310 / 0.4334 | 0.0063 / 0.0072 | 0.1115 / 0.1195 |
| High blood pressure | 2918 | 0.7439 | 0.7860 / 0.7897 | 0.5525 | 0.7914 / 0.7954 | 0.0054 / 0.0057 | 0.1598 / 0.1662 |
| Coronary heart disease | 2917 | 0.3780 | 0.5991 / 0.5993 | 0.1413 | 0.5990 / 0.5993 | -0.0001 / 0.0000 | 0.0296 / 0.0335 |
| Stroke | 2898 | 0.3322 | 0.4827 / 0.4820 | 0.1090 | 0.4827 / 0.4820 | 0.0000 / 0.0000 | 0.0291 / 0.0293 |
| Asthma | 2902 | 0.0614 | 0.3599 / 0.3600 | 0.0023 | 0.3629 / 0.3633 | 0.0030 / 0.0033 | 0.0782 / 0.0802 |
| Obesity | 2915 | 0.3576 | 0.5353 / 0.5352 | 0.1267 | 0.5374 / 0.5374 | 0.0022 / 0.0022 | 0.0813 / 0.0816 |
| Arthritis | 2917 | 0.3527 | 0.4655 / 0.4689 | 0.1228 | 0.4701 / 0.4743 | 0.0046 / 0.0054 | 0.0980 / 0.1043 |
| High cholesterol | 2918 | 0.5785 | 0.6168 / 0.6181 | 0.3338 | 0.6240 / 0.6254 | 0.0072 / 0.0074 | 0.1347 / 0.1366 |
| Cancer | 2914 | 0.0847 | 0.4576 / 0.4544 | 0.0060 | 0.4612 / 0.4583 | 0.0036 / 0.0039 | 0.0889 / 0.0898 |
| Hearing disability | 2956 | 0.6627 | 0.5254 / 0.5328 | 0.4380 | 0.5283 / 0.5338 | 0.0029 / 0.0010 | 0.0754 / 0.0570 |
| Vision disability | 2956 | 0.5466 | 0.4007 / 0.3989 | 0.2976 | 0.4003 / 0.3983 | -0.0004 / -0.0006 | 0.0411 / 0.0382 |
| Cognitive disability | 2956 | 0.5412 | 0.4332 / 0.4308 | 0.2912 | 0.4342 / 0.4328 | 0.0010 / 0.0020 | 0.0668 / 0.0730 |
| Mobility disability | 2956 | 0.7535 | 0.6363 / 0.6339 | 0.5672 | 0.6364 / 0.6339 | 0.0002 / 0.0000 | 0.0524 / 0.0512 |
| Self-care disability | 2956 | 0.5635 | 0.4134 / 0.4108 | 0.3169 | 0.4126 / 0.4100 | -0.0008 / -0.0008 | -0.0144 / -0.0149 |
| Independent-living disability | 2956 | 0.6264 | 0.5112 / 0.5076 | 0.3917 | 0.5106 / 0.5071 | -0.0006 / -0.0005 | 0.0132 / 0.0149 |


### Numbers versus Claude: larger counties

| Outcome | n, both | Raw r, both | CV D, I / C | CV P, both | CV D+P, I / C | Gain, I / C | Partial r, I / C |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Diabetes | 1016 | 0.7190 | 0.7598 / 0.7603 | 0.5146 | 0.7681 / 0.7686 | 0.0083 / 0.0084 | 0.2022 / 0.2017 |
| COPD | 1016 | 0.6739 | 0.7020 / 0.6973 | 0.4513 | 0.7074 / 0.7037 | 0.0054 / 0.0064 | 0.1518 / 0.1600 |
| Depression | 1016 | 0.3112 | 0.5524 / 0.5545 | 0.0927 | 0.5571 / 0.5598 | 0.0047 / 0.0053 | 0.1097 / 0.1145 |
| High blood pressure | 1017 | 0.7573 | 0.8065 / 0.8081 | 0.5724 | 0.8186 / 0.8209 | 0.0121 / 0.0128 | 0.2441 / 0.2522 |
| Coronary heart disease | 1016 | 0.3373 | 0.5952 / 0.5953 | 0.1094 | 0.5973 / 0.5977 | 0.0022 / 0.0025 | 0.0800 / 0.0822 |
| Stroke | 1016 | 0.2983 | 0.5557 / 0.5571 | 0.0853 | 0.5550 / 0.5565 | -0.0008 / -0.0006 | 0.0498 / 0.0494 |
| Asthma | 1016 | -0.0227 | 0.2929 / 0.2899 | -0.0029 | 0.3164 / 0.3127 | 0.0235 / 0.0228 | 0.1869 / 0.1828 |
| Obesity | 1016 | 0.4306 | 0.5792 / 0.5778 | 0.1791 | 0.5806 / 0.5793 | 0.0013 / 0.0015 | 0.0552 / 0.0585 |
| Arthritis | 1016 | 0.3569 | 0.5285 / 0.5329 | 0.1223 | 0.5347 / 0.5389 | 0.0062 / 0.0060 | 0.1323 / 0.1275 |
| High cholesterol | 1017 | 0.6143 | 0.6739 / 0.6774 | 0.3750 | 0.6891 / 0.6938 | 0.0152 / 0.0164 | 0.2221 / 0.2269 |
| Cancer | 1016 | 0.0503 | 0.5615 / 0.5679 | -0.0011 | 0.5624 / 0.5689 | 0.0010 / 0.0011 | 0.0732 / 0.0754 |
| Hearing disability | 1485 | 0.7728 | 0.6655 / 0.6660 | 0.5953 | 0.6675 / 0.6688 | 0.0019 / 0.0028 | 0.0725 / 0.0899 |
| Vision disability | 1485 | 0.6351 | 0.5221 / 0.5230 | 0.4019 | 0.5217 / 0.5229 | -0.0005 / -0.0001 | 0.0489 / 0.0570 |
| Cognitive disability | 1485 | 0.6107 | 0.6008 / 0.6016 | 0.3716 | 0.6041 / 0.6046 | 0.0032 / 0.0030 | 0.0993 / 0.0980 |
| Mobility disability | 1485 | 0.8406 | 0.7762 / 0.7762 | 0.7058 | 0.7850 / 0.7849 | 0.0088 / 0.0087 | 0.1946 / 0.1953 |
| Self-care disability | 1485 | 0.7103 | 0.5852 / 0.5879 | 0.5031 | 0.5879 / 0.5903 | 0.0027 / 0.0024 | 0.1045 / 0.1007 |
| Independent-living disability | 1485 | 0.7188 | 0.6606 / 0.6630 | 0.5156 | 0.6610 / 0.6628 | 0.0003 / -0.0002 | 0.0591 / 0.0483 |


For larger-county age-standardized asthma, independent CV R² rises from **0.292908 to 0.316395**, a gain of **0.023488**; RMSE falls from **1.006280 to 0.989426 percentage points**. For hypertension, R² rises by **0.012061** and RMSE falls from **2.864368 to 2.773653 points**. The latter removes about **6.23% of baseline held-out squared error**, despite its small gain as a fraction of total outcome variance. “Small” should be tied to intended use and error reduction, not treated as synonymous with zero.

### Actual Medicare prevalence versus crude PLACES

These are additional independent tests; Claude did not report this specification. D and partial r include MA share. They are more natural inputs for a descriptive burden atlas, but they still compare different populations and ascertainment systems.

All matched counties:

| Claims outcome | n | Raw r | CV D | CV P | CV D+P | Gain | Partial r |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Diabetes | 2919 | 0.5577 | 0.7247 | 0.3104 | 0.7263 | 0.0016 | 0.0852 |
| COPD | 2919 | 0.5654 | 0.5813 | 0.3186 | 0.5835 | 0.0023 | 0.0839 |
| Depression | 2918 | 0.3781 | 0.4528 | 0.1417 | 0.4674 | 0.0146 | 0.1645 |
| High blood pressure | 2920 | 0.5591 | 0.7738 | 0.3117 | 0.7748 | 0.0010 | 0.0698 |
| Coronary heart disease | 2920 | 0.1373 | 0.5895 | 0.0169 | 0.5893 | -0.0002 | 0.0021 |
| Stroke | 2911 | 0.1763 | 0.4796 | 0.0298 | 0.4802 | 0.0006 | 0.0485 |
| Asthma | 2910 | 0.1233 | 0.3325 | 0.0137 | 0.3451 | 0.0126 | 0.1404 |
| Obesity | 2917 | 0.3735 | 0.5412 | 0.1388 | 0.5437 | 0.0025 | 0.0797 |
| Arthritis | 2919 | 0.1270 | 0.4560 | 0.0147 | 0.4583 | 0.0023 | 0.0720 |
| High cholesterol | 2920 | 0.3298 | 0.6047 | 0.1070 | 0.6087 | 0.0039 | 0.1004 |
| Cancer | 2918 | 0.0199 | 0.4462 | -0.0010 | 0.4526 | 0.0064 | 0.1037 |


Larger counties:

| Claims outcome | n | Raw r | CV D | CV P | CV D+P | Gain | Partial r |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Diabetes | 1017 | 0.5656 | 0.7558 | 0.3180 | 0.7627 | 0.0068 | 0.1818 |
| COPD | 1017 | 0.6349 | 0.6881 | 0.3998 | 0.6895 | 0.0014 | 0.0945 |
| Depression | 1017 | 0.3739 | 0.5857 | 0.1356 | 0.5938 | 0.0080 | 0.1443 |
| High blood pressure | 1017 | 0.6088 | 0.8043 | 0.3677 | 0.8140 | 0.0097 | 0.2215 |
| Coronary heart disease | 1017 | 0.1772 | 0.5888 | 0.0251 | 0.5880 | -0.0008 | 0.0153 |
| Stroke | 1016 | 0.1523 | 0.5812 | 0.0208 | 0.5807 | -0.0005 | 0.0321 |
| Asthma | 1016 | 0.0416 | 0.3202 | -0.0018 | 0.3496 | 0.0294 | 0.2096 |
| Obesity | 1016 | 0.4472 | 0.5794 | 0.1938 | 0.5805 | 0.0012 | 0.0518 |
| Arthritis | 1017 | 0.2103 | 0.5338 | 0.0409 | 0.5387 | 0.0049 | 0.1066 |
| High cholesterol | 1017 | 0.4823 | 0.6795 | 0.2302 | 0.6931 | 0.0136 | 0.2091 |
| Cancer | 1017 | 0.0798 | 0.5583 | 0.0013 | 0.5612 | 0.0029 | 0.0839 |


The largest gain here is asthma in larger counties, **0.029352**, compared with **0.023488** in the paired adjusted specification. Across all 112 independent rows, D beats P alone in **112/112**; the largest incremental gain is that 0.029352. Thus “0–2.3 R² points” describes Claude's chosen forms approximately, not every plausible form, and small negative gains must not be silently clipped to zero.

### Partial r given demographics and state, without MA

These are the Medicare partial correlations requested literally. The ACS values already appear above because no MA adjustment is used for ACS.

| Outcome | Actual/crude, all | Actual/crude, large | Adjusted/adjusted, all | Adjusted/adjusted, large |
| --- | --- | --- | --- | --- |
| Diabetes | 0.0850 | 0.1738 | 0.1663 | 0.1918 |
| COPD | 0.0850 | 0.1019 | 0.1236 | 0.1590 |
| Depression | 0.1981 | 0.1772 | 0.1379 | 0.1376 |
| High blood pressure | 0.0701 | 0.2210 | 0.1573 | 0.2422 |
| Coronary heart disease | 0.0013 | 0.0215 | 0.0286 | 0.0817 |
| Stroke | 0.0492 | 0.0383 | 0.0292 | 0.0527 |
| Asthma | 0.1536 | 0.2190 | 0.0870 | 0.1954 |
| Obesity | 0.0875 | 0.0583 | 0.0856 | 0.0603 |
| Arthritis | 0.0710 | 0.1021 | 0.0958 | 0.1284 |
| High cholesterol | 0.1001 | 0.2109 | 0.1357 | 0.2219 |
| Cancer | 0.0944 | 0.0803 | 0.0761 | 0.0662 |

### Source verification

**The supplied CMS rates match the live endpoint.** I first re-queried diabetes actual, diabetes standardized and asthma actual, 3,241 records each. I then extended the audit to all 11 requested conditions and both filters: **71,302/71,302 rates match exactly**. Source JSON responses, including the `dencat` population-size category omitted from the supplied CSV, are preserved here. This verifies the public data behind the MMD tool; it is not a claim that I manually inspected every county tooltip.

Representative checks, all exactly equal to the supplied CSV:

| County | FIPS | Diabetes actual | Diabetes age-standardized | Asthma actual |
| --- | --- | --- | --- | --- |
| Autauga, Alabama | 01001 | 31% | 32% | 7% |
| Los Angeles, California | 06037 | 33% | 33% | 8% |
| Miami-Dade, Florida | 12086 | 30% | 29% | 8% |
| New York, New York | 36061 | 22% | 21% | 8% |
| King, Texas | 48269 | 0% code | 0% code | 0% code |

The live [MMD tool](https://data.cms.gov/mmd-population/map.html) constructs requests to `https://data.cms.gov/data-api/v1/mmd-tool/` and parses its `rate` and `dencat` fields. The saved `mmd_map.html` and menu scripts document the connection to the public interface. The request uses source `prev_final_long_fltr12_racecat_all_sexcat_all_23_p`, population `f`, year `23`, geography `c`, measure `v`, the condition code, all demographic filters, and filter 1 or 2.

**Zeros are ambiguous, not verified absence of disease.** CMS says denominator cells below 11 are omitted; a positive numerator below three is displayed as 0%. True zero or a very small rate expressed at integer precision cannot be distinguished from suppression using `rate` alone. I therefore exclude all zero codes conservatively and retain that limitation. The supplied files contain whole-percentage values, but the exact rounding-versus-truncation rule was not established. [CMS MMD public FAQ, p. 7](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/MappingPublicFAQs.pdf).

**Age-standardized does not mean harmonized with PLACES.** CMS uses the national age distribution of the selected measure's Medicare population, with groups under 65, 65–74, 75–84 and 85+. Its published example weights are for 2012, not verified 2023 weights. The relevant CDC county estimates use the year-2000 US population standard. The standardized series is a reasonable additional predictor-comparison test, but cannot make Medicare FFS and adult PLACES rates the same estimand or justify subtracting their levels. [CMS technical documentation, section 6 and A.2.10](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/Mapping-Technical-Documentation.pdf), [CDC county prevalence age adjustment](https://www.cdc.gov/united-states-cancer-statistics/technical-notes/screening-hpv-risk-factor-prevalence.html).

**The requested “larger” threshold is an imperfect reliability proxy.** MMD reports denominator bands 11–499, 500–999, 1,000–4,999, 5,000–9,999 and ≥10,000, rather than exact denominators. [CMS technical documentation, section 8](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/Mapping-Technical-Documentation.pdf). Across the supplied GV geographies, 35 counties with OM≥5,000 have an MMD denominator band below 5,000. Thirty are in the larger hypertension comparison: 29 have band 1,000–4,999 and Kenai Peninsula has band 11–499. `large_panel_denominator_flags.csv` lists them.

Kenai Peninsula, Alaska (02122), is a concrete source discrepancy to flag before mapping: the live GV count is **12,302 OM beneficiaries**, but live MMD says **11–499**; actual diabetes is **22%**, standardized diabetes is **0%**, and standardized hypertension is **33%**. My model produces a hypertension residual of **−20.538 percentage points** for that county. It must not become an unqualified “better than expected” county. Both source responses were checked independently; the cause of their denominator discrepancy is unresolved, and I did not try to reconstruct suppressed numerators. The discrepancy is upstream of Claude's regression. All **3,197** supplied GV county count rows match the independent live re-query.

**ACS extraction also passes.** I re-queried official 2023 ACS5 B18102–B18107 groups and independently selected the four adult age groups by sex, eight numerator and eight denominator cells per type. All six rates reproduce across **3,222 counties/equivalents**, with maximum absolute error **7.11e−15 percentage points**. The live counts, labels and checks are saved. These are adult civilian noninstitutionalized denominators, not B01001's entire adult population. The population cutoff is not a survey sample-size cutoff. [Census B18102 metadata](https://api.census.gov/data/2023/acs/acs5/groups/B18102.json), [Census B18107 metadata](https://api.census.gov/data/2023/acs/acs5/groups/B18107.json).

## Part B: disagreements and code audit

**No demonstrated arithmetic bug in Claude's reported statistics or saved residuals.** With Claude's age/race grouping reconstructed independently from the earlier raw-derived ACS cells, all **238 cells** (34 rows × seven statistics) reproduce with maximum error **3.32e−15**. All **49,778 nonmissing saved county residuals** reproduce with maximum error **1.99e−12 percentage points**. Common-sample adjustment, same-fold model comparisons, pooled R², MA handling and the current unseen-state fallback pass on these data.

`disagreements_beyond_rounding.csv` enumerates every primary independent-versus-Claude difference exceeding 0.0005, the tolerance for a three-decimal display. There are **98**: 27 baseline CV R², 29 augmented CV R², 11 gains, and 31 partial correlations. None concerns n, raw r, or PLACES-only CV R². The maximum absolute differences are 0.007381 in baseline R², 0.006502 in augmented R², 0.001909 in gain and 0.018479 in partial r. **All are explained by the age/race feature-space choices.** The seed, sorting and pooled-score convention agree. Male versus female coding and different omitted education categories are equivalent linear parameterizations, not causes.

The audit found these implementation limitations:

* **Atlas coverage bug, although the comparison sample is correct.** `expected_vs_observed.py:133` requires PLACES to be nonmissing before fitting D or saving residuals at lines 159–169. This is necessary for comparing models on a common sample, but unnecessary for a demographics-only expected-versus-observed atlas. It drops **all 187 Kentucky/Pennsylvania counties for every outcome**, despite usable observed outcomes and predictors. For example, the same geographic spine supports 3,104 diabetes counties without the PLACES requirement versus 2,917 with it, and 3,143 ACS counties versus 2,956. Fit the production atlas baseline on its own observed-plus-covariate support, separate from the paired validation panel. Starting from PLACES also excludes Loving County, Texas, before any outcome-specific reliability assessment.
* **Reliability information is discarded before the atlas export.** `fetch_mmd_prevalence.py:48–57` saves rates without `dencat`; `fetch_observed_outcomes.py:59–65` saves ACS percentages without contributing counts or MOEs; `expected_vs_observed.py:169` exports only residuals. Those residuals cannot by themselves distinguish suppression, small analysis denominators, survey imprecision or source mismatch. The Kenai example demonstrates why the GV count alone is insufficient. Keep these fields, reason-coded missingness and source flags in the atlas data contract.
* **The zero comment and presentation labels overstate what is known.** `expected_vs_observed.py:49` says zero marks suppressed cells. Zero can represent suppression, but is not an exclusive suppression flag. Exclusion is a defensible conservative choice, not a verified classification of every zero. The frozen independent script's corresponding comment is also too categorical; `PART_A_VALIDATION.md` corrects it without changing frozen numerical files. Labels “Stroke,” “Cancer,” and “High cholesterol” conceal CMS stroke/TIA, four-site cancer and hyperlipidemia versus the different PLACES definitions. Preserve explicit phenotype and universe labels.
* **Future-data hardening is still needed, with no observed effect here.** The fetcher does not mask negative Census special codes and sums with default missing-value skipping; joins do not validate cardinality, and `pivot_table` can silently aggregate duplicate rates. This run has no duplicate keys, invalid contributing ACS counts or incorrect adult-cell mapping. Add assertions and deliberate missing-data rules before automated refreshes. The state fallback works here; if reused on very small subsets, test the omitted-reference-state case as well.

There is an additional coverage limitation independent of those bugs: **26 PLACES geographies have no MMD row**, including Connecticut's nine planning regions, 14 Alaska geographies, Kalawao, Oglala Lakota and Manassas Park. Some are geography-vintage incompatibilities; not every absence is suppression. Do not repair them by name matching or zero-filling. Harmonize geography from documented crosswalks or display unavailable. The unmatched FIPS and coverage accounting are saved.

### Post-freeze sensitivity checks

I ran five additional shuffled ten-fold partitions, keeping the same primary feature specification. These ranges describe split sensitivity, not confidence intervals:

| Larger-county pair | Primary gain | Gain range over five additional seeds |
| --- | --- | --- |
| Medicare asthma, adjusted | 0.023488 | 0.022415–0.027212 |
| Medicare hypertension, adjusted | 0.012061 | 0.011171–0.012727 |
| Medicare hyperlipidemia, adjusted | 0.015193 | 0.015476–0.017897 |
| ACS mobility, crude | 0.008772 | 0.008152–0.009580 |

A fixed exploratory expansion using each demographic share's square and its interaction with poverty reduces median larger-county gains from **0.005447 to 0.002634** for Medicare and from **0.002299 to 0.000013** for ACS. It does not improve every baseline, and it was not tuned or selected as a winner. Asthma's adjusted larger-county gain remains **0.026236**. This is consistent with some PLACES increment representing nonlinear demographic structure, but does not identify how much is county-specific health information.

Removing MA share on the same Medicare county samples leaves gains small, with the largest adjusted larger-county gain **0.026295**. Requiring the MMD denominator category itself to be at least 5,000 yields larger-county adjusted gains from **−0.001449 to 0.023951**. Excluding Kenai where it has a nonzero standardized outcome also leaves the broad conclusion unchanged. Full values and sample sizes are in `sensitivity_results.csv`.

## Part C: eight methods findings, most important first

1. **This is a fair test of incremental linear prediction for these outcomes, not of whether PLACES contains any additional information.** The common-sample, held-out nested comparison directly answers the operational question. It supports small incremental R² in this panel. Positive gains are repeatable for several outcomes, and partial r reaches 0.244 in the larger adjusted Medicare panel. A null or negative gain can reflect noise, population mismatch, linear-model misspecification or insufficient precision. No equivalence margin, uncertainty interval or spatial validation establishes that a useful increment has been ruled out. Nor does baseline superiority over PLACES alone answer the incremental question by itself.

2. **The Medicare comparisons are external proxy-outcome tests with substantial population and phenotype mismatch.** Medicare FFS is mostly older adults, with younger disabled beneficiaries; PLACES is adult population prevalence. A county's adult diabetes pattern need not rank its selected FFS population the same way. Stroke/TIA versus stroke, four-site cancer versus non-skin cancer or melanoma, and hyperlipidemia versus reported high cholesterol among screened adults are not interchangeable endpoints. Age adjustment removes only a specified age-distribution component; different standards and age-specific relationships remain. Use actual and adjusted analyses as complementary tests, not as alternative routes to a common “true prevalence.” [CDC health-outcome definitions](https://www.cdc.gov/places/measure-definitions/health-outcomes.html), [CDC current measure display](https://places.cdc.gov/).

3. **“Observed” means directly ascertained in the named source, not clinically measured population disease.** Claims identify conditions from recorded diagnoses and services. Diagnosis opportunity, access, coding practices and enrollment affect what is recorded; an unexpectedly low claims rate can reflect underdiagnosis or incomplete capture as well as lower morbidity. ACS is a direct survey estimate of reported difficulty, with sampling and nonsampling error. These are useful observations, but neither establishes a gold standard for PLACES or causal county performance. [CMS case-identification FAQ](https://www.cms.gov/About-CMS/Agency-Information/OMH/Downloads/MappingPublicFAQs.pdf), [CDC disability definitions](https://www.cdc.gov/places/measure-definitions/disability.html).

4. **MA share and state adjustment change the estimand; they do not remove selection or make the baseline purely demographic.** MA/(MA+OM) is a sensible sensitivity covariate, but it cannot recover the health mix of excluded MA beneficiaries or all enrollment transitions. The GV count definitions refer to specified coverage throughout entitled months or the year; this ratio should be labeled as the share among the two counted groups, not assumed identical to an official all-beneficiary participation rate. County-wide ACS shares also do not describe the FFS risk pool exactly. State fixed effects absorb real policy, healthcare-system and diagnostic differences. Report a within-state comparator explicitly, and retain a demographics-only national comparator if the goal includes showing between-state disparities. [CMS GV dictionary](https://data.cms.gov/sites/default/files/2026-05/267755af-8e26-4bcd-a3ea-fef41c96b7fc/2014-2024%20Original%20Medicare%20Geographic%20Variation%20Data%20Dictionary.pdf).

5. **Integer reporting, suppression and denominator mismatch limit residual precision.** Whole-percentage claims values have coarse resolution, especially for low-prevalence endpoints. Suppression is informative missingness, concentrated in small cohorts; dropping zeros is conservative but changes support. Larger GV counties are usually more stable, but the audited denominator bands show that the requested threshold is not a guarantee. Preserve the MMD band and ambiguity flags, avoid reconstructing suppressed counts, and investigate source-discrepant extreme residuals. Do not calculate a binomial standard error using GV OM as though it were the exact MMD denominator, or treat a standardized rate as one binomial proportion.

6. **ACS offers closer population and question alignment, but shares measurement structure with the predictors.** Outcomes and covariates use the same 2019–2023 ACS period, so shared survey error, weights, imputation and demographic relationships can contribute to predictive fit. This is not literal leakage of the disability outcome into the supplied X, but it prevents calling the benchmark wholly independent. Survey mode, proxy reporting and the five-year versus BRFSS annual time window remain differences. A population of 20,000 adults is not 20,000 respondents. Retain MOEs and estimate uncertainty for the constructed ratios, using variance replicates where available or documented approximations that acknowledge covariance. [Census MOE guidance](https://www.census.gov/help/topics/faq.do-i-need-to-consider-the-margins-of-error-when-comparing-acs-estimates.html), [Census variance replicate tables](https://www.census.gov/programs-surveys/acs/data/variance-tables.html).

7. **The validation supports interpolation within the observed states and this data vintage.** Random county folds leave neighboring counties and most state peers in training. The tested demographic margins approximate the PLACES inputs; they do not reproduce the fitted individual-level MRP or its joint poststratification cells. The repeated-fold and nonlinear checks strengthen the descriptive result, but are not spatial, temporal or out-of-state tests. Before ranking counties, predefine the target population and weighting, validate spatial blocks within states and a later period, and quantify stability of residual signs and magnitudes. Do not infer that the unexplained part is exclusively the county random effect. [CDC PLACES methodology](https://www.cdc.gov/places/methodology/index.html).

8. **The atlas can use observed-minus-expected, provided it is framed as a descriptive, reliability-aware contrast.** Define expected for county i as a cross-fitted prediction of the **same source-specific observed outcome**, using prespecified demographic predictors and state, plus the selected Medicare enrollment covariates. For the main burden view, use actual claims prevalence and crude ACS difficulty prevalence. Keep a separately labeled standardized view if desired. PLACES is an optional predictor benchmark or context layer; it should not be subtracted from CMS or ACS as if it were the expected value on the same scale. Fit the atlas on every eligible observed-plus-covariate county, without requiring PLACES availability.

For display, label the main value **“Observed prevalence minus demographic-and-state prediction, percentage points.”** For Medicare add **“Recorded diagnoses among Original Medicare beneficiaries, 2023; adjusted for county MA share.”** For ACS use **“Reported difficulty among civilian noninstitutionalized adults, 2019–2023.”** State the age-standardization status and exact phenotype in each layer. Expected is an empirical peer comparator, not an attainable target, an equitable rate or the amount of disease demographics cause.

Show observed, expected and their difference together; use a zero-centered diverging scale with consistent limits within an outcome. Keep missing, suppressed/ambiguous and uncertain values visibly distinct from zero. Include denominator band or survey denominator, MOE/uncertainty when supported, geographic coverage, source period, fold/model version and source-quality flags in the county detail. Cross-fitted residuals prevent direct self-fitting, but their county values still depend on the partition; evaluate stability across partitions.

For a stable atlas signal, estimate a latent county deviation with an explicit measurement-error or hierarchical model and partially pool unreliable counties toward the chosen baseline. Distinguish the **raw observed-minus-predicted difference** from the **shrunken estimated deviation** in both labels and downloads. Shrinkage needs defensible uncertainty inputs; the present integer MMD rates and GV proxy counts are insufficient for precise county intervals. Until those inputs are adequate, use denominator/quality flags and cautious descriptive display rather than confident rankings. Do not label negative residuals “good performance,” or positive residuals “excess preventable disease,” without an additional causal argument.

## Verdict and recommended claim

**Approved as an exploratory predictive result, with qualification; not cleared as an unqualified county ranking or disease-performance atlas.**

Recommended wording:

> In these available counties, demographic composition plus state, with Medicare Advantage share for Medicare outcomes, predicts the directly ascertained claims and survey outcomes better than PLACES alone. Adding PLACES usually improves held-out linear-model prediction only slightly: median R² gains range from approximately zero to 0.0055 in the primary comparisons, with a maximum of 0.0235; the additional actual/crude Medicare comparison reaches 0.0294. Some small gains persist across partitions. These results do not establish that PLACES contains no additional health information or that the residuals measure avoidable disease or county performance.

The most urgent production changes are to separate atlas coverage from the PLACES comparison panel, retain reliability metadata, and prevent source-discrepant counties from receiving unqualified residual interpretations. The Kenai denominator discrepancy remains a specific unresolved source issue.

## Deliverables and verification

`REPORT.md` is this report. `comparison.csv` contains independent, Claude and independently matched-specification values. `disagreements_beyond_rounding.csv` enumerates all 98 primary non-rounding differences. `matched_spec_checks.csv` and `saved_residual_checks.csv` verify every reported cell and residual. `independent_results.csv` and `independent_predictions.csv` preserve Part A; `PART_A_FROZEN.json` hashes the analysis and inputs, and `PART_A_VALIDATION.md` records the source-verification boundary before Part B.

`reviewed_snapshot/` and `reviewed_sources.json` identify the precise Claude code/results reviewed. `cms_denominator_categories.csv`, the live response JSONs, `endpoint_spotchecks.csv`, `acs_live_checks.csv`, `acs_disability_counts_live.csv`, `acs_disability_mapping.csv`, `gv_verification.json`, `coverage_audit.csv`, and denominator-flag files preserve the source and coverage audit. `sensitivity_results.csv` contains the post-freeze checks. `final_verification.json` records completion and hash checks.

## Shortcuts taken

* Reused the authorized independently built ACS covariates instead of re-extracting all five original summary files. For the exact Claude specification I reconstructed the older-age split from the saved raw-derived B01001 cells. The current disability and Medicare sources were re-queried independently.
* CMS verification checked the endpoint used by the tool and its public client code, not manually rendered county tooltips. The cause of Kenai's source discrepancy, the exact integer-rounding rule and the numerical 2023 age-standardization weights remain unverified; no suppressed numerator was inferred.
* Excluded all ambiguous CMS zeros. I did not identify which represent genuine zero, suppression or quantization, and did not fit a censoring model. The frozen script's zero-code comment overstates this distinction; the recorded validation note and this report correct it.
* Models use county demographic margins, not beneficiary-level FFS composition or the exact CDC fitted MRP. Alternative prevalence forms in the CSV are sensitivity specifications, not independent outcomes. No causal attribution or phenotype harmonization is claimed.
* Used one primary partition plus five additional partitions on the 34 main comparison rows; the additional actual/crude and cross-form rows use one partition. The nonlinear expansion is exploratory. No spatial/temporal validation, population-weighted scoring, full errors-in-variables model, county uncertainty intervals or shrinkage was implemented, because this task reviews the empirical test rather than builds the production atlas.
* I did not alter Claude's code or output files under the write-only review scope. This is the requested independent Codex review leg; I did not commission another model to approve it or claim that the project's separate Agy check is complete.
* The four mortality pairs added concurrently were excluded from this review's verdict; the requested 17-pair results were checked against the expanded current files and are unchanged.
