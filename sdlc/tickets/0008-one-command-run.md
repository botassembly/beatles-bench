# 0008 One command runs the bench

Owner: Claude marketing session. Status: done. Ticket review 1 returned six findings, and code review 1 returned three. The work takes all nine.

## Why

Ian asked on 2026-09-25 for the bench to run with one command. Today a reader runs four commands from the README, in order, and must know to unset the key for a replay. Ian wants four steps: clone, change into the folder, set the backend address, and run one script. The script writes a run folder and prints the tables.

Ian also asked why the model variable is called `BENCH_MODEL`. The name should say which bench it belongs to.

## Prior evidence

- `README.md` "Run it yourself" lists four commands: the tests, `scripts/run/thinkthen.sh replay`, `scripts/score/analyze.py`, and `scripts/score/table.py`.
- `scripts/run/ask.py replay RUN` writes `RUN/replay/answers.jsonl` and leaves the committed files alone. `.gitignore` already ignores `results/runs/*/replay/`.
- `analyze.py` with no arguments scores every folder in `results/runs/` whose `answers.jsonl` covers `questions/`. A new full live run joins the tables with no code change. Its label is the folder name after the date.
- On 2026-09-25, `analyze.py` over the committed runs rewrote `results/tables/` byte for byte, in 7.6 s. `git status` stayed clean.
- `results/runs/2026-09-23-thinkthen-jev/replay-check.txt` records a keyless replay that matched all 1,501 committed answers.
- `score.price` returns no price for a model missing from `scripts/score/prices.tsv`. `analyze.py` then leaves the cost cells blank. `table.py` calls `float()` on the blank `usd_per_1000_questions` cell and fails. A reader's own model hits this on the first run.
- `BENCH_MODEL` appears in `scripts/run/ask.py`, `scripts/run/functions.py`, `scripts/run/rad_pipeline.sh`, `scripts/run/thinkthen.sh`, `scripts/README.md`, and `tests/test_replay_laya.py`.
- `tests/test_replay.py` replays the Jev run into a temporary folder and checks the answers and two accuracy counts.

## Retained behavior

- Every committed run, table, recording, and report stays byte for byte.
- `scripts/run/thinkthen.sh`, `ask.py`, `analyze.py`, and `table.py` keep their arguments and output. The four-command path still works.
- The scripts never read, print, or pass the key. The `thinkthen` command reads `THINKTHEN_API_KEY` itself.
- The other `BENCH_*` variables keep their names.

## Design

- **`./run.sh`** at the repository root. No file of that name exists there now.
  - It first checks for the command (`THINKTHEN_BIN`, else `thinkthen` on the path). When it is missing, it stops with a plain message naming both.
  - An empty `THINKTHEN_BASE_URL` counts as unset.
  - **No `THINKTHEN_BASE_URL`:** the free replay. It runs `scripts/run/thinkthen.sh replay results/runs/2026-09-23-thinkthen-jev` in a subshell that unsets `THINKTHEN_API_KEY`, `THINKTHEN_BASE_URL`, and `BEATLES_BENCH_MODEL`. The Jev recording was made with `jev-latest`, so a leftover model name would break the replay. It compares `replay/answers.jsonl` with the committed `answers.jsonl` and stops with a plain message when they differ. It then runs `analyze.py` and `table.py`. The replay takes no argument. Given one, it stops with the usage line.
  - **`THINKTHEN_BASE_URL` set:** a live run. The folder is `results/runs/<today>-<name>`. The name is the first argument, or else `BEATLES_BENCH_MODEL`, or else `jev-latest`. The argument names the folder only and never sets the model. Each `/` or space in the name becomes `-`, so the folder stays one level deep and `analyze.py` finds it. It runs `scripts/run/thinkthen.sh live` on that folder, then `analyze.py` and `table.py`. A run that stops early resumes when run again the same day, as `ask.py` already does. The folder name carries the date.
  - It passes `BENCH_MAX_INPUT_TOKENS` and `BENCH_WORKERS` through unchanged. The README names `BENCH_MAX_INPUT_TOKENS` as the way to cap a live run. This repository's own paid runs still go through the live guard named in `sdlc/README.md`, not through `./run.sh`.
  - It prints the run folder before the tables.
