# US Data: project notes for assistants

Exploration lab for US public health data, building a portfolio for Johnattan's US job search. Two research tracks, each self-contained with its own notes:

- `atlas/` (see `atlas/CLAUDE.md`): CDC PLACES analysis and the expected-vs-observed county health atlas, with its project site.
- `pharma/` (see `pharma/CLAUDE.md`): public US pharmaceutical data, the Medicare drug price negotiation study, catalog, literature and explainer.

Read the track's own `CLAUDE.md` before working in it.

## Layout
```
atlas/      scripts, outputs, site, dist (git-ignored), literature, reviews
pharma/     scripts, outputs, report, literature, reviews, voice_note
data/raw/   all raw downloads for both tracks (git-ignored; scripts re-fetch them)
.venv/      shared Python environment (requirements.txt)
```
Each track keeps its own `scripts/`, `outputs/`, `literature/` and `reviews/`. Scripts in both tracks locate the repository root from their own file path, so they run from any working directory.

## GitHub
Public repository since 2026-10-21 (Johnattan's choice): https://github.com/j-garciaruiz/us-public-health-data, branch `master`, one repo for both tracks. GitHub Pages is off; the site stays local until he asks. Everything pushed is public, so keep secrets, non-open-access full texts and any WONDER count of 9 or fewer out of tracked files.

## Standing rules
- **Data work gets a triple check (Johnattan, 2026-10-20).** Any analysis that becomes a claim, chart or deliverable is independently replicated by Codex (`gpt-6-astra`, effort high) from raw data, and method-reviewed with an independent recompute by Agy (`gemini-4-argon-high`). Agy's findings are leads, not verdicts: verify each before applying it; Codex is the main cross-family check. Briefs and reports live in the track's `reviews/`; each reviewer writes only in its own folder and sees Claude's code only after producing its own numbers. Report each verdict and any disagreement.
- Census API key is in `.env` (`CENSUS_API_KEY`, git-ignored, activated 2026-10-20). County-wide API pulls need it. Never print it.
- Python: project venv `.venv` (`requirements.txt`). Raw data in `data/raw/` is git-ignored; scripts re-fetch it.
- cdc.gov pages return 403 to curl (bot blocking); they open in a browser.

## Layout change (2026-10-21)
Johnattan asked for symmetric tracks: the atlas files moved from the top level into `atlas/`, and the pharma reviews and literature moved into `pharma/`. The atlas pipeline was re-run afterwards and reproduced all 58 outputs byte for byte. Review reports written before this date cite the old paths; they are dated records and were not rewritten.

## Resume here (session of 2026-10-20 to 2026-10-21)
**What happened:** built the atlas track end to end: literature scan (PLACES), shared-covariate test of PLACES, expected-vs-observed analysis against Medicare claims, Census disability and CDC WONDER mortality, the atlas data with reliability smoothing, and a two-page site (project page + interactive atlas) with single-file shareable bundles. Every stage was reviewed by Codex and Agy and the fixes verified by Codex. The pharma track ran in a side session and is merged (see `pharma/CLAUDE.md`). On 2026-10-21 the repository was reorganized into `atlas/` and `pharma/`.

**Decisions locked in (do not relitigate):**
- Atlas design: expected = prediction from county demographics (default, "national") or demographics + state; observed = measured outcomes; differences are descriptive, not performance.
- Triple check on every claim, chart or deliverable; Agy findings verified before use; Codex is the main check.
- Site stays local, not on GitHub Pages, until Johnattan asks (2026-10-21). The repository itself is public on GitHub (2026-10-21).
- WONDER data used under the NCHS agreement accepted 2026-10-20: no counts of 9 or fewer, zero included.

**Open items:**
- Johnattan to review the site and decide how the "How it was checked" section presents the AI-assisted workflow before sharing it with anyone.
- Planned, not built: an explainer on what PLACES can and cannot tell you (html-explainer).
- The "no one has measured this" gap claim from the literature scan still needs a Consensus search (quota resets 2026-11-01) and a read of Smith et al. 2025 before it is stated publicly.
- Known limits: no spatial or out-of-period validation; Connecticut not matched for mortality; Medicare smoothing uses approximate denominators.
- Housekeeping: the merged pharma worktree `.claude/worktrees/pharma-data-eae972` can be removed once Johnattan confirms.

**Next session starts with:** Johnattan's read-through of `atlas/site/index.html` and the framing decision for "How it was checked"; then the PLACES explainer.
