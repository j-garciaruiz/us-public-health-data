# How Medicare drug pricing works, and what the first year of negotiation changed

A plain-language guide for someone new to US drug pricing. Written 2026-10-20 to accompany our analysis ([ira_findings.md](ira_findings.md)) and literature review ([../literature/ira_negotiation_literature_review.md](../literature/ira_negotiation_literature_review.md)). Fact-checked by Codex (GPT-6 Astra) against the full texts and primary sources; its corrections are applied (`reviews/pharma_explainer_codex_astra/report.md`). The papers are summarized one by one in section 8.

---

## 1. The cast of characters

A brand-name pill passes through several hands before it reaches a Medicare patient, and money flows back along a different route.

| Player | What it does |
|---|---|
| **Manufacturer** (Bristol Myers Squibb, Merck, Novo Nordisk...) | Makes the drug and publishes its list price. Pays rebates and discounts afterwards. |
| **Wholesaler** | Buys from the manufacturer, sells to pharmacies. |
| **Pharmacy** | Buys the drug, dispenses it, and is paid by the patient's plan and the patient. |
| **Medicare Part D plan** | A private insurer (a stand-alone drug plan, or a Medicare Advantage plan that includes drugs) that Medicare pays to cover outpatient prescription drugs for older and disabled Americans. Each plan has a formulary: the list of drugs it covers and what patients pay for each. |
| **Pharmacy benefit manager (PBM)** | Runs the drug benefit for the plan: builds the formulary, negotiates rebates with manufacturers, sets what pharmacies are paid. The three largest (CVS Caremark, Express Scripts, Optum Rx) manage about 80% of US prescription volume (Castle et al. 2026, JAMA Network Open) and belong to groups that also own large insurers. |
| **Medicare (the federal government)** | Pays most Part D costs through payments to the private plans. The first federally negotiated drug prices were agreed in 2024 and took effect in 2026. |
| **Patient** | Pays a premium, a deductible, and a copay or a percentage (coinsurance) at the pharmacy, up to an annual cap. |

Part D generally covers drugs patients take themselves (pills, pens, inhalers); Part B covers certain drugs, often given by a clinician (infusions, many cancer drugs). There are exceptions, so coverage is not decided only by where a drug is dispensed. Our analysis concerns Part D.

## 2. One drug, many prices

This is the part that confuses everyone. There is no single "price" of a drug in the United States.

1. **List price (WAC, wholesale acquisition cost).** A price the manufacturer publishes, before any discounts. It is a benchmark, not necessarily what anyone actually pays.
2. **Pharmacy acquisition cost.** What the pharmacy pays for its stock. For brand drugs it is close to the list price: in a 2015 sample, Medicaid's NADAC measure of pharmacy cost averaged about 99% of the list price (Levy et al. 2018). NADAC comes from a monthly survey of retail pharmacy invoices, published as weekly rates.
3. **Point-of-sale price.** The amount the plan and the patient together pay the pharmacy for a prescription, set by contract and usually tied to list-based benchmarks plus a dispensing fee.
4. **Rebates.** After the pill is dispensed, the manufacturer pays the PBM or plan a confidential rebate, often a large share of the list price, in exchange for good formulary placement (a low copay tier, no prior authorization, or excluding a competitor).
5. **Net price.** A price after rebates and discounts. Always ask whose net price: what the manufacturer keeps and what the plan ends up spending are not the same number, and both are confidential drug by drug.

The gap between list and net is large for the drugs in our study. In 2024, rebates cut the gross Part D cost of the first ten negotiated drugs by **nearly 45%**, versus just under 30% for single-source brand drugs overall (MedPAC, March 2026 report, chapter 13). For four leading insulin products the gap grew into a famous "gross-to-net bubble": between 2012 and 2019 their gross sales roughly doubled (about $13 billion to $27 billion) while the manufacturers' net revenue fell about 40% (about $8 billion to $5 billion) (Feldman & Rome 2023, on Dickson et al. 2023).

