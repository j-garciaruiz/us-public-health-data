# Part 1: Independent Recompute (Blind)

Computed independently using `.venv/bin/python` and `reviews/pharma_agy_argon/recompute.py` from `data/raw/pharma/nadac/nadac_2025.csv` and `data/raw/pharma/nadac/nadac_2026.csv` prior to inspecting `pharma/outputs/`, `pharma/scripts/`, `reviews/pharma_codex_astra/`, or the "Starter dataset" section of `pharma/README.md`.

## 1. SHA-256 Verification Against Sidecars

Both raw CSV files match their `.meta.json` sidecar SHA-256 digests, byte counts, and data row counts exactly:

| File | Sidecar SHA-256 | Recomputed SHA-256 | Match | Bytes | Data Rows |
|---|---|---|---|---:|---:|
| `nadac_2025.csv` | `317c0387d2005b18ade760029bf61b3ff5a3aab74ef96e322d319432c410ed80` | `317c0387d2005b18ade760029bf61b3ff5a3aab74ef96e322d319432c410ed80` | PASS | 139,475,442 | 1,608,416 |
| `nadac_2026.csv` | `62205340628b7e313534c22e963a9f5e47495c621f9c115180f761b2256ceed8` | `62205340628b7e313534c22e963a9f5e47495c621f9c115180f761b2256ceed8` | PASS | 109,956,674 | 1,268,309 |

## 2. 2026 Dataset Summary Metrics

- **Data rows:** `1,268,309` (plus 1 header line = `1,268,310` total lines)
- **Number of snapshots (`As of Date`):** `42`
- **First snapshot:** `2026-01-07` (`01/07/2026`)
- **Latest snapshot:** `2026-10-21` (`10/21/2026`)
- **Distinct NDCs:** `32,972`
- **NDCs per snapshot (min / median / max):** `29,918` / `30,168.5` / `30,597` (Across the 42 weekly snapshots, the 21st and 22nd sorted counts are `30,159` and `30,178`, yielding an exact median of `30,168.5`.)
- **NDCs not 11 digits:** `0` rows (`0` distinct NDCs) when `NDC` is read as a string. (`239,123` rows start with a leading zero and would be truncated below 11 digits if parsed as integer.)
- **Duplicate `(snapshot, NDC)` rows:** `0`

## 3. Latest 2026 Snapshot (`2026-10-21` / `10/21/2026`): Median NADAC Per Unit (`Pricing Unit == "EA"`)

- **Generics (`Classification for Rate Setting == "G"`, `Pricing Unit == "EA"`):** `$0.14096` (`0.14096`, across `22,874` NDCs; mean `$2.14124`)
- **Brands (`Classification for Rate Setting == "B"`, `Pricing Unit == "EA"`):** `$12.67003` (`12.67003`, across `1,667` NDCs; mean `$115.87285`)
- *Note on additional brand-related classifications in the latest snapshot (`Pricing Unit == "EA"`):* `B-ANDA` has `70` NDCs with median `$1.73830`, and `B-BIO` has `6` NDCs with median `$499.25158`. If `B`, `B-ANDA`, and `B-BIO` are pooled (`1,743` NDCs), the pooled median is `$12.14492`.

## 4. 2026 Monthly Survey Refreshes

Defining a monthly survey refresh as a 2026 snapshot in which more than 50% of NDCs present in both that snapshot and the immediately preceding snapshot have a changed `Effective Date`, there are **10** monthly survey refreshes in 2026 (one per month from January through October):

