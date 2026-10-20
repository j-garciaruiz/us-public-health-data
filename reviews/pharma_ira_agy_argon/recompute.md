# Independent Blind Recompute: IRA Medicare Drug Price Negotiation Study (January 2026)

This document records the independent blind design and recomputation of Part 1 of `reviews/pharma_ira_agy_task.md`, completed and saved prior to inspecting `pharma/scripts/ira_analysis.py`, `pharma/outputs/ira/`, `pharma/ira_findings.md`, or `reviews/pharma_ira_codex_astra/`.

---

## 1. Own Study Design and Results for (a), (b), and (c)

### 1.1 Design Principles
To measure what changed in January 2026 when the first ten Medicare Maximum Fair Prices (MFPs) took effect on `2026-01-01`, a sound empirical design must address three structural features of the CMS Part D, NADAC, and IRA MFP datasets:

1. **Part D Point-of-Sale Price vs. Composition Confounding**:
   - Under Social Security Act Section 1193(a)(1) and Section 1860D-2(d)(1)(B), the Part D "negotiated price" reported on Prescription Drug Event (PDE) records for selected drugs in 2026 cannot exceed the MFP (plus dispensing fee).
   - However, `partd_spending_quarterly.csv` reports only `Tot_Spndng`, `Tot_Clms`, and `Tot_Benes` (omitting `Tot_Dsg_Unts` and `Tot_Days_Supply`, which are reported only in `partd_spending_annual.csv` through 2024). Therefore, `Avg_Spnd_Per_Clm = Tot_Spndng / Tot_Clms` conflates changes in unit price with changes in average units per claim (e.g., 30-day vs. 90-day fills, strength mix, or formulation mix).
   - Our design supplements the raw 2025 (Q1-Q4) to 2026 (Q1) per-claim change with: (i) the 2024 baseline (`Tot_Spndng_2024 / Tot_Clms_2024` and `Tot_Dsg_Unts_2024 / Tot_Clms_2024` from `partd_spending_annual.csv`), (ii) theoretical 2026 per-claim spending at constant 2024 units per claim (`UPC_2024 * MFP_Per_Unit`), (iii) annualized claim volume change (`4 * Clms_2026Q1 / Clms_2025 - 1`) and generic/biosimilar entry tracking to detect volume flight and days-supply compression, and (iv) disaggregation of multi-brand families (`NovoLog` vs. `Fiasp`) where constituent brands had different pre-2026 pricing histories.
2. **WAC List-Price Adjustments vs. Survey Drift**:
   - In `nadac_comparison.csv`, wholesale list-price changes are explicitly tagged with `Primary Reason == "WAC Adjustment"`, whereas routine pharmacy invoice survey updates are tagged `"Survey Rate"`. Our design tracks every `WAC Adjustment` event from 2024 through 2026 at the exact NDC-11 level across IPAY 2026, IPAY 2027, IPAY 2028, and non-selected brand comparators, distinguishing January 2026 cuts from earlier cuts (January 2024 `NovoLog`, January 2025 `Januvia`) and non-MFP cuts driven by the 2024 removal of the Medicaid 100%-of-AMP rebate cap.
3. **Exact NDC-11 Paired Acquisition Cost Ratio (`NADAC_i / MFP_i`)**:
   - Different NDCs within a single selected drug family can have different NCPDP billing units (`EA` vs. `ML`, as in `Xarelto` tablets vs. oral suspension), different concentrations (`Stelara` 5 mg/mL IV vial vs. 90 mg/mL subcutaneous syringe), or different device form factors (`NovoLog` vial `$6.96/mL` vs. FlexPen `$8.96/mL`).
   - Computing an unpaired ratio `median(NADAC) / median(MFP)` across a drug family mismatches formulations and units. Our design links NADAC snapshots (`12/31/2025` for end-of-2025 and `01/14/2026` plus `10/21/2026` for 2026) to `selected_drugs_mfp.csv` on exact 11-digit `NDC` (`NDC-11` stripped of hyphens), deduplicates identical `NDC-11` rows in the MFP file, and computes the exact paired ratio `R_i = NADAC_i / MFP_i` for each NDC before taking the within-drug median.

---

### 1.2 Part (a): Medicare Part D Spending per Claim (Own Design)

#### Table 1A: IPAY 2026 Selected Drugs in Medicare Part D (2024, 2025 Q1-Q4, and 2026 Q1)

