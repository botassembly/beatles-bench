# Full results

The audited runs of 2026-09-23, with every Jev run asked again from an empty recording on 2026-09-25 (ticket 0009) and again on 2026-09-26 (ticket 0014, `sdlc/tickets/0014-shipped-recognize-and-relate.md`). Jev's rows come from `results/runs/2026-09-26-thinkthen-jev` and `2026-09-26-functions-jev`. This report holds every number the front page leaves out: the intervals, the tests, the baselines, the function suite, the costs, and the audit history. `python3 scripts/score/table.py` prints the two main tables below from `results/tables/`.

## Main results

1,501 questions in 15 categories. The headline is Beatles-only: every category but the two reversal-general ones, 1,313 questions. Each cell is the share right with its 95% Wilson interval. `decide` says yes at 0.5, `choose` takes its winner, and a tie at the top that holds the truth earns one over the number tied. Chance is the expected share of a uniform guess.

| System | Beatles-only (1,313) | Overall (1,501) | Dollars per 1,000 questions | Median time per answer |
| --- | --- | --- | --- | --- |
| Jev | 67.0% (64.4% to 69.4%) | 70.2% (67.9% to 72.5%) | 0.0150 | 0.21 s |
| GLM-5.3 Flash | 96.2% (95.0% to 97.1%) | 96.7% (95.7% to 97.5%) | 0.0555 | 8.24 s |
| Laya | 35.0% (32.5% to 37.7%) | 35.8% (33.4% to 38.2%) | 0.0000 | 0.07 s |
| *Vector search (question vs. options)* | | | | |
| BM25 | 33.8% (31.3% to 36.4%) | 35.0% (32.6% to 37.4%) | 0.0000 | no model call |
| Embeddings | 37.6% (35.0% to 40.3%) | 39.8% (37.3% to 42.3%) | 0.0000 | no model call |
| Hybrid | 35.9% (33.4% to 38.6%) | 37.5% (35.1% to 40.0%) | 0.0000 | no model call |
| Word overlap | 33.2% (30.7% to 35.8%) | 34.2% (31.8% to 36.6%) | 0.0000 | no model call |
| Chance | 31.4% | 30.6% | | |

