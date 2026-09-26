# 0016 Clean the repository for public launch

Owner: the queue owner. Status: open. Ticket review 1 returned seventeen findings across 0016 and 0017, review 2 returned nine, review 3 returned four, review 4 returned two, review 5 returned five, review 6 returned two, and review 7 returned one. All are taken. Review 8 returned ACCEPT.

## Why

The repository goes public at launch. A fresh reviewer read it on 2026-09-26 as a first-time visitor would. The reader meets internal words, stale runs, and pages that duplicate the ThinkThen documentation website. Several published numbers have no bench check. `./run.sh` writes a live run to a folder its replay never reads.

The queue owner decided each change below on 2026-09-26. Ian can overturn each one. "Owner's decisions" lists them.

This ticket covers the content. Ticket 0017 covers the renames and the slide folders. Ticket 0017 says why the work splits in two.

## Prior evidence

- The reviewer's report of 2026-09-26: `python3 -m unittest discover -s tests` passes 178 tests and skips 21 with no `THINKTHEN_BIN`. The README mixes dates, machine loads, and builds in its open-book paragraph (line 43) and its fourth takeaway (line 54). It has no link to the website. `results/runs/` holds 33 runs in 203 MB.
- The same report lists deck slides whose bench numbers no test checks. Slide 4 shows 306 songs and 1,501 questions. Slide 26 shows open book at 35% and 94%. Slide 24 shows four bars, and a test checks only two of them, 67.0% and 96.2%. `tests/test_table.py` checks the README's headline cells against `table.py`. No test reads chance (31.4%) or embeddings (37.6%) from `reports/results.md`. No test reads the open-book row "68 (35%) | 184 (94%)" from `reports/open-book.md`.
- Internal words in tracked text, outside recordings, counted on 2026-09-26 at 2cdb6445:
  - A workspace experiment path (`experiments/NNN-...`) appears in 25 files. Fifteen are run ledgers (`results/runs/*/ledger.txt`). The rest are `scripts/README.md` and nine `sdlc/` files.
  - Four code files name experiment 249 in their comments: `scripts/harvest/harvest.py`, `tests/fixtures/audit/249/make.py`, `tests/test_diff_guard.py`, and `tests/test_leaning_no.py`. `make.py` also calls it a "workspace experiment".
  - A session name appears in 23 `sdlc/` files, including `sdlc/README.md` and every ticket's Owner line.
  - Workspace paths appear in `sdlc/`: `notes/todos/`, `worktrees/beatles-bench-NNNN`, and an agent worktree under `.claude/`. Scratch files of the deck's author appear in tickets and records 0006, 0007, and 0009.
  - Ticket 0002, line 7, cites a note in Ian's private vault by its file name.
  - The bench history holds one commit, 2cdb6445. Every other bench commit hash in `sdlc/` and the docs can no longer resolve. The thinkthen hashes, such as 02dc0b96, resolve on thinkthen main.
  - Record 0002, line 3, names the build machine by its nickname. No other tracked file names a machine. No tracked file names a private project or a home path.
