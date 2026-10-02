# 0026 Delete the old runs and run the bench on 0.1.0 alone

Owner: the queue owner. Status: open.

## Why

Ticket 0025 converted nine examples to the 0.1.0 question store and pinned every old run to the build that recorded it. With only 0.1.0 installed, the suite skips 27 tests. The old runs under `results/runs/` and `results/archive/` stay in the digest form, about 270 MB tracked, and replay only under builds this machine lacks.

Ian ruled on 2026-10-02. He does not need the old runs, and they can be deleted. He does not care about skipped tests, and they can be deleted. He authorized live runs for the bench under a token cap. The outcome is a bench that runs fully on ThinkThen 0.1.0, with no test that skips for lack of an old build.

## Prior evidence

- Record 0025: 242 tests, OK, 27 skipped under 0.1.0 with no key. The skips are the old-run replays and contracts, the recognize and relate examples, the Liquid d1 replay, `test_chat` (no venv) and `test_harvest` (no page cache).
- A probe on 2026-10-02 in this ticket's worktree deleted every folder under `results/runs/` and `results/archive/` and `results/builds.tsv`, then ran the suite: 5 failures and 66 errors, 20 skipped. The failures fall in four groups:
  - replays and contracts of deleted recordings;
  - checks that rebuild a published table or quote from a deleted run (`test_answers.Recompute`, `test_suite.TableTest`, part of `test_published_numbers`, `test_run`);
  - tests of finished experiments that use a deleted run as a fixture (`test_rad`, `test_score_rad`, `test_rad_pipeline`, `test_open_book`, `test_relation_vectors`, `test_in_text_check`, `test_replay_laya`, `test_baselines.NaturalTest`);
  - tests that borrow one old run as a convenient fixture (`test_generate`, `test_table`).
- Tracked bytes under `results/runs/` and `results/archive/`: recordings 129.5 MB, `details.jsonl` 48.7 MB, `outputs.jsonl` 48.8 MB, `questions.jsonl` 14.2 MB, `answers.jsonl` 10.4 MB, the rest under 20 MB.
- `results/answers.jsonl` already holds every current run's every answer, one row per case, with the run, backend, model, build and date. `results/tables/`, `results/history.tsv`, `results/by-question.jsonl` and `reports/` hold the published numbers.
- The site's `npm run pull-bench` copies files at the bench commit `examples/beatles/bench-pin` names, 97090765. One site folder, `blind-spots`, runs in `results/runs/2026-09-26-thinkthen-jev`. The site already keeps its own converted copy of that recording, and its README says pull-bench is not run because it would copy old recordings back over the converted copies. Deleting the folder at a later bench commit does not change the pinned pull. A future pin move would need the site to drop or replace that folder. This ticket files that as a message in the site's inbox.
- `examples/recognize` and `examples/relate` were recorded on 2026-09-25 by build 02dc0b96 through the default Jev backend with `--model jev-latest`. The backend reported `jev-1.13.0`. 0.1.0's `--plan` shows recognize sends one request for 28 pieces with at most 56 name requests, and relate sends one request for 49 questions.

## Retained behavior

- Every published number keeps its value: the README tables, `reports/`, `results/tables/`, `results/history.tsv`, `results/answers.jsonl` and `results/by-question.jsonl`. These become frozen result tables.
- The nine converted examples and `diff` replay byte for byte under 0.1.0.
- `./run.sh` with no key replays every example and exits 0. With a backend address set it still asks a live run into `results/runs/<today>-...`.

## Changes

