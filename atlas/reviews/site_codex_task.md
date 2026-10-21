Read reviews/site_brief.md. Your folder: reviews/site_codex_astra/.

Check, with your own code:
1. Number fidelity: every number shown on index.html (including those computed in site/assets/index.js from site/data/findings.js: the big percentage, the 2.3 points, chart values, the Caddo/Iberia/Staten Island/Brooklyn examples, 34 outcomes, 3,144 counties) and in the atlas (tooltips, details, extremes lists, table) must trace to the reviewed outputs. Recompute them independently from the output CSVs and compare. Check export_site_data.py for bugs (county alignment to geometry order, null handling, rounding, mode/tier mapping, medicare_std without shrinkage).
2. Claims: is every sentence on index.html supported by the reviewed results and the review summaries? Flag overclaims (for example about what the residuals mean, what PLACES is "good for", the "rebuilt from demographics" headline, the process description of how the work was checked) and suggest exact replacement wording.
3. NCHS data use rule: no mortality value based on 9 or fewer deaths may be shown or recoverable from any file in site/ (including from SMR x expected deaths).
4. Atlas behaviour: run it in a headless browser if you can (Playwright is in .venv; use chromium-headless-shell, never the real Chrome). Check that outcome switching, the three views, both comparison modes, smoothing and fading toggles, search, pinning from the URL hash, the extremes lists and the table work and show consistent values; check the color scales (diverging centered at zero; the sequential scale shared by measured and expected), the legend, and missing-data hatching. Report JavaScript errors.
5. Basic accessibility and robustness: keyboard access, labels, contrast of text, behaviour when opened from disk (file://), console errors.

At most 10 findings, most important first, each with file:line and a concrete fix. Write reviews/site_codex_astra/REPORT.md with pass/fail per check, findings, and "Shortcuts taken".
