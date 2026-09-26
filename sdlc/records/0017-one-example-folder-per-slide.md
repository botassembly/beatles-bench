# 0017 Rename the three "functions" folders and give each slide one example folder: record

Built on 2026-09-26 on `ticket/0017-one-example-folder-per-slide` from main at 5f04abbb. No model call ran. No key was set or read. The spend is $0.

The work lands in three commits before this record:

1. **Pure moves.** `git mv` alone. `git diff -M --name-status` of the commit gives 356 files, each at R100.
2. **Paths.** Every script, test, and page that names a moved path now names its new one. The commit changes no other text.
3. **Slide folders.** The index, the ten new folders, the eleven `run.txt` files, the tests, and the README lines about them.

## The moves

| Old path | New path |
| --- | --- |
| `functions/` | `examples/` |
| `questions/functions/` | `questions/suite/` |
| `scripts/generate/functions.py` | `scripts/generate/make_suite.py` |
| `scripts/run/functions.py` | `scripts/run/ask_suite.py` |
| `scripts/run/functions.sh` | `scripts/run/ask_suite.sh` |
| `scripts/score/functions.py` | `scripts/score/score_suite.py` |
| `tests/test_functions.py` | `tests/test_suite.py` |
| `tests/test_function_folders.py` | `tests/test_examples.py` |

The `functions` subcommand of `scripts/run/chat.py` is now `suite`. `.gitignore` names `examples/*/replay/` and `examples/diff/[ab].jsonl`. The run labels `functions-jev`, `functions-glm-5.3-flash`, and `functions-laya` keep their names. So do `results/tables/functions*.tsv` and the generator's seed.

## Result

1. **Index.** `examples/README.md` gives all 30 slides one row each, in the talk's order of 2026-09-26. Each row gives the number, the name, what the slide shows, its folder, its sources, its check, and its build. Four rows read "the deck holds it": title, runs-in, filter-live, and backends. Four read "no bench data": scripting, systems, frames, and close.
2. **Slide folders.** Ten new folders each hold one `README.md`: `strings`, `jev`, `bench`, `recognize-how`, `sql`, `what-jev-knows`, `catches`, `open-book`, `know-this`, and `bench-run`. Each names the slide's claims in a table with their values and sources, then the build and the check. The twelve function folders keep their files. With the new folders, 22 of the 30 slides have a folder.
3. **Builds.** Each of the eleven recorded function folders holds `run.txt`. Its four lines come from `results/archive/runs/2026-09-25-examples-jev/run.txt`: the thinkthen version line, the SHA-256, the model the backend reported, and the date. The machine line and the guard lines stay in the archived run. Each function README lists `run.txt` under "The files". `examples/diff/README.md` names `../audit/run.txt` and says `diff` calls no model. Each new folder names the `run.txt` of the run it reads. The GLM rows and the batching line read "build not recorded".
4. **Catches.** `examples/catches/README.md` reads Jev's answers from `results/runs/2026-09-26-thinkthen-jev/answers.jsonl`. The slide's six probabilities match that run: 0.34 and 0.14, 0.58 and 0.31, 0.69 and 0.31. The three panels read `popularity.tsv`, `controls.tsv`, and `composition.tsv`.
5. **Know-this.** The 4× run does not join the bench. It posted its request bodies without the thinkthen command, so it cannot replay through the 02dc0b96 build. `examples/know-this/README.md` lists the 4× line and the 3 to 14% range under "Claims with no bench source". The deck issue lists them too. No run was copied, so the copy checks do not apply.
6. **run.sh.** `./run.sh` replays the twelve function folders in the talk's order, with `diff` after `audit`. The new folders stay out of it.
7. **Pages.** The README's map and "What's new" name `examples/`. `questions/README.md`, `scripts/README.md`, `tests/README.md`, `results/README.md`, `reports/results.md`, `reports/open-book.md`, and `data/README.md` name the new paths.

## Tests

- `tests/test_examples.py`:
  - The folder test now expects the twelve function folders, the ten slide folders, and `README.md`. Each slide folder holds only its README.
  - A new index test checks the 30 rows in the talk's order. Each linked row names a folder that exists, each folder has one row, and every other row reads "the deck holds it" or "no bench data".
  - A new build test checks that each of the eleven recorded folders has `run.txt` with a SHA-256 line, a thinkthen line, a model line, and a date. It also checks that the diff README names `../audit/run.txt`.
  - `RecognizeHowTest` runs `thinkthen recognize ... --replay recording --details` in `examples/recognize/` with no key. It checks each of the 26 word rows, the five names the join rule gives, the token counts, and the model against the page. A `--dry-run` must plan one request. It skips with no build.
