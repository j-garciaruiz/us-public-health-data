# What we expect in 2027: pre-registered predictions for the second negotiation cycle

Written 2026-10-20, before any 2027 outcome data were examined. The git commit that adds this file is the registration timestamp; later edits go in the "Amendments" section at the end and never change a prediction above it.

Data note: CMS posted a monthly plan pricing release for contract year 2027 on 2026-10-08. It was not downloaded or opened before registration, so prediction P1 is tested on published but unseen data. Everything else (NADAC from 2026-12-20, Part D spending for 2027 Q1) does not exist yet.

Baseline numbers and the calibration: `pharma/outputs/prereg_2027/baseline.md` (script `pharma/scripts/prereg_2027.py`, CSVs beside it).

## Why we can make sharp predictions

In finding 4, plan prices for the ten 2026 drugs moved to the MFP on 2026-01-01. If the MFP binds, a drug's gross Part D spending per claim should fall by about **1/r − 1**, where r is the plan unit price divided by the coming MFP in the last plan pricing file before the MFP starts. Tested after the fact on the 2026 drugs (October 2025 file vs the measured 2025 to 2026 Q1 change), the rule missed by at most **2.1 percentage points** for eight of the ten drugs (Eliquis predicted −58%, measured −56%; Enbrel −71% and −71%; Stelara −68% and −68%). The two misses have known causes: Entresto lost most of its claims to generics during 2026 (−54% predicted, −70% measured), and the CMS NovoLog entry pools two brands with very different prices (−50% and −30%). At fixed 2025 claim mix the rule gave −62.2% for the ten drugs; the measured change was −61.4%.

This was fitted to nothing: the rule has no free parameter. The 2027 cohort is its first real test.

## Predictions

### P1. Plan prices move to the MFP on 2027-01-01 (first plan pricing file for plan year 2027)

- For each of the 15 drugs, the median plan unit price divided by the 2027 MFP per unit is between 0.995 and 1.005.
- Across all plan-product rows of the 15 drugs, at least 90% are within 0.5% of the MFP; weighting each drug by its 2026 Q1 claims, at least 97%.
- No drug has more than 5% of its rows above the MFP by more than 0.5% (in the January 2026 file the only exception was unbranded ustekinumab grouped with Stelara).
- The six 2026 drugs that continue (Eliquis, Enbrel, Farxiga, Imbruvica, Januvia, Jardiance) sit at their inflation-adjusted 2027 MFP (2.7% above the 2026 MFP for each): median ratio between 0.995 and 1.005 for each.
- Most likely exception: semaglutide. Its MFP is $274 per 30 days, while the administration's most-favored-nation agreement with Novo Nordisk sets $245 a month for Medicare (KFF 2025-11-26 calls the interaction of the two prices unclear). If semaglutide's median ratio is below 0.95, we read that as the agreement price binding instead of the MFP, not as a failure of the MFP to bind.

### P2. Gross Part D spending per claim falls by 1/r − 1 (Part D quarterly spending, 2027 Q1; expected around July 2027)

Comparison: 2026 full year (the 2026 Q4 year-to-date file) vs 2027 Q1, the design of finding 1. Predicted change by drug, from the October 2026 plan pricing file:

| Drug | r (Oct 2026) | Predicted change | Gabriel et al.: MFP vs estimated net | CMS: MFP vs 2024 list |
|---|---|---|---|---|
| Tradjenta | 6.02 | −83% | −60% | −84% |
| Breo Ellipta | 5.69 | −82% | −58% | −83% |
| Trelegy Ellipta | 3.81 | −74% | −43% | −73% |
| Ozempic | 3.63 | −72% | −36% | −71% |
| Janumet | 3.63 | −72% | −43% | −85% |
| Xifaxan | 3.25 | −69% | −54% | −63% |
| Otezla | 3.24 | −69% | −26% | −65% |
| Pomalyst | 2.70 | −63% | not estimable | −60% |
| Ofev | 2.13 | −53% | −40% | −50% |
| Ibrance | 2.02 | −50% | −35% | −50% |
| Linzess | 1.99 | −50% | −44% | −75% |
| Xtandi | 1.98 | −49% | −26% | −48% |
| Vraylar | 1.94 | −48% | −23% | −44% |
| Austedo | 1.68 | −41% | −15% | −38% |
| Calquence | 1.67 | −40% | −36% | −40% |

