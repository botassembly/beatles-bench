# 0005 Test Laya with one catalog line as context

Ticket: [0005](../tickets/0005-laya-with-one-line-of-context.md). Branch `ticket/0005-laya-one-line`. Built 2026-09-24 by a Claude build session on the local Linux machine. Not merged. The fresh review is still to come.

## What landed

- `scripts/run/ask.py` sends a question's own `context` field before its text, in the shape it already used for `catalog.txt`. `tests/test_run.py` covers it.
- `tests/test_replay_laya.py` replays both one-line runs with no key and no tunnel, and pairs the Laya run's calls with its shim log. Its replay helper now copies `questions.jsonl` and `ids.txt`.
- `results/runs/2026-09-24-thinkthen-laya-one-line/` and `-jev-one-line/` hold the questions, recordings, answers, and timing. The Laya folder also holds `shim.log`, `model-time.tsv`, `build.py` (writes both question files), and `table.py` (prints the report's tables).
- `scripts/README.md` says how the Laya shim starts on the Mac, the tunnel, and how to stop both.
- `reports/open-book.md` gains the section "One line for Laya".

## Decisions (the owner can overturn these)

- The 7 reverse singer-to-song questions are left out. Each names four songs. No single line serves them, and the answer's line alone would give the answer away. 38 of the 45 lead-singer questions remain.
- The context is the song's line exactly as it stands in the open-book catalog, found by title. Each of the 38 titles matched one line.
- The table is printed by `table.py` in the run folder. `scripts/score/open_book.py compare` divides by zero on a run with no questions in some topic. The ticket's file limits kept that script untouched.
- Jev ran live under the cap. No earlier recording held one-line requests.

## Commands and results

- Red: `python3 -m unittest tests.test_run` failed on the new test. The request carried "Something" in place of "Catalog:\nSomething (lead: Harrison)\nText: Something".
- Green: the same command ran 6 tests, OK. Pushed as 06c98e8.
- Red for the replay test: without copying `questions.jsonl`, the one-line replay test failed with an error. Green after restoring the copy.
- Fit check: Laya's own tokenizer on the Mac counted at most 88 tokens of text, question, and options. The shim reported at most 111 input tokens. All 38 fit in 512. None was dropped.
- Laya run: `THINKTHEN_BIN=.../thinkthen/target/release/thinkthen THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/thinkthen.sh live results/runs/2026-09-24-thinkthen-laya-one-line`. 38 answers, no gaps, 3,549 input tokens, median 0.043 s a call. `model_time.py` paired every call with the shim log.
- Jev run: the thinkthen guard `sdlc/scripts/live --max-tokens 30000 JOB`, with the job running `BENCH_MAX_INPUT_TOKENS=25000 BENCH_WORKERS=4 scripts/run/thinkthen.sh live results/runs/2026-09-24-thinkthen-jev-one-line`. Ledger before: 427,899,418 charged. After: 427,934,418. That includes this run's 30,000 row and a 5,000 row this run did not write. 38 calls, no probe, 13,171 input and 1,000 output tokens, model jev-1.13.0.
- Replay: `env -u THINKTHEN_API_KEY -u THINKTHEN_BASE_URL THINKTHEN_BIN=.../thinkthen .venv/bin/python -m unittest discover -s tests` with the tunnel down ran 175 tests, OK, 1 skipped (the harvest cache test, `data/raw/` absent). The one-line replays match the committed answers byte for byte.
- No credential text in either recording (`grep -i` for bearer, authorization, api key found none).

| Model | context | right of 38 | median input tokens |
| --- | --- | --- | --- |
| Laya | none | 15 (39%) | 54 |
| Laya | one line | 27 (71%) | 92 |
| Jev | none | 13 (34%) | 293 |
| Jev | one line | 36 (95%) | 335 |
| Jev | whole catalog | 35 (92%) | 12,145 |

Laya's gain mixes reading with a change of lean. With the line it said yes to 27 of 31 yes-or-no questions and got 4 of the 15 no answers right. The report gives the breakdown.

## The Mac

- Reached from the local Linux machine over ssh, key login, no password.
- Found: no shim running, nothing on port 8791, the experiment folder `experiments/220-thinkthen-second-backend` with its venv and the cached model. Nothing was installed.
- Started: `.venv/bin/python shim.py --port 8791 --log /tmp/bb0005-shim.log > /tmp/bb0005-shim.out` (pid 27174), and a local tunnel `ssh -f -N -L 8791:127.0.0.1:8791 MAC`. The fit check ran one short Python process that read the tokenizer and exited.
- Stopped: the tunnel, then `kill 27174`, then `rm -f /tmp/bb0005-shim.log /tmp/bb0005-shim.out` after copying the log into the run folder.
- Check after: `pgrep -fl "shim.py"` on the Mac printed nothing, `lsof -iTCP:8791` printed nothing, `ps -axo pid,command | grep -i -E "shim|laya|8791"` showed only an unrelated macOS process (AmbientDisplayAgent). Both temporary files tested gone. The experiment folder listing and the md5 of its `shim.log` and `shim.out` match the listing taken before. On the local Linux machine, `pgrep -a ssh | grep 8791` and `ss -ltn | grep 8791` printed nothing.

## Left open

- The fresh review of the exact commit.
- `scripts/score/open_book.py compare` divides by zero when a topic has no questions. It belongs to a later ticket.

## Review

A fresh reviewer accepted at 2a9e043 with one finding: name the 7 dropped questions. They are reverse-singer-to-song-002, -011, -012, -018, -025, -026, and -035, all of kind singer-to-song. Each names four songs, so no single song's line serves it.
