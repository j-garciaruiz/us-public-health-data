# IRA follow-up review

**Verdict: CONFIRMED WITH FIXES**

The revised numbers are confirmed. `replication2.md` was saved before opening the revised results. All 8,542 numeric comparisons passed, covering 781 Part D families, four group summaries, both WAC windows, cut-event details, brand/all-NDC/constant-panel ratios and the weekly chart series. No published table value disagrees beyond floating-point precision. See `comparison_checks.json` and `claim_audit.md` for the complete numerical and statement audit.

Confirmed anchors: 741 Other brands; fixed-weight changes of -61.374% / +1.482% / +1.225% / +1.082% for IPAY 2026 / 2027 / 2028 / Other brands; 2026 selected WAC increases of 13/69 through January and 32/69 through February; brand NADAC coverage of 69 and 70 NDCs. Remaining corrections:

1. **Finding 1, line 19: the headline overstates individual declines.** “About two thirds for all ten” is unsupported. The median is -63.69%, but the combined NovoLog/Fiasp family falls 30.42% and Imbruvica 39.92%. Write: “All ten selected families fell at least 30%; the median decline was 64%.” Explicitly label NovoLog/Fiasp as pooled: separately, named NovoLog products fall 8.78% and Fiasp 72.03%. Prefer a descriptive Part D chart title over one implying that the analysis identifies the MFP effect.

2. **Finding 1, line 19: the explanation does not cover every large comparator decline.** There are 13 such products, not exclusively the named list-price-cut products. Yuflyma(Cf) Autoinjector (-42.01%) and Butalbital-Acetaminophen-Caffe (-30.67%) are also present, without the asserted WAC-cut evidence. Replace “those are products whose manufacturers cut list prices” with “11 of the 13 belong to the listed insulin and empagliflozin-combination products with documented WAC-related cuts.”

3. **Finding 3, line 29: correct the NADAC mechanism and recovery claim.** A national list-price cut is not the only way NADAC can fall: monthly invoice surveys and substantiated Help Desk reviews also update brand rates ([NADAC methodology, p. 23](https://www.medicaid.gov/medicaid-chip-program-information/by-topics/prescription-drugs/ful-nadac-downloads/nadacmethodology.pdf)). Off-invoice refunds do not directly change the original invoice, but an all-payer scope alone does not establish invariance. Delete “a gap like this is what dispensing pharmacies wait to recover”: NADAC minus MFP is not a measured receivable. Default refunds use WAC minus MFP, with alternative arrangements permitted ([CMS guidance, §§40.4–40.4.4](https://www.cms.gov/files/document/ipay-2028-final-guidance.pdf)). Retain the benchmark-gap description and the absence of actual refund/loss measurements.

4. **Name-based limit, line 39: clarify NovoLog Mix's disposition.** It is excluded from the selected family, but both NovoLog Mix 70-30 and FlexPen remain in Other brands and pass the volume filter. Their 2025 claims total 211,862. Say “excluded from selected-family mapping and retained in Other brands.” The implementation follows the revised brief.

5. **Finding 3, line 27: constant-panel equality is rounded equality.** Entresto's October median is 2.215230 across eight NDCs versus 2.217951 across the seven common NDCs. Both display as 2.22. Replace “are the same” with “agree at the displayed precision.”

6. **Two harmless implementation differences remain.** `ira_analysis.py` ends the expanded window on February's last day, including February 29 in 2024, instead of the specified February 28. It also requires an MFP interval covering January 1 for pre-2026 snapshots rather than selecting each NDC's earliest 2026 row. Neither changes the present published results. Use literal February 28 and implement the stated pre-2026 fallback for exact specification compliance.

The remaining figures, payment-rule explanation, WAC dates/product identities, 22% counterfactual, preliminary-quarter caveat, mix decomposition, deselection of four families, noncausal limitations and proposed extensions are supported as qualified in `claim_audit.md`. Qualify the opening assertion that all review fixes have been applied until the corrections above are made.

**Shortcuts taken:** the CMS dataset page returned 403, so its current extraction-timing statement was checked through indexed CMS text. No commercial per-NDC billing-unit crosswalk or claim-level refund data was obtained; aggregate replication does not establish transaction-level concordance.
