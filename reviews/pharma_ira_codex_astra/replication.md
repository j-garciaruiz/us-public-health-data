# Independent Part A replication

Saved 2026-10-20T18:06:44.350932+00:00, before opening the original IRA script, outputs or findings.
Implemented from raw inputs in `replicate.py`. All available sidecar SHA-256 checks passed.
Percentiles use linear interpolation. Pooled changes use the same volume-eligible families.
Other-brand families are uppercase brand names. Missing brand names are excluded.
WAC windows include both endpoints; event counts are distinct January-universe NDCs.
Selected cut medians use each NDC's most negative event; earliest date is among qualifying cut events.
NDC identifiers preserve leading zeroes. No cross-IPAY NDC is counted twice.
Ratio summaries use all matched NDCs independently at each snapshot, without a constant-panel restriction.
The MFP CSV has no explicit pricing-unit column, so these are arithmetic joins pending unit validation in Part B.
Last snapshot dates: {"2024": "2024-12-25", "2025": "2025-12-31", "2026": "2026-10-21"}. The 2026 snapshot is labeled one day after retrieval.

## A1. Part D spending per claim

| group | families | median_pct | p25_pct | p75_pct | pooled_pct | share_falling_30_pct |
| --- | --- | --- | --- | --- | --- | --- |
| IPAY 2026 | 10 | -63.6885 | -68.0761 | -57.5764 | -61.6566 | 90.0000 |
| IPAY 2027 | 15 | 2.3680 | 0.7829 | 3.5504 | 4.2766 | 6.6667 |
| IPAY 2028 | 15 | 1.7083 | 0.0074 | 3.8670 | 13.2197 | 0.0000 |
| Other brands | 1088 | 0.2932 | -3.9031 | 3.4673 | 7.1852 | 1.7463 |

| family | claims_2025 | claims_2026q1 | per_claim_2025 | per_claim_2026q1 | change_pct | annualized_claim_change_pct |
| --- | --- | --- | --- | --- | --- | --- |
| ELIQUIS | 26359023.0000 | 6501172.0000 | 912.3142 | 399.0101 | -56.2640 | -1.3443 |
| ENBREL | 473766.0000 | 119666.0000 | 8681.6348 | 2536.7401 | -70.7804 | 1.0338 |
| ENTRESTO | 3645979.0000 | 123085.0000 | 1077.5611 | 323.7403 | -69.9562 | -86.4964 |
| FARXIGA | 6736318.0000 | 1171247.0000 | 997.7509 | 328.9655 | -67.0293 | -30.4518 |
| IMBRUVICA | 146696.0000 | 32041.0000 | 16055.4616 | 9646.3037 | -39.9189 | -12.6329 |
| JANUVIA | 3868076.0000 | 913473.0000 | 556.0755 | 214.0121 | -61.5138 | -5.5372 |
| JARDIANCE | 13826680.0000 | 3461230.0000 | 1091.1936 | 386.8292 | -64.5499 | 0.1319 |
| NOVOLOG | 2132339.0000 | 738999.0000 | 291.8489 | 208.9360 | -28.4095 | 38.6269 |
| STELARA | 120962.0000 | 17003.0000 | 26682.0038 | 8424.8196 | -68.4251 | -43.7741 |
| XARELTO | 6511197.0000 | 1465876.0000 | 1006.2108 | 374.0380 | -62.8271 | -9.9474 |
| LINZESS | 2784367.0000 | 670465.0000 | 843.4261 | 429.9901 | -49.0186 | -3.6815 |

## A2. January WAC-related cuts

| year | group | universe | cuts | cuts_pct | increases | increases_pct |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 | IPAY 2026 | 63 | 3 | 4.7619 | 58 | 92.0635 |
| 2024 | IPAY 2027 | 63 | 0 | 0.0000 | 55 | 87.3016 |
| 2024 | IPAY 2028 | 20 | 0 | 0.0000 | 20 | 100.0000 |
| 2024 | Other brands | 1572 | 57 | 3.6260 | 786 | 50.0000 |
| 2025 | IPAY 2026 | 67 | 13 | 19.4030 | 47 | 70.1493 |
| 2025 | IPAY 2027 | 70 | 15 | 21.4286 | 42 | 60.0000 |
| 2025 | IPAY 2028 | 30 | 0 | 0.0000 | 30 | 100.0000 |
| 2025 | Other brands | 2327 | 5 | 0.2149 | 929 | 39.9226 |
| 2026 | IPAY 2026 | 69 | 21 | 30.4348 | 13 | 18.8406 |
| 2026 | IPAY 2027 | 67 | 3 | 4.4776 | 36 | 53.7313 |
| 2026 | IPAY 2028 | 33 | 1 | 3.0303 | 21 | 63.6364 |
| 2026 | Other brands | 2198 | 33 | 1.5014 | 836 | 38.0346 |

### Selected families with qualifying cuts

| year | group | family | ndcs | median_pct | earliest |
| --- | --- | --- | --- | --- | --- |
| 2024 | IPAY 2026 | NOVOLOG | 3 | -75.0000 | 2024-01-01 |
| 2025 | IPAY 2026 | JANUVIA | 13 | -42.4100 | 2025-01-01 |
| 2025 | IPAY 2027 | JANUMET | 15 | -42.4100 | 2025-01-01 |
| 2026 | IPAY 2026 | ELIQUIS | 6 | -43.0000 | 2026-01-01 |
| 2026 | IPAY 2026 | FARXIGA | 5 | -37.0000 | 2026-01-01 |
| 2026 | IPAY 2026 | JARDIANCE | 6 | -44.3900 | 2026-01-01 |
| 2026 | IPAY 2026 | NOVOLOG | 4 | -75.0000 | 2026-01-01 |
| 2026 | IPAY 2027 | LINZESS | 3 | -50.2700 | 2026-01-01 |
| 2026 | IPAY 2028 | XELJANZ | 1 | -25.0000 | 2026-01-01 |

## A3. NADAC / MFP per unit

2025 and 2026 column labels refer to the last available snapshot listed above.

| family | ratio_2025 | ndcs_2025 | units_2025 | ratio_2026 | ndcs_2026 | units_2026 |
| --- | --- | --- | --- | --- | --- | --- |
| ELIQUIS | 2.3383 | 6 | EA | 1.3310 | 6 | EA |
| ENBREL | 3.3964 | 4 | ML | 3.5683 | 4 | ML |
| ENTRESTO | 2.1561 | 7 | EA | 2.2183 | 8 | EA |
| FARXIGA | 3.1653 | 7 | EA | 1.9949 | 7 | EA |
| IMBRUVICA | NA | 0 |  | NA | 0 |  |
| JANUVIA | 2.7008 | 13 | EA | 2.6986 | 13 | EA |
| JARDIANCE | 2.9637 | 6 | EA | 1.6469 | 6 | EA |
| NOVOLOG | 1.9998 | 10 | ML | 0.9970 | 10 | ML |
| STELARA | 3.1624 | 2 | ML | 3.3223 | 2 | ML |
| XARELTO | 2.7793 | 19 | EA, ML | 2.8405 | 19 | EA, ML |
