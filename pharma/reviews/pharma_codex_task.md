# Codex review brief: pharma catalog and NADAC starter pull (2026-10-20)

You are an independent reviewer. Work only inside `reviews/pharma_codex_astra/` (create it). Do not edit anything else in the repository. Repository root: `/Users/hari/Documents/VSC Python/US Data/.claude/worktrees/pharma-data-eae972`. No em dashes in what you write.

## Order matters

Do Part A first and save its output **before** opening `pharma/outputs/`, `pharma/scripts/summarize_nadac.py`, or the "Starter dataset" and "Things that trip people up" sections of `pharma/README.md`. Write your own code (Python with pandas is available at `.venv/bin/python`; or the standard library).

## Part A: recompute NADAC numbers from raw data (blind)

Raw files (CMS NADAC yearly files from data.medicaid.gov, downloaded 2026-10-20):
- `data/raw/pharma/nadac/nadac_2026.csv` and `nadac_2025.csv` (+ `.meta.json` sidecars with source URL and SHA-256)

First confirm the files match their sources: check SHA-256 against the sidecars, and confirm the 2026 row count against the live API (`https://data.medicaid.gov/api/1/datastore/query/fbb83258-11c7-47f5-8b18-5f8e79f7e704/0?limit=1&count=true`).

Then compute, for the 2026 file (one row per NDC per weekly snapshot; snapshot = `As of Date`):
1. Total rows; number of weekly snapshots; first and latest snapshot dates; min, median, max NDCs per snapshot; distinct NDCs in the year.
2. Count of NDCs that are not exactly 11 digits; duplicate (snapshot, NDC) rows; rows with missing or non-positive `NADAC Per Unit`.
3. The snapshots in which more than half of the NDCs (that were also present in the previous snapshot) have a different `Effective Date` from the previous snapshot.
4. Number of NDCs in the latest 2026 snapshot that also appear in the latest 2025 snapshot.
5. Latest snapshot: by `Classification for Rate Setting` x `Pricing Unit`, the count of NDCs and the 10th percentile, median and 90th percentile of NADAC per unit. Also the OTC Y/N counts.
6. Between the last two 2026 snapshots: NDCs in both; NDCs with a new Effective Date; NDCs whose NADAC changed; of those, how many changed by more than 1% and how many increased; NDCs added and dropped.
7. For these exact `NDC Description` values, the median NADAC per unit across NDCs at the first 2025 snapshot, the first 2026 snapshot and the latest 2026 snapshot, and the % change first-2025 to latest-2026: ATORVASTATIN 20 MG TABLET; METFORMIN HCL 500 MG TABLET; LISINOPRIL 10 MG TABLET; AMLODIPINE BESYLATE 5 MG TAB; LEVOTHYROXINE 50 MCG TABLET; ALBUTEROL HFA 90 MCG INHALER; SITAGLIPTIN PHOSPHATE 100 MG TABLET; JANUVIA 100 MG TABLET; ELIQUIS 5 MG TABLET; XARELTO 20 MG TABLET; JARDIANCE 10 MG TABLET; OZEMPIC 1 MG/DOSE (4 MG/3 ML) PEN; LANTUS SOLOSTAR 100 UNIT/ML.
8. For ELIQUIS 5 MG TABLET and JARDIANCE 10 MG TABLET, the snapshot at which the median dropped and the % size of the drop. For JANUVIA 100 MG TABLET and XARELTO 20 MG TABLET, whether any drop occurred in the first four 2026 snapshots.

Save code as `reviews/pharma_codex_astra/recompute_nadac.py` and results as `reviews/pharma_codex_astra/nadac_recompute.md`.

## Part B: compare

Only now open `pharma/outputs/nadac_sanity.md`, `pharma/outputs/nadac_tracers.csv`, `pharma/scripts/summarize_nadac.py`, `pharma/scripts/fetch_nadac.py` and the "Starter dataset" and project-idea 2 text in `pharma/README.md`. List every number that disagrees with yours, which one is right and why. Review both scripts for bugs (e.g. the effective-date shift logic, the tracer pivot labels, the row count in the fetcher, behaviour when the previous year's file is missing).

## Part C: verify the catalog live

`pharma/README.md` has catalog tables claiming, for each source, status, latest period, row counts and access method as checked on 2026-10-20. Re-check every row live today (API calls, HEAD/GET, or opening the page). For each row give: CONFIRMED, WRONG (with the correct value) or COULD NOT CHECK (with the reason, e.g. 403 to scripts). Also check every factual statement in "Things that trip people up" that can be checked against a primary source (NDC padding rules, suppression thresholds, FUL 175% rule, Big Four discount, CA HCAI thresholds, Part D spending excludes rebates, SDUD suppression counts, MFP refund via the Medicare Transaction Facilitator). Flag anything important that is missing from the catalog.

Do not accept any website terms, create accounts or log in anywhere. `cdc.gov` and some other sites block scripts with 403; record those as COULD NOT CHECK rather than wrong.

## Output

`reviews/pharma_codex_astra/report.md` with: (1) verdict line (PASS / PASS WITH FIXES / FAIL), (2) Part A summary, (3) Part B disagreements and script bugs, (4) Part C table, (5) at most 15 findings ranked by severity, each with the fix. Keep it concise.
