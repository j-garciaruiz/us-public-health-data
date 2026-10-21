Read reviews/covariate_test_brief.md first. Your review folder is reviews/agy_argon/ (write only there). You may use data/raw/acs_county_2023.csv as ready-made county covariates (built by another analyst; check a few values against the raw summary files before trusting it).

Task: method critique plus independent recompute of the headline numbers.

1. Methods (most important): is regressing each PLACES measure on county covariates + state fixed effects, then correlating residuals, a valid way to answer the question? Explain what the residual contains in an MRP model (county random effect, poststratification nonlinearity, covariate mismatch). Could the test overstate how much inputs explain? Understate? Is "share of raw covariance remaining in the residuals" a sensible summary? Is the ACS uninsurance benchmark a fair comparison given ACS sampling error in small counties? Check the PLACES methodology page and Kong & Zhang 2020 for anything that changes the reasoning.
2. Recompute with your own code: (a) median cross-validated R-squared across the 40 age-adjusted measures; (b) diabetes~foodinsecu raw and partial correlation and covariance share; (c) the uninsurance benchmark (PLACES access2_crudeprev vs ACS uninsurance, both on the same covariates, all counties and >= 20,000 adults).
3. Only after your numbers are saved, compare with outputs/covariate_test/summary.txt, highlight_pairs_adjprev.csv and benchmark_uninsurance.csv. Report disagreements beyond rounding.

Write reviews/agy_argon/REPORT.md: your numbers, the comparison, at most 8 methods findings ranked by importance, and a verdict on whether the claim "most of the county-to-county variation and of the strong correlations is reproduced by the model inputs" holds. Keep code in reviews/agy_argon/.
