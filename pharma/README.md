# US pharmaceutical data: pricing, utilization, spending, access

Map of public US drug data, checked live on **2026-10-20** (each source opened or queried that day; status, latest period and row counts are what the source returned then). Starter pull: NADAC weekly pharmacy acquisition prices, see [Starter dataset](#starter-dataset-nadac).

Access legend. **API**: JSON/CSV endpoint that works from a script. **Bulk**: downloadable file (CSV, XLSX, ZIP) at a stable URL. **Browser**: the site blocks scripted requests (403 to curl) or needs clicking; it works in a normal browser. None of the sources below needs an account or a terms-of-use acceptance to read, except where noted.

```
pharma/
  README.md                 this catalog
  scripts/fetch_nadac.py    downloads NADAC yearly files from data.medicaid.gov (standard library)
  scripts/summarize_nadac.py  structure checks + tracer drugs -> pharma/outputs/
  outputs/                  small derived files (sanity summary, tracer series)
data/raw/pharma/            raw downloads (git-ignored; re-fetch with the scripts)
```

## Catalog

### Medicare (CMS, data.cms.gov)

All data.cms.gov datasets share one API: `https://data.cms.gov/data-api/v1/dataset/<uuid>/data?size=5000&offset=N` (JSON, max 5,000 rows per call; `/data/stats` gives the row count). The full catalog is `https://data.cms.gov/data.json`; each year is a separate dataset version with its own uuid.

| Source | What it gives | Geography | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|---|
| **Part D Spending by Drug** | Gross spending, claims, beneficiaries, dosage units, avg spend per unit, by brand and generic name and manufacturer; 5 years side by side | National | 2020–2024 in the current file | API + Bulk CSV | OK. 14,536 rows (`7e0b4365-fd63-4a29-8f5e-e0ac9f66a81b`) |
| **Quarterly Part D Spending by Drug** | Same measures, year to date | National | 2025 Q1–Q4 and 2026 Q1 | API + Bulk CSV | OK. 27,748 rows (`4ff7c618-…`) |
| **Part B Spending by Drug** | Physician-administered drugs by HCPCS code (oncology, biologics, injectables) | National | 2020–2024 | API + Bulk CSV | OK. 799 rows (`76a714ad-…`) |
| **Quarterly Part B Spending by Drug** | Year-to-date Part B | National | 2025, 2026 Q1 | API + Bulk | OK. 1,742 rows |
| **Part B Discarded Drug Units** | Wasted units from single-dose vials (refund program) | National | 2023 | API | OK |
| **Part D Prescribers by Provider and Drug** | Claims, 30-day fills, days supply, drug cost per prescriber NPI and drug | Prescriber (NPI, with city/state) | 2013–2024 | API (paged) + Bulk CSV (large) | OK. 28,023,892 rows for 2024 |
| **Part D Prescribers by Geography and Drug** | Same by state and national; flags for opioids, antibiotics, antipsychotics; LIS vs non-LIS cost share | State, national (no county) | 2013–2024 | API + Bulk | OK. 117,661 rows for 2024 |
| **Part D Prescribers by Provider** | One row per prescriber: totals, opioid and antibiotic shares, beneficiary demographics | Prescriber | 2013–2024 | API + Bulk | OK |
| **Part D Opioid Prescribing Rates by Geography** | Opioid and long-acting opioid prescribing rates, 1- and 5-year change | National, state, county, ZIP; urban/rural (RUCA) breakouts | 2024 file (with trends) | API + Bulk | OK. 359,139 rows |
| **Prescription Drug Plan Formulary, Pharmacy Network and Pricing files (SPUF)** | Every Part D plan's formulary (tiers, prior auth, step therapy, quantity limits), pharmacy networks, plan drug prices, beneficiary cost sharing | Plan, county service areas, pharmacy | Quarterly 2019–2026 Q3; monthly versions too | Bulk ZIP (large) | OK. Latest `SPUF_2026_20261007.zip` |
| **Medicare Drug Price Negotiation (IRA)**: selected drugs and Maximum Fair Prices | NDC-level list of negotiated drugs, MFP per 30-day supply and per unit, effective dates, inflation adjustments | National | IPAY 2026 (10 drugs, in effect since 2026-01-01), IPAY 2027 (15 drugs, prices published), IPAY 2028 (15 drugs selected, prices not yet in file) | Bulk ZIP (CSV + XLSX), cms.gov page | OK. File dated 2026-09-21 |
| **ASP pricing files (Part B payment limits)** | Quarterly Average Sales Price payment limits by HCPCS (ASP + 6%), NDC-HCPCS crosswalk | National | Quarterly; October 2026 is latest | Bulk ZIP | OK |
| **CMS Program Statistics: Part D** | Enrollment and aggregate Part D program tables | National, state | 2013–2024 | API | OK |
| **Medicaid Spending by Drug** (on data.cms.gov) | Same layout as the Part D file, for Medicaid (before rebates) | National | 2020–2024 | API + Bulk | OK. 18,511 rows |
| **Open Payments** (Sunshine Act) | Every payment from drug and device makers to physicians and teaching hospitals: food, speaking, consulting, research, ownership | Recipient (NPI, address) | 2019–2025 general payments (older years archived) | API (`openpaymentsdata.cms.gov/api/1/...`) + Bulk | OK with a plain script; returns 403 to some browser user agents |

### Medicaid (data.medicaid.gov)

All datasets share one API: `https://data.medicaid.gov/api/1/datastore/query/<dataset-id>/0?limit=N&offset=N&count=true` (filters with `conditions[0][property]=...&conditions[0][value]=...`, sorting with `sorts[0][property]=...&sorts[0][order]=desc`; use `curl -g` because of the brackets). Catalog: `https://data.medicaid.gov/api/1/metastore/schemas/dataset/items`.

| Source | What it gives | Geography | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|---|
| **NADAC** (National Average Drug Acquisition Cost) | Average invoice price retail community pharmacies pay, per unit, by 11-digit NDC; brand/generic class, OTC flag | National | One file per year, 2013–2026; weekly snapshots | API + Bulk CSV | OK. 2026 file: 1,268,309 rows, latest snapshot 2026-10-21. **Pulled** |
| **NADAC Comparison** | Week-over-week old vs new NADAC per NDC with % change and reason | National | Rolling, back to 2021 | API + Bulk | OK. 3,492,310 rows |
| **First Time NADAC Rates** | NDCs getting their first NADAC | National | Rolling | API | OK |
| **State Drug Utilization Data (SDUD)** | Prescriptions, units and amount reimbursed (Medicaid + non-Medicaid share) by state, NDC, quarter, fee-for-service vs managed care | State | 1991–2026 (2026 has Q1 only) | API + Bulk | OK. 2025: 5,308,547 rows. 652,561 of 1,287,884 rows in 2026 Q1 are suppressed (see pitfalls) |
| **ACA Federal Upper Limits (FUL)** | Cap on Medicaid reimbursement for multiple-source generics (175% of weighted average AMP) | National | Monthly, 2016–2026-09 | API + Bulk | OK. 2,280,950 rows |
| **Drug Products in the Medicaid Drug Rebate Program** | Every covered outpatient drug by NDC: labeler, FDA application, approval and market dates, drug category (S/I/N), line-extension flag | National | Quarterly, through 2026 Q2 | API + Bulk | OK. 2,002,508 rows |
| **Product Data for Newly Reported Drugs** | Weekly additions to the rebate program | National | Weekly files | API | OK |
| **Drug AMP Reporting (monthly, quarterly)** | Whether each NDC's Average Manufacturer Price was reported (status only, not the AMP value) | National | 2017–2026 | API | OK |
| **Medicaid Opioid Prescribing Rates by Geography** (data.cms.gov) | Opioid prescribing rates in Medicaid | State, county | 2024 file | API | OK |

### FDA and NLM (product identity, approvals, safety, shortages)

| Source | What it gives | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|
| **openFDA drug/ndc** | NDC directory: product and package NDCs, labeler, active ingredients, dosage form, marketing category, application number | Current listings | API (`api.fda.gov/drug/ndc.json`) + Bulk | OK. 138,319 products, updated 2026-10-16 |
| **openFDA drug/label** | Structured product labels (indications, warnings, dosing) | Current | API + Bulk (14 parts) | OK. 262,897 labels |
| **openFDA drug/event (FAERS)** | Adverse event reports | 2004 onward | API + Bulk (1,767 parts) | OK. 20,692,690 reports, API data through 2026-07-30 |
| **openFDA drug/enforcement** | Drug recalls with class and reason | 2004 onward | API | OK. 18,010 recalls |
| **openFDA drug/drugsfda** | Drugs@FDA: applications, sponsors, products, submission history | 1939 onward | API | OK. 29,390 applications |
| **openFDA drug/shortages** | FDA drug shortage list by package NDC: status, therapeutic category, company | Current | API | OK. 1,581 records (1,141 current, 421 to be discontinued, 19 resolved) |
| **Orange Book** | Small-molecule approvals with therapeutic equivalence codes, patents, exclusivities | Monthly | Bulk ZIP (fda.gov) + openFDA bulk | OK |
| **Purple Book** | Licensed biologics, biosimilars, interchangeability, exclusivity | Monthly | Bulk CSV/XLSX per month | OK. Latest file September 2026 |
| **Drugs@FDA data files** | Same as openFDA drugsfda, as flat files | Weekly | Bulk ZIP | OK |
| **NDC Directory text files** | Product and package tables, plus unfinished and excluded products | Daily | Bulk ZIP (`accessdata.fda.gov/cder/ndctext.zip`) | OK |
| **FDA Drug Shortages Database** | Narrative shortage entries, reasons, estimated resolution | Current | Browser (`accessdata.fda.gov/scripts/drugshortages/`) | OK |
| **ASHP / University of Utah drug shortages** | Independent shortage list (broader definition than FDA) and quarterly counts since 2001 | Through 2026 Q2 (227 active shortages) | Browser (403 to scripts); reprint needs permission from Utah DIS | OK in browser |
| **RxNorm / RxNav API** (NLM) | Maps NDCs to ingredients, strengths and clinical drugs (RxCUI); NDC status and history | Monthly | API (`rxnav.nlm.nih.gov/REST`) | OK. Example: NDC 00071015523 resolves to atorvastatin 10 mg [Lipitor] |
| **DailyMed** (NLM) | Current labels, SPL documents, NDC-to-label links | Current | API | OK |

### Other federal: access, out-of-pocket, controlled substances, government prices

| Source | What it gives | Geography | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|---|
| **HRSA 340B OPAIS** | Covered entities (hospitals, health centers, clinics), their contract pharmacies, participating manufacturers, Medicaid exclusion file | Entity address | Daily exports | Browser (Reports page; daily Excel and JSON exports, no login for the public reports) | OK. 340B ceiling prices are **not** public |
| **AHRQ MEPS Prescribed Medicines files** | Every household-reported fill with payment by source (out of pocket, private, Medicare, Medicaid), linked to person-level demographics and insurance | National (survey) | Annual; 2024 file is HC-254A, 2023 is HC-248A | Bulk (SAS, Stata, ASCII, XLSX) | OK |
| **NHANES Prescription Medications (RXQ_RX)** | Self-reported prescription use in the past 30 days with drug codes, linked to exam and lab data | National (survey) | 2021–2023 cycle is `RXQ_RX_L` | Bulk XPT | OK. Used for the NCHS prescription drug use data briefs (cdc.gov pages: Browser) |
| **CDC opioid dispensing rate maps** | Retail opioid prescriptions per 100 persons (from IQVIA) | State, county (about 98% of counties) | 2019–2024 | Browser (CSV download on page) | OK in browser. National rate 46.8 (2019) to 35.4 (2024) per 100 persons, per the page |
| **DEA ARCOS Retail Drug Summary** | Grams of controlled substances distributed, by state and 3-digit ZIP, per 100K population | State, 3-digit ZIP | Annual PDFs; 2025 is latest | Bulk PDF (tables need extraction) | OK |
| **VA Federal Supply Schedule pharmaceutical prices** | FSS, Big Four (statutory, at least 24% below non-federal average manufacturer price) and national contract prices by NDC | National | Monthly; `TPharmPrices2026-10-01.xlsx` | Bulk XLSX (department.va.gov) | OK. 43,225 price rows, 16,277 NDCs (30,447 FSS, 10,862 Big4, 1,916 NC) |
| **NPPES NPI Registry** | Every pharmacy with an NPI, address and taxonomy (e.g. Community/Retail Pharmacy 3336C0003X) | Address (geocodable) | Weekly full file, live API | API (200 rows per call) + Bulk ZIP | OK. API returned 186 community/retail pharmacies for Vermont |
| **Census County Business Patterns** | Pharmacy establishments and employment (NAICS 446110 in the 2017 coding) | County, ZIP | 2023 latest (41,792 establishments nationally) | API (key in main `.env`) | OK |

### State drug price transparency

| Source | What it gives | Access | Status 2026-10-20 |
|---|---|---|---|
| **California HCAI CTRx** | Manufacturer reports of WAC increases (over 16% cumulative in 3 years on drugs above $40 per course) and new drugs launched above the Part D specialty threshold; monthly updates | Bulk CSV/XLSX on the CHHS open data portal (`data.chhs.ca.gov`, dataset "prescription-drug-wholesale-acquisition-cost-wac-increases"); latest file covers Jan–Sep 2026 | OK. The old `hcai.ca.gov/data/cost-transparency/prescription-drug-costs/` URL is 404; use `/data/cost-transparency/rx/` |
| **Oregon Drug Price Transparency (DFR)** | Manufacturer price-increase and new-drug reports, insurer and PBM reports, annual legislative report (2025 report published 2025-12) | Browser (data pages and PDFs) | OK |
| **Vermont Attorney General** | Annual report to the Legislature on the 15 drugs with the highest spending and price increases; insurer data stays confidential | Browser (PDF reports) | OK |

### Not public or not usable for research

- **GoodRx** retail cash prices: no public dataset or open API found; goodrx.com returns 403 to scripts. Treat as unavailable unless a licensed feed is arranged.
- **Mark Cuban Cost Plus Drugs**: posts prices on its site but returns 403 to scripts; no documented public API found. Browser only, manual spot checks.
- **IQVIA, Symphony, SSR Health** (net prices): commercial licenses. CDC's opioid maps are the only free IQVIA-derived series found.
- **340B ceiling prices, Medicaid AMP and Best Price values, Part D rebates by drug**: confidential by statute.

### LAC comparison side (for cross-country projects)

- **Colombia SISMED** (prices and sales, 2010 onward): available through the Aphorics MCP already connected to this machine.
- **Brazil CMED price lists** (ANVISA): monthly XLSX of factory (PF) and maximum consumer (PMC) prices, plus government purchase ceiling (PMVG). Checked 2026-10-20: latest list dated 2026-10-09.

## Things that trip people up

**NDC formats.** The FDA prints NDCs in three 10-digit layouts (4-4-2, 5-3-2, 5-4-1). CMS and most claims data use an 11-digit 5-4-2 form with no dashes, made by padding the short segment with a leading zero: `0071-0155-23` (4-4-2) becomes `00071015523`, `12345-678-90` (5-3-2) becomes `12345067890`, `12345-6789-0` (5-4-1) becomes `12345678900`. You cannot pad a dashless 10-digit NDC correctly without knowing its layout, so always normalize from the dashed form (openFDA and the NDC directory give it). Keep NDCs as strings; Excel and pandas drop leading zeros. NADAC and SDUD use 11 digits; the VA price file and the IRA file use dashed 11 digits; Part D spending files have no NDC at all (brand and generic names), so joins to NDC-level data go through RxNorm or name matching.

**Product NDC vs package NDC.** The first 9 digits (labeler + product) identify the product; the last 2 the package. Prices are per package NDC; NADAC and FUL are per unit. The IRA file gives both an NDC-9 price per unit and an MFP per 30-day equivalent supply.

**List vs net price.** WAC (wholesale acquisition cost) is the manufacturer's list price to wholesalers. AWP (average wholesale price) is a published benchmark, typically about 20% above WAC, used in old contracts; nobody pays it. NADAC is what pharmacies actually pay on invoice, survey-based. ASP (Part B) is the manufacturer's average sales price net of most discounts, reported to CMS. AMP drives Medicaid rebates and is confidential. None of these subtracts the rebates manufacturers pay to PBMs, insurers and Medicaid, so "spending" in Part D and Medicaid files is gross: Medicare Part D spending excludes rebates by design, and Medicaid's State Drug Utilization Data is pre-rebate. For brands, net can be less than half of list. A pharmacy can also keep paying close to list for a negotiated (IRA) drug: the Maximum Fair Price reaches the pharmacy as a refund through the Medicare Transaction Facilitator, not as a lower invoice price.

**NADAC specifics.** One row per NDC per weekly snapshot (`As of Date`). The monthly survey refresh moves most rates at once (in 2026: 01-21, 02-18, 03-18, 04-22, 05-20, 06-17, 07-22, 08-19, 09-23, 10-21); other weeks change few rates. Covers retail community pharmacies only (`Pharmacy Type Indicator` = C/I), not mail order or specialty, so many specialty drugs are missing. `Pricing Unit` is EA, ML or GM: an Ozempic pen is priced per mL, so multiply by package volume.

**Suppression of small counts.** CMS suppresses cells under 11 claims or beneficiaries. In SDUD, rows under 11 prescriptions keep the row but blank the numbers (`suppression_used = true`): 652,561 of the 1,287,884 rows in 2026 Q1 are suppressed, so summing SDUD understates totals, more in small states. Part D prescriber files drop prescribers with fewer than 11 claims for a drug and blank age-65+ breakouts under 11 (`GE65_Sprsn_Flag`).

**Part D vs Part B.** Part D covers drugs dispensed by pharmacies (pills, pens, inhalers). Part B covers drugs administered in a clinic or hospital outpatient department (infusions, many cancer drugs, biologics), billed by HCPCS J-codes, not NDCs. The same molecule can sit in both. Use the ASP NDC-HCPCS crosswalk to connect them. Medicare drug spending = Part D + Part B; either alone is a partial picture.

**Medicaid fee-for-service vs managed care.** SDUD splits `FFSU` and `MCOU`. States moved most enrollees into managed care over the 2010s, so trends in FFS alone are mostly program design, not prescribing.

**Spending files are drug-level, not person-level.** Part D Spending by Drug cannot tell you who uses a drug; MEPS can (with survey weights and a small sample).

**Brand classification.** NADAC's `B-ANDA` (brand name on a generic approval) and `B-BIO` (biosimilars), Medicaid's drug category S (single source), I (innovator multiple source), N (non-innovator) and FDA's therapeutic equivalence codes do not line up one to one. Pick one definition and state it.

## Starter project ideas

1. **US vs Colombia vs Brazil: what the same molecule costs.** NADAC (US pharmacy acquisition), VA Big Four (US government price), Medicare MFP (negotiated), SISMED (Colombia) and CMED PF (Brazil) for a basket of 30 WHO essential medicines and 10 high-spend brands, matched through ATC/RxNorm and normalized per defined daily dose. Shows US data fluency and Decilion's market access lens; the headline is that US generics are often cheaper than in LAC while brands are many times more expensive.
2. **What did IRA negotiation change at the pharmacy counter?** Track NADAC and Part D quarterly spending for the 10 IPAY 2026 drugs before and after 2026-01-01, against similar non-selected brands. Early hint from the starter pull: median NADAC for Eliquis 5 mg fell 43% (snapshot of 2026-01-14) and Jardiance 10 mg 44% (2026-01-07), while Januvia 100 mg and Xarelto 20 mg, also negotiated for 2026, did not fall. The cause is not established here (manufacturer list-price cuts are the obvious candidate to check against WAC data).
3. **Generic price shocks and shortages.** Link NADAC Comparison (weekly jumps over 100%) with openFDA shortages and ASHP counts: do price spikes precede or follow shortages, and are sole-source generics the ones that spike? A health economics question with policy relevance.
4. **Pharmacy deserts and Medicaid access.** Geocode NPPES community pharmacies (or use County Business Patterns), overlay county Medicaid enrollment and the Part D opioid prescribing map, and find counties with high need and few pharmacies. Connects to the expected-vs-observed county atlas in this repository.
5. **Who pays for insulin and GLP-1s?** MEPS prescribed-medicines files (out-of-pocket share by insurance, income, Hispanic origin) plus Part D and Medicaid spending trends, before and after the 2023 $35 insulin cap and the GLP-1 obesity boom.
6. **Open Payments and prescribing.** Join Open Payments to Part D Prescribers by NPI for one class (e.g. GLP-1s or anticoagulants) and describe how payment receipt relates to brand share. Descriptive only, with the well-known selection caveats.

## Starter dataset: NADAC

```
.venv/bin/python pharma/scripts/fetch_nadac.py 2025 2026     # ~250 MB, under a minute
.venv/bin/python pharma/scripts/summarize_nadac.py 2026
```

Pulled 2026-10-20: `nadac_2025.csv` (1,608,415 rows, snapshots to 2025-12-31) and `nadac_2026.csv` (1,268,309 rows, 42 weekly snapshots 2026-01-07 to 2026-10-21). Each file has a `.meta.json` with source URL, catalog date and SHA-256. Summary in [outputs/nadac_sanity.md](outputs/nadac_sanity.md); weekly tracer series in [outputs/nadac_tracers.csv](outputs/nadac_tracers.csv).

Highlights from the latest snapshot (2026-10-21): about 30,100 NDCs priced; all NDCs 11 digits, no duplicates within a snapshot. Median NADAC per tablet or capsule is $0.14 for generics and $12.67 for brands. Atorvastatin 20 mg costs a pharmacy about 3 cents a tablet, metformin 500 mg about 1.5 cents.

Review status: Codex (GPT-6 Astra, high) verification of the catalog's live-status claims and the sanity numbers, see `reviews/pharma_codex_astra/`. Agy method review not yet run.
