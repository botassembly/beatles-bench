# Jev with the catalog in hand

Written 2026-09-23. Model: Jev 1.13.0 from TypeSafe, called through the `thinkthen` command.

## Setup

`scripts/run/catalog.py` writes every song in `data/songs.tsv` as one line under its first album, in release order, with songs first out on a single under "Singles". Each line gives the lead singer, the credited writers, the length, the first release date, and for singles the first album. The catalog holds 306 songs in 30,098 characters. Jev counts it as about 11,850 input tokens. In open-book mode, `scripts/run/ask.py` sends "Catalog:", the catalog, and then "Text:" with the question's own input. The question wording stays the same. The catalog covers 1,075 questions: every Beatles-only question except the event questions and the reversal pairs about producers and subjects. The budget allowed 196 calls. `scripts/score/open_book.py pick` drew 134 of the 342 covered questions Jev missed closed book and 62 of the 733 it got right, each spread over the topics in proportion with a fixed seed. The run lives in `results/archive/runs/2026-09-23-thinkthen-jev-open-book/`, with its catalog, its question list, its recording, and its timing. A replay with no key gives the same answers byte for byte.

## Results

Same 196 questions. A tie at the top counts as wrong here. `python3 scripts/score/open_book.py compare results/archive/runs/2026-09-23-thinkthen-jev results/archive/runs/2026-09-23-thinkthen-jev-open-book` prints this table.

| Topic | n | closed right | open right | misses fixed | hits broken |
| --- | --- | --- | --- | --- | --- |
| first album | 62 | 24 (39%) | 60 (97%) | 36 of 38 | 0 of 24 |
| dates | 56 | 10 (18%) | 55 (98%) | 45 of 46 | 0 of 10 |
| lead singer | 45 | 16 (36%) | 42 (93%) | 27 of 29 | 1 of 16 |
| songwriter | 16 | 5 (31%) | 14 (88%) | 9 of 11 | 0 of 5 |
| song length | 8 | 5 (62%) | 8 (100%) | 3 of 3 | 0 of 5 |
| word traps | 9 | 2 (22%) | 8 (89%) | 6 of 7 | 0 of 2 |
| all | 196 | 62 (32%) | 187 (95%) | 126 of 134 | 1 of 62 |

The sample holds mostly closed-book misses, so the closed-book share here sits far below its 68% on all 1,075 covered questions. Weighting the fixed rate and the kept rate back to the full set puts open-book Jev at about 97% on those 1,075 questions. GLM-5.3 Flash scores 96% on the Beatles-only set from memory.

| Measure | closed book | open book |
| --- | --- | --- |
| median time per call | 0.28 s | 0.54 s |
| 90th percentile time | | 1.22 s |
| median input tokens per call | 362 | 12,214 |
| median top probability, wrong answers | 0.53 (134) | 0.62 (9) |
| median top probability, right answers | 0.79 (62) | 0.99 (187) |

The machine ran at a load average near 400 during the open-book run. Part of the slower time comes from the local load and part from the longer request.

## The nine misses

Only nine questions stayed wrong, and each was read by hand against its catalog line.

| Question | Truth | Jev picked | Cause |
| --- | --- | --- | --- |
| Does Paul McCartney sing a lead vocal on "Day Tripper"? | yes | no (0.62) | Misread. The line says "lead: Lennon, McCartney". |
| Does Paul McCartney sing a lead vocal on "She Loves You"? | yes | no (0.70) | Misread. The line says "lead: Lennon, McCartney". |
| Do two or more Beatles share the lead on "The Ballad of John and Yoko"? | no | yes (0.78) | Misread. The line says "lead: Lennon". The title names two people. This is the one hit the catalog broke. |
| Album Yellow Submarine: which song did it include first? | Hey Bulldog | Yellow Submarine (0.65) | Misread. The word trap survives. The song sits under Revolver. |
| First month of the song "Yellow Submarine" | August 1966 | January 1967 (0.53) | Misread. The line says 1966-08-05. The album of the same name came out in January 1969. |
| First album of "I'll Cry Instead", with "none of these" allowed | none of these | Help! (0.64) | Misread. The song sits under A Hard Day's Night. "Help!" is also a song line. |
| Album Help!: which song did it include first? | It's Only Love | I'll Be Back (0.55) | Misread. "Help!" names both a song and an album. |
| Songwriter Ringo Starr: which song is credited to him? | Flying | Misery (0.51) | Catalog gap. The credit reads "Starkey", his legal surname, and the catalog never links it to Ringo Starr. |
| Songwriter George Harrison: which song is credited to him? | Dig It | Any Time at All (0.35) | Weak label. Dig It carries a four-way credit, and Jev spread its answer over the options. |

Seven of nine misses are misreads, and five of those seven involve a title shared with an album or a person. One is a catalog gap and one is a weak label. Adding "Starkey (Ringo Starr)" to the catalog would close the gap.

