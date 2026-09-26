# 0013 One folder per function

Owner: the queue owner. Status: done 2026-09-26. Ticket review 1 returned nine findings. All are taken, one in part. Code review 1 returned seven findings, and code review 2 returned two. All are fixed. The record gives the proof.

## Why

Ian ruled on 2026-09-26, after he viewed the first site preview (the deck repo's `sdlc/planning/2026-09-25-site-map-beatles-bench-section.md`, "Ian's rulings of 2026-09-26"): "The bench repo keeps a structure that runs the whole bench, and gains one folder per function, such as `functions/decide/`. Each folder has a short README with how to run it, the lessons, and a link back to its thinkthen.dev page, one `run` script with subcommands, and its data."

The repository then serves two readers. One runs the whole bench with `./run.sh`. The other opens one function's folder and sees the slide, runs it, and finds how the example was built, what it assumed, and its data.

The thinkthen.dev pages will link to `https://github.com/botassembly/beatles-bench/tree/main/functions/<name>`. Those paths are fixed by this ticket.

The unlanded branch `preview/site-pages`, in its own worktree at an earlier commit, holds the first preview's pages. Ian rejected that direction. This ticket supersedes it and builds from main. The branch stays as it is.

## Prior evidence

- `examples/` holds twelve numbered folders, `01-decide` to `12-diff`, and `context-article/`. Git tracks 342 files there.
- Each of `01` to `11` holds its case files, `outputs.jsonl`, `timing.tsv`, `recording/`, `slide.png`, a `run.sh` of `live OUT | replay [OUT]`, and a long page as `README.md` (86 to 189 lines). `05-filter` and `06-rank` add `lists/`. `11-audit` adds `tune.sh`, `key.jsonl`, the rows, and the audit files. `12-diff` holds `diff.sh`, `diff.jsonl`, `slide.png`, and its page.
- Twelve folders hold a `run.sh`. The ten of `01` to `10` differ only in `BENCH_TESTS` and their usage line. They call `scripts/run/functions.sh`. `functions.sh` calls `functions.py`. None calls `thinkthen` directly. `11-audit/run.sh` then runs `tune.sh`. `12-diff/run.sh` runs `diff.sh`.
- `./run.sh` replays every numbered folder through its `run.sh` and checks the files byte for byte. `tests/test_run_sh.py` checks its printed lines, `replayed examples/NN-name`.
- `tests/test_examples.py` checks the folders, the generator output, and every command on every page listed in `docs/README.md`.
- `scripts/generate/examples.py` writes the case files into `examples/NN-name/`.
- The talk deck `decks/2026-09-24-thinkthen-beatles` reads the bench. `build-functions.py` quotes sections and phrases of `examples/01-decide/README.md` to `10-relate/README.md`. `build.sh` replays those ten through their `run.sh`. `build-graph.py` reads `examples/11-audit/`. `build-open.py` and `jev_facts_test.py` read `examples/02-choose/outputs.jsonl`. `build-end.py` quotes the top README, including "every example in `examples/`".
- thinkthen `score`, `rank`, `find`, and `annotate` take no `--threshold`. `annotate` keeps a bar per field in its card. `decide`, `choose`, `tag`, `filter`, `recognize`, and `relate` take `--threshold`. `audit` and `diff` read standard input as `-`.
- The suite on main passes with a local thinkthen build: 173 tests, one skipped. A second local build now prints precision and F1 in audit's output, and five tests fail with it. It no longer matches its README's commit `02dc0b96`.

## Retained behavior

- Every data file moves with `git mv`. `git log --follow` then finds its history. No case, answer, recording, timing, list, key, audit file, or slide changes by one byte.
- `./run.sh` keeps its arguments, its replay checks, its live path, and its tables. Only its printed folder names change.
- A live run of the full bench still writes each function into `results/runs/<today>-examples-<NAME>/<function>/`. The committed `results/runs/2026-09-25-examples-jev/NN-name/` folders stay as they are.
- Each long page keeps its commands, its printed blocks, its sections, and its explanations. Every command on it still prints the block below it. The changes are listed in change 2.
- The generator writes the same bytes.
- No script reads, prints, or passes `THINKTHEN_API_KEY`.

## Changes

1. **Folders.** `git mv examples/NN-name functions/name` for all twelve: `decide`, `choose`, `tag`, `score`, `filter`, `rank`, `find`, `annotate`, `recognize`, `relate`, `audit`, `diff`. `examples/context-article/README.md` moves to `docs/context-article.md`. `examples/` goes.
2. **The long page.** Each `README.md` moves to `docs/walkthroughs/<name>.md` with `git mv`. The folder then holds only the README, `run`, and the data. These parts of each page change:
   - the links, the slide image path, and "Run this in" name the new folder
   - "The files" names the new `run` and drops the old `run.sh`
   - the audit page's `run.sh replay`, `run.sh live OUT`, and `tune.sh` lines name `scripts/run/example.sh audit` and `scripts/score/tune.sh`
   - the diff page's `diff.sh` and `run.sh` lines name `scripts/score/context_diff.sh`, and its paths read `../audit`
   - `docs/run-it-for-free.md` gives the same commands with the new paths
3. **The short README.** Each folder gets a new `README.md`. It holds:
   - a title, the slide image, and a sentence or two on what the slide shows
   - `./run` and its printed output, `./run threshold X` at another bar and its output, and `./run live`
   - the two lessons, "You control the bar" and "The number is the number", each with this slide's own case
   - one short list of the files. The last line links `docs/walkthroughs/<name>.md`. That page shows how the example was built and what it assumed.
   - the link `https://thinkthen.dev/learn/beatles-bench/<name>/`

   It repeats nothing the top README says.
4. **The `run` script.** Each folder gets one executable POSIX `sh` script named `run`. It calls `thinkthen` directly and shapes the output with `jq`. It is the slide's command.
   - `./run` answers from `recording/` with `--replay recording`. No key, no network.
   - `./run live` swaps `--replay recording` for `--no-cache` and asks the server `THINKTHEN_BASE_URL` names. No answer comes from a cache. thinkthen reads the key itself.
   - `./run threshold X` sets the bar. For `decide`, `choose`, `tag`, `filter`, `recognize`, and `relate`, it passes `--threshold X`. For `annotate`, it writes a copy of the card with every field's bar set to X. For `audit` and `diff`, it grades again at X. `score`, `rank`, and `find` take no bar. There `jq` applies X, as a program would. The table below gives each one. These three and `annotate` refuse a band with the usage line. Every `run` refuses a bar with any character other than a digit, a point, or a colon. jq or thinkthen refuses the rest.

| Function | Field `jq` compares with X | Printed | `./run` default |
| --- | --- | --- | --- |
| `score` | the probability of the likeliest level | `level` is null under X, as not sure | no bar |
| `rank` | the probability of yes | `over` is true at X or more | 0.8, the slide's bar |
| `find` | the probability of the pick | `pick` is null under X, as not sure | no bar |

   - `live` and `threshold` combine: `./run live threshold 0.3:0.7`.
   - `audit`'s `./run` asks the 70 songs from `recording/` and grades the answers against `key.jsonl`. Its `live` asks them of the server: 70 calls. `diff`'s `./run` asks the 70 songs cold and with the catalog entry from `../audit/recording/` and compares them. Its `live` asks both sets of the server: 140 calls. Each README states its call count for `live`.
   - Temporary files go to `mktemp -d` and are removed on exit. A live run writes nothing into the folder.
5. **The full-bench path.** The twelve per-folder `run.sh` files go. One script, `scripts/run/example.sh NAME live OUT | replay [OUT]`, holds each function's case list and calls `functions.sh`. For `audit` it then runs `tune.sh`. `examples/11-audit/tune.sh` moves to `scripts/score/tune.sh`, and `examples/12-diff/diff.sh` to `scripts/score/context_diff.sh`, both with `git mv`. `tune.sh` then reads `key.jsonl` from `functions/audit/`. `context_diff.sh` finds `diff_guard.sh` from the repository root and defaults to `functions/audit` and `functions/diff`. `./run.sh` calls them in the talk's order, kept in one list in `run.sh`. `.gitignore` follows the new paths and keeps the pattern for the committed `12-diff` run folder.
6. **Generator.** `scripts/generate/examples.py` writes into `functions/<name>/`.
7. **Docs.** The top README says once what a function folder holds and how the two readers use the repository. Its map lists `functions/`. `docs/README.md` lists each walkthrough. `docs/context-and-cost.md`, `docs/run-it-for-free.md`, `docs/the-data.md`, and `scripts/README.md` name the new paths. `scripts/README.md` keeps the sentence the deck quotes: "A rerun answers unchanged questions from the recording and sends only the new ones." The docs README drops its line about a site that pulls these pages.
8. **Tests.** `tests/test_examples.py` becomes `tests/test_function_folders.py` and follows the new paths. It adds:
   - each README's `./run` blocks print the block below them, with a build present and no key or address. The prose number check covers the READMEs.
   - each README links `https://thinkthen.dev/learn/beatles-bench/<name>/` and names both lessons. The site links to these folders, and the pages link back.
   - one edge-case table: an unknown subcommand, `threshold` with no value, a bar that is not a number, and a band for `score`, `rank`, `find`, and `annotate` each print the usage line and exit 2 with no network.
   `tests/test_run_sh.py` expects `replayed functions/<name>`.

## Proof

- `python3 -m unittest discover -s tests` passes with no `THINKTHEN_BIN` and no network.
- With `THINKTHEN_BIN` set to the first local build and no key, the suite passes. That build passes on main today.
- `./run.sh` with no address and no key passes and prints `replayed functions/<name>` for all twelve.
- Every `./run` and `./run threshold X` in replay prints what its README shows. The test above proves it. The audit and diff blocks match the first local build. A build whose audit prints precision and F1 changes them.
- `git log --follow` on one moved recording file and one moved long page reaches its pre-move history.
- `git diff --stat -M main` shows every data file as a rename with no change.
- The generator writes the committed bytes.
- `git grep -n "examples/" -- . ':!sdlc' ':!results/runs'` finds no stale path. A grep for the numbered folder names, such as `01-decide`, finds none outside `sdlc/` and `results/runs/`.
- `git status` is clean after the suite.
- `git grep -n -E "run\.sh|functions\.sh" -- 'functions/*/run'` prints nothing. Each `run` calls `thinkthen` directly.
- No live call runs. No key is set or read.

## The deck

Before landing, the record lists every bench path and quote the talk deck reads, each with its new path or the reason it stays. A Quick Fix in the deck repository's own worktree on `ticket/qf-bench-function-folders` makes the matching change. The known reads:

| Deck file | Reads | After this ticket |
| --- | --- | --- |
| `build-functions.py` | sections and phrases of `examples/NN-name/README.md`, and those paths in its notes | `docs/walkthroughs/<name>.md` |
| `build.sh` | `examples/NN-name/run.sh replay` for the ten, and the check that `run.sh` exists | `scripts/run/example.sh <name> replay` |
| `build-graph.py` | `examples/11-audit/` files, and `examples/12-diff/diff.sh` in its notes | `functions/audit/`, `scripts/score/context_diff.sh` |
| `build-open.py`, `jev_facts_test.py` | `examples/02-choose/outputs.jsonl` | `functions/choose/outputs.jsonl` |
| `build-end.py` | the top README's "Run it yourself" commands and its replay sentence | the new replay sentence |
| `build-end.py`, `build-cache.py` | the `scripts/README.md` sentence on reruns | stays word for word |
| `build-sql.py` | `examples/05-filter/recording` at an earlier bench commit, in its notes | stays. It names a past commit. |
| `talking-points.md` | the reminder naming `examples/01-decide` to `examples/10-relate` | `functions/decide` to `functions/relate` |

The deck build must pass with 28 slides against the new bench commit. The deck change lands right after the bench.

## Owner's decisions (Ian can overturn each)

- The long pages stay, as `docs/walkthroughs/<name>.md`. They show how each example was built and what it assumed. The deck quotes them. The folder holds only the README, `run`, and the data. Dropping the pages would mean rewriting the deck's notes.
- The folder names drop their numbers, to match the site links. The talk's order lives in `run.sh` and `docs/README.md`.
- The full-bench machinery moves out of the folders into `scripts/`. Each folder then has one executable.
- `run` needs `jq`, as the long pages already do. It calls `thinkthen` from `PATH`.
- The unknown-subcommand table and the README link check stay. Ticket review 1 asked to drop the README check. The README link is the folder's contract with the site. One check guards it.
- For a function with no bar option, `./run threshold X` marks the answers in `jq`. That shows a program owns the bar.
- New live runs keep the `examples-<NAME>` run folder name. They then sit beside the committed ones.
- The proof uses the first local build. The 9c609296 build the last preview needed has no known binary, and this one passes on main.

## Deferred

- The thinkthen.dev pages behind the README links. The site does not serve them yet.
- Moving the bench to a thinkthen build whose audit prints precision and F1. The audit files and the audit and diff README blocks then need regenerating.
- The second local build no longer matches its README's commit. The fix belongs in that local experiment's README.
- `preview/site-pages` stays unlanded and superseded.

## Done when

The proof passes, a fresh reviewer accepts the code, the bench lands on main by fast-forward and is pushed, and the deck change lands right after.

## Ticket review 1 (fresh reviewer, 2026-09-26): nine findings, all taken, one in part

1. The long pages change more than their paths. Change 2 lists each change.
2. The long pages move to `docs/walkthroughs/`. The folder holds the README, `run`, and the data.
3. The `threshold` rule for `score`, `rank`, and `find` is a table. A band is refused.
4. Twelve `run.sh` files go. The edits to the moved `tune.sh` and `diff.sh` are named.
5. The `live` call counts are named, and each README states its own.
6. The presence, `sh -n`, and `run.sh` name checks go. The last is a proof grep. The README link check stays, as the decisions say.
7. The deck table lists each read with its new path or why it stays.
8. The proof names the build the audit and diff blocks match. A usage test covers bad subcommands.
9. The prose splits its trailing clauses.