The CMS column is measured against 2024 list prices, before the Janumet (2025) and Linzess (2026) list-price cuts; that is why those two predicted changes are smaller than CMS's discounts.

- **Pass:** at least 12 of the 15 drugs within 5 percentage points of the prediction (a wider band than the 2.1-point calibration error, because the 2026 baseline is a full year that includes January 2026 list-price changes and mix shifts).
- **Group:** at fixed 2026 claim mix, gross spending per claim on the 15 drugs falls by 63% (pass if between −58% and −68%). At 2026 Q1 volumes this removes about **$8.0 billion of gross spending a quarter** from $12.7 billion.
- **Ordering:** the predicted ranks hold: Spearman correlation between predicted and measured change of at least 0.8.
- The gross fall exceeds the net discount Gabriel et al. estimate for every drug, because list prices exceed net prices; this is a gross measure and says nothing about net savings. CMS's own estimate (44%, about $12 billion a year against 2024 net spending) and Gabriel's median net discount (38%) are the net benchmarks; our data cannot test them.
- Comparison groups (drugs selected for 2028 and other brands) change by between −3% and +5% at fixed mix, as in 2026 (about +1%). Tradjenta is renegotiated for 2028 but keeps its 2027 MFP until then.
- Known risks, recorded now: the semaglutide entry ("Ozempic" above) pools the Part D rows of Ozempic, Rybelsus and Wegovy, and Wegovy has its own per-package MFP, so a shift toward Wegovy moves per-claim spending without a price change; generic pomalidomide already has its own Part D row, so Pomalyst brand claims can shift; switches between formulations (Austedo to Austedo XR) can do the same, as generic entry did for Entresto in 2026.

### P3. List prices and pharmacy acquisition cost (NADAC, weekly)

Nine of the 15 drugs have brand NADAC rates (Tradjenta, Breo, Trelegy, Ozempic, Janumet, Otezla, Linzess, Vraylar, Austedo); the six specialty drugs do not. Janumet (−42%, 2025-01-01) and Linzess (−50%, 2026-01-01) have already cut list prices. Base rate from 2026: 5 of 10 drugs cut list prices by 20% or more between 2025-12-20 and 2026-02-28 (Eliquis, Jardiance, Farxiga and Fiasp on 2026-01-01, Imbruvica on 2025-12-22), 6 of 10 since 2024.

- **Count:** of the seven NADAC drugs without an earlier cut, between 2 and 5 get a WAC-based NADAC cut of 20% or more effective 2026-12-20 to 2027-02-28.
- **Where:** cuts are more likely where list price is far above the MFP and rebates are large (Tradjenta, Breo and Trelegy, at 3.8 to 6.0 times the MFP) than for Vraylar and Austedo (1.7 to 1.9 times).
- **Siblings:** if a manufacturer cuts a selected drug, it cuts related brands on the same day, as Boehringer Ingelheim did with Jardiance's combinations in 2026. Specifically: a Tradjenta cut comes with a Jentadueto cut; a Breo or Trelegy cut comes with a cut on at least one other GSK Ellipta brand (Anoro, Incruse, Arnuity).
- **Gap persists:** drugs without a cut keep NADAC at 1.5 or more times the 2027 MFP in the last NADAC file of June 2027 (median today 3.6). Drugs that cut stay at or above the MFP (in 2026 Eliquis went to 1.33, Jardiance 1.65, Farxiga 2.00, Fiasp 0.99).

### P4. The four drugs leaving the program on 2027-01-01

