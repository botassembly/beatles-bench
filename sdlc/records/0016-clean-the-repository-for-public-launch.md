# 0016 Clean the repository for public launch: record

Built on 2026-09-26 on `ticket/0016-clean-the-repository-for-public-launch` from main at 7d246844. No model call ran. No key was set or read. The spend is $0.

The work lands in two commits. The first changes the text and the code. The second moves the superseded runs and adds the two `.gitignore` lines. The tests pass only after the second commit, because the tests read the archive paths.

## Result

1. **Internal words.** Every tracked text file outside the recordings now uses plain words for sessions, agents, experiment paths, workspace paths, the private note, the deck's slide source, and the machine nickname. Every ticket's Owner line reads "Owner: the queue owner." A ledger's binary path reads "a local build", and its SHA-256 stays. A bench hash that no longer resolves reads "an earlier commit". A deck repository hash reads "a deck repository commit". `sdlc/README.md` says one agent owns the queue under Ian, and it says why `sdlc/` is public.
2. **Pages leave for the website.** `docs/walkthroughs/`, `docs/run-it-for-free.md`, `docs/context-article.md`, and `docs/README.md` are deleted. The README's "Learn more" links https://thinkthen.dev/learn/beatles-bench/. The function folder READMEs keep their site link and drop the walkthrough link.
3. **Pages merge.** `data/README.md` takes the four sections of `docs/the-data.md`: one row, from a row to a question, how Jev answered it, and the catalog. `reports/open-book.md` ends with "Context and cost". Its whole-catalog subsection repeated the fresh-run section and was dropped. `docs/context.jq` moved to `scripts/score/context.jq`. `docs/` no longer exists. `tests/test_function_folders.py` checks the commands in the merged sections.
4. **Top README.** The README follows the ticket's order. The Jev numbers come from 2026-09-26. GLM, Laya, and the baselines come from 2026-09-23. The GLM and Laya times read "build and load not recorded". The Jev time names its load average, 3.83 to 7.10 on 16 cores. "What's new" has five dated lines.
5. **New READMEs.** `tests/README.md` gives the suite command and the `THINKTHEN_BIN` rule, and it lists nine files that skip and why. `paper/README.md` names the runs the notes use. `results/runs/README.md` gives each label with its system, its questions, and its report. It also names the two labels `./run.sh NAME` writes.
6. **scripts/README.md.** The page keeps five sections: set up, replay, rerun, add a backend, and draw figures. Both sentences the deck checks stay word for word. The Laya section moved to "How the Laya runs were made" below. Kev now runs through `./run.sh kev`.
7. **Archive.** `results/archive/runs/` holds 14 folders. Five are the 2026-09-23 Jev folders, one is `2026-09-24-pipeline-jev`, seven are the superseded 2026-09-25 folders, and the last is `2026-09-25-examples-jev`. `results/archive/probes/` and `results/archive/in-text-check/` hold the two folders of those names. `results/runs/` keeps 19 runs. `results/README.md` describes each part of the archive.
8. **Reports.** Every link and plain-text mention of a moved run now names its archive path.
9. **Paper notes.** `paper/notes.md` takes the 2026-09-26 Jev numbers. GLM keeps its 2026-09-23 numbers. A finding with no fresh run keeps its number and names its date.
10. **run.sh.** `./run.sh [NAME]` takes the name from its argument alone and defaults to `jev`. A live run writes `results/runs/DATE-thinkthen-NAME/` and `results/runs/DATE-examples-NAME/NAME/`. Both folders get `backend.txt` with the base URL and the model. A replay reads `backend.txt` and sends the same base URL and model with no key. A replay of `jev` replays the committed function folders. Any name then replays its newest examples folder when one exists. `scripts/run/example.sh NAME replay [OUT] [FROM]` takes the FROM folder. A live run stops with exit 2 in three cases:
   - The model is set and the run has no name.
   - A folder holds a file git tracks.
   - Outside git, a folder already holds files.

## Numbers in paper/notes.md

The 2026-09-26 Jev figures came from `results/runs/2026-09-26-thinkthen-jev` and its open-book, RAD, and RAD2 runs. GLM came from `results/runs/2026-09-23-glm-5.3-flash`. The main changes:

