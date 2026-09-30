# 0020 Score every function on reading, beside memory: record

Built on 2026-09-30 on `ticket/0020-reading-scores` from main at 32616683. The one paid job ran through a local spend guard. `THINKTHEN_BIN` was the pinned build `thinkthen-c22512868`, SHA-256 `fbc4ff6a`, of thinkthen main at c22512868.

## Result

- Every card-answerable function has a `reading` test: a seeded sample of at most 100 eligible memory cases with the facts the truth needs written into the record as a short card. decide and choose draw 100 cases each from the main `questions/*.jsonl` files; a case is eligible only when its kind is on the list `READING_KINDS` names and `songs.tsv` covers every fact the truth needs. That leaves out the world-event, pair, and album-date kinds. tag, score, filter, find, and annotate sample their own cases; rank samples 100 of each of its two asks, as `reading-popularity` and `reading-date`.
- The card is the song's `songs.tsv` row as lines: Title, Lead singers, First album, Year, Length, plus Written, Released, or 2024 page views where the case's `needs` say the truth needs them. One card per record — and for a find set, one per unit. The question wording, options, and truth stay as the memory case's; decide and choose cases carry `source`, the id of the memory question they reuse.
- `find` grew from 52 to 156 sets: the same generator adds up to nine more sets per album in test `album-more`, preferring targets the old test did not take. The old run still covers test `album` whole, so its table stays byte-identical, and the merged table's find row scores all 156.
- `score_suite.py` scores a reading test with its memory measure and prints the rows under test `reading`. decide and choose reading cases score with the main run's measures: accuracy at 0.5 with the confusion rows for decide, accuracy with a top-tie share and coverage rows for choose. A test the run did not touch still has no rows; a part-asked test still fails the table.
- `reports/results.md` opens with a By function table — function, cases, the ask, memory, reading — and the suite table below holds the reading rows beside the memory ones. It notes that `thinkthen audit` tunes a cut on labeled cases and `thinkthen diff` compares runs.
- The live run `results/runs/2026-09-30-reading-jev` asked the 1,004 new cases. No gap, no failed question. A replay with the key unset wrote the same bytes, and the ten list replays match too.

## Paid job

| Job | Cap | Input tokens sent | Dollars |
| --- | --- | --- | --- |
| Reading tests and album-more find sets | 6,000,000 | 558,621 | 0.0235 |

- The plan's upper bound before the run was 882,004 input tokens over the 1,004 cases, summed from each case's `--plan` output. The run spent 558,621.
- The guard reported 1,004 calls and $0.0235 of spend (its totals moved 629 → 1,633 calls, $0.0519 → $0.0754). The run returned 83,062 output tokens.

## Numbers that moved

| Function | Memory | Reading |
| --- | --- | --- |
| decide | 0.689 | 1.000 |
| choose | 0.705 | 0.950 |
| tag | 0.291 | 1.000 |
| score | 0.696 | 0.733 |
| filter | 0.639 | 1.000 |
| rank, fame / date | 0.638 / 0.805 | 0.808 / 0.979 |
| find | 0.596 | 1.000 |
| annotate | 0.310 | 1.000 |

The carded facts read almost perfectly. What still costs is ordering and matching: score and rank on 2024 page views keep 0.73–0.81, because a five-point scale and a ranking both need the model to map a number onto a judgment, not just read it. choose's five misses all sit on album-to-song questions, where the right answer needs a match across the five option cards.

## Proof

- `python3 -m unittest tests.test_suite` under the c22512868 build: 35 tests, OK, the old suite replay skipped (its recording binds to build 02dc0b96).
- `python3 -m unittest discover -s tests` with no `THINKTHEN_BIN`: 196 tests, OK, 25 skips.
- `tests.test_published_numbers` pins the By function table's cells to `results/tables/functions.tsv` and the run's outputs.
- A rebuild of `questions/suite/` gives the same bytes; the card test checks every reading case's card carries each fact its `needs` name, and the decide/choose `source` check pins question, options, and truth to the memory question.
- The replay test runs the new recording under the build `run.txt` names and compares `outputs.jsonl` and the ten `lists/` files byte for byte.

## What the build taught us

- A recording's byte-exact replay needs `meta.attempts` stripped: this build prints per-request detail under `--details` on the six judgment verbs, and a cache hit or a replay adds none. The runner drops it with `cached` and `requests_sent`.
- The same recording needs its `thinkthen.sqlite` index to replay: this build packs several records into one request, so a question digest resolves through the index, not a filename. The lock files under `.locks/` are private runtime state and stay out.
- `tag` sends four requests a case under this build and `annotate` six; the Requests column counts those, so the reading rows' request counts sit above their case counts.
- Two live passes over the same run folder spent once: the second found every request in the recording and sent nothing.

## Deferred

- GLM and Laya runs of the reading tests.
- A reading test for relate waits on ticket 0019's relist; recognize has no memory test by nature.
- The By function table is written by hand; `test_published_numbers` pins its cells to the generated tables.

## Reviews

Pending independent review.
