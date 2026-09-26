# what-jev-knows

The what-jev-knows slide. Four bars give each system's share right on the `1,313` Beatles-only questions: every category but the two reversal-general ones.

## What the slide shows

| Bar | Share | Source |
| --- | --- | --- |
| Random guess | `31.4%` | [`../../reports/results.md`](../../reports/results.md), "Main results", row Chance, Beatles-only column |
| Vector search | `0.3762` | [`../../results/tables/accuracy.tsv`](../../results/tables/accuracy.tsv), row Embeddings, scope beatles-only |
| Jev from memory | `0.6695` | the same table, row Jev, scope beatles-only |
| Big chat model | `0.9622` | the same table, row GLM-5.3 Flash, scope beatles-only |

The slide rounds each share to a whole percent: 31%, 38%, 67%, and 96%. The chance share is the expected share of a uniform guess. `accuracy.tsv` holds no Chance row.

## The build

- Jev: [`run.txt`](../../results/runs/2026-09-26-thinkthen-jev/run.txt) of the 2026-09-26 Jev run.
- GLM-5.3 Flash: `results/runs/2026-09-23-glm-5.3-flash`, asked through `scripts/run/chat.py` with thinking off. It used no thinkthen build. Build not recorded.
- Vector search: `results/runs/2026-09-23-baseline-embed`. It calls no model.

## The check

`tests/test_published_numbers.py` reads each share in the table from its source.