- `tests/test_published_numbers.py` gains `SLIDE_CLAIMS`, 49 rows. Each gives a folder's page, the quoted text, and the source that computes the value. They cover `strings`, `jev`, `bench`, `sql`, `what-jev-knows`, `catches`, `open-book`, `know-this`, and `bench-run`. The `sql` row computes each song's 1, 0, or NULL at the band 0.3:0.7 from the filter folder's cold probabilities. The band rule is thinkthen's: yes at or above the high side, no below the low side. A second new test pins the values the slides show: 0.215, 0.022466, 3.83, 7.10, the five choose probabilities, the six catches probabilities, the twelve sql answers, and A Day in the Life as the one wrong answer.
- Planted faults each failed their test, and the restored pages passed: Ringo 0.84 changed to 0.85, Penny Lane NULL to 0, John Lennon 0.34 to 0.35, and one recognize-how word probability.

## Proof

- **Suite.** `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests`:
  - With `THINKTHEN_BIN` set to the 02dc0b96 build (SHA-256 `eb4a5713`), the venv from `requirements.txt`, and a local `data/raw/`: 193 tests, OK, none skipped.
  - With no `THINKTHEN_BIN`, no `thinkthen` on `PATH`, and the system Python: 189 tests, OK, 22 skipped. `test_chat.py` skips as one module there.
- **Replay.** `./run.sh` with no key and no address exited 0. It printed "replayed results/runs/2026-09-26-thinkthen-jev: all answers match its answers.jsonl" and 12 lines of "replayed examples/NAME: every file matches the committed folder", from decide to diff in the talk's order. `git status` was clean after it.
- **Renames.** Before the record commit, `git diff -M --name-status main HEAD` gave 338 files at R100, 18 moved files with changed bytes, 20 modified files, and 22 added files. This record is the 23rd added file. The moved files with changed bytes:
  - The twelve function READMEs. Each gains one line about `run.txt`.
  - `scripts/generate/make_suite.py`, `scripts/run/ask_suite.py`, `scripts/run/ask_suite.sh`, and `scripts/score/score_suite.py`. Their usage lines and paths changed.
  - `tests/test_examples.py` and `tests/test_suite.py`. Their paths changed, and `test_examples.py` gained the new tests.
- **Unchanged data.** `git diff -M --stat main HEAD` over `results/tables/`, `results/history.tsv`, `questions/`, every `recording/`, and every `outputs.jsonl` shows renames only, apart from `questions/README.md` and `results/README.md`.
- **Recordings.** For each of the eleven recorded folders, `diff -rq results/archive/runs/2026-09-25-examples-jev/NN-NAME/recording examples/NAME/recording` printed nothing.
- **Old paths.** The ticket's grep over the tracked files, outside `sdlc/`, `results/archive/`, and `results/runs/`, printed nothing.
- **Internal words.** The internal-word check of ticket 0016 printed nothing over `examples/`, `tests/`, `scripts/`, `README.md`, and `run.sh`.
- **Private and machine names.** The private-names check listed 0 files. The machine-name check counted 0 matches.
- **Links.** The link checker of record 0016 printed "188 relative links and anchors, 0 broken".

## Downstream

- **The talk deck.** Quick Fix qf-bench-0017 in the deck's repository reads the new paths. The deck built against this branch with 30 slides and every check passing. Its issue `sdlc/issues/2026-09-26-beatles-bench-0017-renames-paths-the-deck-reads.md` gives the path map, the four "deck holds it" slides, and the claims with no bench source.
- **ThinkThen.** The issue `sdlc/issues/2026-09-26-the-beatles-bench-section-keeps-its-own-copy.md` on ThinkThen main, filed by ticket 0016, already gives this ticket's path map. It leaves out the two renamed tests. The site's copy of 71 bench files and its links change in the ThinkThen repository. This ticket did not edit it.

## Deferred

- The ticket's own Deferred list stands: a released thinkthen build, the `functions-*` run labels and tables, and a rerun of the example folders.
- The know-this batching line and the strings search comparison have no bench source.
- The ThinkThen issue does not name `tests/test_examples.py` and `tests/test_suite.py`.

## Reviews

- Code review 1 checked the moves, the paths, the unchanged data, the recordings, the `run.txt` files, the name checks on every commit, each slide claim against its source, the suite both ways, and the replay. It returned one finding: the Renames bullet counted 22 added files, and HEAD holds 23 with this record. The bullet now says the counts came before the record commit. Code review 2 returned ACCEPT.
