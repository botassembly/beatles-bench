# 0011 Ask and grade through thinkthen

Owner: Claude marketing session. Status: done. The ticket review is done: three reviews. Review 1 returned 14 findings, review 2 returned 8 plus one test that does not earn its place, and review 3 returned one finding. All are fixed. It lands before ticket 0009, which reruns the bench on these paths.

## Why

Ian ruled in the marketing session's 2026-09-25 conversation: "Rerun everything and validate that everything passes, making sure that we get the same result every single time, so we can use the audit and the diff tools as well." He added the same day: "Yes test everything with thinkthen. Create new issues if necessary."

Ian added a rule on 2026-09-25: every bench script works against any ThinkThen-compliant server, not just Jev. Every backend address and model comes from `THINKTHEN_BASE_URL`, the model setting, or an argument. A hard-coded one that is simple to fix is fixed here. One that needs a thinkthen change gets a thinkthen issue.

This ticket meets that in two ways. Every call to Jev is a `thinkthen` call, and a check proves it. Every grade that `thinkthen audit` can make is checked against the bench's own tables by a contract test. Python stays the single grader of every published table. The tables move onto audit once the thinkthen issues below close.

## Asking already meets the rule

`scripts/run/ask.py` calls `thinkthen decide` or `choose` once per question. `scripts/run/functions.py` calls the function's own command once per record. Every example's `run.sh` goes through `functions.py`. This ticket rewrites no ask driver.

The drivers keep what the bench needs:

- the 140 question texts in `questions/*.jsonl`, sent as written
- the `Catalog:\n...\nText: ...` wrapping for open book and one line
- gaps: a refused question is recorded once and never asked again (`scripts/run/gaps.py`)
- the token stop, `BENCH_MAX_INPUT_TOKENS`
- `loadavg.txt`, and each call's wall time in `timing.tsv`

## Prior evidence

- `ask.py` builds `[TT, function, question, "--jsonl", "--field", "/input", "--details", ...]` for each question. `functions.py` does the same for each record.
- `scripts/run/in_text_check.py` and `tests/fixtures/audit/249/make.py` fix the binary to a path under the author's home. `reports/rad.md` line 110 gives a relative build path.
- `scripts/tools/measure.py` prototypes audit and diff. thinkthen records 0113 and 0114 landed the Rust `audit` and `diff` on 2026-09-24. Record 0114 reads the held-out half of experiment 249 as the prototype does: 87 right at 0.5 and 89 at the cut of 0.42.
- `thinkthen audit` grades `decide` and `choose` only (thinkthen `specification/audit.md`, "The verb"). Its `--by` groups by answer name, question text, or verb.
- A `choose` answer's `value` is the option label. The Jev row for `comparison-longer-001` has `"value":"a"`, and its question has `"truth": "a"`.
- The questions are 1,273 `choose` and 228 `decide`. No key file exists for them.
- The author ran `thinkthen audit` (thinkthen 0.0.1, the experiment 259 build) over the 2026-09-23 Jev run with a key built from `truth`, no key and no network. Lead-set John gave 26 rows, 11 right at 0.5, yes recall 0.368421, AUC 0.56391, and mean p(yes) 0.466923. `decide.tsv` prints 11, 0.3684, 0.564, and 0.4669. All 1,501 gave 903 `choose` and 155 `decide` right, with 15 ties. `accuracy.tsv` prints 1062.0. The gap of 4.0 is the tie share. The calibration errors differ by method.
- `decide.tsv` has seven Jev sets. Five have one question text each: lead-set george, john, paul, and ringo, and shared-lead. multi-hop same-month spans 51 texts and reverse singer-yes-no spans 2, so audit cannot group them without a record field.
- `results/tables/functions.tsv` takes its decide and choose rows from the 1,501. The decide row is 228 questions at 0.680, with TP FP TN FN of 98 89 35 6 at 0.3 and 43 12 112 61 at 0.5.
- Laya overall is 537.0 of 1,501 with no ties.
- Every example's `run.sh live` writes into its own committed folder, because `functions.py live RUN` writes to `RUN`. `12-diff/diff.sh` takes an output folder but reads its input from `../11-audit/`. The digests of the cold and context rows differ.
- Stale prototype text sits in `README.md` line 61 and the map line 102 ("and tools"), `scripts/README.md` line 12, `scripts/tools/README.md`, `reports/leaning-no.md` (its commands, and "They use only the Python standard library"), `reports/results.md` (the yes/no cuts line), and `paper/notes.md` line 7. `tests/test_measure.py` is the only reader of `tests/fixtures/audit/small/` and `249/key-noparts.jsonl`.
- `tests/test_replay_laya.py` replays Laya with `THINKTHEN_BASE_URL=http://127.0.0.1:8791`, the address the recording was made at.
- No thinkthen release exists (thinkthen issue `2026-09-25-release-and-install-for-0-1.md`). The proof pins thinkthen origin/main at `02dc0b96`. Its command code is the same as at `c8ca9a65`.

