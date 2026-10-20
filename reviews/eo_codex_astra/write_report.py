from pathlib import Path
import pandas as pd
from replicate import HERE
from compare import LABELS

c=pd.read_csv(HERE/"comparison.csv")
r=pd.read_csv(HERE/"independent_results.csv")
freeze=__import__("json").loads((HERE/"PART_A_FROZEN.json").read_text())

def table(headers,rows):
    return "| "+" | ".join(headers)+" |\n| "+" | ".join(["---"]*len(headers))+" |\n"+\
        "\n".join("| "+" | ".join(map(str,row))+" |" for row in rows)+"\n"

def compare_table(sample):
    rows=[]
    for x in c[c["sample"]==sample].itertuples(index=False):
        pair=lambda k:f"{getattr(x,k+'_independent'):.4f} / {getattr(x,k+'_claude'):.4f}"
        rows.append([x.outcome,int(x.n_independent),f"{x.raw_r_independent:.4f}",pair("cv_demo"),
                     f"{x.cv_places_independent:.4f}",pair("cv_both"),pair("gain"),pair("partial_r")])
    return table(["Outcome","n, both","Raw r, both","CV D, I / C","CV P, both",
                  "CV D+P, I / C","Gain, I / C","Partial r, I / C"],rows)

def crude_table(sample):
    d=r[(r.source=="Medicare")&(r.fltr==1)&(r.places_type=="crudeprev")&(r["sample"]==sample)]
    return table(["Claims outcome","n","Raw r","CV D","CV P","CV D+P","Gain","Partial r"],
                 [[LABELS[x.condition],x.n,*[f"{getattr(x,k):.4f}" for k in
                    ["raw_r","cv_demo","cv_places","cv_both","gain","partial_r"]]] for x in d.itertuples(index=False)])

summary=r[((r.source=="Medicare")&(r.fltr==2)&(r.places_type=="adjprev"))|
          ((r.source=="ACS")&(r.places_type=="crudeprev"))]
sumrows=[]
for (source,sample),d in summary.groupby(["source","sample"],sort=False):
    sumrows.append([source,sample,f"{d.cv_demo.min():.4f}–{d.cv_demo.max():.4f}",
                    f"{d.gain.median():.4f}",f"{d.gain.min():.4f}–{d.gain.max():.4f}"])
st=table(["Source","Sample","Baseline CV R² range","Median gain","Gain range"],sumrows)

text=f"""# Independent review: PLACES versus directly observed county outcomes

Reviewed 2026-10-20. **The narrow prediction claim is supported; an absence-of-information claim is not.** Demographic composition plus state, with Medicare Advantage share for Medicare, beats PLACES alone for every one of the 17 pairs in both samples. Adding PLACES usually improves held-out R² only slightly. Some positive increments persist across repeated folds, especially larger-county asthma, hypertension, hyperlipidemia, and ACS mobility. The present residual export is an exploratory layer, not a publication-ready measure of excess disease or county performance.

## Independence, scope and execution

I completed and froze the independent results at **{freeze['frozen_utc']}**, before opening `scripts/expected_vs_observed.py`, `scripts/fetch_observed_outcomes.py`, or `outputs/expected_vs_observed/`. The project instruction file `CLAUDE.md` was read first and exposed its short headline conclusion; the analysis was therefore implementation-independent, not fully blinded to the claimed direction. I reused my previously independently constructed `reviews/codex_astra/covariates.csv`, as authorized, and did not import Claude's analysis functions. The pre-existing review report was background.

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

{st}

Here an R² gain of 0.01 means one percentage point of county outcome variance, not a one-point increase in disease prevalence. The outcome and RMSE units are prevalence percentage points. All counties means all available matched counties, not a complete national panel.

### Numbers versus Claude: all available counties

I = independent Part A; C = Claude's saved output. Counts, raw correlations and PLACES-only CV scores agree; those columns are shown once. Medicare uses MMD `fltr=2` versus PLACES age-adjusted prevalence. ACS uses direct crude disability prevalence versus PLACES crude prevalence.

{compare_table('all')}

### Numbers versus Claude: larger counties

{compare_table('large')}

For larger-county age-standardized asthma, independent CV R² rises from **0.292908 to 0.316395**, a gain of **0.023488**; RMSE falls from **1.006280 to 0.989426 percentage points**. For hypertension, R² rises by **0.012061** and RMSE falls from **2.864368 to 2.773653 points**. The latter removes about **6.23% of baseline held-out squared error**, despite its small gain as a fraction of total outcome variance. “Small” should be tied to intended use and error reduction, not treated as synonymous with zero.

### Actual Medicare prevalence versus crude PLACES

These are additional independent tests; Claude did not report this specification. D and partial r include MA share. They are more natural inputs for a descriptive burden atlas, but they still compare different populations and ascertainment systems.

All matched counties:

{crude_table('all')}

Larger counties:

{crude_table('large')}

The largest gain here is asthma in larger counties, **0.029352**, compared with **0.023488** in the paired adjusted specification. Across all 112 independent rows, D beats P alone in **112/112**; the largest incremental gain is that 0.029352. Thus “0–2.3 R² points” describes Claude's chosen forms approximately, not every plausible form, and small negative gains must not be silently clipped to zero.

### Partial r given demographics and state, without MA

These are the Medicare partial correlations requested literally. The ACS values already appear above because no MA adjustment is used for ACS.

"""
prrows=[]
for condition in LABELS:
    sub=r[(r.source=="Medicare")&(r.condition==condition)]
    if sub.empty: continue
    vals=[]
    for fltr,typ,sample in [(1,"crudeprev","all"),(1,"crudeprev","large"),(2,"adjprev","all"),(2,"adjprev","large")]:
        vals.append(f"{sub[(sub.fltr==fltr)&(sub.places_type==typ)&(sub['sample']==sample)].iloc[0].partial_r_no_ma:.4f}")
    prrows.append([LABELS[condition],*vals])
text+=table(["Outcome","Actual/crude, all","Actual/crude, large","Adjusted/adjusted, all","Adjusted/adjusted, large"],prrows)
text+="""
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
"""
(HERE/"REPORT.md").write_text(text)
assert "\u2014" not in text
print("Wrote REPORT.md:",len(text.split()),"words")
