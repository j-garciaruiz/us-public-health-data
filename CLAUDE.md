# US Data: project notes for assistants

Exploration lab for US public health data (portfolio for US job search). See README.md for the source catalog.

## Standing rules
- **Data work gets a triple check (Johnattan, 2026-10-20).** Any analysis that becomes a claim, chart or deliverable is independently replicated by Codex (`gpt-6-astra`, effort high) from raw data, and method-reviewed with an independent recompute by Agy (`gemini-4-argon-high`). Briefs live in `reviews/`; each reviewer writes only in its own `reviews/<name>/` folder and sees Claude's code only after producing its own numbers. Report each verdict and any disagreement.
- Census API key is in `.env` (`CENSUS_API_KEY`, git-ignored, activated 2026-10-20). County-wide API pulls need it. Never print it.
- Python: project venv `.venv` (`requirements.txt`). Raw data in `data/raw/` is git-ignored; scripts re-fetch it.

## Data facts learned
- PLACES 2025 county release: Kentucky and Pennsylvania are missing for most measures (187 counties); the 7 social-needs measures cover 39 states + DC (2,299 counties).
- ACS table-based summary files (`www2.census.gov/.../table-based-SF/data/5YRData/acsdt5y2023-<table>.dat`) match the API exactly (checked 5 variables x 3,222 counties, 2026-10-20).
- cdc.gov pages return 403 to curl (bot blocking); they open in a browser.

## Direction (decided 2026-10-20)
Johnattan chose the **expected-vs-observed atlas**: county demographics + state (what PLACES is built from) as the expectation, directly measured outcomes (Medicare claims prevalence, ACS disability, CDC WONDER mortality) as the observation; the map shows observed minus expected.

## Current work (updated 2026-10-20, after the session restart)
- **Atlas data** (`scripts/build_atlas_data.py` -> `outputs/atlas/atlas_county_long.csv`, regenerable, git-ignored): 34 outcomes x 2 modes (national default, within-state toggle); observed, cross-fitted expected (10 x 10-fold), raw and empirical-Bayes-shrunk difference, reliability and tiers. Medicare actual is the main claims view; age-standardized is a labeled alternative.
- **PLACES vs measured outcomes** (`scripts/expected_vs_observed.py`): reviewed by Codex and Agy; summary in `outputs/expected_vs_observed/REVIEW_SUMMARY.md`. Supported claim: PLACES adds only slightly beyond demographics plus state; not that it carries no information.
- **Mortality**: `scripts/fetch_wonder.py` drives the WONDER form headlessly (Playwright 1.58.0, chromium-headless-shell) after accepting the NCHS agreement (Johnattan approved 2026-10-20); `scripts/build_mortality_smr.py` builds indirect SMRs. Counts of 9 or fewer, zero included, are suppressed and must never be published. Connecticut cannot be matched (old counties vs planning regions).
- Medicare claims prevalence: CMS Mapping Medicare Disparities endpoint (downloads retired); keep `dencat` bands. County PQI columns in the 2023 Geographic Variation file are empty.
- Codex verified the atlas fixes and its five findings are applied (`reviews/atlas_codex_astra/REPORT.md`, summary appended to `outputs/expected_vs_observed/REVIEW_SUMMARY.md`).
- Pharmaceutical data track runs in a separate session on branch `claude/pharma-data-eae972` (worktree); not merged here.
- **Next:** after the Codex check, design the atlas front end (interactive county map with observed/expected/difference, reliability tiers, national vs within-state toggle) and the explainer on what PLACES can and cannot tell you.

Earlier: shared-covariate test of PLACES (`scripts/covariate_test.py`, charts in `scripts/covariate_charts.py`, results in `outputs/covariate_test/`). Codex review done and fixes applied; Agy review pending. Literature context: `literature/places_atlas_literature_review.md`.