| Drug Family (`Brnd_Name` rows summed) | 2024 SPC ($) | 2025 SPC ($) | 2026 Q1 SPC ($) | 2024 to 2025 (%) | 2025 to 2026 Q1 (%) | 2024 Units / Clm | Implied 2026 Units / Clm (`SPC_26 / MFP`) | Ann. Claim Vol. Chg (%) | Key Structural / Market Mechanism |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **Eliquis** (`Eliquis`) | $863.42 | $912.31 | $399.01 | +5.66% | **-56.26%** | 89.61 EA | 95.33 EA | -1.34% | POS price dropped to MFP (`$4.1855/EA`); stable 90d share |
| **Enbrel** (`Enbrel`, `Enbrel Mini`, `Enbrel Sureclick`) | $7,881.14 | $8,681.63 | $2,536.74 | +10.16% | **-70.78%** | 4.33 ML | 4.42 ML | +1.03% | POS price dropped to MFP (`$573.72/mL`); WAC rose +5% |
| **Entresto** (`Entresto`, `Entresto Sprinkle`) | $1,031.16 | $1,077.56 | $323.74 | +4.50% | **-69.96%** | 93.40 EA | 62.01 EA | **-86.50%** | Generic `Sacubitril-Valsartan` entry (`1.08M` Q1 clms); 90d fills left brand, shrinking units/claim by -33.6% |
| **Farxiga** (`Farxiga`) | $938.93 | $997.75 | $328.97 | +6.26% | **-67.03%** | 51.27 EA | 54.39 EA | **-30.45%** | POS price dropped to MFP (`$6.0488/EA`); generic `Dapagliflozin` grew to `746k` Q1 clms |
| **Imbruvica** (`Imbruvica`) | $15,478.17 | $16,055.46 | $9,646.30 | +3.73% | **-39.92%** | 37.57 EA | 31.02 EA | -12.63% | POS price dropped to MFP (`$311.00/EA`); specialty oncology |
| **Januvia** (`Januvia`) | $945.51 | $556.08 | $214.01 | **-41.19%** | **-61.51%** | 52.64 EA | 56.81 EA | -5.54% | Cut WAC -42.41% on `2025-01-01`; POS dropped to MFP (`$3.767/EA`) in 2026 Q1 (-77.37% vs. 2024) |
| **Jardiance** (`Jardiance`) | $1,005.96 | $1,091.19 | $386.83 | +8.47% | **-64.55%** | 53.15 EA | 56.92 EA | +0.13% | POS price dropped to MFP (`$6.7959/EA`); WAC cut -44.39% |
| **NovoLog / Fiasp (all 7 brand rows)** | $325.53 | $293.80 | $204.42 | -9.75% | **-30.42%** | 25.07 ML | 23.80 ML | +41.35% | Blended average of pre-cut `NovoLog` and newly cut `Fiasp` |
| *-- Sub-family: NovoLog (3 rows: Vial, FlexPen, PenFill)* | *$221.38* | *$221.96* | *$202.48* | *+0.26%* | ***-8.78%*** | *25.43 ML* | *23.59 ML* | *+46.15%* | *Already cut WAC -75% on `2024-01-01` to match MFP level* |
| *-- Sub-family: Fiasp (4 rows: Vial, FlexTouch, PenFill, PumpCart)* | *$796.71* | *$809.33* | *$225.79* | *+1.58%* | ***-72.10%*** | *23.47 ML* | *26.06 ML* | *+6.88%* | *Cut WAC -75% and effectuated MFP on `2026-01-01`* |
| **Stelara** (`Stelara`) | $25,424.43 | $26,682.00 | $8,424.82 | +4.95% | **-68.43%** | 1.85 ML | 1.72 ML | **-43.77%** | POS price dropped to MFP (`$4,897.45/mL`); 6 ustekinumab biosimilars entered in 2025-2026 |
| **Xarelto** (`Xarelto`) | $935.74 | $1,006.21 | $374.04 | +7.53% | **-62.83%** | 54.10 EA | 56.79 EA | -9.95% | POS price dropped to MFP (`$6.586/EA` for tablets); WAC rose +2.3% |
| **IPAY 2026 Summary (10 families)** | **$942.22** (med) | **$1,001.98** (med) | **$380.44** (med) | **+5.30%** (med) | **-63.69%** (med) / **-59.17%** (mean) | -- | -- | **-7.75%** (med) | Claim-weighted pooled SPC fell **-61.69%** (`$1,082.97` to `$414.88`) |

#### Table 1B: Comparison Across Cohorts in Medicare Part D (2025 Q1-Q4 vs. 2026 Q1)

| Drug Cohort | Number of Drug Families / Rows | Median SPC Change (%) | Mean SPC Change (%) | 25th Percentile (%) | 75th Percentile (%) | Notable Outliers / Key Drivers |
|---|---:|---:|---:|---:|---:|---|
| **IPAY 2026 Selected Drugs** (family-summed) | 10 families | **-63.69%** | **-59.17%** | -68.08% | -57.57% | All 10 fell (`-30.42%` to `-70.78%`); Fiasp alone fell `-72.10%`, NovoLog alone `-8.78%` |
| **IPAY 2027 Selected Drugs** (family-summed, MFPs effective 2027) | 15 families | **+2.37%** | **-0.78%** | +1.29% | +3.72% | `Linzess` fell **-49.02%** (`$843.43` to `$429.99`) after a `-50.27%` WAC cut on `2026-01-01`; the other 14 drugs ranged from `-0.69%` (`Ibrance`) to `+9.31%` (`Austedo`), median `+2.42%` |
| **IPAY 2028 Selected Drugs** (family-summed, MFPs effective 2028, in Part D) | 15 families | **+1.71%** | **+1.13%** | -1.24% | +4.25% | `Xeljanz` fell `-7.30%` (after `-25.00%` WAC cut on 5 mg tablets on `2026-01-01`); `Cosentyx` rose `+5.75%` |
| **Other Brand-Name Drugs** (`Brnd_Name != Gnrc_Name`, excl. IPAY 2026/27/28, `Clms_25 >= 4,000` & `Clms_26 >= 1,000`) | 1,108 rows | **+0.28%** | **-1.15%** | -3.91% | +3.55% | AMP-cap WAC cuts drove steep drops in non-selected insulins (`Tresiba` `-72.2%`, `Humalog` `-44.3%`) and BI SGLT2 combinations (`Synjardy` `-42.7%`, `Glyxambi` `-43.4%`, `Trijardy XR` `-44.0%`) |
| **Other Brand-Name Drugs** (`Brnd_Name != Gnrc_Name`, excl. IPAY 2026 only, `Clms_25 >= 4,000` & `Clms_26 >= 1,000`) | 1,150 rows | **+0.38%** | **-1.09%** | -3.81% | +3.57% | Using exact IPAY 2026 row exclusions (`N = 1,154`): median **+0.36%** (`+0.37%` via `Avg_Spnd_Per_Clm`) |
| **Single-Source Brand Drugs** (`Brnd_Name != Gnrc_Name`, `Tot_Mftr == 1`, excl. IPAY 2026) | 806 rows | **+0.85%** | **-0.53%** | -2.62% | +3.96% | Removes multi-source brands experiencing generic substitution |

