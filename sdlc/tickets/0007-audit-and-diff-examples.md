# 0007 Worked examples for audit and diff

Owner: Claude marketing session. Status: done. Ticket review 1 returned eight findings. This version takes all eight.

## Why

Ian asked on 2026-09-25 for the audit and diff examples to live in the bench, each with its own talk slide. Choosing the bar is the hard part of using Jev. audit shows which bar gets the most right on answers you already saved. diff shows which answers flip when you move the bar, and whether each flip fixes or breaks one. Neither command sends a request.

## Prior evidence

The marketing session ran both commands by hand in scratch on 2026-09-25, with a thinkthen build of main at e70bddab. Only that build has audit and diff. The 2026-09-24 release build does not.

- The saved answers: `decide "It appears on the album Abbey Road."` over 70 hand-picked titles, all in `data/songs.tsv`. Seven are on Abbey Road.
- The key: `{"id": title, "value": "yes"|"no"}` from `first_album`.
- audit at seven bars:

| Bar | Right of 70 | Said yes, wrong | Said no, wrong |
| --- | --- | --- | --- |
| 0.5 | 56 | 14 | 0 |
| 0.6 | 62 | 8 | 0 |
| 0.7 | 65 | 5 | 0 |
| 0.8 | 64 | 5 | 1 |
| 0.83 | 65 | 3 | 2 |
| 0.9 | 65 | 2 | 3 |
| 0.95 | 65 | 0 | 5 |

