# 0021 Give every function one shape: memory, card and context

Owner: the queue owner. Status: accepted after ticket review 1; its findings are taken below.

## Why

Ian asked on 2026-09-30 for more questions, round numbers, and a consistent shape. The function suite today is uneven: find has 156 sets, relate 47, recognize 200, and the rest between 158 and 353. The reading test from ticket 0020 scores 1.000 on five of eight functions, because each card states the answer outright. A perfect score cannot show a regression. The bench needs a harder reading level that still sets every truth by script.

## Prior evidence

- `reports/results.md`, "By function": memory and reading scores from tickets 0018 to 0020.
- `reports/open-book.md`: with all 306 songs in the text, Jev got 184 of 196 right. Finding the right facts among many is harder than reading one card, and it is the common real use.
- A 95% interval on 100 cases near 70% is about 9 points either side. On 300 cases it is about 5.
- `scripts/generate/make_suite.py` draws the suite from 182 songs: core catalogue, first album by 1970, and a Beatle lead. Today's distinct asks: decide 228, tag 158, score 171, annotate 182, filter 240, rank 353, find 156.

## Retained behavior

- The 1,501 knowledge questions in `questions/*.jsonl`, their keys, and every published run keep their bytes.
- Every truth comes from `data/` by script with a fixed seed. No person or model sets an answer.
- The existing function-suite cases keep their ids and bytes. New cases get new ids, so old recordings still replay.

## Changes

1. **Three levels, one question set.** Each of decide, choose, tag, score, filter, rank, find and annotate gets 300 distinct questions. Every question is asked at `memory` and at `context`, and 100 of them at `card`. The case's `level` field names the level. The same question at every level makes the level comparisons paired.
   - `memory`: the record holds only what the memory test holds today.
   - `card`: the record carries the cards of the songs the truth needs, as in ticket 0020.
   - `context`: the record carries 20 cards in a seeded order: the cards the truth needs, and the rest drawn from the catalog. Filler cards never change the truth. For find, the eight units keep their cards, and the 12 filler songs exclude every song first released on the asked album.
2. **More questions from the table.** Where a function has fewer than 300 distinct asks, add at most one more kind of question built from `songs.tsv` columns. Examples: decide on first album and on year, tag on song traits (a cover, over three minutes, a Lennon–McCartney credit), score on length, annotate with a second card of writers, cover and length, filter and find on more albums and singers. No question repeats within a level. rank counts each ask as one question.
3. **Controls, per function.**
   - decide keeps its equal yes and no.
   - filter keeps its mix of kept and dropped songs.
   - About 15% of choose questions offer "none of these" as the right answer.
   - About 15% of tag questions on traits have an empty truth.
   - About 15% of find sets have no right unit and run with `--none`.
   - score, rank and annotate take no control.
4. **recognize and relate.** recognize grows to 300 name sentences and 100 relation sentences, from the 0018 generators, with level `text`. relate grows to 100 entity sets from the 0019 groups, with level `memory`.
5. **One catalog.** `questions/catalog.jsonl` lists every question in the bench, knowledge and suite alike: id, file, function, test, level, category, and truth. A script writes it, and a test checks it against the question files.
6. `questions/README.md` gives the counts in one table.

## Proof

- `tests/test_suite.py` checks:
  - the count of every function and level
  - that each question appears once per level
  - the control share per function
  - that each context record holds the needed cards and 20 in all, and no filler card makes a second right answer
  - that a rebuild gives the same bytes
- The card-facts test extends to the context level: each needed fact appears in the record exactly once.
- No live call in this ticket.

## Deferred gaps

- Runs and scores come in ticket 0023. The answers table comes in ticket 0022.
- A private copy under another seed lives outside this repo.
