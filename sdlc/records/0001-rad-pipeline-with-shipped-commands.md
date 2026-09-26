# 0001 Show retrieval-augmented decisions with shipped ThinkThen commands

Ticket: [0001](../tickets/0001-rad-pipeline-with-shipped-commands.md). Branch `ticket/0001-rad-pipeline`. Built 2026-09-24 by a Claude build session.

## What landed

- `scripts/run/rad_pipeline.sh` runs the three steps with `thinkthen` and `jq` only. It uses `--record` on a live run and `--replay` otherwise. `scripts/run/rad_pipeline.checks.json` holds the correctness and grounding checks.
- `tests/test_rad_pipeline.py` drives the script with the fake binary and replays the committed run with the real one. `tests/fixtures/fake-thinkthen` now answers `tag` and `annotate`, reads `--input`, and logs its arguments when `FAKE_LOG` is set.
- `results/runs/2026-09-24-pipeline-jev/` holds the live run, its recording, and `ledger.txt`.
- `reports/rad.md` gains the section "With shipped commands".

Every flag the ticket names ships in `thinkthen` 0.0.1: `--details`, `--field`, `--jsonl`, `--options`, `--record`, `--replay`, and `--input`.

## Commands and results

- Red: `python3 -m unittest tests.test_rad_pipeline` failed with the script missing (1 error, 1 skipped).
- Green: the same command passed (1 run, 1 skipped) with the fake binary.
- Live: `THINKTHEN_BIN=<thinkthen>/target/release/thinkthen <thinkthen>/sdlc/scripts/live --max-tokens 200000 scripts/run/rad_pipeline.sh live results/runs/2026-09-24-pipeline-jev` exited 0. The guard's `charged_tokens` went from 427,569,418 to 427,769,418.
- Replay: `THINKTHEN_BIN=<thinkthen>/target/release/thinkthen python3 -m unittest tests.test_rad_pipeline` passed both tests with the key unset.
- Full suite at the record commit: `python3 -m unittest discover -s tests` ran 156 tests, OK, 8 skipped. With `THINKTHEN_BIN` set and the key unset it ran 156, OK, 2 skipped.

## Tokens spent

92 requests: 75,467 input and 5,054 output tokens, or 0.0032 dollars. The ticket's cap was 200,000 input tokens.

## Open

- Code review: a fresh reviewer returned ACCEPT at a7beabc. It observed 156 tests OK with 8 skipped, and the replay test OK with no key. The context input is dropped in the deck repo's `sdlc/planning/thinkthen-asks.md`.
- The deck repo's asks file still needs the send-or-drop line. The build session recommends drop and left that file to its owner.
- The grounding check saw only right answers. A case with a planted wrong answer would show whether it catches one.
