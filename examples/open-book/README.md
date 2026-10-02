# open-book

The open-book slide. On the same `196` questions, Jev answers from memory and then with the song catalog in the text.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| From memory | `68 (35%)` | [`../../reports/open-book.md`](../../reports/open-book.md), "Fresh run of 2026-09-26", row all |
| With the catalog | `184 (94%)` | the same row |

At commit [a6a6be71](https://github.com/botassembly/beatles-bench/tree/a6a6be71), `python3 scripts/score/open_book.py compare results/runs/2026-09-26-thinkthen-jev results/runs/2026-09-26-thinkthen-jev-open-book` printed the row. The sample was drawn mostly from Jev's misses, so the share from memory sits low.

## The build

- From memory: [`run.txt`](https://github.com/botassembly/beatles-bench/blob/a6a6be71/results/runs/2026-09-26-thinkthen-jev/run.txt) of the 2026-09-26 Jev run.
- With the catalog: [`run.txt`](https://github.com/botassembly/beatles-bench/blob/a6a6be71/results/runs/2026-09-26-thinkthen-jev-open-book/run.txt) of the 2026-09-26 open-book run.

## The check

`tests/test_published_numbers.py` runs the compare and checks both values.
