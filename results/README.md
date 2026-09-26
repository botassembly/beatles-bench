# Results

Every run the bench made, and the tables scored from them.

- `runs/`: the current runs, one folder per run, named `DATE-LABEL`. They hold the newest run of each label: Jev, GLM-5.3 Flash, Laya, the four baselines, the three function suites, the open-book run, the section-picking runs, the one-line runs, the pipelines, and the relation-vector run. The Jev one-line run of 2026-09-24 stays beside its Laya pair. [runs/README.md](runs/README.md) explains each label.
- `tables/`: the scored tables, one row per system and category. `scripts/score/analyze.py` and `scripts/score/functions.py` write them.
- `history.tsv`: one dated row per run and per function measure, so drift in a model shows over time.
- `archive/`: runs no table reads. Each still replays or keeps its answers.
  - `archive/runs/`: superseded runs under their own names. They hold the Jev runs of 2026-09-23 and 2026-09-25 that a fresh run replaced, the first pipeline run of 2026-09-24, and `2026-09-25-examples-jev`, the live run the function folders' recordings came from. The 2026-09-25 runs replay with the thinkthen build their `run.txt` names.
  - `archive/2026-09-23-seed/`: the 629-question seed set and its runs.
  - `archive/2026-09-23-natural-phrasing/`: the baselines in the natural wording.
  - `archive/in-text-check/`: the 20-question wiring check, with the Jev and Laya recordings and results.
  - `archive/probes/`: one-off live probes, such as the Jev header probe of 2026-09-23.

## What a run folder holds

Every run holds `answers.jsonl`: one row per question with the value, the probabilities, the backend, the model, the tokens, and the wall time. A run of a model holds more.

- `recording/`: every request and response body, keyed by a hash of the request. No header is kept, so no key is stored.
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
- `catalog.txt`, `questions.jsonl`, `rank-*.tsv`, `split.tsv`, and `loadavg.txt`: the open-book and section-picking runs' inputs, section ranks, split, and machine load.

## How replay works

A run asks through the `thinkthen` command with `--cache RUN/recording`, so every exchange is saved. A replay passes `--replay RUN/recording` with the key unset. The command then answers from the recording alone, with no network and no spend, and stops on any request the recording lacks. The replay writes `RUN/replay/`, and its `answers.jsonl` must match the committed one byte for byte. A recording binds to one backend address and one model, so each backend gets its own run folder. [scripts/README.md](../scripts/README.md#replay) gives the commands.
