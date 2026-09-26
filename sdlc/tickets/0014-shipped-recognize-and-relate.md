# 0014 Score recognize and relate from the shipped commands, then rerun every Jev run

Owner: the queue owner. Status: done 2026-09-26. Ticket review 1 returned ten findings, review 2 returned nine, and review 3 returned eight and three wording nits. All are taken.

## Why

Ian's standing rule: Beatles Bench runs everything through ThinkThen, and every bench script works against any ThinkThen-compatible server (tickets 0009 and 0011).

A diagnosis on 2026-09-26 found that the function suite breaks the rule for recognize. `scripts/generate/functions.py` never calls `thinkthen recognize`. It asks two `annotate` questions of each word, each over a five-word window. Its docstring says the command "lacks" recognize. `spans()` in `scripts/score/functions.py`, lines 108 to 136, then joins the words into names with its own connector rule and punctuation handling. The shipped command has been settled since thinkthen ticket 0080. It sends the whole sentence as evidence and assembles the names in `crates/thinkthen/src/core/recognize.rs`.

Ticket 0011 said that `functions.py` "calls the function's own command once per record". That was wrong for recognize and relate. This ticket audits every function and fixes each one found.

Ian widened the scope on 2026-09-26. The queue owner relayed it. After the move, the whole bench reruns fresh against Jev: the function suite, the 1,501-question run, and the RAD and open-book runs. Other models are not rerun. Rerunning every model waits for the 0.1 release candidate. The spend stays within this ticket's $1.00 cap. Each job is dry-run first, and the work stops and reports if the total would pass the cap.

## Prior evidence

- `questions/functions/recognize.jsonl` holds 865 cases, one per word of 48 sentences. Each is `annotate recognize.json` over a five-word window. `recognize-sentences.json` holds each sentence's words and its true spans: one song, one person, and one album per sentence, 144 names.
- `questions/functions/relate.jsonl` holds three cases. Each is `annotate relate-0N.json` over a numbered list of 199 entities, in chunks of at most 90,000 bytes. `relate_rows()` makes an edge from each option at 0.5 or more (`T_EDGE`).
- The fresh Jev run of 2026-09-25 (`results/runs/2026-09-25-functions-jev`, ticket 0009) gives recognize song precision 0.194 (7 of 36) and relate edge F1 0.704. Recognize cost 324,612 input tokens over 593 requests. Relate cost 114,779 over 3 requests.
- The Laya run of 2026-09-23 asked the same annotate cases. Its recognize rows are 0 of 94 songs, and the shim refused relate with status 422. Laya runs only on a Mac through a local shim. It cannot run here.
- GLM-5.3 Flash never asked recognize or relate (`scripts/run/chat.py`, `CHAT_TESTS`).
- The function folders already call the shipped commands. `functions/recognize/run` runs `thinkthen recognize person song album place`, and `functions/relate/run` runs `thinkthen relate @relate.json`. Their cases use `"function": "recognize"` and `"function": "relate"`.
- The pinned binary, a local build, has SHA-256 `eb4a571370527ec56c5fe0e10aec410ae906799c05b4de3d9a97ba6eaf48e255`. Every 2026-09-25 `run.txt` names that SHA-256: a release build of thinkthen main at 02dc0b96. So the pinned binary is the build that made every 2026-09-25 recording. The experiment's `RESULTS.md` still names e70bddab. That line predates the binary's replacement at 17:15 that day. The 2026-09-25 ledgers ran a second local build path. That path held the same SHA-256 then. It was replaced at 22:44 that day and now hashes `60712648…`, and its README still names `eb4a5713…`. The matching SHA-256 in each `run.txt` proves the first copy is the build that made the recordings. The second path is not used.
- Recognize on the pinned build (02dc0b96) against thinkthen origin/main 0f255579: `core/recognize.rs` is the same. `engine/facade/recognize.rs` differs by one added `None` argument, so request planning is the same. `cli/recognize/dry_run.rs` differs. The pinned `--dry-run` prints only `tokens`, `detection_questions`, `kind_questions`, and `requests`, for the first record. Main prints `words`, `request_count`, and every request body.
- The tokenizer peels `.`, `!`, `?`, `,`, `:`, and `;` from the end of each word, each as its own token (`split_piece()` in `recognize.rs`, and `specification/recognize.md`, "Names"). A name is one run of `IN` tokens, so a name may keep or drop a peeled mark. Thirteen of the 144 true names end in one of those marks or hold one: `Help!` (six times), `Why Don't We Do It in the Road?`, `Back in the U.S.S.R.`, `Here, There and Everywhere`, and `Sgt. Pepper's Lonely Hearts Club Band` (four times).
- One pinned `recognize song person album --dry-run` per sentence prints one request each, 48 in all, over 878 tokens. To measure bytes, the author sent each sentence from the pinned build to a local listener at 127.0.0.1 with a dummy key. The listener answered status 500. The 48 requests hold 977,190 bytes. The largest holds 30,162. The same capture of the `functions/recognize` example gives 29,227 bytes, and its recording reports 8,092 input tokens: 0.277 tokens a byte. So the suite needs about 270,700 input tokens, and the largest request about 8,400.
- `thinkthen relate` over the suite's 199 entities, with `sung_by=song:person` and `appears_on=song:album`, plans one `choice` question per song for each rule. On the pinned build the dry run prints two requests: 84,568 bytes and 162,649 bytes. The hosted backend refuses a request over 65,536 input tokens, and relate JSON runs about 0.516 tokens a byte (thinkthen `specification/backends.md`). So the second request would be refused.
- thinkthen main differs here. Ticket 0123 added a built-in 96,000-byte ceiling for relation requests at the built-in address. The pinned build has no ceiling. It honours a profile's `max_request_bytes` (`--profile FILE`, `thinkthen.backend-profile/1`). With `max_request_bytes` 96,000, its dry run prints three requests: 84,568, 95,818, and 77,692 bytes, about 133,000 input tokens.
- Ticket 0009 reran every Jev run fresh on 2026-09-25. Its record gives each job's cap and spend: 6,191,593 input tokens in all, examples included.
- A downstream talk deck's what-jev-knows NOTES print the first main measure per function from `results/tables/functions.tsv`. They show recognize song precision 0.19 and relate edge F1 0.70. Other slides quote the front-page, open-book, and RAD numbers. The recognize and relate slides draw from `functions/recognize` and `functions/relate`.