- AUC 0.967. audit's suggested cut is 0.83, tuned on a seeded half and checked on the other half.
- diff at 0.5 against 0.83: 13 answers change. 11 are fixed and 2 are broken (Something 0.81 and Octopus's Garden 0.72, both on Abbey Road). Right answers go from 56 to 65. McNemar p is 0.022.
- The key's `value` field must be named `value`. audit refuses `answer`.

## Retained behavior

Everything ticket 0006 landed stays as it is. The ten folders, their recordings, and the suite's eight cases replay byte for byte. `data/SOURCES.md` still holds: no Wikipedia text.

## Design

- **Folders.** `examples/11-audit/` and `examples/12-diff/`, in the talk's order.
- **The live run.** `11-audit` holds one case file, `audit-cold.jsonl`, with records `audit-01` to `audit-70`. It asks `decide "The text is the title of a song by the Beatles. It appears on the album Abbey Road." --jsonl --field /input` over the 70 titles. It goes through the runner like ticket 0006, with `BENCH_TESTS=audit-cold`, and keeps `recording/`, `outputs.jsonl`, and `timing.tsv`.
- **Generator.** `scripts/generate/examples.py` writes the case file and `key.jsonl` from `data/songs.tsv`. The key holds `{"id": title, "value": "yes"|"no"}` from `first_album`. The 70 titles sit in the generator as a fixed list, because they were chosen by hand for the talk. The generator says so.
- **Rows.** audit and diff cannot read the runner's wrapped `outputs.jsonl`. `11-audit/tune.sh` first writes `rows.jsonl` with `jq -c '.rows[]' outputs.jsonl`. Each row's `input` is `{"id","input"}`, so both commands use `--id /input`, which gives the title and matches the key.
- **audit outputs.** `tune.sh` then writes these files, in JSON:
  - `audit-asrun.json` from `thinkthen audit rows.jsonl key.jsonl --id /input`. It carries the suggested cut.
  - `audit-<bar>.json` for each bar in 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, plus the suggested cut, from the same command with `--threshold <bar>`.
- **diff output.** `12-diff/diff.sh` writes `diff.jsonl` from `thinkthen diff ../11-audit/rows.jsonl --threshold 0.5 --compare-threshold <cut> --key ../11-audit/key.jsonl --id /input`. It reads the cut from `../11-audit/audit-asrun.json`.
- **Run flow.**
  - `11-audit/run.sh live|replay` runs the runner, then `tune.sh`. In replay mode, `tune.sh` writes to `replay/`, and the committed files stay as they are.
  - `12-diff/run.sh` takes no mode. It needs no key and sends nothing. It writes to `12-diff/replay/`.
- **Numbers may move.** A fresh live run may change every number in Prior evidence. The pages and slides use the committed outputs. The ticket table stays as the scratch record.

## Work

1. Add both folders with `README.md` pages in ticket 0006's form: the question in plain words, the slide, the command, and an output excerpt. Each excerpt is a `jq` command over a committed JSON file, followed by a fenced `json` block. The pages may also show `--table` output in a fenced `text` block. The number check and the jq check read only `json` blocks.
2. The pages explain the two mistakes in plain words. A low bar says yes too often. A high bar misses real ones.
3. The "With context" section names ticket 0006's decide example with context. There every answer lands near 0 or 1, and the bar matters less. No new context run.
4. Change `tests/test_examples.py`:
   - `FOLDERS` adds `11-audit` and `12-diff`. The required parts become per folder. `12-diff` needs `README.md`, `slide.png`, `run.sh`, `diff.sh`, and `diff.jsonl`, with no recording.
   - `answers()` adds the audit JSON files for `11-audit`. For `12-diff`, it adds `diff.jsonl` and the files from `11-audit`.
   - With `THINKTHEN_BIN` set, `11-audit` replays with no key. Its `outputs.jsonl`, `rows.jsonl`, and audit files match the committed files byte for byte.
   - With `THINKTHEN_BIN` set, `12-diff/run.sh` writes a `diff.jsonl` that matches the committed file byte for byte.
   - If `$THINKTHEN_BIN audit --help` exits nonzero, the audit and diff checks skip with the reason "this thinkthen has no audit or diff".
5. Add `slide.png` to each folder. The scratch source is the marketing session's `gen6.py` and its HTML pages. Point it at the committed `11-audit/outputs.jsonl`, `key.jsonl`, audit files, and `12-diff/diff.jsonl`, then render. If the numbers moved, the slide shows the new ones.

## Limits

The live cap is 25,000 input tokens, through the `sdlc/scripts/live` guard in thinkthen. The scratch run of the same 70 records cost 20,313 input tokens, about 290 each.

## Proof

- `python3 -m unittest discover -s tests` passes with no network.
- Set `THINKTHEN_BIN` to a build of thinkthen main at e70bddab or later. With no key, the example tests pass, including the audit and diff checks.
- The ten 0006 folders still replay unchanged.

## Deferred

- audit and diff over other functions, such as filter or score.
- The docs pages, which belong to the thinkthen queue.

## Done when

The proof passes, a fresh reviewer accepts, and the work is committed and pushed.

## Ticket review 1 (fresh reviewer, 2026-09-25): eight findings, all taken

1. The cap was too low. The scratch run cost 20,313 input tokens. The cap is now 25,000.
2. audit cannot read the wrapped `outputs.jsonl`. `tune.sh` writes `rows.jsonl` first.
3. `--id ''` does not fit the runner's records. Both commands use `--id /input`, and the case ids are named.
4. The 0006 tests would break. The ticket names the per-folder parts, the output files, the `answers()` change, and the block types.
5. The run flow is now stated for both folders.
6. The test compares fresh audit and diff output against the committed files, and it names its skip rule.
7. The bar list is fixed, plus audit's suggested cut.
8. The slide source is named as `gen6.py`, pointed at the committed files.

## Amendment 1 (2026-09-25, Ian): diff compares cold with context

Ian ruled on 2026-09-25 that the diff example compares the cold run with a run that adds context. Two bars on one run repeat audit's result. Two runs show what diff alone does. Two runs need no answer key, and they tie diff to the talk's context slide.

This amendment replaces these earlier parts: Design "diff output" and "Run flow" for `12-diff`, Work item 3's "No new context run", the 25,000 cap in Limits, and the Proof lines on the two-bar diff. The builder rewrites both "With context" sections (`11-audit/README.md` and `12-diff/README.md`) and the header comments of `12-diff/diff.sh` and `12-diff/run.sh`.

- **New live case.** `11-audit` adds `audit-context.jsonl` over the same 70 titles, with ids `audit-context-01` to `audit-context-70` (`one_each("audit-context", ...)`). Each record takes ticket 0006's context shape, `"Catalog:\n<entry>\nText: <title>"` from `catalog.entry()`. The question opens "The text gives a catalog entry and then names a song by the Beatles." The runner asks both cases with `BENCH_TESTS=audit-cold,audit-context` through the shared recording. The cold answers replay free. The cold ids stay `audit-01` to `audit-70`.
- **Rows.** `tune.sh` splits the one `outputs.jsonl`:
  - `rows.jsonl`: `jq -c 'select(.id|startswith("audit-context-")|not)|.rows[]'`
  - `rows-context.jsonl`: `jq -c 'select(.id|startswith("audit-context-"))|.rows[]'`
  - The audit files still grade `rows.jsonl`, the cold run alone.
- **diff.** `12-diff/diff.sh` maps both row files to the title with one filter, `jq -c '.input = {id: (.input.input | split("\nText: ") | last)}'`. It writes them to `DIR/a.jsonl` and `DIR/b.jsonl`, which are not committed. It then runs `thinkthen diff DIR/a.jsonl DIR/b.jsonl --threshold 0.5 --key ../11-audit/key.jsonl` into `diff.jsonl`. It no longer reads `audit-asrun.json`.
- **Page.** `12-diff/README.md` explains diff as "what changed between two runs". It says diff needs no key, and that with a key it marks each flip fixed or broken. It shows the flips and the summary.
- **Slide.** `12-diff/slide.png` shows each flipped song with its cold score, its context score, and fixed or broken. The marketing session supplies `11-audit/slide.png` from its table design.
- **Limit.** The run goes through the `sdlc/scripts/live` guard with `BENCH_MAX_INPUT_TOKENS=40000`. Ticket 0006's context records averaged about 350 input tokens each, which predicts about 25,000 for this run.
- **Tests.**
  - `PARTS["11-audit"]` adds `audit-context.jsonl` and `rows-context.jsonl`.
  - `answers()` for `11-audit` adds `rows-context.jsonl`. The replay test and the number check both read that list.
  - The generator test picks up `audit-context.jsonl` with no change.
  - The `12-diff` byte-for-byte test stays.
- **Proof added.**
  - `rows.jsonl` and every `audit-*.json` match commit 390dbc9c byte for byte.
  - The cold lines of `outputs.jsonl` keep their text and order, and the new lines are only appended.

## Amendment 1 review (fresh reviewer, 2026-09-25): six findings, all taken

1. The rows are split by id, and the context ids are named.
2. The jq step reads the title from both shapes, and the mapped files have named paths.
3. The test changes are listed.
4. The proof protects the cold results.
5. The amendment names the text it replaces.
6. The cap names its guard and its measured basis.
