# Quick Fix qf-claims: name the pinned thinkthen build

Built on 2026-09-26 on `qf/claims` from main `af538978`. A local architect review of 2026-09-26 ran `./run.sh` with a newer thinkthen build. It replayed the main run and ten function folders byte for byte, then stopped at `examples/audit/replay/audit-0.5.json`. The newer `audit` adds a `by_bin` array (thinkthen 411cb67a). The README said `./run.sh` needs "thinkthen main at 02dc0b96 or later" and "checks every replayed answer and example file against the committed ones, byte for byte". The second sentence holds only for the pinned build.

## Changes

| Claim | Where | Action | Before | After |
| --- | --- | --- | --- | --- |
| The build `./run.sh` needs | `README.md`, "Run it" | Reworded | "thinkthen main at 02dc0b96 or later, until a release carries it" | "The bench pins thinkthen main at 02dc0b96. That build wrote the committed outputs. The pin holds until a release carries `audit`." |
| The byte check | `README.md`, "Run it" | Reworded | "It checks every replayed answer and example file against the committed ones, byte for byte." | The same sentence, then "That check holds for the pinned build. A later build can replay every answer and still change an output's bytes. At thinkthen 411cb67a, `audit` added a `by_bin` array, so `./run.sh` stops at `examples/audit/replay/audit-0.5.json`." |
| The missing-audit message | `run.sh`, `tests/test_run_sh.py` | Reworded | "Install a build from thinkthen main at 02dc0b96 or later." | "Install the pinned build, thinkthen main at 02dc0b96." |
| The test build | `tests/README.md` | Reworded | "thinkthen main at 02dc0b96 or later" | "They pass with the pinned build, thinkthen main at 02dc0b96. A later build can change an output's bytes. At 411cb67a, `audit` added a `by_bin` array." |
| The know-this slide | `examples/know-this/README.md` | Reworded | The claims list named the 4× and 3–14% batching figures and the cache and caps | The list adds the slide's new batching figure, all 306 titles in one request doubling the wrong yeses, with its counts. It says the 3–14% moved to the slide's notes. It scopes the cache key and the database cap and names the two ThinkThen issues |

The talk's deck changed its know-this slide the same day. The website copies none of these files. The deck reads `README.md` "Run it" and keeps every command it checks.

## Checks

- `env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests` with `THINKTHEN_BIN` set to the pinned build (SHA-256 `eb4a5713`) and the venv from `requirements.txt`: 193 tests, OK, 1 skipped. The skip is the harvest rebuild, which needs the local `data/raw/` page cache that the worktree lacks.
- `./run.sh` with the key and the base address unset and the pinned build: exit 0. Every replay matched byte for byte, and the tables printed. No tracked file changed.
- No live or paid call ran.

## Review

A fresh read-only reviewer checked every new wording against its source. It returned two findings: a private name in this record, and two sentences with a middle appositive and a trailing clause. Both are fixed. The recheck returned ACCEPT.