---

### 1.3 Part (b): Manufacturer List Prices (WAC Adjustments in NADAC, 2024 to 2026)

In `nadac_comparison.csv`, wholesale list-price changes (`Primary Reason == "WAC Adjustment"`) show a sharp bifurcation among the 10 IPAY 2026 drugs:
- **Four IPAY 2026 drug families cut WAC in January 2026**:
  1. **Eliquis**: `-43.00%` across all 6 NDCs (effective `01/01/2026`, NADAC comparison date `01/14/2026`).
  2. **Jardiance**: `-44.39%` across all 6 NDCs (effective `01/01/2026`, NADAC comparison date `01/07/2026`).
  3. **Farxiga**: `-37.00%` across all 5 branded Farxiga NDCs (effective `01/01/2026`, NADAC comparison date `01/14/2026`).
  4. **Fiasp** (part of the `NovoLog / Fiasp` selected drug): `-75.00%` across all 4 Fiasp NDCs (effective `01/01/2026`, NADAC comparison date `01/14/2026`).
- **Two IPAY 2026 drug families had already cut WAC by >40% before 2026 (coinciding with the 2024 Medicaid AMP rebate cap removal) and made zero WAC adjustments in 2026**:
  5. **NovoLog**: `-75.00%` across all 3 IPAY 2026 NovoLog NDCs on effective date `01/01/2024` (NADAC comparison date `01/10/2024`); no WAC changes in 2025 or 2026.
  6. **Januvia**: `-42.41%` across all 13 Januvia NDCs on effective date `01/01/2025` (NADAC comparison date `01/01/2025`); no WAC changes in 2026.
- **Four IPAY 2026 drug families increased WAC in early 2026 (relying on retrospective MTF refunds rather than WAC cuts to deliver the MFP)**:
  7. **Enbrel**: `+5.00%` across 4 NDCs (effective `01/01/2026`, comparison date `01/07/2026`, following `+5.00%` in Jan 2024 and `+5.00%` in Jan 2025).
  8. **Entresto**: `+3.00%` across 5 NDCs (effective `01/02/2026`, comparison date `01/07/2026`, following `+3.00%` in Jan 2024 and `+3.50%` in Jan 2025).
  9. **Stelara**: `+5.00%` across 2 NDCs (effective `01/02/2026`, comparison date `01/07/2026`, following `+4.50%` in Jan 2024 and `+5.00%` in Jan 2025).
  10. **Xarelto**: `+2.30%` across 18 NDCs (effective `02/03/2026`, comparison date `02/04/2026`, following `+4.50%` in Jan 2024 and `+3.50%` in Jan 2025).
  *(Note: **Imbruvica** has zero NDCs in NADAC because it is dispensed through specialty pharmacies outside the retail community pharmacy NADAC survey.)*

- **Comparison with IPAY 2027, IPAY 2028, and Non-Selected Brands**:
  - Among **IPAY 2027** drugs (whose MFPs do not take effect until `2027-01-01`), **Linzess** cut WAC by `-50.27%` on `2026-01-01` (after cutting `-8.89%` on `2025-01-01`), and **Janumet / Janumet XR** cut WAC by `-42.41%` on `2025-01-01` (matching Januvia). The other IPAY 2027 drugs in NADAC posted routine January 2026 WAC increases of `+2.0%` to `+6.8%` (`Breo Ellipta` `+2.0%`, `Trelegy Ellipta` `+2.65%`, `Tradjenta` `+3.0%`, `Austedo` `+5.5%`, `Otezla` `+6.24%`, `Xifaxan` `+6.8%`).
  - Among **IPAY 2028** drugs, **Xeljanz 5 mg** cut WAC by `-25.00%` on `2026-01-01` (while `Xeljanz 10 mg` and `Xeljanz XR` rose `+3.0%`), and other IPAY 2028 drugs rose `+3.0%` to `+7.0%`.
  - Among **non-selected brands**, large January 2026 WAC cuts occurred in product lines with high Medicaid inflation rebates or shared active ingredients with selected drugs: Boehringer Ingelheim cut non-selected `Synjardy`, `Synjardy XR`, `Glyxambi`, and `Trijardy XR` by the exact same `-44.39%` on `2026-01-01` as `Jardiance`; Novo Nordisk cut non-selected `Tresiba` by `-72.18%` on `2026-01-01`; Eli Lilly cut non-selected `Lyumjev` and `Humalog 200 U/mL` by `-70.00%` on `2026-02-01`.

