# 0012 Calibration sums the tie shares: record

Built on 2026-09-25 on `ticket/0012-calibration-sums-tie-shares` from main at an earlier commit. No model call ran. No key was set or read.

## Result

- `stats.calibration` sums each bin's shares. A tie of k options that holds the key counts 1/k, as in `coverage` and `accuracy.tsv`.
- `analyze.py` writes the `right` column of `calibration.tsv` as `round(k, 2)`. Every whole count now prints with `.0`, as in `accuracy.tsv`.
- `3_calibration.py` rounds each legend value half up from its `ece.tsv` text. GLM's ECE with shares is 0.030549. The legend and `results.md` both print 0.031.
- `tests/test_stats.py` gains a two-way tie that holds the key. It counts 0.5 in calibration and in coverage.
- `analyze.py` regenerated `results/tables/` from the committed runs. Only `ece.tsv` and `calibration.tsv` changed. Figure 3 was redrawn. Before the change, a redraw from the committed tables matched the committed SVG and PNG byte for byte.
- `tests/test_audit_contract.py` covers no calibration cell. Its coverage did not change: 7 question files for Jev and 15 for Laya.

## Numbers that moved

`ece.tsv`:

| System | Old ece, lo, hi | New ece, lo, hi |
| --- | --- | --- |
| Jev | 0.0277, 0.0123, 0.0437 | 0.023, 0.0084, 0.0389 |
| GLM-5.3 Flash | 0.031, 0.024, 0.038 | 0.0305, 0.0236, 0.0376 |
| BM25 | 0.6102, 0.59, 0.629 | 0.1573, 0.1396, 0.176 |
| Word overlap | 0.6431, 0.6267, 0.659 | 0.1687, 0.1503, 0.1869 |
| Hybrid | 0.1466, 0.1227, 0.1722 | 0.0943, 0.0721, 0.1154 |

Embeddings (0.0651) and Laya (0.1602) have no tie that holds the key. They stay.

`calibration.tsv`, bins whose value moved:

| System | Bin | n | Old right, accuracy | New right, accuracy |
| --- | --- | --- | --- | --- |
| Jev | 0.3 to 0.4 | 117 | 56, 0.4786 | 51.0, 0.4359 |
| Jev | 0.4 to 0.5 | 152 | 70, 0.4605 | 68.0, 0.4474 |
| GLM-5.3 Flash | 0.2 to 0.3 | 1 | 1, 1.0 | 0.33, 0.3333 |
| BM25 | 0.1 to 0.2 | 133 | 133, 1.0 | 15.79, 0.1187 |
| BM25 | 0.2 to 0.3 | 654 | 654, 1.0 | 163.5, 0.25 |
| BM25 | 0.3 to 0.4 | 91 | 91, 1.0 | 30.33, 0.3333 |
| BM25 | 0.5 to 0.6 | 127 | 78, 0.6142 | 64.5, 0.5079 |
| Word overlap | 0.1 to 0.2 | 133 | 133, 1.0 | 15.79, 0.1187 |
| Word overlap | 0.2 to 0.3 | 657 | 657, 1.0 | 164.25, 0.25 |
| Word overlap | 0.3 to 0.4 | 83 | 83, 1.0 | 27.67, 0.3333 |
| Word overlap | 0.5 to 0.6 | 113 | 106, 0.9381 | 54.0, 0.4779 |
| Hybrid | 0.1 to 0.2 | 133 | 23, 0.1729 | 20.5, 0.1541 |
| Hybrid | 0.2 to 0.3 | 877 | 332, 0.3786 | 285.5, 0.3255 |
| Hybrid | 0.3 to 0.4 | 127 | 72, 0.5669 | 64.0, 0.5039 |
| Hybrid | 0.5 to 0.6 | 137 | 91, 0.6642 | 69.5, 0.5073 |

Every other `right` cell in a bin with answers changed form only, as in `368` to `368.0`. Empty bins keep `0`. The Jev bin from 0.9 to 1.0 stays 368 of 378 at 0.9735.

Figure 3: the Jev legend moved from "ECE 0.028, 0.012 to 0.044" to "ECE 0.023, 0.008 to 0.039". The Jev line moved at its 0.3 to 0.4 and 0.4 to 0.5 points, as in the table. The GLM and Laya legends and lines stay. GLM's moved bin holds one answer and is not drawn.

`reports/results.md` line 27:

- Jev ECE 0.028 (0.012 to 0.044) became 0.023 (0.008 to 0.039).
- GLM stays 0.031 (0.024 to 0.038). Laya stays 0.160 (0.138 to 0.183).
- "A second Jev run over the same questions moved its error by 0.023" is gone. No committed answer file reproduces it. "The fresh run of 2026-09-25 moved it from 0.020 to 0.028" became "Two Jev runs over the same questions give 0.018 (2026-09-23) and 0.023 (2026-09-25)." Both are computed with shares.

## Checks

- `python3 -m unittest discover -s tests` passes with no key: without `THINKTHEN_BIN`, and with `THINKTHEN_BIN` set to a local build.
- `./run.sh` with the key and address unset and `THINKTHEN_BIN` set to the pinned binary exits 0. Its `analyze.py` run left `git status` unchanged.
- `git diff --stat main -- results reports` names only `ece.tsv`, `calibration.tsv`, `reports/results.md`, and figure 3's SVG and PNG.

## Gaps

- The talk deck quotes the Jev ECE, the 0.023 sentence, and the Jev top bin as the string `368`. The talk deck's repo tracks the moves in `sdlc/issues/2026-09-25-bench-calibration-numbers-moved.md`.