1. Delete every folder under `results/runs/` and `results/archive/`, `results/builds.tsv`, and `tests/builds.py`, in Git only. Keep `results/runs/README.md`, rewritten to say new live runs land here.
2. Remove the `BENCH_BIN_<id>` gating from `run.sh` and every test. `run.sh` with no address replays the examples only. It no longer rebuilds `results/tables/`, `results/answers.jsonl` or `reports/generated/`, because those builders read the committed runs and would empty the frozen tables. It prints the frozen tables with `scripts/score/table.py`. After a live run it prints `score.py report` for the new run.
3. Delete the tests that replay a deleted recording or check a contract against one, and the tests that skip: `test_audit_contract`, `test_leaning_no` and `test_diff_guard` where they pin a deleted output, `test_replay_laya`, `test_in_text_check`, `test_rad_pipeline`, the d1 and all-jev replays, `test_chat` and `test_harvest`'s cache test.
4. Delete the scripts of finished experiments whose inputs were deleted runs, with their tests: the RAD scripts (`scripts/run/rad.py`, `rad_pipeline.sh`, `rad_pipeline.checks.json`, `scripts/score/rad_table.py`), `scripts/score/open_book.py`, `scripts/run/relation_vectors.py`, `scripts/run/in_text_check.py` and `scripts/run/chat.py`. Drop `requirements.txt` lines that only `chat.py` needed. Each report that describes one says its runs and scripts are at commit a6a6be71.
5. Retarget each remaining check of a published number to the kept tables. A quote whose number `results/answers.jsonl` or `results/tables/` holds keeps its check against that file. A quote whose only source was a deleted file, such as a load average in `loadavg.txt`, keeps its number in the page and loses its check. The record lists each lost check.
6. `scripts/answers/report.py` finds its systems from `results/answers.jsonl` alone, in place of the committed run folders, so `reports/generated/` still rebuilds byte for byte from the kept table.
7. Tests that borrowed an old run as a fixture build a small one in a temporary folder, or read the same row from `results/answers.jsonl`.
8. Every page link to a deleted file becomes a link to that file at commit a6a6be71 on GitHub. The data README's page command that replays `results/runs/2026-09-26-thinkthen-jev` replays an example recording, or goes. The README, `results/README.md`, `scripts/README.md` and `tests/README.md` say the tables are frozen and name the builds and dates that produced them: 02dc0b96 for the runs of 2026-09-23 to 2026-09-26, c22512868 and aec7819bb for the runs of 2026-09-30, aec7819bb and 2c5ac772b for the Kev and Nimble runs, and no build for the chat and search runs.
9. Re-record `examples/recognize` and `examples/relate` under 0.1.0 at `~/.local/bin/thinkthen`, with `scripts/run/example.sh NAME live OUT`, the default Jev backend and `--model jev-latest`. Cap each with `BENCH_MAX_INPUT_TOKENS=200000`. Stop if a run would need more than 2 million tokens. The key comes from `THINKTHEN_API_KEY` in the environment and is never printed or recorded. The recording holds bodies only. Copy the new `recording/thinkthen.jsonl`, `outputs.jsonl` and `timing.tsv` into each folder, write `run.txt`, and regenerate each README's blocks and `examples/recognize-how`. A changed answer is expected, and the pages say what 0.1.0 found. The tests that pinned the old form assert the question store.
10. The Liquid d1 replay with its 513 unanswered gaps goes with its run. Answering the gaps live would mean a Liquid run and a 50 MB converted recording, so deletion is the cheaper option.
11. File a message in `sdlc/inbox/thinkthen/` of the sdlc repo saying the bench no longer holds `results/runs/2026-09-26-thinkthen-jev` after this ticket's landing, so the site's `blind-spots` folder needs its own source before `bench-pin` moves past it.

## Proof

- `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests` under `systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0`, with 0.1.0 on `PATH` and no key: 0 failures, 0 errors, 0 skipped. The record gives the count.
- `./run.sh` with no key exits 0 and replays all twelve example folders byte for byte.
- `git ls-files results/runs results/archive` lists only `results/runs/README.md`. The record gives the bytes deleted.
- `reports/generated/` and `results/by-question.jsonl` rebuild byte for byte from `results/answers.jsonl`.
- The live runs' input and output tokens, from their outputs' `meta.usage`, are in the record.
- No private name and no home path in the diff.

## Deferred gaps

- Rebuilding `results/tables/` and `results/answers.jsonl` needs committed runs. The builders stay for the next committed run, which will replace the frozen tables.
- A fresh 0.1.0 run of the whole bench, which would replace the frozen numbers.
- The site's `blind-spots` source, owned by the site.
