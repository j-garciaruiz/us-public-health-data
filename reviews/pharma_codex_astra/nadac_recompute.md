# Independent NADAC recomputation

Computed UTC: 2026-10-20T12:37:01.820154+00:00

Written before opening the author's outputs, analysis scripts or README sections.
NDCs are strings. Dates are parsed; weekly comparisons join adjacent snapshots by NDC.
Quantiles use pandas linear interpolation. Prices are dollars per listed pricing unit.
A change greater than 1% means absolute relative change > 0.01. Increases are also reported separately.

- 2025: SHA-256 matches sidecar `317c0387d2005b18ade760029bf61b3ff5a3aab74ef96e322d319432c410ed80`; 1,608,416 parsed rows.
  Source recorded in sidecar: https://download.medicaid.gov/data/nadac-national-average-drug-acquisition-cost-12-31-2025.csv
- 2026: SHA-256 matches sidecar `62205340628b7e313534c22e963a9f5e47495c621f9c115180f761b2256ceed8`; 1,268,309 parsed rows.
  Source recorded in sidecar: https://download.medicaid.gov/data/nadac-national-average-drug-acquisition-cost-10-21-2026.csv
- Live 2026 API count: 1,268,309, matches parsed rows.
- Hashes establish agreement with saved provenance, not an independent re-download of source bytes.

## 1. Coverage

Rows: 1,268,309; snapshots: 42; first: 2026-01-07; latest: 2026-10-21.
NDCs per snapshot min/median/max: 29,918 / 30,168.5 / 30,597.
Distinct annual NDCs: 32,972.

## 2. Integrity

Not exactly 11 ASCII digits: 0.
Duplicate (snapshot,NDC) rows beyond first: 0.
Missing/non-numeric price: 0; non-positive: 0.

## 3. Effective-date changes exceeding half of shared NDCs

| snapshot | shared | effective_changed | effective_pct |
| --- | --- | --- | --- |
| 2026-01-21 | 30421 | 28227 | 92.787877 |
| 2026-02-18 | 30449 | 28464 | 93.480902 |
| 2026-03-18 | 30050 | 28176 | 93.763727 |
| 2026-04-22 | 30167 | 28349 | 93.973547 |
| 2026-05-20 | 30228 | 29197 | 96.589255 |
| 2026-06-17 | 29972 | 28936 | 96.543441 |
| 2026-07-22 | 30083 | 29037 | 96.522953 |
| 2026-08-19 | 30239 | 29226 | 96.650021 |
| 2026-09-23 | 29892 | 28926 | 96.768366 |
| 2026-10-21 | 29992 | 29138 | 97.152574 |

## 4. Annual overlap

Latest 2025 (2025-12-31) and latest 2026 shared NDCs: 27,573.

## 5. Latest-snapshot strata

| Classification for Rate Setting | Pricing Unit | NDCs | p10 | median | p90 |
| --- | --- | --- | --- | --- | --- |
| B | EA | 1667 | 2.0940700000000003 | 12.67003 | 94.71785800000019 |
| B | GM | 108 | 1.1314580000000003 | 19.628095000000002 | 63.13678799999999 |
| B | ML | 477 | 0.7889880000000002 | 37.29673 | 2083.68575 |
| B-ANDA | EA | 70 | 0.12488 | 1.7383 | 31.589522000000002 |
| B-ANDA | GM | 8 | 1.0683410000000002 | 5.091595 | 20.578042999999997 |
| B-ANDA | ML | 12 | 1.643208 | 6.315564999999999 | 21.349040000000002 |
| B-BIO | EA | 6 | 488.95029 | 499.25158 | 904.3636650000001 |
| B-BIO | ML | 30 | 21.141716000000002 | 723.01205 | 2949.3370640000007 |
| G | EA | 22874 | 0.03364 | 0.14096 | 1.92417 |
| G | GM | 1542 | 0.06151 | 0.30981 | 2.45816 |
| G | ML | 3301 | 0.02407 | 0.4591 | 9.41555 |

| OTC | NDCs |
| --- | --- |
| N | 27470 |
| Y | 2625 |

## 6. Last-two-snapshot transition

From 2026-10-14 to 2026-10-21.

| snapshot | shared | effective_changed | effective_pct | price_changed | abs_change_gt1pct | increased_any | increased_gt1pct | added | dropped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-21 | 29992 | 29138 | 97.152574 | 28712 | 20165 | 14883 | 10629 | 103 | 39 |