## The audit

"Direct" means the bench scores what the shipped `thinkthen <verb>` prints.

| Function or run | Path | Calls | Finding |
| --- | --- | --- | --- |
| decide | the 1,501-question run, `scripts/run/ask.py` line 57 | `thinkthen decide` | direct |
| choose | the same | `thinkthen choose` | direct |
| tag | suite, `scripts/run/functions.py` line 115 | `thinkthen tag` | direct |
| score | suite | `thinkthen score` | direct |
| filter | suite, `functions.py` lines 115 and 148 to 150 | `thinkthen filter` | direct, note 1 |
| rank | suite, the same lines | `thinkthen rank` | direct, note 1 |
| find | suite | `thinkthen find` | direct |
| annotate | suite | `thinkthen annotate` | direct |
| recognize | suite, `scripts/generate/functions.py` lines 18, 55 to 65, 171 to 197, 244 to 247, and 260 to 261. `scripts/score/functions.py` lines 33 to 34, 108 to 136, and 293 to 320. `scripts/run/chat.py` lines 171 to 175 describe it. | `thinkthen annotate` over five-word windows | **rebuilt**, note 2 |
| relate | suite, `scripts/generate/functions.py` lines 65 to 70 and 199 to 241. `scripts/score/functions.py` lines 34 and 322 to 339. | `thinkthen annotate` with the bench's own numbered list and wording | **rebuilt**, note 3 |
| audit | `functions/audit`, `scripts/score/tune.sh` | `thinkthen audit` | direct |
| diff | `functions/diff`, `scripts/score/context_diff.sh`, `diff_guard.sh` | `thinkthen diff` | direct |
| the ten function folders | `functions/<name>/run` and `scripts/run/example.sh` | each folder's own verb | direct |
| 1,501-question run | `scripts/run/ask.py` | `decide`, `choose` | direct, note 4 |
| open book | `ask.py` with `catalog.txt` | `decide`, `choose` | direct, note 4 |
| RAD | `scripts/run/rad.py`, `thinkthen.sh`, `ask.py`, `rad_pipeline.sh` | `choose`, `tag`, `annotate` | direct, note 5 |
| GLM-5.3 Flash | `scripts/run/chat.py`, lines 42 to 96 and its ask path | GLM's own API through httpx and instructor | not ThinkThen by design, note 6 |
| baselines | `scripts/run/baselines.py`, `relation_vectors.py`, `rad.py rank bm25` and `rank minilm` | no model, or a local embedding model | not ThinkThen by design, note 6 |

