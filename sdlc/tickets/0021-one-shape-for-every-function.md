# 0021 Give every function one shape: memory, card and context

Owner: the queue owner. Status: ready for review.

## Why

Ian asked on 2026-09-30 for more questions, round numbers, and a consistent shape. The function suite today is uneven: find has 156 sets, relate 47, recognize 200, and the rest between 158 and 353. The reading test from ticket 0020 scores 1.000 on six of eight functions, because each card states the answer outright. A perfect score cannot show a regression. The bench needs a harder reading level that still sets every truth by script.

## Prior evidence

- `reports/results.md`, "By function": memory and reading scores from tickets 0018 to 0020.
- `reports/open-book.md`: with all 306 songs in the text, Jev got 184 of 196 right. Finding the right facts among many is harder than reading one card, and it is the common real use.
- A 95% interval on 100 cases near 70% is about 9 points either side. On 300 cases it is about 5.
- `scripts/generate/make_suite.py` holds every function's generator, the card builder from 0020, and the recognize and relate groups from 0018 and 0019.

## Retained behavior

- The 1,501 knowledge questions in `questions/*.jsonl`, their keys, and every published run keep their bytes.
- Every truth comes from `data/` by script with a fixed seed. No person or model sets an answer.
- The existing function-suite cases keep their ids and bytes. New cases get new ids, so old recordings still replay.

## Changes

1. Each of decide, choose, tag, score, filter, rank, find and annotate gets three levels, each named in the case's `level` field:
   - `memory`: 300 cases. The record holds only what the memory test holds today. Existing memory cases count toward the 300.
   - `card`: 100 cases. The record carries the named songs' cards, as in ticket 0020. The existing reading cases become this level.
   - `context`: 300 cases. The record carries the cards of 20 songs, in a seeded order: the songs the truth needs, and the rest drawn from the catalog. The question names the song, so the model must find its card and read it. For find, the eight units keep their cards and 12 more songs join as context.
   rank counts each of its two asks as half of each level. decide and choose draw from the main question files, as in ticket 0020, and keep the same eligibility rules.
2. About 15% of each level are controls, where the right answer is no, none, or the empty set, as the function allows.
3. recognize grows to 300 name sentences and 100 relation sentences, from the 0018 generators and groups. relate grows to 100 entity sets, from the 0019 groups.
4. `questions/catalog.jsonl` lists every question in the bench, knowledge and suite alike: id, file, function, test, level, category, and truth. A script writes it, and a test checks that it matches the question files.
5. `questions/README.md` gives the counts in one table.

## Proof

- `tests/test_suite.py` checks the count of every function and level, the control share, that each context record holds the needed cards and 20 in all, and that a rebuild gives the same bytes.
- A card-facts test extends to the context level: each needed fact appears in the record exactly once.
- No live call in this ticket.

## Deferred gaps

- Runs and scores come in ticket 0023. The answers store comes in ticket 0022.
- A private copy under another seed lives outside this repo.
