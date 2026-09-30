# 0022 Store every answer in one table, and report from it

Owner: the queue owner. Status: ready for review.

## Why

Ian wants reports on every question, and data files anyone can query. Today each run folder has its own layout: `answers.jsonl` for the knowledge runs, `outputs.jsonl` for the suite runs, and scores land in `results/tables/*.tsv` through several scripts. Comparing two backends question by question means custom code each time.

## Prior evidence

- Run folders under `results/runs/`: the knowledge runs of Jev, GLM-5.3 Flash, Laya, and the untracked Liquid d1 and Kev runs of 2026-09-29, plus the suite runs of tickets 0018 to 0020.
- `scripts/score/score.py` and `scripts/score/score_suite.py` hold each measure: tie shares, exact set, Spearman, F1, and the relate edge rules.
- DuckDB 1.x is installed on the build machine. Python's `sqlite3` is in the standard library.

## Retained behavior

- Every run folder keeps its bytes. The published tables in `results/tables/` keep their values; this ticket adds new files beside them.
- The existing scorers stay the authority for each measure. The new table records per-question outcomes by calling their rules, not by reimplementing them.

## Changes

1. `scripts/answers/build.py` writes `results/answers.jsonl`, one row per question per run: run, backend, model, build, date, id, function, test, level, truth, answer, probability, right (a number from 0 to 1, so a tie share fits), input tokens, and milliseconds where the run recorded them. It reads every committed run folder, and joins `questions/catalog.jsonl` for function, test and level.
2. `scripts/answers/report.py` loads the catalog and the answers into an in-memory SQLite database, runs the queries in `scripts/answers/queries/*.sql`, and writes:
   - `reports/generated/by-function.md`: share right with a 95% Wilson interval per function, level and backend.
   - `reports/generated/head-to-head.md`: for each pair of backends run on the same questions, agreement and an exact McNemar test per function and level.
   - `reports/generated/calibration.md`: expected calibration error per backend and function, where the answer carries a probability.
   - `results/by-question.jsonl`: one row per question with every backend's answer, probability and right.
3. The README of `scripts/answers/` shows three example queries, each in both DuckDB over the JSONL files and SQLite.
4. `run.sh` runs `build.py` and `report.py` after scoring, with no key and no network.

## Proof

- A test builds the answers from the committed runs and checks, per run and test, that the mean of `right` equals the figure in `results/tables/`, within rounding.
- A test runs `report.py` twice and gets identical bytes.
- A test checks the Wilson and McNemar code against worked examples.
- No live call in this ticket.

## Deferred gaps

- A web view of the reports.
