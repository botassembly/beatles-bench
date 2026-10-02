# Five models on the knowledge questions

Five models and the search baselines on the bench's 1,501 knowledge questions. Each figure is one run, and
the builds differ across rows. The questions ask from memory only. Each cell is the share right with its 95%
Wilson interval. `Against Jev` is the exact McNemar test of the row's run against the Jev run, paired by
question id over the 1,501 questions and scored right or wrong by the scorer's default verdict — a tied pick
counts wrong. Its two counts are the questions only that system answered right, then the questions only Jev
answered right. `python3 scripts/score/table.py` prints the table from [results/tables/](../results/tables/).

| System | Beatles-only (1,313) | Overall (1,501) | Hard (505) | Easy (996) | Against Jev (McNemar) | Run | Build | Date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jev | 67.4% (64.8% to 69.8%) | 70.5% (68.1% to 72.7%) | 56.9% (52.6% to 61.2%) | 77.3% (74.6% to 79.8%) | — | 2026-09-30-all-jev | aec7819bb | 2026-09-30 |
| Liquid d1 | 64.3% (61.7% to 66.9%) | 67.6% (65.1% to 69.9%) | 52.9% (48.5% to 57.2%) | 75.0% (72.2% to 77.6%) | 140 to 191, p = 0.006 | 2026-09-30-all-liquid-d1 | aec7819bb | 2026-09-30 |
| Nimble 9B | 48.0% (45.3% to 50.7%) | 51.9% (49.4% to 54.4%) | 41.6% (37.4% to 45.9%) | 57.1% (54.0% to 60.2%) | 148 to 422, p < 0.001 | 2026-09-30-thinkthen-nimble-9b | aec7819bb | 2026-09-30 |
| Kev 4B | 44.1% (41.4% to 46.8%) | 47.2% (44.7% to 49.8%) | 39.0% (34.8% to 43.3%) | 51.4% (48.3% to 54.5%) | 137 to 481, p < 0.001 | 2026-09-29-thinkthen-kev-4b | 2c5ac772b | 2026-09-29 |
| Laya | 35.0% (32.5% to 37.7%) | 35.8% (33.4% to 38.2%) | 29.9% (26.1% to 34.0%) | 38.8% (35.8% to 41.8%) | 96 to 612, p < 0.001 | 2026-09-23-thinkthen-laya | — | 2026-09-23 |
| GLM-5.3 Flash | 96.2% (95.0% to 97.1%) | 96.7% (95.7% to 97.5%) | 95.4% (93.3% to 97.0%) | 97.3% (96.1% to 98.2%) | 419 to 21, p < 0.001 | 2026-09-23-glm-5.3-flash | chat script | 2026-09-23 |
| *Vector search (question vs. options)* | | | | | | | | |
| BM25 | 33.8% (31.3% to 36.4%) | 35.0% (32.6% to 37.4%) | 29.0% (25.2% to 33.1%) | 38.0% (35.1% to 41.1%) | 65 to 594, p < 0.001 | 2026-09-23-baseline-bm25 | — | 2026-09-23 |
| Embeddings | 37.6% (35.0% to 40.3%) | 39.8% (37.3% to 42.3%) | 33.3% (29.3% to 37.5%) | 43.1% (40.0% to 46.2%) | 104 to 560, p < 0.001 | 2026-09-23-baseline-embed | — | 2026-09-23 |
| Hybrid | 35.9% (33.4% to 38.6%) | 37.5% (35.1% to 40.0%) | 30.8% (26.9% to 34.9%) | 41.0% (38.0% to 44.0%) | 75 to 575, p < 0.001 | 2026-09-23-baseline-hybrid | — | 2026-09-23 |
| Word overlap | 33.2% (30.7% to 35.8%) | 34.2% (31.8% to 36.6%) | 28.7% (24.9% to 32.8%) | 36.9% (34.0% to 40.0%) | 66 to 602, p < 0.001 | 2026-09-23-baseline-overlap | — | 2026-09-23 |
| Chance | 31.4% | 30.6% | 30.3% | 30.8% | | | | |

## The runs

- **Jev** is `jev-1.13.0`, TypeSafe's small model, through the `thinkthen` command on build aec7819bb:
  [`results/runs/2026-09-30-all-jev`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs/2026-09-30-all-jev), a local Linux machine with 16 cores, 2026-09-30. The author of this
  bench builds ThinkThen; weigh its row with that in mind.
- **Liquid d1** is Liquid AI's `d1:free` through `thinkthen --backend liquid`, on the same build and machine
  the same day: [`results/runs/2026-09-30-all-liquid-d1`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs/2026-09-30-all-liquid-d1). It left three questions unanswered at the rate
  limit; they score wrong. An earlier full run of 2026-09-29 on build 2c5ac772b stays as history in
  [`results/archive/runs/2026-09-29-thinkthen-liquid-d1free-full`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/archive/runs/2026-09-29-thinkthen-liquid-d1free-full).
- **Nimble 9B** is the `nimble` model through Ollama 0.35 on an Apple Silicon Mac, reached over a loopback
  SSH tunnel, on build aec7819bb: [`results/runs/2026-09-30-thinkthen-nimble-9b`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs/2026-09-30-thinkthen-nimble-9b), 2026-09-30.
- **Kev 4B** is `kev-latest` on an Apple Silicon Mac at a loopback System One address, on build 2c5ac772b:
  [`results/runs/2026-09-29-thinkthen-kev-4b`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs/2026-09-29-thinkthen-kev-4b), 2026-09-29.
- **Laya** is `laya-mlx`, a small Jev-like model served by a local shim on an Apple Silicon Mac, reached over
  an SSH tunnel: [`results/runs/2026-09-23-thinkthen-laya`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs/2026-09-23-thinkthen-laya), 2026-09-23. The run predates the run.txt record,
  so the table shows no build; the bench's pinned build of that day was thinkthen main 02dc0b96.
- **GLM-5.3 Flash** is the reference chat model from Z.ai, `glm-5.3-flash` with thinking off and no search
  tool, asked through `scripts/run/chat.py` rather than a thinkthen build:
  [`results/runs/2026-09-23-glm-5.3-flash`](https://github.com/botassembly/beatles-bench/blob/a6a6be71/results/runs/2026-09-23-glm-5.3-flash), 2026-09-23.

## The hard set

The hard set is the 505 question ids in [questions/hard.txt](../questions/hard.txt), the set experiment 413
picked: the lexical traps and their controls, the multi-hop questions, the none-of-these questions, the
reversal questions, the shared-lead questions, and the year questions of `forward`. The other 996 questions
are the easy set.

## Read next

- [results.md](results.md): every category, the function suite, and the costs.
- [baselines.md](baselines.md): the four search baselines and how they score.
