# jev

The jev slide. One bench question goes to Jev's choose endpoint, and a probability comes back for each singer. The slide also gives Jev's typical time and price.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| John for Octopus's Garden | `0.01` | [`../choose/outputs.jsonl`](../choose/outputs.jsonl), id `choose-cold-04` |
| Paul for Octopus's Garden | `0.02` | the same row |
| George for Octopus's Garden | `0.13` | the same row |
| Ringo for Octopus's Garden | `0.84` | the same row |
| John and Paul duet for Octopus's Garden | `0.0` | the same row |
| The typical time of one question | `median_s` `0.215` | [`../../results/tables/cost.tsv`](../../results/tables/cost.tsv), row Jev |
| The price of the 1,501 questions | `usd` `0.022466` | the same row |
| The load at the start of the run | `3.83` | [`loadavg.txt`](../../results/runs/2026-09-26-thinkthen-jev/loadavg.txt) of the 2026-09-26 Jev run, second start line |
| The load at the end of the run | `7.10` | the same file, end line |
| The price per million input tokens | `usd_per_m_input` `0.042` | [`../../scripts/score/prices.tsv`](../../scripts/score/prices.tsv), row jev |

The first start line of `loadavg.txt` belongs to an attempt that stopped on a backend timeout. The second attempt resumed into the same folder.

## The build

- The probabilities: [`../choose/run.txt`](../choose/run.txt).
- The time, the price, and the load: [`run.txt`](../../results/runs/2026-09-26-thinkthen-jev/run.txt) of the 2026-09-26 Jev run.

## The check

`tests/test_published_numbers.py` reads each value in the table from its source. `./run.sh` replays the choose folder byte for byte.
