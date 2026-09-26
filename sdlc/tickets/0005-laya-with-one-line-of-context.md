# 0005 Test Laya with one catalog line as context

Owner: Claude marketing session. Status: landed 2026-09-24. Code review ACCEPT at 2a9e043 with one record fix.

## Why

Laya holds 512 tokens per request, too few for the catalog. One song's catalog line fits. The test shows whether a small local model gains from RAD the way Jev does.

## Work

1. On the Mac, as a light one-time check under the workspace machine rules: start the Laya shim if it is not running, reach it through the SSH tunnel in `scripts/README.md`, and stop what you started when done.
2. Ask Laya the lead-singer questions from the open-book sample with only that song's catalog line before the question. Use `scripts/run/ask.py` with a one-line catalog, recorded so it replays.
3. Compare with Laya closed book on the same questions, and with Jev with the same one line (from the recording, or live under the cap).
4. Report the table in `reports/open-book.md`, section "One line for Laya".

## Limits

Jev live cap: 50,000 input tokens. Laya costs nothing. Nothing is left running on the Mac.

## Done when

The replay passes with no key and no tunnel, a fresh reviewer accepts, the Mac is left as found, and the work is committed and pushed.

## Ticket review 1 (fresh reviewer, 2026-09-24): three findings, all taken

- `ask.py` takes one catalog per run. Red first: add a per-question `context` field in `questions.jsonl` that `ask.py` sends before the text, with a test.
- Find how the Laya shim starts on the Mac and the tunnel command, and write both into `scripts/README.md` before the run.
- Name the lead-singer questions from the open-book sample by id, and check each request fits in 512 tokens. Drop any that do not, and say so.
