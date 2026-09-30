# 0022 One answers table, and reports from it: record

Built on 2026-09-30 on `ticket/0022-answers-table` from main at bd7045fd. No paid job ran; the whole ticket is
offline reads of the committed runs.

## Result

- `scripts/answers/build.py` writes `results/answers.jsonl`: 19,083 rows, one per case per committed run
  folder, listed by `git ls-files` (`score.tracked`), so an uncommitted folder on one machine never enters.
  Each row carries run, date, backend, model, build, id, function, test, level, category, truth, the answer
  itself, the per-case `right`, the scored `counts` units, the `value` the ordering measures rank, the
  answer's `probability`, and the recorded cost (input, cached and output tokens, milliseconds, requests).
- `right` holds a mean measure's per-case score (accuracy with tie shares, exact set, top pick, find,
  annotate fields, "no name found"); `counts` holds the tp/fp/fn units for filter, relate and recognize so
  pooled precision, recall and F1 come from a sum; `value` holds the score answer, rank's negated print
  position, decide's p(yes) and choose's tie width. annotate writes one row per field as `case:field`, and a
  refusal keeps a row with `gap` set. recognize gets no probability, because its strength is not one.
- Level comes from the case's own field under ticket 0021, and falls back to the test shape until the
  catalog lands: `memory` for the knowledge questions, `reading` for the reading tests, `text` for
  recognize. The build joins `questions/catalog.jsonl` for function, test, level, category and truth the
  day it exists.
- `scripts/answers/report.py` loads the table into an in-memory SQLite database, runs the queries in
  `scripts/answers/queries/` (scores, units, values, the backend join, calibration, by-question), and
  computes the intervals and tests in Python. It writes `reports/generated/by-function.md` (each function's
  main measure per level and backend, Wilson for shares, seeded bootstrap for Spearman and F1),
  `head-to-head.md` (agreement and the exact McNemar test for each model-backend pair on the same
  questions, baselines excluded; Spearman where the measure is a value), `calibration.md` (the expected
  calibration error per backend, function and level where an answer carries a probability), and
  `results/by-question.jsonl` (one row per question with every run's answer, probability and score).
- A system pools its committed knowledge run (the one `analyze.py` scores) with the suite runs on the same
  backend and model, the way `score_suite.py` merges Jev's four folders; a newer folder wins for a case
  both asked. Part-question runs (open-book, section-picking, one-line) fill the table but stay out of the
  pooled measures.
- `run.sh` runs the build and the report after scoring. `analyze.py` now discovers its runs through
  `score.tracked` too, so the tables and the answers file use the same committed-folder rule; its tables
  regenerate byte-identical.
- `scripts/answers/README.md` shows three queries (per-run accuracy, two runs on the same cases, run cost)
  in DuckDB over the JSONL and in equivalent SQLite through Python's built-in driver.

## Proof

- `tests.test_answers` — 19 tests, OK in 11 s. `Recompute` derives every row of
  `results/tables/functions.tsv` (220), `functions-glm.tsv` (37) and `functions-laya.tsv` (37) from
  `results/answers.jsonl` alone: every `n`, `value`, `lo` and `hi`, plus the usage columns on the main
  rows (requests, input tokens, dollars through `prices.tsv`, median and p90 seconds) and the relate
  tuned-cut rows, whose cut is the audit's and whose held-half precision, recall and F1 recompute from
  the stored edges and skip lists. It also derives every row of `accuracy.tsv` (200), including the ties
  column and the chance benchmark (which needs the question files' option counts, not the answers). All
  inside the tables' own rounding.
- `python3 scripts/answers/report.py` twice writes identical bytes for all four outputs (the test also
  compares a fresh generation to the committed files).
- The three DuckDB examples run verbatim with `duckdb` v1.1.3; the SQLite examples run through
  `python3` and its `sqlite3` module. The disagreement join returns 368 questions.
- `python3 -m unittest discover -s tests` with `THINKTHEN_BIN` and `THINKTHEN_API_KEY` unset: 221 tests,
  OK, 26 skips, in 185 s.
- Worked examples pin `stats.wilson`, `stats.mcnemar` and the seeded bootstrap.

## What the build taught us

- Row order is part of the data: the seeded bootstrap intervals for F1 and Spearman resample the unit
  list, so reproducing a published interval byte for byte needs the run's own case order, not a sorted
  one. The table keeps the run folders' order and the pools keep file order.
- `meta.requests` in a suite run is the request hash list, not a count; the number is the distinct-name
  count, or 1 when the rows name none (the scorer's rule).
- A case the suite renamed away (the Laya run's `recognize-NN-wNN` word-split outputs and `relate-NN`
  gaps) still lands in the table — it is a recorded answer — but stays out of the pooled systems, since
  the current suite files name no such case.
- `pick/`-style run questions carry no truth, so they get `right` null but still carry `value` (the tie
  width) and `probability`; `by-question.jsonl` reaches them through the questions table's union with the
  ids seen in answers.
- The calibration number pairs the pick's probability with the pick's own rightness for tag and
  annotate's singer — not with the exact-set score, which made Jev's tag look twice as miscalibrated.
- `git ls-files` is the whole committed-folder rule; `score.tracked` falls back to the filesystem outside
  a checkout, where a copy holds committed files only.

## Deferred

- `questions/catalog.jsonl` (ticket 0021): the builder already joins it when it exists.
- Coverage, confusion and coverage-at-cut columns beyond the accuracy table's headline rows are
  recomputed where the published file has them; the per-bucket calibration and coverage tables keep their
  own format for now.
- The reports do not yet plot or compare systems beyond the backend pairs the ticket asks for.

## Reviews

(pending)
