# What researchers have done with CDC PLACES (and what that means for the atlas)

Literature scan for the county chronic disease atlas. Searched 2026-10-20.

**How this was searched.** Consensus (one semantic search before its monthly quota ran out; resets 2026-11-01), OpenAlex (keyword searches plus forward citations of the PLACES reference paper, the main validation paper and the main methods critique), and PubMed E-utilities. Every paper below was confirmed in OpenAlex or PubMed with its DOI; citation counts are OpenAlex's as of the search date. Claims about a paper come from its abstract unless noted (Kong & Zhang 2020 was read in full). This is a scoping scan, not a systematic review.

**Size of the field.** The PLACES reference paper (Greenlund 2022) has 105 citing works in OpenAlex (Consensus reports 214, so OpenAlex undercounts). The MRP validation paper behind PLACES (Zhang 2015) has 184. The literature is large, but most of it uses PLACES as an input; few papers interrogate it.

---

## 1. How PLACES is built and how well it holds up

PLACES estimates come from **multilevel regression and poststratification (MRP)**: a model is fit to BRFSS respondents using individual age, sex, race/ethnicity (and in later versions education) plus county-level poverty, then applied to Census population counts for every small area.

| Paper | What it found | Why it matters for the atlas |
|---|---|---|
| Zhang et al. 2014, *Am J Epidemiol* ([10.1093/aje/kwu018](https://doi.org/10.1093/aje/kwu018)), 223 cites | Introduced the MRP approach with COPD; model vs direct estimates correlated 0.99 at state level, 0.88–0.95 at county level | The founding method paper |
| Zhang et al. 2015, *Am J Epidemiol* ([10.1093/aje/kwv002](https://doi.org/10.1093/aje/kwv002)), 187 cites | External validation against Missouri's own county survey: county correlations of **0.28 for obesity and uninsurance, 0.40 smoking, 0.51 diabetes, 0.69 COPD** | Key fact: agreement at county level is moderate and varies a lot by measure. Some maps deserve more trust than others |
| Wang et al. 2017, *Prev Chronic Dis* ([10.5888/pcd14.170281](https://doi.org/10.5888/pcd14.170281)) | Boston validation: city-level estimates close to the local survey; strong correlation at neighborhood level for most indicators | Supports use at city level |
| Wang et al. 2018, *Prev Chronic Dis* ([10.5888/pcd15.180313](https://doi.org/10.5888/pcd15.180313)) | Adding education and area poverty to the model improved accuracy, especially for smoking | Documents which covariates go into the model (see section 4) |
| Greenlund et al. 2022, *Prev Chronic Dis* ([10.5888/pcd19.210459](https://doi.org/10.5888/pcd19.210459)) | The official PLACES description (29 measures at the time; now 40) | The reference to cite whenever PLACES is used |
| Chien et al. 2018, *Data Sci J* ([10.5334/dsj-2018-008](https://doi.org/10.5334/dsj-2018-008)) | Three different small-area methods for county diabetes agreed only moderately (r 0.60–0.80), but agreed well on which counties are in the top and bottom fifth | Rankings of extremes are more robust than exact values |
| Nielsen et al. 2024, *Am J Prev Med* ([10.1016/j.amepre.2024.02.018](https://doi.org/10.1016/j.amepre.2024.02.018)) | Massachusetts EHR-based estimates were higher and more variable than PLACES for most conditions (differences of 12–40%) | Self-report misses undiagnosed cases; PLACES measures "told by a doctor," not true prevalence |

Related method work: Srebotnjak et al. 2010 (IHME's county diabetes validation framework, [10.1186/1478-7954-8-26](https://doi.org/10.1186/1478-7954-8-26)); Liu et al. 2019 combining NHIS and BRFSS for county cancer measures ([10.5888/pcd16.190013](https://doi.org/10.5888/pcd16.190013)); Kuh et al. 2023 on how hard MRP is to validate ([10.1002/sim.9964](https://doi.org/10.1002/sim.9964)).

## 2. What people use PLACES for

By far the most common design: **link PLACES to another area-level index and test the association**.

| Paper | Design | Note |
|---|---|---|
| Liu et al. 2023, *JAMA Cardiology* ([10.1001/jamacardio.2023.4680](https://doi.org/10.1001/jamacardio.2023.4680)), 61 cites | 71,659 census tracts; CDC Environmental Burden Index + SVI linked to PLACES cardiovascular measures | Top-journal template for the "link an index" design |
| Carlson et al. 2023, *Prev Chronic Dis* ([10.5888/pcd20.230025](https://doi.org/10.5888/pcd20.230025)) | CDC authors merge PLACES COPD with SVI; high-burden, high-vulnerability counties cluster along the Ohio and lower Mississippi rivers; profiles and counts of affected adults | **Closest existing work to the atlas idea**, and descriptive rather than causal |
| Hunyadi et al. 2024, *Am J Prev Med* ([10.1016/j.amepre.2024.08.022](https://doi.org/10.1016/j.amepre.2024.08.022)) | Built a county Chronic Disease Burden Index from 20 PLACES measures (2018–2021) with PCA; hotspots in the South, persistent in Kentucky and West Virginia, rising in Ohio and Texas; strongly tied to SVI | Shows a composite index and change over time are publishable angles |
| Benavidez et al. 2024, *Prev Chronic Dis* ([10.5888/pcd21.230267](https://doi.org/10.5888/pcd21.230267)), 147 cites | ZCTA-level score across 10 chronic diseases, linked to ACS income, insurance, car ownership and distance to hospitals | Very cited despite simple methods: accessible framing travels |
| Lu et al. 2023, *Prev Chronic Dis* ([10.5888/pcd20.230004](https://doi.org/10.5888/pcd20.230004)) | County disability estimates (median 29.5% any disability) with cluster-outlier maps | Example of hotspot mapping on these data |
| Vo et al. 2023, *JMIR Public Health Surveill* ([10.2196/44070](https://doi.org/10.2196/44070)) | 29,126 tracts in 499 cities; SDOH factors vs health outcomes | Typical ecological SDOH analysis |
| Descarpentrie et al. 2025, *JAMA Netw Open* ([10.1001/jamanetworkopen.2025.38377](https://doi.org/10.1001/jamanetworkopen.2025.38377)) | 2024 PLACES tracts; social and behavioral correlates of diabetes in Southern California (large Hispanic population) vs the US | **The Latino-health bridge**: regional contrast with a Hispanic focus |

Other uses seen: environmental justice (asthma/COPD and the Environmental Justice Index, *Lancet Regional Health Americas* 2025, [10.1016/j.lana.2025.101195](https://doi.org/10.1016/j.lana.2025.101195)), historical redlining, greenspace, heat vulnerability, sleep (Pankowska et al. 2023, [10.5888/pcd20.220400](https://doi.org/10.5888/pcd20.220400), 106 cites), stroke correlates (*Ann Neurol* 2024, [10.1002/ana.27039](https://doi.org/10.1002/ana.27039)), and machine-learning "surrogates" that predict PLACES from faster-updating data (Gupta et al. 2026 preprint, [10.48550/arxiv.2607.28655](https://doi.org/10.48550/arxiv.2607.28655)).

## 3. The county-atlas tradition to position against

| Work | What it did |
|---|---|
| Dwyer-Lindgren et al. 2016, *JAMA* ([10.1001/jama.2016.13645](https://doi.org/10.1001/jama.2016.13645)), 290 cites | County mortality trends for major causes, 1980–2014 (IHME) |
| Dwyer-Lindgren et al. 2017, *JAMA Intern Med* ([10.1001/jamainternmed.2017.0918](https://doi.org/10.1001/jamainternmed.2017.0918)), 417 cites | 20-year gap in life expectancy across US counties |
| Dwyer-Lindgren et al. 2022, *Lancet* ([10.1016/S0140-6736(22)00876-5](https://doi.org/10.1016/S0140-6736(22)00876-5)), 263 cites | County life expectancy by race and ethnicity, 2000–19, including Latino populations |
| Chetty et al. 2016, *JAMA* ([10.1001/jama.2016.4226](https://doi.org/10.1001/jama.2016.4226)), 2,803 cites | Income and life expectancy, with local-area variation |
| Remington et al. 2015, *Popul Health Metr* ([10.1186/s12963-015-0044-2](https://doi.org/10.1186/s12963-015-0044-2)), 379 cites | Rationale and methods of the County Health Rankings |

These set the visual and narrative standard US audiences know. The Lancet 2022 paper is the natural partner for any Latino-health extension.

## 4. Cautions in the literature, and the gap

**Kong & Zhang 2020, *AJPH*** ([10.2105/ajph.2020.305611](https://doi.org/10.2105/ajph.2020.305611); full text read 2026-10-20). A four-page commentary on the 500 Cities estimates (the predecessor of PLACES). Xingyou Zhang is also first author of the two CDC method papers above, so this is the method's own builder warning users. Its points:

1. **The estimates are "akin to synthetic estimates."** They give the *expected* prevalence for an area from its age, sex and race/ethnicity mix, area poverty, and unmeasured county and state effects. They are not observed prevalence.
2. **Local context is missing.** Neighborhood factors and local policies are not in the model. Their example: a city whose tobacco policy cut smoking would still get a smoking estimate that is likely "biased upward." A high estimate does not mean something about the place is driving it; it may just mean many high-risk people live there.
3. **The shared-covariate problem, stated directly.** Regressing estimates on the demographic variables used to make them "will result in associations that reflect the group compositional variables used to estimate" them. They add that regressing estimates "on one another (e.g., physical activity with obesity) will also likely reflect significant associations." Using those demographics as controls is acceptable, but their coefficients should not be read as meaningful.
4. **Uncertainty is usually ignored.** Margins of error differ widely by measure, place and scale and are largest in small populations. Secondary analyses rarely model this, so reported standard errors are "more than likely biased," raising false-positive risk. They urge reporting margins of error. (They point to Lewis & Linzer 2005 on regressions where the dependent variable is itself an estimate.)
5. **Validation varies.** It summarizes the evidence in section 1 and adds a Massachusetts EHR comparison (city-level r from 0.65 for obesity to 0.89 for diabetes; Klompas et al. 2017, [10.2105/ajph.2017.303874](https://doi.org/10.2105/ajph.2017.303874)).

It also names the **City Health Dashboard** (NYU Langone with RWJF) as an existing interactive visualization of these data, a direct comparator for the atlas.

**Other documented cautions:** validation is uneven by measure (Zhang 2015), self-report undercounts (Nielsen 2024), and rankings of extremes are more stable than point values (Chien 2018).

**What the gap actually is (revised after reading Kong & Zhang).** The *warning* is not new: Kong & Zhang made it in 2020. I went through all 43 works citing it (OpenAlex, 2026-10-20). None, judging by title and abstract, **measures how large the artifact is**: how much of a given correlation between PLACES measures, or between PLACES and poverty or vulnerability indices, comes from the shared model inputs. Most citing papers mention the caution and then run the regressions anyway. One methods paper is worth reading before claiming the gap: Smith et al. 2025, "Incorporating small-area estimation into mediation analyses with areal datasets" (*Spatial and Spatio-temporal Epidemiology*, [10.1016/j.sste.2025.100735](https://doi.org/10.1016/j.sste.2025.100735); no abstract available in OpenAlex).

So the opportunity is narrower and better defined: the atlas data already shows the pattern (diabetes vs food insecurity r = 0.94 across 2,299 counties; depression vs loneliness only 0.05). An explainer that **shows readers how much of a correlation is left once you remove what the model put in** would turn a 2020 written warning into something people can see. Cite Kong & Zhang as the source of the argument; the contribution is the demonstration.

## 5. Practical notes picked up along the way

- **Archived copies:** ICPSR now holds preservation copies of PLACES releases (e.g. County 2024 release, [10.3886/e240704](https://doi.org/10.3886/e240704)). Useful to cite and as a fallback if CDC pages move.
- **Current release:** the 2025 county release uses BRFSS 2023 for 35 measures and BRFSS 2022 for 5 biennial ones (teeth lost, dental visits, mammograms, colorectal screening, short sleep), with ACS 2019–2023 (CDC dataset metadata).
- **Most-cited outlet:** *Preventing Chronic Disease* (CDC's open-access journal) publishes most PLACES work; a good target if the atlas becomes a paper.

## How this shapes the atlas

1. **Lead with description, not causation**, like Carlson 2023 and the IHME atlases.
2. **Show confidence by measure**: flag weakly validated measures (obesity, uninsurance) differently from stronger ones (COPD, diabetes).
3. **Emphasise top and bottom groups over exact ranks** (Chien 2018).
4. **Make the shared-covariate problem the explainer's centerpiece**: credit Kong & Zhang 2020 for the argument and contribute the visual demonstration of its size.
6. **Show the 95% intervals PLACES publishes** (Kong & Zhang's explicit ask), and look at the City Health Dashboard first so the atlas does something it does not.
5. **Hispanic angle**: Descarpentrie 2025 and Dwyer-Lindgren 2022 give the hook for a Latino-focused layer.
