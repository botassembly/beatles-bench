# 0007 Worked examples for audit and diff

Ticket: [0007](../tickets/0007-audit-and-diff-examples.md). Branch `ticket/0007-audit-diff-examples`. Built 2026-09-25 by the builder on the local Linux machine.

## What landed

- `examples/11-audit/`: the case file `audit-cold.jsonl` (records `audit-01` to `audit-70`), `key.jsonl`, `recording/`, `outputs.jsonl`, `timing.tsv`, `rows.jsonl`, `audit-asrun.json`, one `audit-BAR.json` for each bar in 0.5, 0.6, 0.7, 0.8, 0.9, 0.95 and the suggested cut 0.85, `run.sh live|replay`, `tune.sh [DIR]`, `slide.png`, and `README.md`.
- `examples/12-diff/`: `diff.jsonl`, `diff.sh [DIR]`, `run.sh`, `slide.png`, and `README.md`. It has no recording.
- `scripts/generate/examples.py` writes the audit case file and the key from `data/songs.tsv`. The 70 titles sit in the generator as a fixed list. A comment says they were chosen by hand for the talk. The key matches the scratch key line for line.
- `tests/test_examples.py`:
  - `FOLDERS` adds `11-audit` and `12-diff`, and each folder has its own list of required parts.
  - `answers()` adds `rows.jsonl` and the audit files for `11-audit`. For `12-diff` it adds `diff.jsonl` and the `11-audit` files.
  - Two new replay checks compare fresh audit and diff output with the committed files byte for byte.
  - Both skip with "this thinkthen has no audit or diff" when `$THINKTHEN_BIN audit --help` exits nonzero.
- The root README's map and `scripts/README.md` name the two new folders.

## Commands and results

- Live: `sdlc/scripts/live --max-tokens 25000 JOB` in the thinkthen checkout. The job was a `#!/bin/sh` script outside the repository. It set `THINKTHEN_BIN` to the thinkthen release build of main at e70bddab, `BENCH_WORKERS=4`, and `BENCH_MAX_INPUT_TOKENS=23500`, then ran `examples/11-audit/run.sh live`. The key reached only the command, through the guard.
- Ledger before: 427,994,418 charged, 48,005,582 remaining. After: 428,019,418 charged, 47,980,582 remaining. The guard precharges the full 25,000.
- Spend: 70 calls, 70 requests, 20,313 input and 1,470 output tokens (jev-1.13.0). The scratch run of the same records also cost 20,313 input tokens.
- `examples/12-diff/diff.sh` wrote the committed `diff.jsonl` with no request.
- `grep -ril` for authorization and bearer found no match in either folder.
- Suite with no key and no `THINKTHEN_BIN`: `env -u THINKTHEN_API_KEY -u THINKTHEN_BIN HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 python3 -m unittest discover -s tests` ran 181 tests, OK, 12 skipped.
- Suite with `THINKTHEN_BIN` set to the e70bddab build and no key, same proxy settings: 181 tests, OK, 2 skipped. Neither skip is an example test. The ten 0006 folders replay byte for byte.
- Skip rule: with the thinkthen release build of 2026-09-23, `audit --help` exits 2 and both new checks skip with the named reason. That build also fails to replay `09-recognize`. That failure comes from ticket 0006's folder and the old build. This ticket did not cause it.

## Final numbers

Right answers of 70 at each bar, from the committed audit files:

| Bar | Right | Said yes, wrong | Said no, wrong |
| --- | --- | --- | --- |
| 0.5 | 56 | 14 | 0 |
| 0.6 | 62 | 8 | 0 |
| 0.7 | 64 | 6 | 0 |
| 0.8 | 64 | 4 | 2 |
| 0.85 | 66 | 2 | 2 |
| 0.9 | 66 | 2 | 2 |
| 0.95 | 64 | 0 | 6 |

