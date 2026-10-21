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

## Standing rules
- **Data work gets a triple check (Johnattan, 2026-10-20).** Any analysis that becomes a claim, chart or deliverable is independently replicated by Codex (`gpt-6-astra`, effort high) from raw data, and method-reviewed with an independent recompute by Agy (`gemini-4-argon-high`). Agy's findings are leads, not verdicts: verify each before applying it; Codex is the main cross-family check. Briefs and reports live in the track's `reviews/`; each reviewer writes only in its own folder and sees Claude's code only after producing its own numbers. Report each verdict and any disagreement.
- Census API key is in `.env` (`CENSUS_API_KEY`, git-ignored, activated 2026-10-20). County-wide API pulls need it. Never print it.
- Python: project venv `.venv` (`requirements.txt`). Raw data in `data/raw/` is git-ignored; scripts re-fetch it.
- cdc.gov pages return 403 to curl (bot blocking); they open in a browser.

## Layout change (2026-10-21)
Johnattan asked for symmetric tracks: the atlas files moved from the top level into `atlas/`, and the pharma reviews and literature moved into `pharma/`. The atlas pipeline was re-run afterwards and reproduced all 58 outputs byte for byte. Review reports written before this date cite the old paths; they are dated records and were not rewritten.
