# 0014 Score recognize and relate from the shipped commands: record

Built on 2026-09-26 on `ticket/0014-shipped-recognize-and-relate` from main at 716360eb. Every paid call ran on the local Linux machine through thinkthen's `sdlc/scripts/live` guard. `THINKTHEN_BIN` was `experiments/259-talk-claims/thinkthen`, SHA-256 `eb4a5713`, a release build of thinkthen main at 02dc0b96.

## Result

- The audit in the ticket stands. Of the twelve functions and four runs, only the suite's recognize and relate were rebuilt from `annotate`. Both now call the shipped command.
- recognize asks `thinkthen recognize song person album --jsonl --field /input` once per sentence, 48 cases. Its truth holds each name as character offsets, end exclusive, as the command prints them.
- relate asks `thinkthen relate @relate-suite.json --profile relate-profile.json --threshold 0.5` once over 199 entities. The profile caps each request at 96,000 bytes, so the call sends three requests. The fresh call reported no failed question.
- The matching rule trims `.`, `!`, `?`, `,`, `:`, and `;` from the end of both names, and nothing else. The scorer's docstring cites thinkthen `specification/recognize.md`. An edge-case table in `tests/test_functions.py` covers `Help!`, `Back in the U.S.S.R.`, `Why Don't We Do It in the Road?`, `Here, There and Everywhere`, `Sgt. Pepper's Lonely Hearts Club Band`, `Abbey Road.`, a wrong kind, and a name of only `!`.
- `overlap()` now counts an empty name as sharing no character.
- The shipped recognize in the pinned build matches thinkthen main 0f255579 in `core/recognize.rs`. Only its dry-run output differs. The pinned build lacks main's 96,000-byte relation ceiling, so the case passes the same ceiling as a profile. No ThinkThen defect turned up.
- Laya's recognize and relate rows left `functions-laya.tsv`. GLM's table keeps every value. Its rank date row now counts 183 requests, because one call sent two.

## Paid jobs

`--max-tokens` is the cap plus 4 times the job's largest request, as in ticket 0009. Input tokens are summed from the fresh recordings, at 0.042 dollars per million.

| Job | Cap | Input tokens sent | Dollars |
| --- | --- | --- | --- |
| The 1,501, two attempts | 600,000 | 534,901 | 0.0225 |
| Open book, 196 questions | 2,640,000 | 2,394,007 | 0.1005 |
| One line, 38 questions | 15,000 | 13,171 | 0.0006 |
| RAD picks | 211,000 | 191,308 | 0.0080 |
| RAD Jev k=2 and BM25 k=2 answers | 747,000 | 677,235 | 0.0284 |
| RAD MiniLM k=2 and Jev k=1 answers | 570,000 | 521,415 | 0.0219 |
| RAD2 picks with options | 249,000 | 226,302 | 0.0095 |
| RAD2 answers | 560,000 | 503,136 | 0.0211 |
| Pipeline | no stop, 136,000 reserved | 101,879 | 0.0043 |
| Function suite, two attempts | 1,000,000 | 894,429 | 0.0376 |
| Total | 6,592,000 | 6,057,783 | 0.2544 |

- The runs returned 473,126 output tokens. Jev's output is free.
- No job reached its cap. The total stayed under the 1 dollar ceiling.
- Two jobs stopped on a backend timeout (exit 4) and resumed into the same folder with the cap less the tokens spent. The 1,501 stopped at `forward-songwriter-011` after 121,782 tokens. The function suite stopped at `filter-singer-4-13` after 295,138 tokens. Each timed-out request may have been billed without a recording. A 1,501 request holds at most 469 tokens, and a filter request at most 308.
- The guard charged 8,408,512 tokens of reservations (439,236,779 to 447,645,291).
- No fresh folder has a `gaps.tsv`. Every response names model `jev-1.13.0`. No fresh file holds the key. Recordings hold `adapter`, `request`, `response`, `schema`, and `url`, and no header.
- Before the paid jobs, a dry run measured recognize's request size. The pinned build sent the 48 sentences to a local listener with a dummy key. The first listener port, 8799, belonged to another local process. It received 48 requests with the dummy key and answered them. The real key was never used. The capture ran again on a free port.

## Numbers that moved

Old is the 2026-09-25 run of ticket 0009. New is the 2026-09-26 run.

