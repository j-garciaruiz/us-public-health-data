# Expected vs Observed: US county health atlas

Two linked pieces of work on US county health data, started 2026-10-20.

1. **How much of CDC PLACES is demographics?** PLACES publishes model-based county estimates for 40 health measures. County demographics plus state reproduce a median 96% (crude prevalence) to 97% (age-adjusted) of their county-to-county variation in counties the model did not see. Against 21 directly measured outcomes, adding PLACES to demographics and state improves prediction by at most 0.8 percentage points of R² in the full samples and 2.3 in restricted larger-county samples.
2. **The atlas.** For 34 outcome layers (deaths from CDC WONDER, Medicare claims, Census disability), each county's measured value is compared with a prediction from demographics, with or without state, with reliability-aware smoothing of small-county noise.

Results are descriptive comparisons with a model, not estimates of preventable disease or county performance.

## Layout

```
atlas/
  scripts/      data pulls, analysis, atlas build, site export and bundling (see CLAUDE.md for the run order)
  outputs/      covariate_test/, expected_vs_observed/ (with REVIEW_SUMMARY.md files), atlas/ (git-ignored)
  site/         index.html (project page), atlas.html (interactive atlas), assets/, data/, vendor/, fonts/, design/
  dist/         single-file shareable HTML (git-ignored; rebuild with scripts/bundle_site.py)
  literature/   places_atlas_literature_review.md
  reviews/      Codex and Agy briefs and reports for every stage
```

Raw data lives in the repository's shared `data/raw/` (git-ignored).

## Viewing the site

Open `atlas/site/index.html` in a browser (no server needed), or the shareable single files in `atlas/dist/`. Kept local by decision of 2026-10-21; not published.

## Data sources

CDC PLACES 2025 county release; CDC WONDER Multiple Cause of Death 2018-2024 (used under the NCHS data use rules: no counts of 9 or fewer are shown); CMS Mapping Medicare Disparities 2023; Census American Community Survey 2019-2023; Census 2023 cartographic boundaries.