- `scripts/README.md` runs 114 lines. Its "Laya" section gives operator steps for a shim on a Mac over an SSH tunnel. A reader cannot repeat them without that Mac.
- `docs/` holds 17 Markdown pages and `context.jq`. `docs/README.md` lists 16 pages in reading order, starting with the top README. Twelve are walkthroughs under `docs/walkthroughs/`. Each walkthrough cites two or three `functions/...` paths, and `run-it-for-free.md` cites four.
- The ThinkThen repository's issue `2026-09-25-a-worked-examples-section-pulled-from-beatles-bench.md` is open. It plans to pull the docs pages into the site from a pinned bench commit. The site has no Beatles Bench route yet. The function folder READMEs already link `https://thinkthen.dev/learn/beatles-bench/<name>/`.
- `tests/test_function_folders.py` runs every command block on each folder README and each page `docs/README.md` lists. It also checks each number in those pages against the data.
- `results/archive/` already holds `2026-09-23-seed/` and `2026-09-23-natural-phrasing/`. `results/README.md` calls them runs over the older question sets.
- Run generations. The newest run of each label is the 2026-09-26 Jev run, the 2026-09-23 GLM, Laya, and baseline runs, and the 2026-09-24 relation-vector, Laya one-line, and pipeline-jev2 runs. `analyze.py` scores only the newest folder of each label that holds `answers.jsonl`. Superseded Jev generations stay in `results/runs/`: five 2026-09-23 folders, `2026-09-24-pipeline-jev`, and seven 2026-09-25 folders. `2026-09-25-examples-jev` is the only run of its label. Its recordings are the source of the function folders' recordings, and it holds no `answers.jsonl`.
- Tests read superseded runs by name. `test_open_book.py`, `test_table.py`, `test_generate.py`, `test_rad.py`, and `test_score_rad.py` read 2026-09-23 Jev folders. `test_replay_laya.py` and `test_open_book.py` read `2026-09-24-thinkthen-jev-one-line`. That run pairs with the Laya one-line run.
- `reports/open-book.md` and `reports/rad.md` open with 2026-09-23 sections that cite runs this ticket archives. Their section `## Fresh run of 2026-09-26` comes last. The talk deck's build reads the tables under that heading in both reports. It also checks exact phrases in `paper/notes.md`.
- `paper/notes.md` takes its numbers from the 2026-09-23 runs.
- `./run.sh` with an address set writes to `results/runs/<today>-<NAME>`. NAME comes from its argument, then `BEATLES_BENCH_MODEL`, then `jev-latest`. With no address, it rejects any argument and replays `score.py newest thinkthen-jev`. So a live run named by default lands in `DATE-jev-latest`. The replay never reads that folder.
- `tests/fixtures/fake-thinkthen` has no `audit` command, and it asserts `--details` and `--jsonl` on every call. `run.sh` stops at its `audit --help` check with that fake. The fake has no `--cache` or `--replay` folder handling and cannot answer the example verbs. `tests/fixtures/fake-thinkthen-functions` handles those. `run.sh` uses one `THINKTHEN_BIN` for both steps. `tests/test_run_sh.py` holds `RunShTest` and `NoAuditTest`.
- `ask.py live` writes with `--cache` into its run folder. A live run on the date of a committed run would write into the committed folder.
- `.gitignore` ignores `results/runs/*/replay/` and `results/runs/*/*/replay/`. It ignores nothing under `results/archive/`.
- The talk deck builds its function slides' text from `docs/walkthroughs/<fn>.md`. Its build checks the `scripts/README.md` sentence "A rerun answers unchanged questions from the recording and sends only the new ones." It stops unless the bench holds 2cdb6445 as an ancestor. The ThinkThen site issue names bench commit 9d7f1820, which no longer resolves.
- The README's time column gives Jev's median from a run that recorded its load (3.83 to 7.10 on 16 cores) and its build. The GLM and Laya medians come from 2026-09-23 runs that recorded neither.
- ThinkThen keeps its own `sdlc/` public. The workspace rule makes each repository's `sdlc/` its only record.

## Retained behavior

- Every question file, answer, recording, table in `results/tables/`, and `results/history.tsv` keeps its bytes. No paid call is made.
- `./run.sh` with no address still replays the newest Jev run and every function folder byte for byte. It still rescores and prints the tables.
- `analyze.py` still scores the newest run of each label. The tables do not change. Every moved folder with answers is a superseded generation. `2026-09-25-examples-jev` holds no answers.
- Every archived run keeps its recording bytes. The archived 2026-09-25 Jev runs still replay with the 02dc0b96 build their `run.txt` names.
- `sdlc/` stays public and complete. Each ticket, record, and issue keeps its numbers, decisions, and reviews. Only the internal words change.
- Each run's `run.txt` keeps its thinkthen version line and its SHA-256.
- The dated sections of `reports/open-book.md` and `reports/rad.md` stay. The heading `## Fresh run of 2026-09-26` and its tables keep their text and order.
- The function folders, `questions/functions/`, and `scripts/*/functions.py` keep their names in this ticket. Ticket 0017 renames them.

## Changes

The builder makes two commits. The first cleans the text. The second moves the runs. The second commit's diff then holds pure renames.

