PASS WITH FIXES

Independent methods review and blind recomputation of the CMS National Average Drug Acquisition Cost (NADAC) starter pull and `pharma/README.md` catalog, conducted on 2026-10-20 using `.venv/bin/python` (`reviews/pharma_agy_argon/recompute.py` and `reviews/pharma_agy_argon/methods_checks.py`). Part 1 was executed and saved to `reviews/pharma_agy_argon/recompute.md` before opening `pharma/outputs/`, `pharma/scripts/`, `reviews/pharma_codex_astra/`, or the "Starter dataset" section of `pharma/README.md`.

---

## Part 1: Independent Recompute Numbers

### 1. SHA-256 and Provenance Verification

Both raw NADAC CSV files match their `.meta.json` sidecar SHA-256 digests, byte sizes, and data row counts exactly:

| File | Sidecar SHA-256 | Recomputed SHA-256 | Match | Bytes | Data Rows |
|---|---|---|---|---:|---:|
| `nadac_2025.csv` | `317c0387d2005b18ade760029bf61b3ff5a3aab74ef96e322d319432c410ed80` | `317c0387d2005b18ade760029bf61b3ff5a3aab74ef96e322d319432c410ed80` | PASS | 139,475,442 | 1,608,416 |
| `nadac_2026.csv` | `62205340628b7e313534c22e963a9f5e47495c621f9c115180f761b2256ceed8` | `62205340628b7e313534c22e963a9f5e47495c621f9c115180f761b2256ceed8` | PASS | 109,956,674 | 1,268,309 |

### 2. 2026 Dataset Structure Metrics

| Metric | Independent Recompute |
|---|---|
| Total data rows (excluding header) | `1,268,309` |
| Weekly snapshots (`As of Date`) | `42` |
| First 2026 snapshot | `2026-01-07` (`01/07/2026`) |
| Latest 2026 snapshot | `2026-10-21` (`10/21/2026`) |
| Distinct 11-digit NDCs in 2026 | `32,972` |
| NDCs per snapshot (min / median / max) | `29,918` / `30,168.5` / `30,597` |
| NDCs not 11 digits (string check) | `0` rows (`0` distinct NDCs; `239,123` rows have a leading zero) |
| Duplicate `(As of Date, NDC)` rows | `0` |

### 3. Latest 2026 Snapshot (`2026-10-21`): Median NADAC Per Unit (`Pricing Unit == "EA"`)

- **Generics (`Classification for Rate Setting == "G"`, `Pricing Unit == "EA"`):** **`$0.14096`** (`22,874` NDCs; p10 `$0.03364`, p90 `$1.92417`, mean `$2.14124`).
- **Brands (`Classification for Rate Setting == "B"`, `Pricing Unit == "EA"`):** **`$12.67003`** (`1,667` NDCs; p10 `$2.09407`, p90 `$94.71786`, mean `$115.87285`).
- *(Additional brand-related rate classifications with `Pricing Unit == "EA"` in `2026-10-21`: `B-ANDA` has `70` NDCs with median `$1.73830`; `B-BIO` has `6` NDCs with median `$499.25158`. Pooling `B`, `B-ANDA`, and `B-BIO` yields `1,743` NDCs with median `$12.14492`.)*

### 4. 2026 Monthly Survey Refreshes (>50% of Common NDCs with Preceding Snapshot Have New `Effective Date`)

All **10** monthly survey refreshes in 2026 (one per month, January through October):

| # | Snapshot (`YYYY-MM-DD`) | Raw `As of Date` | Preceding Snapshot | Common NDCs | New `Effective Date` | % Changed |
|---:|---|---|---|---:|---:|---:|
| 1 | `2026-01-21` | `01/21/2026` | `2026-01-14` | 30,421 | 28,227 | 92.79% |
| 2 | `2026-02-18` | `02/18/2026` | `2026-02-11` | 30,449 | 28,464 | 93.48% |
| 3 | `2026-03-18` | `03/18/2026` | `2026-03-11` | 30,050 | 28,176 | 93.76% |
| 4 | `2026-04-22` | `04/22/2026` | `2026-04-15` | 30,167 | 28,349 | 93.97% |
| 5 | `2026-05-20` | `05/20/2026` | `2026-05-13` | 30,228 | 29,197 | 96.59% |
| 6 | `2026-06-17` | `06/17/2026` | `2026-06-10` | 29,972 | 28,936 | 96.54% |
| 7 | `2026-07-22` | `07/22/2026` | `2026-07-15` | 30,083 | 29,037 | 96.52% |
| 8 | `2026-08-19` | `08/19/2026` | `2026-08-12` | 30,239 | 29,226 | 96.65% |
| 9 | `2026-09-23` | `09/23/2026` | `2026-09-16` | 29,892 | 28,926 | 96.77% |
| 10 | `2026-10-21` | `10/21/2026` | `2026-10-14` | 29,992 | 29,138 | 97.15% |

### 5. Tracer Medians at First 2025 Snapshot (`2025-01-01`) and Latest 2026 Snapshot (`2026-10-21`)

