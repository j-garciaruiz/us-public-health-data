# Medicare drug price negotiation: what is known, what others have written, and how they used our data

Literature and grey-literature scan for the IRA negotiation study ([pharma/ira_findings.md](../pharma/ira_findings.md)). Searched 2026-10-20.

**How this was searched.** Three parallel search legs (Claude Opus 5.5 subagents): peer-reviewed and working papers (OpenAlex, PubMed, PMC full text, NBER/SSRN), grey literature (CMS, CBO, MedPAC, KFF, consultancies, pharmacy associations, trade press, legal trackers), and prior uses of our data sources (NADAC, Part D Spending by Drug, the MFP file, SDUD). Their full tables, with about 180 entries, are in [ira_notes/academic.md](ira_notes/academic.md), [ira_notes/grey.md](ira_notes/grey.md) and [ira_notes/data_uses.md](ira_notes/data_uses.md). Verification: every one of the 108 DOIs cited across the three files resolves (107 in Crossref, one Zenodo DataCite DOI opened directly), and the DOI titles of the papers used below match their descriptions. The grey-literature claims this summary relies on were reopened at the source (CMS MTF fact sheet, MedPAC March 2026 chapter 13, NCPA's WAC-decrease alert and refund-delay notice, Drug Channels, 46brooklyn, the Supreme Court denial); figures that could not be confirmed at the source are left out or marked. Claims about papers come from abstracts unless marked full text; two papers' numbers come only from press coverage and are marked (press). The Consensus quota was exhausted and OpenAlex hit its daily limit near the end, so a few searches (commercial-price spillovers, inflation-rebate studies, stock-market event studies) did not run. This is a scoping scan, not a systematic review.

---

## 1. The program in one page

- **Law and timeline.** The Inflation Reduction Act (Pub. L. 117-169, August 2022) lets Medicare negotiate prices (Maximum Fair Prices, MFPs) for high-spend single-source drugs: small molecules after 7 years on the market (9 years before prices apply), biologics after 11 (13). First 10 Part D drugs selected 2023-08-29, prices published 2024-08-15, **in effect 2026-01-01**. Second cohort of 15 Part D drugs: prices published 2025-11-25, effective 2027-01-01. Third cohort of 15 (first Part B drugs, plus Tradjenta renegotiated): selected 2026-01-27; final offers due 2026-09-30, acceptance by 2026-10-31, **prices published by 2026-11-30**, effective 2028-01-01. Full verified timeline in [grey.md](ira_notes/grey.md).
- **What CMS claims.** Against 2023 prices, the first 10 MFPs would have saved 22% of net spending (about $6 billion); the 2027 cohort 44% (about $12 billion; 36% or $8.5 billion counting coverage-gap discounts). Wouters et al. 2024 (JAMA) argue the 22% overstates savings because the comparison is not to current net prices.
- **The list is already shrinking.** Stelara, Entresto and Xarelto (generic or biosimilar entry, determined October 2025) and NovoLog/Fiasp (March 2026) leave the program on 2027-01-01; Xeljanz (2028 cohort) on 2029-01-01.
- **Legal status.** The Supreme Court declined to hear the manufacturers' challenges on 2026-05-18 (AstraZeneca, Novo Nordisk, Novartis, Bristol Myers Squibb, Janssen, Boehringer Ingelheim; [Duane Morris](https://www.duanemorris.com/alerts/supreme_court_declines_hear_challenges_inflation_reduction_act_medicare_drug_price_0526.html)). The D.C. Circuit ruled for CMS in Teva's case on 2026-08-18; AbbVie's Botox suit (February 2026) is pending.
- **Political changes around it.** The 2025 reconciliation law broadened the orphan-drug exclusion from the 2028 cohort (CBO: $8.8 billion over 10 years, via secondary reporting). The administration's most-favored-nation deals set a $245 Medicare GLP-1 price, below the $274 semaglutide MFP, with a GLP-1 bridge outside Part D through 2027; the GLOBE Part B model exempts drugs with an MFP in effect. The "pill penalty" fix (EPIC Act) was not found to have passed. A proposed rule (CMS-4215-P, 2026-06-16) would codify the program.

## 2. How big are the price cuts, and against what

The single most important lesson for our study: **list, net and MFP are three different prices, and these drugs carried very large rebates.**

| Source | What it shows |
|---|---|
| MedPAC, March 2026, ch. 13 ([PDF](https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch13_MedPAC_Report_To_Congress_SEC.pdf), read in full) | In 2024, rebates reduced gross Part D costs by **nearly 45% for the 2026 cohort** and about 34% for the 2027 cohort (all single-source drugs: just under 30%). Rebates on the 2026 drugs totalled nearly $28 billion, about 35% of all Part D rebates. MedPAC concludes the program looks more effective for the 2027 cohort, which had less rebate competition. |
| Wouters et al. 2024, JAMA ([10.1001/jama.2024.22582](https://doi.org/10.1001/jama.2024.22582)) | IPAY 2026 MFPs were 8% (dapagliflozin) to 42% (sitagliptin) below estimated 2021 net prices, and 1.1 to 4.3 times prices in six other high-income countries. |
| Hernandez, Gabriel & Dickson 2023, JMCP ([10.18553/jmcp.2023.29.8.868](https://doi.org/10.18553/jmcp.2023.29.8.868)); Sullivan et al. 2024, Value in Health ([10.1016/j.jval.2024.08.001](https://doi.org/10.1016/j.jval.2024.08.001)) | Before prices were announced: the statutory ceiling bound for only a few drugs (etanercept, ibrutinib, ustekinumab); for others, existing net prices were already below the ceiling. |
| Jeon et al. 2026, Value in Health ([10.1016/j.jval.2026.03.010](https://doi.org/10.1016/j.jval.2026.03.010)) | Projected 2026 Part D **net** spending on the 10 drugs: $26.1 billion without negotiation vs $23.8 billion with it, **−8.8%**. |
| Gabriel et al. 2026, JMCP ([10.18553/jmcp.2026.32.5.530](https://doi.org/10.18553/jmcp.2026.32.5.530)); Li et al. 2026, Value in Health ([10.1016/j.jval.2025.09.3054](https://doi.org/10.1016/j.jval.2025.09.3054)) | IPAY 2027 MFPs: a median 38% below estimated net prices (range 15–60%), yet a median 108% above purchasing-power-adjusted prices in most-favored-nation countries. Li et al. had predicted 32–78% off list. |

**What this means for our finding 1.** Our −64% median (−61% fixed-mix) drop in gross Part D spending per claim is mostly the **list price collapsing onto something close to the old net price**. With 45% rebates on these drugs, a 60% gross drop is consistent with a net saving in the single digits to low teens, which is what Jeon et al. project. Our headline must keep "gross" in the first sentence and set it beside the net projections.

## 3. What has been observed since 2026-01-01

**Realized spending: nothing published.** None of the three legs found a peer-reviewed paper, working paper or grey-literature report that measures realized 2026 Part D spending or prices for the ten drugs. Everything published is either a projection or a different outcome:

| Outcome | Evidence |
|---|---|
| Formulary access | Jain & McCoy 2026, Health Affairs Scholar ([10.1093/haschl/qxag290](https://doi.org/10.1093/haschl/qxag290)): every plan covers all 10 drugs in 2026; step therapy on negotiated diabetes drugs rose to 5.0% (comparators under 1%). Zheng et al. 2026 ([10.1093/haschl/qxag171](https://doi.org/10.1093/haschl/qxag171)): access to non-selected brands in competitive classes fell 11.8 points in stand-alone plans, 2024–2026. |
| Patient out-of-pocket | Castle et al. 2026, Annals ([10.7326/annals-26-02703](https://doi.org/10.7326/annals-26-02703)) (press): projected savings of about $685 a year (stand-alone plans) and $470 (Medicare Advantage); 26–49% lower OOP for six drugs, none for Stelara, Imbruvica and Enbrel users already at the $2,100 cap. Lederman et al. 2025, NBER ([10.3386/w33889](https://doi.org/10.3386/w33889)): with the 2025 cap and nonlinear cost sharing, most users see no change or a higher marginal OOP. |
| Benefit redesign (confounder) | Anderson et al. 2026, Health Affairs ([10.1377/hlthaff.2025.00644](https://doi.org/10.1377/hlthaff.2025.00644)); Zhang et al. 2026, AJHP ([10.1093/ajhp/zxag083](https://doi.org/10.1093/ajhp/zxag083)): the 2025 redesign raised deductibles and shifted tiers to coinsurance. |
| Pharmacy refunds | CMS fact sheet (April 2026, [PDF](https://www.cms.gov/files/document/pharmacy-dispensing-entity-mtf-fact-sheet.pdf), read in full): plans have 7 days to submit claim data and manufacturers 14 days to process; refunds reach pharmacies **within 21 days of the date of service, on average**. NCPA (2026-02-27, [notice](https://www.ncpa.org/newsroom/qam/2026/02/27/ncpa-shares-survey-results-cms-showing-mfp-refund-delays)): most member pharmacies waited 22 days or more and about a fifth more than 28 days; a majority drew on savings. (Exact survey percentages and sample size reported elsewhere could not be confirmed at the source.) Long-term-care pharmacies: Bhardwaj et al. 2026, JMCP ([10.18553/jmcp.2026.25312](https://doi.org/10.18553/jmcp.2026.25312)) model large revenue losses. |

**List-price cuts: well documented in grey literature, not in academic work.** NCPA's alert (dated 2025-12-10, [page](https://ncpa.org/wac-decreases-coming-take-action-now)) listed the coming WAC decreases: **Imbruvica 2025-12-22**; Eliquis, Farxiga, Jardiance, Glyxambi, Synjardy, Synjardy XR, Trijardy XR, Fiasp, Tresiba and Linzess on 2026-01-01; Lilly's Humalog U-200 and Lyumjev on 2026-02-01. 46brooklyn's January 2026 price review (Elsevier Gold Standard WAC data) reports Eliquis −43.0% and Jardiance −44.4%, the same figures as our NADAC rows. Drug Channels (2026-04-08) counts list-price cuts on **6 of the 10** products with a 2026 MFP. Explanations offered:

- Under CMS's default refund (WAC minus MFP), a lower WAC shrinks refunds owed and the pharmacy float (Drug Channels, Milliman). Drug Channels warns this also erases any pharmacy margin on MFP drugs.
- Bristol Myers Squibb told Reuters the Eliquis cut avoids Medicare inflation penalties (secondary report, not reopened here).
- The cuts raised 340B prices from near zero (Penn State rural health office: Eliquis $245, Jardiance $120.05 from 2026-07-01; not reopened here).
- For insulin and some inhalers, the 2024 removal of the Medicaid rebate cap is the documented driver (KFF 2024; Levy et al. 2024, JAMA Health Forum, [10.1001/jamahealthforum.2024.3624](https://doi.org/10.1001/jamahealthforum.2024.3624), on Flovent; Han et al. 2026, Health Affairs, [10.1377/hlthaff.2025.01309](https://doi.org/10.1377/hlthaff.2025.01309): generic share rose 23 points after the 2024 inhaler cuts).

## 4. Strategic responses and innovation

- **Launch prices.** Shanmugam et al. 2026, JAMA ([10.1001/jama.2026.17742](https://doi.org/10.1001/jama.2026.17742)) (press): no measurable change in the launch-price trend after the IRA.
- **Trials and the "pill penalty".** Studies funded by the National Pharmaceutical Council (an industry body) report 25–68% drops in small-molecule investment or trials; Kang et al. 2026, Health Affairs ([10.1377/hlthaff.2025.00720](https://doi.org/10.1377/hlthaff.2025.00720)) find overall trial activity stable, with fewer trials only at manufacturers with negotiated drugs. Wouters et al. 2024, JAMA ([10.1001/jama.2024.16911](https://doi.org/10.1001/jama.2024.16911)) find little evidence that biologics need the longer protection. Funding sources matter here and are recorded in [academic.md](ira_notes/academic.md).
- **Deselection.** Beinfeld et al. 2025 model the overlap of Stelara's MFP and biosimilars; no one has measured it.

## 5. How others have used our data sources

| Source | Typical uses (examples in [data_uses.md](ira_notes/data_uses.md)) | Lessons for us |
|---|---|---|
| NADAC | Generic markups and PBM spread pricing (Medicaid, Part D), Cost Plus comparisons, generic price spikes; the closest IRA use is Three Axis Advisors for NCPA (January 2025), a pre-launch pharmacy cash-flow model built on NADAC, WAC and the Part D dashboard | Brand NADAC sits about 1% below WAC on average (Levy et al. 2017), so our NADAC/MFP ratio is in practice a list-to-MFP ratio. NADAC excludes specialty pharmacies (Imbruvica and Stelara were missing in Three Axis's data too). Screen for level shifts from the 2024 chain-reporting change. |
| Part D Spending by Drug | Top-spending drugs, price growth per dosage unit, predicting which drugs get selected, savings simulations | Per-claim measures mix price with days supply; per-unit or 30-day-equivalent measures are standard. Use per-unit once the annual 2026 file exists. |
| MFP file | MFP vs list, net (SSR Health), VA and international prices (Wouters 2024; Gabriel 2026; KFF/Peterson: MFPs 2.8 times an 11-country average) | Our NDC-level join to NADAC by date is not in the literature. |
| SDUD and plan files | Medicaid insulin spending after list cuts; difference-in-differences around price events (Wing et al. 2026, NBER); Part D plan pricing files (SPUF) with NADAC (Hernandez et al. 2023; Dusetzina 2024) | The SPUF plan pricing file would show directly whether plans price the 10 drugs at the MFP. |

## 6. Where our three findings stand

| Our finding | Status in the literature | Change to make |
|---|---|---|
| 1. Part D gross spending per claim −64% (median) for the 10 drugs, comparison groups flat | **New.** No published measure of realized 2026 spending. | Lead with "gross"; set it beside MedPAC's 45% rebate share and Jeon et al.'s −8.8% projected net change. |
| 2. List-price cuts on 2026-01-01, same-day cuts on related brands | **Confirmed independently** by NCPA (dates) and 46brooklyn (Eliquis −43.0%, Jardiance −44.4%). Not studied academically. | Add Imbruvica's 2025-12-22 cut (no NADAC, so our data missed it). With Januvia (2025) and NovoLog (2024) that is consistent with Drug Channels' count of list-price cuts on 6 of the 10 MFP products. Cite the refund-mechanism, inflation-penalty and 340B explanations as candidates. Report a spending-weighted share as well as the NDC share. |
| 3. NADAC 1.3–3.6 times the MFP for most drugs | **New as a public-data measure.** Grey literature documents refund timing (CMS: 21 days on average) and pharmacy strain; one modelling paper for long-term-care pharmacies. | Frame it as a list-to-MFP benchmark gap, combined with CMS's 21-day refund timing, rather than a measured loss. |

## 7. The Latin America angle

- RAND for ASPE (2024, [10.7249/rhq-11-03-05](https://doi.org/10.7249/rhq-11-03-05), 2022 IQVIA MIDAS data) gives US prices as a share of Colombian, Mexican and Chilean prices: for Colombia, 267% overall, about 1,165% for brand originators and 48.5% for unbranded generics (Mexico 172/402/51, Chile 260/748/76, from Table B.1 as transcribed by the scan; worth reopening before quoting).
- No study compares the MFPs with Latin American prices.
- Colombia's Circular 03 de 2013 lists the United States among the 17 international reference countries; whether later circulars changed the basket, and which US price enters it, was not checked. If US list prices enter the reference, the January 2026 cuts could feed into Colombian price ceilings.
- Moye-Holz & Vogler 2021 ([10.1007/s40258-021-00670-4](https://doi.org/10.1007/s40258-021-00670-4)) give the PPP-per-DDD method for Latin American procurement prices.

## 8. Next steps the literature suggests for our study

1. Read the plan pricing files (SPUF 2026) to check whether plans price the 10 drugs at the MFP (Hernandez 2023, Dusetzina 2024 method).
2. Add a spending-weighted version of the WAC-cut share (46brooklyn weights by prior-year Medicaid spending from SDUD).
3. Bracket net with published estimates rather than guessing (MedPAC rebate shares, Wouters, Jeon); add VA Big Four prices as a public lower bracket.
4. Write down expected 2027 changes for the 15 IPAY 2027 drugs now, with Gabriel and Li as benchmarks (the "write the outcomes down first" step in our findings).
5. Track the four deselected drugs after 2026-12-31 (Entresto and Stelara generics/biosimilars in NADAC and Part D).
6. Optional Latin America extension: MFP and NADAC against SISMED (Colombia) and CMED (Brazil) prices per DDD.

## Not used or not confirmed

Numbers seen only in summaries or press (Castle 2026, Shanmugam 2026, the DLA Piper survey, the NCPA survey percentages and sample size, Reuters on Bristol Myers Squibb, the Penn State 340B prices, the CBO $8.8 billion figure via CRFB/STAT) are marked or left out above. Several publisher and government sites (cbo.gov, congress.gov, healthaffairs.org) refused scripted access. The scans' own "Not verified" lists are in the three notes files.
