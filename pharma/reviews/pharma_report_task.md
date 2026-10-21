# Review brief: project report HTML (2026-10-20)

Fact-check `pharma/report/index.html` (built by `pharma/scripts/build_report.py` from `pharma/report/template.html` and `pharma/report/prereg_note.html`). Work only in `reviews/pharma_report_codex_astra/`. No em dashes. Do not commit. Do not edit anything outside your folder. Never download or open any 2027 plan pricing or 2027 outcome data.

## Check
1. Every number and factual statement in the rendered page text (prose, hero figures, tables, captions, tooltips built from the embedded JSON) against its source: `pharma/outputs/` (ira, spuf, prereg_2027), `pharma/ira_findings.md`, `pharma/prereg_2027.md` (including Amendments 1 and 2), `literature/ira_negotiation_literature_review.md`, `literature/ira_notes/*.md`, the full texts in `literature/ira_fulltext/text/`, and public primary sources where needed (CMS, MedPAC, NCPA pages). List every mismatch, overstatement or unsupported claim, with the correct wording.
2. Does the page ever imply net savings, causation, or a stronger result than the findings support?
3. Do the summary of the 2027 predictions and of the amendments in the page match `pharma/prereg_2027.md` exactly (no registered number or band misstated)?
4. Charts: does each chart encode the data it claims (axis, units, groups, snapshot labels)? You may render the page headlessly (for example with `uv run --no-project --with playwright==1.58.0`; Playwright's chromium-headless-shell is installed) and inspect screenshots.
5. Links: do the data and DOI links resolve to the stated items?

## Output
`report.md` in your folder: verdict (PASS / PASS WITH FIXES / FAIL), then findings ranked (at most 15), each with location in the page, the problem, the evidence and the exact replacement text.