1. Each filter or rank record goes through `thinkthen decide`. That call sends the same request. Each list then runs whole through `thinkthen filter` or `rank` with `--replay`. The scorer reads the kept records or the order the shipped command prints. The single-record calls only time each request.
2. The bench builds the verb from annotate and joins the words itself in `spans()`.
3. The bench builds the relation questions itself and makes edges from option probabilities.
4. Python grades the published tables. Ticket 0011 keeps that and checks each cell `audit` can make in `tests/test_audit_contract.py`. In open book, the catalog rides in the text sent, and `open_book.py compare` grades.
5. `rad.py` writes the questions, and `scripts/run/thinkthen.sh` asks them through `ask.py`. The top-K sort of the pick's probabilities sits at `rad.py` lines 92 to 94 and `rad_pipeline.sh` line 65. It is the pipeline's own retrieval step. No shipped verb returns the K likeliest options.
6. They are the comparisons, under ticket 0011's exception.

Two paths are rebuilt: recognize and relate in the function suite. The graders that stay in Python are ticket 0011's decision. They grade only.

## Retained behavior

- The answer key. Each sentence keeps its words, its three true names, their kinds, and the data fields behind them. Each relate question keeps its truth edges, and a song whose lead is not settled still has no `sung_by` truth.
- The measures and their names. `recognize`, `names`, and `song precision` stay first. `relate`, `song to singer and album`, and `edge F1` stay first. The deck finds its cells by these names.
- `questions/*.jsonl`, `questions/keys/`, and the other six function tests' case files stay byte for byte. In `questions/functions/`, only `recognize.jsonl` and `relate.jsonl` change. `recognize.json`, `recognize-sentences.json`, and `relate-01.json` to `relate-03.json` go. `relate-suite.json` and `relate-profile.json` are new.
- Every committed run folder stays as it is, the 2026-09-25 folders included. Code finds the newest run of each label (ticket 0009). The fresh folders then take over. The old folders stay as the record.
- The 2026-09-25 function run no longer replays whole under the new suite. Its six unchanged tests still replay and give their committed rows byte for byte.
- The ten function folders, `functions/<name>/`, are not rerun. They already call the shipped commands, and the deck's slides draw on their recordings. The functions/recognize example does not change.
- GLM-5.3 Flash, Laya, the baselines, relation vectors, and the BM25 and MiniLM ranks stay at their old dates.
- `./run.sh` and its replays stay as they are. No script reads, prints, or passes `THINKTHEN_API_KEY`.

## Changes

