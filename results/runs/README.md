# Run names

Each folder here is one run, named `DATE-LABEL`. The date is the day the run asked its questions. The label says which system answered which questions. `python3 scripts/score/score.py newest LABEL` prints the newest folder of a label, and `scripts/score/analyze.py` scores only that one. Superseded runs sit in [../archive/runs/](../archive/runs/). The Jev one-line run of 2026-09-24 stays here, because it pairs with the Laya one-line run of that day.

| Label | System | Questions | Report |
| --- | --- | --- | --- |
| `thinkthen-jev` | Jev through the `thinkthen` command | the 1,501 questions in `questions/` | [results.md](../../reports/results.md) |
| `thinkthen-jev-open-book` | Jev with the 306-song catalog before each question (`catalog.txt`) | 196 sampled questions (`ids.txt`) | [open-book.md](../../reports/open-book.md) |
| `thinkthen-jev-rad` | Jev answers from the top catalog sections a pick ranks: Jev's own `choose`, BM25, or MiniLM | the same 196 | [rad.md](../../reports/rad.md), "Results" |
| `thinkthen-jev-rad2` | the same, with the options in the pick text and a fallback cut tuned on one half | the same 196, split into a tune half and a held-out half (`split.tsv`) | [rad.md](../../reports/rad.md), "Second test" |
| `thinkthen-jev-one-line` | Jev with one song's catalog line as context | 38 lead-singer questions of the open-book sample (`questions.jsonl`) | [open-book.md](../../reports/open-book.md), "One line for Laya" |
| `thinkthen-laya-one-line` | Laya with the same one line | the same 38 | [open-book.md](../../reports/open-book.md), "One line for Laya" |
| `thinkthen-laya` | Laya, a small local model, through the `thinkthen` command | the 1,501 | [results.md](../../reports/results.md), "Laya" |
| `glm-5.3-flash` | GLM-5.3 Flash through `scripts/run/chat.py` | the 1,501 | [results.md](../../reports/results.md) |
| `functions-jev` | Jev on the function suite | `questions/functions/` | [results.md](../../reports/results.md), "The function suite" |
| `functions-glm-5.3-flash` | GLM-5.3 Flash on the function suite | `questions/functions/` | [results.md](../../reports/results.md), "The function suite" |
| `functions-laya` | Laya on the function suite | `questions/functions/` | [results.md](../../reports/results.md), "The function suite" |
| `recognize-jev` | Jev on the function suite's new recognize groups | `questions/suite/` recognize cases past `names-template` (`BENCH_SUITE_ONLY`) | [results.md](../../reports/results.md), "The function suite" |
| `reading-jev` | Jev on the function suite's reading tests and the new find sets | `questions/suite/` cases under `BENCH_SUITE_ONLY` | [results.md](../../reports/results.md), "By function" |
| `pipeline-jev` | Jev through `scripts/run/rad_pipeline.sh`, with shipped commands and `jq` only | the lead singers of the Abbey Road songs, from memory and from picked sections | [rad.md](../../reports/rad.md), "With shipped commands" |
| `pipeline-jev2` | the same pipeline, which also asks single questions three ways and plants a wrong singer | the pipeline, plus single questions such as Tomorrow Never Knows | [rad.md](../../reports/rad.md), "A question Jev does not know" |
| `baseline-bm25`, `baseline-embed`, `baseline-hybrid`, `baseline-overlap` | search baselines that score the question against each option, with no model | the 1,501 | [baselines.md](../../reports/baselines.md) |
| `relation-vectors` | vector search with the relation named in the query | 20 forward questions (`sample.json`) | [baselines.md](../../reports/baselines.md), "Relation-conditioned queries" |

`./run.sh NAME` with a backend address writes two more kinds of folder:

- `thinkthen-NAME`: that backend on the 1,501, with `backend.txt` naming its base URL and model.
- `examples-NAME`: that backend on each folder in `functions/`, one subfolder per function, with its own `backend.txt`.

[../README.md](../README.md) says what a run folder holds and how a replay works.
