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

1. For each of decide, choose, tag, score, filter, rank, find and annotate, add a `reading` test. It takes a seeded sample of the memory cases, at most 100 per function, and puts the song's own row into the record as a short card: title, lead singers, first album, year, length, and page views where the question needs them. The question stays the same. Popularity questions give the page views, so the reading score measures reading, not guessing.
2. Grow find to about 150 sets and tag to about 150 cases in the memory test, from the same generators.
3. Score each reading test with its memory test's measure.
4. Add a "By function" table at the top of `reports/results.md`: function, cases, what it asks, memory score, reading score. The function-suite section below it keeps its detail.
5. Add a short note on audit and diff to the same report: a user tunes the cut on labeled cases with `thinkthen audit`, and compares runs with `thinkthen diff`.

## Proof

- `tests/test_suite.py` checks that each reading case's card holds the fact its truth needs, and that a rebuild gives the same bytes.
- `tests/test_published_numbers.py` checks each new figure in the report against its table.
- The live run records every exchange, and a replay with no key gives the same answers.
- Token cap: 6,000,000 input tokens for this ticket, about $0.25. The plan's upper bound is checked before the run.

## Deferred gaps

- GLM and Laya reading runs.
- A private held-out reading set, which lives in the release QA suite.