1. **Recognize cases.** `scripts/generate/functions.py` writes one case per sentence: `{"id": "recognize-NN", "function": "recognize", "test": "names", "args": ["song", "person", "album", "--jsonl", "--field", "/input"], "records": [{"id": "recognize-NN", "input": TEXT}], "truth": NAMES, "fields": ...}`. `TEXT` is the sentence's words joined by single spaces, as before. Each true name is `[start, end, kind, name]` in Unicode characters, end exclusive, as the command prints offsets. The threshold is the command's default, 0.5. The kinds keep the old test's order, `KINDS`. The function folder adds `place`. The suite leaves it out, because its sentences hold no place and the old test asked three kinds. `DETECT`, `KIND`, the old `RECOGNIZE` question set, `window()`, `recognize.json`, and `recognize-sentences.json` go.
2. **The matching rule.** `scripts/score/functions.py` reads the names from each row's `value.entities`. Before any comparison, the end of every name, said or true, moves left past any of `.!?,:;` that end it. Those are the marks the command's tokenizer peels from a word. A said name then matches a true name when start, end, and kind are equal. A said name made only of a peeled mark trims to nothing. It still counts as said, and it matches no true name. The overlap measures count a said name that shares at least one character with a true name of the same kind. The docstring states the rule and cites thinkthen `specification/recognize.md`. `spans()`, `CONNECTORS`, `T_SPAN`, and `FLIP_BAR` go. Nothing else touches the command's names.
3. **Relate cases.** One case, `relate-songs`, with `"function": "relate"`. Its records are the 199 entities, `{"name", "kind"}`, in the order the old list used. Its args are `@relate-suite.json --profile relate-profile.json --threshold 0.5 --jsonl --timeout 180`. `relate-suite.json` holds the two rules: `sung_by` song to person, reading "has its lead vocal sung by", and `appears_on` song to album, reading "first appeared on the album". Those are the function folder's readings. `relate-suite.json` holds no `threshold`. The folder's `relate.json` sets 0.01, and the case's `--threshold 0.5` pins the command's default. `relate-profile.json` is `{"schema": "thinkthen.backend-profile/1", "name": "request-96000", "max_request_bytes": 96000}`. The case keeps `truth` and adds `skip`: the songs whose `sung_by` edges are not scored. `INTRO`, `RULES`, `CHUNK_BYTES`, and the `relate-0N.json` files go.
4. **Relate scoring.** `relate_rows()` reads the edges the command prints in `value`, at its default threshold of 0.5. An edge is `(relation, source name, target name)`. It drops `sung_by` edges from a skipped song. The bootstrap unit is one relation of one song, as before. `T_EDGE` goes. A row whose `meta.failed_questions` is above 0 stops the table. A part is not scored, as `gap_rows()` already rules for refused cases.
5. **Fresh runs.** The jobs below write fresh folders dated 2026-09-26 from empty recordings. Each folder gets `inputs.sha256`, `run.txt`, and `ledger.txt` as ticket 0009 wrote them. Before the first paid call, the fixed inputs come from the 2026-09-25 folders with the commands in `scripts/README.md`, "Fixed inputs for a fresh run": `ids.txt` and `catalog.txt` for open book, `rank-bm25.tsv` and `rank-minilm.tsv` for RAD, `split.tsv` and `rank-bm25opt.tsv` for RAD2, and `questions.jsonl` and `ids.txt` for one line. `open_book.py pick` then never redraws the 196.
6. **RAD build order.** RAD: `rad.py build RUN` for the picks, then `rad.py rank jev RUN`, then `rad.py build RUN jev:2 bm25:2`, then `rad.py build RUN jev:2 bm25:2 minilm:2 jev:1`. RAD2: `rad.py build RUN --options`, then `rank jev`, then `build RUN --options jev:2 bm25opt:2:held`. The last builds give the 2026-09-25 `questions.jsonl` byte for byte from the 2026-09-25 rank files.
7. **Tests follow the fresh runs.** `tests/published.py` moves `JEV` to 2026-09-26 in the same commit as the tables. `tests/test_audit_contract.py` sets `COVERED_FILES["Jev"]` to the count from the fresh 1,501 answers: the question files where no tie holds the right answer. The record gives the old count, 7, and the new one. `tests/test_score_rad.py` keeps its named 2026-09-23 folders. The Laya suite replay asks its six unchanged tests and compares their rows.
8. **Docs.** The generator and scorer docstrings, the `scripts/run/functions.py` docstring (its line 8 says each case sends one request, and relate sends three), the `chat.py` comment on recognize and relate (lines 171 to 175), `questions/README.md`, and `scripts/README.md` say what the suite now asks. `reports/results.md` drops "`recognize` and `relate` are not in the command". Its line 74 says GLM skips recognize and relate because they are "built from annotate's probabilities". The new reason: the shipped commands read a probability for each token or option, and a chat model states one. It explains Laya's blank recognize and relate cells.

## Tests