1. **Internal words.** Replace each internal word in every tracked text file outside recordings. The scope covers `sdlc/`, `scripts/`, `tests/`, the READMEs, and the run ledgers.
   - A session or agent name becomes "the queue owner" or "the builder". The Owner line of every ticket reads "Owner: the queue owner."
   - An experiment path or an experiment number becomes "a local experiment". A binary path in a ledger becomes "a local build". The SHA-256 beside it stays.
   - A workspace path (`notes/todos/`, `worktrees/...`, `.claude/...`) becomes plain words: "Ian's todo list", "the ticket's worktree", "an agent's worktree".
   - The vault note in ticket 0002 becomes "a private note".
   - A scratch file of the deck's author becomes "the deck's slide source".
   - The machine nickname in record 0002 becomes "a local machine". "The local Linux machine" and "the Mac" stay.
   - A bench commit hash that no longer resolves becomes "an earlier commit". A hash that resolves in the bench or on thinkthen main stays.
   - `sdlc/README.md` says one agent owns the queue under Ian. It says why `sdlc/` is public.
2. **Pages leave for the website.** Delete `docs/walkthroughs/`, `docs/run-it-for-free.md`, `docs/context-article.md`, and `docs/README.md`. Links that pointed there point to https://thinkthen.dev/learn/beatles-bench. That covers the top README, the function folder READMEs, and `tests/test_function_folders.py`. No other file links the deleted pages today.
3. **Pages merge.** Merge `docs/the-data.md` into `data/README.md`, with one section per topic and no repeated facts. Add `docs/context-and-cost.md` to `reports/open-book.md` as a new last section, "Context and cost". Move `docs/context.jq` to `scripts/score/context.jq`. `docs/` then no longer exists.
4. **Top README.** Rewrite `README.md` in this order: what it is, the results table, run it, what's new, learn more, repository map, and data and licenses.
   - Every number names its run date once. The 2026-09-26 Jev runs give every Jev number. The 2026-09-23 runs give GLM, Laya, and the baselines. The open-book line gives 68 and 184 of 196 from 2026-09-26 only.
   - The time column marks the GLM and Laya medians "build and load not recorded". Jev's cell names its load.
   - Run it names the thinkthen build once: main at 02dc0b96 or later, until a release carries `audit`.
   - What's new lists the dated changes a reader needs, newest first, in at most five lines.
   - Learn more links https://thinkthen.dev/learn/beatles-bench.
5. **New READMEs.**
   - `tests/README.md` says how to run the suite and gives the `THINKTHEN_BIN` rule. With no `THINKTHEN_BIN` and no `thinkthen` on the path, the replay tests skip. The page names each skipping test file and its reason.
   - `paper/README.md` says what the folder holds and which runs the notes use.
   - `results/runs/README.md` is a key to run-name labels. It gives each label (`thinkthen-jev`, `-open-book`, `-rad`, `-rad2`, `-one-line`, `functions-*`, `pipeline-jev`, `pipeline-jev2`, `baseline-*`, `glm-5.3-flash`, `thinkthen-laya`, `relation-vectors`) with its system, its questions, and its report.
6. **scripts/README.md.** Trim it to what a reader does: set up, replay, rerun, add a backend, and draw figures. The sentence "A rerun answers unchanged questions from the recording and sends only the new ones." stays word for word. The deck checks it. Move the "Laya" section into this ticket's record, under "How the Laya runs were made", in generic words. The README keeps one line. The line says the Laya runs replay with no Mac.
7. **Archive.** The archive gets this layout:
   - `results/archive/2026-09-23-seed/` and `results/archive/2026-09-23-natural-phrasing/` stay. They hold runs over older question sets.
   - `results/archive/runs/` holds superseded run folders under their own names. It takes the five 2026-09-23 Jev folders (`thinkthen-jev`, `-open-book`, `-rad`, `-rad2`, `functions-jev`), `2026-09-24-pipeline-jev`, and the seven superseded 2026-09-25 folders. It also takes `2026-09-25-examples-jev`, the source of the function folders' recordings.
   - `results/archive/probes/` and `results/archive/in-text-check/` take the two folders of those names.
   - The 2026-09-23 GLM, Laya, and baseline runs stay in `results/runs/`. So do the 2026-09-24 one-line, relation-vector, and pipeline-jev2 runs.
   - Every test path, script default, and `results/README.md` follow the new places. `results/README.md` describes each part of the archive.
   - `.gitignore` gains `results/archive/runs/*/replay/` and `results/archive/runs/*/*/replay/` in the move commit.
