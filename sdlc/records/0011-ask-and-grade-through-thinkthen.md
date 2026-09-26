# 0011 Ask and grade through thinkthen: record

Built on 2026-09-25 at an earlier commit on `ticket/0011-ask-and-grade-through-thinkthen`. The pinned thinkthen build is main `02dc0b96`, built from source. Its command code matches `c8ca9a65`.

## Result

- With the pinned build and no key, 165 tests pass and 2 skip. The two skips are the chat test, which needs a missing module, and the harvest rebuild, which needs the local page cache. Without the build, 165 pass and 22 skip.
- These replays match byte for byte: the Jev run, the Laya and one-line runs, examples 01 to 12, the function suite, the RAD pipeline, and the new in-text check.
- The contract test agrees with the Python tables on these cells:
  - the five one-text decide sets
  - the function-suite decide rows at 0.3 and 0.5
  - right answers in 11 of 15 question files for Jev and 15 of 15 for Laya
  - Laya overall, 537

  The four Jev files it skips each have a tie that holds the right answer. That gap is thinkthen issue `2026-09-25-audit-gives-no-share-to-a-tie-that-holds-the-right-answer.md`.
- No published table changed.
- Ian's any-server rule: `in_text_check.py` now reads `BEATLES_BENCH_MODEL`. No other script hard-codes a backend address or model outside the named exceptions.

## Code review

A fresh reviewer returned ACCEPT and ran the suite with and without the build. It accepted the three small departures:
- a replay-only output folder for `functions.py`
- `tune.sh` copying `key.jsonl` into an output folder
- the wider per-file key test

Of its four notes, the queue owner took one: the per-file test now pins the exact covered counts, 11 and 15. The frozen `tries/screen` script and `249/make.py` keep `jev-latest`, because each is bound to a Jev recording.