---

### 1.4 Part (c): Pharmacy Acquisition Cost (NADAC) Relative to the MFP

Linking `nadac_2025.csv` (last snapshot `12/31/2025`) and `nadac_2026.csv` (both early January `01/14/2026` and latest snapshot `10/21/2026`) to `selected_drugs_mfp.csv` (`MFP Effective Date == "01/01/2026"`) on exact 11-digit NDC reveals that retail pharmacy acquisition cost (`NADAC`) **remained substantially above the MFP for 8 of the 9 selected drugs present in NADAC**:

1. **Full List-Price Convergence to MFP (1 drug family: `NovoLog / Fiasp`)**:
   - After `NovoLog` cut WAC `-75%` in Jan 2024 and `Fiasp` cut WAC `-75%` in Jan 2026, all 6 primary branded NovoLog and Fiasp NDCs have 2026 NADAC equal to `0.995x–0.998x` of their 2026 MFP (`$6.93–$8.95/mL` NADAC vs. `$6.96–$8.96/mL` MFP).
2. **Partial List-Price Cut, Acquisition Cost Still 1.33x–1.99x Above MFP (3 drugs: `Eliquis`, `Jardiance`, `Farxiga`)**:
   - Even after their `-37%` to `-44.39%` January 2026 WAC cuts, 2026 NADAC remains above the MFP because their negotiated MFPs represented 62%–79% discounts off 2025 WAC:
     - `Eliquis`: NADAC/MFP fell from `2.34x` (`12/31/2025`) to **`1.33x`** (`01/14/2026` and `10/21/2026`).
     - `Jardiance`: NADAC/MFP fell from `2.96x` (`12/31/2025`) to **`1.65x`** (`01/14/2026` and `10/21/2026`).
     - `Farxiga`: Branded NADAC/MFP fell from `3.17x` (`12/31/2025`) to **`1.99x`** (`01/14/2026` and `10/21/2026`).
3. **No 2026 WAC Cut, Acquisition Cost 2.22x–3.57x Above MFP (5 drugs: `Entresto`, `Januvia`, `Xarelto`, `Stelara`, `Enbrel`)**:
   - Manufacturers kept WAC unchanged (`Januvia` at **`2.70x`** MFP) or raised WAC in Jan/Feb 2026 (`Entresto` **`2.16x` -> `2.22x`**, `Xarelto` **`2.78x` -> `2.84x`**, `Stelara` **`3.16x` -> `3.32x`**, `Enbrel` **`3.40x` -> `3.57x`**).
   - For these 8 drugs where `NADAC > MFP`, retail pharmacies purchase inventory at `1.33x–3.57x` the MFP, get reimbursed at most the MFP at the Part D point of sale, and rely on retrospective **Medicare Transaction Facilitator (MTF)** manufacturer refunds (`WAC - MFP`) to bridge the working-capital gap.

---

## 2. Fixed Quantities for Comparability

### 2.1 Fixed Quantity 1: Gross Part D Spending per Claim, 2025 vs. 2026 Q1

**Specification**: For each of the ten IPAY 2026 drugs, sum `Tot_Spndng` and `Tot_Clms` across all brand-name rows of each drug family in `partd_spending_quarterly.csv` with `Mftr_Name == "Overall"`, comparing `2025 (Q1-Q4)` against `2026 (Q1)`. Also report sensitivity variants for single-row vs. multi-row families and for the comparison group of other brand-name drugs with `Tot_Clms >= 4,000` in 2025 and `Tot_Clms >= 1,000` in 2026 Q1.

#### Table 2.1A: Ten IPAY 2026 Drugs -- Gross Part D Spending per Claim (2025 vs. 2026 Q1)