CMS ends the MFP of Entresto, Stelara, Xarelto and NovoLog/Fiasp on 2026-12-31 because generics or biosimilars are marketed. If nothing else changes, plans go back to list-based prices with rebates.

- In the first 2027 plan pricing file, brand Entresto, Xarelto and Stelara products are no longer at the old MFP: median plan unit price at least 1.5 times the 2026 MFP for each, near today's NADAC multiple (Entresto 2.2, Xarelto 2.8, Stelara 3.3).
- NovoLog and Fiasp stay near the old MFP (ratio 0.9 to 1.2), because their list prices were already cut to about that level (NADAC at 1.00 and 0.99 times the MFP).
- Part D gross spending per claim on the brand rows rises from 2026 to 2027 Q1 by at least 50% for Entresto, Xarelto and Stelara.
- What would break this: manufacturers keep their brand prices near the old MFP to compete with generics and biosimilars (a WAC cut in NADAC before 2027-02-28 would show it). That would be a finding in itself.

### P5. The six continuing drugs

Gross spending per claim from 2026 to 2027 Q1 changes by between −3% and +6% for each (their MFP rises 2.7%; Imbruvica has no NADAC and is judged on Part D alone).

## How each prediction will be scored

| Prediction | Data | Expected | Script |
|---|---|---|---|
| P1, P4 (plan prices) | Plan pricing files, plan year 2027 (monthly CY2027 release posted 2026-10-08; quarterly January 2027 release) | Now (monthly) and January 2027 | `spuf_mfp_check.py`, extended to 2027 MFPs |
| P3 | NADAC weekly and the NADAC Comparison file | January to June 2027 | `ira_analysis.py` |
| P2, P4, P5 (spending) | Part D quarterly spending, 2026 Q4 and 2027 Q1 | About July 2027 (2026 Q1 came out 2026-07-08) | `ira_analysis.py` with the 2027 groups |

Each prediction is scored pass or fail as written; partial results are reported as such. Results go in `pharma/ira_findings.md` with a link back here.

## Amendments

### Amendment 1 (2026-10-20, after the Codex review; no 2027 outcome data opened)

Codex (GPT-6 Astra, high) replicated every baseline number from the raw files (221 values, differences at floating-point level; `reviews/pharma_prereg_codex_astra/report.md`, PASS WITH FIXES). This amendment fixes how the predictions are scored. It changes no registered number or band.

**Correction of the data note.** The CMS monthly series posted 2026-10-08 is "Formulary and Pharmacy Network Information": by its catalog description it has plan, formulary, cost-sharing and network tables but no pricing (unit cost) table. Plan-year 2027 prices therefore do not exist yet in public data, and P1 and P4 cannot be tested before the first quarterly pricing release with plan-year 2027 prices (expected January 2027). Nothing from that series was opened.