8. **Reports.** `reports/open-book.md`, `reports/rad.md`, and every other page update each mention of a moved run, in links and in plain text. The dated sections keep their order and their text otherwise.
9. **Paper notes.** Refresh `paper/notes.md` in place to the 2026-09-26 runs. A finding with no 2026-09-26 run keeps its number and names its dated run. The section headings stay.
10. **run.sh.**
    - NAME comes from the argument alone and defaults to `jev`. `BEATLES_BENCH_MODEL` sets only the model each request carries.
    - A live run with `BEATLES_BENCH_MODEL` set and no NAME stops with "run.sh: name the run: ./run.sh NAME" and exits 2. Another model then never lands in the Jev folder.
    - A live run stops with exit 2 when its run folder or examples folder holds a file git tracks. A live run then never writes into a committed run.
    - A live run writes to `results/runs/<today>-thinkthen-<NAME>`. It asks the examples into `results/runs/<today>-examples-<NAME>/<example>/`.
    - The replay takes the same optional NAME: `./run.sh [NAME]`. It replays the newest `DATE-thinkthen-<NAME>`. With NAME `jev`, it then replays the committed function folders. With another NAME, it replays each folder of the newest `DATE-examples-<NAME>` when one exists.
    - `scripts/run/example.sh NAME replay [OUT] [FROM]` gains an optional FROM: the run folder whose recording it replays. The cases still come from `functions/<name>/`. For audit it still runs `tune.sh`. With no FROM, it replays `functions/<name>/recording` as today.
    - Each replay of a live examples folder is checked byte for byte against that folder's own `outputs.jsonl`, `lists/`, `rows.jsonl`, `rows-context.jsonl`, and `audit-*.json`. `diff` replays from `$ex/audit` and is checked against `$ex/diff/diff.jsonl`.
    - A live run writes `backend.txt` into `DATE-thinkthen-<NAME>/` and `DATE-examples-<NAME>/`. It holds the base URL and the model name the run used. It holds no key. The replay reads that file and passes the same base URL and model with no key. A recording binds to both, so a replay of any backend then finds its answers. A folder with no `backend.txt` replays with the defaults, as the committed Jev runs do today.
    - With no `DATE-thinkthen-<NAME>` folder, the replay prints "run.sh: no results/runs/DATE-thinkthen-NAME run to replay." and exits 2.
    - With NAME `jev`, the replay also replays the newest `DATE-examples-jev` after the committed folders when one exists. A default live run is then the set of folders a default replay reads.
    - Outside a git checkout, such as a ZIP download, the tracked-file guard has nothing to read. The live run then stops only when its run folder already exists and holds files, with "run.sh: RUN already holds files." and exit 2. `scripts/README.md`, the README, and the header of `run.sh` say so.

## Tests

- **Published numbers.** A new file, `tests/test_published_numbers.py`, holds one table of claims. Each row gives a page, the quoted text, and the source it must equal. The rows cover:
  - 306 songs and 20 albums in the README, from the rows of `data/songs.tsv` and `data/albums.tsv`.
  - 1,501 questions and 1,313 Beatles-only questions, from the question files.
  - The open-book "all" row, 68 (35%) and 184 (94%) of 196, from `open_book.py compare` on the 2026-09-26 runs.
  - Chance 31.4% and embeddings 37.6% in `reports/results.md`, from `table.py`.
- **run.sh.** A new fixture, `tests/fixtures/fake-thinkthen-run`, serves both steps of a live run and their replays. It answers `audit --help` and `audit ROWS KEY` with JSON that holds `suggested.cut`, as `scripts/score/tune.sh` reads it. It answers `diff` for `scripts/score/diff_guard.sh` and answers `choose` itself. It hands every other call to `fake-thinkthen` or `fake-thinkthen-functions` by its verb and flags. New cases join `tests/test_run_sh.py`, and `RunShTest` and `NoAuditTest` stay. `setUpClass` makes one temporary copy with `git clone` of the working repository. It then copies the working tree's `run.sh`, `scripts/`, and `tests/fixtures/` over the clone and commits them there. The copy then has git history and the code under test. The cases:
  - `./run.sh demo` live with the fake, then `./run.sh demo` with no address. The replay reads the folders the live run wrote and exits 0. Each replayed file equals the live file.
  - `BEATLES_BENCH_MODEL=other ./run.sh other` live with an address, then `./run.sh other` with no address. `FAKE_LOG` shows the replay sends the same `--model` and base URL. `fake-thinkthen-run` logs `THINKTHEN_BASE_URL` beside its arguments.
  - A replay for a NAME with no run exits 2 with its message.
  - A live run with `BEATLES_BENCH_MODEL` set and no NAME exits 2.
  - A live run whose folder holds a file committed inside the clone exits 2 and writes nothing.