| Exact `NDC Description` | NDCs (`2025-01-01`) | Median (`2025-01-01`) | NDCs (`2026-10-21`) | Median (`2026-10-21`) | Change ($/unit) | % Change |
|---|---:|---:|---:|---:|---:|---:|
| `ATORVASTATIN 20 MG TABLET` | 57 | `$0.03166` | 69 | `$0.02858` | `-$0.00308` | `-9.73%` |
| `METFORMIN HCL 500 MG TABLET` | 53 | `$0.01304` | 57 | `$0.01483` | `+$0.00179` | `+13.73%` |
| `ELIQUIS 5 MG TABLET` | 3 | `$9.51063` | 3 | `$5.52144` | `-$3.98919` | `-41.94%` |
| `JARDIANCE 10 MG TABLET` | 3 | `$19.54698` | 3 | `$11.18898` | `-$8.35800` | `-42.76%` |
| `JANUVIA 100 MG TABLET` | 5 | `$10.55893` | 5 | `$10.55001` | `-$0.00892` | `-0.08%` |
| `XARELTO 20 MG TABLET` | 5 | `$18.20331` | 5 | `$19.53935` | `+$1.33604` | `+7.34%` |

### 6. Snapshot and Size of Median Drop for `ELIQUIS 5 MG TABLET` and `JARDIANCE 10 MG TABLET`

- **`ELIQUIS 5 MG TABLET`** (`NDC`s `00003089421`, `00003089431`, `00003089470`):
  - **Snapshot of drop:** **`2026-01-14`** (`01/14/2026`), with `Effective Date = 01/01/2026` and `Explanation Code = 3`.
  - **Size of weekly step drop (`2026-01-07` to `2026-01-14`):** From `$9.69551` to `$5.52654`, a drop of **`$4.16897` per tablet (`-43.00%`, exact `-42.9990%`)**.
  - **Net change (`2025-01-01` to `2026-10-21`):** From `$9.51063` to `$5.52144`, a drop of **`$3.98919` per tablet (`-41.94%`)** (reflecting a `+2.00%` WAC increase on `2025-01-08` from `$9.51063` to `$9.70084` before the `-43.00%` cut on `2026-01-14`).
- **`JARDIANCE 10 MG TABLET`** (`NDC`s `00597015230`, `00597015237`, `00597015290`):
  - **Snapshot of drop:** **`2026-01-07`** (`01/07/2026`, the first snapshot of 2026 compared against `2025-12-31`), with `Effective Date = 01/01/2026` and `Explanation Code = 3`.
  - **Size of weekly step drop (`2025-12-31` to `2026-01-07`):** From `$20.13497` to `$11.19625`, a drop of **`$8.93872` per tablet (`-44.39%`, exact `-44.3940%`)**.
  - **Net change (`2025-01-01` to `2026-10-21`):** From `$19.54698` to `$11.18898`, a drop of **`$8.35800` per tablet (`-42.76%`)** (reflecting a `+3.00%` WAC increase on `2025-01-08` from `$19.54698` to `$20.13339` before the `-44.39%` cut on `2026-01-07`).

---

## Part 3: Comparison Against `pharma/outputs/nadac_sanity.md` and `pharma/outputs/nadac_tracers.csv`

- **`pharma/outputs/nadac_tracers.csv` (`1,152` data rows across 13 tracers):** **Zero disagreements.** Every row matches our independent recompute on `(NDC Description, as_of)`, `ndcs`, `unit`, `cls`, and `median_nadac` (maximum absolute floating-point difference `2.22e-16` on two midpoint medians for `ALBUTEROL HFA 90 MCG INHALER`).
- **`pharma/outputs/nadac_sanity.md`:** **Zero numerical disagreements beyond display rounding (`floatfmt="{:,.5g}"` and `+.1%`).** All structure checks, class/unit counts and quantiles (`p10`, `median`, `p90`), week-over-week movement counts (`2026-10-14` to `2026-10-21`), and tracer endpoint medians agree with our recompute after accounting for the 5-significant-digit formatting in `summarize_nadac.py` (which prints `$12.67003` as `12.67`, `$19.54698` as `19.547`, `$10.55893` as `10.559`, and `$10.55001` as `10.55`).
- **Presentation and baseline caveats in `nadac_sanity.md` (covered in Findings 3 and 10 below):**
  1. The tracer table starts at `2025-01-01`, which is the exact snapshot where `JANUVIA 100 MG TABLET` dropped `-42.41%` (`$18.33402` on `2024-12-25` to `$10.55893` on `2025-01-01`), making Januvia appear flat (`-0.1%`) over 2025–2026.
  2. The tracer table shows only `NDCs (latest)`, concealing that active NDC counts changed between `2025-01-01` and `2026-10-21` (e.g., `ATORVASTATIN 20 MG TABLET` `57 -> 69`, `METFORMIN HCL 500 MG TABLET` `53 -> 57`, `ALBUTEROL HFA 90 MCG INHALER` `10 -> 12`, `SITAGLIPTIN PHOSPHATE 100 MG TABLET` `0 -> 8` starting `2026-08-05`).

---

## Part 2: Ranked Methods Findings (10 Findings)

### 1. [High] NADAC's hybrid rate-setting method (survey vs brand WAC indexing) is omitted, and the cause of the Eliquis and Jardiance drops is already recorded in `Explanation Code` and `NADAC Comparison`

