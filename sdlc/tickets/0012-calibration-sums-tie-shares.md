# 0012 Calibration sums the tie shares

Owner: the queue owner. Status: done 2026-09-25. Record gives the numbers. The ticket review is done: review 1 returned four findings, and all four are taken. It fixes issue `2026-09-25-calibration-counts-a-tie-holding-the-key-as-fully-right.md`.

## Why

`stats.calibration` counts a bin's right answers as the number of truthy credits. A tie of k options that holds the key has credit 1/k. That credit is truthy, so the tie counts as fully right in `ece.tsv` and `calibration.tsv`. `stats.coverage` and `accuracy.tsv` sum the credits. The bench grades the same answer two ways. thinkthen `audit` grades ties at their share from thinkthen ticket 0131 onward. With this fix the bench and audit count a tie the same way.

## Prior evidence

- A local experiment (item 6) found the gap. It ran the bench's own Python on committed runs and made no model call. It gave the 2026-09-23 Jev ECE as 0.0202 now and 0.0182 with shares.
- `scripts/score/analyze.py` builds each calibration pair as `(confidence(r), credit(r))`. `score.credit` returns a float: 1.0, 0.0, or 1/k for a tie that holds the key.
- `analyze.py` writes `k` into the `right` column of `calibration.tsv` as it comes. `accuracy.tsv` writes its `right` as `round(k, 2)`, so it prints `1062.0`.
- `score.py calibration` (`score.buckets`) grades each answer as run with `default()`. A tie there is wrong. `score.py report`, `sweep`, and `history` grade as run too. That report is consistent with itself, and this ticket leaves it alone.
- The author reran `analyze.py`'s tables in memory on the committed runs, with the calibration sum swapped. Only BM25, Word overlap, Hybrid, GLM-5.3 Flash, and Jev move. Embeddings and Laya have no tie that holds the key.
- `tests/test_audit_contract.py` covers no calibration cell. ECE, its interval, and the bins sit under thinkthen issue `2026-09-25-audit-calibration-differs-from-the-benchs-ece-and-its-interval.md`. Its coverage cannot change.
- `reports/results.md` line 27 quotes the ECEs. It also says "A second Jev run over the same questions moved its error by 0.023." That sentence dates from 2026-09-23 (commit 98725536). No committed answer file reproduces it: the old recording's superseded first pass has no answer file. The 2026-09-23 and 2026-09-25 Jev runs are two committed runs over the same 1,501 questions.
- `reports/figures/3-calibration.svg` and `.png` print each model's ECE and interval in the legend and draw the bins with 10 or more answers. `scripts/figures/3_calibration.py` draws it with `kuva`. `kuva` sits in Cargo's bin folder on this machine. The legend formats the four-place `ece.tsv` values with `:.3f`. A stored 0.0305 is a float just below 0.0305, so `:.3f` prints 0.030.
- The talk deck quotes the Jev bin from 0.9 to 1.0 (368 of 378 right), the Jev and GLM ECEs, and the 0.023 sentence. It reads `results/tables/` at build time and checks some cells as strings.

## Change

1. In `stats.calibration`, a bin's right answers are `sum(r for _, r in sel)`. The docstring says the right answers are summed shares, as in `coverage`.
2. `analyze.py` writes the `right` column of `calibration.tsv` as `round(k, 2)`, the same as `accuracy.tsv`.
3. `tests/test_stats.py` gains one edge-case row in the calibration test: a two-way tie that holds the key, with credit 0.5, counts 0.5 in its bin. The same pairs give the same right count in `calibration` and in `coverage`.
4. `scripts/figures/3_calibration.py` rounds each legend value half up from its `ece.tsv` text with `decimal`. GLM's ECE with shares is 0.030549. `ece.tsv` stores 0.0305, and the legend then prints 0.031, the same as `results.md`.
5. Regenerate `results/tables/` with `analyze.py`, offline, from the committed runs. Only `ece.tsv` and `calibration.tsv` may change. Redraw figure 3 with `scripts/figures/3_calibration.py`. No other figure is redrawn.
6. `reports/results.md` line 27 takes the new ECEs and intervals. The unsourced 0.023 sentence gives way to the two committed Jev runs: the 2026-09-23 run's error and the 2026-09-25 run's error, both with shares.
7. Close the issue with a pointer to this ticket.

## Numbers that move

From the in-memory rerun. The record confirms each one against the regenerated tables.

