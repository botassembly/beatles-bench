# 0019 Score relate as it works today

Owner: the queue owner. Status: ready for review. Change 5 lands with or after ticket 0018.

## Why

The published relate rows measure a planner that ThinkThen ticket 0167 replaced. relate now asks one yes or no question for each pair a rule allows. Nothing measures that planner. The suite also has only one relate case, one set of 199 entities, so it cannot say how relate behaves on small sets, duets or relations outside singer and album.

## Prior evidence

- `reports/results.md`: the relate rows are historical, from thinkthen main at 02dc0b96. Edge F1 0.719, precision 0.867, recall 0.614. Duets: 11 of 12 picks named a lead.
- ThinkThen `specification/relate.md`: edges come from the model's knowledge of the names, not from text. The limit is 255 entities. Adding one entity changes every request, so a rerun of a grown set misses the cache.
- `data/links.tsv` holds 142 Beatles pairs from Wikidata, mostly song and composer or song and producer.

## Retained behavior

- The historical rows stay, labeled as historical.
- The `relate-songs` case keeps its entity set, so the new score is comparable.

## Changes

1. Rerun `relate-songs` through the current ThinkThen main and publish its rows beside the historical ones.
2. Add about 40 small-set cases. Each holds one to three songs, the four Beatles and three albums, one of them right. The groups are `solo`, `duet`, and `wrong-album-only`, where the right album is left out and the correct answer is no `appears_on` edge.
3. Add a `links` group from `links.tsv`: song and composer, and song and producer, in sets of about 20 entities, scored against the Wikidata pairs.
4. Score edges by precision, recall and F1 per group, at the 0.5 cut. Also report the best cut found by `thinkthen audit` on half the cases, scored on the other half.
5. `reports/results.md` explains that relate reads names from memory. For relations a text states, it points to recognize's relations group from ticket 0018.

## Proof

- `tests/test_suite.py` checks each new case: the truth edges come from the tables, every entity is named once, and a rebuild gives the same bytes.
- The live run records every exchange, and a replay with no key gives the same answers.
- Token cap: 3,000,000 input tokens for this ticket, about $0.13. The plan's upper bound is checked before the run.

## Deferred gaps

- Relations beyond singer, album, composer and producer.
- GLM and Laya.