- Existing tests follow the moved folders. `test_function_folders.py` checks the merged sections of `data/README.md` and `reports/open-book.md` in place of the deleted pages.

## Proof

- `python3 -m unittest discover -s tests` passes with no key and no network. It runs with and without `THINKTHEN_BIN` set to a build of thinkthen main at 02dc0b96 (SHA-256 `eb4a5713`). The record gives both counts.
- `./run.sh` with no key and no address replays the newest Jev run and every function folder byte for byte.
- Each archived 2026-09-25 Jev run replays with the 02dc0b96 build and matches its answers. The record gives the loop and its output.
- `git diff --stat` shows no change to `results/tables/`, `results/history.tsv`, `questions/`, or any recording. `git diff -M` of the second commit shows each archived folder as a pure rename.
- One check lists every hex token of 7 to 40 characters that holds a letter from a to f. It reads the tracked Markdown files and scripts. It skips recordings, the data files in `results/runs/`, SHA-256 lines, and tickets 0016 and 0017. Ticket 0016 names the dead pin 9d7f1820 as evidence. Each token resolves in the bench or on thinkthen main. The record gives the output.
- `git grep -i -E 'experiments/|experiment [0-9]|workspace|vault|marketing session|marketing lead|build session|coordinator|notes/todos|worktrees/|\.claude/'` prints nothing outside recordings and tickets 0016 and 0017. Those two tickets quote the words as patterns. The records of 0016 and 0017 point to this line and do not repeat the pattern. The moved Laya section uses none of the words.
- A second check reads a list of machine names kept outside the repository, as the private-names list is kept. The list holds the nickname in record 0002, the Linux machine's product name, and each host name in its `name.local` form. The check is a case-sensitive whole-word match over every tracked text file except `data/`, `questions/`, and the recordings. Song words match in those three. It prints nothing. The record gives the count only. The names then never enter the repository. The Mac's chip model stays in `reports/results.md` and `scripts/README.md`. It describes hardware and names no machine. The private-names check prints nothing.
- Every relative link in every tracked Markdown file resolves. The record gives the checker and its output.
- A fresh clone passes the suite. `git status` stays clean after it.

## Owner's decisions (Ian can overturn each)

- `sdlc/` stays public. The workspace makes it the only record, and ThinkThen keeps its own public. The ticket strips internal words and keeps the history.
- The walkthroughs and the free-run page leave the bench. The website section holds them. One copy stays current.
- The merged pages join the pages they repeat. `docs/context-article.md` goes. It holds no recording and backs no slide.
- The archive keeps every superseded run. The repository size stays near 203 MB.
- The 2026-09-24 one-line runs stay. The Laya one-line run pairs with the Jev one-line run of the same day.
- `paper/notes.md` stays in place and takes the fresh numbers. Most of its findings rest on the 1,501 questions, and the 2026-09-26 run covers them.
- The README marks the GLM and Laya times "build and load not recorded". A paid rerun would measure them. This ticket makes none.
- `run.sh` uses the label `thinkthen-<NAME>`. `analyze.py` already maps `thinkthen-jev` to Jev. A reader's own backend then gets a label of the same shape.

## Deferred

- Making a released thinkthen build the stated requirement. It waits for ThinkThen 0.1. Until then the replay tests skip with no `THINKTHEN_BIN`, and `tests/README.md` says so.
- Replaying the archived 2026-09-23 runs. Other builds made them, and no copy of those builds is kept.
- Shrinking the repository. The archive keeps every run.
- Rerunning GLM and Laya to measure their time with a named build and load.
- Command checks for the website's copy of the walkthroughs. The site issue carries it.

## Downstream

The ThinkThen repository gets one issue on its main, in `sdlc/issues/`. It revises the open worked-examples issue:

- The site holds its own copy of the walkthroughs and the free-run page at `/learn/beatles-bench`.
- The site copies the pages from the bench main commit just before 0016's first commit. The issue records that hash. The copy lives in the ThinkThen repository, so a later squash of the bench breaks nothing. The dead pin 9d7f1820 goes.
- Its links to bench files use paths on the bench's main after ticket 0017. The issue gives 0017's path map: `functions/` becomes `examples/`, `questions/functions/` becomes `questions/suite/`, and each `scripts/*/functions.py` takes its new name.
- The site needs no bench commit pin. The bench history may be squashed again at launch.