- **Matching rule.** One edge-case table test on `trim()` and `overlap()`. Each row gives a true name, a said name, and whether they match exactly and by overlap:
  - `Help!` said as `Help` and as `Help!`: both match
  - `Back in the U.S.S.R.` said as `Back in the U.S.S.R`: match. Said as `Back in the`: overlap only.
  - `Why Don't We Do It in the Road?` said without the `?`: match
  - `Here, There and Everywhere` said as `Here`: overlap only
  - `Sgt. Pepper's Lonely Hearts Club Band` said as `Sgt` and a second name `Pepper's Lonely Hearts Club Band`: each overlap only
  - `Abbey Road` said as `Abbey Road.`, the tokenizer's general case of a mark kept at a name's end: match
  - the right span with the wrong kind: neither
  - a said name of only `!`: neither, and it still counts as said
- **Key.** A generator test checks that each true name's slice of the text equals its name, and that each sentence holds one song, one person, and one album.
- **Relate truth.** `test_relate_truth_edges_come_from_the_data` follows the new case. A test checks that `skip` holds exactly the songs `settled_lead()` rejects.
- **Partial relate.** One case: a relate row with a failed question stops the table.
- **Runner.** The fake command in `tests/fixtures/fake-thinkthen-functions` answers `recognize` and `relate`. `test_every_case_gets_one_timed_output_and_replays` repeats a tag case under a second id for its answered-from-the-recording row.
- **Tables and replays.** The existing tests point at the fresh folders. `TableTest` scores the fresh Jev run, and Laya and GLM as before. `ReplayTest` replays the fresh function run whole. `test_replay_laya.py` replays Laya's six unchanged tests.
- The tests for `spans()` and the gap test on the old relate cases follow the code they tested.

## The run

This is a paid run under Ian's approval for testing everything through ThinkThen. On 2026-09-26 the queue owner relayed Ian's raise of this ticket's cap from $0.25 to $1.00, and then the wider scope.

- **Cap.** The ticket stops at $1.00: 23,809,523 input tokens at $0.042 per million.
- **Dry run.** Before any paid call, each job's requests are checked with no key. The pinned `--dry-run` plans only the first record, so it cannot total a job. So the check replays each 2026-09-25 folder with the pinned build and the current code. A replay answers only a request that matches a recorded one byte for byte. Each replay that passes proves its job sends the same requests, and the 2026-09-25 recording gives its exact tokens. The RAD answers depend on the fresh picks. Their estimate is the 2026-09-25 spend. Recognize and relate are measured above. The work stops before any paid call if a replay fails or the total passes the cap.
- **Order.** The 1,501, open book, one line, RAD, RAD2, the pipeline, then the function suite. RAD reads the fresh open-book folder's catalog and ids. Those equal the old ones.
- **Jobs.** Each runs through thinkthen `sdlc/scripts/live` with `THINKTHEN_BIN` set to the pinned binary and `BENCH_WORKERS=4`. The job first checks the binary's SHA-256. `BENCH_MAX_INPUT_TOKENS` is the cap. The guard's `--max-tokens` is the cap plus 4 times the job's largest request, as ticket 0009 set it.

| Job | Fresh folder under `results/runs/` | Expected input tokens | Largest request | Cap | Guard `--max-tokens` |
| --- | --- | --- | --- | --- | --- |
| The 1,501 | `2026-09-26-thinkthen-jev` | 534,901 | 469 | 600,000 | 601,876 |
| Open book, 196 questions | `2026-09-26-thinkthen-jev-open-book` | 2,394,007 | 12,317 | 2,640,000 | 2,689,268 |
| One line, 38 questions | `2026-09-26-thinkthen-jev-one-line` | 13,171 | 412 | 15,000 | 16,648 |
| RAD picks | `2026-09-26-thinkthen-jev-rad` | 191,308 | 1,140 | 211,000 | 215,560 |
| RAD Jev k=2 and BM25 k=2 answers | same | about 684,000 | 3,122 | 747,000 | 759,488 |
| RAD MiniLM k=2 and Jev k=1 answers | same | about 517,000 | 3,122 | 570,000 | 582,488 |
| RAD2 picks with options | `2026-09-26-thinkthen-jev-rad2` | 226,302 | 1,190 | 249,000 | 253,760 |
| RAD2 answers | same | about 506,000 | 3,117 | 560,000 | 572,468 |
| Pipeline | `2026-09-26-pipeline-jev` | 101,879 | 2,181 | no stop | 136,000 |
| Function suite | `2026-09-26-functions-jev` | about 898,000 | about 49,500 | 1,000,000 | 1,198,000 |
| Total | | about 6,066,000, about $0.255 | | 6,592,000 plus 136,000 | |

