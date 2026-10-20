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
| **Quarterly Part D Spending by Drug** | Year-to-date spending, claims, beneficiaries, average spending per claim and per beneficiary (no dosage units, so no unit prices) | National | 2025 Q1–Q4 and 2026 Q1 | API + Bulk CSV | OK. 27,748 rows (`4ff7c618-…`) |
| **Part B Spending by Drug** | Physician-administered drugs by HCPCS code (oncology, biologics, injectables) | National | 2020–2024 | API + Bulk CSV | OK. 799 rows (`76a714ad-…`) |
| **Quarterly Part B Spending by Drug** | Year-to-date Part B | National | 2025, 2026 Q1 | API + Bulk | OK. 1,742 rows |
| **Part B Discarded Drug Units** | Wasted units from single-dose vials (refund program) | National | 2023 | API | OK. 824 rows |
| **Part D Prescribers by Provider and Drug** | Claims, 30-day fills, days supply, drug cost per prescriber NPI and drug | Prescriber (NPI, with city/state) | 2013–2024 | API (paged) + Bulk CSV (large) | OK. 28,023,892 rows for 2024 |
| **Part D Prescribers by Geography and Drug** | Same by state and national; flags for opioids, antibiotics, antipsychotics; LIS vs non-LIS cost share | State, national (no county) | 2013–2024 | API + Bulk | OK. 117,661 rows for 2024 |
| **Part D Prescribers by Provider** | One row per prescriber: totals, opioid and antibiotic shares, beneficiary demographics | Prescriber | 2013–2024 | API + Bulk | OK. 1,416,883 rows for 2024 |
| **Part D Opioid Prescribing Rates by Geography** | Opioid and long-acting opioid prescribing rates, 1- and 5-year change | National, state, county, ZIP; urban/rural (RUCA) breakouts | 2024 file (with trends) | API + Bulk | OK. 359,139 rows |
| **Prescription Drug Plan Formulary, Pharmacy Network and Pricing files (SPUF)** | Every Part D plan's formulary (tiers, prior auth, step therapy, quantity limits), pharmacy networks, plan drug prices, beneficiary cost sharing | Plan, county service areas, pharmacy | Quarterly 2019–2026 Q3; a separate monthly series already has contract year 2027 (release 2026-10-08) | Bulk ZIP (large) | OK. Latest quarterly `SPUF_2026_20261007.zip`; release date and contract year differ |
| **Medicare Drug Price Negotiation (IRA)**: selected drugs and Maximum Fair Prices | NDC-level list of negotiated drugs, MFP per 30-day supply and per unit, effective dates, inflation adjustments | National | IPAY 2026 (10 drugs, in effect since 2026-01-01), IPAY 2027 (15 drugs, prices published), IPAY 2028 (15 drugs selected, prices not yet in file) | Bulk ZIP (CSV + XLSX), cms.gov page | OK. File dated 2026-09-21 |
| **ASP pricing files (Part B payment limits)** | Quarterly Average Sales Price payment limits by HCPCS (generally ASP + 6%; qualifying biosimilars get their ASP plus 8% of the reference product's ASP), NDC-HCPCS crosswalk | National | Quarterly; October 2026 is latest | Bulk ZIP | OK |
| **CMS Program Statistics: Part D** | Enrollment and aggregate Part D program tables | National, state | 2013–2024 | Bulk ZIP tables (no row API) | OK |
| **Medicaid Spending by Drug** (on data.cms.gov) | Same layout as the Part D file, for Medicaid (before rebates) | National | 2020–2024 | API + Bulk | OK. 18,511 rows |
| **Open Payments** (Sunshine Act) | Every payment from drug and device makers to physicians and teaching hospitals: food, speaking, consulting, research, ownership | Recipient (NPI, address) | 2019–2025 general payments (older years archived) | API (`openpaymentsdata.cms.gov/api/1/...`) + Bulk | Mixed. Answered curl and Python requests (HTTP 200) but returned 403 to requests with no or Safari user agent; Codex's independent requests got 403. Set an explicit User-Agent and retry |

### Medicaid (data.medicaid.gov)

All datasets share one API: `https://data.medicaid.gov/api/1/datastore/query/<dataset-id>/0?limit=N&offset=N&count=true` (filters with `conditions[0][property]=...&conditions[0][value]=...`, sorting with `sorts[0][property]=...&sorts[0][order]=desc`; use `curl -g` because of the brackets). Catalog: `https://data.medicaid.gov/api/1/metastore/schemas/dataset/items`.

| Source | What it gives | Geography | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|---|
| **NADAC** (National Average Drug Acquisition Cost) | Average invoice price retail community pharmacies pay, per unit, by 11-digit NDC; brand/generic class, OTC flag | National | One file per year, 2013–2026; weekly snapshots | API + Bulk CSV | OK. 2026 file: 1,268,309 rows, latest snapshot 2026-10-21. **Pulled** |
| **NADAC Comparison** | Week-over-week old vs new NADAC per NDC with % change and reason | National | Cumulative weekly changes, 2013-12-05 to 2026-10-21 (Effective Date filled from 2017-06-07; filter on End Date) | API + Bulk | OK. 3,492,310 rows |
| **First Time NADAC Rates** | New rate groups getting a first NADAC (description, rate, class, unit, effective date; no NDC column) | National | Rolling | API | OK. 1,390 rows |
| **State Drug Utilization Data (SDUD)** | Prescriptions, units and amount reimbursed (Medicaid + non-Medicaid share) by state, NDC, quarter, fee-for-service vs managed care | State, plus national total rows (`state = XX`) | 1991–2026 (2026 has Q1 only) | API + Bulk | OK. 2025: 5,308,547 rows. 652,561 of 1,287,884 rows in 2026 Q1 are suppressed; the 78,939 national `XX` rows have 20,467 suppressed (see pitfalls) |
| **ACA Federal Upper Limits (FUL)** | Aggregate cap on Medicaid reimbursement for multiple-source drugs: 175% of weighted average AMP, raised to the NADAC-based acquisition-cost floor where that is higher; publishes the weighted AMP | National | Monthly, 2016–2026-09 | API + Bulk | OK. 2,280,950 rows |
| **Drug Products in the Medicaid Drug Rebate Program** | Every covered outpatient drug by NDC: labeler, FDA application, approval and market dates, drug category (S/I/N), line-extension flag | National | Quarterly, through 2026 Q2 | API + Bulk | OK. 2,002,508 rows |
| **Product Data for Newly Reported Drugs** | Weekly additions to the rebate program | National | Weekly files | API | OK |
| **Drug AMP Reporting (monthly, quarterly)** | Whether each NDC's Average Manufacturer Price was reported (status only, not the AMP value) | National | Monthly 2017 to 2026-06; quarterly 2013 to 2026 Q2 | API | OK |
| **Medicaid Opioid Prescribing Rates by Geography** (data.cms.gov) | Opioid prescribing rates in Medicaid | State, county | 2024 file | API | OK. 597,297 rows |

### FDA and NLM (product identity, approvals, safety, shortages)

| Source | What it gives | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|
| **openFDA drug/ndc** | NDC directory: product and package NDCs, labeler, active ingredients, dosage form, marketing category, application number | Current listings | API (`api.fda.gov/drug/ndc.json`) + Bulk | OK. 138,319 products, updated 2026-10-16 |
| **openFDA drug/label** | Structured product labels (indications, warnings, dosing) | Current | API + Bulk (14 parts) | OK. 262,897 labels |
| **openFDA drug/event (FAERS)** | Adverse event reports (voluntary, duplicated, not evidence of causation; no denominator) | 2004 onward | API + Bulk (1,767 parts) | OK. 20,692,690 reports; API updated 2026-07-30, newest receive date 2026-06-30 |
| **openFDA drug/enforcement** | Drug recalls with class and reason | Documented as 2004 onward; earliest report date returned is 2012-06-20, so treat early years as incomplete | API | OK. 18,010 recalls |
| **openFDA drug/drugsfda** | Drugs@FDA: applications, sponsors, products, submission history | 1939 onward | API | OK. 29,390 applications |
| **openFDA drug/shortages** | FDA drug shortage list by package NDC: status, therapeutic category, company | Current | API | OK. 1,581 records (1,141 current, 421 to be discontinued, 19 resolved) |
| **Orange Book** | Small-molecule approvals with therapeutic equivalence codes, patents, exclusivities | Monthly | Bulk ZIP (fda.gov), openFDA API (`/drug/orangebook.json`) and bulk | OK. 48,865 records in openFDA |
| **Purple Book** | Licensed biologics, biosimilars, interchangeability, exclusivity | Monthly | Bulk CSV/XLSX per month | OK. Latest file September 2026 |
| **Drugs@FDA data files** | Same as openFDA drugsfda, as flat files | Updated weekday mornings (page dated 2026-10-19) | Bulk ZIP | OK |
| **NDC Directory text files** | Product and package tables, plus unfinished and excluded products (an NDC listing is not an FDA approval) | Daily | Bulk ZIP (`accessdata.fda.gov/cder/ndctext.zip`) | OK |
| **FDA Drug Shortages Database** | Narrative shortage entries, reasons, estimated resolution | Current | Browser (`accessdata.fda.gov/scripts/drugshortages/`) | OK |
| **ASHP / University of Utah drug shortages** | Independent shortage list (broader definition than FDA) and quarterly counts since 2001 | Through 2026 Q2 (227 active shortages) | Browser (403 to scripts); reprint needs permission from Utah DIS | OK in browser (Claude); Codex's scripted check got 403 |
| **RxNorm / RxNav API** (NLM) | Maps NDCs to ingredients, strengths and clinical drugs (RxCUI); NDC status and history | Monthly | API (`rxnav.nlm.nih.gov/REST`) | OK. Example: NDC 00071015523 resolves to atorvastatin 10 mg [Lipitor] |
| **DailyMed** (NLM) | Current labels, SPL documents, NDC-to-label links | Current | API | OK |

### Other federal: access, out-of-pocket, controlled substances, government prices

| Source | What it gives | Geography | Years / latest | Access | Status 2026-10-20 |
|---|---|---|---|---|---|
| **HRSA 340B OPAIS** | Covered entities (hospitals, health centers, clinics), their contract pharmacies, participating manufacturers, Medicaid exclusion file | Entity address | Daily exports | Browser (Reports page; daily Excel and JSON exports, no login for the public reports) | OK. 340B ceiling prices are **not** public |
| **AHRQ MEPS Prescribed Medicines files** | Every household-reported fill with payment by source (out of pocket, private, Medicare, Medicaid), linked to person-level demographics and insurance | National (survey) | Annual; 2024 file is HC-254A, 2023 is HC-248A | Bulk (SAS, Stata, ASCII, XLSX) | OK |
| **NHANES Prescription Medications (RXQ_RX)** | Self-reported prescription use in the past 30 days, linked to exam and lab data. The 2021–2023 file (`RXQ_RX_L`) has only a use indicator and a count; drug names and codes (`RXDDRUG`, `RXDDRGID`) are in earlier cycles, through 2017–March 2020 (`P_RXQ_RX`) | National (survey) | 1999–2023 | Bulk XPT | OK. Basis of the NCHS prescription drug use data briefs (cdc.gov pages: Browser) |
| **CDC opioid dispensing rate maps** | Retail opioid prescriptions per 100 persons (from IQVIA) | State, county (about 98% of counties) | 2019–2024 | Browser (CSV download on page) | OK in browser (Claude). National rate 46.8 (2019) to 35.4 (2024) per 100 persons, per the page; Codex's scripted check got 403 |
| **DEA ARCOS Retail Drug Summary** | Grams of controlled substances distributed, by state and 3-digit ZIP, per 100K population | State, 3-digit ZIP | Annual PDFs; 2025 is latest | Bulk PDF (tables need extraction) | OK. Buprenorphine is excluded from the 2024 and 2025 reports, pending DEA review |
| **VA Federal Supply Schedule pharmaceutical prices** | FSS, Big Four (statutory, at least 24% below non-federal average manufacturer price) and national contract prices by NDC | National | Updated around the 2nd and 16th of each month; `TPharmPrices2026-10-01.xlsx` | Bulk XLSX (department.va.gov) | OK. 43,225 price rows, 16,277 NDCs (30,447 FSS, 10,862 Big4, 1,916 NC) |
| **NPPES NPI Registry** | Every pharmacy with an NPI, address and taxonomy (e.g. Community/Retail Pharmacy 3336C0003X); an NPI does not prove the pharmacy is open or licensed | Address (geocodable) | Monthly full file, weekly incremental files, live API | API (200 rows per call) + Bulk ZIP | OK. API returned 186 community/retail pharmacies for Vermont |
| **Census County Business Patterns** | Pharmacy establishments and employment (NAICS 446110 in the 2017 coding) | County, ZIP | 2023 latest (41,792 establishments nationally) | API (key in main `.env`) + Bulk files | OK |

### State drug price transparency

| Source | What it gives | Access | Status 2026-10-20 |
|---|---|---|---|
| **California HCAI CTRx** | Manufacturer reports of WAC increases (over 16% cumulative in 3 years on drugs above $40 per course) and new drugs launched above the Part D specialty threshold; monthly updates | Bulk CSV/XLSX on the CHHS open data portal (`data.chhs.ca.gov`, dataset "prescription-drug-wholesale-acquisition-cost-wac-increases"); latest file covers Jan–Sep 2026 | OK. The old `hcai.ca.gov/data/cost-transparency/prescription-drug-costs/` URL is 404; use `/data/cost-transparency/rx/` |
| **Oregon Drug Price Transparency (DFR)** | Manufacturer price-increase and new-drug reports, insurer and PBM reports, annual legislative report (2025 report published 2025-12) | Browser (data pages and PDFs) | OK |
| **Vermont Attorney General** | Annual report to the Legislature (latest found: 2025-11-25) on 15 drugs chosen from lists that DVHA and large insurers submit of drugs with steep net-cost increases, plus drug spending context; it is a selected subset, not a complete ranking, and insurer data stays confidential | Browser (PDF reports) | OK |

### Not public or not usable for research

- **GoodRx** retail cash prices: no public dataset or open API found. A drug page returned 403 to Claude's scripted request, while Codex got the homepage; either way, extraction rights are not established. Treat as unavailable unless a licensed feed is arranged.
- **Mark Cuban Cost Plus Drugs**: posts prices on its site; the medications page returned 403 to Claude's scripted request (Codex reached the homepage). No documented public API found. Browser only, manual spot checks.
- **IQVIA, Symphony, SSR Health** (net prices): commercial licenses. CDC's opioid maps are the only free IQVIA-derived series found.
- **340B ceiling prices, Medicaid AMP and Best Price values, Part D rebates by drug**: confidential by statute.

### LAC comparison side (for cross-country projects)

- **Colombia SISMED** (prices and sales, 2010 onward): available through the Aphorics MCP configured on this machine (not checked from this session; Codex could not reach it).
- **Brazil CMED price lists** (ANVISA): monthly XLSX of factory (PF) and maximum consumer (PMC) prices, plus government purchase ceiling (PMVG). Checked 2026-10-20: latest list dated 2026-10-09.

## Things that trip people up

**NDC formats.** The FDA prints NDCs in three 10-digit layouts (4-4-2, 5-3-2, 5-4-1). CMS and most claims data use an 11-digit 5-4-2 form with no dashes, made by padding the short segment with a leading zero: `0071-0155-23` (4-4-2) becomes `00071015523`, `12345-678-90` (5-3-2) becomes `12345067890`, `12345-6789-0` (5-4-1) becomes `12345678900`. You cannot pad a dashless 10-digit NDC correctly without knowing its layout, so always normalize from the dashed form. In openFDA and the NDC directory, `product_ndc` is the two-segment labeler-product code (pads to NDC-9); only `packaging[].package_ndc` has the three-segment package code that pads to 11 digits. Both list only currently marketed products, so for discontinued NDCs in multi-year NADAC, SDUD or claims panels use RxNorm (`/REST/ndcstatus`, which keeps NDC history) or the Medicaid Drug Rebate Program product file. FDA will move all NDCs to a uniform 12-digit 6-4-2 format on 2033-03-07, with a three-year transition ([final rule, 91 FR 10749, 2026-03-05](https://www.federalregister.gov/documents/2026/03/05/2026-04368/revising-the-national-drug-code-format-and-drug-label-barcode-requirements)). Keep NDCs as strings; Excel and pandas drop leading zeros. NADAC and SDUD use 11 digits; the VA price file and the IRA file use dashed 11 digits; Part D spending files have no NDC at all (brand and generic names), so joins to NDC-level data go through RxNorm or name matching.

**Product NDC vs package NDC.** In the 11-digit form, the first 9 digits (labeler + product) identify the product; the last 2 the package. Price files are keyed by package NDC, but NADAC and FUL are per pricing unit, not per package. The IRA file gives both an NDC-9 price per unit and an MFP per 30-day equivalent supply.

**List vs net price.** WAC (wholesale acquisition cost) is the manufacturer's list price to wholesalers. AWP (average wholesale price) is a published benchmark set above WAC and used as a reference in many contracts; it is not a transaction price. NADAC is the average invoice price retail community pharmacies pay; it excludes off-invoice discounts and the rebates wholesalers or buying groups pay pharmacies, which can be large for generics. ASP (Part B) is the manufacturer's average sales price net of most discounts and rebates, reported to CMS (sales excluded from ASP include Medicaid rebates, 340B and federal purchaser sales; the published Part B file is the payment limit built on ASP, not raw ASP), so it is the one public price that approaches net. AMP drives Medicaid rebates and is confidential at product level (FUL publishes a weighted AMP per product group). WAC, AWP and NADAC do not subtract the rebates manufacturers pay to PBMs, insurers and Medicaid, and the spending files are gross: Medicare Part D Spending by Drug excludes manufacturer rebates by design, and its gross drug cost includes dispensing fees, sales tax and vaccine administration fees and pools all strengths and forms of a brand; Medicaid's State Drug Utilization Data is pre-rebate and includes dispensing fees. For some brands net is less than half of list; the gap varies by drug. For negotiated (IRA) drugs, CMS lets manufacturers give pharmacies the Maximum Fair Price either prospectively or as a retrospective refund (through the Medicare Transaction Facilitator's payment module or their own arrangement). Where it is a refund, the invoice price, and therefore NADAC, can stay well above the MFP, so NADAC alone cannot show what pharmacies net.

**NADAC specifics.** One row per NDC per weekly snapshot (`As of Date`), but CMS sets rates for rate groups (ingredient, strength, form, brand or generic, sometimes package size, `Explanation Code` 5), so most NDCs sharing a description carry the identical rate. Generic rates come from the monthly invoice survey. Brand rates also move between surveys: when a brand's published WAC changes, CMS applies the same percentage change to its NADAC (`Explanation Code` 3; `Primary Reason` "WAC Adjustment" in NADAC Comparison), so brand NADAC follows list-price moves; at a survey refresh a brand rate close to the surveyed cost is carried forward (`Explanation Code` 2) ([NADAC methodology](https://www.medicaid.gov/medicaid/prescription-drugs/retail-price-survey)). The `Corresponding Generic Drug NADAC Per Unit` column gives the generic rate next to a multi-source brand. The monthly survey refresh moves most rates at once (in 2026: 01-21, 02-18, 03-18, 04-22, 05-20, 06-17, 07-22, 08-19, 09-23, 10-21); other weeks change few rates. Covers retail community pharmacies only (`Pharmacy Type Indicator` = C/I), not mail order or specialty, so many specialty drugs are missing. `Pricing Unit` is EA, ML or GM: an Ozempic pen is priced per mL, so multiply by package volume. NADAC Comparison is the place to see why a rate moved: `Primary Reason` separates survey changes from WAC adjustments and help-desk corrections.

**Suppression of small counts.** Each CMS product has its own rule; read the methodology. In SDUD, rows with fewer than 11 prescriptions keep the row but blank the numbers (`suppression_used = true`), and secondary suppression blanks some larger rows so the small ones cannot be backed out: 652,561 of the 1,287,884 rows in 2026 Q1 are suppressed. Keep suppressed values missing (never zero, never in a unit-price denominator); summing published amounts understates totals. SDUD also carries national total rows (`state = XX`), suppressed only when the NDC is small nationally: use them for national totals, and drop them before summing states to avoid double counting. Part D prescriber files drop prescriber-drug combinations with 10 or fewer claims and blank age-65+ breakouts that would be small (`GE65_Sprsn_Flag`).

**Part D vs Part B.** Part D covers drugs dispensed by pharmacies (pills, pens, inhalers). Part B covers drugs administered in a clinic or hospital outpatient department (infusions, many cancer drugs, biologics), billed by HCPCS J-codes, not NDCs. Part B also pays for some pharmacy-dispensed drugs (oral transplant immunosuppressants and certain oral cancer and antiemetic drugs, nebulizer solutions used with durable medical equipment, insulin in external pumps, and some vaccines). The same molecule can sit in both. The ASP NDC-HCPCS crosswalk connects them; converting between NDC units and HCPCS billing units needs its package-size and billing-units-per-package fields. Even together the two files are not total Medicare drug spending: the Part B file covers traditional Medicare only (not drugs paid under Medicare Advantage's medical benefit), and drugs given during inpatient stays are bundled into Part A hospital payments.

**Medicaid fee-for-service vs managed care.** SDUD splits `FFSU` and `MCOU`. Most states moved enrollees into managed care over the 2010s, and some carve pharmacy back into FFS, so check each state's pharmacy benefit arrangement before reading an FFS-only trend as a change in prescribing.

**Spending files are drug-level, not person-level.** Part D Spending by Drug cannot tell you who uses a drug; MEPS can (with survey weights and a small sample).

**Brand classification.** NADAC's `B-ANDA` (brand name on a generic approval) and `B-BIO` (biosimilars), Medicaid's drug category S (single source), I (innovator multiple source), N (non-innovator) and FDA's therapeutic equivalence codes do not line up one to one. Pick one definition and state it.

## Starter project ideas

1. **US vs Colombia vs Brazil: what the same molecule costs.** NADAC (US pharmacy acquisition), VA Big Four (US government price), Medicare MFP (negotiated), SISMED (Colombia) and CMED PF (Brazil) for a basket of 30 WHO essential medicines and 10 high-spend brands, matched through ATC/RxNorm and normalized per defined daily dose. Shows US data fluency and Decilion's market access lens; the headline is that US generics are often cheaper than in LAC while brands are many times more expensive.
2. **IRA negotiation, first year.** Started 2026-10-20: see [ira_findings.md](ira_findings.md). Part D gross spending per claim fell by about two thirds for all ten 2026 drugs while comparison groups stayed flat; several manufacturers cut WAC on 2026-01-01 (Eliquis, Jardiance, Farxiga, Fiasp; Januvia a year earlier, on 2025-01-01); NADAC stays 1.3 to 3.6 times the MFP for most of them.
3. **Generic price shocks and shortages.** Link NADAC Comparison (weekly jumps over 100%) with openFDA shortages and ASHP counts: do price spikes precede or follow shortages, and are sole-source generics the ones that spike? A health economics question with policy relevance.
4. **Pharmacy deserts and Medicaid access.** Geocode NPPES community pharmacies (or use County Business Patterns), overlay county Medicaid enrollment and the Part D opioid prescribing map, and find counties with high need and few pharmacies. Connects to the expected-vs-observed county atlas in this repository.
5. **Who pays for insulin and GLP-1s?** MEPS prescribed-medicines files (out-of-pocket share by insurance, income, Hispanic origin) plus Part D and Medicaid spending trends, before and after the 2023 $35 insulin cap and the GLP-1 obesity boom.
6. **Open Payments and prescribing.** Join Open Payments to Part D Prescribers by NPI for one class (e.g. GLP-1s or anticoagulants) and describe how payment receipt relates to brand share. Descriptive only, with the well-known selection caveats.

## Starter dataset: NADAC

```
.venv/bin/python pharma/scripts/fetch_nadac.py 2025 2026     # ~250 MB, under a minute
.venv/bin/python pharma/scripts/summarize_nadac.py 2026
```

Pulled 2026-10-20: `nadac_2025.csv` (1,608,416 rows, snapshots to 2025-12-31) and `nadac_2026.csv` (1,268,309 rows, 42 weekly snapshots 2026-01-07 to 2026-10-21). Each file has a `.meta.json` with source URL, catalog date and SHA-256. Summary in [outputs/nadac_sanity.md](outputs/nadac_sanity.md); weekly tracer series in [outputs/nadac_tracers.csv](outputs/nadac_tracers.csv).

Highlights from the latest snapshot (2026-10-21): about 30,100 NDCs priced; all NDCs 11 digits, no duplicates within a snapshot. Median NADAC per tablet or capsule is $0.14 for generics and $12.67 for brands. Atorvastatin 20 mg costs a pharmacy about 3 cents a tablet, metformin 500 mg about 1.5 cents.

Review status (2026-10-20): Codex (GPT-6 Astra, high) recomputed every NADAC number blind from the raw files and re-checked all 49 catalog rows live: verdict PASS WITH FIXES (report in `reviews/pharma_codex_astra/report.md`). Its corrections are applied above: one row-count off-by-one in the 2025 sidecar, an effective-date comparison that bridged missing weeks, a crash with a single snapshot, and catalog wording (quarterly Part D fields, NHANES drug codes, ASP and MFP mechanics, release cadences). Agy (Gemini 4 Argon, high) recomputed the starter numbers blind with zero disagreements and reviewed the methods (PASS WITH FIXES, `reviews/pharma_agy_argon/REPORT.md`); its corrections on NADAC rate-setting, NDC history, SDUD national rows, price definitions and the tracer method are applied above.
