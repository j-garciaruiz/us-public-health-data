# Shared-covariate test: review summary (2026-10-20)

Reviewed independently by Codex (GPT-6 Astra, high; `reviews/codex_astra/REPORT.md`) and Agy (Gemini 4 Argon, high; `reviews/agy_argon/REPORT.md`). Both rebuilt the analysis from raw files before seeing Claude's code.

## Agreed result
County demographics (age, sex, race/ethnicity, education, adults below 150% of poverty) **plus state** reproduce a median 97.1% of the county-to-county variation in the 40 age-adjusted PLACES measures, out of sample (Codex 0.9709, Agy 0.9711, Claude 0.9712). Without state: about 83%. Strongly correlated pairs (|r| >= 0.7): 279; their leftover correlations fall to a median |r| of 0.16 across all pairs.

## Fixed after review
- Pairwise leftovers are now computed on the counties both measures share (Codex bug 1); diabetes vs food insecurity leftover r = 0.62.
- Covariance share computed directly on the common sample (Codex bug 2).
- Washington, DC no longer inherits Alabama's state effect in cross-validation (Codex bug 3).
- Chart wording no longer implies the health relationships are spurious; "demographics" now reads "demographics and state".

## How to state it
- Say: the published PLACES county estimates can be almost entirely reconstructed from demographics plus state. Not: the underlying health relationships are fake.
- State effects carry real survey information (state policy, behavior), not only demographics (Agy finding 1, Codex finding 3).
- Do not headline "1.2% of covariance remains": with R2 near 0.98 for both measures it cannot exceed about 1.9% even for perfectly correlated leftovers (Agy finding 2). Report leftover correlation and spread instead.
- Part of the leftover correlation is model curvature: on the logit scale diabetes vs food insecurity drops from 0.62 to 0.48 (Agy finding 3).
- Uninsurance benchmark: in counties with >= 20,000 adults, after correcting for ACS sampling error, demographics plus state explain about 86% of measured uninsurance vs 98% of the PLACES version, a real gap of about 12 points (Agy finding 5). In all counties, part of the gap is ACS noise.

## Open (not done)
Repeated and spatially blocked cross-validation; a common 2,299-county panel; propagating PLACES and ACS margins of error.
