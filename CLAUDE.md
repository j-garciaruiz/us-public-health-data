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

## Current work (2026-10-20)
Shared-covariate test of PLACES (`scripts/covariate_test.py`, charts in `scripts/covariate_charts.py`, results in `outputs/covariate_test/`). Under review by Codex and Agy (`reviews/`). Literature context: `literature/places_atlas_literature_review.md`.