- **Issue:** `pharma/README.md:114` describes NADAC simply as "what pharmacies actually pay on invoice, survey-based", `pharma/README.md:116` says "The monthly survey refresh moves most rates at once ... other weeks change few rates", and `pharma/README.md:131` states regarding the January 2026 Eliquis (`-43%`) and Jardiance (`-44%`) drops that "the cause is not established here (manufacturer list-price cuts are the obvious candidate to check against WAC data)."
  Under CMS's official NADAC methodology, NADAC is a **hybrid of monthly invoice surveys and weekly brand WAC indexing**:
  1. **Generics (`G` / MDRP `N`):** Calculated monthly from a **3-month moving average** of retail community pharmacy invoice surveys (`Explanation Code = 1`) and never adjusted for WAC changes (`0` generic `WAC Adjustment`s in `NADAC Comparison`).
  2. **Brands (`B`, `B-ANDA`, `B-BIO` / MDRP `S` or `I`):** Monitored weekly against national pricing compendia. Whenever a brand's published Wholesale Acquisition Cost (`WAC`) changes by `±2%` or more, CMS mechanically adjusts the existing NADAC by the **exact percentage change in WAC**, assigns `Explanation Code = 3` in the weekly NADAC file, and logs `Primary Reason = "WAC Adjustment"` in `NADAC Comparison`. Furthermore, during subsequent monthly survey refreshes, if the newly surveyed brand acquisition cost is within `±2%` of the existing NADAC, CMS **carries forward the existing rate and `Effective Date` unchanged (`Explanation Code = 2`, which appears on `12,209` brand rows and `0` generic rows in 2026)**.
  3. Across all 32 non-refresh weekly files of 2026, `NADAC Comparison` contains **`0` `Survey Rate` changes**; `1,020` of the `1,080` non-refresh changes (`94.4%`, all class `B`) are `WAC Adjustment`s, and the remaining `60` (`41` `Help Desk`, `19` `Rate Group Change`) are administrative revisions.
  4. Both the `2026-01-14` `ELIQUIS 5 MG TABLET` drop (`$9.69551` to `$5.52654`, `-43.00%`, `Effective Date = 01/01/2026`) and the `2026-01-07` `JARDIANCE 10 MG TABLET` drop (`$20.13497` to `$11.19625`, `-44.39%`, `Effective Date = 01/01/2026`) carry `Explanation Code = 3` in `nadac_2026.csv` and `Primary Reason = "WAC Adjustment"` in `nadac_comparison.csv`, and were carried forward for four consecutive monthly survey refreshes (`Jan–Apr 2026`) under `Explanation Code`s `2` and `4` before receiving their first post-cut survey update (`Code 1`) on `2026-05-20` (`-0.05%` and `-0.01%`).