- **Rename** `BENCH_MODEL` to `BEATLES_BENCH_MODEL` in the six files above. It stays optional, with `jev-latest` as the default. The records in `sdlc/records/` keep the old name, because they record what ran.
- **README.** "Run it yourself" keeps the line that says to install the `thinkthen` command first. It becomes:

  ```sh
  git clone https://github.com/botassembly/beatles-bench
  cd beatles-bench
  ./run.sh
  ```

  Then, for your own backend:

  ```sh
  export THINKTHEN_BASE_URL=https://your-server/v1
  export THINKTHEN_API_KEY=...
  ./run.sh
  ```

  It says in plain words: the model name matters only when one server offers several models or versions. A server with one model can ignore it. `BEATLES_BENCH_MODEL` sets it. `scripts/README.md` gets the same rename and points to `./run.sh`.
- **Unpriced model.** `table.py` prints a blank cost cell for a model with no price. The README says to add a line to `scripts/score/prices.tsv` for a cost.

## Tests

- Replace `tests/test_replay.py` with an outside-in test of `./run.sh` in a new `tests/test_run_sh.py`. With `THINKTHEN_BIN` set and no key and no base URL, `./run.sh` exits 0 and prints the Jev results row with the Beatles-only share from the committed `results/tables/accuracy.tsv`. It skips when the command is missing, as the old test did. It also skips when `git status --porcelain results/` is not empty at the start, so it never overwrites uncommitted tables. At the end, `git status --porcelain results/` is still empty. The old test checked the replay and the score. The script now checks the replay itself, and the printed row checks the score.
- A regression test for the unpriced model in a new `tests/test_table.py`. It calls `analyze.tables` on the Jev run with a `prices` function that returns `(None, "no price")`, and `analyze.write` puts the tables in a temporary folder. The test points `common.TABLES` at that folder. `table.results()` then prints the Jev row with a blank cost cell. It fails before the fix.

## Proof

- `python3 -m unittest discover -s tests` passes with no network and no `THINKTHEN_BIN`.
- With `THINKTHEN_BIN` set to a `thinkthen` build and no key, the suite passes, including the new `./run.sh` test.
- `git grep -nw BENCH_MODEL -- . ':!sdlc'` prints nothing. The `-w` flag skips `BEATLES_BENCH_MODEL`.
- `git status` is clean after the suite.
- No live call runs. No key is set.

## Deferred

- A live run of `./run.sh` against a real backend. That spends money and needs a cap in its own ticket.
- The function suite (`scripts/run/functions.sh`) and the figures stay separate steps.
- Renaming the other `BENCH_*` variables.

## Done when

The proof passes, a fresh reviewer accepts the code, and the work is committed and pushed.

## Ticket review 1 (fresh reviewer, 2026-09-25): six findings, all taken

1. The rename check now uses `git grep -nw` and leaves out `sdlc/`.
2. The README keeps the install line, and `run.sh` checks for the command first.
3. The unpriced test names its file, points `common.TABLES` at its folder, and passes a `prices` function with no price.
4. `run.sh` passes the cap and worker variables through. The README names the cap. This repository's paid runs keep the live guard.
5. The run name replaces `/` and spaces. The argument names the folder only. The replay rejects an argument. An empty address counts as unset.
6. The `./run.sh` test skips on uncommitted table edits, checks the tree stays clean, and reads the expected share from the committed table.

## Code review 1 (fresh reviewer, 2026-09-25): three findings, all taken

1. A leftover `BEATLES_BENCH_MODEL` broke the replay. The replay subshell now unsets it, and the test removes it from its environment.
2. A stopped run resumes only on the same day, because the folder name carries the date. The README and the design now say so.
3. `env -u` is not POSIX. The replay now runs in a subshell that unsets the three variables.
