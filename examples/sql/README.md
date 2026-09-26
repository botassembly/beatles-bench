# sql

The sql slide. One SQLite query asks the filter slide's question of twelve songs, with the band `0.3:0.7`. The answer column holds 1, 0, or NULL. The deck holds the SQLite run itself: the table, the query, and all it printed. That run read [`../filter/recording`](../filter/recording/) as its cache and sent no request.

## What the slide shows

`decide` under a band answers yes when the probability is at or above the high side. It answers no when the probability is below the low side. Anything between is not sure, and SQL prints it as NULL. Each probability comes from the cold rows of [`../filter/outputs.jsonl`](../filter/outputs.jsonl).

| Song | Probability | Answer at `0.3:0.7` |
| --- | --- | --- |
| Octopus's Garden | 0.75 | 1 |
| Yellow Submarine | 0.12 | 0 |
| Something | 0.8 | 1 |
| Here Comes the Sun | 0.96 | 1 |
| Yesterday | 0.11 | 0 |
| Come Together | 0.95 | 1 |
| Hey Jude | 0.29 | 0 |
| Penny Lane | 0.43 | NULL |
| A Day in the Life | 0.93 | 1 |
| Her Majesty | 0.9 | 1 |
| Let It Be | 0.27 | 0 |
| Maxwell's Silver Hammer | 0.94 | 1 |

A Day in the Life reads 1, and it is wrong. It first came out on Sgt. Pepper's Lonely Hearts Club Band. Penny Lane reads NULL. The other ten are right by the `first_album` column of [`../../data/songs.tsv`](../../data/songs.tsv).

## The build

[`../filter/run.txt`](../filter/run.txt). The deck names the SQLite version and the thinkthen extension build of its run.

## The check

`tests/test_published_numbers.py` computes each answer from the filter folder's probabilities and checks every row of the table.
