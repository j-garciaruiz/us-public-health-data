# Medicare drug price negotiation, first year: what moved in January 2026

Status: draft, 2026-10-20. Descriptive analysis, triple-checked: Codex (GPT-6 Astra) replicated every number blind (PASS WITH FIXES, `reviews/pharma_ira_codex_astra/report.md`) and Agy (Gemini 4 Argon) recomputed blind and reviewed the method (PASS WITH FIXES, `reviews/pharma_ira_agy_argon/REPORT.md`). Both reviews' fixes are applied. Numbers come from `pharma/scripts/ira_analysis.py`; tables in [outputs/ira/summary.md](outputs/ira/summary.md).

## Question

The first ten Maximum Fair Prices (MFPs) negotiated under the Inflation Reduction Act took effect on 2026-01-01 for Medicare Part D. Three public CMS sources show what changed, from three angles:

| Angle | Source | Measure |
|---|---|---|
| What Part D records as spent | Quarterly Part D Spending by Drug (2025 full year; 2026 Q1, preliminary) | Gross spending per claim |
| What manufacturers list | NADAC Comparison rows whose reason is a WAC adjustment | Early-year WAC-related NADAC cuts and increases, by NDC |
| What pharmacies pay on invoice | NADAC weekly files 2024–2026, joined by NDC to the CMS MFP file | NADAC per unit divided by the MFP per unit in effect |

Comparison groups: the 15 drugs negotiated for 2027 (MFP from 2027-01-01), the 15 selected for negotiation for 2028 (prices not yet published), and other brand-name products.

## Findings

**1. Part D gross spending per claim fell by about two thirds for all ten negotiated drugs, while the comparison groups barely moved.** Between 2025 and 2026 Q1 the median change across the ten was −64% (range −30% for NovoLog and Fiasp to −71% for Enbrel), and every one fell by 30% or more. Holding each group's 2025 drug mix fixed, the change was −61% for the ten, +1.5% for drugs negotiated for 2027, +1.2% for those selected for 2028 and +1.1% for 741 other brand-name products (their median was +0.9%, middle half −2.0% to +3.6%). Only 2% of other brands fell by 30% or more, and those are products whose manufacturers cut list prices at the same time: Novo Nordisk's Tresiba, Eli Lilly's Humalog U-200 and Lyumjev, and Boehringer Ingelheim's empagliflozin combinations (Synjardy, Glyxambi, Trijardy XR). In the 2027 group, Linzess (−49%) also follows a 50% list-price cut on 2026-01-01.

