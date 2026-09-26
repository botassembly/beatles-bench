# 0017 Rename the three "functions" folders and give each slide one example folder

Owner: the queue owner. Status: done. Waits for ticket 0016 to land. Ticket review 1 covered 0016 and 0017 together. Its findings 12 to 17 and the 0017 parts of 11 apply here. Review 2 findings 5 to 7, review 4 finding 2, and review 5 finding 3 apply here. All are taken. Review 8 returned ACCEPT for both tickets.

## Why

Three different things share the name "functions". `functions/` holds one folder per talk slide. `questions/functions/` holds the function suite. The headline tables score it. `scripts/generate/functions.py`, `scripts/run/functions.py`, and `scripts/score/functions.py` build, ask, and score that suite. A first-time reader cannot tell a slide's example from the suite.

The reviewer of 2026-09-26 also found deck slides with no bench folder and no bench check. A reader who sees a slide should find one folder that gives its source, its check, and the thinkthen build that made its answers.

The queue owner decided each change below on 2026-09-26. Ian can overturn each one. "Owner's decisions" lists them.

## Why this is its own ticket

Ticket 0016 rewrites prose, deletes pages, and moves old runs. This ticket moves paths that code reads: every test's path constant, `run.sh`, and `scripts/run/example.sh`. The deck's build scripts read the same paths. The deck issue carries their change. A reviewer checks a move by `git diff -M`. That check works only when the diff holds no prose rewrite. The new slide folders also need a read of each slide, which 0016 does not need. So 0016 lands first, and this ticket follows on its main.

## Prior evidence

- The reviewer's report of 2026-09-26 lists the slides with no bench check: 1, 4 (306 songs, 1,501 questions), 11 (a live recording with no build named), 22 (sql), 26 (open book 35% and 94%), 27 (a batching line from a local experiment), and 29 (hardcoded). Slide 25 has checks against copies from a local experiment. Slide 24 has checks for only 67.0% and 96.2%. The 2026-09-26 Jev run (build 02dc0b96) backs slides 3 and 28.
- The deck of 2026-09-26 has 30 slides. Its `order.txt` numbers each slide folder from its place in the list. Two Quick Fixes on 2026-09-26 added slides, and each one moved the numbers of every later slide.
- Each slide's notes name its bench sources. By slide name:
  - `decide`, `choose`, `tag`, `score`, `filter`, `rank`, `find`, `annotate`, `recognize`, `relate`, `audit`, and `diff` read their function folders. `tests/test_function_folders.py` replays each folder and checks its files.
  - `recognize-how` replays `functions/recognize/recording` with `--details`. No bench test checks the values it shows.
  - `sql` reads `functions/filter/recording` at the band 0.3:0.7. No bench test checks its 0, 1, and NULL cells.
  - `jev` and `bench-run` read the Jev row of `results/tables/cost.tsv` and the 2026-09-26 Jev run's `loadavg.txt` and `run.txt`.
  - `strings` reads one cell of `data/songs.tsv` and the chance and embeddings cells of `reports/results.md`.
  - `bench` reads the row counts of `data/songs.tsv` and `data/albums.tsv`.
  - `what-jev-knows` shows four bars. Three come from `results/tables/accuracy.tsv`: embeddings, Jev, and GLM. The random bar comes from the Chance row of `reports/results.md`.
  - `open-book` reads the "all" row of `reports/open-book.md`.
  - `catches` shows three bench questions with Jev's answers. Its check reads copies from a local experiment.
  - `know-this` reads the Jev row of `results/tables/cost.tsv`. Its "4× cheaper" line cites a batching measurement in a local experiment.
  - `title`, `runs-in`, and `filter-live` show runs the deck recorded live itself. `backends` shows a `thinkthen check` output the deck holds as text.
  - `scripting`, `systems`, `frames`, and `close` show no bench data.
- Eleven function folders hold a recording. `diff` holds none: it compares the audit folder's saved rows. Each of the eleven `recording/` folders holds the same file names as the matching folder of `results/runs/2026-09-25-examples-jev`. Ticket 0016 moves that run to `results/archive/runs/`. Its `run.txt` names thinkthen main at 02dc0b96, SHA-256 `eb4a5713...`, and the model jev-1.13.0. No function folder names its build today.
- The function folder READMEs link `https://thinkthen.dev/learn/beatles-bench/<name>/`. `tests/test_function_folders.py` checks that link for each folder.
- The talk deck's build scripts and notes read `functions/<name>/` paths on 119 lines. `scripts/score/functions.py` appears in its bench notes.

## Retained behavior

