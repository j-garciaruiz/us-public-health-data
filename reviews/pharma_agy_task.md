# Agy review brief: NADAC starter pull and pharma catalog method (2026-10-20)

You are an independent methods reviewer with an independent recompute. Repository root is your working directory. Write only inside `reviews/pharma_agy_argon/` (create it). Do not edit any other file. No em dashes in what you write. Do not accept website terms, create accounts or log in anywhere.

Use Python (`.venv/bin/python`, pandas available) for computation. Keep your code in `reviews/pharma_agy_argon/`.

## Order matters

Do Part 1 and save `reviews/pharma_agy_argon/recompute.md` **before** opening `pharma/outputs/`, `pharma/scripts/`, `reviews/pharma_codex_astra/` or the "Starter dataset" section of `pharma/README.md`.

## Data

- `data/raw/pharma/nadac/nadac_2026.csv` and `nadac_2025.csv`: CMS NADAC (National Average Drug Acquisition Cost) yearly files from data.medicaid.gov, downloaded 2026-10-20. One row per NDC per weekly snapshot (`As of Date`). Each has a `.meta.json` with source URL and SHA-256.
- Data dictionary and methodology: https://data.medicaid.gov/dataset/fbb83258-11c7-47f5-8b18-5f8e79f7e704 and the NADAC methodology on medicaid.gov (search "NADAC methodology").

## Part 1: independent recompute (blind)

1. Verify the SHA-256 of both files against their sidecars.
2. For 2026: rows, number of snapshots, first and latest snapshot, distinct NDCs, min/median/max NDCs per snapshot, NDCs not 11 digits, duplicate (snapshot, NDC) rows.
3. Latest 2026 snapshot: median NADAC per unit for generics (class G) and brands (class B) with Pricing Unit EA.
4. Which 2026 snapshots are monthly survey refreshes (more than half of NDCs present in both that snapshot and the immediately preceding one have a new `Effective Date`)?
5. Median NADAC per unit across NDCs with these exact descriptions, at the first 2025 snapshot and the latest 2026 snapshot: ATORVASTATIN 20 MG TABLET; METFORMIN HCL 500 MG TABLET; ELIQUIS 5 MG TABLET; JARDIANCE 10 MG TABLET; JANUVIA 100 MG TABLET; XARELTO 20 MG TABLET.
6. For ELIQUIS 5 MG TABLET and JARDIANCE 10 MG TABLET, the snapshot where the median dropped and the size of the drop.

## Part 2: methods (most important)

Read `pharma/README.md` sections "Catalog" and "Things that trip people up" (allowed from the start) and judge, against primary sources (CMS, FDA, medicaid.gov):
- Is NADAC described and used correctly (what it measures, retail community pharmacies only, per pricing unit, survey vs brand WAC-based rates, what monthly refresh vs weekly change means)?
- Are the explanations of NDC 10-to-11-digit normalization, list vs net prices (WAC, AWP, NADAC, ASP, AMP), MFP effectuation, suppression, and Part D vs Part B correct and complete enough for a public health analyst?
- Is "median NADAC across NDCs sharing a description" a sound tracer measure? What would be better (package-weighted, utilization-weighted with SDUD, per-NDC panels)?
- What could make the Eliquis and Jardiance drops misleading (NDC turnover, which NDCs carry the description, brand WAC-based rate method)? Is there a NADAC field or companion dataset that shows the reason for a rate change?

## Part 3: compare

Only after `recompute.md` is saved, open `pharma/outputs/nadac_sanity.md` and `pharma/outputs/nadac_tracers.csv` and report disagreements beyond rounding.

## Output

`reviews/pharma_agy_argon/REPORT.md`: verdict line (PASS / PASS WITH FIXES / FAIL), your numbers, the comparison, and at most 10 methods findings ranked by importance, each with the fix and a primary-source link.