| Finding | Before (2026-09-23) | Now (2026-09-26) |
| --- | --- | --- |
| Jev overall, the 1,501 | 70.5% | 70.0% |
| Every topic weighted equally, Jev | 64.8% | 64.0% |
| Jev misses, and GLM right on them | 443 and 416 | 451 and 423 |
| Open book, misses fixed and hits broken | 126 of 134 and 1 of 62 | 117 of 128 and 1 of 68 |
| RAD: Jev pick, full catalog, BM25 | 167, 187, 163 | 170, 184, 162 |
| Jev median time | 0.30 s, no load recorded | 0.21 s, load 3.83 to 7.10 |

The weighted open-book figure of 97% and the "seven of nine" misread finding keep their 2026-09-23 date. No fresh run measures them.

The method first reproduced the published 2026-09-23 numbers from the archived run. Every figure matched with two exceptions. The reversal pairs gave 65 and 91, where the page printed 64 and 92. The topic-weighted shares gave 64.6% and 94.7%, where the page printed 64.8% and 94.4%. The published figures came from a method the bench no longer holds. The fresh figures all come from the same method, so each row compares like with like. The GLM topic-weighted figure keeps its published 94.4%.

## How the Laya runs were made

The bench reached Laya on a Mac with an Apple M5 chip. A small local server on the Mac spoke the System One API for Laya. The server needs no key, so the runs sent `local` as a dummy key. An SSH tunnel carried one call at a time to port 8791. The server logged each call to a temporary file. That file was then copied into the run folder as `shim.log` and removed from the Mac.

The runs:

```sh
THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/thinkthen.sh live results/runs/2026-09-23-thinkthen-laya
THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/functions.sh live results/runs/2026-09-23-functions-laya
THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/thinkthen.sh live results/runs/2026-09-24-thinkthen-laya-one-line
python3 scripts/run/model_time.py RUN RUN/shim.log   # pairs each call with the server's log lines
```

The one-line runs ask each lead-singer question of the open-book sample with only its song's catalog line in the question's `context` field. A question that names four songs has no one line and is left out. `reports/open-book.md`, section "One line for Laya", gives the command that writes `questions.jsonl` and `ids.txt`.

`tests/test_replay_laya.py` replays every Laya run from its recording with no key and no Mac.

## Tests

- `tests/test_published_numbers.py` holds 13 claims. Each gives a page, the quoted text, and the source that computes the number. A second test pins the values the talk shows: 306, 1,501, 1,313, 68 (35%), 184 (94%), 31.4%, and 37.6%. A README changed from "68 (35%)" to "69 (35%)" failed two claims, and the restored README passed.
- `tests/fixtures/fake-thinkthen-run` serves a live run and its replay. It binds each recording to its base URL and model, as the real command does. A replay with another address or model stops.
- `tests/test_run_sh.py` gains `LiveRunTest`, with five cases. It clones the working repository, copies the code under test over the clone, and commits it there.
  1. A live `./run.sh demo` and its replay. Every replayed file equals the live file.
  2. A live run of model `other` and its replay. The fake's log shows the replay sends the same `--model` and base URL.
  3. A replay of a name with no run exits 2 with its message.
  4. A live run with the model set and no name exits 2 and adds no run folder.
  5. A live run into a folder with a committed `run.txt` exits 2 and writes nothing.

## Proof

- **Suite.** `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests`:
  - With `THINKTHEN_BIN` set to the 02dc0b96 build (SHA-256 `eb4a5713`): 184 tests, OK, 2 skipped.
  - With no `THINKTHEN_BIN` and no `thinkthen` on `PATH`: 184 tests, OK, 22 skipped.
- **Replay.** `./run.sh` with no key and no address exited 0. It printed "replayed results/runs/2026-09-26-thinkthen-jev: all answers match its answers.jsonl" and 12 lines of "replayed functions/NAME: every file matches the committed folder". `git status` was clean after it.
- **Unchanged files.** `git diff --stat 7d246844 HEAD` over `results/tables/`, `results/history.tsv`, and `questions/` prints nothing. No recording file changed outside a pure rename. `git diff -M --name-status` of the second commit gives 11,593 files at R100 and one modified file, `.gitignore`.
- **Fresh clone.** A fresh clone of the branch passed the suite with the build: 184 tests, OK, 2 skipped. `git status` stayed clean after it. The clone's working tree is 221 MB.
- **Internal words.** The internal-word check in the ticket's Proof section printed nothing outside recordings and tickets 0016 and 0017.
- **Private and machine names.** The private-names check listed 0 files. The machine-name check counted 0 matches.
- **Hex tokens.** The hex check reads every tracked Markdown file and script outside recordings, run data, tickets 0016 and 0017, and this record. The record quotes the check's output. It skips SHA-256 lines. It keeps each 7 to 40 character token with a letter from a to f and a digit. It then asks whether the token is an ancestor of the bench's HEAD or of thinkthen's main. It printed two lines:

  ```text
  UNRESOLVED reports/results.md aac6fef
  UNRESOLVED tests/test_model_time.py aac6fef
  ```

  Both are one exception. `aac6fef` is part of the Laya model id `aac6fef/laya-mlx`. The token names no commit, and it stays.