- Every file in a moved folder keeps its bytes. Every recording, answer, question, table, and `results/history.tsv` keeps its bytes.
- `./run.sh` with no address replays the newest Jev run and every function folder byte for byte, `diff` included.
- Each function slide's folder keeps its name. The website route `/learn/beatles-bench/<name>/` stays.
- The run labels `functions-jev`, `functions-glm-5.3-flash`, and `functions-laya` stay. The tables `results/tables/functions*.tsv` keep their names. `results/history.tsv` rows name them.
- `sdlc/` tickets and records keep the old paths. Each records what was true on its date.
- No paid call is made.

## Changes

1. **examples/.** `git mv functions examples`. `examples/README.md` holds one table in the deck's order. Each row gives the slide's number on 2026-09-26, its name, what it shows, its folder or "the deck holds it", its source files, its check, and its build.
2. **Slide folders.** Each slide that shows bench data gets `examples/<slide-name>/`. The name drops the deck's number. The twelve function folders keep their files. New folders hold a `README.md` that names the slide's claims, their sources, and the test that checks them. The new folders are `jev`, `strings`, `bench`, `recognize-how`, `sql`, `what-jev-knows`, `catches`, `open-book`, `know-this`, and `bench-run`.
3. **Builds.** Each recorded folder gets a `run.txt` in the form of a run folder's: the thinkthen version line, the SHA-256, the model the backend reported, and the date. The eleven recorded function folders take them from the archived `2026-09-25-examples-jev/run.txt`. `examples/diff/README.md` names the audit folder's `run.txt` as the build of the rows it compares. `diff` itself calls no model. A folder that reads a run names that run's `run.txt`. A number with no recorded build says "build not recorded" in its README.
4. **Suite rename.** `git mv questions/functions questions/suite`. `scripts/generate/functions.py` becomes `scripts/generate/make_suite.py`. `scripts/run/functions.py` becomes `scripts/run/ask_suite.py`, and `scripts/run/functions.sh` becomes `scripts/run/ask_suite.sh`. `scripts/score/functions.py` becomes `scripts/score/score_suite.py`. `tests/test_functions.py` becomes `tests/test_suite.py`. `tests/test_function_folders.py` becomes `tests/test_examples.py`.
5. **Readers of the paths.** `run.sh`, `scripts/run/example.sh`, `scripts/run/chat.py`, `scripts/score/context_diff.sh`, `scripts/score/tune.sh`, `scripts/generate/examples.py`, `scripts/score/table.py`, `reports/results.md`, `results/README.md`, `.gitignore`, every test, and every README follow the new paths. The `functions` subcommand of `chat.py` becomes `suite`. `.gitignore` names `examples/*/replay/` and `examples/diff/[ab].jsonl`.
6. **run.sh.** `run.sh` replays every function folder in the deck's order, with `diff` after `audit`. `diff` still replays from audit's rows and checks `diff.jsonl` byte for byte. The new slide folders stay out of `run.sh`. `recognize-how` and `sql` read the function folders' recordings. A copied `know-this` run gets its own replay test in `tests/test_examples.py`. The test replays its recording with no key and checks the ratio the slide shows.
7. **Catches and know-this.** The `catches` check reads Jev's answers from `results/runs/2026-09-26-thinkthen-jev/answers.jsonl`. The slide's values match that run. The `know-this` batching line shows two numbers: "4×" and a 3 to 14% range. The 4× run counts only if it replays with no key through the 02dc0b96 build, by a command its README names. The builder copies it into `examples/know-this/` with its `run.txt` when it does. The 3 to 14% range rests partly on rows the bench cannot hold. The folder README and the deck issue list it as having no bench source. The copy passes the same cleaning as ticket 0016: no internal word, no experiment path, and a clean private-names check. Otherwise the folder README says the line has no bench source, and the deck issue lists it.

## Tests

- `tests/test_examples.py` checks the index. Each folder has one row, and each row with a folder names one that exists. Each recorded folder has a `run.txt` with a SHA-256 line.
- One table of slide claims extends `tests/test_published_numbers.py` from ticket 0016. Each row gives a folder, a quoted value, and its source:
  - `sql`: each song's 0, 1, or NULL at the band 0.3:0.7, from the filter folder's `outputs.jsonl` probabilities.
  - `jev` and `bench-run`: `median_s` 0.215 and `usd` 0.022466 from `cost.tsv`, and the loads 3.83 and 7.10 from `loadavg.txt`.
  - `what-jev-knows`: the three bars from `accuracy.tsv`, and the random bar from the Chance row of `reports/results.md`.
  - `catches`: each question's two shown probabilities, from `results/runs/2026-09-26-thinkthen-jev/answers.jsonl`.
  - `know-this`: the cost row, and the batching ratio when its run is in the bench.
