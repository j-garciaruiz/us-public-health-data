# Independent Part A replication

Completed 2026-10-21T01:00:14.689261+00:00 before opening any author code or pharma outputs.

No 2027 plan pricing data or new data were accessed. Inputs were limited to the seven named local raw sources (two pricing archives, MFP, spending, and two NADAC files).

## Methods

MFP rows with end before start are excluded. The 2026 lookup is active on 2026-12-31 to use the corrected Entresto Sprinkle values; the 2027 lookup is active on 2027-01-01. Pricing uses every matched plan x NDC x segment row at 30 days, with equal row weight. NDC strings retain leading zeros. The ratio median is inverted only after aggregation.

Part D uses Overall manufacturer rows, pools brand families using the selected names as prefixes with a word boundary, and excludes NovoLog Mix and InPen devices. This includes Enbrel Mini/SureClick, Fiasp Pumpcart and Austedo XR titration kits. Exact mappings are saved in brand_mapping.csv. Fixed claim mix means sum(baseline claims x new price per claim) / sum(baseline claims x old price per claim) minus 1, so baseline spending weights apply to percentage changes. Errors below are realized minus predicted, in percentage points. All dollars are gross.

## 2026 calibration

| Drug | r | Prediction % | Realized % | Error pp | 2025 $/claim | 2026Q1 $/claim | Matched rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ELIQUIS | 2.403119 | -58.3874 | -56.2640 | 2.1234 | 912.3142 | 399.0101 | 16721 |
| ENBREL | 3.438480 | -70.9174 | -70.7804 | 0.1370 | 8681.6348 | 2536.7401 | 23983 |
| ENTRESTO | 2.180282 | -54.1344 | -69.9562 | -15.8218 | 1077.5611 | 323.7403 | 25511 |
| FARXIGA | 3.173218 | -68.4862 | -67.0293 | 1.4569 | 997.7509 | 328.9655 | 10978 |
| IMBRUVICA | 1.722669 | -41.9505 | -39.9189 | 2.0317 | 16055.4616 | 9646.3037 | 29665 |
| JANUVIA | 2.707961 | -63.0718 | -61.5138 | 1.5580 | 556.0755 | 214.0121 | 16404 |
| JARDIANCE | 2.966900 | -66.2948 | -64.5499 | 1.7449 | 1091.1936 | 386.8292 | 11248 |
| NOVOLOG | 1.989688 | -49.7409 | -30.4241 | 19.3168 | 293.8035 | 204.4164 | 19089 |
| STELARA | 3.120436 | -67.9532 | -68.4251 | -0.4719 | 26682.0038 | 8424.8196 | 13446 |
| XARELTO | 2.837117 | -64.7529 | -62.8271 | 1.9259 | 1006.2108 | 374.0380 | 32674 |


Fixed 2025 claim mix: predicted -62.184889%; realized -61.374450%. Mean absolute drug-level error 4.6588 pp; maximum 19.3168 pp.

## 2027 cohort

| Drug | r | Prediction % | 2026Q1 $/claim | 2026Q1 claims | Gross removed, $m | Matched rows |
| --- | --- | --- | --- | --- | --- | --- |
| AUSTEDO | 1.683888 | -40.6136 | 8526.2792 | 74006 | 256.270351 | 50856 |
| BREO ELLIPTA | 5.685312 | -82.4108 | 535.2629 | 477136 | 210.471624 | 16120 |
| CALQUENCE | 1.674388 | -40.2767 | 14579.4461 | 49197 | 288.890507 | 5496 |
| IBRANCE | 2.015165 | -50.3763 | 15771.6047 | 43602 | 346.424347 | 21984 |
| JANUMET | 3.626331 | -72.4239 | 563.3744 | 230272 | 93.955080 | 23252 |
| LINZESS | 1.986037 | -49.6485 | 429.9901 | 670465 | 143.133190 | 16488 |
| OFEV | 2.125468 | -52.9515 | 13550.6618 | 51721 | 371.112802 | 3918 |
| OTEZLA | 3.239055 | -69.1268 | 5485.2146 | 62840 | 238.273765 | 18970 |
| OZEMPIC | 3.628883 | -72.4433 | 1417.5089 | 3358770 | 3449.088584 | 33030 |
| POMALYST | 2.701133 | -62.9785 | 23154.1226 | 21372 | 311.649007 | 9508 |
| TRADJENTA | 6.015458 | -83.3762 | 806.0406 | 292530 | 196.593534 | 5018 |
| TRELEGY ELLIPTA | 3.810245 | -73.7550 | 932.0863 | 1656431 | 1138.730003 | 10877 |
| VRAYLAR | 1.938442 | -48.4122 | 1559.8591 | 210833 | 159.213013 | 32976 |
| XIFAXAN | 3.253426 | -69.2632 | 3030.6940 | 111610 | 234.286681 | 8565 |
| XTANDI | 1.977230 | -49.4242 | 13812.7064 | 90089 | 615.021165 | 16488 |


Fixed 2026Q1 claim mix change: -63.400073%. Gross spending removed at Q1 volumes: $8,053,113,653.13, from $12,702,057,381.95 to $4,648,943,728.82.

## NADAC snapshot 2026-10-21

Only brand-classified NDCs in the latest global snapshot are used. Each NDC has equal weight. WAC cuts use Effective Date, Percent Change <= -20, and Primary Reason containing WAC.

| 2027 drug | NADAC/MFP | NDCs | WAC cuts since 2024 (date: range %) |
| --- | --- | --- | --- |
| AUSTEDO | 1.657543 | 12 | None |
| BREO ELLIPTA | 5.650074 | 5 | None |
| JANUMET | 3.635445 | 15 | 2025-01-01: -42.41 to -42.41 |
| LINZESS | 1.980967 | 3 | 2026-01-01: -50.27 to -50.26 |
| OTEZLA | 3.170688 | 4 | None |
| OZEMPIC | 3.595390 | 22 | None |
| TRADJENTA | 6.009500 | 3 | None |
| TRELEGY ELLIPTA | 3.804924 | 4 | None |
| VRAYLAR | 1.883633 | 10 | None |


Deselected 2026 drugs, NADAC / 2026 MFP:

| Drug | NADAC/MFP | NDCs |
| --- | --- | --- |
| ENTRESTO | 2.215230 | 8 |
| FIASP | 0.994848 | 4 |
| NOVOLOG | 0.996529 | 3 |
| STELARA | 3.322268 | 2 |
| XARELTO | 2.840470 | 19 |


2026 cohort WAC-cut base rate: 4/10 in 2025-12-20 through 2026-02-28 (ELIQUIS, FARXIGA, JARDIANCE, NOVOLOG); 5/10 since 2024 (ELIQUIS, FARXIGA, JANUVIA, JARDIANCE, NOVOLOG).

## Six continuing 2026 drugs

| Drug | 2026 MFP / 30 days | 2027 MFP / 30 days | Change % |
| --- | --- | --- | --- |
| ELIQUIS | 231.00 | 237.25 | 2.705628 |
| ENBREL | 2355.00 | 2418.70 | 2.704883 |
| FARXIGA | 178.50 | 183.33 | 2.705882 |
| IMBRUVICA | 9319.00 | 9571.07 | 2.704904 |
| JANUVIA | 113.00 | 116.06 | 2.707965 |
| JARDIANCE | 197.00 | 202.33 | 2.705584 |


These are descriptive gross price predictions, without a causal or net-savings interpretation.
