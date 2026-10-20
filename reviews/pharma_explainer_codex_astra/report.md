# Fact-check: Medicare drug-pricing explainer

Reviewed against information available on 2026-10-20. Target: `pharma/explainer_medicare_drug_pricing.md`. The target was not edited.

## Verdict

**SUBSTANTIVE CORRECTIONS REQUIRED before circulation.** The analysis's headline figures agree with the supplied results, and most paper-specific numbers are transcribed correctly. However, several simplifications teach the wrong mechanism: the statutory ceiling reverses the meaning of the 60% discount; pharmacy reimbursement is described as an exact payment rather than a cap; NADAC minus MFP is treated as an actual refund receivable; and list-price cuts are assigned unconditional effects on patients, PBMs and 340B entities. The PBM self-dealing allegation is not established by the cited studies. The Jain summary materially misstates its sample and findings.

Two further distinctions matter throughout: projections are not measured 2026 outcomes, and savings percentages calculated against different years and discount arrangements are not directly comparable. Twelve ranked fixes below supply replacement wording.

## Checked claims

**Status convention:** CONFIRMED means supported at the precision and scope stated in the check, not independently proven causal. WRONG includes materially misleading scope, mechanism or certainty; the correction appears in the same row. COULD NOT CHECK identifies what the available evidence cannot establish. Repeated claims are grouped. Paper and grey-document identifiers refer to the supplied [manifest](../../literature/ira_fulltext/MANIFEST.md); their extracted texts were inspected directly, not accepted from the literature review's summaries.

### Pricing, benefit design and public purchasers

