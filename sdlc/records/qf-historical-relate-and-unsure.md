# Quick Fix qf-historical-relate-and-unsure: label old relate results and name the new word

Built on 2026-09-29 on `qf/historical-relate-and-unsure` from main `ed8ffe49`. ThinkThen issues `2026-09-27-site-and-bench-relate-pair-examples.md` and `2026-09-27-marketing-audit-diff-wording.md` asked for these changes. ThinkThen ticket 0167 replaced relate's choice planner with one yes or no question per allowed pair. ThinkThen ticket 0152 renamed the machine word for a not sure answer to `unsure`.

## Changes

| Claim | Where | Action |
| --- | --- | --- |
| The relate rows of the function table | `reports/results.md` | A note under the table labels the rows historical. It names the old choice planner, thinkthen main at 02dc0b96, and 2026-09-26. The planner description moves to past tense. No number changed |
| The relate example's answers | `examples/relate/README.md` | A note labels them historical and links the site's pair-planner page |
| `0 unresolved` in the audit count | `examples/audit/README.md` | A note says the pinned build prints `unresolved`, and ThinkThen main at ce04682c prints `0 not sure` |
| `unresolved -> no 44` in the diff table | `examples/diff/README.md` | A note says ThinkThen main at ce04682c prints `unsure -> no 44` |

The blocks themselves stay as the pinned build printed them, so the byte check still holds. The new words come from ThinkThen main at ce04682c, run by hand over the committed answers in `examples/audit/outputs.jsonl`. `audit --table` printed `50 right, 20 wrong, 0 not sure, 0 tied`. `diff --table` at `0.2:0.8` printed `unsure -> no 44; yes -> no 3; unsure -> yes 1`.

The bench has not scored the pair planner. A rerun of the relate corpus needs a ticket with a token cap.

## Checks

- `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests` with `THINKTHEN_BIN` set to the pinned build (SHA-256 `eb4a5713`): 193 tests, OK, 1 skipped (the harvest rebuild).
- No live or paid call ran.

## Review

A fresh read-only reviewer checked every changed sentence against deslop, voice and its source. Three rounds returned findings on tense, placement of the historical label, and a status word. All are fixed.
