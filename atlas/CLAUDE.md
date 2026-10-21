# Atlas track: notes for assistants

Expected-vs-observed county health atlas and the CDC PLACES analysis behind it. Project-wide rules (triple check, Census key, Python) are in the root `CLAUDE.md`. Every script anchors itself at the repository root, so run them from anywhere: `.venv/bin/python atlas/scripts/<name>.py`.

## Direction (decided 2026-10-20)
Johnattan chose the **expected-vs-observed atlas**: county demographics + state (what PLACES is built from) as the expectation, directly measured outcomes (Medicare claims prevalence, ACS disability, CDC WONDER mortality) as the observation; the map shows observed minus expected.

## Data facts learned
- PLACES 2025 county release: Kentucky and Pennsylvania are missing for most measures (187 counties); the 7 social-needs measures cover 39 states + DC (2,299 counties).
- ACS table-based summary files (`www2.census.gov/.../table-based-SF/data/5YRData/acsdt5y2023-<table>.dat`) match the API exactly (checked 5 variables x 3,222 counties, 2026-10-20).
- Medicare claims prevalence comes from the CMS Mapping Medicare Disparities endpoint (downloadable chronic-conditions files were retired); keep the `dencat` bands. County PQI columns in the 2023 Geographic Variation file are empty.
- WONDER county mortality: `atlas/scripts/fetch_wonder.py` drives the WONDER form headlessly (Playwright 1.58.0, chromium-headless-shell) after accepting the NCHS agreement (Johnattan approved 2026-10-20). **Counts of 9 or fewer, zero included, are suppressed and must never be published**; `export_site_data.py` refuses to export if any mortality row fails this. Connecticut cannot be matched (old counties vs planning regions).

## Pipeline (local stages, in order)
1. `fetch_acs_county.py` (county covariates from the ACS summary files), `fetch_observed_outcomes.py`, `fetch_mmd_prevalence.py`, `fetch_wonder.py`, `fetch_socrata.py` (network pulls into `data/raw/`)
2. `build_mortality_smr.py` (indirect SMRs)
3. `covariate_test.py` and `covariate_charts.py` (how much of PLACES demographics and state reproduce) -> `atlas/outputs/covariate_test/`
4. `expected_vs_observed.py` (PLACES vs measured outcomes) -> `atlas/outputs/expected_vs_observed/`
5. `build_atlas_data.py` -> `atlas/outputs/atlas/` (regenerable, git-ignored)
6. `export_site_data.py` -> `atlas/site/data/`; `bundle_site.py` -> `atlas/dist/` (single-file HTML, git-ignored)

## Results and reviews
- Shared-covariate test: summary in `atlas/outputs/covariate_test/REVIEW_SUMMARY.md`.
- PLACES vs measured outcomes and atlas fixes: `atlas/outputs/expected_vs_observed/REVIEW_SUMMARY.md`. Supported claim: PLACES adds only slightly beyond demographics plus state; not that it carries no information.
- Review reports are in `atlas/reviews/`. Reports written before 2026-10-21 cite the old top-level paths (`scripts/`, `outputs/`, `site/`); those are dated records and were not rewritten.

## Site (built 2026-10-21)
- `atlas/site/index.html` (project page) and `atlas/site/atlas.html` (interactive atlas), static D3. Preview: `.claude/launch.json` ("site", port 8731).
- Reviewed by Codex and Agy, then Codex verified the fixes (`atlas/reviews/site_*`, `atlas/reviews/site2_codex_astra/`); the second-round fixes were applied using Codex's own tested wording.
- **Live on GitHub Pages since 2026-10-21 (Johnattan asked the same day, reversing the earlier keep-local decision):** https://j-garciaruiz.github.io/us-public-health-data/atlas/ . Every push to master that touches `atlas/site/` redeploys it.

## Layout change (2026-10-21)
The atlas track moved from the repository top level into `atlas/` to mirror `pharma/`. Re-running every local stage from another working directory reproduced all 58 output files byte for byte.
