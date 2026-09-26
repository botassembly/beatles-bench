# 0008 One command runs the bench

Ticket: [0008](../tickets/0008-one-command-run.md). Branch `ticket/0008-one-command-run`. Built 2026-09-25 by the queue owner on the local Linux machine.

## What landed

- `run.sh` at the repository root.
  - With no `THINKTHEN_BASE_URL`, it replays `results/runs/2026-09-23-thinkthen-jev` with the key, the address, and the model name unset. It compares the replay with the committed answers, rescores every run, and prints the tables.
  - With `THINKTHEN_BASE_URL` set, it asks that backend into `results/runs/<today>-<name>`, then rescores and prints the tables. The name is its argument, else `BEATLES_BENCH_MODEL`, else `jev-latest`. Each `/` or space becomes `-`.
  - It stops with a plain message when the command is missing, and with the usage line on a wrong argument.
- `BENCH_MODEL` is now `BEATLES_BENCH_MODEL` in `scripts/run/ask.py`, `functions.py`, `rad_pipeline.sh`, `thinkthen.sh`, `scripts/README.md`, and `tests/test_replay_laya.py`. The records keep the old name.
- `scripts/score/table.py` prints a blank cost cell for a model with no price.
- `README.md` "Run it yourself" shows clone, `cd`, and `./run.sh`, then the two exports for your own backend. It explains the model name in plain words. `scripts/README.md` names each step `./run.sh` runs.
- `tests/test_run_sh.py` replaces `tests/test_replay.py`. `tests/test_table.py` covers the unpriced model.

## Commands and results

- Red first: `tests/test_table.py` failed before the fix with `ValueError: could not convert string to float: ''`, then passed.
- `./run.sh` with no key and no address printed `replayed results/runs/2026-09-23-thinkthen-jev: all answers match the committed run` and the tables. The Jev row read 67.5% Beatles-only and 70.8% overall. `git status` stayed clean.
- `./run.sh x` with no address exited 2 with the usage line. `THINKTHEN_BIN=/nope ./run.sh` exited 2 with the missing-command message.
- The live path ran once against a closed local port (`http://127.0.0.1:9/v1`) with a placeholder key value and no real key. It made `results/runs/2026-09-25-my-model-x` from the name `my model/x`, and the command stopped with its connection sentence. No request left the machine. The folder was removed.
- Suite with no key and no command, proxies pointed at a closed port: 182 tests, OK, 12 skipped.
- Suite with `THINKTHEN_BIN` set to the thinkthen build of main at e70bddab and no key: 182 tests, OK, 2 skipped (the chat backend and the harvest cache). The `./run.sh` test ran.
- `git grep -nw BENCH_MODEL -- . ':!sdlc'` printed nothing.
- No live call ran. No key was read.

## Deferred

- A live `./run.sh` run against a real backend. It spends money and needs its own ticket with a cap.
- The function suite and the figures stay separate steps.
- The other `BENCH_*` variables keep their names.