## Inventory

### Paths that ask

| Path | Calls | Check |
| --- | --- | --- |
| `ask.py`, `thinkthen.sh` | `thinkthen decide`, `choose` | stays |
| `functions.py`, `functions.sh`, `examples/NN-name/run.sh` | the function's command | stays |
| `rad.py` pick and answer, `rad_pipeline.sh` | `thinkthen`, through `thinkthen.sh` or directly | stays |
| `in_text_check.py` | `thinkthen` at a fixed path | reads `THINKTHEN_BIN` |
| `chat.py` | GLM through its own structured output | exception |
| `baselines.py` word overlap, BM25, embeddings, hybrid | no model, or a local sentence-transformer | exception |
| `rad.py rank bm25`, `rank minilm` | BM25, or a local sentence-transformer | exception |
| `relation_vectors.py` | local embedding and reranker models | exception |
| `scripts/harvest/` | Wikipedia and Wikidata, no model | exception |
| `examples/context-article.md` | `thinkthen` over text fetched at run time | stays, with no recording |

Laya ran through `thinkthen` against a local shim. It is no exception.

### Paths that grade

Every grader stays in Python. None moves to audit in this ticket.

| Path | What it grades |
| --- | --- |
| `analyze.py`, `score.py`, `stats.py` | the tables in `results/tables/`, and `score.py report`, `sweep`, `diff`, `calibration`, `history` |
| `scripts/score/functions.py` | the function suite |
| `open_book.py compare`, `rad_table.py` | the open-book and RAD arms |
| `rad_pipeline.sh` | its `jq` scoring into `checks.tsv` and `scores.tsv` |
| `in_text_check.py` | its `RESULTS-*.tsv` |
| `results/runs/2026-09-24-thinkthen-laya-one-line/table.py` | the one-line table in `reports/open-book.md` |
| `examples/11-audit/tune.sh`, `examples/12-diff/diff.sh` | already `thinkthen audit` and `thinkthen diff` |
| `scripts/tools/measure.py` | retired |

GLM, the four baselines, and the sentence-transformer, BM25, and vector arms fall under Ian's comparison exception for asking and grading.

### The contract with thinkthen audit

A contract test runs `thinkthen audit` on the committed Jev and Laya runs and asserts it agrees with the Python tables. It covers each cell that matches:

- the five one-text decide sets in `decide.tsv`: right at 0.5, yes recall at 0.5, AUC, and mean p(yes)
- the function-suite decide rows: n, right at 0.5, and TP FP TN FN at 0.3 and 0.5
- `choose` right answers as run, for each question file where no tie holds the answer
- Laya overall right answers

Each cell that does not match is named with its thinkthen issue:

