# bench-run

The bench-run slide. Three facts about the bench, and the steps to run it.

## What the slide shows

| Claim | Value | Source |
| --- | --- | --- |
| Questions | `1,501` | [`../../results/tables/cost.tsv`](../../results/tables/cost.tsv), row Jev, `questions` |
| A full Jev run costs | `usd` `0.023347` | the same row |
| A typical answer takes | `median_s` `0.195` | the same row |
| Jev per 1,000 questions | `usd_per_1000_questions` `0.015554` | the same row |
| GLM-5.3 Flash per 1,000 questions | `usd_per_1000_questions` `0.055528` | the same table, row GLM-5.3 Flash |
| The load at the start of the run | `6.74` | [`loadavg.txt`](../../results/runs/2026-09-30-all-jev/loadavg.txt) of the 2026-09-30 all-jev run, second start line |
| The load at the end of the run | `11.18` | the same file, end line |

The steps are the commands of the bench README, "Run it". `./run.sh` with no backend address replays the newest Jev run and every function folder here with no key.

## The build

- Jev: [`run.txt`](../../results/runs/2026-09-26-thinkthen-jev/run.txt) of the 2026-09-26 Jev run.
- GLM-5.3 Flash: `results/runs/2026-09-23-glm-5.3-flash`, asked through `scripts/run/chat.py`. It used no thinkthen build. Build not recorded.

## The check

`tests/test_published_numbers.py` reads each value in the table from its source.