| Selected Drug | `Brnd_Name` Rows Summed (`Mftr_Name == "Overall"`) | 2025 `Tot_Spndng` ($) | 2025 `Tot_Clms` | 2025 Spending / Claim ($) | 2026 Q1 `Tot_Spndng` ($) | 2026 Q1 `Tot_Clms` | 2026 Q1 Spending / Claim ($) | % Change (2025 to 2026 Q1) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Eliquis** | `Eliquis` | $24,047,711,043.00 | 26,359,023 | **$912.31** | $2,594,033,195.88 | 6,501,172 | **$399.01** | **-56.26%** |
| **Enbrel** | `Enbrel`, `Enbrel Mini`, `Enbrel Sureclick` | $4,113,063,403.00 | 473,766 | **$8,681.63** | $303,561,536.52 | 119,666 | **$2,536.74** | **-70.78%** |
| **Entresto** | `Entresto`, `Entresto Sprinkle` | $3,928,765,105.00 | 3,645,979 | **$1,077.56** | $39,847,573.11 | 123,085 | **$323.74** | **-69.96%** |
| **Farxiga** | `Farxiga` | $6,721,167,568.00 | 6,736,318 | **$997.75** | $385,299,858.09 | 1,171,247 | **$328.97** | **-67.03%** |
| **Imbruvica** | `Imbruvica` | $2,355,271,994.00 | 146,696 | **$16,055.46** | $309,077,195.29 | 32,041 | **$9,646.30** | **-39.92%** |
| **Januvia** | `Januvia` | $2,150,942,112.00 | 3,868,076 | **$556.08** | $195,494,251.72 | 913,473 | **$214.01** | **-61.51%** |
| **Jardiance** | `Jardiance` | $15,087,584,932.00 | 13,826,680 | **$1,091.19** | $1,338,904,897.81 | 3,461,230 | **$386.83** | **-64.55%** |
| **NovoLog / Fiasp** | 7 brand rows (see Table 2.1B for variants) | $564,239,705.00 | 1,920,477 | **$293.80** | $138,728,539.77 | 678,635 | **$204.42** | **-30.42%** |
| **Stelara** | `Stelara` | $3,227,508,549.00 | 120,962 | **$26,682.00** | $143,247,207.34 | 17,003 | **$8,424.82** | **-68.43%** |
| **Xarelto** | `Xarelto` | $6,551,637,029.00 | 6,511,197 | **$1,006.21** | $548,293,383.25 | 1,465,876 | **$374.04** | **-62.83%** |

#### Table 2.1B: Sensitivity Variants for Multi-Row Drug Families in Part D

| Drug Family & Row Definition Variant | `Brnd_Name` Rows Included | 2025 `Tot_Clms` | 2025 SPC ($) | 2026 Q1 `Tot_Clms` | 2026 Q1 SPC ($) | % Change |
|---|---|---:|---:|---:|---:|---:|
| **Enbrel (all 3 rows)** | `Enbrel`, `Enbrel Mini`, `Enbrel Sureclick` | 473,766 | $8,681.63 | 119,666 | $2,536.74 | **-70.78%** |
| **Enbrel (exact 1 row only)** | `Enbrel` | 98,175 | $8,633.28 | 21,986 | $2,541.17 | **-70.57%** |
| **Entresto (both rows)** | `Entresto`, `Entresto Sprinkle` | 3,645,979 | $1,077.56 | 123,085 | $323.74 | **-69.96%** |
| **Entresto (exact 1 row only)** | `Entresto` | 3,645,454 | $1,077.74 | 122,431 | $325.48 | **-69.80%** |
| **NovoLog / Fiasp (7 brand rows in CMS NDC list)** | `Novolog`, `Novolog Flexpen`, `Novolog Penfill`, `Fiasp`, `Fiasp Flextouch`, `Fiasp Penfill`, `Fiasp Pumpcart` | 1,920,477 | $293.80 | 678,635 | $204.42 | **-30.42%** |
| **NovoLog / Fiasp (6 exact names in CMS Drug Name string)** | Same as above minus `Fiasp Pumpcart` | 1,919,863 | $293.49 | 678,368 | $204.40 | **-30.35%** |
| **NovoLog / Fiasp (9 prefix-matched rows, incl. non-selected Mix 70-30)** | 7 brand rows + `Novolog Mix 70-30`, `Novolog Mix 70-30 Flexpen` | 2,132,339 | $291.85 | 738,999 | $208.94 | **-28.41%** |
| **NovoLog / Fiasp + Unbranded Insulin Aspart (10 selected rows)** | 7 brand rows + `Insulin Aspart`, `Insulin Aspart Flexpen`, `Insulin Aspart Penfill` | 2,730,776 | $254.68 | 767,579 | $190.00 | **-25.40%** |
| **NovoLog only (3 selected NovoLog rows)** | `Novolog`, `Novolog Flexpen`, `Novolog Penfill` | 1,690,829 | $221.96 | 617,328 | $202.48 | **-8.78%** |
| **NovoLog only (5 prefix rows incl. Mix 70-30)** | `Novolog`, `Novolog Flexpen`, `Novolog Penfill`, `Novolog Mix 70-30`, `Novolog Mix 70-30 Flexpen` | 1,902,691 | $227.79 | 677,692 | $207.54 | **-8.89%** |
| **NovoLog (single row `Novolog` only)** | `Novolog` | 305,717 | $260.58 | 105,650 | $239.55 | **-8.07%** |
| **Fiasp only (4 selected Fiasp rows)** | `Fiasp`, `Fiasp Flextouch`, `Fiasp Penfill`, `Fiasp Pumpcart` | 229,648 | $809.33 | 61,307 | $225.79 | **-72.10%** |

#### Table 2.1C: Median Change Across Other Brand-Name Drugs (`Clms_2025 >= 4,000` and `Clms_2026Q1 >= 1,000`)

