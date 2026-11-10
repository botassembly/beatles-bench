# Find migration protocol: aggregate records to per-record lines

The historical suite and published results remain unchanged. Its 0.1 command selected a record across a candidate set. The 0.2 command selects a nonblank line within each record. This is a new presentation arm, not a flag rename or an established quality-equivalent replacement.

## Offline admission and representation

Run `python3 scripts/run/ask_suite.py validate-find questions/suite/find.jsonl`. It makes no command or model calls. The original inventory is 700 cases: 300 memory, 300 context, 100 card, 90 gold-none and 400 cases with multiline candidates.

The benchmark-only `find_packing.py` keeps the original question and candidate order. If every candidate is nonblank with no CR/LF, their exact texts become lines (`plain-lines-v1`). Otherwise every candidate becomes compact JSON containing `id` and `text`, with escaped CR/LF (`json-candidates-v1`). Empty or whitespace-only candidates remain encoded options. The offset map is computed after serialization in Unicode scalar values, with inclusive start and exclusive end. Duplicate text is valid; duplicate candidate or case IDs are refused. No text is truncated to fit. The engine's ordinary typed failure records a case that exceeds its limits; failed/missing/unsure outcomes cannot become none.

## Run and score the migrated arm

With an explicitly selected 0.2 `THINKTHEN_BIN`, use `python3 scripts/run/ask_suite.py packed-find NEW_RUN_DIR`. `BENCH_FUNCTIONS` selects the folder containing find.jsonl and `BENCH_SUITE_ONLY` can restrict case IDs. The existing `BEATLES_BENCH_MODEL` and `BENCH_THINKTHEN_ARGS` select the fixed model and threshold/settings. Ordinary backend environment settings belong to the command. The runner creates a new output directory; there is no implicit replay, response cache or resume in this mode. Each case sends exactly one packed record to its own command invocation.

Outputs retain the command exit, raw typed row/source, original question, original none-option flag, exact packed spans, document hash/bytes, presentation version and explicit outcome. Source records retain the engine's actual question identity/backend/model. A threshold argument is recorded separately; its absence means the engine's versioned default. No tokens, costs or request counts are invented when unavailable. The old cache/replay modes and historical result identities remain on their existing path.

Use `python3 scripts/score/score_suite.py find RUN_DIR [CASES.jsonl]` for the new arm. Exact-match success uses all labeled cases; answered accuracy uses answered cases; coverage uses all cases. Separate counts expose answered, none correct/false, unsure, typed failure, call failure, missing output and harness errors. A missing result stays in the denominator. A command that cannot start and invalid span/text mappings are harness errors. The migration report accepts only packed 0.2 output; historical aggregate results remain on the historical scorer path. This command does not update frozen tables or historical cost estimates.

## Installed-command proof

`THINKTHEN_02_BIN=/installed/bin/thinkthen python3 tests/installed_find_migration.py` exercises the actual installed command against a retained-port local HTTP fixture, with no ambient provider credential. It checks wire option count/text and one result per case for duplicate display text, Unicode scalar offsets, multiline text, blank candidates, none, unsure, low-confidence none and malformed replies. An oversized record must fail explicitly before a request. Offline scoring then distinguishes a missing result and an empty successful output. This explicit 0.2 check is separate from the historical 0.1 replay suite.

## Separately authorized live comparison

A future paid dispatch must first fix actual backend/model identity, source versions, threshold, selected cases, retry/cap policy and an approved request/token or dollar budget. The primary arms are retained 0.1 aggregate-find and 0.2 packed-find on the same immutable 700 cases, each with 700 command calls before retries. A multiline-preserving choose arm is optional and separately named/budgeted, not a replacement proof. Missing historical raw results cannot become a current baseline.

Report all denominators, the 90 none cases, none/unsure/failure transitions, and presentation differences. The new contract always has a none option, while only 90 legacy cases passed --none; preserve that distinction. There is no prompt search, universal threshold recommendation or asserted model-quality improvement. No paid comparison is authorized by this protocol. A reusable public product helper waits for evidence that the documented recipe is inadequate.
