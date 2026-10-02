# 0026 Delete the old runs and run the bench on 0.1.0 alone: record

Built on 2026-10-02 on `ticket/0026-delete-the-old-runs` from main at a6a6be71. Two live calls ran, under the token cap the ticket set.

## Result

- Git no longer tracks any folder under `results/runs/` or `results/archive/`, nor `results/builds.tsv`, `tests/builds.py` and `tests/published.py`. The deletion removes 39,510 files and 270.2 MB. History keeps every file at a6a6be71.
- `results/runs/README.md` now says new live runs land there. Stub `README.md` files in `results/runs/2026-09-26-thinkthen-jev/` and `results/runs/2026-09-26-thinkthen-jev-open-book/` link each run at a6a6be71, so the site's two links at main keep a page.
- `run.sh` lost its build pinning. With no address, it replays every example and prints the frozen tables with `table.py`. `./run.sh NAME` replays the newest live run of that name, and exits 2 with a message when none exists. A live run ends with `score.py report` for its new run. `run.sh` no longer runs `analyze.py`, `build.py` or `report.py`, because those builders read committed runs.
- `score.py newest` skips a folder that holds only `README.md`. `score.py load` scores a live run's own `questions.jsonl` or `ids.txt` when it has one.
- `scripts/answers/report.py` finds its systems from `results/answers.jsonl` alone. A rerun leaves `reports/generated/` and `results/by-question.jsonl` byte for byte unchanged.
- The scripts of finished experiments went with their tests: the RAD scripts, `open_book.py`, `relation_vectors.py` and `in_text_check.py`. `chat.py` stays. Each page that describes one says its runs and scripts are at a6a6be71.
- The tests that replayed a deleted recording or skipped went: `test_audit_contract`, `test_replay_laya`, `test_in_text_check`, `test_rad_pipeline`, `test_rad`, `test_score_rad`, `test_open_book`, `test_relation_vectors`, `test_chat`, the replays and pending-table checks in `test_suite`, `test_run` and `test_answers`, and `test_harvest`'s cache test. Missing `jq`, `git` or `thinkthen`, or a dirty `results/`, now fails with the old skip message.
- `test_leaning_no` and `test_diff_guard` run under 0.1.0. 0.1.0 prints a calibration error of 0.086 for the leaning-no answers, where 02dc0b96 printed 0.092. `reports/leaning-no.md` gives both.
- Every page mention of a deleted path links that path at a6a6be71. The README, `results/README.md`, `scripts/README.md` and `tests/README.md` say the tables are frozen and name the builds and dates behind them.
- The Liquid d1 replay with 513 unanswered gaps went with its run. Answering the gaps live would need a Liquid run and a 50 MB converted recording, so deletion was cheaper.

## The live runs

- Backend: the default Jev address with `--model jev-latest`, the same as the 2026-09-25 recordings. The backend reported `jev-1.13.0`, unchanged from those recordings.
- Command: `scripts/run/example.sh NAME live OUT` under the 0.1.0 release binary (SHA-256 `b322a349...`, in each `run.txt`), with `BENCH_MAX_INPUT_TOKENS=200000` on each step.
- recognize sent 2 calls: 6,871 input and 1,846 output tokens. relate sent 1 call: 1,765 input and 877 output tokens. The total is 8,636 input and 2,723 output tokens, 11,359 in all, far under the 2 million stop.
- Each live `thinkthen.sqlite` was converted with `thinkthen cache convert`. The old digest files were deleted. Each folder's `./run`, its threshold variants and `example.sh` replay from the new `recording/thinkthen.jsonl` with no key.
- The key came from the environment and was never printed or recorded. A search of both recordings finds no `authorization`, `x-api-key` or `bearer` text, and no value of the key variables.
- 0.1.0's recognize asks where each word stands in a name, then asks each name's kind. 0.1.0's relate asks one yes or no question for each pair in one request. The pages show these answers and say the slides show the older planners' answers. `examples/recognize-how` now shows 0.1.0's two steps.

## Proof

- `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests` under `systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0`, on the committed tree, with 0.1.0 on `PATH`, `THINKTHEN_BIN` unset, `jq` and `git` present: 180 tests, OK, 0 skipped, in 92 seconds.
- `grep -rnE "skipTest|skipIf|skipUnless|unittest\.skip|SkipTest" tests/` finds nothing.
- `git ls-files results/runs results/archive` lists only `results/runs/README.md` and the two stubs.
- No private name and no home path appears in the added lines of the diff.

## Lost checks

These checks read a deleted file and have no source in the kept tables. The pages keep their numbers.

- The load averages quoted from each run's `loadavg.txt`.
- The non-top option probabilities on the catches page (John and George, It's All Too Much).
- The all-jev input-token figure, which no kept table holds.
- `TableTest`'s byte-for-byte rebuild of the tables. `test_answers.Recompute` still rebuilds the reports from `results/answers.jsonl`.
- The audit contract and every old-run replay.
- The relate tuned cut now comes from the table itself, so its check only confirms the table against itself.

## Deferred gaps

- Rebuilding `results/tables/` and `results/answers.jsonl` needs committed runs. A fresh 0.1.0 run of the whole bench would replace the frozen numbers.
- The site's `blind-spots` folder needs its own source before its bench pin moves past a6a6be71. The site's owner has a message about it.
