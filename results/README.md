# Results

The frozen result tables, and the folder new live runs land in.

- `runs/`: new live runs, one folder per run, named `DATE-LABEL`. [runs/README.md](runs/README.md) explains each label. The old runs, with their recordings, are at commit [a6a6be71](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/runs). Two stub folders keep the links to them working.
- `tables/`: the scored tables, one row per system and category. `scripts/score/analyze.py` and `scripts/score/score_suite.py` wrote them.
- `answers.jsonl`: every old run's every answer, one row per case. `scripts/answers/build.py` wrote it and `scripts/answers/report.py` reports from it.
- `by-question.jsonl`: one row per question with every run's answer, probability and score.
- `history.tsv`: one dated row per run and per function measure, so drift in a model shows over time.

These tables are frozen. Build 02dc0b96 made the runs of 2026-09-23 to 2026-09-26. Builds c22512868 and aec7819bb made the runs of 2026-09-30. Builds aec7819bb and 2c5ac772b made the Kev and Nimble runs. The chat and search runs used no thinkthen build. The builders of `tables/` and `answers.jsonl` read committed runs, so a new committed run will replace the frozen tables.

## What a run folder holds

Every run holds `answers.jsonl`: one row per question with the value, the probabilities, the backend, the model, the tokens, and the wall time. A run of a model holds more.

- `recording/`: every request and response body. No header is kept, so no key is stored.
- `details.jsonl`: the command's full output per question.
- `timing.tsv`: each request's wall time.
- `ledger.txt`: the token guard's count for a live Jev run.
- `run.txt`: the thinkthen build, its SHA-256, the model, and the machine of a live Jev run.
- `backend.txt`: the base URL and the model a `./run.sh` live run used, which its replay passes back.
- `usage.json`: a chat run's tokens and dollars.
- `replay-check.txt`: the date and result of the last byte-for-byte replay.
- `outputs.jsonl` and `lists/`: a function suite's output.
- `gaps.tsv`: requests the backend refused.
- `model-time.tsv` and `shim.log`: for Laya, the model's own time per call, paired from the shim's log.
- `catalog.txt`, `questions.jsonl`, `rank-*.tsv`, `split.tsv`, and `loadavg.txt`: the old open-book and section-picking runs' inputs, section ranks, split, and machine load. A live run writes `loadavg.txt` too.

## How replay works

A run asks through the `thinkthen` command with `--cache RUN/recording`, so every exchange is saved. A replay passes `--replay RUN/recording` with the key unset. The command then answers from the recording alone, with no network and no spend, and stops on any request the recording lacks. The replay writes `RUN/replay/`, and its `answers.jsonl` must match the committed one byte for byte. A recording binds to one backend address and one model, so each backend gets its own run folder. [scripts/README.md](../scripts/README.md#replay) gives the commands.
