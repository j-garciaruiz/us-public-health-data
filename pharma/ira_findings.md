# Medicare drug price negotiation, first year: what moved in January 2026

Status: draft, 2026-10-20. Descriptive analysis; under independent review (Codex Astra replication, Agy Argon method review). Numbers below come from `pharma/scripts/ira_analysis.py`; tables in [outputs/ira/summary.md](outputs/ira/summary.md).

## Question

The first ten Maximum Fair Prices (MFPs) negotiated under the Inflation Reduction Act took effect on 2026-01-01 for Medicare Part D. Three public CMS sources let us see what changed, from three angles:

| Angle | Source | Measures |
|---|---|---|
| What Medicare Part D records as spent | Quarterly Part D Spending by Drug (2025 full year, 2026 Q1) | Gross spending per claim |
| What manufacturers list | NADAC Comparison file, rows whose reason is a WAC adjustment | January list-price (WAC) cuts and increases by NDC |
| What pharmacies pay on invoice | NADAC weekly files 2024–2026, joined by NDC to the CMS MFP file | NADAC per unit divided by MFP per unit |

Comparison groups: the 15 drugs negotiated for 2027 and the 15 for 2028 (selected, similar high-spend brands, MFP not yet in effect) and all other brands.

## Findings

**1. Part D gross spending per claim fell by about two thirds for the negotiated drugs, and did not fall for the comparison groups.** Between 2025 and 2026 Q1, the median change across the ten drugs was −64% (range −28% for NovoLog to −71% for Enbrel; pooled across the ten, −62%). Drugs negotiated for 2027 changed by a median +2.4%, those for 2028 by +1.7%, and 1,088 other brand families by +0.3% (middle half −3.9% to +3.5%). Nine of the ten negotiated drugs fell by 30% or more; 2% of other brands did. The one large drop in the 2027 group, Linzess (−49%), follows a 50% list-price cut on 2026-01-01.

![Part D spending per claim](outputs/ira/chart_partd_per_claim.png)

**2. Manufacturers cut list prices on several negotiated drugs on the day the MFPs began.** NADAC records WAC-based rate cuts effective 2026-01-01 of 43% for Eliquis, 44% for Jardiance, 37% for Farxiga and 75% for NovoLog products. In January 2026, 30% of brand NDCs of the 2026 drugs had a WAC cut of 20% or more, against 1.5% of other brand NDCs, and only 19% had any WAC increase, against 38% of other brands. Januvia (and Janumet, a 2027 drug) had already been cut 42% on 2025-01-01. Large cuts were rare among other brands in every January checked (3.6% in 2024, 0.2% in 2025, 1.5% in 2026).

**3. Pharmacies still pay well above the negotiated price for most of these drugs.** NADAC, the average invoice cost of retail community pharmacies, was 2.0 to 3.4 times the 2026 MFP per unit in December 2025. By October 2026 the list-price cuts brought it to 1.00 times for NovoLog, 1.33 for Eliquis, 1.65 for Jardiance and 1.99 for Farxiga, while Januvia (2.70), Xarelto (2.84), Entresto (2.22), Stelara (3.32) and Enbrel (3.57) did not come down. Where the MFP is delivered as a refund after dispensing, the pharmacy pays this difference up front and waits to be made whole. Imbruvica has no NADAC (specialty distribution).

![NADAC relative to MFP](outputs/ira/chart_nadac_vs_mfp.png)

## How to read this (limits)

- **Gross, not net.** Part D spending is gross drug cost before manufacturer rebates. These brands carried large confidential rebates before 2026, so Medicare's net saving is smaller than the gross drop. CMS does not publish net prices.
- **Preliminary quarter.** 2026 Q1 Part D data were extracted three months after the quarter; CMS calls them preliminary and payment fields may still change.
- **Mix, not only price.** Spending per claim also moves with days supply and strength mix. Entresto (brand claims down 87% on an annualized basis, after generic entry), Stelara (down 44%, biosimilars) and Farxiga (down 30%) changed their user base at the same time, so part of their drop is composition.
- **Full year vs one quarter.** 2025 is a full year and 2026 is Q1. The near-zero median for other brands suggests no large first-quarter effect on gross cost per claim, but this was not tested against earlier first quarters.
- **NADAC covers retail community pharmacies only** and is per pricing unit; the MFP comparison uses CMS's NDC-9 MFP per unit for the period starting 2026-01-01 and assumes the same unit definitions.
- **Not causal.** A before/after change against comparison groups describes what happened; it does not separate the MFP from list-price strategy, generic and biosimilar entry, the 2025 Part D redesign or rebate renegotiations. Patients' out-of-pocket costs are not measured here.

## Where this could go

1. Add 2026 Q2 when CMS releases it, and an earlier Q1-vs-full-year baseline from the annual file to test the seasonality assumption.
2. Units-based price: the annual Part D file has dosage units; for 2026 it will allow spending per unit instead of per claim, removing days-supply mix.
3. The 2027 group: the same three charts become a pre-registered test for the next 15 drugs, whose MFPs start on 2027-01-01.
4. Pharmacy cash flow: combine NADAC − MFP gaps with Part D claim volumes to estimate the amount community pharmacies front each month while awaiting refunds.