**Scoring contract (all predictions).**
- Primary test: the first CMS release containing plan-year 2027 unit prices. Later releases are reported as replications, never as replacements.
- Unit of analysis for plan prices: contract x plan x segment x NDC rows with `DAYS_SUPPLY = 30`, compared at full precision with the MFP per unit for that NDC in the CMS MFP file as downloaded on 2026-10-20 (`data/raw/pharma/ira/`), superseded rows dropped. Later MFP revisions are reported separately.
- Claim-weighted share: sum over drugs of (2026 Q1 claims x the drug's within-0.5% share), divided by total 2026 Q1 claims.
- Each clause of P1 to P5 is scored separately as pass, fail or not evaluable. There is no overall verdict. A missing product or drug counts as not evaluable, is listed, and never counts as a pass or leaves a denominator silently.

**P1, semaglutide.** The equality test stands as written for all 15 drugs, semaglutide included: a semaglutide median below 0.995 is a fail of P1. The sentence reading a median below 0.95 as the $245 agreement price binding is withdrawn as an excuse; it becomes a separate descriptive note. Context recorded: CMS's GLP-1 Bridge runs outside Part D coverage and payment from 2026-07-01 to 2027-12-31 (CMS page last modified 2026-07-13), so the agreement is not expected to show up in Part D plan unit prices. Separately from the equality test, we report whether every price satisfies the MFP ceiling (at or below the MFP).

**P2, weights and comparators.** The group prediction (−63.4%) uses 2026 Q1 claims as fixed weights. Scoring: observed index = sum(Q1 2026 claims x 2027 Q1 spending per claim) / sum(Q1 2026 claims x full-year 2026 spending per claim) − 1, scored against the registered −58% to −68% band. The same index computed with the full-year 2026 per-claim baseline times (1 + predicted change) is reported as a sensitivity. The $8.05 billion figure is an illustration at fixed 2026 Q1 prices and volumes, not a forecast of 2027 spending. Comparison groups are frozen as defined in `pharma/scripts/ira_analysis.py` at registration; Tradjenta stays in the 2027 group, and named sibling brands with list-price cuts (P3) are reported separately.

**P2, honest calibration.** The 2.1-point figure covers eight of ten drugs, chosen after the two misses were seen. Across all ten, the mean absolute error is 4.7 points and the rank correlation is 0.72, below the 0.8 P2 asks for, so the rank clause is a harder test than the calibration passed. The two misses carried 6.5% of 2026-cohort spending; semaglutide carries 37.5% of the 2027 cohort's 2026 Q1 spending and 42.8% of the predicted dollar change, so the group test leans on it. All 15 drugs stay in the primary test.

**P3, definitions.**
- A family cut: at least one brand-classified NDC of the drug on the frozen MFP list with a NADAC Comparison row whose primary reason contains "WAC" and whose percent change is −20 or lower, effective 2026-12-20 to 2027-02-28 inclusive; counted once per drug. The seven drugs: Tradjenta, Breo Ellipta, Trelegy Ellipta, semaglutide (Ozempic, Rybelsus, Wegovy), Otezla, Vraylar, Austedo.
- "Where" is exploratory: we report the cut share among Tradjenta, Breo and Trelegy against Vraylar and Austedo, without a pass/fail.
- Siblings: only the named pairs (Tradjenta with Jentadueto; Breo or Trelegy with Anoro, Incruse or Arnuity). Pass if the sibling has a WAC-based cut of 20% or more with the same effective date; not evaluable if the triggering drug does not cut.
- Gap: in the last NADAC snapshot of June 2027, the median NADAC / 2027 MFP over each drug's brand NDCs. Drugs without a family cut must be at 1.5 or more; drugs with one at 1.00 or more. The 1.00 floor stays as registered but is strict: the 2026 precedent it cites, Fiasp, sits at 0.99 and would fail it. A 0.98 floor is reported as a sensitivity.
- Base-rate sources: NADAC alone shows 4 of 10 2026 drugs with a cut in the window and 5 of 10 since 2024; adding Imbruvica's 2025-12-22 cut (no NADAC; NCPA notice and 46brooklyn) gives the registered 5 of 10 and 6 of 10. The 2027 count is NADAC-only.

**P4, a hypothesis, not a consequence.** Deselection does not force plans back to list-based prices; P4 tests the hypothesis that they return. The 1.5x plan-price clause and the 50% spending clause are separate tests, scored on brand products only (NovoLog and Fiasp split; unbranded ustekinumab and other unbranded NDCs excluded). A brand with no plan-price rows or fewer than 1,000 claims in 2027 Q1 is not evaluable. A WAC cut, continued plan discounting, coverage loss or a change in mix are reported as possible mechanisms; none turns a failed threshold into a pass.

**P2 wording.** "The gross fall exceeds the net discount Gabriel et al. estimate for every drug" applies to the 14 drugs with an estimable net price, and the two are different estimands (Gabriel: 2022 estimated net prices). CMS's net benchmark is 44% (about $12 billion) excluding Coverage Gap Discount Program discounts and 36% (about $8.5 billion) including them.
