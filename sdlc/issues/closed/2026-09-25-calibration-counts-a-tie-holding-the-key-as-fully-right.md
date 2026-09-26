# Calibration counts a tie holding the key as fully right

Status: Closed 2026-09-25. Ticket 0012 fixed it: `stats.calibration` sums the shares, as `coverage` does. `ece.tsv`, `calibration.tsv`, figure 3, and `reports/results.md` are regenerated. `sdlc/records/0012-calibration-sums-tie-shares.md` lists every moved number.

Found by ThinkThen ticket 0131's writer on 2026-09-25, in experiment 263 (`experiments/263-audit-vs-bench-methods/`, item 6). The experiment ran the bench's own Python on committed runs. It made no model call.

`calibration` in `scripts/score/stats.py` counts a bin's right answers as the number of truthy credits (`sum(1 for _, r in sel if r)`). A tie of k options that holds the key has credit 1/k, which is truthy. So it counts as fully right in `ece.tsv` and `calibration.tsv`. `stats.coverage` sums the shares instead. The two tables grade the same answer two ways.

With the shares summed in calibration, these errors change:

| Run | ECE now | ECE with shares |
| --- | --- | --- |
| Jev | 0.0202 | 0.0182 |
| GLM | 0.0310 | 0.0305 |
| BM25 baseline | 0.6102 | 0.1573 |

## Fix

Sum the credits (`sum(r for _, r in sel)`) in `calibration`, as `coverage` does. Then recapture `ece.tsv` and `calibration.tsv`, and check every page and slide that quotes an ECE. ThinkThen `audit` grades ties at their share from ticket 0131 onward. The two tools then agree.
