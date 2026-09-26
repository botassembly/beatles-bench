# Context and cost

From memory, Jev gets about two in three Beatles questions right. Put the facts in the text, and it reads them. This page shows what the catalog entry fixes in the worked examples, what the whole catalog fixes across the bench, and what each costs in input tokens.

Run every command here from the top folder of the bench. None of them sends a request.

## What the catalog entry is

Each context run sends a song's catalog entry, and then its title. The entry comes from the song's row in `data/songs.tsv`. [The data](the-data.md) shows the row behind the entry:

```sh
jq -r '.records[0].input' functions/annotate/annotate-context.jsonl | tail -4
```

```text
Catalog:
Abbey Road (1969-09-26)
Octopus's Garden (lead: Starr; written: Starkey; 2:51; released 1969-09-26; first album: Abbey Road)
Text: Octopus's Garden
```

The question opens "The text gives a catalog entry and then names a song by the Beatles." The rest of it stays the same.

## What the entry fixes in the examples

Seven examples ask the same cases twice, cold and with the entry. [`docs/context.jq`](context.jq) marks each answer against its case's `truth` and adds up the input tokens of each side:

```sh
for ex in decide choose score filter find annotate audit; do
  cat functions/$ex/*-cold.jsonl functions/$ex/*-context.jsonl |
    jq -sc --arg ex "$ex" --slurpfile out "functions/$ex/outputs.jsonl" -f docs/context.jq
done
```

```json
{"example":"decide","cold":{"right":5,"of":6,"input_tokens":1729},"context":{"right":6,"of":6,"input_tokens":2101}}
{"example":"choose","cold":{"right":4,"of":5,"input_tokens":1632},"context":{"right":5,"of":5,"input_tokens":1929}}
{"example":"score","cold":{"right":6,"of":8,"input_tokens":3063},"context":{"right":8,"of":8,"input_tokens":3567}}
{"example":"filter","cold":{"right":11,"of":12,"input_tokens":3469},"context":{"right":12,"of":12,"input_tokens":4214}}
{"example":"find","cold":{"right":1,"of":1,"input_tokens":537},"context":{"right":1,"of":1,"input_tokens":1179}}
{"example":"annotate","cold":{"right":4,"of":6,"input_tokens":1158},"context":{"right":6,"of":6,"input_tokens":1303}}
{"example":"audit","cold":{"right":50,"of":70,"input_tokens":19543},"context":{"right":70,"of":70,"input_tokens":24871}}
```

With the entry, every answer is right in every example. The misses it fixes are the ones each page traces:

- [decide](walkthroughs/decide.md): A Day in the Life, sure it is on Abbey Road from memory.
- [choose](walkthroughs/choose.md): She Loves You, split between John, Paul, and the duet.
- [score](walkthroughs/score.md): Revolution 9 and A Day in the Life, a level off.
- [filter](walkthroughs/filter.md): A Day in the Life again.
- [annotate](walkthroughs/annotate.md): the album and year of Octopus's Garden, left not sure.
- [audit](walkthroughs/audit.md) and [diff](walkthroughs/diff.md): 20 wrong yeses of 70.

An annotate field counts as right only when it is filled and right. A score counts as right when its likeliest level names the whole minute nearest the real length. The `find` pick was right both times. With the entry it grew surer.

One entry adds tens of input tokens to each question. In the audit example, 70 questions went from 19,543 input tokens to 24,871.

## What the whole catalog fixes

The open-book run hands Jev the whole catalog of 306 songs before each question. It asks 196 bench questions, drawn mostly from the questions Jev missed from memory on 2026-09-23. This command compares the fresh closed-book answers with the fresh open-book answers on those 196:

```sh
python3 scripts/score/open_book.py compare results/runs/2026-09-26-thinkthen-jev results/runs/2026-09-26-thinkthen-jev-open-book
```

```text
| Topic | n | closed right | open right | misses fixed | hits broken |
| --- | --- | --- | --- | --- | --- |
| first album | 62 | 26 (42%) | 60 (97%) | 34 of 36 | 0 of 26 |
| dates | 56 | 10 (18%) | 55 (98%) | 45 of 46 | 0 of 10 |
| lead singer | 45 | 18 (40%) | 40 (89%) | 23 of 27 | 1 of 18 |
| songwriter | 16 | 7 (44%) | 13 (81%) | 6 of 9 | 0 of 7 |
| song length | 8 | 5 (62%) | 8 (100%) | 3 of 3 | 0 of 5 |
| word traps | 9 | 2 (22%) | 8 (89%) | 6 of 7 | 0 of 2 |
| all | 196 | 68 (35%) | 184 (94%) | 117 of 128 | 1 of 68 |

closed: median 0.220 s per call, median 362 input tokens, 71059 input tokens in all, median top probability 0.53 on wrong (128) and 0.76 on right (68)
open: median 0.277 s per call, median 12214 input tokens, 2394007 input tokens in all, median top probability 0.56 on wrong (12) and 0.99 on right (184)
```

From memory, Jev gets 68 of the 196 right on 2026-09-26. With the catalog in hand, it gets 184. It fixes 117 misses and breaks 1 right answer. [reports/open-book.md](../reports/open-book.md) has the full report and the older run.

## What it costs

The whole catalog is large. Each open-book question carries it, so each costs far more. This command adds up the input tokens of each run. It prices them at Jev's 0.042 dollars per million input tokens, from `results/tables/cost.tsv`:

```sh
for run in 2026-09-26-thinkthen-jev 2026-09-26-thinkthen-jev-open-book; do
  jq -sc --arg run "$run" '(map(.input_tokens) | add) as $t
    | {run: $run, answers: length, input_tokens: $t, tokens_per_answer: ($t / length | round),
       dollars_per_1000_answers: ($t / length * 0.042 | round / 1000)}' "results/runs/$run/answers.jsonl"
done
```

```json
{"run":"2026-09-26-thinkthen-jev","answers":1501,"input_tokens":534901,"tokens_per_answer":356,"dollars_per_1000_answers":0.015}
{"run":"2026-09-26-thinkthen-jev-open-book","answers":196,"input_tokens":2394007,"tokens_per_answer":12214,"dollars_per_1000_answers":0.513}
```

From memory, 1,000 answers cost about 0.015 dollars. With the whole catalog, they cost about 0.513 dollars. The catalog costs more than 30 times the tokens, and it moves the right answers from 68 to 184 of these 196.

Two ways cut that cost:

- **Send only the entry you need.** The worked examples send one song's entry, tens of tokens. That works when you know which song the question is about.
- **Let Jev pick the sections.** [reports/rad.md](../reports/rad.md) has Jev choose which parts of the catalog to read, then answer from those parts alone.

## What this page leaves out

- **The cache.** `--cache DIR` answers a repeated request from disk, so a repeat sends nothing. No example here shows it, because a cache hit needs a live first call.
- **A whole article.** [Context from a Wikipedia article](context-article.md) hands Jev a whole Wikipedia article. Its runs keep no recording, because a recording would store Wikipedia text. It does not replay, and this page draws no number from it.
- **relate with the catalog.** The whole catalog beside a set of names passes Jev's input limit. [The relate page](walkthroughs/relate.md) says more.
