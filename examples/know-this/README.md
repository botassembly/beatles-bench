# know-this

The know-this slide. Four plain points: the price, the cache, what batching saves, and how to see and cap spend.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| Jev's price per million input tokens | `0.042` | [`../../results/tables/cost.tsv`](../../results/tables/cost.tsv), row Jev, `price_source`, and [`../../scripts/score/prices.tsv`](../../scripts/score/prices.tsv), row jev |
| Output is free | `usd_per_m_output` `0` | `prices.tsv`, row jev |
| The 1,501 questions cost | `usd` `0.023347` | `cost.tsv`, row Jev |

## Claims with no bench source

- **Batching, "up to 4× less".** A local experiment measured ten rows a request. It sent its requests without the thinkthen command, so it does not replay through the 02dc0b96 build. The bench holds no copy.
- **Batching, "3–14% of answers changed".** The same experiment and one before it. Part of the range rests on rows the bench cannot hold. The slide's notes keep this range. The slide itself no longer shows it.
- **Batching, "all 306 titles in one request doubled the wrong yeses".** A local review sent the batching design's own request form live: all 306 titles in one request, asked whether each is on Abbey Road. Three runs scored 272 to 274 right with 32 to 34 wrong yeses. One title a request scored 285 right with 16 to 17. The bench holds no copy.
- **The cache and the caps.** These describe the thinkthen command and its libraries. The thinkthen specification is their source. The cache keys on the model name sent, not the version that answers. A database caps the requests of one process, and DuckDB's warm step skips that cap. ThinkThen's issues `2026-09-26-architect-review-08-cache.md` and `2026-09-26-architect-review-04-libraries-and-databases.md` record both.

## The build

The cost row: [`run.txt`](../../results/runs/2026-09-26-thinkthen-jev/run.txt) of the 2026-09-26 Jev run. The batching numbers: build not recorded in the bench.

## The check

`tests/test_published_numbers.py` reads the price and the cost from their tables.
