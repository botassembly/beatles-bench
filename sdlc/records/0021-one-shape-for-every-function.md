# 0021 One shape for every function: record

Built on 2026-10-01 on `ticket/0021-one-shape`. Generation and tests only; no live call was made and no ThinkThen command ran.

## Result

Every suite case carries a `level`, and the eight card-answerable functions share one shape: each distinct question is asked at `memory` and at `context`, and 100 of them at `card`.

- `memory` keeps today's records. Committed cases keep their ids and bytes; the only new keys on an old case are `level`, and `source` on a card case.
- `card` is the ticket-0020 reading case, kept whole: the input text, then one short card per song it names.
- `context` is new: the input text, then 20 cards in a seeded order — the cards the truth needs plus truth-safe fillers from the catalogue. For find, the eight units keep their cards and 12 fillers join them; for an album set no filler was first released on the asked album, and for a singer set no filler has the named Beatle on lead. Context cases carry `source` (the memory question they twin) and `songs` (the titles their cards must hold).
- One new ask kind per function that had fewer than 300, each a small generator of its own: tag `traits` (a cover, runs over four minutes, a Lennon–McCartney credit), score `length` (a five-level scale), filter `album-more` (two more albums), find `singer` (the unit with a named Beatle on lead), annotate `details` (writers, cover and length, `annotate-details.json`), decide `album` (did the song first appear on this album). choose needed none: its 300 questions are main-bench chooses.
- decide and choose memory asks stay in `questions/*.jsonl`: decide's 300 are its 168 card-answerable mains plus the 132 album asks; choose's are a seeded 300 of its eligible mains.
- recognize grows to 400 sentences — 300 name sentences and 100 relation sentences — at level `text`; relate grows to 100 entity sets at level `memory`.
- `questions/catalog/catalog.jsonl` lists all 7,392 questions — the 1,501 mains and every suite case — as `{id, file, function, test, level, category, truth}`. The generator writes it; `tests/test_suite.py` checks it against the files row for row.

## Counts

| function | memory | card | context | text | cases |
| --- | --- | --- | --- | --- | --- |
| decide | 132 + 168 mains | 100 | 300 | — | 532 |
| choose | 300 mains | 100 | 300 | — | 400 |
| tag | 300 | 100 | 300 | — | 700 |
| score | 300 | 100 | 300 | — | 700 |
| filter | 300 | 100 | 300 | — | 700 |
| rank | 353 | 200 | 353 | — | 906 |
| find | 300 | 100 | 300 | — | 700 |
| annotate | 300 | 100 | 300 | — | 700 |
| recognize | — | — | — | 400 | 400 |
| relate | 100 | — | — | — | 100 |

rank keeps all 353 of its asks — 171 by fame, 182 by date — see below. Its card level stays two tests of 100, so 200.

## Controls

- decide: 150 yes / 150 no over its 300 questions.
- filter: the kept share stays the groups' 8-in-30 — 80 kept of 300.
- choose: 30 of 300 have `none` right — 10%, all the eligible pool holds; the mains hold only 30 `none of these` answers.
- tag traits: 21 of 142 have an empty truth — 14.8%.
- find: 45 of 300 sets have no right unit and run with `--none` — 15%.
- score, rank, annotate take no control.

## Proof

- `python3 -m unittest tests.test_suite` with no `THINKTHEN_BIN`: 45 tests, OK, 4 skips (replays that bind to a recorded build).
- `python3 -m unittest discover -s tests` with no `THINKTHEN_BIN`: 208 tests, OK, 26 skips.
- Rebuild check: `python3 scripts/generate/make_suite.py data OUT` twice into fresh folders, `diff -r` clean — identical bytes, catalog included.
- New tests pin the counts per function and level, the memory/card/context pairing by `source`, the control shares, the 20-card context records, each needed card exactly once, and the catalog row for row against the question files. The find check now reads truth from `data/`: an album set's only matching unit is the truth, and a `--none` set holds none.
- Largest context record: 3,374 bytes — `annotate-context-242`'s one record (the input text and 20 cards). Largest context case: `find-context-162`, 5,082 bytes (20 records).

## What the build taught us

- rank cannot shrink to 300 while the committed tables stand. The 2026-09-26 run recorded each rank kind as one ordered list of all its units — 182 song units under `rank-date` — and `score_suite.py`'s `rank_rows` asserts the list equals the test's truths exactly. Dropping 53 date asks would orphan recorded units, and `scripts/score/` is out of scope. rank therefore keeps 353 questions, paired at every level; reaching 300 needs the ticket-0023 republish.
- The catalog could not sit at `questions/catalog.jsonl`: `questions/*.jsonl` globs in `scripts/score`, `scripts/run`, and several tests would read catalog rows as questions. It lives at `questions/catalog/catalog.jsonl`, a subfolder no glob touches — the same trick `questions/keys/` already uses. Ticket 0022 reads that path.
- New memory cases must be generated only after `reading()`: the seeded card draws sample the memory pools, so growing a pool first would change which cases the 100 committed card cases pair with. `main()` runs `reading()` before `more()`.
- choose could not reach 15% none-of-these: the card-answerable pool holds 30 such questions in all, so the control share is 10% — every one of them is in the 300.
- `find`'s singer kind needed `--none` in args so a no-right-unit set can answer `none`; the context twin inherits both the flag and the truth.
- Tests that iterate a whole file must scope by `test`: `truth["singer"]` exists only on annotate's first kind, and a find `key` of `john` is a singer set, not an album.

## Deferred

- rank at 353 questions rather than 300 — see above; the 53 extra date asks go when the run tables are republished (ticket 0023) or a parent rules otherwise.
- `score_suite.py` knows only the old test names; the new kinds and the `-context` tests produce no rows until ticket 0023 runs and scores them.
- choose's none-of-these share is 10%, not 15% — the data hold no more.
- GLM and Laya have no card or context runs.

## Review

Independent review pending.