## Cost

197 live calls: one probe and 196 questions. They used 2,406,214 input tokens. The 196 question calls also returned 9,823 output tokens. At 0.042 dollars per million input tokens and free output, the run cost 0.101 dollars. The guard reserved 2,485,000 tokens in two jobs. An open-book call costs about 34 times a closed-book call. An open-book pass costs about 0.51 dollars per 1,000 questions.

## One line for Laya

Written 2026-09-24 for ticket 0005. Laya holds 512 tokens per request, too few for the catalog. One song's catalog line fits. This test asks whether a small local model gains from one line the way Jev does.

The questions are the 45 lead-singer questions of the open-book sample, less the 7 that ask which of four songs a member sings alone. Those name four songs. No one line serves them. The other 38 each name one song. Each goes out with that song's line from the open-book catalog as its `context` field. `scripts/run/ask.py` sends it as "Catalog:\n<line>\nText: <input>". The longest request came to 88 tokens of text, question, and options by Laya's own tokenizer, and Laya's shim reported at most 111 input tokens. Every request fit in 512. None was dropped for size. `results/runs/2026-09-24-thinkthen-laya-one-line/build.py` writes the question file and the id list for both runs. A fresh Jev one-line run does not rebuild them. It copies `questions.jsonl` and `ids.txt` from the newest one-line Jev run, with the commands in [scripts/README.md](../scripts/README.md#rerun). `python3 results/runs/2026-09-24-thinkthen-laya-one-line/table.py` prints both tables below from the committed answers. The closed-book rows come from the 2026-09-23 runs of each model on the same questions.

| Model | context | right of 38 | median input tokens |
| --- | --- | --- | --- |
| Laya | none | 15 (39%) | 54 |
| Laya | one line | 27 (71%) | 92 |
| Jev | none | 13 (34%) | 293 |
| Jev | one line | 36 (95%) | 335 |
| Jev | whole catalog | 35 (92%) | 12,145 |

| Model | context | who sings (of 7) | yes/no, truth yes (of 16) | yes/no, truth no (of 15) |
| --- | --- | --- | --- | --- |
| Laya | none | 0 | 1 | 14 |
| Laya | one line | 7 | 16 | 4 |
| Jev | none | 0 | 3 | 10 |
| Jev | one line | 7 | 14 | 15 |

The line helps Laya on the pick-one questions. It names the singer on all 7 with the line and on none without it. On yes-or-no questions the line moves Laya from nearly always no to nearly always yes. Closed book it said no to 29 of 31. With the line it said yes to 27 of 31. Its top probability on the 11 wrong yes answers ran from 0.76 to 0.97. So Laya's rise from 15 to 27 mixes real reading with a change of lean. It fixed 22 of 23 misses and broke 10 of 15 hits. All the broken hits are questions whose answer is no.

Jev reads the line. It fixed 23 of 25 misses and broke none. One line did as well as the whole catalog on these 38 questions. It took 335 input tokens a call against 12,145. Its two misses are yes answers it called no: "She Loves You" with "lead: Lennon, McCartney" asked about Paul McCartney (0.42 yes), and "Boys" with "lead: Starr" asked whether Ringo Starr is its only lead singer (0.48 yes). The sample was drawn mostly from Jev's closed-book misses. Both closed-book rows sit low for that reason.

Laya answered all 38 with no refusal, one call in flight, at a median 0.043 seconds per call through the tunnel. The Laya calls cost nothing. The Jev run made 38 live calls with no probe. They used 13,171 input tokens and returned 1,000 output tokens, about 0.0006 dollars. The guard reserved 30,000 tokens with a stop at 25,000. Both runs replay with no key and no tunnel (`tests/test_replay_laya.py`).

## Fresh run of 2026-09-26

Ticket 0014 asked every Jev run again from an empty recording (`sdlc/records/0014-shipped-recognize-and-relate.md`). Ticket 0009 had done the same on 2026-09-25. The open-book run took the same `ids.txt` and `catalog.txt`, so the 196 questions stay the same. `thinkthen diff` pairs all 196 with the 2026-09-25 run: four answers changed, and two of them lost a right answer. `python3 scripts/score/open_book.py compare results/runs/2026-09-26-thinkthen-jev results/runs/2026-09-26-thinkthen-jev-open-book` prints:

| Topic | n | closed right | open right | misses fixed | hits broken |
| --- | --- | --- | --- | --- | --- |
| first album | 62 | 26 (42%) | 60 (97%) | 34 of 36 | 0 of 26 |
| dates | 56 | 10 (18%) | 55 (98%) | 45 of 46 | 0 of 10 |
| lead singer | 45 | 18 (40%) | 40 (89%) | 23 of 27 | 1 of 18 |
| songwriter | 16 | 7 (44%) | 13 (81%) | 6 of 9 | 0 of 7 |
| song length | 8 | 5 (62%) | 8 (100%) | 3 of 3 | 0 of 5 |
| word traps | 9 | 2 (22%) | 8 (89%) | 6 of 7 | 0 of 2 |
| all | 196 | 68 (35%) | 184 (94%) | 117 of 128 | 1 of 68 |