Other government buyers get their own prices by law:

- **Medicaid** receives a statutory rebate. For most brand drugs the basic part is the greater of 23.1% of the average manufacturer price (AMP) or AMP minus the manufacturer's best price, plus an inflation rebate if the price rose faster than inflation. The former cap of 100% of AMP ended on 2024-01-01 (Dickson 2019; KFF 2024).
- **340B** lets eligible hospitals and clinics that serve many low-income patients buy at a ceiling price, generally AMP minus the Medicaid rebate per unit. If that comes out below one cent, the ceiling is $0.01 a unit: "penny pricing".
- **The VA** (veterans' health system) gets statutory discounts and negotiates directly. In 2016, if Medicare Part D had paid VA prices for the top 50 oral drugs, it would have spent $14.4 billion (44%) less (Venker et al. 2019).

**Why list prices matter even though few pay them:** a patient in the deductible, or paying coinsurance (a percentage), pays a share of a list-based price, not of the secret net price (Socal & Bai 2023). And several payments are computed from manufacturer prices: Medicaid rebates, 340B ceilings, inflation penalties, and in many contracts the PBM's own fees.

## 3. How a Medicare patient pays

- People enroll in a private Part D plan, either separately or through Medicare Advantage. Premiums, deductibles and pharmacy cost sharing depend on the plan, the drug and any low-income subsidy; some drugs skip the deductible.
- Out-of-pocket spending on covered Part D drugs is capped: **$2,000 in 2025 and $2,100 in 2026**. After that, patients owe no more cost sharing for covered Part D drugs that year. Premiums, uncovered drugs and Part B costs are outside the cap.
- In 2025 a new Manufacturer Discount Program replaced the old coverage-gap discount, and plans took on more of the cost of very expensive patients. Drugs with a negotiated price are exempt from the new manufacturer discounts while that price applies. Studies of 2025 plan designs found higher deductibles and more coinsurance (Anderson et al. 2026; Zhang et al. 2026).

## 4. The negotiation program

### What the law does

The Inflation Reduction Act of 2022 lets Medicare negotiate the price of some of its most expensive drugs for the first time. The negotiated price is called the **Maximum Fair Price (MFP)**.

- **Which drugs.** CMS picks high-spending drugs that have no real generic or biosimilar competition. Pills (small molecules) must generally be at least **7 years** past FDA approval when selected, and biologics **11 years** past licensure; prices take effect later, so the earliest effective ages are about 9 and 13 years. From the 2028 price year, a wider orphan exclusion covers drugs whose approved uses are all rare diseases, and for drugs first approved for a rare disease the clock starts at their first non-rare approval. CBO projects that the 2025 change adds **$8.8 billion** to federal costs over 2025–2034 (CBO letter, 2025-10-20). The different clock for pills and biologics is the "pill penalty" debate (section 7).
- **How the price is agreed.** CMS and the manufacturer exchange offers and negotiate. For the rounds taking effect in 2026–2028, the law sets a **ceiling**: the lower of the drug's Part D net price and a fixed share of the manufacturer's average price to non-federal buyers, 75% of it for most drugs (so **at least 25% off**) and 40% for drugs at least 16 years past approval (so **at least 60% off**). CMS can negotiate below the ceiling. A company that refuses faces heavy penalties, or can withdraw its products from Medicare and Medicaid; all the selected companies have signed.

### How often, and when it takes effect

Negotiation is **annual**, and each round takes effect about two years after the drugs are picked.

| Round | Drugs | Selected | Negotiated | Prices published | Prices in effect |
|---|---|---|---|---|---|
| 1 | 10 Part D drugs | 2023-08-29 | 2024-02-01 to 2024-08-01, after 2023 selection and preparation | 2024-08-15 | **2026-01-01** |
| 2 | 15 Part D drugs | 2025-01-17 | during 2025 | 2025-11-25 | 2027-01-01 |
| 3 | 15 drugs, the first Part B drugs, plus Tradjenta renegotiated | 2026-01-27 | during 2026 (final offers 2026-09-30, answers by 2026-10-31) | by 2026-11-30 | 2028-01-01 |
| 4 onward | up to 20 a year | each year | | | from 2029 |

So the first drugs were selected in 2023, their prices were negotiated and published in 2024, and those prices took effect on 2026-01-01. Round-two prices were negotiated in 2025 and take effect in 2027.

The ten round-one drugs: **Eliquis** and **Xarelto** (blood thinners), **Jardiance**, **Farxiga** and **Januvia** (diabetes), **Entresto** (heart failure), **Enbrel** and **Stelara** (autoimmune disease), **Imbruvica** (blood cancer), and the insulin **NovoLog/Fiasp**.

### How long a negotiated price lasts

- A selected drug stays in the program until a legal exit date that follows CMS's finding that a generic or biosimilar is really being marketed; approval of a competitor alone does not end the price. Four of the first ten leave on **2027-01-01**: Stelara (biosimilars launched in 2025), Entresto and Xarelto (generics), and NovoLog/Fiasp. In August 2026 a federal appeals court upheld how CMS groups related products and let Teva continue its challenge to CMS's test of when a generic counts as "marketed", which decides how fast a brand leaves (Teva v. Kennedy, D.C. Circuit, 2026-08-18).
- The price is **adjusted for inflation** each year. In CMS's file, the Eliquis price per 30 days is $231 in 2026 and $237.25 in 2027.
- CMS can **renegotiate** a drug in a later round (Tradjenta in round three).

### How the pharmacy gets the negotiated price

For a selected drug, the price used at the pharmacy (plan payment plus patient cost sharing) cannot exceed the MFP plus dispensing fees. But the pharmacy may have bought its stock at close to the list price. Manufacturers must give access to the MFP, either up front or, usually, through **refunds** afterwards. By default the refund is the list price minus the MFP per eligible unit, though other arrangements and 340B rules can change what is owed. A CMS system, the **Medicare Transaction Facilitator**, exchanges the claim data; manufacturers may pay through it or separately. Manufacturers generally must send payment within 14 days of receiving the data, and CMS reports refunds reaching pharmacies **within 21 days of the date of service on average** (CMS fact sheet, April 2026). That is an average, not a guarantee; pharmacies report longer waits (section 6).

## 5. What a list-price cut does to everyone else

Several manufacturers cut their list prices on 2026-01-01 (Eliquis −43%, Jardiance −44%, Farxiga −37%, Fiasp −75%; Januvia had cut 42% in January 2025). A lower list price is not automatically a lower real price for everyone. The effects depend on contracts and benefit design:

| Who | Possible effect of a lower list price |
|---|---|
| **Commercially insured patients** | People paying a deductible or coinsurance can save if the price used for their bill falls; the result depends on their benefit, any copay assistance and spending limits. Fixed copays usually change less. |
| **Uninsured patients paying cash** | Can save if the pharmacy's cash or discount-card price falls; a lower list price does not guarantee it. |
| **Employers and insurers** | A lower gross price can be offset by smaller rebates. Their net spending may fall, stay about the same or even rise, depending on the contract. |
| **PBMs** | Compensation linked to prices or rebates can fall, but their fee and pass-through terms decide the actual effect. After the 2024 list-price cuts on brand inhalers, generic use rose 23 percentage points (Han et al. 2026); weaker rebate incentives are a possible explanation, not a measured one. |
| **Medicaid** | Smaller basic or inflation rebates can offset the lower price; net cost could even rise if the rebate falls more than the price. |
| **340B hospitals and clinics** | A smaller inflation rebate can raise the 340B ceiling and end penny pricing. The Pennsylvania Office of Rural Health reported package prices from 2026-07-01 of $245 for Eliquis, $113.83 for Farxiga, $120.05 each for Jardiance and Synjardy, and $166.38 for Linzess, up from about a penny. |
| **Pharmacies under negotiation** | Lower invoice prices can reduce the cash tied up while waiting for refunds; margins depend on acquisition costs, reimbursement, fees and refunds, which our data do not measure. |
| **Manufacturers** | Lower gross receipts can be offset by smaller rebates, discounts or refunds. Bristol Myers Squibb told Reuters (2026-02-05) that its Eliquis cut helps avoid Medicare inflation penalties. We do not measure the net effect or a common motive. |

**About PBMs and high prices:** manufacturers set list prices. The criticism of PBMs is that some contracts have rewarded large rebates or tied PBM pay to drug prices, which can favor high-list-price products, while patients' cost sharing follows the list-based price. A related but different problem shows up in pharmacy payments: for the 50 highest-spending generics in stand-alone Part D plans in early 2021, point-of-sale prices averaged **5.4 times** pharmacy acquisition cost, above 10 times for some plan sponsors and drugs (Hernandez et al. 2023); and for generic imatinib, Medicare's point-of-sale price fell 81% from 2017 to 2023 while pharmacies' cost fell 99% (Dusetzina 2024). These studies do not show which pharmacies received the money or their final profits after fees.

Congress responded in the **Consolidated Appropriations Act, 2026** (signed 2026-02-03): from **2028-01-01**, PBMs in Part D may only be paid flat service fees not linked to drug prices or rebates, with rebates passed through to the plans; separate provisions require PBMs to pass 100% of manufacturer rebates and fees through to employer plans, generally from **2029** for calendar-year plans (Sidley summary of the law; CMS's implementing rules were still being proposed in October 2026).

## 6. Our data and what we found

**Data (all free, from the federal government):**

1. CMS **Quarterly Part D Spending by Drug**: total spending and number of prescriptions per drug, full-year 2025 and preliminary first quarter of 2026. Gives spending per claim, **before rebates**.
2. Medicaid's **NADAC**: a monthly survey of retail pharmacy invoice costs, published as weekly rates per tablet, milliliter or gram and linked to product codes (NDCs); plus the **NADAC Comparison** file, which records why each rate changed (survey update or list-price change).
3. CMS's **negotiated-price file**: every product covered, with its MFP per unit and per 30-day supply.

Comparison groups: the 15 drugs negotiated for 2027 (no negotiated price yet in 2026), the 15 selected for 2028, and about 740 other brand-name drugs.

**Findings:**

1. **Gross Part D spending per claim fell substantially for the ten selected drugs.** Comparing full-year 2025 with the first quarter of 2026, the median change was −64%, and every drug fell at least 30%. Holding each group's 2025 drug mix fixed, the comparison groups changed by +1.5%, +1.2% and +1.1%. The pattern fits the new MFP-based payment cap, but spending per claim also moves with days supplied, strength, form and substitution, and this comparison does not isolate the effect of negotiation. It is before rebates: because these drugs already had rebates of about 45%, the real saving is much smaller. One study projects about **9% lower net spending** in 2026 (Jeon et al. 2026); we cannot measure net savings with public data.
2. **Several manufacturers cut list prices on the day negotiated prices started** (Eliquis, Jardiance, Farxiga, Fiasp), and some related drugs that were not negotiated moved with them (Boehringer Ingelheim cut its Jardiance combination pills the same day by the same 44%). Independent price trackers confirm the cuts (NCPA's notice of price cuts; 46brooklyn's January 2026 review).
3. **NADAC stays well above the MFP for most of these drugs.** For Januvia, Xarelto, Entresto, Stelara and Enbrel, NADAC is 2.2 to 3.6 times the MFP; after the cuts, Eliquis is 1.3 times, Jardiance 1.65 and Farxiga 2.0. These are unweighted medians across matched brand products in the latest weekly file (dated 2026-10-21); they do not represent every pharmacy's cost, and no NADAC rows matched Imbruvica. This is a gap between a retail invoice-cost benchmark and the MFP, not a measured amount owed to pharmacies. Separately, in a survey of over 500 independent pharmacies, 67% waited 22 days or more for refunds and 60% drew on savings (NCPA letter to CMS, 2026-02-26).

**What appears new:** as of 2026-10-20 our scoping search did not find a published study measuring realized 2026 spending across all ten drugs, or a weekly product-level comparison of NADAC with the negotiated price through 2026. That is not proof that none exists. The closest studies looked only at Stelara (Castle et al. 2026, JAMA Network Open) or compared price benchmarks at one point in time (PORTAL, 2024).

## 7. The debates around the program

- **How much does it save?** The estimates use different years and rules. CMS estimated that round-one prices would have cut 2023 net spending on those drugs by 22%; for round two it estimated 44% against 2024 spending (36% counting coverage-gap discounts). Wouters et al. argue the 22% overstates savings, partly because negotiated drugs are exempt from the new manufacturer discounts. Jeon et al. project 2026 net spending on the ten drugs of $23.8 billion with negotiation versus about $26 billion without, roughly 9% less. None of these measures realized 2026 net savings.
- **Do patients save?** A model of 2026 plan designs for people without low-income subsidies estimates average annual savings across six drugs of $685 in stand-alone plans and $470 in Medicare Advantage drug plans. For Stelara, Imbruvica and Enbrel, modeled patients reach the $2,100 cap with or without negotiation, so their direct costs do not fall further (Castle et al. 2026, Annals). These are projections, not observed savings.
- **Will companies raise launch prices to compensate?** In 643 new drugs approved 2008–2025, launch prices rose about 7.8% a year before the law, and the study did not detect a significant change in trend afterwards; the estimate is imprecise, so it does not prove the law had no effect (Shanmugam et al. 2026).
- **Does it hurt innovation?** Industry-funded work reports a 68% peak-to-mid-2024 fall in early-stage investment in small molecules within a selected cohort (Schulthess et al. 2025), a descriptive comparison that does not establish cause. Wouters et al. (2024) find little support for giving biologics longer protection; Kang et al. (2026) find stable overall trial activity but fewer trial starts at companies with negotiated drugs. The EPIC Act proposal would give pills the same 11 years as biologics. The long-run effect on innovation is unsettled.
- **Who may bear costs?** Surveys report pharmacy cash-flow problems and planned service cuts, and models project lower margins for long-term-care pharmacies (Bhardwaj et al. 2026) and lower net revenue for some 340B hospitals (Courtemanche 2026). These are surveys and projections, not measured losses for every pharmacy or hospital.
- **Is it legal?** Courts have upheld it so far; the Supreme Court declined to hear the companies' challenges on 2026-05-18.

## 8. What each paper and report says

### Spending, prices and savings

- **Jeon et al. 2026, Value in Health.** Projects $23.8 billion in 2026 net Part D spending on the ten drugs with negotiation. Against a scenario keeping the old coverage-gap discount, spending without negotiation would be $26.1 billion (an 8.8% saving); against the current benefit design without negotiation, $26.2 billion (9.0%). *Why it matters to us:* the best benchmark for how much of our gross drop is a real saving.
- **Wouters et al. 2025, JAMA.** Round-one negotiated prices are 8% (dapagliflozin, the ingredient in Farxiga) to 42% (sitagliptin, in Januvia) below estimated 2021 net prices. Apart from insulin, every negotiated price is still above list prices in six peer countries (Australia, Canada, France, Germany, Switzerland, UK), though the gap narrowed. Argues CMS's 22% savings figure is an overestimate.
- **Gabriel et al. 2026, Journal of Managed Care & Specialty Pharmacy.** Round-two prices are 15% to 60% (median 38%) below estimated US net prices, but 17% to 755% (median 108%) above prices in the "most favored nation" reference countries.
- **Li et al. 2026, Value in Health.** Predicted CMS's initial offers for round two from net prices, comparable drugs and clinical evidence: discounts of 32% to 78% off list and 16% to 56% off net.
- **Rome & Kesselheim 2026, NEJM.** Commentary: round two saves an average 44% versus 22% in round one, because Medicare had its team and processes in place and because of how the ceiling works for older drugs.
- **Venker et al. 2019, JAMA Internal Medicine.** Before the law: Medicare would have saved $14.4 billion (44%) in 2016 on the top 50 oral drugs at VA prices.
- **RAND for ASPE, February 2024.** With 2022 data for 33 OECD countries, US manufacturer prices averaged 278% of prices elsewhere ($2.78 for every dollar); 422% for brand-name originators (about 308% after the report's estimated US rebate adjustment; its summary page says at least 322%); 67% for unbranded generics, which are cheaper in the US.
- **CBO letter, 2025-10-20.** The 2025 widening of the rare-disease exclusion costs $8.8 billion over 2025–2034 (range $6.7 to $10.9 billion), after adding Darzalex, Keytruda and Opdivo to the original $4.9 billion estimate.
- **Rome, Mooney & Kesselheim 2026, Journal of General Internal Medicine.** Of 327 brand drugs with over $100 million Medicare spending in 2023, 126 were approved for at least one rare disease; the 2025 change potentially exempts 15 drugs approved for several rare diseases and delays negotiation for others.

### Patients and plans

- **Castle et al. 2026, Annals of Internal Medicine.** Models 2026 out-of-pocket costs for people without low-income subsidies: average annual savings across six below-cap drugs of $685 (stand-alone plans) and $470 (Medicare Advantage), reductions of 33–49% and 26–42%; Stelara, Imbruvica and Enbrel users reach the $2,100 cap either way. Most plans use coinsurance for these drugs.
- **Castle et al. 2026, JAMA Network Open.** Stelara and its biosimilars in 2026: 83% of Part D plans cover Stelara (gross price $8,980 per fill), most cover about two biosimilars, and nearly all use coinsurance. Because of the cap, out-of-pocket costs are similar across products, so patients have little reason to choose cheaper versions. Plans in the same corporate group as a PBM rarely covered their own affiliated biosimilar.
- **Jain & McCoy 2026, Health Affairs Scholar.** Studied nine of the ten drugs (excluding Entresto) and comparable drugs. Coverage reached 100% for the negotiated drugs analyzed in 2026. Step therapy (try another drug first) reached 5.0% for the negotiated SGLT2 diabetes drugs (Jardiance, Farxiga) versus under 1% for comparators; the negotiated DPP-4 drug had none. Cost-sharing structures were broadly stable.

### List prices, rebates and PBMs

- **Han et al. 2026, Health Affairs.** After manufacturers cut list prices on brand inhalers in January 2024 (when the Medicaid rebate cap ended), generic use rose 23 percentage points (33 in commercial plans, 24 in Medicare). The authors suggest lower list prices left less room for rebate-driven formulary deals.
- **Dickson 2019, JAMA Internal Medicine.** In 2017, 271 brand products (15.9% of those assessed) hit the Medicaid rebate cap, reducing rebates by $104 million; insulin (Humalog) was the largest single case. Context for the 2024 insulin list-price cuts.
- **Hernandez et al. 2023, JAMA.** For the top 50 generics in early 2021, Part D point-of-sale prices averaged 5.4 times pharmacy acquisition cost (NADAC); some sponsors paid over 10 times cost for specific drugs. Uses the same NADAC data and plan pricing files we could use next.
- **Dusetzina 2024, JAMA Internal Medicine.** Generic imatinib: pharmacy cost fell 99% from 2017 to 2023 ($5,310 to $59 per fill), while Medicare's median point-of-sale price fell 81% ($8,618 to $1,602).
- **Levy et al. 2018, Value in Health.** Proposes NADAC as an upper bound and VA prices as a lower bound for net drug costs; in 2015, brand NADAC averaged about 99% of the list price and VA prices about half.

### Pharmacies, 340B and innovation

- **Three Axis Advisors for NCPA, January 2025.** Before the program started, modeled a typical independent pharmacy's weekly cash-flow shortfall at about $10,800 while waiting for refunds, and an annual revenue loss of $40,000 to $46,000 from lost margins on the ten drugs.
- **NCPA letter to CMS, 2026-02-26.** Survey of over 500 pharmacies in the first two months: 67% waited 22 days or more for refunds, 22% more than 28 days, 60% used savings, 78% had trouble reconciling payments.
- **Bhardwaj et al. 2026, JMCP.** Long-term-care pharmacies: projects revenue net of acquisition cost on the selected drugs falling more than 85% in 2027 under its reimbursement and dispensing-fee assumptions.
- **ASCP and SCPC survey, 2025-12-30.** 84% of responding long-term-care pharmacies planned to cut services and 78% to lay off staff (stated plans, not measured outcomes).
- **Courtemanche 2026, SSRN working paper.** Projects that the negotiation program reduces 340B covered entities' net revenue by $5.73 billion in 2027, rising to over $24 billion a year within ten years under preferred assumptions.
- **Schulthess et al. 2025, Therapeutic Innovation & Regulatory Science (Vital Transformation, industry-funded).** In a selected cohort of 161 early-stage assets, small-molecule investment fell 68% from its peak before the law ($2 billion to $640 million by June 2024); a descriptive comparison, not a proven effect.
- **Shanmugam et al. 2026, JAMA.** 643 new drugs, 2008–2025: launch prices rose 7.8% a year before the law; the estimated change in trend afterwards was −3.7% a year with a very wide uncertainty range (−23.6 to +21.4), so no significant change was detected.

### Official and industry documents

- **MedPAC, March 2026, chapter 13.** Rebates cut 2024 gross Part D costs by nearly 45% for the round-one drugs and about 34% for round two; round-two drugs face less rebate competition, so negotiation saves more there.
- **CMS fact sheet on the Medicare Transaction Facilitator, April 2026.** Refunds reach pharmacies within 21 days of the date of service on average.
- **NCPA notice of list-price cuts (December 2025)** and **46brooklyn's January 2026 review**: list the January 2026 cuts and confirm their size.
- **Pennsylvania Office of Rural Health, 2026-06-26.** 340B penny prices ending on 2026-07-01 (section 5).
- **Reuters, 2026-02-05.** Bristol Myers Squibb on why it cut the Eliquis list price.

## 9. Glossary

| Term | Meaning |
|---|---|
| WAC | Wholesale acquisition cost: the published list price, before discounts. |
| AWP | Average wholesale price: an older published benchmark above WAC, still used in some contracts. |
| NADAC | National Average Drug Acquisition Cost: a monthly survey of retail pharmacy invoice costs, published as weekly rates. |
| AMP | Average manufacturer price: a confidential legal measure of what manufacturers receive for drugs sold to retail pharmacies; used for Medicaid rebates. |
| Net price | A price after rebates and discounts; say whose (manufacturer's or payer's). Confidential. |
| Rebate | Money a manufacturer pays back to a PBM, plan or Medicaid after the sale. |
| MFP | Maximum Fair Price: the negotiated Medicare price. |
| IPAY | Initial price applicability year: the year a negotiated price starts (2026, 2027, 2028...). |
| Part D / Part B | Medicare coverage generally of self-administered drugs / of certain drugs often given by a clinician. |
| PBM | Pharmacy benefit manager. |
| 340B | Federal program giving discounted prices to eligible hospitals and clinics serving low-income patients. |
| MTF | Medicare Transaction Facilitator: CMS's system for exchanging claim data and facilitating negotiated-price refunds. |
| Coinsurance / copay | A percentage of the price / a fixed amount, paid by the patient. |
| Biosimilar | A near-copy of a biologic drug (the biologic equivalent of a generic). |