| Filter Definition for "Other Brand-Name Drugs" | Number of Drug Rows (`N`) | Median % Change (`Tot_Spndng / Tot_Clms`) | Median % Change (`Avg_Spnd_Per_Clm` col) | Mean % Change | IQR (25th to 75th Percentile) |
|---|---:|---:|---:|---:|---|
| **`Brnd_Name != Gnrc_Name`**, excluding IPAY 2026 (prefix match) | 1,150 | **+0.38%** | **+0.39%** | -1.09% | -3.81% to +3.57% |
| **`Brnd_Name != Gnrc_Name`**, excluding IPAY 2026 (exact match) | 1,154 | **+0.36%** | **+0.37%** | -1.21% | -3.83% to +3.56% |
| **`Brnd_Name != Gnrc_Name`**, excluding IPAY 2026, 2027, 2028 (prefix) | 1,108 | **+0.28%** | **+0.25%** | -1.15% | -3.91% to +3.55% |
| **`Brnd_Name != Gnrc_Name`**, excluding IPAY 2026, 2027, 2028 (exact) | 1,116 | **+0.29%** | **+0.29%** | -1.25% | -3.93% to +3.53% |
| **All `Overall` rows** (incl. generics where `Brnd_Name == Gnrc_Name`), excl. IPAY 2026 (prefix) | 1,713 | **+0.24%** | **+0.24%** | -1.16% | -5.80% to +4.09% |
| **All `Overall` rows** (incl. generics), excl. IPAY 2026, 2027, 2028 (prefix) | 1,671 | **+0.11%** | **+0.12%** | -1.21% | -5.94% to +4.07% |
| **Single-source brand rows** (`Brnd_Name != Gnrc_Name`, `Tot_Mftr == 1`), excl. IPAY 2026 | 806 | **+0.85%** | **+0.85%** | -0.53% | -2.62% to +3.96% |

---

### 2.2 Fixed Quantity 2: WAC-Based NADAC Changes of 20% or More Since 2024

**Specification**: For `Eliquis`, `Jardiance`, `Farxiga`, `NovoLog`, and `Januvia`, report the date and size of every WAC-based NADAC change (`Primary Reason == "WAC Adjustment"` in `nadac_comparison.csv`) of 20% or more (`|Percent Change| >= 20%`) since 2024.

#### Table 2.2: All WAC-Based NADAC Changes >= 20% Since 2024 for the Five Specified Drugs

| Drug | Effective Date | NADAC Comparison Window (`Start Date` to `End Date`) | Number of NDCs | Old NADAC / Unit ($) | New NADAC / Unit ($) | Exact Percent Change | Notes / NDC Breakdown |
|---|---|---|---:|---:|---:|---:|---|
| **Eliquis** | **`01/01/2026`** | `01/07/2026` to `01/14/2026` | 6 | `$9.66849`–`$9.69551` | `$5.51104`–`$5.52654` | **-43.00%** | `00003-0893-21/31` (2.5 mg): `$9.68961 -> $5.52317`; `00003-0894-21/31/70` (5 mg): `$9.69551 -> $5.52654`; `00003-3764-74` (starter pack): `$9.66849 -> $5.51104` |
| **Jardiance** | **`01/01/2026`** | `12/31/2025` to `01/07/2026` | 6 | `$20.13497`–`$20.13542` | `$11.19625`–`$11.19650` | **-44.39%** | `00597-0152-30/37/90` (10 mg): `$20.13497 -> $11.19625`; `00597-0153-30/37/90` (25 mg): `$20.13542 -> $11.19650` |
| **Farxiga** | **`01/01/2026`** | `01/07/2026` to `01/14/2026` | 5 | `$19.15906`–`$19.17096` | `$12.07003`–`$12.07753` | **-37.00%** | `00310-6205-30/90` (5 mg): `$19.15906 -> $12.07003`; `00310-6210-30/39/90` (10 mg): `$19.17096 -> $12.07753`. *(Authorized generic `Dapagliflozin` `66993-0456/0457-30` had a `-98.38%` / `-98.20%` drop on `06/03/2026` under `Primary Reason == "Help Desk"`, not `WAC Adjustment`.)* |
| **NovoLog** | **`01/01/2024`** | `01/03/2024` to `01/10/2024` | 3 (IPAY 2026) / 5 (incl. Mix 70-30) | `$27.79486`–`$35.79382` | `$6.94871`–`$8.94845` | **-75.00%** (`-75.90%` on Mix 70-30 Vial) | IPAY 2026 NDCs: `00169-7501-11` (Vial): `$27.79486 -> $6.94871` (`-75.00%`); `00169-6339-10` (FlexPen): `$35.79382 -> $8.94845` (`-75.00%`); `00169-3303-12` (PenFill): `$34.36045 -> $8.59011` (`-75.00%`). Non-selected `Novolog Mix 70-30 FlexPen` `00169-3696-19` also fell `-75.00%` and `Mix 70-30 Vial` `00169-3685-12` fell `-75.90%`. **Zero** WAC adjustments for NovoLog in 2025 or 2026. |
| **Fiasp** *(in NovoLog / Fiasp selected family)* | **`01/01/2026`** | `01/07/2026` to `01/14/2026` | 4 | `$27.73069`–`$35.72122` | `$6.93267`–`$8.93031` | **-75.00%** | `00169-3201-11` (Vial): `$27.73069 -> $6.93267`; `00169-3204-15` (FlexTouch): `$35.72122 -> $8.93031`; `00169-3205-15` (PenFill): `$34.40111 -> $8.60028`; `00169-3206-15` (PumpCart): `$34.41057 -> $8.60230` |
| **Januvia** | **`01/01/2025`** | `12/25/2024` to `01/01/2025` | 13 | `$18.32623`–`$18.33402` | `$10.55444`–`$10.55893` | **-42.41%** | `00006-0221-01/28/31/54` (25 mg): `$18.33045 -> $10.55687`; `00006-0112-01/28/31/54` (50 mg): `$18.32623 -> $10.55444`; `00006-0277-01/28/31/54/82` (100 mg): `$18.33402 -> $10.55893`. **Zero** WAC adjustments in 2026. |