- **Links.** A checker resolves every relative link in every tracked Markdown file against the working tree, with anchors checked against headings. It printed "129 relative links, 0 broken". The count was 229 before the change, because the deleted pages held 100 links.

### Archived 2026-09-25 Jev runs

The loop replays each archived 2026-09-25 Jev run with the 02dc0b96 build, the key unset, and the model `jev-latest`. It then compares the replay with the committed file:

```sh
A=results/archive/runs
for r in thinkthen-jev thinkthen-jev-open-book thinkthen-jev-rad thinkthen-jev-rad2 thinkthen-jev-one-line; do
  scripts/run/thinkthen.sh replay $A/2026-09-25-$r; cmp $A/2026-09-25-$r/replay/answers.jsonl $A/2026-09-25-$r/answers.jsonl
done
scripts/run/functions.sh replay $A/2026-09-25-functions-jev
scripts/run/rad_pipeline.sh replay $A/2026-09-25-pipeline-jev   # compare scores.tsv and checks.tsv
for each NN-NAME folder of $A/2026-09-25-examples-jev but 12-diff:
  scripts/run/example.sh NAME replay FOLDER/replay FOLDER; cmp FOLDER/replay/outputs.jsonl FOLDER/outputs.jsonl
```

Output:

- The five `thinkthen-jev` runs matched their `answers.jsonl`.
- The pipeline run matched its `scores.tsv` and `checks.tsv`.
- The eleven examples folders matched their `outputs.jsonl`.
- `2026-09-25-functions-jev` stopped at `recognize-01` with exit 5. Its recording holds no entry for the current request.

The recognize and relate cases changed on 2026-09-26, when ticket 0014 scored them from the shipped commands. The recording holds the old requests. The same replay fails at main 7d246844, before this ticket. The six functions with unchanged cases replay from that run with `BENCH_TESTS=tag,score,filter,rank,find,annotate`: 1,156 outputs, each byte for byte equal to its committed line.

## Downstream

- **The website.** The site preview copies 71 bench files. `git diff --name-only 2cdb6445 HEAD` over those 71 paths prints nothing, and each path exists at HEAD.
- **The talk deck.** The deck built against the branch stops at its first bench check: `docs/walkthroughs/decide.md is missing`. A copy of the branch with the pre-ticket `docs/walkthroughs/` and `paper/notes.md` restored built all 30 pages with exit 0. A copy with only `docs/walkthroughs/` restored stops at the notes phrase "Numbers come from the audited 1,501-question runs of 2026-09-23". Of the phrases the deck quotes from the notes, the refresh also changes "Every topic weighted equally: Jev 64.8%, GLM 94.4%.". Every other bench path and phrase the deck reads holds on the branch. The deck issue lists each change the deck needs.
- **Issues filed.** Each issue sits on its repository's main:
  - ThinkThen: `sdlc/issues/2026-09-26-the-beatles-bench-section-keeps-its-own-copy.md`. It revises the worked-examples issue of 2026-09-25, records 7d246844 as the source of the site's copy, drops the older issue's dead bench pin, and gives ticket 0017's path map.
  - The talk deck: `sdlc/issues/2026-09-26-beatles-bench-0016-moves-pages-the-deck-reads.md`. It lists the deleted walkthroughs, the two changed notes phrases, the archived runs, the kept lines, and the 2cdb6445 pin.

## Deferred

- The archived `2026-09-25-functions-jev` run replays only its six unchanged functions. Its recognize and relate requests predate the 2026-09-26 cases. A full replay would need the old case files, and the bench no longer holds them.
- The deck builds against this branch only after its issue lands.
- The ticket's own Deferred list stands: a released thinkthen build, the 2026-09-23 replays, the repository size, a GLM and Laya time rerun, and command checks for the site's copy of the walkthroughs.

## Reviews

The code review section follows the review.
