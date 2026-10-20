# Review brief: do PLACES county correlations survive removing the model's inputs?

Project folder: `/Users/hari/Documents/VSC Python/US Data`

## The question

CDC PLACES publishes model-based county estimates for 40 health measures. CDC's methods page (checked 2026-10-20, https://www.cdc.gov/places/methodology/index.html) says every measure comes from a multilevel logistic model using, "based on model performance": individual-level age, sex, race/ethnicity and education (from BRFSS); county-level percentage of adults below 150% of the federal poverty level (5-year ACS); and state- and county-level random effects. Predictions are poststratified to county population estimates.

Kong & Zhang (2020, AJPH, doi 10.2105/AJPH.2020.305611) warn that associations between such estimates, or between an estimate and the variables used to build it, partly reflect the shared model inputs.

**Question:** across US counties, how much of the variation in each PLACES measure, and of the correlations between PLACES measures, is reproduced by county-level versions of those model inputs (plus state)? And how does a directly measured rate behave under the same procedure?

## Data available

- `data/raw/places_county_2025.csv`: PLACES 2025 county release (data.cdc.gov dataset `i46a-9kgh`), wide format. Columns `<measure>_crudeprev` and `<measure>_adjprev` (age-adjusted), `countyfips` (pad to 5 characters), `stateabbr`. 3,143 counties; some measures are missing for some states.
- `data/raw/acs_sf/acsdt5y2023-*.dat`: ACS 2019-2023 5-year table-based summary files (pipe-delimited, all geographies; county rows have `GEO_ID` starting `0500000US`, FIPS = last 5 characters; column `B01001_E003` = estimate for variable `B01001_003`). Tables: B01001 (sex by age), B03002 (Hispanic origin by race), B15003 (education 25+), B17024 (age by ratio of income to poverty), B27010 (health insurance by age).
- Variable labels: `https://api.census.gov/data/2023/acs/acs5/groups/<TABLE>.json` (no key needed).
- The Census data API also works with the key in `.env` (`CENSUS_API_KEY`). Never print, log or copy the key.
- Python: use the project venv `.venv/bin/python` (pandas, numpy, matplotlib). Install anything else into `.venv` with `uv pip install --python .venv/bin/python <pkg>`.

## Rules

- Write ONLY inside your own review folder (given in your task). Do not modify anything else in the project.
- Do not open `scripts/covariate_test.py`, `scripts/covariate_charts.py`, `scripts/fetch_acs_county.py`, `data/raw/acs_county_2023.csv` or `outputs/` until your own numbers exist (your task says when).
- Report what you actually ran. Say what you skipped, assumed or could not verify.