The talk deck's repository gets one issue on its main, in `sdlc/issues/`. It lists each bench path the deck reads that this ticket moves or deletes, with its new place. The list covers the archived run folders and `scripts/README.md` lines. The function slides' text then comes from the site's copy of the walkthroughs in the ThinkThen repository. The issue lists the deck's pin of bench commit 2cdb6445 in its build and its sql slide. A launch squash would break that pin. It lists each `paper/notes.md` phrase the deck checks that the refresh changes. The deck's changes land in the same window as this ticket, before launch.

## Done when

The proof passes, a fresh reviewer accepts the code, the bench lands on main and is pushed, and both downstream issues sit on their repositories' main. The launch waits for https://thinkthen.dev/learn/beatles-bench to serve the pages.

## Ticket review 1 (fresh reviewer, 2026-09-26): seventeen findings across 0016 and 0017, all taken

1. The docs and README counts are right, and the four code files that name experiment 249 join the evidence and the grep.
2. The vault note in ticket 0002 is named and replaced.
3. The text cleaning and the move land as two commits. The move then proves as pure renames.
4. The archive layout sits beside the existing folders. `2026-09-25-examples-jev` is named as the recordings' source.
5. The reports keep their dated sections and the Fresh heading. Plain-text path mentions change too. The paper notes are refreshed in place.
6. run.sh names its folder from the argument alone. The replay takes NAME, handles the examples folder, and names its error.
7. The run.sh test runs in a temporary copy with a fake that answers `audit --help`.
8. The replay proof names what run.sh replays. The archive claim covers recording bytes and the 2026-09-25 replays.
9. The hex check reads only tokens with a letter, in Markdown and scripts.
10. The site issue carries 0017's path map. 0017's ThinkThen issue is unconditional.
11. The role name is gone. Five trailing clauses are split.
12. to 17. Ticket 0017 lists them.

## Ticket review 2 (fresh reviewer, 2026-09-26): nine findings across 0016 and 0017, all taken

1. A live run with `BEATLES_BENCH_MODEL` and no NAME stops. A live run never writes into a tracked folder. The test covers both.
2. A new fake serves both run.sh steps. The new cases join `tests/test_run_sh.py`, and the existing tests stay.
3. The deck issue names the site copy as its walkthrough source and lists the 2cdb6445 pin. The `scripts/README.md` sentence the deck checks stays. The site issue names the commit it copies from.
4. `.gitignore` covers archive replays.
5. to 7. Ticket 0017 lists them.
8. The archive count reads seven superseded 2026-09-25 folders plus `2026-09-25-examples-jev`.
9. The evidence says "a session name". The proof grep carries the words.

## Ticket review 3 (fresh reviewer, 2026-09-26): four findings, all taken

1. The run.sh fake answers `audit`, `diff`, and `choose` itself. The temporary copy comes from `git clone`, so it has history.
2. The hex check skips tickets 0016 and 0017.
3. The records point to the grep line and do not repeat its pattern.
4. The link updates name the files that link the deleted pages today. `questions/` stays untouched.

## Ticket review 4 (fresh reviewer, 2026-09-26): two findings across 0016 and 0017, all taken

1. `example.sh` takes a FROM folder to replay. Each replay of a live examples folder is checked against that folder's own files. The run.sh test has a pass condition.
2. Ticket 0017 lists it.

## Ticket review 5 (fresh reviewer, 2026-09-26): five findings across 0016 and 0017, all taken

1. The machine nickname in record 0002 is named as evidence, replaced, and checked by a proof that prints no names.
2. The run.sh cases clone once and overlay the working tree's code. The planted file is committed inside the clone.
3. Ticket 0017 lists it.
4. The default replay also replays the newest `DATE-examples-jev`.
5. A live run outside a git checkout has a stated guard.

## Ticket review 6 (fresh reviewer, 2026-09-26): two findings, all taken

1. A live run saves its base URL and model in `backend.txt`. The replay passes them back, and a test checks the model it sends.
2. The machine-name check reads a list kept outside the repository, with a case-sensitive whole-word match that leaves out the song data.

## Ticket review 7 (fresh reviewer, 2026-09-26): one finding, taken

1. The machine-name check reads every tracked text file except `data/`, `questions/`, and the recordings. Ticket 0017's proof runs it again.

## Ticket review 8 (fresh reviewer, 2026-09-26): ACCEPT
