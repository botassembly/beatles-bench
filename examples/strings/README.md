# strings

The strings slide. Code sees three strings. A person sees an album, a song on it, and the drummer who sings it. The slide's reminder gives the share a random guess and vector search get on the Beatles questions.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| Ringo sings Octopus's Garden | `lead_vocals` `Starr` | [`../../data/songs.tsv`](../../data/songs.tsv), row Octopus's Garden |
| Octopus's Garden first came out on Abbey Road | `first_album` `Abbey Road` | the same row |
| A random guess | `31.4%` | [`../../reports/results.md`](../../reports/results.md), "Main results", row Chance, Beatles-only column |
| Vector search | `37.6%` | the same table, row Embeddings |

## The build

No model answered these values. `data/` comes from the harvest, and the two shares come from the chance rule and the embeddings baseline. The grep and search comparison in the slide's notes comes from a local experiment. The bench holds no source for it.

## The check

`tests/test_published_numbers.py` reads each value in the table from its source.