- **Fix:** In `pharma/README.md` ("List vs net price", "NADAC specifics", and Starter Project 2) and `pharma/outputs/nadac_sanity.md`, explain the dual rate-setting rule (generic 3-month moving-average survey vs brand `±2%` survey carryover `Code 2` and weekly `WAC Adjustment` `Code 3`), and state explicitly that `Explanation Code = 3` and `NADAC Comparison` (`Primary Reason = "WAC Adjustment"`) establish that the Eliquis (`-43.00%`) and Jardiance (`-44.39%`) drops were mechanical WAC adjustments effective `2026-01-01`, not observed January survey invoice drops.
- **Primary sources:** [CMS Retail Price Survey and NADAC Methodology](https://www.medicaid.gov/medicaid/prescription-drugs/retail-price-survey), [CMS NADAC Q&A (`nadacqa.pdf`)](https://www.medicaid.gov/medicaid-chip-program-information/by-topics/prescription-drugs/ful-nadac-downloads/nadacqa.pdf), [NADAC 2026 Dataset (`fbb83258-11c7-47f5-8b18-5f8e79f7e704`)](https://data.medicaid.gov/dataset/fbb83258-11c7-47f5-8b18-5f8e79f7e704), [NADAC Comparison Dataset (`a217613c-12bc-5137-8b3a-ada0e4dad1ff`)](https://data.medicaid.gov/dataset/a217613c-12bc-5137-8b3a-ada0e4dad1ff).

### 2. [High] "Unweighted median NADAC across NDCs sharing an `NDC Description`" is either redundant (within a single CMS rate group) or distorted by NDC entry/exit across package-size rate groups (`Explanation Code = 5`)

- **Issue:** `summarize_nadac.py` and `nadac_sanity.md` track drugs using the unweighted median across all 11-digit NDCs sharing an exact `NDC Description` ("Medians across all NDCs (labelers, package sizes) carrying the exact description").
  1. **Zero within-group variance for 87.2% of multi-NDC descriptions:** CMS does not calculate independent NADACs per 11-digit NDC; it pools survey invoices across all NDCs in a **rate group** (active ingredient, strength, dosage form, route, `S/I` vs `N` category, OTC status, and package size only when `Explanation Code = 5` applies) and assigns the identical rate to every active NDC in that group. In the `2026-10-21` snapshot, `3,186` of `3,652` multi-NDC `NDC Description`s (`87.24%`) have only **1 unique `NADAC Per Unit`** across all their NDCs (`min == median == max`). Across all 95 snapshots of 2025–2026 (`1,152` tracer-week cells), **12 of the 13 tracers have `min == median == max` in every snapshot** (e.g., all 69 NDCs of `ATORVASTATIN 20 MG TABLET` equal `$0.02858`; all 57 NDCs of `METFORMIN HCL 500 MG TABLET` equal `$0.01483`).
  2. **Composition jumps where `Explanation Code = 5` splits a description by package size:** The sole tracer with `>1` unique rate, `ALBUTEROL HFA 90 MCG INHALER` (priced per `GM` with `Explanation Code = 5`), combines three distinct package-size rate groups for 200-actuation inhalers: `8.5 g` ProAir-equivalent generics (`$1.52204/g` on `2026-10-21`, or `$12.94/inhaler`), `6.7 g` Proventil-equivalent generics (`$1.83196/g`, or `$12.27/inhaler`), and `18 g`/`8 g` Ventolin-equivalent generics (`$2.08079/g`, or `$37.45` per `18 g` inhaler). Because the unweighted median simply picks the middle NDC across 10–12 NDCs:
     - On **`2025-11-26`** (`n=11 -> 10`), one `18 g` NDC exited the file and the reported tracer median dropped **`-6.64%` (`$2.24216` to `$2.09323/g`)** while all 10 continuing NDCs had a **`0.00000` price change**.
     - On **`2026-04-29`** (`n=10 -> 11`), one new `8.5 g` NDC (`69238129101` at `$1.70516/g`) entered the file and the reported tracer median dropped **`-7.87%` (`$1.97645` to `$1.82100/g`)** in a non-refresh week while all 10 continuing NDCs had a **`0.00000` price change**.
  3. **Exact string matching splits clinical drugs:** Matching on exact `NDC Description` misses generic entry under the nonproprietary name (e.g., `JANUVIA 100 MG TABLET` vs `SITAGLIPTIN PHOSPHATE 100 MG TABLET`; `LANTUS SOLOSTAR 100 UNIT/ML` vs `INSULIN GLARGINE-YFGN U100 PEN` and `REZVOGLAR`), and remains vulnerable to repackager/carry-forward (`Explanation Code = 4`) NDCs if a description has only 3 primary NDCs (as with Eliquis 5 mg and Jardiance 10 mg).
- **Fix:** Document in `pharma/README.md` that NADAC is a rate-group price, and upgrade the tracer method in three tiers: (1) **Utilization-weighted average NADAC** by joining 11-digit `NDC`s to quarterly Medicaid `SDUD` (`state == "XX"` national `units_reimbursed`) across all NDCs sharing an RxNorm clinical drug (`RxCUI`), (2) **Package-normalized rate-group series** (multiplying `GM`/`ML` rates by FDA NDC package size so `6.7 g`, `8.5 g`, and `18 g` inhalers and `3 mL` pens are compared per inhaler/pen or per Defined Daily Dose, and tracking each package-size rate group separately rather than taking an unweighted median across `Explanation Code = 5` subgroups), and (3) **Balanced per-NDC panels** to isolate rate changes from NDC turnover.
- **Primary sources:** [CMS Retail Price Survey Methodology](https://www.medicaid.gov/medicaid/prescription-drugs/retail-price-survey), [Medicaid State Drug Utilization Data (SDUD)](https://www.medicaid.gov/medicaid/prescription-drugs/state-drug-utilization-data), [FDA NDC Directory](https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-directory), [RxNorm API](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html).

### 3. [High] Starting the tracer window on `2025-01-01` misses Januvia's `-42.41%` WAC cut by one week (`2024-12-25` to `2025-01-01`), and `pharma/README.md` omits `Corresponding Generic Drug NADAC Per Unit`

- **Issue:** `pharma/outputs/nadac_sanity.md` reports `JANUVIA 100 MG TABLET` as flat from `2025-01-01` (`$10.559`) to `2026-10-21` (`$10.55`, `-0.1%`), and `pharma/README.md:131` contrasts Eliquis (`-43%`) and Jardiance (`-44%`) against Januvia and Xarelto. However, `data/raw/pharma/nadac/nadac_2024.csv` and `nadac_comparison.csv` show that `JANUVIA 100 MG TABLET` (along with Januvia 25 mg and 50 mg) experienced an almost identical **`-42.41%` `WAC Adjustment` in the `2025-01-01` snapshot (`$18.33402` on `2024-12-25` to `$10.55893` on `2025-01-01`, `Effective Date = 01/01/2025`, `Explanation Code = 3`, `Primary Reason = "WAC Adjustment"`)** when Merck cut Januvia's WAC one year ahead of IPAY 2026 (just as Novo Nordisk cut `NOVOLOG` WAC by `-75.00%` effective `2024-01-01` while cutting `FIASP` WAC by `-75.00%` effective `2026-01-01`).
  Furthermore, on **`2026-08-05`**, 8 generic `SITAGLIPTIN PHOSPHATE 100 MG TABLET` NDCs entered NADAC at `$3.77084/EA` (`$3.84929/EA` on `2026-10-21`, 63.5% below Januvia's `$10.55001`), which populated the **`Corresponding Generic Drug NADAC Per Unit`** column on `JANUVIA 100 MG TABLET` (`43,354` rows in `nadac_2026.csv` carry a corresponding generic NADAC). `pharma/README.md` never mentions the `Corresponding Generic Drug NADAC Per Unit` column, which state Medicaid programs use to cap reimbursement on multi-source brands (`I`) at the generic rate.
- **Fix:** Include `nadac_2024.csv` (specifically `2024-12-25`) as the pre-2025 baseline in `summarize_nadac.py` and Starter Project 2 so Januvia's `-42.41%` WAC cut (`$18.33402 -> $10.55893`) is captured rather than hidden in the `2025-01-01` starting value, and document `Corresponding Generic Drug NADAC Per Unit` (and generic sitagliptin's `2026-08-05` entry) in `pharma/README.md`.
- **Primary sources:** [NADAC 2024 Dataset (`99315a95-37ac-4eee-946a-3c523b4c481e`)](https://data.medicaid.gov/dataset/99315a95-37ac-4eee-946a-3c523b4c481e), [NADAC 2025 Dataset (`f38d0706-1239-442c-a3cc-40ef1b686ac0`)](https://data.medicaid.gov/dataset/f38d0706-1239-442c-a3cc-40ef1b686ac0), [NADAC Comparison Dataset (`a217613c-12bc-5137-8b3a-ada0e4dad1ff`)](https://data.medicaid.gov/dataset/a217613c-12bc-5137-8b3a-ada0e4dad1ff).

### 4. [High] The IRA MFP discussion (`pharma/README.md:114, 131`) does not separate cross-payer WAC cuts from Part D-only MFP effectuation, omits that post-cut 2026 NADACs for Eliquis and Jardiance remain 33% to 65% above their unit MFPs, and overlooks that Imbruvica has `0` NADAC rows

- **Issue:** `pharma/README.md:114` notes that where MFP is effectuated as a retrospective refund, "the invoice price, and therefore NADAC, can stay well above the MFP", and Starter Project 2 (`pharma/README.md:131`) proposes tracking "NADAC and Part D quarterly spending for the 10 IPAY 2026 drugs before and after 2026-01-01". Three essential methodological facts are missing:
  1. **Cross-payer invoice scope vs Part D-only MFP:** Because retail pharmacies purchase commingled wholesale inventory across commercial, Medicaid, cash, and Medicare patients, a Part D-only MFP refund never lowers wholesale invoice prices (NADAC); NADAC falls only when a manufacturer chooses to cut its **national list price (WAC) across all payers** (as occurred on `2026-01-01` for Eliquis `-43.00%`, Jardiance `-44.39%`, Farxiga `-37.00%`, and Fiasp `-75.00%`, and on `2025-01-01` for Januvia `-42.41%`, whereas Xarelto `+2.30%`, Entresto `+3.00%`, Enbrel `+5.00%`, and Stelara `+5.00%` raised WAC in early 2026).
  2. **Post-cut 2026 NADACs are still far above Part D MFPs:** Joining `data/raw/pharma/ira/selected_drugs_mfp.csv` (`IPAY == 2026`, `MFP Effective Date == 01/01/2026`) to `nadac_2026.csv` shows that even after the January 2026 WAC cuts, the `2026-10-21` NADAC per tablet remains **33.2% (`1.33x`) above the unit MFP for Eliquis 5 mg** (`$5.52144` NADAC vs `$4.145072` `NDC-9 MFP per Unit Price`, a `$1.38/tablet` gap), **64.7% (`1.65x`) above MFP for Jardiance 10 mg** (`$11.18898` vs `$6.793978`, a `$4.40/tablet` gap), **170.0% (`2.70x`) above MFP for Januvia 100 mg** (`$10.55001` vs `$3.907885`), and **184.0% (`2.84x`) above MFP for Xarelto 20 mg** (`$19.53935` vs `$6.880894`). Thus, even for Eliquis and Jardiance, the WAC cut did not bring pharmacy invoice acquisition prices down to the MFP; Part D fills still require retrospective MTF refunds for the remaining gap.
  3. **Imbruvica is absent from NADAC and Quarterly Part D lacks unit prices:** Of the 10 IPAY 2026 drugs, **`IMBRUVICA` (ibrutinib) has `0` rows in `nadac_2025.csv` and `nadac_2026.csv`** because it is dispensed through specialty pharmacies outside NADAC's retail community (`C/I`) frame, and `Quarterly Part D Spending by Drug` has no dosage-unit column (`Tot_Dsg_Unts` is only in the annual file, currently through 2024). Moreover, `selected_drugs_mfp.csv` records that `ENTRESTO`, `STELARA`, `XARELTO`, and `NOVOLOG`/`FIASP` are already marked `Deselect` (`end date of 12/31/2026`) due to generic/biosimilar competition.
- **Fix:** Update `pharma/README.md:114, 131` to: (1) explain why only national cross-payer WAC cuts move NADAC, (2) report the exact gap between post-cut 2026 NADAC and `NDC-9 MFP per Unit Price` for Eliquis (`$5.52` vs `$4.15`) and Jardiance (`$11.19` vs `$6.79`), and (3) note that Imbruvica is missing from NADAC (`0` rows) and that Quarterly Part D cannot provide unit spending.
- **Primary sources:** [CMS Final Guidance for IPAY 2027 and Manufacturer Effectuation of the MFP in 2026 and 2027](https://www.cms.gov/files/document/medicare-drug-price-negotiation-final-guidance-ipay-2027-and-manufacturer-effectuation-mfp-2026-2027.pdf), [CMS Selected Drug List and Negotiated Prices (MFP) ZIP](https://www.cms.gov/files/zip/selected-drug-list-negotiated-prices-also-known-maximum-fair-prices-statutezip.zip), [CMS Pharmacy and Dispensing Entity Resources](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/pharmacy-dispensing-entity-resources).

### 5. [Medium] "List vs net price" (`pharma/README.md:114`) omits off-invoice pharmacy discounts in NADAC, conflates published Part B Payment Limits with raw ASP, and omits non-ingredient components and strength pooling in Part D Spending by Drug

- **Issue:** Three price-definition details in `pharma/README.md:24, 35, 114` can mislead a public health analyst comparing prices across datasets:
  1. **NADAC excludes off-invoice pharmacy discounts:** While `nadac_sanity.md:4` states that NADAC excludes "off-invoice discounts", `pharma/README.md:114` mentions only "rebates manufacturers pay to PBMs, insurers and Medicaid." Per CMS's NADAC methodology, NADAC captures invoice prices only and excludes off-invoice discounts, prompt-pay discounts, and retrospective wholesaler, distributor, or buying-group rebates paid to pharmacies themselves (which can be substantial on generic drugs).
  2. **Published ASP Payment Limit vs raw ASP and statutory exclusions:** Under 42 U.S.C. § 1395w-3a(c)(2) and 42 CFR § 414.804, ASP excludes not only Medicaid rebates, but also **340B discounted sales**, VA/DoD/PHS/Federal Supply Schedule sales, Part D rebates, and bona fide service fees. Furthermore, the quarterly CMS ASP Pricing File (`pharma/README.md:35`) publishes the **Part B Payment Limit** (`106%` of ASP before the `2%` Medicare sequester reduction, or biosimilar `ASP + 8%` of the reference product's ASP, or `103%` of WAC for new drugs without established ASP), not raw ASP directly.
  3. **Part D `Avg_Spnd_Per_Dsg_Unt_Wghtd` includes dispensing fees/taxes and pools strengths:** While `pharma/README.md:114` warns that Medicaid SDUD "includes dispensing fees", it does not warn that Medicare `Part D Spending by Drug` (`Tot_Spndng` and `Avg_Spnd_Per_Dsg_Unt_Wghtd`) also includes **pharmacy dispensing fees, sales tax, and vaccine administration fees**, and aggregates across **all strengths and dosage forms** sharing a brand/generic name (e.g., pooling Eliquis 2.5 mg and 5 mg, or Ozempic pens and tablets).
- **Fix:** In `pharma/README.md:24, 35, 114`, add off-invoice pharmacy/wholesaler rebates to the NADAC exclusion note, distinguish the published Part B Payment Limit (`1.06 * ASP`) and ASP's 340B/federal-ceiling exclusions from raw ASP, and warn that Part D Spending by Drug unit spending includes dispensing fees/sales tax/vaccine administration fees and pools strengths.
- **Primary sources:** [42 CFR § 414.804 (Computation of Manufacturer's Average Sales Price)](https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-414/subpart-J/section-414.804), [CMS Medicare Part B ASP Pricing Files](https://www.cms.gov/medicare/payment/part-b-drugs/asp-pricing-files), [CMS Medicare Part D Spending by Drug Methodology](https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-part-d-spending-by-drug), [CMS NADAC Q&A (`nadacqa.pdf`)](https://www.medicaid.gov/medicaid-chip-program-information/by-topics/prescription-drugs/ful-nadac-downloads/nadacqa.pdf).

### 6. [Medium] NDC 10-to-11-digit normalization (`pharma/README.md:110-112`) omits that `openFDA drug/ndc` separates 2-segment `product_ndc` from 3-segment `packaging[].package_ndc`, excludes delisted historical NDCs, and is scheduled for FDA's 12-digit (`6-4-2`) transition

- **Issue:** `pharma/README.md:110` instructs analysts to "always normalize from the dashed form (openFDA and the NDC directory give it)." In practice:
  1. In `openFDA drug/ndc` (`api.fda.gov/drug/ndc.json`) and `ndctext.zip`, the top-level `product_ndc` is a **2-segment** labeler-product identifier (`4-4`, `5-3`, or `5-4`, which normalizes to a 9-digit `5-4` `NDC-9`); only the nested `packaging[].package_ndc` field contains the **3-segment** 10-digit code (`4-4-2`, `5-3-2`, `5-4-1`) that pads to an 11-digit `5-4-2` NDC.
  2. `openFDA drug/ndc` and the FDA NDC Directory contain **only currently listed active products** (`pharma/README.md:60`), whereas multi-year NADAC, SDUD, and claims panels contain discontinued or delisted NDCs whose 10-digit layout is absent from `openFDA`. To normalize or map historical NDCs to active ingredients and clinical drugs (`RxCUI`), analysts must use NLM's **RxNorm API** (`/REST/ndcstatus.json?ndc=...`, which accepts both 10-digit dashed and 11-digit dashless NDCs including inactive history) or CMS's quarterly **MDRP Drug Products** file (`0ad65fe5-3ad3-5d79-a3f9-7893ded7963a`).
  3. Under FDA's final rule (*Revising the National Drug Code Format and Drug Label Barcode Requirements*, 89 FR 73544, effective March 7, 2033), FDA-assigned NDCs will transition to a uniform 12-digit (`6-4-2`) format.
- **Fix:** In `pharma/README.md:110-112`, distinguish `packaging[].package_ndc` (pads to 11-digit `5-4-2`) from `product_ndc` (pads to 9-digit `5-4`), point analysts to RxNorm `/REST/ndcstatus` and MDRP Drug Products for delisted/historical NDCs missing from `openFDA drug/ndc`, and note the FDA 12-digit (`6-4-2`) rule effective March 7, 2033.
- **Primary sources:** [FDA National Drug Code Format and 12-Digit Final Rule](https://www.fda.gov/drugs/electronic-drug-registration-and-listing-system-edrls/national-drug-code-format), [openFDA Drug NDC API Documentation](https://open.fda.gov/apis/drug/ndc/), [NLM RxNorm API (`getNDCStatus`)](https://lhncbc.nlm.nih.gov/RxNav/APIs/api-RxNorm.getNDCStatus.html).

### 7. [Medium] The SDUD suppression section (`pharma/README.md:49, 118`) omits that SDUD includes pre-computed national total rows (`state == "XX"`) that avoid state-level cell suppression and must be filtered before summing states

- **Issue:** `pharma/README.md:118` accurately explains primary (`<11` prescriptions) and secondary counter-suppression in Medicaid SDUD (`652,561` of `1,287,884` rows in 2026 Q1 have `suppression_used = true`) and notes that "summing published amounts understates totals." However, it omits a critical structural feature of SDUD: every quarterly/annual SDUD dataset includes pre-computed **national aggregate rows (`state == "XX"`, `National Totals`)** alongside state rows (`AK`–`WY`).
  - If an analyst sums across all rows of SDUD without filtering `state`, they **double-count** every unsuppressed state total on top of `state == "XX"`.
  - Conversely, if an analyst sums only across the 50 states + DC (`state != "XX"`) to obtain national utilization or spending, they lose `50.7%` of rows to state-level primary and counter-suppression, whereas filtering directly to **`state == "XX"`** yields CMS's true national totals per NDC (suppressed only when an NDC has `<11` prescriptions across the entire United States).
- **Fix:** In `pharma/README.md:49, 118`, document that SDUD contains `state == "XX"` (`National Totals`) rows, instruct analysts to filter to `state == "XX"` for national aggregates and NADAC utilization weights, and warn never to sum state rows without excluding `state == "XX"`.
- **Primary sources:** [CMS Medicaid State Drug Utilization Data Field Descriptions](https://www.cms.gov/files/document/medicaid-state-drug-utilization-data-field-descriptions.pdf), [CMS SDUD Suppression FAQ](https://www.medicaid.gov/faq/2020-04-09/91856).

### 8. [Medium] The Part D vs Part B and ASP crosswalk section (`pharma/README.md:120`) omits Part B pharmacy-dispensed statutory categories and the billing-unit conversion required to link HCPCS codes to NDC unit prices

- **Issue:** `pharma/README.md:120` states: "Part D covers drugs dispensed by pharmacies (pills, pens, inhalers). Part B covers drugs administered in a clinic or hospital outpatient department (infusions, many cancer drugs, biologics), billed by HCPCS J-codes, not NDCs. The same molecule can sit in both. Use the ASP NDC-HCPCS crosswalk to connect them."
  1. **Part B covers key pharmacy-dispensed oral/inhalation drugs:** Under Social Security Act § 1861(s)(2), Medicare Part B also covers retail/specialty pharmacy-dispensed **oral immunosuppressive drugs** (after a Medicare-covered transplant), **oral anticancer prodrugs/equivalents** (e.g., capecitabine, temozolomide, cyclophosphamide), **oral antiemetics**, **nebulizer inhalation solutions** (e.g., albuterol, ipratropium, budesonide, tobramycin billed as Durable Medical Equipment supplies), **insulin used in external infusion pumps**, and Part B **preventive vaccines** (hepatitis B, pneumococcal, influenza, COVID-19, which use `Q` and `90xxx` CPT codes rather than `J`-codes).
  2. **Crosswalk unit conversion (`BILLUNITSPKG` vs `PKGSIZE`):** Connecting NDC-level NADAC (`per EA, ML, or GM`) to Part B ASP (`per HCPCS billing unit`, such as `per 1 mg`, `per 10 mg`, `per 0.5 mL`, or `per dose`) requires using the `PKGSIZE` and `BILLUNITSPKG` (Billing Units per Package) fields in the CMS ASP NDC-HCPCS Crosswalk; joining by NDC-to-HCPCS code alone without converting units produces severe unit mismatches.
- **Fix:** In `pharma/README.md:120`, note Part B's statutory outpatient pharmacy categories (oral transplant immunosuppressives, oral cancer/antiemetics, DME nebulizer drugs, pump insulin, and `Q`/`90xxx` vaccines) and state that joining NADAC to Part B ASP via the NDC-HCPCS crosswalk requires converting pricing units via `PKGSIZE` and `BILLUNITSPKG`.
- **Primary sources:** [Medicare Outpatient Prescription Drug Coverage (`medicare.gov`)](https://www.medicare.gov/coverage/prescription-drugs-outpatient), [CMS Medicare Part B Spending by Drug Methodology](https://data.cms.gov/resources/medicare-part-b-spending-by-drug-methodology), [CMS ASP NDC-HCPCS Crosswalk Files](https://www.cms.gov/medicare/payment/part-b-drugs/asp-pricing-files).

### 9. [Low] `pharma/README.md:47` misstates `NADAC Comparison` coverage as "Rolling, back to 2021" (it covers `2013-12-05` to `2026-10-21`) and omits an upstream CMS `Start Date` typo (`09/16/2023`) on `2026-09-23`

- **Issue:** `pharma/README.md:47` lists `Years / latest` for `NADAC Comparison` (`3,492,310` rows) as "Rolling, back to 2021". Parsing the full `data/raw/pharma/nadac/nadac_comparison.csv` file shows that `End Date` spans **`2013-12-05` through `2026-10-21`** across all 14 calendar years (`18,443` rows in 2013; `225,685` in 2014; `234k–343k` per year in 2015–2025; `285,322` in 2026 through October 21); `05/19/2021` simply happens to appear in the first unsorted lines of the CSV. In addition, all `28,605` rows of the `09/23/2026` monthly refresh in `nadac_comparison.csv` have an upstream CMS typo of **`Start Date = 09/16/2023`** (with `End Date = 09/23/2026` and `Effective Date = 09/23/2026`), and `Effective Date` is blank (`NaN`) on the `830,609` comparison rows prior to `2017-06-07`.
- **Fix:** Update `pharma/README.md:47` from `Rolling, back to 2021` to `Cumulative weekly changes, 2013-12-05 to 2026-10-21`, and note in "NADAC specifics" to filter/sort `NADAC Comparison` on `End Date` rather than `Start Date` (due to the `09/16/2023` typo on the `09/23/2026` release) and that `Effective Date` in `NADAC Comparison` starts on `2017-06-07`.
- **Primary sources:** [NADAC Comparison Dataset (`a217613c-12bc-5137-8b3a-ada0e4dad1ff`)](https://data.medicaid.gov/dataset/a217613c-12bc-5137-8b3a-ada0e4dad1ff), [Direct CSV (`nadac-comparison-10-21-2026.csv`)](https://download.medicaid.gov/data/nadac-comparison-10-21-2026.csv).

### 10. [Low] `pharma/scripts/summarize_nadac.py` and `pharma/outputs/nadac_sanity.md` truncate 5-decimal-place NADAC rates to 5 significant digits (`{:,.5g}`), omit baseline NDC counts in the tracer table, and use fragile positional column indexing

- **Issue:**
  1. CMS publishes all `NADAC Per Unit` values to a fixed **5 decimal places (`$0.00001`)**. In `summarize_nadac.py:49`, `md_table` formats floats with `floatfmt="{:,.5g}"` (5 significant figures), which drops decimal precision in `nadac_sanity.md` for all prices above `$1.00` (e.g., `$12.67003` displays as `12.67`, `$37.29673` as `37.297`, `$19.54698` as `19.547`, `$2,083.68575` as `2,083.7`).
  2. The tracer summary table in `nadac_sanity.md` reports only `NDCs (latest)` (`summarize_nadac.py:153-158`), hiding that NDC counts changed across the comparison window (`57 -> 69` for Atorvastatin 20 mg, `53 -> 57` for Metformin 500 mg, `10 -> 12` for Albuterol HFA, `0 -> 8` for Sitagliptin 100 mg).
  3. `summarize_nadac.py:155` computes `first_col, last_col = wide.columns[4], wide.columns[-1]`, which assumes `wide` has at least two snapshot columns; if run on the first weekly release of a new year without a prior-year file (`len(snaps) == 1`), `wide` has only 4 columns (`NDC Description`, `unit`, `cls`, `ndcs`, plus 1 date column = 5 columns, where `wide.columns[4]` equals `wide.columns[-1]`, or if all tracers are missing, 4 columns causing an `IndexError`).
- **Fix:** In `pharma/scripts/summarize_nadac.py`, format NADAC unit prices to 5 decimal places (`{:,.5f}`), report `NDCs (first / latest)` in the tracer summary table, and compute the tracer percentage change explicitly from named first and last snapshot columns only when at least two distinct snapshots are present.
- **Primary sources:** [NADAC 2026 Data Dictionary (`fbb83258-11c7-47f5-8b18-5f8e79f7e704`)](https://data.medicaid.gov/dataset/fbb83258-11c7-47f5-8b18-5f8e79f7e704).

---

## Shortcuts Taken

- None on Part 1, Part 2, or Part 3: all four local NADAC files (`nadac_2024.csv`, `nadac_2025.csv`, `nadac_2026.csv`, `nadac_comparison.csv`) and the IRA MFP file (`selected_drugs_mfp.csv`) were parsed in full via `.venv/bin/python`, and primary sources on `medicaid.gov`, `cms.gov`, `fda.gov`, `ecfr.gov`, and `nlm.nih.gov` were verified against official documentation and the saved public-source receipts. No files outside `reviews/pharma_agy_argon/` were created or modified.