| # | Snapshot (`YYYY-MM-DD`) | Raw `As of Date` | Preceding Snapshot | Common NDCs | Changed `Effective Date` | % Changed | Modal New `Effective Date` |
|---:|---|---|---|---:|---:|---:|---|
| 1 | `2026-01-21` | `01/21/2026` | `2026-01-14` | 30,421 | 28,227 | 92.79% | `01/21/2026` |
| 2 | `2026-02-18` | `02/18/2026` | `2026-02-11` | 30,449 | 28,464 | 93.48% | `02/18/2026` |
| 3 | `2026-03-18` | `03/18/2026` | `2026-03-11` | 30,050 | 28,176 | 93.76% | `03/18/2026` |
| 4 | `2026-04-22` | `04/22/2026` | `2026-04-15` | 30,167 | 28,349 | 93.97% | `04/22/2026` |
| 5 | `2026-05-20` | `05/20/2026` | `2026-05-13` | 30,228 | 29,197 | 96.59% | `05/20/2026` |
| 6 | `2026-06-17` | `06/17/2026` | `2026-06-10` | 29,972 | 28,936 | 96.54% | `06/17/2026` |
| 7 | `2026-07-22` | `07/22/2026` | `2026-07-15` | 30,083 | 29,037 | 96.52% | `07/22/2026` |
| 8 | `2026-08-19` | `08/19/2026` | `2026-08-12` | 30,239 | 29,226 | 96.65% | `08/19/2026` |
| 9 | `2026-09-23` | `09/23/2026` | `2026-09-16` | 29,892 | 28,926 | 96.77% | `09/23/2026` |
| 10 | `2026-10-21` | `10/21/2026` | `2026-10-14` | 29,992 | 29,138 | 97.15% | `10/21/2026` |

(All other 2026 snapshots have `<2%` of common NDCs changing `Effective Date`, including the cross-year boundary `2025-12-31` to `2026-01-07` at `1.14%`.)

## 5. Tracer Medians at First 2025 Snapshot (`2025-01-01`) and Latest 2026 Snapshot (`2026-10-21`)

| Exact `NDC Description` | NDCs (`2025-01-01`) | Median NADAC (`2025-01-01`) | NDCs (`2026-10-21`) | Median NADAC (`2026-10-21`) | Absolute Change ($/unit) | % Change |
|---|---:|---:|---:|---:|---:|---:|
| `ATORVASTATIN 20 MG TABLET` | 57 | 0.03166 | 69 | 0.02858 | -0.00308 | -9.73% |
| `METFORMIN HCL 500 MG TABLET` | 53 | 0.01304 | 57 | 0.01483 | +0.00179 | +13.73% |
| `ELIQUIS 5 MG TABLET` | 3 | 9.51063 | 3 | 5.52144 | -3.98919 | -41.94% |
| `JARDIANCE 10 MG TABLET` | 3 | 19.54698 | 3 | 11.18898 | -8.35800 | -42.76% |
| `JANUVIA 100 MG TABLET` | 5 | 10.55893 | 5 | 10.55001 | -0.00892 | -0.08% |
| `XARELTO 20 MG TABLET` | 5 | 18.20331 | 5 | 19.53935 | +1.33604 | +7.34% |

## 6. Snapshot and Size of Median Drop for `ELIQUIS 5 MG TABLET` and `JARDIANCE 10 MG TABLET`

- **`ELIQUIS 5 MG TABLET`** (`NDC`s `00003089421`, `00003089431`, `00003089470`):
  - **Snapshot of drop:** `2026-01-14` (`01/14/2026`), carrying `Effective Date = 01/01/2026` and `Explanation Code = 3`.
  - **Size of step drop at `2026-01-14`:** From `$9.69551` (at `2026-01-07`) to `$5.52654`, a drop of **`$4.16897` per tablet (`-43.00%`, exact `-42.9990%`)**.
  - **Size of overall change (`2025-01-01` to `2026-10-21`):** From `$9.51063` to `$5.52144`, a net change of **`-$3.98919` per tablet (`-41.94%`)**.
- **`JARDIANCE 10 MG TABLET`** (`NDC`s `00597015230`, `00597015237`, `00597015290`):
  - **Snapshot of drop:** `2026-01-07` (`01/07/2026`, the first weekly snapshot of 2026, compared with `2025-12-31` in the 2025 file), carrying `Effective Date = 01/01/2026` and `Explanation Code = 3`.
  - **Size of step drop at `2026-01-07`:** From `$20.13497` (at `2025-12-31`) to `$11.19625`, a drop of **`$8.93872` per tablet (`-44.39%`, exact `-44.3940%`)**.
  - **Size of overall change (`2025-01-01` to `2026-10-21`):** From `$19.54698` to `$11.18898`, a net change of **`-$8.35800` per tablet (`-42.76%`)**.
  - *Note if restricted to `nadac_2026.csv` alone:* Because `JARDIANCE 10 MG TABLET` already entered the first 2026 snapshot (`2026-01-07`) at `$11.19625`, its step drop occurs across the `2025-12-31` to `2026-01-07` year boundary; within 2026 snapshots alone, its largest week-to-week decline is `-$0.00470` (`-0.04%`) on `2026-08-19`.
