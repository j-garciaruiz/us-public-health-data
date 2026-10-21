# Part A: Independent Baseline Replication

Generated prior to inspecting any files in `pharma/scripts/`, `pharma/outputs/`, or `pharma/prereg_2027.md`.
Code: [part_a_replicate.py](file:///Users/hari/Documents/VSC%20Python/US%20Data/.claude/worktrees/pharma-data-eae972/reviews/pharma_prereg_agy_argon/part_a_replicate.py) and [test_nadac_partd.py](file:///Users/hari/Documents/VSC%20Python/US%20Data/.claude/worktrees/pharma-data-eae972/reviews/pharma_prereg_agy_argon/test_nadac_partd.py).

---

## 1. The Rule: IPAY 2026 Calibration (2025Q3 SPUF vs 2026 MFP, and 2025 vs 2026 Q1 Part D Spending)

### Methodology Notes
- **MFP per unit (IPAY 2026):** Extracted from `data/raw/pharma/ira/selected_drugs_mfp.csv` for `IPAY == 2026`, excluding superseded rows where `MFP End Date < MFP Effective Date` and using the recalculated unit MFPs effective `2026-06-01` for the two Entresto Sprinkle NDCs (`00078-1231-20` at `$5.521349` and `00078-1238-20` at `$5.648068`; neither Sprinkle NDC appears in `2025Q3` SPUF, so `r` is invariant to this choice). Matching `2025Q3` SPUF (`DAYS_SUPPLY == 30`) on 11-digit `NDC` or 9-digit `NDC-9` yields identical row counts and medians for all 10 drugs.
- **Part D brand pooling (`Mftr_Name == "Overall"`):** Two pooling conventions are shown below because two drugs have additional brand-row variants in `partd_spending_quarterly.csv`:
  1. **All Selected-Drug Brand Rows (Broad, excluding NovoLog Mix and InPen devices):** Pools all Part D brand rows corresponding to the selected drug's NDCs in `selected_drugs_mfp.csv` (`Enbrel` + `Enbrel Mini` + `Enbrel Sureclick` for Enbrel; `Fiasp` + `Fiasp Flextouch` + `Fiasp Penfill` + `Fiasp Pumpcart` + `Novolog` + `Novolog Flexpen` + `Novolog Penfill` for Insulin Aspart).
  2. **Exact `"Selected Drug Name"` Strings:** Pools only exact case-insensitive matches to the semicolon-delimited names in `Selected Drug Name` (`Enbrel` only for Enbrel; omits `Fiasp Pumpcart` for Insulin Aspart).

### Per-Drug Calibration Table (IPAY 2026)

| Selected Drug | 2025Q3 30d Rows ($n$) | Median $r = \text{UNIT\_COST}/\text{MFP}$ | Predicted Change ($1/r - 1$) | 2025 Spend / Claim (Broad / Exact) | 2026 Q1 Spend / Claim (Broad / Exact) | Realized Change (Broad / Exact) | Error: Realized $-$ Predicted (Broad / Exact) | Error: Predicted $-$ Realized (Broad / Exact) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Eliquis; Eliquis Sprinkle | 16,721 | 2.4031 | -58.39% | $912.31 | $399.01 | -56.26% | +2.12 pp | -2.12 pp |
| Enbrel | 23,983 | 3.4385 | -70.92% | $8,681.63 / $8,633.28 | $2,536.74 / $2,541.17 | -70.78% / -70.57% | +0.14 pp / +0.35 pp | -0.14 pp / -0.35 pp |
| Entresto; Entresto Sprinkle | 25,511 | 2.1803 | -54.13% | $1,077.56 | $323.74 | -69.96% | -15.82 pp | +15.82 pp |
| Farxiga | 10,978 | 3.1732 | -68.49% | $997.75 | $328.97 | -67.03% | +1.46 pp | -1.46 pp |
| Imbruvica | 29,665 | 1.7227 | -41.95% | $16,055.46 | $9,646.30 | -39.92% | +2.03 pp | -2.03 pp |
| Januvia | 16,404 | 2.7080 | -63.07% | $556.08 | $214.01 | -61.51% | +1.56 pp | -1.56 pp |
| Jardiance | 11,248 | 2.9669 | -66.29% | $1,091.19 | $386.83 | -64.55% | +1.74 pp | -1.74 pp |
| NovoLog / Fiasp (pooled) | 19,089 | 1.9897 | -49.74% | $293.80 / $293.49 | $204.42 / $204.40 | -30.42% / -30.35% | +19.32 pp / +19.39 pp | -19.32 pp / -19.39 pp |
| Stelara | 13,446 | 3.1204 | -67.95% | $26,682.00 | $8,424.82 | -68.43% | -0.47 pp | +0.47 pp |
| Xarelto | 32,674 | 2.8371 | -64.75% | $1,006.21 | $374.04 | -62.83% | +1.93 pp | -1.93 pp |

### Group-Level Calibration Summary (Fixed 2025 Claim Mix and Unweighted)

- **Fixed 2025 claim mix (group per-claim spending / total group spending change holding each drug's 2025 claim count fixed, i.e., 2025 gross-spending-weighted average of per-drug percentage changes):**
  - **Broad brand pooling:** Predicted = **-62.18%**, Realized = **-61.37%**, Error (Realized $-$ Predicted) = **+0.81 pp** (Predicted $-$ Realized = **-0.81 pp**).
  - **Exact `"Selected Drug Name"` pooling:** Predicted = **-61.73%**, Realized = **-60.88%**, Error (Realized $-$ Predicted) = **+0.85 pp** (Predicted $-$ Realized = **-0.85 pp**).
- **2025 claim-count-weighted average of per-drug percentage changes ($\sum C_{i,2025} \Delta_i / \sum C_{i,2025}$):**
  - **Broad brand pooling:** Predicted = **-61.68%**, Realized = **-60.29%**, Error (Realized $-$ Predicted) = **+1.39 pp**.
  - **Exact `"Selected Drug Name"` pooling:** Predicted = **-61.62%**, Realized = **-60.23%**, Error (Realized $-$ Predicted) = **+1.40 pp**.
- **Unweighted across the 10 drugs:**
  - Mean Predicted = **-60.57%**, Mean Realized = **-59.17%** (Broad) / **-59.14%** (Exact), Mean Error (Realized $-$ Predicted) = **+1.40 pp** (Broad) / **+1.43 pp** (Exact).
  - Mean Absolute Error (MAE) = **4.66 pp** (Broad) / **4.69 pp** (Exact); Median Absolute Error = **1.83 pp**; on the 8 drugs excluding Entresto (generic entry in mid-2025) and NovoLog/Fiasp (75% NovoLog WAC cut in Jan 2024 vs Fiasp in Jan 2026 plus package/formulary mix shift), errors range from **-0.47 pp to +2.12 pp** (MAE **1.43 pp** Broad / **1.46 pp** Exact).

---

## 2. The 2027 Cohort: IPAY 2027 Predictions (2026Q3 SPUF vs 2027 MFP, and 2026 Q1 Part D Spending)

### Per-Drug Prediction Table (IPAY 2027)

Note: For 14 of the 15 drugs, Broad and Exact Part D brand matching are identical. For `AUSTEDO; AUSTEDO XR`, Exact matches `Austedo` and `Austedo XR` (`73,461` claims, `$626,969,414` spending, `$8,534.72`/claim in 2026 Q1), whereas Broad also includes `Austedo XR Titration Kt(Wk1-4)` (`545` claims, `$4,026,402` spending; pooled `74,006` claims, `$630,995,816` spending, `$8,526.28`/claim). Both are reported below.

| Selected Drug | 2026 MFP ($30\text{d}$) | 2026Q3 30d Rows ($n$) | Median $r = \text{UNIT\_COST}/\text{MFP}$ | Predicted Change ($1/r - 1$) | 2026 Q1 Claims | 2026 Q1 Spend / Claim | 2026 Q1 Gross Spending ($M) | Gross Spending Removed at 2026 Q1 Volume, 1 Qtr ($M) | Gross Spending Removed Annualized $\times 4$ ($M) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Austedo; Austedo XR (Exact) | $4,093 | 50,856 | 1.6839 | -40.61% | 73,461 | $8,534.72 | $626.97 | $254.64 | $1,018.55 |
| Austedo; Austedo XR (Broad) | $4,093 | 50,856 | 1.6839 | -40.61% | 74,006 | $8,526.28 | $631.00 | $256.27 | $1,025.09 |
| Breo Ellipta | $67 | 16,120 | 5.6853 | -82.41% | 477,136 | $535.26 | $255.39 | $210.47 | $841.89 |
| Calquence | $8,600 | 5,496 | 1.6744 | -40.28% | 49,197 | $14,579.45 | $717.27 | $288.89 | $1,155.56 |
| Ibrance | $7,871 | 21,984 | 2.0152 | -50.38% | 43,602 | $15,771.60 | $687.67 | $346.42 | $1,385.69 |
| Janumet; Janumet XR | $80 | 23,252 | 3.6263 | -72.42% | 230,272 | $563.37 | $129.73 | $93.96 | $375.82 |
| Linzess | $136 | 16,488 | 1.9860 | -49.65% | 670,465 | $429.99 | $288.29 | $143.13 | $572.52 |
| Ofev | $6,350 | 3,918 | 2.1255 | -52.95% | 51,721 | $13,550.66 | $700.85 | $371.11 | $1,484.45 |
| Otezla; Otezla XR | $1,650 | 18,970 | 3.2391 | -69.13% | 62,840 | $5,485.21 | $344.69 | $238.27 | $953.09 |
| Ozempic; Rybelsus; Wegovy | $274 | 33,030 | 3.6289 | -72.44% | 3,358,770 | $1,417.51 | $4,761.09 | $3,449.09 | $13,796.36 |
| Pomalyst | $8,650 | 9,508 | 2.7011 | -62.98% | 21,372 | $23,154.12 | $494.85 | $311.65 | $1,246.59 |
| Tradjenta | $78 | 5,018 | 6.0155 | -83.38% | 292,530 | $806.04 | $235.79 | $196.59 | $786.38 |
| Trelegy Ellipta | $175 | 10,877 | 3.8102 | -73.75% | 1,656,431 | $932.09 | $1,543.94 | $1,138.73 | $4,554.91 |
| Vraylar | $770 | 32,976 | 1.9384 | -48.41% | 210,833 | $1,559.86 | $328.87 | $159.21 | $636.85 |
| Xifaxan | $1,000 | 8,565 | 3.2534 | -69.26% | 111,610 | $3,030.69 | $338.26 | $234.29 | $937.14 |
| Xtandi | $7,004 | 16,488 | 1.9772 | -49.42% | 90,089 | $13,812.71 | $1,244.37 | $615.02 | $2,460.09 |

### Cohort-Level Totals (IPAY 2027)
- **2026 Q1 baseline volume and spending:**
  - **Exact brand match:** `7,400,329` claims; `$12,698,030,980.11` (`$12.698B`) gross spending; `$1,715.87` group spending per claim.
  - **Broad brand match:** `7,400,874` claims; `$12,702,057,381.95` (`$12.702B`) gross spending; `$1,716.29` group spending per claim.
- **Group change at fixed 2026 Q1 claim mix:**
  - **Group per-claim spending / total gross spending change holding 2026 Q1 claim counts fixed (spending-weighted average of per-drug predicted changes):**
    - **Exact:** **-63.41%** (group per-claim spending drops from `$1,715.87` to `$627.88`).
    - **Broad:** **-63.40%** (group per-claim spending drops from `$1,716.29` to `$628.16`).
  - **2026 Q1 claim-count-weighted average of per-drug predicted percentage changes ($\sum C_{i,2026\text{Q1}} \Delta_i / \sum C_{i,2026\text{Q1}}$):** **-69.88%** (both Exact and Broad).
  - **Unweighted mean / median across 15 drugs:** **-61.17%** / **-62.98%**.
- **Gross spending removed at 2026 Q1 volumes:**
  - **Single-quarter (2026 Q1 volume):** **`$8,051,478,384.89`** (`$8.051B`, Exact) / **`$8,053,113,653.13`** (`$8.053B`, Broad).
  - **Annualized ($\times 4$):** **`$32,205,913,539.56`** (`$32.206B`, Exact) / **`$32,212,454,612.51`** (`$32.212B`, Broad).

---

## 3. NADAC Analysis (`nadac_2026.csv` and `nadac_comparison.csv`)

### 3a. Latest Snapshot (`As of Date = 10/21/2026`) for IPAY 2027 Drugs (Brand-Classified `B` NDCs)
Nine of the 15 IPAY 2027 drugs have brand-classified (`Classification for Rate Setting == "B"`) NDCs in the latest `nadac_2026.csv` snapshot (`10/21/2026`); the other six (Calquence, Ibrance, Ofev, Pomalyst, Xifaxan, Xtandi) have no NDCs in `nadac_2026.csv`.

| IPAY 2027 Drug | Brand (`B`) NDCs in NADAC ($n$) | Median $\text{NADAC} / \text{2027 MFP}$ | Implied Discount ($1 - \text{MFP}/\text{NADAC}$) | Notes |
|---|---:|---:|---:|---|
| Austedo; Austedo XR | 12 | 1.6575 | -39.67% | Range 1.6531 to 1.6661 (`NDC-9` match adds 1 row, median 1.6573) |
| Breo Ellipta | 5 | 5.6501 | -82.30% | 5 `B` NDCs (range 4.6663 to 5.6689); also 2 `G` NDCs (`66993-*`, ratios 5.4399, 5.5350; all 7 median = 5.5350) |
| Calquence | 0 | N/A | N/A | Absent from NADAC (specialty distribution) |
| Ibrance | 0 | N/A | N/A | Absent from NADAC (specialty distribution) |
| Janumet; Janumet XR | 15 | 3.6354 | -72.49% | Range 3.6339 to 3.6386 |
| Linzess | 3 | 1.9810 | -49.52% | Ratios 1.9801, 1.9810, 1.9820 (post Jan 2026 -50.3% WAC cut) |
| Ofev | 0 | N/A | N/A | Absent from NADAC (brand; generic nintedanib `G` NDCs exist outside selected NDC list) |
| Otezla; Otezla XR | 4 | 3.1707 | -68.46% | Ratios 3.1043, 3.1705, 3.1709, 3.1768 |
| Ozempic; Rybelsus; Wegovy | 22 | 3.5954 | -72.19% | 12 Ozempic/Rybelsus NDCs around 3.5973-3.5999 (median 3.5979); 10 Wegovy NDCs around 3.3812-3.3885 (median 3.3866) |
| Pomalyst | 0 | N/A | N/A | Absent from NADAC (specialty distribution) |
| Tradjenta | 3 | 6.0095 | -83.36% | All 3 NDCs = 6.0095 |
| Trelegy Ellipta | 4 | 3.8049 | -73.72% | Range 3.7842 to 3.8215 |
| Vraylar | 10 | 1.8836 | -46.91% | Range 1.8811 to 1.8847 |
| Xifaxan | 0 | N/A | N/A | Absent from NADAC |
| Xtandi | 0 | N/A | N/A | Absent from NADAC (specialty distribution) |

### 3b. WAC-Based Cuts of 20% or More on IPAY 2027 NDCs Since 2024 (`nadac_comparison.csv`)
Across all IPAY 2027 selected NDCs in `nadac_comparison.csv` since `2024-01-01`, exactly **two IPAY 2027 drugs** had WAC-based cuts (`Primary Reason == "WAC Adjustment"`) of 20% or more:
1. **Janumet; Janumet XR:** **-42.41%** across all 15 brand (`B`) NDCs, effective **2025-01-01** (e.g., Janumet 50-1000 mg NADAC per unit fell from `$9.17020` to `$5.28130`; Janumet XR 100-1000 mg fell from `$18.32966` to `$10.55642`).
2. **Linzess:** **-50.26% to -50.27%** across all 3 brand (`B`) NDCs (`00456-1201-30`, `00456-1202-30`, `00456-1203-30`), effective **2026-01-01** (NADAC per unit fell from `$18.13941-$18.15250` to `$9.02163-$9.02815`).

*(Note on IPAY 2026 and 2028 NDCs in `nadac_comparison.csv` since 2024: Among IPAY 2026 drugs, brand WAC cuts $\ge 20\%$ occurred for **NovoLog** on `2024-01-01` [-75.00% on 3 `B` NDCs, plus -50.00% `Help Desk` on 3 `G` insulin aspart NDCs], **Januvia** on `2025-01-01` [-42.41% on 13 `B` NDCs], **Eliquis** on `2026-01-01` [-43.00% on 6 `B` NDCs], **Farxiga** on `2026-01-01` [-37.00% on 5 `B` NDCs, plus -98.20% to -98.38% `Help Desk` on 2 `G` dapagliflozin NDCs on `2026-06-03`], **Jardiance** on `2026-01-01` [-44.39% on 6 `B` NDCs], and **Fiasp** on `2026-01-01` [-75.00% on 4 `B` NDCs]. That is 4 of 10 IPAY 2026 drugs with WAC cuts between `2025-12-20` and `2026-02-28` [Eliquis, Farxiga, Jardiance, and Fiasp within the NovoLog/Fiasp selected drug], and 5 of 10 IPAY 2026 drugs since 2024 [adding Januvia in Jan 2025 and NovoLog in Jan 2024]. Among IPAY 2028 drugs, 1 `B` NDC of **Xeljanz** [`00069-1001-01`] had a -25.00% WAC Adjustment on `2026-01-01`.)*

### 3c. Four Deselected IPAY 2026 Drugs (MFP Ends `2026-12-31`): $\text{NADAC} / \text{2026 MFP}$ (`10/21/2026` Snapshot)

| Deselected IPAY 2026 Drug / Sub-Brand | Brand (`B`) NDCs ($n$) | Median $\text{NADAC} / \text{2026 MFP}$ (Brand `B`) | Range Across `B` NDCs | Notes on Alternative Subsets |
|---|---:|---:|---|---|
| **Entresto; Entresto Sprinkle** | 8 | **2.2152** | 2.0549 to 2.2187 | 6 tablet NDCs (`00078-0659/0696/0777`): median **2.2180** (2.2125-2.2187); 2 Sprinkle NDCs (`00078-1231/1238` vs 2026-06-01 MFP): **2.1054** and **2.0549** |
| **Stelara** | 2 | **3.3223** | 3.3176 to 3.3269 | `57894-0060-03` (45 mg/0.5 mL): **3.3269**; `57894-0061-03` (90 mg/mL): **3.3176** |
| **Xarelto** | 19 | **2.8405** | 2.8304 to 2.8441 | Oral suspension (`50458-0575-01`): 2.8304; 18 tablet NDCs: 2.8397 to 2.8441 |
| **NovoLog** (separately) | 3 | **0.9965** | 0.9950 to 0.9974 | PenFill (`00169-3303-12`): 0.9950; Vial (`00169-7501-11`): 0.9965; FlexPen (`00169-6339-10`): 0.9974. (3 `73070-*` `G` unbranded insulin aspart NDCs have ratios 1.9896, 1.9994, 2.0008) |
| **Fiasp** (separately) | 4 | **0.9948** | 0.9913 to 1.2326 | Vial (`00169-3201-11`): 0.9948; FlexTouch (`00169-3204-15`): 0.9949; PenFill (`00169-3205-15`): 0.9913; PumpCart (`00169-3206-15`): 1.2326. (Excluding PumpCart, $n=3$ median is also **0.9948**) |
| *NovoLog + Fiasp (pooled)* | *7* | *0.9950* | *0.9913 to 1.2326* | *Including the 3 `73070-*` `G` NDCs ($n=10$), median is **0.9970*** |

---

## 4. The Six Continuing IPAY 2026 Drugs: 2027 MFP vs 2026 MFP

| Continuing IPAY 2026 Drug | 2026 Single MFP per 30 DES | 2027 Single MFP per 30 DES | Dollar Change ($/30\text{d}$) | 30-Day MFP % Change | Per-Unit MFP % Change (Median Across NDCs) |
|---|---:|---:|---:|---:|---:|
| Eliquis; Eliquis Sprinkle | $231.00 | $237.25 | +$6.25 | +2.7056% (+2.71%) | +2.7049% |
| Enbrel | $2,355.00 | $2,418.70 | +$63.70 | +2.7049% (+2.70%) | +2.7049% |
| Farxiga | $178.50 | $183.33 | +$4.83 | +2.7059% (+2.71%) | +2.7049% |
| Imbruvica | $9,319.00 | $9,571.07 | +$252.07 | +2.7049% (+2.70%) | +2.7049% |
| Januvia | $113.00 | $116.06 | +$3.06 | +2.7080% (+2.71%) | +2.7049% |
| Jardiance | $197.00 | $202.33 | +$5.33 | +2.7056% (+2.71%) | +2.7049% |