| Cell | thinkthen issue |
| --- | --- |
| multi-hop same-month and reverse singer-yes-no in `decide.tsv` | `2026-09-25-audit-cannot-group-by-a-record-field.md` |
| Scopes by category, kind, fact, and direction | `2026-09-25-audit-cannot-group-by-a-record-field.md` |
| Right answers where a tie holds the answer | `2026-09-25-audit-gives-no-share-to-a-tie-that-holds-the-right-answer.md` |
| The held-out tuned cut in `decide.tsv` | `2026-09-25-audit-tunes-its-cut-on-one-half-and-never-swaps.md` |
| ECE, its interval, and the calibration bins | `2026-09-25-audit-calibration-differs-from-the-benchs-ece-and-its-interval.md` |
| Coverage at each confidence, and the choose coverage rows | `2026-09-25-audit-reports-coverage-at-one-rule-not-along-every-confidence.md` |
| The paired test between systems | `2026-09-25-diff-mcnemar-leaves-out-pairs-that-become-right-from-not-sure.md` |
| `tag`, `score`, `filter`, `rank`, `find`, `annotate`, `recognize`, `relate` | `2026-09-25-audit-is-complete-for-0-1.md`. `recognize` and `relate` are F1, section 1 |

## Retained behavior

- Every committed run folder, table, report number, and recording stays byte for byte. No published number changes.
- The ask drivers keep the five behaviors listed above.
- The recordings the suite replays today still replay with no key. The Laya replays use `THINKTHEN_BASE_URL=http://127.0.0.1:8791`.
- `./run.sh` keeps its arguments and output. The scripts never read, print, or pass the key.
- `tests/fixtures/audit/249/` keeps `control.jsonl`, `soft.jsonl`, `key.jsonl`, and `make.py`.

## Design

1. **Key files.** `scripts/generate/generate.py` also writes `questions/keys/NAME.jsonl` for each question file: one `{"id", "value"}` line per question. A `decide` value is `"yes"` or `"no"`. A `choose` value is the label, `q["truth"]`. Key lines carry no `part`, so audit makes its own seeded split. The generator stays deterministic. The contract test reads them.
2. **Retire the prototype.** Delete `scripts/tools/`, `tests/test_measure.py`, `tests/fixtures/audit/golden/`, `tests/fixtures/audit/small/`, and `tests/fixtures/audit/249/key-noparts.jsonl`. thinkthen keeps its own copies in `crates/thinkthen/tests/fixtures/measure/`. Rewrite the stale text in Prior evidence. The README map line drops "and tools". The commands in `reports/leaning-no.md` become `thinkthen audit --by verb` and `thinkthen diff`, and their printed numbers stay.
3. **Fixed paths.** `in_text_check.py` and `249/make.py` read `THINKTHEN_BIN`, with `thinkthen` on the path as the default. `reports/rad.md` says `THINKTHEN_BIN=path/to/thinkthen`.
4. **Example folders.** Every `examples/NN-name/run.sh` takes an optional output folder, as `live|replay [OUT]`. `live` without `OUT` refuses, so a live run never writes into the committed folder. `12-diff/run.sh` and `diff.sh` take an input folder holding `rows.jsonl`, `rows-context.jsonl`, and `key.jsonl`, and an output folder. Their defaults keep today's replay.
5. **Diff guard.** `scripts/score/diff_guard.sh A B [--allow-unpaired] [--no-digest] -- DIFF_ARGS` runs `thinkthen diff` and reads its summary. It stops when `records` is 0. It stops when `only_a` or `only_b` is above 0, unless `--allow-unpaired`. It stops when any pair's `meta.question_sha256` differs, or a row has none, unless `--no-digest`. Its callers are `12-diff/diff.sh` with `--no-digest`, the leaning-no control-against-soft diff with `--no-digest`, and ticket 0009's old-against-fresh pairs. The leaning-no control and soft runs use different wordings by design, so every digest differs. The leaning-no Test 1 diff, `thinkthen diff control.jsonl --compare-threshold 0.42`, compares two cuts on one run. The guard takes two runs, so that command runs `thinkthen diff` directly.
6. **No audit.** `./run.sh` checks `thinkthen audit --help` after its command check. When it fails, it stops with: "run.sh: this thinkthen has no audit command. Install a build from thinkthen main at 02dc0b96 or later."