---

### 2.3 Fixed Quantity 3: Median NADAC per Unit Divided by 2026 MFP per Unit

**Specification**: For the IPAY 2026 drugs, compute the median NADAC per unit divided by the 2026 MFP per unit (`NDC-9 MFP per Unit Price`, rows with `MFP Effective Date == "01/01/2026"` in `selected_drugs_mfp.csv`), at the last 2025 NADAC snapshot (`As of Date == "12/31/2025"`, 74 unique matched NDC-11s) and the last 2026 NADAC snapshot (`As of Date == "10/21/2026"`, 75 unique matched NDC-11s).

Because different analysts may compute either:
- **Method A (Exact NDC-11 Paired Ratio, Preferred)**: `median_i(NADAC_i / MFP_i)` across matched NDC-11s within each drug family, or
- **Method B (Unpaired Ratio of Medians)**: `median_i(NADAC_i) / median_i(MFP_i)` across matched NDC-11s (or across all MFP rows),
and may either include all matched NDCs or filter to brand-classified NDCs (`Classification for Rate Setting == "B"`), we report all variants in Table 2.3.

#### Table 2.3: NADAC per Unit Divided by 2026 MFP per Unit (`MFP Effective Date == 01/01/2026`) at `12/31/2025` and `10/21/2026`

| Selected Drug | Matched NDCs (`2025` / `2026`) | 2025 `median(NADAC_i / MFP_i)` (Method A, All Matched) | 2026 `median(NADAC_i / MFP_i)` (Method A, All Matched) | 2025 Brand-Only (`Class == B`) | 2026 Brand-Only (`Class == B`) | 2025 Unpaired `med(NADAC) / med(MFP)` (Method B) | 2026 Unpaired `med(NADAC) / med(MFP)` (Method B) | Notes on Formulation & Unit Anomalies |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Eliquis** | 6 / 6 | **2.34x** (`2.3383`) | **1.33x** (`1.3310`) | 2.34x (`2.3383`) | 1.33x (`1.3310`) | 2.34x (`2.3383`) | 1.33x (`1.3310`) | Uniform `$4.149744/EA` MFP across all 6 tablet NDCs |
| **Enbrel** | 4 / 4 | **3.40x** (`3.3964`) | **3.57x** (`3.5683`) | 3.40x (`3.3964`) | 3.57x (`3.5683`) | 3.40x (`3.3964`) | 3.57x (`3.5683`) | Uniform `$573.72125/mL` MFP across all 4 syringe/autoinjector NDCs |
| **Entresto** | 7 / 8 | **2.16x** (`2.1561`) | **2.22x** (`2.2183`) | 2.16x (`2.1561`) | 2.22x (`2.2183`) | 2.16x (`2.1561`) | 2.22x (`2.2183`) | 6 tablet NDCs have `2.218x` in 2026. The 2 `Entresto Sprinkle` NDCs (`00078-1231-20`, `00078-1238-20`) had an expired `01/01/2026` MFP of `$1.229167/EA` (`9.46x` ratio) that CMS replaced on `06/01/2026` (`$5.52–$5.65/EA`, `2.06x–2.11x`; drug median `2.2152x`) |
| **Farxiga** | 7 / 7 (`5` Brand, `2` Auth. Generic) | **3.17x** (`3.1653`) | **1.99x** (`1.9949`) | 3.17x (`3.1672`) | 2.00x (`1.9952`) | 3.17x (`3.1653`) | 1.99x (`1.9949`) | 5 branded `00310` NDCs are at `1.995x` in 2026; 2 authorized generic `66993` NDCs (`Class == G`) dropped from `1.88x` in 2025 to `0.027x–0.030x` (`$0.16–$0.18/EA`) in June 2026 |
| **Imbruvica** | 0 / 0 | **N/A** (Not in NADAC) | **N/A** (Not in NADAC) | N/A | N/A | N/A | N/A | Specialty pharmacy distribution; absent from retail NADAC survey |
| **Januvia** | 13 / 13 | **2.70x** (`2.7008`) | **2.70x** (`2.6986`) | 2.70x (`2.7008`) | 2.70x (`2.6986`) | 2.70x (`2.7008`) | 2.70x (`2.6986`) | Uniform `$3.910212/EA` MFP across all 13 tablet NDCs |
| **Jardiance** | 6 / 6 | **2.96x** (`2.9637`) | **1.65x** (`1.6469`) | 2.96x (`2.9637`) | 1.65x (`1.6469`) | 2.96x (`2.9637`) | 1.65x (`1.6469`) | Uniform `$6.798934/EA` MFP across all 6 tablet NDCs |
| **NovoLog / Fiasp** | 10 / 10 (`7` Brand, `3` Unbranded `73070`) | **2.00x** (`1.9998`) | **1.00x** (`0.9970`) | **3.99x** (`3.9861`) | **1.00x** (`0.9950`) | **1.29x** (`1.2862`) | **1.23x** (`1.2319`) | See detailed breakdown below: Method B erroneously divides cartridge/pen median NADAC (`$8.57–$8.96/mL`) by vial median MFP (`$6.956927/mL`), producing `1.23x` even when exact paired ratios are `1.00x` |
| **Stelara** | 2 / 2 | **3.16x** (`3.1624`) | **3.32x** (`3.3223`) | 3.16x (`3.1624`) | 3.32x (`3.3223`) | 3.16x (`3.1624`) | 3.32x (`3.3223`) | Both SC syringe NDCs (`005` and `006`) have `$4,897.45/mL` MFP and `$16,270.93/mL` NADAC in Oct 2026 (`3.3223x`) |
| **Xarelto** | 19 / 19 (`23` raw before dedup) | **2.78x** (`2.7793`) | **2.84x** (`2.8405`) | 2.78x (`2.7793`) | 2.84x (`2.8405`) | 2.78x (`2.7793`) | 2.84x (`2.8405`) | 4 NDCs (`00558-29`, `00559-28`, `02021-31`, `02022-30`) appear twice in `selected_drugs_mfp.csv` with `01/01/2026` effective dates; deduplication does not change the drug median |
| **Summary: Median across 9 drugs in NADAC** | **9 drugs** | **2.78x** (`2.7793`) | **2.22x** (`2.2183`) | **2.96x** (`2.9637`) | **2.22x** (`2.2183`) | **2.78x** (`2.7793`) | **2.22x** (`2.2183`) | Mean across 9 drugs (Method A): `2.74x` (`2025`) -> `2.18x` (`2026`) |
| **Summary: Pooled median across all matched NDCs** | **74 / 75 NDCs** (`78 / 79` raw) | **2.78x** (`2.7788` dedup / `2.7790` raw) | **2.70x** (`2.6974` dedup / `2.6986` raw) | **2.78x** (`2.7793`) | **2.70x** (`2.6986`) | -- | -- | Pooled NDC median is heavily weighted toward `Xarelto` (`19` NDCs at `2.84x`) and `Januvia` (`13` NDCs at `2.70x`) |