The function row adds the six unchanged tests of 2026-09-25 (about 494,000), recognize (about 270,700), and relate (about 133,000). The pipeline has no token stop. Its case list is fixed, so its requests are bounded, as ticket 0009 ruled.

- **Stop.** A job that reaches its cap halts. The ledger records the gap and the owner's decision. Spent tokens come from the recording, as ticket 0009 counted them.
- **Key.** The key comes from the environment. Only the command reads it. No script, log, ledger, `run.txt`, or commit holds it.
- **Gaps.** A refused call is a gap in `gaps.tsv`. A finished run needs an empty `gaps.tsv`. A relate run that exits 6 is not scored. Its failed questions go in the ledger, and the owner decides there whether to resume from `--cache`.

## Downstream

Each file below is regenerated from the fresh folders, or rewritten to quote them:

- `results/tables/` from `analyze.py` and `scripts/score/functions.py table`. `functions-glm.tsv` keeps every value. Code review 1 made the requests column count each call's requests, so its rank date row moves from 182 to 183 requests: one GLM call sent two. `functions-laya.tsv` loses its recognize and relate rows.
- `results/history.tsv` gains 2026-09-26 rows.
- `reports/figures/` from `scripts/figures/all.sh`.
- `README.md` lines 34 to 43: the Jev row of the front table, its time, load, and open-book sentence.
- `reports/results.md` lines 3, 23, 27, 49, 74, and 78, and its tables.
- `reports/open-book.md` and `reports/rad.md`: the "Fresh run of 2026-09-25" sections become "Fresh run of 2026-09-26". Each keeps its 2026-09-23 section.
- `docs/context-and-cost.md` lines 63 to 97 and `docs/the-data.md` lines 65 to 89.
- The record lists every number that moves, old and new. It names each one the downstream talk deck quotes.
- An issue in the deck's own repository lists those moves and the stale GLM sentence for the deck owner. The deck is not edited here.

## Proof

- Before the paid jobs: every 2026-09-25 folder in the job table replays under the pinned build with the current code, with no key. The function folder replays its six unchanged tests. The RAD builds give the 2026-09-25 `questions.jsonl` from its rank files.
- `python3 -m unittest discover -s tests` passes with no key and no network, with and without `THINKTHEN_BIN` set to the pinned binary's path.
- `./run.sh` passes with no key and no address.
- Two replays of each fresh folder with no key give the same bytes, one of them from a fresh clone of the branch. Each replay equals the committed files once `cached` and `requests_sent` are stripped, as ticket 0009 compared them.
- `sha256sum -c inputs.sha256` passes in each fresh folder. Every `run.txt` names the pinned binary's SHA-256.
- Each regenerated table equals the committed one when `analyze.py` and `functions.py table` run again on the fresh folders.
- The generator writes the committed bytes twice.
- A one-off check compares each sentence's text, names, and kinds with `recognize-sentences.json` at an earlier commit, and each relate truth edge and skipped song with the three old cases. The record gives its output.
- `git grep -n -E "spans\(|CONNECTORS|FLIP_BAR|T_EDGE|recognize-sentences|window\(" -- scripts tests questions` prints nothing.
- `git grep -n -i "lacks" -- scripts/generate/functions.py` prints nothing.
- `grep -r -i -l -E "authorization|bearer|api.key|x-api" results/runs/2026-09-26-*` prints nothing. The fresh `ledger.txt` and `run.txt` files are in that search.
- `git status` is clean after the suite.

## Owner's decisions (Ian can overturn each)

