from pathlib import Path
import pandas as pd
import json
O=Path(__file__).resolve().parent

def table(name,cols=None,short_drugs=False):
 d=pd.read_csv(O/(name+'.csv'),dtype={'NDC':str})
 if cols:d=d[cols]
 if short_drugs and 'drug' in d:d['drug']=d.drug.str.split(';').str[0].str.strip()
 def f(v):
  if isinstance(v,float):return f'{v:.6f}'
  return str(v)
 return '| '+' | '.join(d.columns)+' |\n| '+' | '.join(['---']*len(d.columns))+' |\n'+'\n'.join('| '+' | '.join(f(v) for v in row)+' |' for row in d.itertuples(index=False,name=None))

report='''# Codex independent review of finding 4

**Verdict: PASS WITH FIXES.** The calculation is correct for the supplied files and the requested estimand. The independently written replication matches all **1,508,521 plan-segment-NDC rows**, including their unit costs, MFP denominators and ratios. All **783 summary-statistic cells** agree beyond floating-point noise, and all three above-MFP NDC summaries agree. Finding 4 contains two factual errors and overstates what reported plan pricing can establish. Correct the prose before treating the finding as cleared.

Reviewer: Codex, assigned Astra review. Date: 2026-10-20. No delegation, commits, source edits, login, or website-terms acceptance. This report is the independent Codex review, not a claim that the separate Agy review has finished.

## Independence and reproducibility

`replicate.py` was written and run on the raw ZIPs and CMS price CSV before opening `pharma/scripts/spuf_mfp_check.py`, anything in `pharma/outputs/spuf/`, or finding 4. `replication.md` and the Part A manifest were saved at **2026-10-20 23:50:59 UTC**. Only then were the author files opened. `compare.py` subsequently checked every matched row and all reported numeric summaries. See `numeric_comparison.csv`, `row_comparison.json`, and `reviewed_files_sha256.json` for the comparisons and reviewed-version hashes.

The raw pricing scans read 55,793,833, 53,249,171 and 54,052,371 rows respectively. All three were scanned in full. Retained records have DAYS_SUPPLY=30, a selected IPAY 2026 or 2027 NDC, and a valid applicable MFP. There are no duplicate contract-plan-segment-NDC keys, missing/negative/zero unit costs, or selected-NDC candidate rows without an applicable MFP in these inputs. There are **144 valid IPAY 2026 NDCs and 160 valid IPAY 2027 NDCs** in each lookup, many of which do not appear in a given pricing file. Counts below describe observed proxy NDCs, not all marketed packages or dispensed prescriptions.

The live CMS September 21 selected-drug CSV was also downloaded into `sources/` and is byte-identical to the supplied raw CSV. Pricing ZIPs were checked locally and hashed, not downloaded again.

## Part A: independently replicated numbers

### Which plan year is each release?

| Folder label | CMS release specified in brief | Plan year | Applicable IPAY 2026 denominator |
|---|---|---|---|
| 2025Q3 | SPUF_2025_20251009 | 2025 | Corrected 2026 MFP, as requested for baseline |
| 2025Q4 | SPUF_2026_20260107 | 2026 | MFP effective January 1, 2026 |
| 2026Q3 | SPUF_2026_20261007 | 2026 | MFP effective after June 1, 2026 |

CMS specifies that the first year in the outer SPUF filename is the contract year and the final date is the posting date. The raw sample formulary CONTRACT_YEAR fields separately corroborate 2025, 2026 and 2026 (`sample_contract_years.csv`). Release dates are not claim-service dates. [CMS SPUF methodology, p. 1](https://data.cms.gov/sites/default/files/2025-10/cf6b8476-ca42-48c6-9fc4-281b08c6ea87/Methodology-SPUF-2026.pdf).

Eliquis 5 mg, NDC 00003-0894-21, provides an independent price check:

'''+table('year_probe')+'''

MFP selection uses start <= reference date <= end, with blank end dates open-ended. Seventy impossible intervals are excluded: 11 starting in 2026 but ending in 2025, and 59 starting in 2027 but ending in 2026. The two Entresto Sprinkle NDCs use $1.229167 initially in 2026, then $5.521349 (00078-1231-20) and $5.648068 (00078-1238-20) from June 1. The baseline uses those corrected amounts, as the brief requires. IPAY 2027 always uses the January 2027 MFP and is explicitly a future benchmark. The author's date handling produces exactly the same denominators for these files.

### Group and plan-type results

All ratios are UNIT_COST / NDC-9 MFP per Unit Price. Percentages are percentages of unweighted rows. `within_pct` uses [0.995, 1.005], `below_pct` means <0.995, and `above_pct` means >1.005. These three categories partition the data. Plans use the full CONTRACT_ID + PLAN_ID + SEGMENT_ID key. Percentiles use linear interpolation. Keeping six decimals here is for reproducibility, not a claim of substantive precision.

'''+table('groups')+'''

IPAY 2026 split by S contracts (PDP) and H/R contracts (MA):

'''+table('plan_types')+'''

### Every IPAY 2026 NDC above the tolerance in a 2026 release

'''+table('above_mfp')+'''

These are **5,350 rows across three NDCs** in the January release. There are **zero** rows above 1.005 in the October release. The median ratios in this exception table are among above-threshold rows, not all rows of the NDC.

### Every drug and release

Names in this table use the first name of the CMS selected-drug group to match the author's labels. The full CMS names are retained in `drugs.csv` and `replication.md`; for example, NOVOLOG includes Fiasp, and OZEMPIC includes Rybelsus and Wegovy. All ten IPAY 2026 groups and all fifteen IPAY 2027 groups are present in every release.

'''+table('drugs',short_drugs=True)+'''

## Part B: ranked findings and fixes

### 1. High priority: reported average prices are not observed point-of-sale payments

**Location:** `pharma/ira_findings.md:33`, heading and last sentence. The assertion that these are the prices plans actually pay at the point of sale exceeds the evidence. SPUF UNIT_COST is a reported average across in-area retail pharmacies for a specified supply category, keyed to a proxy NDC. It is not a claim, the plan-funded portion of a claim, a patient payment, or a complete net expenditure measure. It does not list a separate price for every package and pharmacy. January is the publication of a 2026 schedule, not verification of every transaction beginning January 1. The narrow result, that reported unit prices cluster at the MFP, is strongly supported. All 40 drug-by-plan-type medians in the two 2026 releases round to 1.000 (`drug_plan_type_medians.csv`), so the statement that the pattern spans all ten drugs and both plan types is supported at that aggregate level.

**Fix:** use “Reported Part D retail unit prices cluster at the MFP in the 2026 pricing files.” Replace the final sentence with “This directly checks reported plan unit-price schedules against the MFP; it does not establish realized claim payments or net savings.” [CMS 2026 record layout, pricing file, p. 15](https://data.cms.gov/sites/default/files/2025-10/83da019f-fa24-483e-87de-cc089780a6a5/SPUFRecordLayout-2026.pdf).

### 2. High priority: the 2027 comparison median did not stay at 2.5 in both releases

**Location:** `pharma/ira_findings.md:33`. January is **2.525414**, October **2.111995**, a **16.37% decrease** in the pooled median ratio. Calling both 2.5 is not rounding. The script and summary table are right; the prose is wrong. Every 2027 row remains above 1.005, but stability does not follow. Linzess's drug median falls from approximately 3.992 to 1.986, and the observed NDC/plan mix also changes.

**Fix:** “The IPAY 2027 group remained above its future MFP, with median ratios of 2.525 in January and 2.112 in October.” Also replace the summary generator's prediction that the gap “will close next year” with “measures the gap to the future 2027 MFP.” An upper bound need not produce equality, and a future dataset has not been observed. Evidence: `groups.csv`, `drugs.csv`, and the matching author tables. [CMS selected drugs and negotiated prices](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices).

### 3. High priority: three exception NDCs, and disappearance does not establish correction of every row

**Location:** `pharma/ira_findings.md:33`. The assertion that “only” one product exceeded the MFP contradicts both independent replication and `above_mfp_2026.csv`. NDCs 57894-0440-03, 57894-0440-01 and 57894-0441-01 contribute 5,170, 138 and 42 rows respectively. The largest accounts for **96.64%**, not 100%, of exceptions. These are unbranded ustekinumab presentations included in CMS's STELARA group; the label need not mean the branded product.

The 0.5 mL vial's January median ratio is 2.470604. Of its 5,170 January above-threshold plan-NDC pairs, only 3,642 reappear in October; all are at or below the threshold. The other 1,528 are absent. All 138 and 42 exceptions for the other NDCs reappear at or below the threshold. `exception_followthrough.csv` documents this. Therefore “none observed above in October” is justified, while “corrected” is not established for every January row or as a cause of the change.

**Fix:** enumerate all three NDCs, describe the dominant one as an unbranded 45 mg/0.5 mL vial in the STELARA group, and say “No above-threshold observations remain in the October file.” Do not infer improper actual payments from these reported-price anomalies. [Manufacturer billing guide, pp. 23 and 35](https://asset.jnjwithme.com/document/ustekinumab-billing-and-coding-guide.pdf).

### 4. Medium priority: clarify fees, cost sharing and point-of-sale rebates

**Location:** `pharma/ira_findings.md:37`. Excluding dispensing fees from UNIT_COST is correct. The phrase “say nothing about rebates” is too broad: CMS explicitly directs sponsors to submit unit costs net of rebates and concessions applied at the point of sale; those amounts are not separately identified. Off-invoice/retrospective rebates and the plan's final net cost are not measured. Dispensing fees are separate fields in the pharmacy network file, while beneficiary copays and coinsurance are in separate benefit files. The drug unit cost is not reduced to the plan-paid amount by subtracting patient cost sharing.

**Fix:** “Unit costs exclude separately reported dispensing fees and incorporate concessions applied at the point of sale; they do not identify rebate amounts, final net plan spending, or beneficiary out-of-pocket costs.” The statutory ceiling is MFP **plus dispensing fees** for the negotiated price, so comparing ingredient unit cost with per-unit MFP is conceptually appropriate. [CMS 2026 pricing guidelines, pp. 14, 17 and 22–23, in this ZIP](https://www.cms.gov/files/zip/2026-pricing-data-guidelines-calendar.zip); [CMS final negotiation guidance, p. 196](https://www.cms.gov/files/document/medicare-drug-price-negotiation-final-guidance-ipay-2027-and-manufacturer-effectuation-mfp-2026-2027.pdf).

### 5. Medium priority: unit basis passes, but document it and retain the injectable anomaly

Both systems use NDC-specific NCPDP billing units, including EA, ML and GM, rather than a universal “pill” or “package.” DAYS_SUPPLY=30 selects a price schedule; it does not make UNIT_COST a 30-day total. Likewise the single drug-level MFP per 30-day equivalent supply is not the denominator used here. CMS's NDC-9 per-unit MFP is the appropriate denominator. The NCPDP unit requirement is explicit in the [2026 pricing guidelines, p. 14](https://www.cms.gov/files/zip/2026-pricing-data-guidelines-calendar.zip), and the MFP calculation uses dispensing quantities in [final guidance, sections 60.2 and 60.5](https://www.cms.gov/files/document/medicare-drug-price-negotiation-final-guidance-ipay-2027-and-manufacturer-effectuation-mfp-2026-2027.pdf).

Concrete checks:

- Eliquis 00003-0894-21 is compared per tablet: January median $4.1451 versus MFP $4.145072.
- Fiasp vial 00169-3201-11 is compared per mL: $6.9569 versus $6.956927. Fiasp FlexTouch 00169-3204-15 is also per mL: $8.9570 versus $8.956984 in January. Multiplying by 100 insulin units/mL, 3 mL per pen or 15 mL per carton would change one side's basis incorrectly. The [manufacturer's Fiasp presentation information](https://www.novomedlink.com/diabetes/products/treatments/fiasp/resources/for-pharmacists.html) and [CMS contractor NDC crosswalk](https://www.dmepdac.com/palmetto/PDAC_files.nsf/F/PDAC2025-10-05XWalk.pdf/%24FILE/2025-10-05XWalk.pdf) distinguish package, mL and therapeutic units.
- Enbrel's five observed NDCs all have January and October median ratios effectively 1.000 (`injectable_unit_checks.csv`). Liquid injectables use ML, while an EA-coded powder vial must retain its own billing basis; do not assume every injectable has the same physical unit.
- The manufacturer explicitly specifies **ML 0.5** for one 45 mg vial of 57894-0440-03. Its $8,979.645026 MFP is per mL; on a 0.5 mL basis it is $4,489.822513. January's $22,185.1436 median per mL becomes $11,092.5718 per vial, leaving the ratio **2.470604 unchanged**. The same NDC is effectively 1.000 in October. A package conversion does not erase the discrepancy. In January the vial price is approximately three times the same-plan 0.5 mL syringe's unit price for 4,547 of 4,662 paired plans. That is a reporting-pattern diagnostic, not proof of a valid threefold unit conversion or a specific cause. [Manufacturer guide, p. 35](https://asset.jnjwithme.com/document/ustekinumab-billing-and-coding-guide.pdf).

**Fix:** add a short explicit billing-unit note and retain these NDC checks with the analysis. No unit-conversion correction to the computed ratios is warranted by the evidence inspected. An exhaustive independent product-master audit of every observed NDC was not performed.

### 6. Medium priority: unweighted rows measure schedules, not patients, prescriptions or dollars

The existing unweighted qualifier is necessary and correct. However, the pooled percentage gives more influence to plans with more observed NDCs and to drugs with more package/product codes, with no regard to enrollment or use. In October, PDP contributes only **6.57% of rows**; its within-band share is 89.122885%, versus 91.438040% in MA. Holding within-type composition fixed, increasing PDP's weight lowers the overall within-band share. That alone cannot establish the effect of actual enrollment weights because enrollment varies within each type and the drug mix is unequal.

Two independently computed sensitivities show the choice of estimand:

'''+table('weight_sensitivity')+'''

`equal_plan_pct` first averages each plan-segment's observed NDC indicators, then gives each plan-segment equal weight. `equal_drug_pct` first averages within each CMS drug group and then gives each drug group equal weight. Neither is enrollment-weighted.

**Fix:** keep the current result as an unweighted schedule-level statistic. For beneficiary exposure, join date-matched [CMS monthly plan enrollment](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-advantagepart-d-contract-and-enrollment-data/monthly-enrollment-plan), handle suppressed counts, and reconcile the enrollment key with pricing segments without replicating each plan's full enrollment across its segments. First define a fixed drug/NDC basket or a within-plan summary; then weight that summary by enrollment. Simply attaching enrollment to every NDC also weights plans by their NDC counts. Prescription or spending effects additionally require actual utilization/quantity or expenditure weights. Actual enrollment-weighted shares were not estimated here, so their numerical change remains unknown. Within this observed October sample, zero above 1.005 remains zero under any nonnegative weights.

### 7. Medium priority: the 2027 group is a useful benchmark, not a causal control

It is reasonable to compare 2026 prices with the future MFP of selected 2027 drugs as a check that the entire database was not mechanically normalized to one. All its observed ratios remain above 1.005. It is not a randomized, therapeutically matched or demonstrably parallel-trending control: selection, price changes before implementation, generic competition and composition can differ. The present study therefore supports a descriptive contrast, not a treatment-effect estimate. The wider document's “Not causal” limitation is appropriate and should also govern finding 4.

The changing sample matters. IPAY 2026 observed NDCs decline from 49 to 46 to 44, and observed plan counts also change. In a common contract-plan-segment-NDC panel present in all three releases, the result remains:

'''+table('common_panel')+'''

The common panel preserves the near-one 2026 median, but January's within-band fraction is **98.729472%**, versus **92.747571%** in the full cross-section. It retains only four January above-threshold observations because the unbranded ustekinumab products were rarely observed in the 2025 baseline. This sensitivity is evidence of composition, not a reason to discard the full-sample exceptions. The common 2027 panel still declines from 2.452422 to 2.085909 across 2026, so its pooled decline is not solely caused by changing membership.

**Fix:** call it a future-price comparison group, report the declining medians correctly, and include the fixed-panel sensitivity. Do not call it a causal counterfactual or infer a guaranteed future convergence to exact equality.

### 8. Lower priority: 0.5% is a sensible descriptive band, not literal equality or a compliance allowance

Four-decimal SPUF unit costs and six-decimal MFPs will differ slightly after rounding. A symmetric 0.5% band is defensible for describing clustering, but much wider than numeric rounding: for a $8,980 unit it permits about $44.90 either side. Label “within 0.5%” consistently rather than turning it into exact “at.” In October, 101,228 rows are arithmetically above ratio 1, but the maximum ratio is only **1.000034611**, about **0.00346%** above; none exceed even 1.0001. They are consistent with four-decimal rounding, not substantive excesses.

Sensitivity for IPAY 2026, percentages within the stated band:

| Release | ±0.01% | ±0.1% | ±0.5% | ±1% |
|---|---:|---:|---:|---:|
| 2025Q3 | 0.017525 | 0.207792 | 1.095539 | 1.761475 |
| 2025Q4 | 91.508049 | 92.047084 | 92.747571 | 93.434280 |
| 2026Q3 | 88.777971 | 89.702949 | 91.285991 | 94.589414 |

**Fix:** define below/above as outside the band, write “none more than 0.5% above,” and retain `tolerance.csv`. For a strict equality audit, compare each UNIT_COST with its MFP rounded to four decimal places using an absolute rounding bound. Do not imply CMS legally permits 0.5% excess pricing. The broad empirical result survives much tighter tolerances.

## Suggested replacement for finding 4

**4. Reported Part D retail unit prices cluster at the MFP in the 2026 pricing files.** For observed products in the ten IPAY 2026 drug groups, the median reported unit-cost/MFP ratio fell from 2.767 in the 2025 plan-year file to 1.000 in both 2026 releases. In the January 2026 release, 92.7% of unweighted plan-segment-NDC rows were within 0.5% of the applicable MFP, 4.9% were more than 0.5% below and 2.3% were more than 0.5% above. In the October release, the corresponding shares were 91.3%, 8.7% and 0%. Drug-group medians were near one in both stand-alone PDP and Medicare Advantage plans. January's 5,350 above-threshold rows involved three unbranded ustekinumab NDCs in the STELARA group, predominantly the 45 mg/0.5 mL vial 57894-0440-03; no above-threshold observations remain in October. For IPAY 2027 drugs, whose MFPs were not yet effective, median ratios to their future MFP were 2.525 in January and 2.112 in October. These are reported average in-area retail unit prices for 30-day supply schedules, not observed claim payments, patient costs or net savings.

**Limits:** Rows are unweighted and use observed proxy NDCs rather than a fixed utilization basket. UNIT_COST excludes separate dispensing fees and incorporates concessions applied at the point of sale, without identifying rebate amounts or final net plan spending. Below and above refer to the 0.5% band. The January release's internal 2025Q4 label denotes 2026 plan prices. MFP denominators are date-specific, including the June Entresto Sprinkle correction; the 2025 comparison uses the corrected 2026 benchmark.

## Shortcuts taken

Actual enrollment weights and transaction-level claims were not acquired or estimated; they are not necessary to reproduce the specified unweighted analysis, and no claim about their numerical outcomes is made. Unit verification combined authoritative NCPDP rules with targeted insulin and injectable checks rather than a complete product-master audit. The supplied pricing ZIPs were not downloaded again; their hashes are preserved, contract years were corroborated, and the MFP source was checked against the live official download. The existing chart was not visually reviewed because the task asks for the script, tables and finding; every statistic supplied to its plotted medians and percentiles was verified. All writes are confined to this review folder.
'''
assert '\u2014' not in report
(O/'report.md').write_text(report)
print('Wrote',O/'report.md',len(report.split()),'words')