Jev is jev-1.13.0 through ThinkThen. GLM-5.3 Flash runs with thinking off through `scripts/run/chat.py`. Laya is a local Jev-like model (see [Laya](#laya)). [baselines.md](baselines.md) describes the four baselines.

Jev's time comes from `results/runs/2026-09-26-thinkthen-jev`. Its `loadavg.txt` records a load average of 3.83 at the start and 7.10 at the end, on 16 cores. The GLM-5.3 Flash and Laya times come from the main runs of 2026-09-23. Those runs recorded no load (`paper/notes.md`). A quiet-machine rerun is still to come.

- Jev beats the best baseline, embeddings, on Beatles-only questions by the exact McNemar test (484 against 103 discordant pairs, p < 0.001). GLM beats Jev (410 against 22, p < 0.001). Jev beats Laya (514 against 99, p < 0.001). Laya does not differ from embeddings (194 against 228, p = 0.11).
- Cost uses `scripts/score/prices.tsv`: Jev at 0.042 dollars per million input tokens with free output, GLM at Z.ai's price (0.15 per million input, 0.03 cached, 0.50 output), and Laya at no per-token charge. Time is the wall time of one request. The baselines call no model, so the table shows no time for them.
- Calibration. The expected calibration error is 0.026 for Jev (bootstrap 95% interval 0.011 to 0.043), 0.031 for GLM (0.024 to 0.038), and 0.160 for Laya (0.138 to 0.183). A tie that holds the right answer counts as its share, as in accuracy. The interval covers resampling of these questions only. Three Jev runs over the same questions give 0.018 (2026-09-23), 0.023 (2026-09-25), and 0.026 (2026-09-26).
- Popularity. Jev gets 49% of questions about the least viewed quarter of songs and 73% about the most viewed. GLM stays between 94% and 99%.
- Multi-hop. Jev gets the chained album-year question right on 22 of 60 items. On the 41 items where it gets both single hops right, it gets the chained question right on only 18 (`composition.tsv`).
- Controls. Jev falls from 70% on the lexical-trap controls to 50% on the traps (12 against 1 discordant, p = 0.003). Near neighbors cost it 5 points (75% against 80%), within chance (10 against 7 discordant, p = 0.63).
- Yes/no cuts (`decide.tsv`). Each yes/no set reports its AUC, the right answers at the 0.5 cut, and the right answers at a cut tuned on one half of the items and scored on the other. [leaning-no.md](leaning-no.md) covers Jev's lean toward no and how to audit a run for it with `thinkthen audit` and `thinkthen diff`.

## Tables and figures

Every table sits in [results/tables/](../results/tables/), one row per system and category. `scripts/score/analyze.py` writes them. The figures sit in [figures/](figures/) as SVG and PNG. Figures that show baselines draw the best one.

1. [The graph from singer to first release](figures/1-graph.svg)
2. [Coverage](figures/2-coverage.svg)
3. [Calibration](figures/3-calibration.svg)
4. [Accuracy with intervals](figures/4-accuracy.svg)
5. [Popularity](figures/5-popularity.svg)
6. [Reversal directions](figures/6-directions.svg)
7. [Cost and time beside accuracy](figures/7-cost-time.svg)
8. [The pipeline](figures/8-pipeline.svg)
9. [Time per answer](figures/9-latency.svg)

## The function suite

The categories use only `choose` and `decide`. The function suite tests the other functions ThinkThen names. decide and choose come from each system's main run. The other rows come from `results/runs/2026-09-26-functions-jev` for Jev and `results/runs/2026-09-23-functions-*` for GLM and Laya.

| Function | Test | Measure | Jev | GLM-5.3 Flash | Laya |
| --- | --- | --- | --- | --- | --- |
| decide | yes/no questions | accuracy at 0.5 | 0.689 (0.626 to 0.745) | 0.904 (0.858 to 0.935) | 0.539 (0.475 to 0.603) |
| choose | pick-one questions | accuracy | 0.705 (0.679 to 0.729) | 0.978 (0.969 to 0.985) | 0.325 (0.300 to 0.351) |
| tag | lead singers | exact-set match | 0.291 (0.226 to 0.366) | 0.937 (0.887 to 0.965) | 0.000 (0.000 to 0.024) |
| tag | lead singers | top pick right | 0.747 (0.674 to 0.808) | 0.997 (0.970 to 1.000) | 0.070 (0.039 to 0.120) |
| score | popularity | Spearman with 2024 page views | 0.696 (0.607 to 0.768) | 0.774 (0.704 to 0.830) | 0.123 (-0.032 to 0.272) |
| filter | lead singer or album | F1 | 0.639 (0.543 to 0.724) | 0.891 (0.828 to 0.940) | 0.128 (0.027 to 0.230) |
| rank | popularity | Spearman with 2024 page views | 0.638 (0.537 to 0.721) | 0.774 (0.704 to 0.829) | 0.199 (0.046 to 0.343) |
| rank | date | Spearman with release date | 0.805 (0.745 to 0.852) | 0.893 (0.858 to 0.920) | -0.055 (-0.203 to 0.096) |
| find | album | exact match | 0.654 (0.518 to 0.768) | 0.981 (0.899 to 0.997) | 0.115 (0.054 to 0.230) |
| annotate | card | singer accuracy | 0.310 (0.243 to 0.386) | 0.924 (0.872 to 0.956) | 0.000 (0.000 to 0.024) |
| annotate | card | singer top pick right | 0.734 (0.660 to 0.797) | 0.965 (0.924 to 0.984) | 0.063 (0.035 to 0.113) |
| annotate | card | album accuracy | 0.582 (0.510 to 0.652) | 0.978 (0.945 to 0.991) | 0.115 (0.077 to 0.170) |
| annotate | card | year accuracy | 0.407 (0.338 to 0.479) | 0.989 (0.961 to 0.997) | 0.077 (0.046 to 0.125) |
| recognize | names | song precision | 0.959 (0.863 to 0.989) |  |  |
| recognize | names | song recall | 0.979 (0.891 to 0.996) |  |  |
| recognize | names | person precision | 1.000 (0.926 to 1.000) |  |  |
| recognize | names | person recall | 1.000 (0.926 to 1.000) |  |  |
| recognize | names | album precision | 1.000 (0.924 to 1.000) |  |  |
| recognize | names | album recall | 0.979 (0.891 to 0.996) |  |  |
| relate | song to singer and album | edge F1 | 0.719 (0.673 to 0.766) |  |  |
| relate | song to singer and album | edge precision | 0.867 (0.820 to 0.904) |  |  |
| relate | song to singer and album | edge recall | 0.614 (0.562 to 0.663) |  |  |
| relate | song to singer and album | singer top pick right | 0.899 (0.842 to 0.937) |  |  |
| relate | song to singer and album | album top pick right | 0.637 (0.565 to 0.704) |  |  |
| relate | song to singer and album | duets: pick is a lead | 0.917 (0.646 to 0.985) |  |  |

The relate rows are historical. They measure relate's old choice planner, in thinkthen main at 02dc0b96 on 2026-09-26. ThinkThen ticket 0167 replaced that planner. relate now asks one yes or no question for each pair a rule allows. The bench has not scored the pair planner.

A blank cell was not asked. GLM runs through `scripts/run/chat.py suite`. That command asks tag, score, filter, rank, find, and annotate. recognize and relate run through `thinkthen recognize` and `thinkthen relate`. Those commands read a probability for each token or option, and a chat model states one, so GLM skips them. Laya's run of 2026-09-23 asked the older recognize and relate tests, built from annotate. Those tests are gone, so its cells are blank. Laya runs only on a Mac through a local shim and was not asked again.

recognize scores the names `thinkthen recognize song person album` prints, one sentence per call. The command's tokenizer splits `.`, `!`, `?`, `,`, `:`, and `;` from the end of each word (thinkthen `specification/recognize.md`, "Names"), so a name may keep or drop such a mark. The scorer trims those marks from the end of both the true name and the name said, and compares the rest exactly. Of 144 true names Jev missed two: it split "Back in the U.S.S.R." in two, and it did not name the album "Help!". At that build, the bench asked `thinkthen relate` once over the 199 songs, Beatles, and albums, in three requests of at most 96,000 bytes. relate asked one choice per song for its lead singer. It said a second singer only in an exact tie at 0.5. So each of the 12 duets almost always gained at most one of its two singer edges in the strict counts. The duet row counted the duets whose pick, before the bar, named one of the two leads.

Each strict measure for tag, annotate's singer, and relate has a top pick row beside it. For tag and annotate, the row counts the songs whose likeliest singer is a true lead. A tie at the top earns the share of its singers that are true. An extra singer the strict measure counts wrong does not cost the song. For relate, the two rows counted the old planner's picks that named a true singer or album, one per song. A right answer under the 0.5 bar counted there. The full table in `results/tables/` also keeps the older rows "top label right, single-lead songs". They give a tie at the top to the first singer in the list.

## ThinkThen gaps

Every question type ran through `choose` or `decide` with per-record options (`--options /options`). Every function in the suite runs through its own shipped command.

## Open book and picked sections

- [open-book.md](open-book.md): Jev with the 306-song catalog pasted before each question. In the 2026-09-23 run it gets 187 of 196 right, against 62 of 196 closed book. The fresh runs of 2026-09-25 and 2026-09-26 get 186 and 184.
- [rad.md](rad.md): Jev picks two of 28 catalog sections, then answers with only those. In the 2026-09-23 run it gets 167 of 196 right at 0.12 dollars per 1,000 questions, against 0.51 for the full catalog.

## An in-text check

`scripts/run/in_text_check.py` asks 20 short customer-service questions whose answer is written in the text. It checks the wiring. Laya answers 18 of 20 right. Jev's recording holds 12 of the 20 requests, and it answers all 12 right. The results and recordings sit in `results/archive/in-text-check/`.

## Laya

Laya is `aac6fef/laya-mlx`, ModernBERT-large (about 421M parameters) under MLX on a Mac with an Apple M5 chip. A small shim serves it on the System One API at `127.0.0.1:8791`. It holds 512 tokens per request. The bench reached it through an SSH tunnel, with one call in flight. [scripts/README.md](../scripts/README.md) gives the commands.

`RUN/model-time.tsv` splits each call's wall time into the model's time and the rest (the command's start, the tunnel, and HTTP). The model's median share is 0.017 s over the main questions and 0.020 s over the function suite. Laya scores near BM25 and says yes to all four Beatles on every tag question.

## Spend and history

Before the merge, Jev's main runs cost 0.037 dollars and GLM's 0.14 dollars at Z.ai's price. The function suites then sent 1,776 Jev requests (0.040 dollars) and 87 more after the settled-lead rule (0.0011 dollars), 1,157 GLM requests (0.060 dollars, median 3.5 s), and 1,028 Laya requests at no charge. Each run folder holds its usage. A rerun answers every unchanged question from the recording. `results/history.tsv` gets one dated row per run and per function measure. The fresh Jev runs of 2026-09-25 sent 6,191,593 input tokens in all, about 0.26 dollars (ticket 0009 record). Those of 2026-09-26 sent 6,057,783, about 0.25 dollars (ticket 0014 record).

## Audit history: fixes on 2026-09-23

The seed set of 629 questions (`results/archive/2026-09-23-seed/`) had four label bugs, and an audit of wrong answers found more. Each fix is a test.

- Songwriters. Wikidata names Lennon or McCartney alone for most songs credited "Lennon–McCartney". 21 of 44 reversal composer questions contradicted the published credit. A composer now must agree with the credit, and a shared credit makes the pair the answer.
- Title join. The list links some titles to another song's article ("Can You Take Me Back?" to Cry Baby Cry). 13 relation rows sat on misjoined songs. A song takes facts only from an article whose title matches its own exactly, and a test checks the whole table.
- First release dates. A page that opens with another artist's recording gave that artist's date. 21 songs changed.
- Events. Wars, currencies, and treaties counted as events of a month. The rule now keeps only events Wikidata dates to one day. 19 months changed or dropped. Before/after items are balanced 30 before and 30 after.
- Lead singers. The list's lead column disagreed with the songs' own articles on 8 items (Please Please Me, Thank You Girl, Cry Baby Cry, and others). A lead question now asks a song only when the list and the Personnel section of the song's article name the same Beatles.
- Album questions. "First released on" could mean a single, while the truth was the first album. The audit found 40 questions where a single came first. Every album question now asks for "the first album to include it".
- Three items dropped (`data/pins/excluded.tsv`): an event article that covers two fights in different months, and two reversal pairs where Wikidata and Wikipedia name different people.
- Ties. A system that ties the truth with other options at the top now earns a share (one over the number tied), and ties are counted apart.
- Settled leads. The tag, filter, annotate, and relate tests ask a song's lead singer only when its lead is settled: every lead is a Beatle, no helper sings, and the song's own article agrees with the list. `generate.settled_lead()` holds the rule for the categories and the suite.
