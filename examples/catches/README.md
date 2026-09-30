# catches

The catches slide. Three panels show Jev's share right on easy and hard questions. Under each sits one bench question with two of Jev's answers.

## What the slide shows

Jev's answers come from [`answers.jsonl`](../../results/runs/2026-09-30-all-jev/answers.jsonl) of the 2026-09-30 all-jev run. The questions come from `questions/`.

| Question | Jev's pick | Its probability | The truth | Its probability |
| --- | --- | --- | --- | --- |
| `forward-singer-033`: who sings lead on Nothin' Shakin'? | John Lennon | `0.28` | George Harrison | `0.17` |
| `lexical-trap-album-to-song-001`: which song first came out on the album Yellow Submarine? | Yellow Submarine | `0.52` | It's All Too Much | `0.34` |
| `multi-hop-same-month-050`: did Ticket to Ride come out the same month as the 37th Academy Awards? | No | `0.79` | Yes | `0.21` |

The panels:

| Panel | Value | Source |
| --- | --- | --- |
| Least viewed quarter of songs | `0.5195` | [`../../results/tables/popularity.tsv`](../../results/tables/popularity.tsv), row Jev, bin 1 |
| Most viewed quarter of songs | `0.7181` | the same table, row Jev, bin 4 |
| Word traps right | `26` of `54` | [`../../results/tables/controls.tsv`](../../results/tables/controls.tsv), row Jev, lexical-trap |
| Their controls right | `36` of `54` | the same row |
| Same-month questions with both hops right | `30` | [`../../results/tables/composition.tsv`](../../results/tables/composition.tsv), row Jev, same-month |
| Of those, chained right | `13` | the same row, `both_hops_right` less `wrong_with_both_hops` |

## The build

[`run.txt`](../../results/runs/2026-09-30-all-jev/run.txt) of the 2026-09-30 all-jev run.

## The check

`tests/test_published_numbers.py` reads each probability from the run's answers and each panel value from its table.
