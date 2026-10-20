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

## Current work (2026-10-20)
- `scripts/expected_vs_observed.py`: demographics + state predict measured outcomes better than PLACES for all 17 pairs; adding PLACES gains 0-2.3 R2 points. Under Codex review (`reviews/eo_codex_astra/`).
- Medicare claims prevalence comes from the CMS Mapping Medicare Disparities endpoint (CMS retired the chronic-conditions downloads); county PQI columns in the 2023 Geographic Variation file are empty.
- WONDER county mortality needs Johnattan's OK to accept the NCHS data use agreement (no publishing counts of 9 or fewer).

Earlier: shared-covariate test of PLACES (`scripts/covariate_test.py`, charts in `scripts/covariate_charts.py`, results in `outputs/covariate_test/`). Codex review done and fixes applied; Agy review pending. Literature context: `literature/places_atlas_literature_review.md`.