- Front page, Jev from memory: Beatles-only 68.0% to 67.0%, overall 71.2% to 70.2%, median time 0.32 s to 0.21 s. Dollars per 1,000 stay 0.015. `thinkthen diff` pairs all 1,501: 90 answers changed, 19 gained and 31 lost a right answer, McNemar p = 0.12.
- Function table, Jev: decide 0.693 to 0.689, choose 0.715 to 0.705, tag 0.272 to 0.291, score 0.683 to 0.696, filter 0.644 to 0.639, rank popularity 0.636 to 0.638, rank date 0.811 to 0.805, annotate singer 0.304 to 0.310, album 0.571 to 0.582, year 0.390 to 0.407. find stays 0.654.
- recognize, from the shipped command: song precision 0.194 to 0.959, song recall 0.146 to 0.979, person precision 0.960 to 1.000, person recall stays 1.000, album precision 0.359 to 1.000, album recall 0.292 to 0.979. Jev missed two of 144 names. It split "Back in the U.S.S.R." in two, and it did not name the album "Help!".
- relate, from the shipped command: edge F1 0.704 to 0.719, precision 0.864 to 0.867, recall 0.594 to 0.614.
- `reports/results.md`: McNemar against embeddings 488 and 95 to 484 and 103, GLM against Jev 398 and 22 to 410 and 22, Jev against Laya 521 and 94 to 514 and 99. Jev's calibration error 0.023 to 0.026. Popularity 51% and 74% to 49% and 73%. Multi-hop 25 of 60 to 22 of 60, and 22 of 46 to 18 of 41. Lexical-trap controls 67% and 48% to 70% and 50%, p = 0.013 to 0.003. Near neighbors 73% and 83% to 75% and 80%, p = 0.21 to 0.63.
- Open book: 186 to 184 of 196 with the catalog, and 76 to 68 from memory. Four answers changed. Median time 0.42 s to 0.28 s. One line stays 37 of 38 with no answer changed.
- RAD: Jev picks k = 2 moved from 172 to 170. The fallback row stays 182. Closed book 76 to 68. 70 of 980 answers changed.
- RAD2: 31 of 490 answers changed. The tune half chose 0.35 and 0.40, against 0.35 and 0.35. The McNemar test of the new pick with its fallback against the full catalog moved from 0 and 9, p = 0.004, to 3 and 7, p = 0.34. It no longer shows a difference.
- Pipeline: every score and check stays. Jev's memory answer for The End moved from McCartney and Starr to Lennon, McCartney, and Starr. Both are wrong.
- `COVERED_FILES["Jev"]` in `tests/test_audit_contract.py` stays 7.

## Proof

- `python3 -m unittest discover -s tests` with the pinned build and no key: 176 tests, OK, 3 skipped. The skips are the chat backend's missing module, the local `data/raw/` cache, and `test_run_sh` while results were uncommitted.
- `./run.sh` with no address and no key replayed `results/runs/2026-09-26-thinkthen-jev` and all twelve function folders. Every file matched.
- A fresh clone of the branch replayed each 2026-09-26 folder with no key. `answers.jsonl` matched in the 1,501, open-book, one-line, RAD, and RAD2 folders. The function run's `outputs.jsonl` and `lists/` matched. The pipeline's `scores.tsv` and `checks.tsv` matched. Its per-call `.jsonl` files matched once `cached` and `requests_sent` were stripped, as ticket 0009 compared them.
- A second replay in the worktree gave the same bytes as the clone in every folder. The pipeline's replay `times.tsv` differs, because it times the replay itself.
- `functions.py table` on the replayed function run gives the committed `functions.tsv` byte for byte.
- `sha256sum -c inputs.sha256` passes in each fresh folder. Every `run.txt` names the pinned SHA-256.

## Code review 1 (fresh reviewer): five findings and a nit, all taken

1. The generator docstring no longer names the old `word` and `map` fields. It says every case but relate sends one request, and that `skip` lists songs.
2. The requests column counts each call's distinct `meta.requests`. The relate row now shows 3 requests, and its 2026-09-26 history row shows 1.77601 dollars per 1,000 requests, against 5.32804 per call. GLM's rank date row moves from 182 to 183 requests, because one GLM call sent two. No GLM value moved.
3. The two resumed ledgers carry `#` lines for the cause, the possible unrecorded spend, and the decision to resume.
4. The open-book and RAD reports point at this record.
5. `recognize_rows()` stops on a failed question, as `relate_rows()` does. One test covers both.
- The `chat.py` comment and the runner docstring are rewrapped.

## Code review 2 (fresh reviewer): two text findings, both taken

1. The Result section no longer says GLM's table did not change.
2. The two ledger notes drop a contrastive appositive.

## The deck

A downstream talk deck quotes some of these numbers. Its owner has an issue in the deck's repository listing each move. The deck was not edited here.