- The matching rule trims `.!?,:;` from the end of both names. It follows the command's own tokenizer and favours no model. An exact key that keeps the mark would count `Help` wrong, and a key that drops it would count `Help!` wrong. Either choice would then score the tokenizer. The rule scores the model.
- Relate passes a profile with `max_request_bytes` 96,000. That is the ceiling thinkthen main applies at the built-in address. The pinned build would otherwise send one request of about 84,000 tokens, over the backend's limit. The profile works on any server. A server with no such limit just gets three requests.
- Recognize uses bare kinds in the old order, `song person album`. No kind description is tuned for Jev.
- GLM and the baselines stay outside ThinkThen. They are the comparisons, under ticket 0011's exception.
- The fresh jobs are ticket 0009's jobs with the same build. The ten function folders are not rerun. The deck's slides draw on their recordings, and a rerun would move every slide.
- The open-book, RAD2, and one-line inputs are reused, as ticket 0009 reused them.
- Laya's recognize and relate cells go blank. Its 2026-09-23 run asked the annotate-built tests. Those tests no longer exist. A test with no output for any of its case ids gives no rows (`table()` in `scripts/score/functions.py`), and `TableTest` scores the Laya run to the new `functions-laya.tsv`. Laya cannot run on this machine.

## Deferred

- Rerunning GLM, Laya, and the other models. It waits for the 0.1 release candidate.
- Rerunning the ten function folders.
- Moving the published tables onto `thinkthen audit`. Ticket 0011's issues still hold for the pinned build. thinkthen main has since landed a complete audit (tickets 0125 and 0131). The pinned build predates both.
- Dropping the relate profile once the pinned build carries ticket 0123's ceiling.
- Tickets 0001 and 0013 name a private repository. This ticket does not rewrite them.

## Done when

The proof passes, a fresh reviewer accepts the code, the run stays under its cap, the bench lands on main by fast-forward and is pushed, and the downstream issue is on its repository's main.

## Ticket review 1 (fresh reviewer, 2026-09-26): ten findings, all taken

1. The recognize row names the scorer's `recognize_rows()`, the sentences file writer, and the `chat.py` comment. The RAD row names `thinkthen.sh` and `ask.py`.
2. GLM and the baselines have rows, marked not ThinkThen by design.
3. The pinned build is compared with thinkthen main at 0f255579, dry run included. The counts say how they were measured.
4. The recognize cap comes from measured request bytes and a recorded token rate.
5. Each guard reservation follows ticket 0009's rule.
6. A relate run with failed questions is not scored.
7. A mark-only name counts as said. The edge rows are ones the command can print.
8. The kind order is stated, with why `place` is left out.
9. The builds are named. Review 2 then found that the pinned binary is the build 0009 used.
10. The stale GLM sentence is in the docs change and the downstream issue. The ticket names no private repository. The contrastive sentence is split.

## Ticket review 2 (fresh reviewer, 2026-09-26): nine findings, all taken

1. and 2. The widening edit had dropped every section after Changes. They are back, revised for the wider scope.
3. The job table gives each job's folder, expected tokens, largest request, cap, and guard reservation. It covers the pipeline and the one-line run, the fixed inputs, and the order.
4. The pinned binary's SHA-256 equals the one every 2026-09-25 `run.txt` records. Both run sets use one build, so the diff measures the model alone.
5. The dry run replays each 2026-09-25 folder. A passing replay proves the requests match, and the recording gives the tokens.
6. Retained behavior names the question files that change, the `JEV` move, and the tests that keep their dates. The two-run table is gone.
7. Downstream lists each stale page and table.
8. The key proof covers every fresh folder, ledger, and `run.txt`.
9. The prose is split. The notes sit below the audit table.

## Ticket review 3 (fresh reviewer, 2026-09-26): eight findings and three wording nits, all taken

1. Thirteen true names hold a peelable mark, not nine.
2. The RAD picks and RAD2 picks guards now use the 0009 largest requests, 1,140 and 1,190: 215,560 and 253,760.
3. The caps sum to 6,592,000.
4. The relate case passes `--threshold 0.5`. `relate-suite.json` holds no threshold.
5. `COVERED_FILES["Jev"]` in `tests/test_audit_contract.py` follows the fresh 1,501 answers.
6. A test with no output for its case ids gives no rows. `TableTest` covers the Laya run.
7. The `scripts/run/functions.py` docstring joins Changes 8.
8. The binary history names the second local build path the 2026-09-25 ledgers used.
- Three trailing clauses are split. The `Abbey Road.` row gives the tokenizer's general case. The Proof line names no local path.
