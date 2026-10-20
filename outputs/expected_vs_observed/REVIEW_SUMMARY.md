# Expected vs observed: review summary (2026-10-20)

Independent reviews: Codex (GPT-6 Astra, high; `reviews/eo_codex_astra/REPORT.md`) and Agy (Gemini 4 Argon, high; `reviews/eo_agy_argon/REPORT.md`). Both rebuilt the comparisons before reading Claude's code.

## Agreed result
Across 21 pairs (11 Medicare claims conditions, 6 ACS disability types, 4 WONDER mortality causes), county demographics plus state (plus Medicare Advantage share for Medicare) predict the measured outcome better than PLACES alone in every pair. Adding PLACES improves out-of-sample R2 by under 1 point in 37 of 42 outcome-sample comparisons (Agy) and never by more than about 2.4 points; Codex found the small gains for asthma, hypertension, hyperlipidemia and mobility repeatable across splits.

Supported wording: PLACES adds only slightly to predicting these measured outcomes once demographics and state are known. Not supported: that PLACES contains no additional information, or that residuals measure avoidable disease or county performance.

## Bugs found and fixed
- WONDER zero-death cells were kept as SMR 0; zero is a count of 9 or fewer, so they are now suppressed (Agy bug 1; NCHS rule).
- Kusilvak Census Area, AK (02270 -> 02158) is a rename, now matched (Agy bug 2). Agy's quoted 81 heart deaths for Kusilvak was wrong; the WONDER file shows 74.
- Expected deaths rescaled so matched-county national totals reconcile (ACS age structure ran about 1.4-1.8% low; Agy section 2.2).
- Atlas no longer requires PLACES, so Kentucky and Pennsylvania are included (Codex audit, Agy bug 3).
- Atlas expectations are averaged over 10 repeats of 10-fold cross-fitting, with one indicator per state and no intercept, so single splits, DC and small states no longer drive values (Agy bugs 4-5).
- Medicare denominator bands and ACS margins of error are kept; CMS phenotype labels made exact (Codex).

## Atlas design adopted
- Default "national" expectation (demographics only, so state differences stay visible) with a "within-state" toggle (Agy finding 7).
- Empirical Bayes shrinkage of observed minus expected with DerSimonian-Laird between-county variance and reliability tiers (Agy finding 8, Codex finding 8).
- Labels: observed values are recorded diagnoses (Medicare), reported difficulty (ACS) or certified causes of death (WONDER), not clinically measured disease. Extremes can reflect coding and access (e.g. Louisiana diabetes deaths, New York City Medicare diabetes claims).

## Open
Medicare shrinkage uses an approximate denominator (GV count clipped to the CMS band). Connecticut cannot be matched for mortality without a town-level crosswalk. Spatial and out-of-period validation not done.
