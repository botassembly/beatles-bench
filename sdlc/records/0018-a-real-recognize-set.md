# 0018 Give recognize a real test set, with text relations: record

Built on 2026-09-30 on `ticket/0018-a-real-recognize-set` from main at 60a76b8b. The one paid job ran through thinkthen-qa's `bin/live` guard. `THINKTHEN_BIN` was the pinned build `thinkthen-c22512868`, SHA-256 `fbc4ff6a`, of thinkthen main at c22512868.

## Result

- The suite's recognize cases grew from 48 to 200 in nine tests: `names-template` (the old 48, byte-for-byte), `varied` (36), `song-or-album` (14), `short-names` (16), `case` (12), `no-names` (10), `paragraphs` (10), `punctuation` (14), and `relations` (40). Every truth still comes from `data/` by script.
- The 40 relations cases run `recognize song person album --relation sung_by=song:person --relation appears_on=song:album`. Each case's `edges` truth holds only the edges the sentence states; six cases name two entities while stating no edge.
- `BENCH_SUITE_ONLY` filters cases by id prefix for live runs and replays, so a run can ask one group without sending the rest.
- `score_suite.py` scores each test group per kind and scores relation edges by precision, recall, and F1. It takes several comma-separated runs, requires each touched test whole, and keeps the other models' tables byte-identical.
- The live run `results/runs/2026-09-30-recognize-jev` asked the 152 new cases in 354 requests. No gap, no failed question. A replay with the key unset wrote the same bytes.
- `functions.tsv`, `results/history.tsv`, `reports/results.md`, and the run READMEs hold the new rows.

## Paid job

| Job | Cap | Input tokens sent | Dollars |
| --- | --- | --- | --- |
| Recognize suite, new groups | 2,000,000 | 687,702 | 0.0288 |

- The plan's upper bound before the run was 1,172,089 input tokens for the 112 plain cases and 262,298 for the 40 relations cases, 1,434,387 in all.
- The guard reported 354 calls and $0.0288 of spend. Jev's output tokens are free; the run returned 173,022.

## Numbers that moved

recognize scored 0.959 to 1.000 on the template test. On the new groups:

| Test | Weakest measure | Value |
| --- | --- | --- |
| varied | album recall | 0.833 |
| song-or-album | song and album recall | 0.857 |
| short-names | song precision and recall | 0.938 |
| case | album recall | 0.583 |
| no-names | no name found | 1.000 |
| paragraphs | song recall | 0.950 |
| punctuation | song and album, both directions | 0.786 |
| relations | relation edge recall | 0.783; precision 0.973 |

The misses concentrate where the ticket aimed: casing, marks inside a title, and the second half of a stated relation.

## Proof

- `python3 -m unittest tests.test_suite`: 33 tests, OK. With `THINKTHEN_BIN` at the c22512868 build the new run's replay runs; the old suite's replay skips, because its recording binds to build 02dc0b96. Under the 02dc0b96 build the old suite replays and the new run skips.
- `python3 -m unittest discover -s tests` passes with no `THINKTHEN_BIN` (replay tests skip). Under the c22512868 build, the tests that replay recordings made under 02dc0b96 fail outside this ticket's files: the request digest and some printed bytes changed between the builds. The README already says a replay's byte check holds for the build that wrote the recording.
- A rebuild of `questions/suite/` gives the same bytes, and every truth span slices the sentence to the name.

## Deferred

- The other test files' recording replays (`test_replay_laya`, `test_examples`, `test_rad_pipeline`, `test_in_text_check`, `test_run_sh`) fail under the c22512868 build for the same binding reason; each run folder names only "thinkthen 0.0.1", not the build. Re-recording them or gating them on the recording's build is separate work.
- `test_diff_guard` and `test_leaning_no` show small output changes between the builds (an added warning line, an audit figure from 0.086 to 0.092).
- The ticket's own deferred gaps stand: other kinds, and GLM and Laya runs of the new groups.

## Reviews

Pending independent review.