## 7. Exact-description tracer medians

Missing descriptions remain NaN; no substitution.

| description | 2025-01-01 | 2026-01-07 | 2026-10-21 | change_pct |
| --- | --- | --- | --- | --- |
| ATORVASTATIN 20 MG TABLET | 0.03166 | 0.03072 | 0.02858 | -9.728363866077071 |
| METFORMIN HCL 500 MG TABLET | 0.01304 | 0.01415 | 0.01483 | 13.726993865030668 |
| LISINOPRIL 10 MG TABLET | 0.01707 | 0.01877 | 0.01797 | 5.272407732864681 |
| AMLODIPINE BESYLATE 5 MG TAB | 0.0104 | 0.01111 | 0.01015 | -2.4038461538461564 |
| LEVOTHYROXINE 50 MCG TABLET | 0.0517 | 0.05022 | 0.04006 | -22.514506769825925 |
| ALBUTEROL HFA 90 MCG INHALER | 2.36448 | 2.07215 | 1.83196 | -22.521653809717147 |
| SITAGLIPTIN PHOSPHATE 100 MG TABLET | nan | nan | 3.84929 | nan |
| JANUVIA 100 MG TABLET | 10.55893 | 10.55456 | 10.55001 | -0.08447825679306353 |
| ELIQUIS 5 MG TABLET | 9.51063 | 9.69551 | 5.52144 | -41.944539951612036 |
| XARELTO 20 MG TABLET | 18.20331 | 19.12429 | 19.53935 | 7.33954429167003 |
| JARDIANCE 10 MG TABLET | 19.54698 | 11.19625 | 11.18898 | -42.75852331152945 |
| OZEMPIC 1 MG/DOSE (4 MG/3 ML) PEN | 311.84756 | 331.99298 | 331.93928 | 6.4428017330005805 |
| LANTUS SOLOSTAR 100 UNIT/ML | 6.17208 | 6.16611 | 6.16433 | -0.1255654495729286 |

## 8. Timing of tracer drops

Drops compare consecutive snapshot medians over all available 2025 and 2026 snapshots.

### ELIQUIS 5 MG TABLET

| snapshot | median | drop_pct |
| --- | --- | --- |
| 2025-05-21 | 9.69113 | -0.10009442481270225 |
| 2025-06-18 | 9.69011 | -0.010525088405566319 |
| 2025-08-20 | 9.69127 | -0.00020637087529973286 |
| 2026-01-14 | 5.52654 | -42.99897581457809 |
| 2026-05-20 | 5.52374 | -0.05066461113101273 |
| 2026-06-17 | 5.52276 | -0.01774160260983315 |
| 2026-08-19 | 5.52106 | -0.030962723415972615 |

### JARDIANCE 10 MG TABLET

| snapshot | median | drop_pct |
| --- | --- | --- |
| 2025-05-21 | 20.12245 | -0.05433759540741656 |
| 2025-06-18 | 20.12174 | -0.0035283973870092744 |
| 2026-01-07 | 11.19625 | -44.39400704346716 |
| 2026-05-20 | 11.19542 | -0.007413196382710652 |
| 2026-06-17 | 11.19341 | -0.017953770381107237 |
| 2026-07-22 | 11.19289 | -0.004645590575169667 |
| 2026-08-19 | 11.18819 | -0.041990942464364966 |
| 2026-10-21 | 11.18898 | -0.0027705064396310597 |

### JANUVIA 100 MG TABLET: first four 2026 snapshots

| snapshot | median | change_from_previous_snapshot_pct |
| --- | --- | --- |
| 2026-01-07 | 10.55456 | 0.0 |
| 2026-01-14 | 10.55456 | 0.0 |
| 2026-01-21 | 10.55456 | 0.0 |
| 2026-01-28 | 10.55456 | 0.0 |

### XARELTO 20 MG TABLET: first four 2026 snapshots

| snapshot | median | change_from_previous_snapshot_pct |
| --- | --- | --- |
| 2026-01-07 | 19.12429 | 0.0 |
| 2026-01-14 | 19.12429 | 0.0 |
| 2026-01-21 | 19.12429 | 0.0 |
| 2026-01-28 | 19.12429 | 0.0 |

