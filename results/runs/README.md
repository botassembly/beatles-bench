# Runs

A live run of `./run.sh NAME` with a backend address writes two folders here:

- `DATE-thinkthen-NAME`: that backend on the 1,501 questions in `questions/`, with `backend.txt` naming its base URL and model.
- `DATE-examples-NAME`: that backend on each function folder in `examples/`, one subfolder per function, with its own `backend.txt`.

`./run.sh NAME` with no address replays the newest pair of NAME. `python3 scripts/score/score.py report RUN` scores a run.

The runs behind the published tables, from 2026-09-23 to 2026-09-30, moved to Git history in ticket 0026. They are at commit a6a6be71: [results/runs](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs) and [results/archive](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/archive). Their recordings replay only under the thinkthen builds that made them. Two stub folders here keep the links the ThinkThen site uses: [2026-09-26-thinkthen-jev](2026-09-26-thinkthen-jev/) and [2026-09-26-thinkthen-jev-open-book](2026-09-26-thinkthen-jev-open-book/).

[../README.md](../README.md) says what a run folder holds and how a replay works.
