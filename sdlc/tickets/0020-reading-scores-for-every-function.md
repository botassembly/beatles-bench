# 0020 Score every function on reading, beside memory

Owner: the queue owner. Status: ready for review.

## Why

Almost every bench question hands Jev a song title and asks what it remembers. That measures what Jev knows. ThinkThen's intended use is judging text the user supplies, and the one open-book test shows the gap: 35 percent from memory and 94 percent with the catalog in the text. A reader should see, for each function, how well it reads, beside how much it remembers. The results should also be laid out by function.

## Prior evidence

- `reports/open-book.md`: 62 of 196 closed book against 184 to 187 with the 306-song catalog in the text.
- `reports/results.md`, "The function suite": memory scores per function, from 0.29 exact-set tag to 0.81 rank by date.
- `questions/suite/annotate-card.json`: a card layout already exists for annotate.
- Coverage today: choose 1,273, decide 228, rank 353, filter 240, annotate 182, score 171, tag 158, find 52 sets, recognize 48, relate 1.

## Retained behavior

- Every existing question, run, table and published number keeps its bytes. The new scores are new rows.
- Truth still comes from the tables by script.

## Changes

1. For each of decide, choose, tag, score, filter, rank, find and annotate, add a `reading` test. It takes a seeded sample of the eligible memory cases, at most 100 per function, and puts the facts into the record as a short card: title, lead singers, first album, year, length, and page views where the question needs them. A case is eligible when the song table covers every fact its truth needs. A one-song case gets that song's card. A `find` set gets one card per unit. A `choose` case whose options are songs gets one card per option. Cases about world events or pairs outside the Beatles are not eligible. The question stays the same. Popularity questions give the page views, so the reading score measures reading, not guessing.
2. Grow find to about 150 sets in the memory test, from the same generator.
3. Score each reading test with its memory test's measure.
4. Add a "By function" table at the top of `reports/results.md`: function, cases, what it asks, memory score, reading score. recognize has no memory score, because it already reads the supplied text. relate has no reading score, because it judges names from memory; ticket 0019 covers it. The function-suite section below it keeps its detail.
5. Add a short note on audit and diff to the same report: a user tunes the cut on labeled cases with `thinkthen audit`, and compares runs with `thinkthen diff`.

## Proof

- `tests/test_suite.py` checks that each reading case's card holds the fact its truth needs, and that a rebuild gives the same bytes.
- `tests/test_published_numbers.py` checks each new figure in the report against its table.
- The live run records every exchange, and a replay with no key gives the same answers.
- Token cap: 6,000,000 input tokens for this ticket, about $0.25. The plan's upper bound is checked before the run.

## Deferred gaps

- GLM and Laya reading runs.
- A held-out reading set outside this repo.

## What the build taught us

- With the facts on the card, decide, tag, filter, find and annotate sit at 1.000 on their samples and choose at 0.950; only score and rank keep a gap (0.733 and 0.808/0.979), because a scale and an ordering ask for a judgment over numbers, not a lookup. choose's five misses are all album-to-song questions, where the answer needs a match across five cards.
- A recording's byte-exact replay needed `meta.attempts` stripped: this build prints per-request detail under `--details` on the six judgment verbs, and a replay adds none. The runner drops it with `cached` and `requests_sent`.
- The new build packs several records into one request, so a replay resolves a question digest through the recording's `thinkthen.sqlite` index, not a filename. The index must be committed with the request files.