#### Sub-Breakdown of `NovoLog / Fiasp` NDC-Level Ratios (`NADAC_i / MFP_i`):
- **3 Branded NovoLog NDCs (`00169-7501-11` Vial, `00169-6339-10` FlexPen, `00169-3303-12` PenFill)**:
  - `12/31/2025`: `0.9969x`, `0.9999x`, `0.9997x` (median **`1.00x`** [`0.9997x`]).
  - `10/21/2026`: `0.9949x`, `0.9963x`, `0.9947x` (median **`1.00x`** [`0.9949x`]).
- **4 Branded Fiasp NDCs (`00169-3201-11` Vial, `00169-3204-15` FlexTouch, `00169-3205-15` PenFill, `00169-3206-15` PumpCart)**:
  - `12/31/2025`: `3.9861x`, `3.9885x`, `4.0005x`, `4.9462x` (median **`3.99x`** [`3.9945x`]).
  - `10/21/2026`: `0.9950x` (Vial), `0.9985x` (FlexTouch), `0.9977x` (PenFill), and **`1.2326x`** (PumpCart `00169-3206-15`, because CMS assigned PumpCart the Vial MFP of `$6.956927/mL` while Novo Nordisk set its 2026 cartridge NADAC at `$8.57496/mL`).
- **3 Unbranded Biologic `Insulin Aspart` NDCs (`73070-0100-11` Vial, `73070-0102-15` FlexPen, `73070-0103-15` PenFill, `Classification == "G"`)**:
  - Listed on the CMS IPAY 2026 NDC list with MFPs of `$3.478464/mL` (Vial), `$4.479367/mL` (FlexPen), and `$4.296365/mL` (PenFill), which are 50% lower than branded NovoLog MFPs.
  - Because `nadac_2025.csv` and `nadac_2026.csv` assign the generic `INSULIN ASPART` rate (`$6.95395/mL`, `$8.95854/mL`, `$8.56790/mL`) across all `Classification == "G"` insulin aspart NDCs, their ratio to their own NDC-9 MFP is **`2.00x`** (`1.9991x–1.9999x` in 2025, `1.9942x–1.9999x` in 2026).
  - Consequently, across all 10 matched NDCs in `12/31/2025` (3 NovoLog at `1.00x`, 3 Unbranded Insulin Aspart at `2.00x`, 4 Fiasp at `3.99x–4.95x`), the 5th and 6th ordered values are both `2.00x` (`1.9998x`), whereas in `10/21/2026` (6 branded NovoLog/Fiasp at `0.995x–0.998x`, 1 Fiasp PumpCart at `1.23x`, 3 Unbranded at `2.00x`), the median falls to **`1.00x`** (`0.9970x`).
