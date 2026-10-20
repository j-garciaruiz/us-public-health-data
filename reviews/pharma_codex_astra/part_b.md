# Part B comparison

All 1,152 weekly tracer rows match: keys, counts, units, classes and prices (tolerance 1e-12). All displayed 2026 counts, strata quantiles, overlap, weekly movements, tracer endpoints and percent changes agree at published precision except the median snapshot size: 30,168.5 was truncated to 30,168.

The 2025 file has 1,608,416 records, not 1,608,415. It lacks a terminal newline, so fetch_nadac.py's newline-count-minus-header calculation undercounts by one. Use csv.reader to count records, including a final unterminated record.

The effective-date shift compares to an NDC's last appearance, even across missing weeks. It includes 90 nonadjacent returns across ten snapshots, inflating both numerator and denominator. The ten flagged refresh dates happen to match the correct adjacent-snapshot joins. Full differences: effective_date_comparison.csv. Join each adjacent snapshot pair by NDC instead.

The tracer pivot labels are correct for these inputs: sorted datetime columns match chronological labels. Rename from actual column dates directly, rather than relying on parallel positional labels. With the previous year absent, a sandboxed run succeeds and computes first-to-latest current-year changes correctly (without_previous/). With only one current-year snapshot, weeks.index[-2] raises IndexError; guard this early-year case. No prior-year fallback bug was found.

Price-change increases (14,883) are among all 28,712 changed prices; increases greater than 1% are 10,629. Clarify the two successive 'of which' labels.

Project idea 2's large drops are confirmed: Eliquis 2026-01-14 -42.99898%; Jardiance 2026-01-07 -44.39401%. Januvia and Xarelto are flat in the first four 2026 snapshots; bound that statement to this window, since tiny later decreases do occur. NADAC is acquisition price, not a patient counter price or evidence of an IRA causal effect.
