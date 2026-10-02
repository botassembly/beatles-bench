# 0025 Make the suite pass under 0.1.0: record

Built on 2026-10-02 on `ticket/0025-examples-and-builds` from main at 4d7ffc6d. Every conversion and replay read local files. No paid or live call ran.

## Result

- Nine example recordings are now question stores: annotate, audit, choose, decide, filter, find, rank, score and tag. Each holds one `thinkthen.jsonl`, written by `thinkthen cache convert --quote` under checkpoint 5 (`checkpoint/surfaces/2026-10-02-1`, thinkthen main `4e880cdf6`, 0.1.0). The old entries and `.thinkthen-backend.json` markers are gone, and Git history keeps them. Before committing, each folder was converted again from main's old entries into a scratch folder. All nine came out byte-identical to the committed `thinkthen.jsonl`, so the deletions are exactly the conversion.
- recognize and relate keep their old recordings. Converted with `--quote`, each still misses on replay: 0.1.0 asks recognize and relate questions with other keys than the recorded ones (`the replay folder holds no answer for question ...`). The ticket's stop rule for a changed answer applies. Both folders replay only under `BENCH_BIN_02dc0b96`, and their READMEs say so.
- Each converted example's `timing.tsv` is re-keyed to the question keys a 0.1.0 replay reports. `wall_s` and `sent` therefore replay unchanged, and no example needed the timing exception in the tests or in `run.sh`'s `same()`.
- Each converted example was replayed under checkpoint 5, and its outputs, lists, `run.txt` (SHA-256 `e2962a9b...` of checkpoint 5's debug command, model, date) and README build line were regenerated. Values and probabilities compare equal before and after for all 23 changed answer files. The fields that changed are `meta.tool` (0.0.1 to 0.1.0), `meta.requests` and annotate's `answers.*.request` (question keys in place of request digests), and the new `meta.batch_setting`.
- `examples/audit`: `rows.jsonl` and `rows-context.jsonl` changed only in those same meta fields. The `audit-*.json` reports took 0.1.0's audit shape: `unsure` in place of `unresolved`, plus `f1`, `precision`, `curve`, `tie_share` and other new fields. Every count that also exists in the old shape (`right`, `wrong`, `auc`, `true_yes` and the rest) is unchanged.
- `examples/diff`: `diff.jsonl` is byte-identical. The page's band line now prints `unsure` and `McNemar p 0.000`, where builds before 0.1.0 printed `unresolved` and `p 0.250`. 0.1.0's McNemar test counts every answer that became right or wrong (48 here), where the old test counted only the 3 marked gained. The page explains the change. No answer changed.
- `results/builds.tsv` has 68 rows, one per folder under `results/runs/` and `results/archive/`: 42 rows name 02dc0b96, 3 name aec7819bb, 3 name c22512868, 2 name 2c5ac772b, and 18 say `unknown`. A run takes the build its `run.txt` names. A run without one, dated 2026-09-26 or earlier, takes 02dc0b96. `results/archive/in-text-check/*` takes 02dc0b96, the build its test and record name. A folder whose build no file names says `unknown`. The QA builds' SHA-256 match the runs' `run.txt`: `aec7819bb` is `41af203e...` and `c22512868` is `fbc4ff6a...`.
- `tests/builds.py` reads that table. Every replay or contract check that depends on a run's build now runs only under `BENCH_BIN_<id>`, and otherwise skips with a reason naming the build and the variable. This covers `test_replay_laya`, `test_rad_pipeline`, `test_in_text_check`, `test_suite.ReplayTest`, `test_run`'s all-jev replay, `RunShTest`, the audit and diff contract checks in `test_audit_contract`, `test_leaning_no` and `test_diff_guard`, and each page command in `ExamplePageTest` that replays a `results/` recording.
- `test_suite`'s d1 replay also skips while the run's `run.txt` marks its function table pending. The recording holds no answer for the 513 rate-limited gaps, and the replay still asks them (ticket 0023).
- `run.sh` replays the converted examples under `THINKTHEN_BIN`. It replays the newest Jev run under its `BENCH_BIN_*` command, and otherwise prints one skip line naming the build. It does the same for recognize and relate. Its missing-audit message names 0.1.0. The README install section, `scripts/README.md` and `tests/README.md` state the rule: examples replay under the current checkpoint, and each old run replays under the build `results/builds.tsv` names.
- `ExamplesTest` asserts that every converted example's recording is exactly one `thinkthen.jsonl` whose lines parse, and that recognize and relate keep their old form.

## The memory fault

The first full suite run of this ticket on 2026-10-02 grew to 25 GB on a 27 GB machine. The out-of-memory killer then took down the session's whole tmux pane. Each test module was then run on its own under `systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0`, and the cap killed `test_examples`. One test at a time under a 2 GB cap found the cause: `test_every_number_thinkthen_prints_on_a_page_is_in_its_answers`.

The test read every exponent number from an example's answers with the pattern `-?\d+(?:\.\d+)?e-?\d+` and formatted each one as a plain decimal. 0.1.0 writes question keys into `meta.requests`, and the hex keys hold runs such as `7e9877975802`. Formatting `7e9877975802` as a decimal builds a string of almost ten billion digits. The 0.0.1 digests happened to hold no exponent above 2976.

The fix reads an exponent only as a whole token with at most three exponent digits. A new test pins the pattern: `2e-6`, `-1.5e3` and `4e-05` match, and hex keys and `1e9877975802` do not. The largest converted recordings under `results/` stay unconverted under this ticket, and no test loads one into memory.

Each test module then ran on its own under a 2 GB cap, with `/usr/bin/time -v`, checkpoint 5 as `THINKTHEN_BIN`, and both QA builds set. Every module passed. The largest peaks were `test_answers` at 519 MB, `test_run_sh` at 190 MB, `test_suite` at 129 MB and `test_published_numbers` at 86 MB. `test_examples` peaked at 18 MB, and every other module stayed under 40 MB. The full suite peaks at 533 MB. `test_chat` exits 1 when run alone, because it raises its "needs requirements.txt" skip at import. Under `discover` it counts as a skip.

## Proof

- `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests`, run under a 4 GB cap with 0.1.0 on `PATH` and `THINKTHEN_BIN` unset: 242 tests, OK, 27 skipped, peak 533 MB.
- The same suite with `THINKTHEN_BIN` set to checkpoint 5's command: 242 tests, OK, 27 skipped.
- The same suite with `BENCH_BIN_c22512868` and `BENCH_BIN_aec7819bb` set to the builds QA keeps: 242 tests, OK, 22 skipped. Five more checks run than under 0.1.0 alone: the all-jev replays in `test_suite` and `test_run`, and the recognize, reading and relate run replays. The d1 replay ran under `aec7819bb` once and failed on `rank-reading-popularity-007`, a rate-limited gap the recording holds no answer for. It now skips while the run's function table is pending. No check fails.
- `./run.sh` with no key under 0.1.0 exits 0. It prints `run.sh: skipping the replay of results/runs/2026-09-26-thinkthen-jev: it was recorded with thinkthen 02dc0b96; set BENCH_BIN_02dc0b96 to its command`, replays the nine converted example folders and diff byte for byte, and prints the skip lines for recognize and relate.

Skip reasons with only 0.1.0 present (27):

- 02dc0b96 is not on this machine, so no build here can run these checks: the four `test_audit_contract` checks, the four `test_leaning_no` checks, `test_diff_guard`, `test_in_text_check`'s Jev replay, `test_rad_pipeline`'s replay, the three `test_replay_laya` replays, the Laya rows in `test_suite`, the recognize and relate example replays, `RecognizeHowTest`, and the `data/README.md` page command that replays `results/runs/2026-09-26-thinkthen-jev`. `ExamplePageTest` checks every other page command first, then reports the skip.
- `BENCH_BIN_aec7819bb` and `BENCH_BIN_c22512868` are unset by default: the all-jev replays in `test_suite` and `test_run`, the d1 replay, and the recognize, reading and relate run replays.
- Liquid d1's pending function table (2 skips), `test_chat` (no venv), and `test_harvest` (no page cache).

## Deferred gaps

- Converting `results/runs/` and `results/archive/`, which waits for a ruling on size.
- The recognize and relate examples, which need a fresh recording under 0.1.0. That is a live run with its own token cap.
- The GLM chat folders, which `chat.py` owns.
- Liquid d1's 513 rate-limited gaps (ticket 0023). Its replay stays skipped until they are asked again.
- The site's `npm run pull-bench` gets nine converted examples. recognize and relate still replay only under 02dc0b96.
