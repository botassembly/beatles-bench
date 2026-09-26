# 0013 One folder per function: record

Built on 2026-09-26 on `ticket/0013-function-folders` from main at c1b92610. No model call ran. No key was set or read.

## Result

- `functions/` holds twelve folders: `decide`, `choose`, `tag`, `score`, `filter`, `rank`, `find`, `annotate`, `recognize`, `relate`, `audit`, and `diff`. Each holds a short `README.md`, one executable `run`, and its data.
- Every data file moved with `git mv`. `git diff -M main` lists 331 renames. The 315 data files and slides are 100% renames. The other 16 are the pages, the two moved scripts, and the moved test. `git log --follow` on `functions/decide/recording/14d3568a....json` and on `docs/walkthroughs/decide.md` reaches the commits before the move.
- The long pages moved to `docs/walkthroughs/<name>.md`. Their commands and printed blocks stay. Their paths, their file lists, and the audit and diff script names changed.
- `examples/context-article/README.md` moved to `docs/context-article.md`. `examples/` is gone.
- `scripts/run/example.sh` replaces the twelve per-folder `run.sh` files for the full bench. `tune.sh` moved to `scripts/score/tune.sh`. `diff.sh` moved to `scripts/score/context_diff.sh`.
- Each `run` calls `thinkthen` directly. `./run` replays. `./run threshold X` sets the bar. `./run live` asks the server with `--no-cache`. Each README shows `./run` and `./run threshold X` with their printed output.
- The top README says once what a folder holds and how to run it. Its map lists `functions/`.

## Proof

Environment: the local Linux machine. `THINKTHEN_BIN` was `experiments/259-talk-claims/thinkthen`, SHA-256 `eb4a5713`. That build passes the suite on main. `experiments/264-bench-rerun/bin/thinkthen` now prints precision and F1 in audit, and five tests fail with it on main too.

- `python3 -m unittest discover -s tests` with the build and no key: 175 tests, OK, 2 skipped. The skips are the chat backend's missing module and the local `data/raw/` cache.
- The same with no build and no `thinkthen` on `PATH`: 175 tests, OK, 22 skipped.
- `./run.sh` with no address and no key passed. It printed 13 lines that start with "replayed", one per function folder after the Jev run.
- Every `./run` and `./run threshold X` in replay printed the block its README shows. `tests/test_function_folders.py` runs each one.
- A stub `thinkthen` on `PATH` showed `./run live threshold 0.3` passes `--threshold 0.3 --no-cache` and no `--replay`.
- The generator wrote the committed bytes.
- `git grep` finds no `examples/` path and no numbered folder name outside `sdlc/` and `results/runs/`.
- `git grep -n -E "run\.sh|functions\.sh" -- 'functions/*/run'` prints nothing.
- `git status` was clean after the suite.

## The deck

The talk deck `decks/2026-09-24-thinkthen-beatles` reads these bench paths and quotes. Commits 640a424 and 6e48f90 on the deck repo's `ticket/qf-bench-function-folders` move each one.

| Deck file | Before | After |
| --- | --- | --- |
| `build-functions.py` | sections, the "Here" opening, the first command, and phrases of `examples/NN-name/README.md` | `docs/walkthroughs/<name>.md` |
| `build-functions.py` | `outputs.jsonl`, `lists/`, case files, and the annotate card in `examples/NN-name/` | `functions/<name>/` |
| `build.sh` | `examples/NN-name/run.sh replay` for the ten, and the check that `run.sh` exists | `scripts/run/example.sh <name> replay`, and the check that it exists |
| `build-graph.py` | `examples/11-audit/` `rows.jsonl`, `rows-context.jsonl`, `key.jsonl`, and `audit-asrun.json`, and `scripts/score/diff_guard.sh` | `functions/audit/`, and the guard unchanged |
| `build-graph.py` notes | `examples/12-diff/diff.sh` and `diff.jsonl` | `scripts/score/context_diff.sh` and `functions/diff/diff.jsonl` |
| `build-open.py`, `jev_facts_test.py` | `examples/02-choose/outputs.jsonl` | `functions/choose/outputs.jsonl` |
| `build-end.py` | the top README's "Run it yourself" commands, "`./run.sh NAME` names the folders.", and "every example in `examples/`." | the commands and the NAME sentence unchanged, and "every function folder in `functions/`." |
| `build-end.py`, `build-cache.py` | the `scripts/README.md` sentence "A rerun answers unchanged questions from the recording and sends only the new ones." and the key sentence | unchanged |
| `build-bench.py`, `build-problems.py`, `build-open.py` | `results/`, `reports/`, `data/`, `questions/`, `paper/notes.md`, and ticket 0009 | unchanged |
| `build-sql.py`, `build-open.py` | `examples/05-filter/recording` and `examples/11-audit/recording` at past bench commits | unchanged. They name a past commit. |
| `talking-points.md`, `storyboard.md` | `examples/01-decide` to `examples/10-relate` | `functions/decide` to `functions/relate` |

`build.sh` with `BEATLES_BENCH` at this branch exited 0. It printed "10 bench function examples replay unchanged" and "28 slides". The sweep, fit, and colour checks reported 0 findings. The PDF holds 28 pages. Among the built outputs, only the NOTES of the bench slides and the PDF changed. No slide image changed.

## Reviews

- Ticket review 1 returned nine findings. All are taken, one in part. The ticket lists them.
- Code review 1 returned seven findings. All are fixed in 433b15b9 and the deck repo's 6e48f90:
  1. `./run live` could answer from the default cache. It now passes `--no-cache`.
  2. `docs/context-article.md` named the old annotate card path.
  3. Numbered folder names stayed in two walkthroughs and `scripts/README.md`.
  4. "This folder" in two walkthroughs pointed at `docs/walkthroughs/`.
  5. The top README promised a band for every function. `annotate` now refuses a band with its usage line.
  6. Bar values went to `thinkthen` unquoted and unchecked. Each `run` now checks the value and quotes it. The test table gained two rows.
  7. The deck notes named `examples/12-diff/diff.jsonl`, and `storyboard.md` named the old folders.
- Code review 2 confirmed the seven fixes and returned two findings. Both are fixed in the record commit:
  1. The ticket said every `run` refuses a bar that is not a number. The check refuses only other characters. jq or thinkthen refuses the rest. The ticket now says so.
  2. The top README said each README names the functions that take a band. It now names them: `decide`, `audit`, and `diff`. The audit README says it takes a band.

## Open

- The thinkthen.dev pages behind the README links do not exist yet.
- The audit files and the audit and diff README blocks need regenerating when the bench moves to a build whose audit prints precision and F1.
- `experiments/264-bench-rerun/README.md` names commit `02dc0b96`. Its binary changed on 2026-09-25 and no longer matches. The deck repo's issue `2026-09-26-pinned-thinkthen-build-moved.md` covers it.
- `preview/site-pages` stays unlanded. This ticket supersedes it.