| File | Cell | Old | New |
| --- | --- | --- | --- |
| `ece.tsv` | Jev ece, lo, hi | 0.0277, 0.0123, 0.0437 | 0.023, 0.0084, 0.0389 |
| `ece.tsv` | GLM-5.3 Flash ece, lo, hi | 0.031, 0.024, 0.038 | 0.0305, 0.0236, 0.0376 |
| `ece.tsv` | BM25 ece, lo, hi | 0.6102, 0.59, 0.629 | 0.1573, 0.1396, 0.176 |
| `ece.tsv` | Word overlap ece, lo, hi | 0.6431, 0.6267, 0.659 | 0.1687, 0.1503, 0.1869 |
| `ece.tsv` | Hybrid ece, lo, hi | 0.1466, 0.1227, 0.1722 | 0.0943, 0.0721, 0.1154 |
| `calibration.tsv` | Jev 0.3 to 0.4, right and accuracy | 56, 0.4786 | 51.0, 0.4359 |
| `calibration.tsv` | Jev 0.4 to 0.5, right and accuracy | 70, 0.4605 | 68.0, 0.4474 |
| `calibration.tsv` | GLM 0.2 to 0.3 (n 1) | 1, 1.0 | 0.33, 0.3333 |
| `calibration.tsv` | BM25, Word overlap, Hybrid | four bins each | see the record |
| `results.md` line 27 | Jev ECE and interval | 0.028 (0.012 to 0.044) | 0.023 (0.008 to 0.039) |
| `results.md` line 27 | Jev rerun | moved 0.023; fresh run 0.020 to 0.028 | 0.018 (2026-09-23) to 0.023 (2026-09-25) |
| figure 3 legend | Jev | ECE 0.028, 0.012 to 0.044 | ECE 0.023, 0.008 to 0.039 |
| figure 3 Jev line | points at 0.3 to 0.4 and 0.4 to 0.5 | 0.4786, 0.4605 | 0.4359, 0.4474 |

Every other `right` cell in a bin with answers changes form only, from `368` to `368.0`. Empty bins keep `0`. Its value stays. The Jev bin from 0.9 to 1.0 stays 368 of 378 at 0.9735. GLM's ECE rounds to 0.031 at three places before and after, and its interval stays 0.024 to 0.038. Laya stays 0.160 (0.138 to 0.183). Embeddings stays 0.0651.

## Retained behavior

- Every run folder and recording stays byte for byte. No model call runs. No key is read.
- Every table but `ece.tsv` and `calibration.tsv` stays byte for byte. `git diff --stat results/tables` names only those two.
- `coverage`, `accuracy`, and every other stats function keep their code.
- `score.py calibration` keeps grading as run.
- Figures 1, 2, and 4 to 9 stay byte for byte.
- `tests/test_audit_contract.py` keeps its covered cells and its counts, 7 and 15.

## Proof

- Before any change, `3_calibration.py` redraws figure 3 from the committed tables. The SVG and PNG match the committed files byte for byte, or the record names the `kuva` version and the difference.
- `python3 -m unittest discover -s tests` passes without `THINKTHEN_BIN` and with `THINKTHEN_BIN` set to a local build.
- `./run.sh` passes with `THINKTHEN_API_KEY` and `THINKTHEN_BASE_URL` unset.
- A second `analyze.py` run leaves `git status` clean.
- `git diff --stat main -- results reports` names only `ece.tsv`, `calibration.tsv`, `reports/results.md`, and figure 3's SVG and PNG.
- The record lists every moved cell, old and new, from `git diff` of the two tables.
- `git status` is clean after the suite. A check for uncommitted work lists nothing for this repository.

## Owner's decisions (Ian can overturn each)

- Calibration sums shares, as coverage and accuracy do. A tie that holds the key is 1/k right in every table.
- The `right` column prints as `round(k, 2)`, like `accuracy.tsv`. A whole count reads `368.0`.
- `score.py calibration` keeps grading as run, with the rest of `score.py`.
- The figure legend rounds half up from the table text. `results.md` and the figure then print the same three-place numbers.
- The 0.023 sentence goes. No committed file reproduces it. The two committed Jev runs replace it.
- The talk deck is not edited here. Its repo gets an issue that lists every moved number it quotes and the `368.0` form.

## Deferred

- Moving the contract test onto ECE. It waits on the thinkthen calibration issue and a pinned build with ticket 0131.
- Any rerun.

## Ticket review 1 (fresh reviewer, 2026-09-25): four findings, all taken

1. GLM's 0.030 came from rounding twice. The legend now rounds half up from the table text, and GLM stays 0.031.
2. The figure 3 row names the two Jev points that move.
3. A proof step redraws figure 3 before the change, to show `kuva` alone reproduces it.
4. The trailing clause about `kuva` is split.

## Code review 1 (fresh reviewer, 2026-09-25): two findings, both fixed

The reviewer confirmed the code, the regenerated tables, figure 3, and every moved number. It ran the suite with the pinned binary.

1. The talk deck's issue was not yet filed. It is filed in the deck's repo and pushed.
2. Empty bins keep `0`. The record and this ticket now say so.

## Done when

The proof passes, a fresh reviewer accepts the code, and the branch lands on main and is pushed.
