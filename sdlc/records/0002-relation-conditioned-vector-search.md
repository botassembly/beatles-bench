# 0002 Give vector search a fair try with relation-conditioned queries

Ticket: [0002](../tickets/0002-relation-conditioned-vector-search.md). Branch `ticket/0002-relation-vectors`. Built 2026-09-24 by the builder on a local machine.

## What landed

- `scripts/run/relation_vectors.py` draws the sample, types the options, checks each query for leaks, and scores the 20 questions four ways. `run` writes the results and `table` prints them.
- `tests/test_relation_vectors.py` covers the seeded draw, the leak checks, the exact Qwen strings, the yes score from fake logits, and the verdict rule. It loads no model.
- `results/runs/2026-09-24-relation-vectors/` holds `sample.json`, `scores.jsonl` (every query, typed option, and score), and `times.json`. The file is `scores.jsonl` because `tests/test_run.py` expects every `answers.jsonl` to answer the whole bench.
- `reports/baselines.md` gains the section "Relation-conditioned queries".
- `README.md` drops the vector search row and says why, as the verdict rule requires.
- `requirements.txt` pins torch 2.14.0 from the CPU index, transformers 5.17.0, and sentence-transformers 6.1.0. `scripts/README.md` gives the install command.

## Decisions (the owner can overturn these)

- A single songwriter is typed "NAME, a songwriter". The ticket's "NAMES, songwriters" stays for "John Lennon and Paul McCartney".
- The leak check removes the question's own title before it looks for the answer. A song that shares its album's title then still passes.
- The relation question is the query for all three new methods. The bge query gets no bge instruction prefix, to keep the model as the baseline runs it.

## Commands and results

- Red: `python3 -m unittest tests.test_relation_vectors` failed with the module missing.
- Green: the same command ran 13 tests, OK.
- Model card check: the embedding scorer gave 0.7646, 0.1414, 0.1355, and 0.6000 on the card's example, matching the card. The reranker scored the card's matching pairs 0.9995 and 0.9994 and the mismatched pairs below 0.0001.
- Run: `BENCH_THREADS=4 nice -n 19 .venv/bin/python scripts/run/relation_vectors.py run` finished in 105.7 s with the one-minute load at 4.2.
- `python3 scripts/run/relation_vectors.py table` printed the table in the report. Plain gave the baseline's answer on all 20.
- Full suite: `python3 -m unittest discover -s tests` ran 169 tests, OK, 8 skipped.

| Method | Gained on the wrong ten | Lost on the right ten | Net | Load and score s |
| --- | --: | --: | --: | --: |
| Relation wording | 2 | 5 | -3 | 7.5 |
| Instructed embedding | 2 | 7 | -5 | 19.2 |
| Reranker | 3 | 9 | -6 | 62.4 |

Verdict: no method clears the bar. Vector search leaves the README table.

## Open

- The deck lives outside this repo. Its owner drops vector search there.
- `reports/figures/` and `reports/results.md` still draw embeddings as the baseline. They report a measured result, so they stay.
- Code review: a fresh reviewer returned ACCEPT at an earlier commit. It checked the reranker prompt, token ids, left padding, and batching against the model card, and found the George sweep comes from the model. A rerun of the bge relation arm with the card's query prefix gave the same 2 and 5. The 13 new tests passed.
