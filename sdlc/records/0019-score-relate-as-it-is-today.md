# 0019 Score relate as it works today: record

Built on 2026-09-30 on `ticket/0019-score-relate` from main at 32616683. The one paid job ran through a local spend
guard. `THINKTHEN_BIN` was the pinned build `thinkthen-c22512868`, SHA-256 `fbc4ff6a`, of thinkthen main at
c22512868.

## Result

- The suite's relate cases grew from 1 to 47 in five tests: `song to singer and album` (`relate-songs`, the same
  199-entity set, asked again through the pair planner at the 0.5 cut), `solo` (16), `duet` (6), and
  `wrong-album-only` (16) — small sets of one to three settled songs, the four Beatles, and three albums, the right
  album left out of `wrong-album-only` — and `links` (8), sets of about 20 entities of `data/links.tsv` songs and
  people under `composed_by` and `produced_by` (`relate-links.json`).
- The small and links tests run at a 0.01 cut so `thinkthen audit` can tune a bar. `scripts/score/relate_audit.py`
  writes each test's result lines and a seeded half-and-half key into the run's `relate-audit/` and saves one audit
  report per test. `score_suite.py` cuts the printed edges at the published 0.5 cut itself, groups the relate rows by
  test, reads the saved reports, and adds the tuned cut and its held-half measures as rows. `relate-songs` is one
  case and splits into no halves, so it keeps only the 0.5 rows.
- The live run `results/runs/2026-09-30-relate-jev` asked all 47 cases in 54 requests. No gap, no failed question. A
  replay with the key unset wrote the same bytes.
- `functions.tsv`, `results/history.tsv`, `reports/results.md`, and `results/runs/README.md` hold the new rows. The
  historical relate rows stay in `reports/results.md`, labeled with their planner and build.

## Paid job

| Job | Cap | Input tokens sent | Dollars |
| --- | --- | --- | --- |
| Relate suite, all cases | 3,000,000 | 193,845 | 0.0081 |

- The plan's upper bound before the run was 505,848 input tokens over 54 requests, 342,453 of them `relate-songs`.
- The guard reported 54 calls and $0.0081 of spend. Jev's output tokens are free; the run returned 91,556.

## Numbers that moved

At the 0.5 cut on the same 199-entity set as the historical run: edge F1 0.523 (was 0.719), edge precision 0.420
(was 0.867), edge recall 0.693 (was 0.614), singer top pick 0.722 (was 0.899), album top pick 0.522 (was 0.637),
duets pick a lead 0.833 (was 0.917). The pair planner trades precision for recall. The new groups:

| Test | Weakest measure | Value |
| --- | --- | --- |
| solo | edge precision | 0.644 |
| duet | edge recall | 0.583 |
| wrong-album-only | edge precision | 0.296 (it still names an album for every song; all are wrong) |
| links | edge precision | 0.330; edge recall 0.833 |

Audit-tuned cuts on a seeded half of each test, scored on the other half: solo 0.45 (held F1 0.689), duet 0.19
(0.778), wrong-album-only 0.46 (0.373), links 0.67 (0.596).

## Proof

- `python3 -m unittest tests.test_suite` with `THINKTHEN_BIN` at the c22512868 build: 37 tests, OK, one skip (the
  2026-09-26 suite replay binds to build 02dc0b96). The new relate replay test reruns `ask_suite.py replay` over the
  run's recording and compares `outputs.jsonl` byte for byte.
- The replay match also ran by hand: with the key unset and `BENCH_SUITE_ONLY` at the relate prefixes,
  `ask_suite.sh replay` wrote bytes identical to the live run's `outputs.jsonl`.
- A rebuild of `questions/suite/` gives the same bytes, and every relate truth edge checks against `songs.tsv` and
  `links.tsv` in `tests/test_suite.py`.

## Deferred

- The ticket's own gaps stand: relations beyond singer, album, composer, and producer, and GLM and Laya runs of the
  new groups.
- The tuned-cut rows carry no interval: `thinkthen audit` reports held-half counts, not per-record units.
- `relate-songs` gets no tuned cut: a one-case test has no halves. A cut tuned across the small tests and scored on
  the catalogue set is possible but was not asked for.

## Reviews

Independent review found three items, all fixed on this branch: the 02dc0b96 replay test no longer compares its
choice-planner relate scores against the new table rows (the byte replay still covers them); `wrong-album-only`'s
forced-0.000 `album top pick right` row is gone — a relation with no true edge gets no pick row, and the report
keeps the prose that relate names an album anyway; and `relate_audit.py`'s rows, key, and seeded half split now have
a unit test (`tests/test_relate_audit.py`). Re-review pending.
