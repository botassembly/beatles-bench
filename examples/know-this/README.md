# know-this

The know-this slide. Four plain points: the price, the cache, what batching saves, and how to see and cap spend.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| Jev's price per million input tokens | `0.042` | [`../../results/tables/cost.tsv`](../../results/tables/cost.tsv), row Jev, `price_source`, and [`../../scripts/score/prices.tsv`](../../scripts/score/prices.tsv), row jev |
| Output is free | `usd_per_m_output` `0` | `prices.tsv`, row jev |
| The 1,501 questions cost | `usd` `0.022466` | `cost.tsv`, row Jev |

## Claims with no bench source

- **Batching, "up to 4× less".** A local experiment measured ten rows a request. It sent its requests without the thinkthen command, so it does not replay through the 02dc0b96 build. The bench holds no copy.
- **Batching, "3–14% of answers changed".** The same experiment and one before it. Part of the range rests on rows the bench cannot hold.
- **The cache and the caps.** These describe the thinkthen command and its libraries. The thinkthen specification is their source.

## The build

The cost row: [`run.txt`](../../results/runs/2026-09-26-thinkthen-jev/run.txt) of the 2026-09-26 Jev run. The batching numbers: build not recorded in the bench.

## The check

`tests/test_published_numbers.py` reads the price and the cost from their tables.
