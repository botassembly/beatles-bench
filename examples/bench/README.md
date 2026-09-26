# bench

The bench slide. It shows six rows of the song table and the bench's size.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| Songs | `306` | the rows of [`../../data/songs.tsv`](../../data/songs.tsv) under its header |
| Albums | `20` | the rows of [`../../data/albums.tsv`](../../data/albums.tsv) under its header |
| Questions | `1,501` | the lines of [`../../questions/*.jsonl`](../../questions/) |

The six rows the slide shows come from `data/songs.tsv` as the deck reads it.

## The build

No model answered these values. `scripts/harvest/harvest.py` writes `data/`, and `scripts/generate/generate.py` writes `questions/`.

## The check

`tests/test_published_numbers.py` counts the rows and the questions.