- `recognize-how` gets one replay test with `--details`. It skips with no `THINKTHEN_BIN`, as the other replay tests do.

## Proof

- `python3 -m unittest discover -s tests` passes with no key and no network, with and without `THINKTHEN_BIN` set to the 02dc0b96 build. The record gives both counts.
- `./run.sh` with no key and no address replays every recorded example folder and the newest Jev run byte for byte.
- `git diff -M --stat main` shows each moved file as a rename. A moved file with changed bytes is a script or test whose paths changed. The record lists them.
- `git diff --stat main` shows no change to any recording, `outputs.jsonl`, `results/tables/`, `results/history.tsv`, or question file.
- Each function folder's recording equals the archived `2026-09-25-examples-jev` recording byte for byte. The record gives the check.
- `git grep -n -E '(^|[^-])functions/|questions/functions|functions\.(py|sh)|chat\.py functions'` outside `sdlc/`, `results/archive/`, and `results/runs/` prints nothing. The run folders keep their bytes as history. Their `inputs.sha256` files and ledgers name the old paths.
- The machine-name check and the private-names check of ticket 0016 print nothing once `examples/` exists.
- If `examples/know-this/` takes a copied run, the grep of ticket 0016 and the private-names check print nothing for it.

## Owner's decisions (Ian can overturn each)

- Folder names drop the deck's numbers. The deck renumbers its slides when a slide joins. The index gives the numbers of 2026-09-26.
- A slide gets a folder when it shows bench data. That narrows "one folder per slide" to 22 of the 30 slides. Every slide still gets a row in the index. `title`, `runs-in`, `filter-live`, and `backends` show runs or text the deck recorded itself. The index lists each one as "the deck holds it", and the deck issue asks the deck to check them and name their builds.
- The run labels and the `functions*.tsv` tables keep their names. Renaming them would rewrite `results/history.tsv` and every archived run's label.
- The suite scripts take the names `make_suite.py`, `ask_suite.py`, and `score_suite.py`. They sit beside `ask.py` and `score.py`. Those two do the same jobs for the 1,501 questions.
- The `know-this` batching line joins the bench only with a replayable run. A copied report alone gives a reader nothing to run.

## Deferred

- Making a released thinkthen build the stated requirement. It waits for ThinkThen 0.1. Until then the replay tests skip with no `THINKTHEN_BIN`.
- Renaming the `functions-*` run labels and tables.
- Rerunning the example folders. Every slide keeps its recorded answers.

## Downstream

The talk deck's repository gets one issue on its main, in `sdlc/issues/`. It lists every bench path the deck reads that this ticket moves, with its new path. It lists the slides the index marks "the deck holds it". It lists any claim with no bench source. The deck's changes land in the same window as this ticket, before launch. The deck build fails on the old paths until they land.

The ThinkThen repository gets one issue on its main, in `sdlc/issues/`. The site's copy of the walkthroughs links `functions/` paths, and each one changes to its `examples/` path. The issue gives the full path map. The function slide routes keep their names.

## Done when

The proof passes, a fresh reviewer accepts the code, the bench lands on main and is pushed, and both downstream issues sit on their repositories' main.

## Ticket review 1 (fresh reviewer, 2026-09-26): findings 11 to 17 for 0017, all taken

11. The role name is gone. Two trailing clauses are split.
12. The random bar of `what-jev-knows` reads the Chance row of `reports/results.md`.
13. Eleven function folders hold recordings. `examples/diff/` names the audit folder's build.
14. The grep leaves out `results/runs/`. The reader list adds `chat.py`, `context_diff.sh`, and `tune.sh`. The `chat.py` subcommand becomes `suite`.
15. The deck issue carries the deck's build scripts. Slide 27's batching line and slide 25's copies are told apart.
16. The narrowing to 22 of 30 slides sits under the owner's decisions.
17. A copied `know-this` run passes 0016's cleaning and its proof.

## Ticket review 2 (fresh reviewer, 2026-09-26): findings 5 to 7 for 0017, all taken

5. The reader list adds `.gitignore`, `table.py`, `reports/results.md`, and `results/README.md`.
6. run.sh replays every function folder, `diff` included.
7. The `catches` source is the 2026-09-26 Jev run.

## Ticket review 4 (fresh reviewer, 2026-09-26): finding 2 for 0017, taken

2. The new slide folders stay out of `run.sh`. A copied `know-this` run gets its own replay test.

## Ticket review 5 (fresh reviewer, 2026-09-26): finding 3 for 0017, taken

3. The 4× run needs a named command and the 02dc0b96 build. The 3 to 14% range is listed as having no bench source.
