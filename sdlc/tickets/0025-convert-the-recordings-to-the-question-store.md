# 0025 Make the suite pass under 0.1.0: convert the examples, pin the old runs

Owner: the queue owner. Builder: one SWE-2 worker. Status: landed on 2026-10-02. Code review 1 asked to record the run script edits; done, and re-review accepted. Suite under 0.1.0: 242 tests, OK, 27 skipped. Record: [../records/0025-convert-the-recordings-to-the-question-store.md](../records/0025-convert-the-recordings-to-the-question-store.md).

## Why

ThinkThen 0.1.0 is now the `thinkthen` on this machine's `PATH`. The bench suite's replay tests used to skip when no command was found. Now they run, and 16 tests fail: 9 failures and 7 errors, the same with and without bench `3912d74a`. Every committed recording is in the old digest form, and 0.1.0 replays only a question store. The site's `npm run pull-bench` copies `examples/` and needs files that current ThinkThen replays. The marketing lead asked for that on 2026-09-30.

## Prior evidence (local probe, 2026-10-02, in a throwaway worktree)

- 61 committed folders hold old entries or a `thinkthen.sqlite`. `thinkthen cache convert --quote DIR`, run with checkpoint 5's command (`4e880cdf6`), converted 58 of them. It skipped 0 entries and left 0 answers unquoted, writing 167,943 answers. The three GLM chat folders refused, because `chat.py` wrote them, not thinkthen (review finding 3).
- Without `--quote`, a converted single-record exchange stays unquoted, and every replay misses. `--quote` is required.
- Converted folders replay, but their outputs differ in bytes from the committed ones, for three reasons:
  - the result rows that 0.1.0 prints carry new fields;
  - `tool` reads `thinkthen 0.1.0`;
  - `wall_s` and `sent` come out `null` and `false`, because `timing.tsv` is keyed by request digest and a store replay reports question keys (review finding 2).
- Size: converting every folder writes 362.5 MB of `thinkthen.jsonl`, where the old entries are 74.9 MB in 28,349 files. Three runs hold 226 MB of it: `2026-09-30-all-jev` (113 MB), `2026-09-30-relate-jev` (63 MB) and `2026-09-30-all-liquid-d1` (50 MB). The bench is about to go public, so converting everything is ruled out here (review finding 8).
- `examples/` is 3.6 MB.
- The 0.0.1 builds QA keeps (`aec7819bb`, `c22512868`) also fail the old-run replays. Those tests pass only under the exact build each run was recorded with.

## Retained behavior

- Every run's answers, scores, tables and reports keep their numbers. No `results/runs/` file changes.
- Each example's README keeps its claims. Its build line names the build that last replayed it.

## Changes

Part A: the examples.
1. For each `examples/*/recording` (decide, choose, tag, score, filter, rank, find, annotate, recognize, relate, audit), run `thinkthen cache convert --quote` with checkpoint 5's command. Remove the old entries, folder markers, `.locks/` and any `thinkthen.sqlite`. Git history keeps the old form.
2. Re-key each example's `timing.tsv` from a first 0.1.0 replay: column 2 takes the question keys that `meta.requests` reports for each case id, so a store replay keeps `wall_s` and `sent`. If an example cannot be re-keyed, say why in the record, and leave those two fields out of the byte comparison for that example only, in both the tests and `run.sh`'s `same()`.
3. Replay each example with checkpoint 5's command. Commit the regenerated outputs. Each example's README names the build `checkpoint/surfaces/2026-10-02-1` (`4e880cdf6`, 0.1.0) and states that no answer changed. A changed answer, value or probability stops the ticket for that example, and its difference is reported.

Part B: the old runs, and the checks that read their outputs.
4. Add `results/builds.tsv`, one row per folder under `results/runs/` and `results/archive/`, giving the run folder and the thinkthen commit that recorded it. A run's own `run.txt` names its build. A run without a `run.txt`, dated 2026-09-26 or earlier, takes 02dc0b96, as the README already states. A row whose build cannot be found says `unknown`. An undated folder, such as `results/archive/in-text-check/*-recording`, takes the build its test and record name, 02dc0b96 for in-text-check. The record says why.
5. A replay or contract check that depends on a run's build runs only when `BENCH_BIN_<first 8 of the commit>` names a command for that build, such as `BENCH_BIN_02dc0b96`. Otherwise it skips, with a reason that names the build and the variable. This covers:
   - the old-run replays in `test_replay_laya`, `test_rad_pipeline`, `test_in_text_check`, `test_suite` and `RunShTest`;
   - the `audit` and `diff` contract checks in `test_audit_contract`, `test_leaning_no` and `test_diff_guard`, gated on the build that wrote the committed audit or diff output they compare against;
   - each page command in `test_examples.ExamplePageTest` that replays a `results/` recording, such as `data/README.md`'s `--replay results/runs/2026-09-26-thinkthen-jev/recording`.
   The examples themselves keep using `THINKTHEN_BIN`.
6. `run.sh` replays `examples/` under `THINKTHEN_BIN`, the current checkpoint. It replays the newest Jev run under that run's `BENCH_BIN_*` command when one is set, and otherwise prints one line naming the build and skips that step. Its `audit --help` check names 0.1.0, and `same()` compares what the timing rule in step 2 allows.
7. The README's install section names ThinkThen 0.1.0 as the command for `./run.sh` and the examples, and `BENCH_BIN_*` for old runs. `tests/README.md` states the rule: examples replay under the current checkpoint, and each old run replays under the build in `results/builds.tsv`.
8. Each example's `run.txt` is rewritten for its new build: SHA-256, model and date, as `test_examples` requires. Its README's fenced blocks, and `recognize-how`'s table, are regenerated under 0.1.0.

Coverage lost by this ticket: with only 0.1.0 installed, the old-run replays and the audit and diff contract checks skip. They run again wherever their pinned build is set. 02dc0b96 is not on this machine today, so the record names which checks no build here can run.

## Proof

- `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests`, with `thinkthen` 0.1.0 on `PATH` and with `THINKTHEN_BIN` set to checkpoint 5's command, has 0 failures and 0 errors. The record gives the exact pass and skip counts, and every skip reason.
- The same suite, with `BENCH_BIN_c22512868` and `BENCH_BIN_aec7819bb` set to the builds QA keeps, runs the checks for those builds' runs. The record gives the counts, and any check that still fails with its reason.
- `./run.sh` with no key exits 0 under 0.1.0 and prints the skip line for the old run.
- A test asserts that no `examples/*/recording` holds an old entry, a folder marker or a `thinkthen.sqlite`, and that each holds one `thinkthen.jsonl` whose lines parse.
- Each example's committed answers, before and after, compare equal on `value` and probabilities. The record lists the fields that changed.
- No live call: conversion and replay read files only.

## Deferred gaps

- Converting `results/runs/` and `results/archive/`, at a cost of about 290 MB net. It waits for a ruling on size, such as release assets or a separate data repo.
- The GLM chat folders, which `chat.py` owns.
- Liquid d1's 513 rate-limited gaps (ticket 0023), which are asked again into a converted folder once that ruling exists.
