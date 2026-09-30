# 0022 Store every answer in one table, and report from it

Owner: the queue owner. Status: done on 2026-09-30.

## Why

Ian wants reports on every question, and data files anyone can query. Today each run folder has its own layout: `answers.jsonl` for the knowledge runs, `outputs.jsonl` for the suite runs, and scores land in `results/tables/*.tsv` through several scripts. Comparing two backends question by question means custom code each time.

## Prior evidence

- Committed run folders under `results/runs/`: the knowledge runs of Jev, GLM-5.3 Flash and Laya, and the suite runs of tickets 0018 to 0020.
- `scripts/score/score.py` and `scripts/score/score_suite.py` hold each measure: tie shares, exact set, Spearman, F1, and the relate and recognize edge and name rules.
- DuckDB 1.x is installed on the build machine. Python's `sqlite3` is in the standard library.

## Retained behavior

- Every run folder keeps its bytes. The published tables in `results/tables/` keep their values. This ticket adds new files beside them.
- The existing scorers stay the authority for each measure. The new table stores what each measure needs per case, so the published figures can be recomputed from it.

## Changes

1. `scripts/answers/build.py` writes `results/answers.jsonl`, one row per case per run. It reads only committed run folders, listed by `git ls-files`, so an untracked folder on one machine never enters it. Each row holds:
   - run, backend, model, build, date, id, function, test, level, truth, answer, input tokens, and milliseconds where the run recorded them
   - `right`: 0 to 1 where the measure is a mean of per-case scores (accuracy with tie shares, exact set, top pick, find, annotate fields, "no name found"). It is null otherwise.
   - `counts`: true positives, false positives and false negatives for filter, relate and recognize. The pooled F1, precision and recall come from summing them.
   - `value`: the numeric answer for score, and the position for rank. Spearman comes from these over the test.
   - `probability`: the probability of the answer given, where the backend returns one. It is null for recognize, whose strength is not a probability.
   - annotate writes one row per field, with the field in the id.
2. `scripts/answers/report.py` loads the catalog and the answers into an in-memory SQLite database. It runs the queries in `scripts/answers/queries/*.sql`, computes intervals and tests in Python, and writes:
   - `reports/generated/by-function.md`: each function's main measure per level and backend, with a 95% interval: Wilson for means, bootstrap for Spearman and F1.
   - `reports/generated/head-to-head.md`: for each pair of model backends on the same questions, agreement and an exact McNemar test per function and level, on the per-case measures. Baselines are not backends here.
   - `reports/generated/calibration.md`: expected calibration error per backend and function, where the answer carries a probability.
   - `results/by-question.jsonl`: one row per question, with every backend's answer, probability and score.
3. The README of `scripts/answers/` shows three example queries, each in both DuckDB over the JSONL files and SQLite.
4. `run.sh` runs `build.py` and `report.py` after scoring, with no key and no network.
5. `scripts/score/analyze.py` discovers runs the same way, from committed folders only.

## Proof

- A test builds the answers from the committed runs and recomputes every published figure in `results/tables/functions*.tsv` and the main accuracy tables from `right`, `counts` and `value`, within rounding.
- A test runs `report.py` twice and gets identical bytes.
- A test checks the Wilson, bootstrap and McNemar code against worked examples.
- No live call in this ticket.

## Deferred gaps

- A web view of the reports.