## Tests

- **Contract with audit.** `tests/test_audit_contract.py` runs `thinkthen audit` with the key files on the committed Jev and Laya runs. It asserts each covered cell equals the Python table, rounded as the table prints it. It skips without `THINKTHEN_BIN`.
- **Function tables unchanged.** One case runs `scripts/score/functions.py table` on the committed function runs into a temporary folder and compares it with `results/tables/functions.tsv` byte for byte.
- **Leaning-no reproduced.** `tests/test_leaning_no.py` runs `thinkthen audit ... --by verb` and `thinkthen diff` on `tests/fixtures/audit/249/`: the control-against-soft diff through the guard with `--no-digest`, and the Test 1 cut diff directly. It checks the tuned cut of 0.42, the held-out accuracy of 0.645, and the yes recall of 0.607. It skips without `THINKTHEN_BIN`.
- **Choose key.** One case in `tests/test_generate.py` checks the key line for `comparison-longer-001`: value `"a"`, equal to the committed Jev row's `value`. It also checks one key line per question, no `part`, and byte-for-byte output on a second run.
- **Diff guard.** An edge-case table in one test: matching runs pass; `records` 0 stops; one unpaired id stops, and passes with `--allow-unpaired`; one pair with a different digest stops, and passes with `--no-digest`; a row with no digest stops, and passes with `--no-digest`.
- **Example folders.** One case checks that `run.sh live` without `OUT` refuses and writes nothing.
- **No audit.** One case in `tests/test_run_sh.py` points `THINKTHEN_BIN` at a stub with no `audit`. `./run.sh` exits nonzero with the message.
- **In-text check.** One case replays `results/in-text-check/jev-recording` with `in_text_check.py jev` and no key, and compares `RESULTS-jev.tsv` byte for byte.

`tests/test_run_sh.py` already checks that `analyze.py` leaves `results/` unchanged, so no new test repeats it.

## Proof

Run against the pinned build: thinkthen origin/main at `02dc0b96`.

- `python3 -m unittest discover -s tests` passes with no network and no `THINKTHEN_BIN`.
- With `THINKTHEN_BIN` set to the pinned build and no key, the suite passes. The recordings it replays match byte for byte: the Jev run through `test_run_sh.py`, the Laya and one-line runs through `test_replay_laya.py` with `THINKTHEN_BASE_URL=http://127.0.0.1:8791`, the examples through `test_examples.py`, and the in-text check through its new case. The record lists every other replay test that ran.
- The contract test passes.
- `git status` is clean after the suite.
- `git grep -n measure.py -- . ':!sdlc'` prints nothing.
- `reports/leaning-no.md` line 114, `python3 -m unittest tests.test_measure`, is rewritten to name `tests/test_leaning_no.py`. `git grep -n test_measure -- . ':!sdlc'` prints nothing.
- `git grep -n target/release/thinkthen -- . ':!sdlc'` prints nothing.
- `git grep -lE "urllib|import requests|http\.client|openai|instructor|curl " -- 'scripts/*.py' 'scripts/*.sh' 'examples/*.sh' run.sh` lists only `scripts/harvest/harvest.py` and `scripts/run/chat.py`, the two exceptions that open a connection.
- No live call runs. No key is set.
- `git grep -n -i -E "https?://|typesafe|systemone|jev-latest|laya-mlx|127\.0\.0\.1|localhost" -- 'scripts/*.py' 'scripts/*.sh' 'examples/*.sh' run.sh ':!scripts/harvest'` finds each model name only as the default of `BEATLES_BENCH_MODEL`, in `run.sh`, `ask.py`, `functions.py`, `rad_pipeline.sh`, and `in_text_check.py`. It finds no ThinkThen backend address. The other hits are the GLM comparison exception in `chat.py`, whose address and model come from `CHAT_BASE_URL` and `CHAT_MODEL`, and the SVG namespace in `scripts/figures/common.py`.