- Suggested cut 0.85, tuned on a seeded half of 35 and checked on the other 35. Agreement at the cut is 0.943 on both halves.
- AUC 0.967 (0.96712).
- Wrong at 0.85: A Day in the Life 0.94 and The Long and Winding Road 0.91 say yes. Something 0.77 and Octopus's Garden 0.75 say no.
- Before Amendment 1, diff compared 0.5 with 0.85 on the cold run: 14 flips, 12 fixed, 2 broken (Something 0.77 and Octopus's Garden 0.75), 56 to 66 right, McNemar p 0.013. Amendment 1 replaced that diff. Its numbers are below.

## Slides

This section describes the first build. Amendment 1 replaced both slides, as its section below says.

- The slide source is a copy of the deck's slide source, outside the repository. The originals are unchanged.
- The copy reads `11-audit/rows.jsonl` (title from `input.input`), `11-audit/key.jsonl`, `11-audit/audit-asrun.json`, `11-audit/audit-{0.5,0.85}.json`, and `12-diff/diff.jsonl`. The copy drops three reads of other scratch runs that the slides never use.
- Rendered with the deck's slide source, then copied to each folder's `slide.png`.
- The audit slide's `SPOT` now labels the four mistakes at 0.85. Martha My Dear is no longer a mistake. Octopus's Garden sits above left, Something below left, The Long and Winding Road below right, and A Day in the Life above right. No label crosses a dot or a bar line.
- The diff slide has 14 rows. The row height went from 48 to 44 pixels, so the last row ends above the question at the bottom.

## Stopped or changed from the ticket

- The numbers moved. The runner passes `--details`, and every answer line then carries the bar it was asked with, 0.5. The scratch lines carried none, so the scratch "as run" grade was all unresolved. 55 of 70 probabilities moved, by at most 0.09. The suggested cut is 0.85, not 0.83. The files hold `audit-0.85.json`, and there is no `audit-0.83.json`. The pages and slides use the committed numbers. The ticket table stays as the scratch record.
- The pages quote `--table` output in `text` blocks. The number check reads only `json` blocks, as the ticket says.
- `tune.sh` and `diff.sh` take an optional output folder. `run.sh replay` passes `replay/`.
- The machine blocks `unshare`, so the no-network run could not remove the network. It ran with no key, with no `THINKTHEN_BIN`, and with every proxy variable pointed at a closed port. No test needs the network.
- The root README and `scripts/README.md` gained one line each. The ticket did not name them.

## Amendment 1: diff compares cold with context

Built 2026-09-25 from the amended ticket at an earlier commit.

What changed:

- `scripts/generate/examples.py` writes `11-audit/audit-context.jsonl`: the same 70 titles in ticket 0006's context shape, ids `audit-context-01` to `audit-context-70`.
- `11-audit/run.sh` asks `BENCH_TESTS=audit-cold,audit-context` through the one recording. `tune.sh` splits `outputs.jsonl` by id into `rows.jsonl` and `rows-context.jsonl`. The audit files still grade the cold rows alone.
- `12-diff/diff.sh` maps both row files to the title with the ticket's jq filter into `DIR/a.jsonl` and `DIR/b.jsonl`. It then runs `thinkthen diff DIR/a.jsonl DIR/b.jsonl --threshold 0.5 --key ../11-audit/key.jsonl`. It no longer reads `audit-asrun.json`. `.gitignore` adds `examples/12-diff/a.jsonl` and `b.jsonl`, so a run into the folder itself leaves nothing to commit.
- Both pages were rewritten where the ticket names: the `12-diff` page, both "With context" sections, and the header comments of `diff.sh` and `run.sh`. The `11-audit` page also describes the new table slide and the new cold-only rows command.
- `tests/test_examples.py`: `PARTS["11-audit"]` adds `audit-context.jsonl` and `rows-context.jsonl`, and `answers()` adds `rows-context.jsonl`.
- The root README's map line now says what each of the two folders shows.

Live run:

- `sdlc/scripts/live --max-tokens 40000 JOB`, the same job with `BENCH_MAX_INPUT_TOKENS=40000`.
- Ledger before: 428,019,418 charged, 47,980,582 remaining. After: 428,059,418 charged, 47,940,582 remaining. The guard precharged 40,000.
- Spend: 70 new calls, 70 requests, 24,801 input and 1,470 output tokens (jev-1.13.0), about 354 input tokens per record. The 70 cold cases replayed from the recording at no cost.
- `grep -ril` for authorization and bearer found no match in either folder.

Proof:

- `rows.jsonl` and every `audit-*.json` match an earlier commit byte for byte (`git diff --quiet` against it).
- The first 70 lines of `outputs.jsonl` equal the whole file at that earlier commit. The 70 context lines follow them. `timing.tsv` only gained rows.
- Suite with no key and no `THINKTHEN_BIN`, proxies pointed at a closed port: 181 tests, OK, 12 skipped.
- Suite with `THINKTHEN_BIN` set to the e70bddab build and no key, same proxies: 181 tests, OK, 2 skipped. Neither skip is an example test.

Final numbers:

- Context run: 7 songs get a yes, all at 0.95 or 0.96. The other 63 sit from 0.02 to 0.1.
- diff, cold against context, both at 0.5: 14 of 70 change, all from yes to no. 14 are fixed and 0 are broken. Right answers go from 56 to 70. McNemar p is 0.000122.
- The flips, cold then context: A Day in the Life 0.94 to 0.04, The Long and Winding Road 0.91 to 0.07, Piggies 0.84 to 0.03, Martha My Dear 0.82 to 0.03, Lovely Rita 0.78 to 0.03, Blackbird 0.72 to 0.03, The Ballad of John and Yoko 0.67 to 0.09, Get Back 0.61 to 0.04, Good Night 0.57 to 0.04, Taxman 0.56 to 0.03, Back in the U.S.S.R. 0.55 to 0.03, Julia 0.54 to 0.03, Hello, Goodbye 0.53 to 0.04, Don't Pass Me By 0.51 to 0.02. The key says no for every one.

Slides:

- `11-audit/slide.png` is the queue owner's table design, copied unchanged from the deck's slide source. That source reads the committed cold `rows.jsonl`, `key.jsonl`, and `audit-asrun.json`. The F1 line at 0.75 and the rules on its left are the queue owner's design. audit itself suggests only the most-right-answers bar.
- `12-diff/slide.png` comes from a new page in the deck's slide source. It uses the audit slide's table style. Each changed song shows its cold score, its context score, and fixed or broken. A score is green when it is right at 0.5 and red when it is wrong. The left side gives 56 to 70 right, 14 changed with 14 fixed and 0 broken, and the McNemar p. The question "Is it on Abbey Road?" stays at the bottom. The render has no overlaps.

Changes from the amendment:

- None in behavior. The `.gitignore` lines for `a.jsonl` and `b.jsonl` are an addition the amendment did not name.

## Left open

- audit and diff over other functions, and the docs pages, stay deferred as the ticket says.
- The slide source is not in the repository. Ticket 0006's slides also came from scratch. The talk's owner decides whether the generator moves in.

## Code review of amendment 1 (fresh reviewer, 2026-09-25): two findings, both taken

1. "key" meant both the answer key and the API key. The pages and script comments now say "answer key" or "API key".
2. The audit page now says audit picks its bar only by the most right answers today. The slide's precision, recall, and F1 lines are worked out by hand. ThinkThen issue `2026-09-25-audit-picks-its-cut-only-by-most-right-answers.md` asks for all four.

The queue owner replaced `11-audit/slide.png` with Ian's four-score design of 2026-09-25. Each dashed line marks the bar that gives one score its best value: precision 100%, accuracy 94%, recall 100% with F1 74%, and the default.
