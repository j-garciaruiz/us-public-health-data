# US Public Health Data: exploration lab

Sandbox for getting fluent with US public health data: pulling it, understanding its quirks, and turning it into charts, explainers and small tools. Long-term goal: a portfolio that shows US data fluency alongside the LAC work.

Started 2026-10-20. Access status below was checked live on that date.

## Layout

```
data/raw/     downloaded files (git-ignored; re-fetch with the scripts)
scripts/      fetchers and cleaning
notebooks/    exploration
figures/      chart output
```

`scripts/fetch_socrata.py <dataset_id> <out.csv>` downloads any full dataset from data.cdc.gov (standard library only, pages through large tables).

## Source catalog

"Script" = reachable from code. "Browser" = the site blocks scripted requests (403 to curl) but works in a normal browser; download manually or use the documented API.

### Tier 1: start here (clean, small, map-ready)

| Source | What it gives you | Geography | Access (2026-10-20) |
|---|---|---|---|
| **CDC PLACES** (2025 release) | Model-based estimates of 40 measures: chronic disease, risk behaviors, prevention, disability, and social needs (food insecurity, loneliness, transport) | County, city, census tract, ZCTA | Script. `i46a-9kgh` = county, wide format. **Already pulled: 3,143 counties.** |
| **NCHS VSRR provisional overdose deaths** | Monthly 12-month rolling overdose deaths by drug class | National, state | Script. `xkb8-kh2a`. **Already pulled; data through May 2026.** |
| **County Health Rankings** | ~90 measures per county, one CSV per year, with documented sources | County | Script/download |
| **Census ACS API** | Uninsurance, income, poverty, language, Hispanic origin, disability: the denominators and social determinants for everything else | Down to tract | Script (free API key raises limits) |
| **Census SAHIE** | Model-based uninsured rates by age, sex, income, race/ethnicity | County, state | Script |

### Tier 2: the core federal systems (what US employers expect you to know)

| Source | What it gives you | Access |
|---|---|---|
| **CDC WONDER** (mortality, natality) | Deaths by ICD-10 cause, age, sex, race, Hispanic origin, county; final data 2018–2024 plus provisional to last week | Browser for sub-national queries. The API only returns national-level data. Small counts (<10) suppressed |
| **BRFSS** | The state behavioral risk survey (~400k adults a year); the input behind PLACES | Browser (annual SAS XPT files; pandas reads them). Needs survey weights |
| **NHANES** | Exam + lab + interview survey: measured BP, A1c, cholesterol, BMI, not self-report | Script. XPT files; complex survey design |
| **NHIS** | National household health interview: insurance, access, chronic conditions | Browser |
| **YRBSS** | Youth risk behaviors | Browser |
| **CDC/ATSDR Social Vulnerability Index** | 16 census variables into one vulnerability rank | Browser |
| **CDC Environmental Public Health Tracking** | Heat, air quality, and linked health outcomes | Script/browser |

### Tier 3: financing, coverage, pharma (closest to Decilion's lines of work)

| Source | What it gives you | Access |
|---|---|---|
| **CMS National Health Expenditure Accounts** | US health spending by source and service since 1960; the US counterpart of WHO GHED | Script (downloads) |
| **data.cms.gov** | Medicare Part D prescribers and drugs, geographic variation, hospital quality, provider data | Script (catalog `data.json`) |
| **data.medicaid.gov** | State Drug Utilization Data: Medicaid prescriptions and spending by drug and state | Script |
| **openFDA** | Adverse events, drug labels, NDC directory, recalls | Script (JSON API) |
| **AHRQ MEPS** | Household medical spending and out-of-pocket costs | Browser |
| **HRSA Data Warehouse** | Health professional shortage areas, health centers | Script |
| **KFF State Health Facts** | Curated state tables on Medicaid, coverage, spending | Browser |
| **IHME GHDx** | US county life expectancy and burden estimates | Browser |

## Things that trip people up

- **Crude vs age-adjusted.** PLACES and WONDER give both. Compare places with age-adjusted rates; use crude for burden counts.
- **Suppression.** WONDER hides counts under 10 and flags rates under 20 as unreliable; small counties go blank.
- **Survey weights.** BRFSS, NHANES, NHIS, MEPS are complex samples; unweighted means are wrong.
- **Model-based estimates.** PLACES and SAHIE are small-area models, not direct measurements. Fine for mapping, not for causal claims.
- **FIPS codes** are the join key across everything. Keep them as 5-character strings (leading zeros).
- **Race/ethnicity coding changed**: WONDER moved from bridged race (1999–2020) to single race (2018+).

## Starter projects

1. **County chronic disease atlas** (PLACES + ACS). Choropleths of diabetes, obesity, depression; the diabetes range is already striking (age-adjusted 6.0% in Douglas County, CO vs 23.8% in Oglala Lakota County, SD).
2. **The overdose turn.** 12-month overdose deaths peaked at 111,466 (12 months ending June 2023) and fell to 65,351 (ending May 2026). Which states and drug classes drove the decline?
3. **Latino health in the US** (WONDER + ACS + SAHIE + PLACES). The Hispanic mortality advantage, uninsurance gaps, Puerto Rico. A natural bridge between LAC expertise and US data.
4. **US vs LAC health financing** (CMS NHE + WHO GHED, which you already have an MCP for). Out-of-pocket shares, public vs private spending.
5. **Medicaid drug spending explorer** (State Drug Utilization Data). Builds on the pharma/market-access side of Decilion.
6. **Explainer: why county rankings mislead** (crude vs adjusted, suppression, model uncertainty). An interactive piece using PLACES confidence intervals.