Open book moved from 186 on 2026-09-25 to 184. Closed book moved from 76 to 68 on these 196. The open-book run sent 2,394,007 input tokens, the same as before, about 0.10 dollars. Its median time was 0.28 s per call. The fresh one-line Jev run got 37 of 38 right, the same as on 2026-09-25, with no answer changed. It sent 13,171 input tokens.

## Context and cost

From memory, Jev gets about two in three Beatles questions right. Put the facts in the text, and it reads them. This section shows what one catalog entry fixes in the function examples and what each kind of context costs in input tokens. The section "Fresh run of 2026-09-26" above shows what the whole catalog fixes.

Run every command in this section from the top folder of the bench. None of them sends a request.

### What the catalog entry is

Each context run sends a song's catalog entry, and then its title. The entry comes from the song's row in `data/songs.tsv`. [data/README.md](../data/README.md) shows the row behind the entry:

```sh
jq -r '.records[0].input' examples/annotate/annotate-context.jsonl | tail -4
```

```text
Catalog:
Abbey Road (1969-09-26)
Octopus's Garden (lead: Starr; written: Starkey; 2:51; released 1969-09-26; first album: Abbey Road)
Text: Octopus's Garden
```

The question opens "The text gives a catalog entry and then names a song by the Beatles." The rest of it stays the same.

### What the entry fixes in the examples

Seven examples ask the same cases twice, cold and with the entry. [`scripts/score/context.jq`](../scripts/score/context.jq) marks each answer against its case's `truth` and adds up the input tokens of each side:

```sh
for ex in decide choose score filter find annotate audit; do
  cat examples/$ex/*-cold.jsonl examples/$ex/*-context.jsonl |
    jq -sc --arg ex "$ex" --slurpfile out "examples/$ex/outputs.jsonl" -f scripts/score/context.jq
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

With the entry, every answer is right in every example. The misses it fixes are these:

- [decide](../examples/decide/): A Day in the Life, sure it is on Abbey Road from memory.
- [choose](../examples/choose/): She Loves You, split between John, Paul, and the duet.
- [score](../examples/score/): Revolution 9 and A Day in the Life, a level off.
- [filter](../examples/filter/): A Day in the Life again.
- [annotate](../examples/annotate/): the album and year of Octopus's Garden, left not sure.
- [audit](../examples/audit/) and [diff](../examples/diff/): 20 wrong yeses of 70.

An annotate field counts as right only when it is filled and right. A score counts as right when its likeliest level names the whole minute nearest the real length. The `find` pick was right both times. With the entry it grew surer.

One entry adds tens of input tokens to each question. In the audit example, 70 questions went from 19,543 input tokens to 24,871.

### What it costs

The whole catalog is large. Each open-book question carries it, so each costs far more. This command adds up the input tokens of each run from `results/answers.jsonl`. It prices them at Jev's 0.042 dollars per million input tokens, from `results/tables/cost.tsv`:

```sh
for run in 2026-09-26-thinkthen-jev 2026-09-26-thinkthen-jev-open-book; do
  jq -sc --arg run "$run" 'map(select(.run == $run)) | (map(.input_tokens) | add) as $t
    | {run: $run, answers: length, input_tokens: $t, tokens_per_answer: ($t / length | round),
       dollars_per_1000_answers: ($t / length * 0.042 | round / 1000)}' results/answers.jsonl
done
```

```json
{"run":"2026-09-26-thinkthen-jev","answers":1501,"input_tokens":534901,"tokens_per_answer":356,"dollars_per_1000_answers":0.015}
{"run":"2026-09-26-thinkthen-jev-open-book","answers":196,"input_tokens":2394007,"tokens_per_answer":12214,"dollars_per_1000_answers":0.513}
```

From memory, 1,000 answers cost about 0.015 dollars. With the whole catalog, they cost about 0.513 dollars. The catalog costs more than 30 times the tokens, and it moves the right answers from 68 to 184 of these 196.

Two ways cut that cost:

- **Send only the entry you need.** The worked examples send one song's entry, tens of tokens. That works when you know which song the question is about.
- **Let Jev pick the sections.** [rad.md](rad.md) has Jev choose which parts of the catalog to read, then answer from those parts alone.

### What this section leaves out

- **The cache.** `--cache DIR` answers a repeated request from disk, so a repeat sends nothing. No example here shows it, because a cache hit needs a live first call.
- **relate with the catalog.** The whole catalog beside a set of names passes Jev's input limit.