## Owner's decisions (Ian can overturn each)

- No published table moves to audit in this ticket. Python stays the single grader. A contract test checks each cell audit can make against the Python tables. This avoids two code paths and a set of per-cell exceptions.
- Asking stays as it is. Every model call is already a `thinkthen` call. The ask rows are checks.
- The comparison exception covers asking and grading for GLM, the baselines, and the sentence-transformer, BM25, and vector arms. Laya is checked by the contract.
- The `choose` key value is the label, `q["truth"]`.
- The diff guard has three named callers: `12-diff/diff.sh` with `--no-digest`, the leaning-no commands, and ticket 0009's pairs.
- The proof pins thinkthen origin/main at `02dc0b96`. `./run.sh` stops when the installed thinkthen lacks `audit`.
- Key files live in `questions/keys/`, written by the generator, with no `part`.
- A live example run needs an output folder.

## Deferred

- The published tables move onto audit once their thinkthen issues close, each cell with its issue.
- A thinkthen release. It waits on thinkthen `2026-09-25-release-and-install-for-0-1.md`. Until then a reader builds from main.
- Rerunning anything. Ticket 0009 does that.

## Done when

The proof passes, a fresh reviewer accepts the code, and the work is committed and pushed to main.

## Ticket review 1 (fresh reviewer, 2026-09-25): 14 findings, all taken

1. The `choose` key holds the label, with a test on a committed row.
2. Four new thinkthen issues cover the tuned cut, ECE, coverage, and grouping.
3. GLM and the baselines fall under the exception. Laya is checked by the contract.
4. The diff guard stops on no pairs and on unpaired answers. Its digest check can be turned off.
5. Asking stays. The retained ask behaviors are listed.
6. The embedding, MiniLM, BM25, and vector arms are exceptions.
7. The function suite stays in Python. `recognize` and `relate` are F1.
8. The thinkthen commit is pinned. `./run.sh` stops without audit. The release is deferred.
9. `stats.py`, the `score.py` subcommands, and `249/make.py` are in the inventory.
10. The binary-path grep covers the whole repository outside `sdlc`. `paper/notes.md` and the leaning-no sentence are on the stale-text list.
11. The leaning-no test uses `--by verb`.
12. The examples evidence is corrected. Every asking example gets an output folder.
13. The Laya replay uses `THINKTHEN_BASE_URL=http://127.0.0.1:8791`.
14. Key lines carry no `part`.

## Ticket review 2 (fresh reviewer, 2026-09-25): 8 findings and one test, all taken

1. The two decide sets that span several texts are named with the grouping issue.
2. The choose cells are covered per question file where no tie holds the answer. Laya overall is covered.
3. The function-suite decide rows are in the contract.
4. `rad_pipeline.sh` scoring, `in_text_check.py`, and the one-line `table.py` are graders that stay in Python.
5. The replay claim names the tests that replay, and the in-text check gains a replay case.
6. No cell moves, so there is one code path. The contract test skips without the binary.
7. The diff guard names its three callers. `12-diff` uses `--no-digest`.
8. The deletes cover `small/` and `249/key-noparts.jsonl`, and the README map drops "and tools".
- The `analyze.py` half of "every table unchanged" is dropped. `test_run_sh.py` covers it.

## Ticket review 3 (fresh reviewer, 2026-09-25): one finding, fixed

The reviewer confirmed every spot-checked cell. The one blocking finding: the guard would stop the leaning-no diffs. The control-against-soft diff now runs through the guard with `--no-digest`, because the two runs use different wordings by design. The Test 1 cut diff runs `thinkthen diff` directly, because the guard takes two runs. A proof line covers the rewrite of `reports/leaning-no.md` line 114.