This is what the payment rules would produce: for a selected drug, the law caps the Part D negotiated price at the MFP plus dispensing fees ([SSA §1860D-2(d)(1)(D), added by Pub. L. 117-169](https://www.govinfo.gov/content/pkg/PLAW-117publ169/html/PLAW-117publ169.htm)), and gross drug cost in this file is built from those claim amounts. The aggregate data are consistent with MFP-based payment; they do not prove it for every claim or separate it from other changes.

![Part D spending per claim](outputs/ira/chart_partd_per_claim.png)

**2. On the day the MFPs began, four of the ten negotiated drugs took large list-price cuts, and so did some related non-selected brands.** NADAC records WAC-based cuts effective 2026-01-01 of 43% for Eliquis, 44% for Jardiance, 37% for Farxiga and 75% for Fiasp (the CMS NovoLog entry covers NovoLog and Fiasp; NovoLog itself had been cut 75% on 2024-01-01). Januvia, and Janumet in the 2027 group, had been cut 42% on 2025-01-01. In January 2026, 30% of the brand NDCs of the 2026 drugs had a cut of 20% or more, against 1.5% of other brand NDCs. Most of those other-brand cuts are not independent: 30 of the 33 are Boehringer Ingelheim's empagliflozin combinations, cut by the same 44.4% on the same day as Jardiance, and three are Tresiba; through February, Lilly's 70% cuts on Lyumjev and Humalog U-200 (2026-02-01) join them. List-price increases were as common for the 2026 drugs as for other brands once February is included (46% of their NDCs, from Xarelto on 2026-02-03 and Enbrel, Entresto and Stelara in January, against 39%). These are NADAC changes that CMS attributes to WAC changes, not a separate WAC series. Insulin list-price cuts also cluster around the removal of the Medicaid rebate cap on 2024-01-01, so the MFP is one of several candidate explanations; these data cannot separate them.

**3. NADAC remains well above the MFP for most of these drugs.** For brand-classified NDCs, NADAC, the average invoice cost of retail community pharmacies, was 2.2 to 4.0 times the 2026 MFP per unit at the end of December 2025, except NovoLog, already at 1.0 after its 2024 cut. By October 2026, after the January list-price cuts, it was 0.99 times for Fiasp, 1.33 for Eliquis, 1.65 for Jardiance and 2.00 for Farxiga. Januvia stayed at 2.70, and Xarelto (2.84), Entresto (2.22), Stelara (3.32) and Enbrel (3.57) rose slightly, by 2% to 5%, with their 2026 list-price increases. Ratios use the MFP in effect on each snapshot date (CMS corrected the Entresto Sprinkle MFP from 2026-06-01) and are the same on NDCs present in both snapshots. The CMS list also covers unbranded and authorized-generic NDCs (Novo Nordisk's insulin aspart, dapagliflozin) that carry generic NADAC rates and their own MFPs; they are reported separately in the summary tables.

This is a gap between an invoice benchmark and the MFP. CMS lets manufacturers effectuate the MFP prospectively or through retrospective refunds, by default computed as WAC minus MFP, with the Medicare Transaction Facilitator exchanging claim data ([CMS final guidance, sections 40.4 to 40.4.4](https://www.cms.gov/files/document/ipay-2028-final-guidance.pdf)). NADAC covers all payers' purchases, so a Part D-only refund cannot lower it; only a national list-price cut does. Where refunds apply, a gap like this is what dispensing pharmacies wait to recover; the data here do not show actual pharmacy losses, refund timing or amounts. No NADAC observations matched the Imbruvica NDCs.

![NADAC relative to MFP](outputs/ira/chart_nadac_vs_mfp.png)

## How to read this (limits)

- **Gross, not net. These data do not estimate net savings.** Part D spending is gross drug cost before manufacturer rebates (it includes dispensing fees and pools all strengths of a brand), and these brands carried confidential rebates before 2026; drug-level net spending is not in this dataset. For context only, CMS projected 22% aggregate net savings for the first ten drugs against a 2023 counterfactual ([CMS fact sheet](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026)); that is not an observed 2026 figure.
- **Preliminary quarter.** 2026 Q1 Part D data were extracted three months after the quarter; CMS calls them preliminary and warns they can be revised.
- **Mix, not only price.** Spending per claim also moves with days supply, strength and form. Entresto (brand claims down 87% on an annualized run-rate after generic entry in 2025), Stelara (down 44%, after biosimilar launches in 2025) and Farxiga (down 30%) may reflect mix and substitution as well as price; this analysis does not decompose it.
- **Drug mix across products.** Pooled per-claim spending for other brands rose 10.9%, but with 2025 claim shares held fixed it rose 1.1%: the difference is a shift of claims toward costlier drugs (GLP-1s, specialty drugs), not a price rise. The fixed-weight figures in finding 1 remove that shift; seasonality between a full year and a first quarter is not tested.
- **Name-based groups.** Part D rows have brand names, not NDCs. Selected families use the brand names in the CMS file (NovoLog Mix 70/30 is excluded: its NDCs are not on the list). Rows whose ingredients exactly match a selected drug but carry no selected brand name (unbranded and authorized generics) are left out of every group. "Other brands" is a name-based classification (brand string differs from the generic, its first word is not in the generic name, supplies excluded) and still contains a few generic products.
- **NADAC is retail, per unit and set per rate group.** It covers retail community pharmacies only; brand rates follow WAC changes between surveys. Ratios are unweighted medians across brand NDCs (69 in December 2025, 70 in October 2026), not weighted by claims. NADAC and CMS both use EA/ML/GM billing units, and per-NDC ratios were checked for outliers (two were found: an expired Entresto Sprinkle MFP, now handled by date, and the Fiasp PumpCart, which carries the vial MFP in the CMS file).
- **The 2026 list is already changing.** The CMS file end-dates the MFP of Entresto, NovoLog/Fiasp, Stelara and Xarelto at 2026-12-31 (marked "deselected"), so from 2027 only six of the ten keep an MFP.
- **Not causal.** A before/after change against comparison groups describes what happened. It does not separate the MFP from list-price strategy, the 2024 Medicaid rebate-cap change, generic and biosimilar entry, the 2025 Part D redesign, rebate renegotiation or anticipation by drugs selected later (Janumet and Linzess cut list prices before their MFPs). Patients' out-of-pocket costs are not measured.

## Where this could go

1. Add 2026 Q2 when CMS releases it, and earlier first quarters from archived quarterly releases to test seasonality.
2. Spending per dosage unit from the annual Part D file (available for 2026 once released) removes days-supply variation, though strengths and forms still need standardizing.
3. The 2027 group: write down the outcomes for the next 15 drugs, whose MFPs start on 2027-01-01, before their data arrive (the 2026 results have already been seen).
4. Pharmacy exposure: an estimate of what pharmacies front before refunds needs eligible quantities, actual acquisition and refund dates and 340B handling, not only NADAC and MFP per unit.