| Location and claim | Status | Check, correct value or qualification; evidence |
|---|---|---|
| §1: manufacturer, wholesaler, pharmacy, insurer and PBM roles; three large wholesalers | CONFIRMED | Reasonable simplified supply chain. A pharmacy receives both patient cost sharing and plan/PBM reimbursement. Three national wholesalers dominate distribution. [KFF supply-chain explanation](https://www.kff.org/other-health/follow-the-pill-understanding-the-u-s/). |
| §1: CVS Caremark, Express Scripts and Optum Rx manage about 80% of prescriptions; insurer ownership | CONFIRMED | Approximately 80%, not a precise share of every prescription market. Supported by paper 6's background and the [FTC's PBM report](https://www.ftc.gov/system/files/ftc_gov/pdf/pharmacy-benefit-managers-staff-report.pdf). |
| §1: Medicare funds most Part D costs; private stand-alone and Medicare Advantage drug plans | CONFIRMED | Consistent with [MedPAC, March 2026, chapter 13](https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch13_MedPAC_Report_To_Congress_SEC.pdf). |
| §§1, 9: Part D means pharmacy drugs and Part B means clinic/hospital drugs | WRONG | These are usual patterns, not a location-based rule. Part B also covers certain pharmacy-dispensed drugs and home-use drugs; some outpatient drugs fall under Part D. Use “generally self-administered outpatient drugs” versus “certain drugs, often administered by a clinician.” [Medicare drug coverage](https://www.medicare.gov/coverage/prescription-drugs-outpatient). |
| §2: WAC is what the manufacturer publishes and charges wholesalers | WRONG | WAC is a published list benchmark before discounts, not necessarily the actual wholesaler invoice or transaction price. [Statutory WAC definition, SSA §1847A(c)(6)(B)](https://www.ssa.gov/OP_Home/ssact/title18/1847A.htm). |
| §§2, 6, 9: NADAC is a weekly survey | WRONG | **Monthly invoice survey, weekly published rates**, with interim updates including WAC changes and help-desk reviews. NADAC covers retail community pharmacies and is per billing unit, not the price of an entire NDC package. [CMS methodology](https://www.medicaid.gov/medicaid-chip-program-information/by-topics/prescription-drugs/ful-nadac-downloads/nadacmethodology.pdf). |
| §§2, 8: Levy 2018, brand NADAC about 99% of WAC in 2015; VA about half | CONFIRMED | Paper 5: databases accessed **2015-04-01**; brand NADAC/WAC **0.991**; VA measure **48.3% below WAC**, hence 51.7% of WAC. A historical sample average, not a current guarantee for each drug. NADAC and VA prices are proposed bounds for economic evaluation, not universal legal bounds. |
| §2: plan payment usually tied to list price; rebates negotiated for formulary access | CONFIRMED | Broadly reasonable as a description of traditional brand-drug arrangements, with selected-drug MFP rules an important exception. Rebates can be passed through by PBMs; they are not necessarily retained PBM revenue. [MedPAC chapter 13](https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch13_MedPAC_Report_To_Congress_SEC.pdf). |
| §§2, 9: list minus rebates and discounts is what “the system really ends up paying” | WRONG | Manufacturer net revenue, payer net spending, pharmacy acquisition cost and patient cost sharing are distinct. Fees, distribution margins and whose rebates are counted matter. A net-price estimate needs a named perspective and denominator. Grey C's methods distinguish manufacturer prices from other price concepts. |
| §§2, 8: 2024 rebates nearly 45% for round one, 34% for round two, just under 30% for single-source brands | CONFIRMED | These values and the **2024** reference year match [MedPAC's March 2026 chapter 13](https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch13_MedPAC_Report_To_Congress_SEC.pdf). They do not establish the rebate rate in the analysis's 2025 baseline. |
| §2: insulin gross sales approximately $13bn to $27bn; net approximately $8bn to $5bn, 2012–2019 | WRONG | Rounded amounts and directions are supported, but the underlying Dickson study covers **four leading insulin products**, not all insulin. The scope must be stated. [Dickson et al., underlying study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10267767/). |
| §2: Medicaid basic brand rebate is 23.1% of AMP plus inflation rebate | WRONG | For most innovator drugs, basic rebate is the **greater of 23.1% of AMP or AMP minus best price**, plus any inflation rebate. Certain products have special percentages. AMP is a statutory retail-channel sales measure, not WAC. [CMS rebate formulas](https://www.medicaid.gov/medicaid/prescription-drugs/medicaid-drug-rebate-program/unit-rebate-amount-calculation). |
| §2: rebate cap of 100% removed on 2024-01-01 | CONFIRMED | The former cap was **100% of AMP**, not an unspecified “price.” Effective **2024-01-01** under American Rescue Plan Act §9816. [American Rescue Plan Act, §9816](https://www.govinfo.gov/content/pkg/PLAW-117publ2/html/PLAW-117publ2.htm). |
| §§2, 5: 340B price linked to Medicaid rebates; penny pricing | CONFIRMED | General formula is preceding-quarter **AMP minus unit rebate amount**, with a **$0.01 per-unit** floor when the calculated ceiling is below a penny. It is not $0.01 for every package. [HRSA ceiling-price and package-price definitions](https://www.hrsa.gov/opa/faqs). |
| §§2, 8: VA counterfactual, top 50 oral drugs in 2016, $14.4bn or 44% saving | CONFIRMED | Paper 18 supports the rounded result and **2016** data year; published **2019**. This is a modeled price substitution, not realized Medicare savings. |
| §§1–3: everyone pays a premium, then deductible, then cost sharing up to a cap | WRONG | Plan designs and subsidies differ; some drugs bypass the deductible. The annual cap excludes premiums, noncovered drugs and Part B spending. [Medicare Part D costs](https://www.medicare.gov/health-drug-plans/part-d/basics/costs). |
| §§3, 7, 8: $2000 cap in 2025 and $2100 in 2026 | CONFIRMED | Correct for qualifying out-of-pocket spending on covered Part D drugs. After the threshold there is no additional cost sharing for those drugs that year. [CMS 2026 redesign instructions](https://www.cms.gov/newsroom/fact-sheets/final-cy-2026-part-d-redesign-program-instructions). |
| §3: 2025 redesign made manufacturers pay discounts and shifted catastrophic liability to plans | CONFIRMED | Direction correct, but discounts were not entirely new: the Manufacturer Discount Program **replaced** the Coverage Gap Discount Program. Selected drugs are exempt from the new discounts during their MFP applicability period. [CMS manufacturer-discount guidance](https://www.cms.gov/files/document/manufacturer-discount-program-final-guidance.pdf). |
| §3: higher deductibles and more coinsurance after redesign, Anderson and Zhang 2026 | CONFIRMED | Both are **2026** publications using earlier plan-design data. Higher deductibles are supported by [Anderson's abstract](https://www.healthaffairs.org/doi/10.1377/hlthaff.2025.00644); the coinsurance shift by [Zhang's abstract](https://pubmed.ncbi.nlm.nih.gov/41805901/). Say “studies found” rather than treating all changes as an isolated causal effect of the law. |

### Negotiation: eligibility, ceilings, dates and implementation

| Location and claim | Status | Check, correct value or qualification; evidence |
|---|---|---|
| §§1, 4: negotiation began in 2026; IRA enacted in 2022 | WRONG | **2022** authorization is correct. Selection and preparation began in **2023**; first-round offers and price bargaining occurred in **2024**; prices first applied in **2026**. [CMS first-round fact sheet](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026). |
| §4: single-source high-spending drugs; 7 years for small molecules, 11 for biologics | CONFIRMED | Those are eligibility ages **at selection**, not when MFPs start. Effective prices generally arrive about **9 and 13 years** after first approval/licensure at the earliest. “Small molecule” is not synonymous with “pill.” Other exclusions and the biosimilar-delay process exist. [CMS selection explainer](https://www.cms.gov/files/document/fact-sheet-medicare-selected-drug-negotiation-list-ipay-2026.pdf). |
| §4: 2025 orphan expansion exempts drugs for multiple rare diseases | WRONG | Incomplete enough to mislead: applies starting with **IPAY 2028**; all approved indications must be for designated rare diseases. For initially orphan-only drugs later approved for a non-orphan indication, the selection clock starts at that first non-orphan approval. [CMS IPAY 2028 guidance, §30.1.1](https://www.cms.gov/files/document/ipay-2028-final-guidance.pdf). |
| §§4, 8: CBO letter 2025-10-20, $8.8bn over 2025–2034; $6.7–10.9bn range; original $4.9bn | CONFIRMED | Grey B supports the date, horizon and amounts. Darzalex, Keytruda and Opdivo are included in the additional assessment. These are projected federal costs of the statutory change, not observed spending. |
| §4: CMS sets a final price after company counteroffers | WRONG | CMS and the manufacturer **agree** an MFP through the statutory process. CMS can make a final offer, but a final offer is not automatically an accepted agreement. [SSA §1194](https://www.ssa.gov/OP_Home/ssact/title11/1194.htm). |
| §4: at least 25% below non-federal average price, “up to 60% below” beyond 16 years | WRONG | The 60% is a **minimum discount from the applicable benchmark**, not a maximum. Long-monopoly status starts at **16 years or more on January 1 of the applicability year**. For the current rounds the benchmark percentages are **75%** and **40%**. A **65%** tier for 12–<16-year drugs applies to first agreements for 2030 onward. [SSA §1194(c)](https://www.ssa.gov/OP_Home/ssact/title11/1194.htm). |
| §4: ceiling uses the average current price from non-federal buyers or current net price | WRONG | It uses a statutory **non-FAMP benchmark**, not simply today's average receipts. For 2026: inflation-adjusted 2021 non-FAMP. For 2027 onward: lower of that adjusted historical benchmark and the applicable prior-year non-FAMP, subject to statutory rules for missing 2021 data. Part D comparison is an enrollment-weighted net-price measure. [IRA, §1194(c)](https://www.govinfo.gov/content/pkg/PLAW-117publ169/html/PLAW-117publ169.htm). |
| §4: tax or Medicare/Medicaid withdrawal; therefore all manufacturers signed | WRONG | The sanctions and withdrawal route are real. All selected manufacturers entering agreements does not prove that one motive explains every decision. Distinguish entering negotiation agreements from accepting final MFPs. [CMS program overview](https://www.cms.gov/inflation-reduction-act-and-medicare/medicare-drug-price-negotiation). |
| §4 round 1: 10 drugs; selected 2023-08-29; end 2024-08-01; published 2024-08-15; effective 2026-01-01 | CONFIRMED | All these dates and counts are correct. Change the negotiation-period entry from “late 2023” to **2024-02-01 to 2024-08-01**, with 2023 preparation described separately. [CMS first-round fact sheet](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026). |
| §4 round 2: 15; selected 2025-01-17; published 2025-11-25; effective 2027-01-01 | CONFIRMED | Matches CMS's [second-cycle selection announcement](https://www.cms.gov/newsroom/press-releases/cms-statement-lowering-cost-prescription-drugs) and [2027 negotiated-price fact sheet](https://www.cms.gov/files/document/fact-sheet-negotiated-prices-ipay-2027.pdf). |
| §4 round 3: 15 including first Part B drugs plus Tradjenta; selected 2026-01-27; final offers 2026-09-30; answers 2026-10-31; publish by 2026-11-30; effective 2028-01-01 | CONFIRMED | Correct as completed selection and a scheduled negotiation timetable. **2026-09-30 is an offer deadline**; final responses/publication remain prospective as of this explainer's date. Tradjenta is an additional renegotiation, not one of the 15 newly selected drugs. [CMS 2028 fact sheet](https://www.cms.gov/files/document/factsheet-medicare-negotiation-selected-drug-list-ipay-2028.pdf). |
| §4: annual rounds; up to 20 new drugs per year from 2029 | CONFIRMED | Correct; the selected-drug stock accumulates, subject to exits. [IRA §1192](https://www.govinfo.gov/content/pkg/PLAW-117publ169/html/PLAW-117publ169.htm). |
| §4: names and common uses of first ten drugs | CONFIRMED | All ten selected families are correctly identified, including NovoLog/Fiasp. Indications are examples, not exhaustive lists. [CMS selected-drug table](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices). |
| §4: MFP lasts until a competitor is actually marketed, then removal at a later year's start | CONFIRMED | Broad direction correct. Specify **CMS's bona fide marketing determination**, not FDA approval alone or instantaneous exit. Statute preserves the MFP for a lagged period. [SSA §1192(c)](https://www.ssa.gov/OP_Home/ssact/title11/1192.htm). |
| §4: Stelara, Entresto, Xarelto and NovoLog/Fiasp leave 2027-01-01; Stelara biosimilars launched in 2025 | CONFIRMED | Matches CMS deselection notices and the local MFP file's **2026-12-31** end dates. Stelara's 2025 biosimilar launches are also documented in paper 6. [CMS selected drugs and prices](https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices). |
| §4: Teva decision 2026-08-18 upheld grouping and allowed marketing-test challenge to proceed | CONFIRMED | The opinion upheld same-ingredient grouping and held the bona fide marketing challenge ripe. It did **not** hold the marketing test unlawful. [D.C. Circuit opinion, reproduced by Justia](https://law.justia.com/cases/federal/appellate-courts/cadc/25-5425/25-5425-2026-08-18.html). |
| §4: annual inflation adjustment; Eliquis $231 in 2026 to $237.25 in 2027 per 30 days | CONFIRMED | Both values match the CMS file; adjustment uses CPI-U under statute. Rounded 30-day values need not yield the exact statutory percentage when divided. [SSA §1195(b)](https://www.ssa.gov/OP_Home/ssact/title11/1195.htm). |
| §4: CMS can renegotiate; Tradjenta in round three | CONFIRMED | Correct, but Tradjenta is a **mandatory long-monopoly renegotiation**. Other eligible drugs can be selected using discretionary criteria. [CMS 2028 fact sheet](https://www.cms.gov/files/document/factsheet-medicare-negotiation-selected-drug-list-ipay-2028.pdf). |
| §§4, 6: plan must pay exactly MFP plus dispensing fee | WRONG | Law caps the Part D negotiated price at **no more than MFP plus dispensing fees**. The amount includes patient cost sharing; it is not all paid by the plan. [SSA §1860D-2(d)(1)(D)](https://www.ssa.gov/OP_Home/ssact/title18/1860D-02.htm). |
| §4: upfront access or retrospective refund; default WAC minus MFP | CONFIRMED | Correct as a default **per eligible unit**, with alternative arrangements and 340B nonduplication rules. Refund is not invariably actual acquisition cost minus MFP. [CMS guidance, §§40.4–40.4.4](https://www.cms.gov/files/document/ipay-2028-final-guidance.pdf). |
| §§4, 8: CMS April 2026 fact sheet says average receipt within 21 days of service | CONFIRMED | Matches the fact sheet's reported average. This is **not a guaranteed 21-day deadline**. Manufacturer transmission is due within 14 days after receiving the MTF data; bank settlement can follow. [CMS pharmacy fact sheet](https://www.cms.gov/files/document/pharmacy-dispensing-entity-mtf-fact-sheet.pdf). |
| §9: MTF is the contractor routing refunds | WRONG | MTF comprises data exchange and a payment mechanism. Manufacturers can pay outside its optional payment module. “CMS's system for exchanging eligible claim data and facilitating refunds” is more accurate. [CMS pharmacy fact sheet](https://www.cms.gov/files/document/pharmacy-dispensing-entity-mtf-fact-sheet.pdf). |

### List-price cuts, PBMs, pharmacies and the project's results

| Location and claim | Status | Check, correct value or qualification; evidence |
|---|---|---|
| §§5, 6, 8: 2026-01-01 cuts Eliquis 43%, Jardiance 44%, Farxiga 37%, Fiasp 75%; Januvia 42% in January 2025 | CONFIRMED | Supplied results: **43.0%, 44.4%, 37.0%, 75.0%, 42.4%** respectively; Januvia **2025-01-01**. These are WAC-related NADAC adjustments, supported by independent WAC reporting. NCPA's **2025-12-10** alert establishes announced dates, not every percentage. [NCPA alert](https://ncpa.org/wac-decreases-coming-take-action-now); [project tables](../../pharma/outputs/ira/summary.md). |
| §6: related Boehringer combination drugs cut 44% on the same day | CONFIRMED | Synjardy, Glyxambi and Trijardy entries: **44.4%, 2026-01-01** in supplied tables. Do not imply all are outside the broader future negotiation cohorts. |
| §5: deductible/coinsurance patients pay less; flat-copay patients unchanged; uninsured cash patients pay less | WRONG | These are conditional, not universal results. Savings require a lower applicable negotiated or cash price and depend on deductible, benefit cap, assistance and contract terms. A flat copay may fall if the drug price is lower than the copay. [MedPAC chapter 13](https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch13_MedPAC_Report_To_Congress_SEC.pdf); no patient-payment data were analyzed here. |
| §5: employer/insurer net costs may barely change as rebates shrink | CONFIRMED | A possible mechanism, already appropriately conditional. The size and even direction of the net change require contract-specific rebates and payments. |
| §5: PBMs often lose income from list-price cuts | COULD NOT CHECK | Contracts may create that exposure, but the cited evidence does not measure how often PBM revenue or profit fell after these 2026 cuts. Gross rebate receipts are not identical to retained income. |
| §§5, 8: Han, January 2024 inhaler cuts, generic share +23 points overall, +33 commercial, +24 Medicare | CONFIRMED | Paper 13 supports these rounded **percentage-point** estimates. Weakening rebate incentives is a proposed explanation; confidential rebates were not observed. Replace the assertion that this mechanism was demonstrated. |
| §5: Medicaid rebates fall, so net cost may not fall much | WRONG | It omits an important possible direction: **net Medicaid cost can increase** when inflation rebates fall by more than acquisition/reimbursement prices. The basic rebate also depends on best price, not just a fixed percentage. [CMS formulas](https://www.medicaid.gov/medicaid/prescription-drugs/medicaid-drug-rebate-program/unit-rebate-amount-calculation). |
| §5: 340B entities lose penny pricing after a list-price cut | WRONG | Not automatic for every drug or entity. AMP and rebate calculations determine the result; a smaller inflation rebate **can raise** the ceiling despite a lower WAC. The penny floor is per unit. [340B regulation](https://www.ecfr.gov/current/title-42/chapter-I/subchapter-A/part-10/subpart-B/section-10.10). |
| §§5, 8: PORH notice 2026-06-26, effective 2026-07-01; packages $245, $113.83, $120.05 and $166.38 | CONFIRMED | The [notice](https://www.porh.psu.edu/important-update-announced-about-340b-pricing-and-savings-on-five-common-drugs/) reports **Eliquis $245; Farxiga $113.83; Jardiance and Synjardy $120.05 each; Linzess $166.38**, on the stated dates. Present these as that office's reported package prices. |
| §5: verification boundary for the underlying 340B package-price examples | COULD NOT CHECK | The notice supplies neither complete NDC/package identifiers nor confidential AMP/URA inputs. Public attribution can be checked; the underlying ceiling-price calculation cannot be replicated from it. |
| §5: pharmacies buy cheaper and necessarily lose margins; manufacturers mostly give up already-rebated revenue | WRONG | Lower acquisition prices can reduce cash needed for inventory; margin and manufacturer net-revenue effects depend on reimbursement, rebates, fees and refunds. The project does not measure them. Paper 11 and grey D are projections, not proof of realized losses for all pharmacies. |
| §§5, 8: Reuters 2026-02-05, BMS says Eliquis cut helps avoid Medicare inflation penalties | CONFIRMED | Verified as a reported company explanation in the Reuters syndicated article. It is not evidence that all manufacturers had the same motive or that the IRA negotiation caused all cuts. |
| §§5, 8: Hernandez 2023, mean 5.4 times NADAC in 2021, some sponsor/drug ratios >10 | CONFIRMED | Paper 7: **50 highest-spending generic drugs, 2021 Q1, stand-alone Part D plans**. Preserve those restrictions. Point-of-sale amounts are not final pharmacy profits after concessions. |
| §5: Hernandez and Dusetzina prove PBM plans paid their own affiliated pharmacies far above cost | WRONG | Neither comparison identifies the receiving pharmacies as PBM affiliates. The affiliation-specific assertion is unsupported by these citations. Paper 7 explicitly distinguishes point-of-sale payments from subsequent pharmacy concessions. |
| §§5, 8: imatinib 2017–2023, acquisition $5310 to $59, POS $8618 to $1602, reductions 99% and 81% | CONFIRMED | Paper 8 supports the values; arithmetic gives **98.9%** and **81.4%**, consistent with rounding. Neither number is a PBM profit measure. |
| §5: CAA 2026 signed 2026-02-03; Part D PBM fee reform in 2028 | CONFIRMED | Public Law **119-75**, §6224: bona fide service fees, delinked from drug prices and rebates, effective **2028-01-01**; pass-through requirements apply. “Flat fees” should not imply one identical fee for every service. [Statute](https://www.govinfo.gov/content/pkg/PLAW-119publ75/html/PLAW-119publ75.htm). |
| §5: all employer-plan rebate pass-through begins in 2029 | WRONG | §6702 applies to covered **ERISA** arrangements for plan years starting on/after **2028-08-03**, with the statutory new/renewed-contract condition. **2029** is the usual first calendar-plan year, not the universal start date or scope. Governmental plans are not generally ERISA plans. [Statute, §6702](https://www.govinfo.gov/content/pkg/PLAW-119publ75/html/PLAW-119publ75.htm). |
| §6: 2025 and 2026 Q1 gross spending, 15/15 comparison cohorts, about 740 other brands | CONFIRMED | Supplied tables contain **10, 15, 15 and 741** drug/family entries. Clarify comparison of **full-year 2025 with preliminary 2026 Q1**, not matched quarters. Gross spending includes dispensing fees and patient contributions. [Project findings](../../pharma/ira_findings.md). |
| §6: median gross spending/claim −64%; all ten ≥30% reductions; comparison changes about +1% | CONFIRMED | Tables: median **−63.7%**; all ten at least **30.4%** lower; fixed-mix comparator changes **+1.5%, +1.2%, +1.1%**. These are not net savings or a causal negotiation estimate. |
| §6: acquisition/MFP ratios 2.2–3.6; Eliquis 1.3, Jardiance 1.65, Farxiga 2.0 | CONFIRMED | Brand-NDC medians: Januvia **2.70**, Xarelto **2.84**, Entresto **2.22**, Stelara **3.32**, Enbrel **3.57**, Eliquis **1.33**, Jardiance **1.65**, Farxiga **2.00**. Unweighted NDC medians, not every pharmacy's cost. Imbruvica has no matched NADAC. The latest source snapshot is labeled **2026-10-21** in tables but was obtained on **2026-10-20**; disclose that source label rather than alleging future observation. |
| §6: NADAC minus MFP is what pharmacies wait to recover | WRONG | It is a **benchmark gap**, not a measured receivable. NADAC pools purchases across payers; refunds depend on eligible claims, the manufacturer's method and 340B treatment. [Project findings](../../pharma/ira_findings.md), consistent with CMS effectuation guidance. |
| §§6, 8: NCPA letter 2026-02-26; >500; 67% wait ≥22 days; 22% >28; 60% use savings; 78% reconciliation problems | CONFIRMED | Grey A: **nearly 510 responses**, survey **2026-02-11 to 2026-02-20**. All percentages match. It is a member survey, not a representative estimate of all pharmacies or proof contradicting CMS's differently measured average. |
| §6: no published all-ten realized-spending study or weekly NADAC/MFP comparison | COULD NOT CHECK | A literature scan can report “we did not identify,” not establish universal absence. The recorded scan had coverage limits. Paper 6 is a Stelara study; the [PORTAL memo](https://eadn-wc03-8290287.nxedge.io/wp-content/uploads/2025/01/PORTAL_Price-Measures-for-UPLs-Memo_Final.pdf) is a point-in-time comparison dated **2024-12-13**, although its URL directory says 2025. |

### Savings, patient effects, innovation and legal claims

| Location and claim | Status | Check, correct value or qualification; evidence |
|---|---|---|
| §§7, 8: CMS round-one 22% and round-two 44% savings | CONFIRMED | Correct headline estimates, but different counterfactual years: **2023** and **2024**. For round two, 44%/$12bn excludes Coverage Gap Discount Program discounts; including them gives **36%/$8.5bn**. [CMS 2026 fact sheet](https://www.cms.gov/newsroom/fact-sheets/medicare-drug-price-negotiation-program-negotiated-prices-initial-price-applicability-year-2026), [CMS 2027 fact sheet](https://www.cms.gov/files/document/fact-sheet-negotiated-prices-ipay-2027.pdf). |
| §§6–8: Jeon 2026, $26.1bn to $23.8bn, $2.3bn/8.8% or about 9% | WRONG | Numbers match paper 1, but **$26.1bn is the historical-policy scenario using the old coverage-gap discount**. The current-IRA-without-negotiation scenario is **$26.2bn**, giving **$2.4bn/9.0%** versus $23.8bn with negotiation. Label the benchmark; neither is realized 2026 spending. |
| §8: Wouters, 8–42% below estimated 2021 net prices; six named countries; insulin exception | CONFIRMED | Paper 4 supports **8% dapagliflozin, 42% sitagliptin**, **2021** estimates, the six countries and insulin exception. **2025** is the journal issue year; online publication was in **2024**, so the differing year in the literature review is not by itself an error. |
| §8: Gabriel 2026, net discounts 15–60%, median 38%; international premium 17–755%, median 108% | CONFIRMED | Paper 9 supports all five values. International comparison uses the paper's **purchasing-power-adjusted MFN-country benchmark**, not an unadjusted universal foreign price. |
| §8: Li 2026, predicted initial offers 32–78% off list and 16–56% off net | CONFIRMED | Paper 10 supports the four endpoints and the distinction between predicted **initial offers** and final negotiated prices. Published in a **2026** issue despite a **2025** DOI/online history. |
| §8: Rome and Kesselheim 2026, 44% versus 22%, improved process and ceilings | CONFIRMED | Paper 14 is a **Perspective**, not a causal decomposition. Those are CMS aggregate modeled savings percentages, not an unweighted mean drug-price discount. Treat proposed explanations as interpretation. |
| §§7, 8: Castle Annals 2026, six drugs, $685/$470 annual savings, 33–49%/26–42%; three drugs hit $2100 | CONFIRMED | Paper 2 models beneficiaries **without low-income subsidies**, constant specified utilization and 2026 plan designs. Six-drug average: **$685 PDP, $470 MA-PD**. Stelara, Imbruvica and Enbrel reach the cap in both scenarios. Insulin excluded because of its separate cap. Not observed savings for every user, and delayed cap attainment can still alter payment timing. |
| §8: Castle JAMA Network Open 2026, 83% Stelara coverage, $8980/fill, about two biosimilars, near-universal coinsurance | CONFIRMED | Paper 6: **82.6%** plan coverage, **$8980** for the evaluated **90-mg prefilled-syringe fill**, mean **2.3** biosimilars, **99.2%** coinsurance among Stelara-covering plans. Affiliated-product coverage finding is supported. These are plan-file comparisons and modeled annual costs. |
| §8: Jain studied all ten and every plan covered every drug | WRONG | Methods study **nine of ten**, excluding Entresto because of the comparator design. Results report **100% enrollment-weighted coverage for the analyzed groups**, not independent verification of every formulation in every plan for all ten. This is also why its result should not be equated with paper 6's 82.6% for a specific Stelara presentation. Paper 12. |
| §8: Jain step therapy rose to 5% on negotiated diabetes drugs, comparators <1%; cost sharing unchanged | WRONG | **5.0% refers to selected SGLT2 inhibitors**. Selected DPP-4 inhibitors had **0%** step therapy. Cost-sharing structures/rates were broadly stable; that does not establish unchanged dollar out-of-pocket payments. Paper 12. |
| §8: RAND February 2024, 2022 data, 33 countries, overall 278% and $2.78, brands 422%, generics 67% | CONFIRMED | Grey C supports the rounded ratios. Specify **brand-name originators** and **unbranded generics**, not all brands/generics. The 33 are OECD comparison countries, not uniformly described by one income category. |
| §8: RAND brand ratio at least 322% after rebate adjustment | WRONG | The report's analytical summary and body give **308%** for the adjusted aggregate originator comparison. The supplied file's cover blurb says 322%, an internal source inconsistency. Use **308%**, supported by the current [RAND report](https://www.rand.org/pubs/research_reports/RRA788-3.html), and flag the discrepancy rather than silently treating the cover as decisive. |
| §8: Rome, Mooney and Kesselheim 2026, 327 drugs >$100m in 2023, 126 with rare indications, 15 potential exemptions | CONFIRMED | Paper 15 supports every count, threshold and year. “Potentially” is important; this is an eligibility analysis, not a list of actual future selections avoided. |
| §8: Dickson 2019, 271 drugs/16%, $104m in 2017, Humalog largest | CONFIRMED | Paper 17: **271 brand products/NDCs**, **15.9%**, **$103.54m** foregone rebates in **2017**. These are not 271 unique molecules. Humalog is the largest individual contribution. |
| §8: Three Axis January 2025, weekly $10,800, annual $40,000–46,000 | CONFIRMED | Grey D gives **$10,838 weekly**, **$40,279–46,475 annually** under its assumptions. These are preimplementation modeled exposure/revenue effects, not observed shortfalls. |
| §§7, 8: Bhardwaj 2026, LTC revenue net of acquisition cost falls >85% in 2027 | CONFIRMED | Paper 11 supports the projection and year. It concerns selected-drug revenue after acquisition cost, not an 85% drop in all pharmacy revenue or measured profit. |
| §8: ASCP/SCPC release 2025-12-30, 84% service cuts, 78% layoffs | CONFIRMED | The original release supports both percentages and date, as **stated intentions of respondents**. The explainer correctly says these are not measured outcomes. |
| §8: Courtemanche SSRN 2026, $5.73bn in 2027, >$24bn annually within ten years | CONFIRMED | Paper 16 supports **$5.73bn in 2027** and over **$24bn by 2036** in its preferred scenario. Working-paper model, not measured 340B revenue loss. |
| §§7, 8: Schulthess 2025, 161 assets, 68% fall, $2bn to $640m by June 2024 | CONFIRMED | Grey E: selected cohort **161 lead assets**, of which **83 small molecules and 78 biologics**; the 68% describes the small-molecule subset's peak-to-June-2024 investment comparison. Industry-funded and descriptive, as acknowledged in §8. It does not identify an IRA causal effect. |
| §§7, 8: Shanmugam 2026, 643 drugs 2008–2025, 8% growth before and after; no trend change | WRONG | **643, 2008–2025** and pre-IRA **7.82%** are correct. The study found **no statistically significant change**, not exactly equal growth or proof of no effect. Estimated trend change **−3.71%**, 95% CI **−23.60 to 21.36**. Paper 3. |
| §7: Wouters 2024 finds little empirical support for longer biologic protection | CONFIRMED | Accurately reflects the [paper's conclusion](https://jamanetwork.com/journals/jama/article-abstract/2827104). It addresses evidence for differential protection, not a direct estimate of the IRA's eventual innovation effect. |
| §7: Kang 2026 finds stable overall trial activity | CONFIRMED | Correct but incomplete: the [abstract](https://www.healthaffairs.org/doi/10.1377/hlthaff.2025.00720) also reports **fewer trial starts at manufacturers with negotiated drugs**, particularly some cancers. Include both findings; neither alone establishes long-run innovation effects. |
| §7: pharmacies and 340B entities bear the cost | WRONG | Evidence mixes surveys, company/industry reporting and projections. Specify reported cash-flow difficulties and **projected** margin/revenue losses; do not present all as realized or attributable solely to negotiation. |
| §7: courts upheld program; Supreme Court declined challenges on 2026-05-18 | CONFIRMED | The date and denials are supported by the [Supreme Court docket](https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-348.html) and associated cases. Denial of certiorari is **not a merits ruling approving the statute**, and does not dispose of every implementation challenge, including Teva's. |
| §§8–9: publication labels and glossary remainder | CONFIRMED | The 18 supplied papers and five grey documents match their stated publication years, allowing online/issue-year differences noted above. WAC, AWP, MFP, IPAY, rebate, PBM and copay/coinsurance are acceptable shorthand. AMP needs a statutory retail-channel definition; biosimilar means highly similar with no clinically meaningful differences, not an interchangeable chemical generic. |

## Ranked fixes with exact replacement wording

### 1. Correct the ceiling and agreement mechanism in §4

Replace the entire “How the price is set” bullet with:

> **How the price is agreed.** CMS and the manufacturer exchange offers and negotiate an agreed Maximum Fair Price. For the Part D rounds taking effect in 2026–2028, the ceiling is the lower of an enrollment-weighted Part D net-price measure and a percentage of a statutory non-federal manufacturer-price benchmark: 75% for most selected drugs, or 40% for drugs at least 16 years past approval or licensure on January 1 of the applicability year. These are minimum benchmark discounts of 25% and 60%; CMS can negotiate a lower price. The benchmark uses inflation-adjusted 2021 non-FAMP for 2026. From 2027, it generally uses the lower of that historical benchmark and the applicable prior-year non-FAMP. Nonparticipation can trigger substantial sanctions; a manufacturer can instead withdraw the relevant products from Medicare and Medicaid under the statutory process.

Sources: SSA §§1193–1194 and CMS ceiling guidance. This deliberately describes the rounds covered by the explainer; it avoids incorrectly extending their two-tier rule to 2030 onward.

### 2. Correct pharmacy payment, refunds and the NADAC interpretation

Replace §4's pharmacy-payment paragraph with:

> For a selected Part D drug, the negotiated price used at the pharmacy cannot exceed the MFP plus dispensing fees. Patient cost sharing contributes to that amount. The pharmacy may initially buy inventory above the MFP. Manufacturers must provide access to the MFP, either upfront or through retrospective refunds. The default refund is WAC minus MFP per eligible unit, but alternative arrangements and 340B rules can change what is due. The Medicare Transaction Facilitator exchanges claim data; manufacturers may use its payment module or pay separately. CMS's April 2026 fact sheet reports average refund receipt within 21 days of service. That is an observed average, not a guaranteed deadline: manufacturers generally must transmit payment within 14 days after receiving the MTF data.

Replace §6's “That gap is what pharmacies wait to recover through refunds” with:

> This is a gap between a retail invoice-cost benchmark and the MFP, not a measured pharmacy receivable. NADAC does not identify eligible Medicare quantities, actual refunds, 340B treatment or payment dates.

Replace the MTF glossary definition with:

> Medicare Transaction Facilitator: CMS's system for exchanging eligible claim data and facilitating negotiated-price refunds.

Sources: SSA §1860D-2(d)(1)(D), CMS guidance §§40.4–40.4.4 and April 2026 pharmacy fact sheet.

### 3. Make §5's distributional effects conditional and repair Medicaid/340B mechanics

Replace the effects table with:

| Who | Possible effect of a lower list price |
|---|---|
| **Commercially insured patients** | People paying a deductible or coinsurance can save if the price used for their bill falls. The result depends on their benefit, assistance and spending limits. Fixed copays often change less. |
| **Uninsured patients paying cash** | Can save if the pharmacy's cash or discount-card price falls; a lower manufacturer list price does not guarantee that outcome. |
| **Employers and insurers** | A lower gross price can be offset by smaller rebates. Net spending may fall, stay similar or rise, depending on the contract. |
| **PBMs** | Price- or rebate-linked compensation can fall, but fee changes and pass-through terms determine the revenue effect. Han et al. found increased generic inhaler use after 2024 list-price cuts; weaker rebate incentives are a possible explanation, not a directly measured mechanism. |
| **Medicaid** | Smaller basic or inflation rebates can offset the lower price. Net cost can even rise if rebate reductions outweigh the price reduction. |
| **340B hospitals and clinics** | A smaller inflation rebate can raise the 340B ceiling and end penny pricing for some products. The Pennsylvania Office of Rural Health reported package prices from 2026-07-01 of $245 for Eliquis, $113.83 for Farxiga, $120.05 each for Jardiance and Synjardy, and $166.38 for Linzess. These are reported examples, not verified prices for every package or entity. |
| **Pharmacies under negotiation** | Lower invoice prices can reduce the cash needed to buy inventory. Changes in margins depend on acquisition costs, reimbursement, fees and refunds; our data do not measure realized margins. |
| **Manufacturers** | Lower gross receipts can be offset by smaller rebates, discounts or refunds. Bristol Myers Squibb told Reuters on 2026-02-05 that its Eliquis cut helps avoid Medicare inflation penalties. We do not measure the overall net-revenue effect or establish a common motive for all manufacturers. |

Also replace the Medicaid and 340B bullets in §2 with:

> **Medicaid** receives a statutory rebate. For most brand drugs, its basic component is the greater of 23.1% of average manufacturer price (AMP) or AMP minus the manufacturer's statutory best price, plus any inflation rebate. The former cap of 100% of AMP ended on 2024-01-01.
>
> **340B** lets eligible hospitals and clinics buy covered outpatient drugs at a ceiling generally calculated from the preceding quarter's AMP minus the Medicaid unit rebate amount. If that calculation is below one cent, the ceiling is $0.01 per unit, commonly called penny pricing.

Sources: CMS rebate formulas, HRSA ceiling rules, paper 13 and the attributed PORH and Reuters reports.

### 4. Put the savings estimates on explicit baselines

Replace §7's savings bullet with:

> **How much does it save?** These estimates use different comparison years and discount rules. CMS estimated that round-one prices would have reduced 2023 net spending on the selected drugs by 22%. For round two, CMS estimated a 44% reduction against 2024 spending after rebates but excluding coverage-gap discounts; including those discounts gives 36%. Jeon et al. project 2026 selected-drug net spending of $23.8 billion with negotiation versus $26.2 billion under the other IRA rules without negotiation, about 9% less. None of these is a measurement of realized 2026 net savings.

Replace the first two sentences of the Jeon entry in §8 with:

> **Jeon et al. 2026, Value in Health.** Projects $23.8 billion in 2026 net spending on the ten drugs. Compared with a historical-policy scenario retaining the old coverage-gap discount, the estimate is $26.1 billion without negotiation versus $23.8 billion with it, a $2.3 billion or 8.8% reduction. Compared with the current IRA benefit design without negotiation, the estimate is $26.2 billion versus $23.8 billion, a $2.4 billion or 9.0% reduction.

Sources: both CMS savings fact sheets and paper 1's scenario tables.

### 5. Remove the unsupported affiliated-pharmacy inference and specify PBM-law scope

Replace §5's “About PBMs” paragraph with:

> **About PBMs and high prices:** manufacturers set list prices. Some PBM contracts have rewarded large rebates or linked compensation to drug prices, creating incentives that can favor high-list-price products. The cited pharmacy-price studies show a different issue: for the 50 highest-spending generic drugs in stand-alone Part D plans in early 2021, point-of-sale prices averaged 5.4 times NADAC, with some sponsor/drug ratios above ten. Generic imatinib's point-of-sale price fell 81% from 2017 to 2023 while acquisition cost fell 99%. These studies do not identify the receiving pharmacies as PBM affiliates or measure final pharmacy profits after concessions.
>
> The Consolidated Appropriations Act, 2026, signed on 2026-02-03, restricts Part D PBM compensation to bona fide service fees delinked from drug prices and rebates, with pass-through requirements, from 2028-01-01. Separate ERISA provisions require 100% pass-through of specified manufacturer remuneration for covered arrangements in plan years beginning on or after 2028-08-03, subject to the new- or renewed-contract requirements. For calendar-year plans, this generally means 2029.

Sources: papers 7 and 8; Public Law 119-75 §§6224 and 6702. The law is enacted; implementing details were still proposed in [CMS's 2026-10-16 rulemaking](https://www.cms.gov/newsroom/fact-sheets/medicare-program-implementation-sections-6219-6220-6224-consolidated-appropriations-act-2026-cms).

### 6. Clarify selection ages, orphan exclusions and program dates

Replace §4's “Which drugs” bullet with:

> **Which drugs.** CMS selects eligible high-spending drugs without bona fide generic or biosimilar competition. Small-molecule drugs generally must be at least seven years past approval at selection; biologics, eleven years past licensure. Prices take effect later, generally making the earliest effective ages about nine and thirteen years. Starting with the 2028 price year, the expanded orphan exclusion covers drugs whose approved indications are all for designated rare diseases. For initially orphan-only drugs later approved for a non-orphan use, the eligibility clock starts at that first non-orphan approval. Other statutory exclusions also apply. CBO projects that the 2025 orphan-policy change adds $8.8 billion to federal costs over 2025–2034.

Change the round-one negotiation-period cell to:

> 2024-02-01 to 2024-08-01, following 2023 selection and preparation

Replace the sentence immediately after the timetable with:

> The first drugs were selected in 2023, their prices were negotiated and published in 2024, and those prices took effect on 2026-01-01. Round-two prices were negotiated in 2025 and take effect in 2027.

Replace §1's Medicare description with:

> Pays most Part D costs through payments to private plans. The first federal negotiated prices were agreed in 2024 and took effect in 2026.

Replace §4's first duration sentence with:

> A selected drug remains under the program until the statutory exit date following CMS's determination that a generic or biosimilar is being bona fide marketed; competitor approval alone does not end the MFP immediately.

Sources: CMS cycle documents, SSA §1192, the 2025 orphan amendments and grey B.

### 7. Rewrite the Jain summary using the actual analytic sample

Replace the Jain entry in §8 with:

> **Jain & McCoy 2026, Health Affairs Scholar.** Studied nine first-round negotiated drugs and within-class comparators, excluding Entresto. Enrollment-weighted coverage reached 100% for the analyzed negotiated-drug groups in 2026. Step therapy reached 5.0% for the selected SGLT2 inhibitors, compared with under 1% for their comparators; selected DPP-4 inhibitors had no step therapy. Cost-sharing structures and rates were broadly stable, which does not mean patients' dollar payments were unchanged.

Source: paper 12, Methods and results tables. Do not use its abstract's introductory all-ten claim as a replacement for its actual analysis.

### 8. Preserve uncertainty in launch-price and innovation findings

Replace the launch-price bullet in §7 with:

> **Will companies raise launch prices to compensate?** Shanmugam et al. studied 643 new drugs approved during 2008–2025. Prices rose about 7.8% annually before the IRA, and the study did not detect a statistically significant change in the trend afterward. The estimate was imprecise, so it does not establish that the law had no effect.

Replace the Shanmugam entry in §8 with:

> **Shanmugam et al. 2026, JAMA.** Among 643 new drugs approved during 2008–2025, pre-IRA launch prices rose 7.82% annually. The estimated post-IRA change in trend was −3.71%, with a 95% confidence interval from −23.60 to 21.36. The study did not detect a significant change; it did not establish equal growth before and after the law.

Replace the innovation bullet in §7 with:

> **Does it hurt innovation?** Industry-funded work reports a 68% peak-to-June-2024 decline in early-stage small-molecule investment within a selected cohort; this descriptive comparison does not establish causation. Wouters et al. find little empirical support for longer protection of biologics. Kang et al. find stable overall trial activity but fewer trial starts at manufacturers with negotiated drugs, particularly in some cancers. These studies do not settle the law's long-run effect on innovation. The EPIC Act proposal would equalize the small-molecule and biologic selection waiting periods at eleven years.

Sources: paper 3, grey E and the Wouters and Kang abstracts. This wording describes the EPIC proposal, not an independently verified legislative-status claim.

### 9. Repair basic price definitions and NADAC's frequency

Replace price items 1, 2, 3 and 5 in §2 with:

> 1. **List price (WAC, wholesale acquisition cost).** A manufacturer-published benchmark before discounts, not necessarily the amount actually paid in a transaction.
> 2. **Pharmacy acquisition cost.** What the pharmacy pays for inventory. CMS's NADAC uses a monthly survey of retail community pharmacy invoices and publishes weekly per-unit rates, with interim adjustments. In Levy et al.'s 2015 sample, brand NADAC averaged about 99% of WAC.
> 3. **Point-of-sale negotiated price.** The amount recognized for a covered prescription, including patient cost sharing and plan payment. Contract terms determine it; selected drugs are subject to the MFP-based cap.
> 5. **Net price.** A price after specified rebates and discounts. Always say whose net price is meant: manufacturer revenue and a plan's net spending are not the same measure, and neither automatically includes every distribution cost or fee.

Replace §6's NADAC source description and the glossary's NADAC definition with:

> **NADAC:** a monthly survey of retail community pharmacy invoice costs, published as weekly rates per tablet, milliliter or gram and linked to NDCs. The comparison file records reasons for rate changes, including survey updates and WAC changes.

Replace the AMP glossary definition with:

> Average manufacturer price: a confidential statutory measure of manufacturer sales to wholesalers for retail community pharmacy distribution and directly to those pharmacies; used in Medicaid rebates.

Sources: statutory WAC/AMP definitions, CMS NADAC methodology and paper 5.

### 10. Correct the RAND ratio and narrow historical study universes

Replace the RAND entry in §8 with:

> **RAND for ASPE, February 2024.** Using 2022 data for 33 OECD comparison countries, US manufacturer prices averaged 278% of comparison-country prices, or $2.78 per dollar elsewhere. The ratio was 422% for brand-name originators and 67% for unbranded generics. The report's analytical results put the originator ratio at about 308% after its estimated US rebate adjustment; the supplied cover blurb gives an inconsistent 322%.

Replace §2's insulin sentence with:

> For four leading insulin products, gross sales roughly doubled from $13 billion to $27 billion during 2012–2019, while net manufacturer revenue fell about 40%, from $8 billion to $5 billion. This illustrates a widening gross-to-net gap in those products, not the whole insulin market.

In the Dickson entry, replace “271 brand drugs (16%)” with:

> 271 brand products identified by NDC (15.9%)

Sources: grey C's analytical summary/body, Dickson's insulin study and paper 17. Preserve the cover-versus-body conflict in the source record even if the public explainer omits that editorial detail.

### 11. Keep the project's findings descriptive and state their measurement window

Replace §6 finding 1 with:

> **Gross Part D spending per claim fell substantially for the ten selected drug families.** Comparing full-year 2025 with preliminary 2026 Q1, the median change was −63.7%, and every selected family fell at least 30%. Holding the 2025 drug mix fixed, the comparison groups rose 1.5%, 1.2% and 1.1%. The pattern is consistent with the new MFP-based payment cap, but spending per claim also changes with days supplied, strength, formulation and substitution. This descriptive comparison does not isolate negotiation's causal effect. It is before rebates and does not measure net savings; the roughly 9% estimate discussed below is a separate projection.

After the NADAC ratios in finding 3, insert:

> These are unweighted medians across matched brand NDCs in the latest available weekly file, labeled 2026-10-21 and obtained on 2026-10-20. They do not represent every pharmacy's cost, and no NADAC observations matched Imbruvica.

Replace the novelty paragraph with:

> **What appears new in our scan:** as of 2026-10-20, we did not identify a published study measuring realized 2026 spending across all ten drugs or a weekly product-level NADAC-to-MFP comparison through 2026. This was a scoping search, not proof that no such work exists. The closest identified studies examined Stelara alone or compared price benchmarks at one point in time.

Source: supplied findings, summary tables and recorded literature-search scope. The NCPA survey sentence can remain, with “surveyed independent pharmacies” retained.

### 12. Define benefit boundaries and distinguish modeled patient/revenue effects

Replace the Part B/Part D paragraph in §1, and use its first sentence in the glossary, with:

> Part D generally covers self-administered outpatient prescription drugs; Part B covers certain drugs, often administered by a clinician. There are exceptions, so coverage is not determined solely by where a drug is dispensed. Our analysis concerns Part D.

Replace §3's first three bullets with:

> Beneficiaries enroll in a private Part D plan, either separately or through Medicare Advantage. Premiums, deductibles and pharmacy cost sharing depend on the plan, the drug and any subsidy. Some drugs bypass the deductible. Qualifying out-of-pocket spending on covered Part D drugs is capped at $2000 in 2025 and $2100 in 2026; after that threshold, patients owe no further cost sharing for covered Part D drugs that year. Premiums, noncovered drugs and Part B costs are outside this cap.

Replace §3's manufacturer-discount sentence with:

> In 2025, the Manufacturer Discount Program replaced the old coverage-gap discount program, and plans took on more catastrophic-phase liability. Selected drugs are exempt from the new manufacturer discounts while their MFP applies. Studies of 2025 plan designs found higher deductibles and more use of coinsurance.

Replace §7's patient-savings bullet with:

> **Do patients save?** A model using 2026 plan designs for people without low-income subsidies estimated average annual savings across six drugs of $685 in stand-alone plans and $470 in Medicare Advantage drug plans. In the modeled regimens for Stelara, Imbruvica and Enbrel, patients reached the $2100 cap with or without negotiation, so annual direct cost sharing did not fall further. These are projections under specified treatment assumptions, not observed savings for every user.

Replace §7's cost-bearer bullet with:

> **Who may bear costs?** Surveys report pharmacy cash-flow problems and anticipated service cuts. Models project lower selected-drug margins for long-term-care pharmacies and lower net revenue for some 340B entities. These sources do not establish realized losses for every pharmacy or hospital, or attribute every change solely to negotiation.

Sources: Medicare/CMS benefit guidance, paper 2, paper 11, paper 16 and grey A/D.

## Shortcuts taken

This was a fact-check of the explainer, not a rerun of the raw-data analysis. Project numbers were checked against both supplied results files and relevant source metadata; the code and raw claims were not independently recomputed here. Most cited studies were checked in the supplied full texts; Anderson, Zhang, Kang and the biologic-protection paper were checked through publisher or PubMed abstracts. Reuters was checked through syndication, and the Teva opinion through a reproduction of the judicial text. Confidential rebates, actual pharmacy refunds and confidential 340B inputs could not be reconstructed. The novelty claim was assessed as a bounded search claim, not independently proven by an exhaustive new literature review.
