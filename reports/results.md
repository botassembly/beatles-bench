# Full results

The audited runs of 2026-09-23, with every Jev run asked again from an empty recording on 2026-09-25 (ticket 0009), again on 2026-09-26 (ticket 0014, `sdlc/tickets/0014-shipped-recognize-and-relate.md`), and once more over the whole bench on 2026-09-30 (ticket 0023). Jev's rows come from `results/runs/2026-09-30-all-jev`, and Liquid d1's from `results/runs/2026-09-30-all-liquid-d1`. This report holds every number the front page leaves out: the intervals, the tests, the baselines, the function suite, the costs, and the audit history. `python3 scripts/score/table.py` prints the tables below from `results/tables/` (and the five-model table [models.md](models.md) carries).

## By function

Each function's main measure at three levels: from memory, with the exact context of a card that holds the facts (ticket 0020), and with the extra context the cases carry (ticket 0021). An exact-context case keeps the from-memory case's question and truth, and writes the facts into the record: the text, then one short card per song it names — title, lead singers, first album, year, and length, plus the writers, release date, or 2024 page views where the truth needs them. decide and choose sample 100 eligible questions from the main files; the other functions sample 100 of their own from-memory cases, and rank samples 100 of each of its two asks. recognize has no from-memory score — it only ever reads. relate judges names from memory, so it has no exact-context test; its from-memory score below is the edge F1 of its 100 cases at the 0.5 cut.

| Function | Cases | What it asks | From memory | Exact context | Extra context |
| --- | --- | --- | --- | --- | --- |
| decide | 228 | yes or no about one song | 0.680 | 1.000 | 0.947 |
| choose | 1,273 | the right one of four or five options | 0.709 | 0.960 | 0.948 |
| tag | 300 | every Beatle who sang the lead, and who wrote or played how long | 0.560 | 1.000 | 0.890 |
| score | 300 | how well known the song is today, 1 to 5, and its length | 0.637 / 0.625 | 0.744 | 0.883 / 0.967 |
| filter | 300 | whether a song keeps or drops | 0.719 | 1.000 | 0.969 |
| rank | 353 | the songs in order by fame, and by date | 0.649 / 0.795 | 0.802 / 0.978 | 0.797 / 0.812 |
| find | 300 | the one song of the set that fits | 0.487 | 1.000 | 1.000 |
| annotate | 300 | singer, first album and year, or writers, cover and length | 0.348 | 1.000 | 0.956 |
| recognize | 400 | the song, person and album names in a sentence | — | 1.000 | — |
| relate | 100 | the edges between a set's songs, people and albums | 0.524 | — | — |

The columns are the main measures of the table below: accuracy, exact-set match, F1, or Spearman. The rank and score cells hold their two measures. An exact-context cell covers at most 100 cases a test; annotate's from-memory and extra-context cells count only its settled-lead songs, and score's length measure has its own n. recognize's cell is its song precision on the names-template sentences, and relate's is edge F1 at the 0.5 cut. For score and rank's popularity ask the card prints the song's 2024 page views, so those exact-context figures measure how well the model places a printed number on a coarse five-level scale or an ordering — and ties cost the rank correlation even when the number is read right. All of these numbers come from `results/runs/2026-09-30-all-jev`: the 1,501 questions and 5,838 cases, 9,465,732 input tokens, about $0.40.

The gap between the columns is why the facts belong in the text. On your own work, label a few dozen cases: `thinkthen audit` grades a run against them and suggests a cut, and `thinkthen diff` compares two runs, two cuts or two models without a model call.

## Main results

1,501 questions in 15 categories. The headline is Beatles-only: every category but the two reversal-general ones, 1,313 questions. Each cell is the share right with its 95% Wilson interval. `decide` says yes at 0.5, `choose` takes its winner, and a tie at the top that holds the truth earns one over the number tied. Chance is the expected share of a uniform guess.

| System | Beatles-only (1,313) | Overall (1,501) | Dollars per 1,000 questions | Median time per answer |
| --- | --- | --- | --- | --- |
| Jev | 67.4% (64.8% to 69.8%) | 70.5% (68.1% to 72.7%) | 0.0156 | 0.20 s |
| GLM-5.3 Flash | 96.2% (95.0% to 97.1%) | 96.7% (95.7% to 97.5%) | 0.0555 | 8.24 s |
| Laya | 35.0% (32.5% to 37.7%) | 35.8% (33.4% to 38.2%) | 0.0000 | 0.07 s |
| Kev 4B | 44.1% (41.4% to 46.8%) | 47.2% (44.7% to 49.8%) |  | 0.20 s |
| Liquid d1 | 64.3% (61.7% to 66.9%) | 67.5% (65.1% to 69.9%) | 0.0000 | 0.31 s |
| Nimble 9B | 48.0% (45.3% to 50.7%) | 51.9% (49.4% to 54.4%) |  | 0.28 s |
| *Vector search (question vs. options)* | | | | |
| BM25 | 33.8% (31.3% to 36.4%) | 35.0% (32.6% to 37.4%) | 0.0000 | no model call |
| Embeddings | 37.6% (35.0% to 40.3%) | 39.8% (37.3% to 42.3%) | 0.0000 | no model call |
| Hybrid | 35.9% (33.4% to 38.6%) | 37.5% (35.1% to 40.0%) | 0.0000 | no model call |
| Word overlap | 33.2% (30.7% to 35.8%) | 34.2% (31.8% to 36.6%) | 0.0000 | no model call |
| Chance | 31.4% | 30.6% | | |

Five models answered the same 1,501 knowledge questions. The table below adds the hard and easy split and each model's exact McNemar test against Jev, paired by question id over the 1,501 questions and scored right or wrong by the scorer's default verdict — a tied pick counts wrong. Its two counts are the questions only that system answered right, then the questions only Jev answered right. [models.md](models.md) is the page to cite.

| System | Beatles-only (1,313) | Overall (1,501) | Hard (505) | Easy (996) | Against Jev (McNemar) | Run | Build | Date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jev | 67.4% (64.8% to 69.8%) | 70.5% (68.1% to 72.7%) | 56.9% (52.6% to 61.2%) | 77.3% (74.6% to 79.8%) | — | 2026-09-30-all-jev | aec7819bb | 2026-09-30 |
| Liquid d1 | 64.3% (61.7% to 66.9%) | 67.5% (65.1% to 69.9%) | 52.9% (48.5% to 57.2%) | 75.0% (72.2% to 77.6%) | 140 to 191, p = 0.006 | 2026-09-30-all-liquid-d1 | aec7819bb | 2026-09-30 |
| Nimble 9B | 48.0% (45.3% to 50.7%) | 51.9% (49.4% to 54.4%) | 41.6% (37.4% to 45.9%) | 57.1% (54.0% to 60.2%) | 148 to 422, p < 0.001 | 2026-09-30-thinkthen-nimble-9b | aec7819bb | 2026-09-30 |
| Kev 4B | 44.1% (41.4% to 46.8%) | 47.2% (44.7% to 49.8%) | 39.0% (34.8% to 43.3%) | 51.4% (48.3% to 54.5%) | 137 to 481, p < 0.001 | 2026-09-29-thinkthen-kev-4b | 2c5ac772b | 2026-09-29 |
| Laya | 35.0% (32.5% to 37.7%) | 35.8% (33.4% to 38.2%) | 29.9% (26.1% to 34.0%) | 38.8% (35.8% to 41.8%) | 96 to 612, p < 0.001 | 2026-09-23-thinkthen-laya | — | 2026-09-23 |
| GLM-5.3 Flash | 96.2% (95.0% to 97.1%) | 96.7% (95.7% to 97.5%) | 95.5% (93.3% to 97.0%) | 97.3% (96.1% to 98.2%) | 419 to 21, p < 0.001 | 2026-09-23-glm-5.3-flash | chat script | 2026-09-23 |
| *Vector search (question vs. options)* | | | | | | | | |
| BM25 | 33.8% (31.3% to 36.4%) | 35.0% (32.6% to 37.4%) | 29.0% (25.2% to 33.1%) | 38.0% (35.1% to 41.1%) | 65 to 594, p < 0.001 | 2026-09-23-baseline-bm25 | — | 2026-09-23 |
| Embeddings | 37.6% (35.0% to 40.3%) | 39.8% (37.3% to 42.3%) | 33.3% (29.3% to 37.5%) | 43.1% (40.0% to 46.2%) | 104 to 560, p < 0.001 | 2026-09-23-baseline-embed | — | 2026-09-23 |
| Hybrid | 35.9% (33.4% to 38.6%) | 37.5% (35.1% to 40.0%) | 30.8% (26.9% to 34.9%) | 41.0% (38.0% to 44.0%) | 75 to 575, p < 0.001 | 2026-09-23-baseline-hybrid | — | 2026-09-23 |
| Word overlap | 33.2% (30.7% to 35.8%) | 34.2% (31.8% to 36.6%) | 28.7% (24.9% to 32.8%) | 36.9% (34.0% to 40.0%) | 66 to 602, p < 0.001 | 2026-09-23-baseline-overlap | — | 2026-09-23 |
| Chance | 31.4% | 30.6% | 30.3% | 30.8% | | | | |

Each figure is one run, and the builds differ across rows; the knowledge questions ask from memory only. Liquid d1 left three questions unanswered at the rate limit; they score wrong.

Jev is jev-1.13.0 through ThinkThen. GLM-5.3 Flash runs with thinking off through `scripts/run/chat.py`. Laya is a local Jev-like model (see [Laya](#laya)). [baselines.md](baselines.md) describes the four baselines.

Jev's time comes from `results/runs/2026-09-30-all-jev`. Its `loadavg.txt` records a load average of 6.74 at the start and 11.18 at the end, on 16 cores. The first start line, at 10.24, belongs to an attempt that stopped on a backend timeout; the second attempt resumed into the same folder. The GLM-5.3 Flash and Laya times come from the main runs of 2026-09-23. Those runs recorded no load (`paper/notes.md`). A quiet-machine rerun is still to come.

- Jev beats the best baseline, embeddings, on Beatles-only questions by the exact McNemar test (487 against 101 discordant pairs, p < 0.001). GLM beats Jev (404 against 21, p < 0.001). Jev beats Laya (512 against 92, p < 0.001). Laya does not differ from embeddings (194 against 228, p = 0.11).
- Cost uses `scripts/score/prices.tsv`: Jev at 0.042 dollars per million input tokens with free output, GLM at Z.ai's price (0.15 per million input, 0.03 cached, 0.50 output), and Laya at no per-token charge. Time is the wall time of one request. The baselines call no model, so the table shows no time for them.
- Calibration. The expected calibration error is 0.027 for Jev (bootstrap 95% interval 0.013 to 0.045), 0.031 for GLM (0.024 to 0.038), and 0.160 for Laya (0.138 to 0.183). A tie that holds the right answer counts as its share, as in accuracy. The interval covers resampling of these questions only. Four Jev runs over the same questions give 0.018 (2026-09-23), 0.023 (2026-09-25), 0.026 (2026-09-26), and 0.027 (2026-09-30).
- Popularity. Jev gets 52% of questions about the least viewed quarter of songs and 72% about the most viewed. GLM stays between 94% and 99%.
- Multi-hop. Jev gets the chained album-year question right on 29 of 60 items. On the 39 items where it gets both single hops right, it gets the chained question right on only 23 (`composition.tsv`).
- Controls. Jev falls from 67% on the lexical-trap controls to 48% on the traps (12 against 2 discordant, p = 0.013). Near neighbors cost it nothing (82% against 83%), within chance (7 against 8 discordant, p = 1.0).
- Yes/no cuts (`decide.tsv`). Each yes/no set reports its AUC, the right answers at the 0.5 cut, and the right answers at a cut tuned on one half of the items and scored on the other. [leaning-no.md](leaning-no.md) covers Jev's lean toward no and how to audit a run for it with `thinkthen audit` and `thinkthen diff`.

## Jev and Liquid d1

Liquid's d1 answered the same 1,501 questions and all 5,838 suite cases on 2026-09-30, through `thinkthen --backend liquid` at model `d1:free` (`results/runs/2026-09-30-all-liquid-d1`). `d1:free` is a name the vendor may repoint, so each d1 figure below comes from that one run of 2026-09-30. The generated reports put the two backends side by side: [generated/by-function.md](generated/by-function.md) gives each function's main measure per level, and [generated/head-to-head.md](generated/head-to-head.md) pairs their answers case by case with an exact McNemar test.

From memory the two are close: 67.4% for Jev against 64.3% for d1 on the Beatles-only questions, and on the pick-one questions asked from memory the McNemar test gives p = 0.02 — Jev ahead, barely. The three largest differences by function and level sit in the extra-context tests and the free sentences:

- filter with extra context: F1 0.969 for Jev, 0.525 for d1 (295 of 300 cases fully right against 155).
- recognize on the free sentences: 311 of 400 cases fully right for Jev, 185 for d1.
- decide with extra context: 0.947 for Jev, 0.650 for d1 (284 of 300 against 195).

With the exact facts in the card both backends fill the decide, tag, and filter rows at 1.000. d1 refused the relate `links` and `song to singer and album` tests whole as malformed or too large, and the find `reading` test — the exact-context level — hit the rate limit whole, so those cells stay empty. Seven more tests ended part-answered — annotate's card, details and reading tests, find's album-more and singer tests, rank's reading-popularity test, and relate's more-links — mostly on the rate limit. `gaps.tsv` in the run folder lists all 531 unanswered calls, and the generated reports score only the cases d1 answered. The run's `run.txt` marks its function table pending: `results/tables/functions-liquid-d1.tsv` stays unwritten until the 513 rate-limited gaps are asked again.

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

The categories use only `choose` and `decide`. The function suite tests every function ThinkThen names at four levels: from memory (the plain questions), exact context (a short card with the facts), extra context (a fuller context), and text (free sentences, for recognize). Every Jev row comes from `results/runs/2026-09-30-all-jev`, which asked all 5,838 cases in one folder; Liquid d1's all-run of the same day is compared in [Jev and Liquid d1](#jev-and-liquid-d1). GLM and Laya keep their from-memory rows from `results/runs/2026-09-23-functions-*`; those runs predate the new levels, so their columns stop at the from-memory tests.

| Function | Test | Measure | Jev | GLM-5.3 Flash | Laya |
| --- | --- | --- | --- | --- | --- |
| decide | yes/no questions | accuracy at 0.5 | 0.680 (0.617 to 0.737) | 0.904 (0.858 to 0.935) | 0.539 (0.475 to 0.603) |
| choose | pick-one questions | accuracy | 0.709 (0.683 to 0.733) | 0.978 (0.969 to 0.985) | 0.325 (0.300 to 0.351) |
| decide | album | accuracy at 0.5 | 0.848 (0.778 to 0.900) |  |  |
| decide | reading | accuracy at 0.5 | 1.000 (0.963 to 1.000) |  |  |
| decide | context | accuracy at 0.5 | 0.947 (0.915 to 0.967) |  |  |
| choose | reading | accuracy | 0.960 (0.902 to 0.984) |  |  |
| choose | context | accuracy | 0.948 (0.917 to 0.968) |  |  |
| tag | lead singers | exact-set match | 0.560 (0.503 to 0.615) | 0.937 (0.887 to 0.965) | 0.000 (0.000 to 0.024) |
| tag | lead singers | top pick right | 0.802 (0.753 to 0.843) | 0.997 (0.970 to 1.000) | 0.070 (0.039 to 0.120) |
| tag | reading | exact-set match | 1.000 (0.963 to 1.000) |  |  |
| tag | reading | top pick right | 1.000 (0.963 to 1.000) |  |  |
| tag | context | exact-set match | 0.890 (0.850 to 0.921) |  |  |
| tag | context | top pick right | 0.918 (0.882 to 0.944) |  |  |
| score | popularity | Spearman with 2024 page views | 0.637 (0.536 to 0.721) | 0.774 (0.704 to 0.830) | 0.123 (-0.032 to 0.272) |
| score | reading | Spearman with 2024 page views | 0.744 (0.638 to 0.823) |  |  |
| score | length | Spearman with length in seconds | 0.625 (0.504 to 0.723) |  |  |
| score | popularity-context | Spearman with 2024 page views | 0.883 (0.844 to 0.913) |  |  |
| score | length-context | Spearman with length in seconds | 0.967 (0.953 to 0.977) |  |  |
| filter | lead singer or album | F1 | 0.719 (0.641 to 0.793) | 0.891 (0.828 to 0.940) | 0.128 (0.027 to 0.230) |
| filter | reading | F1 | 1.000 (1.000 to 1.000) |  |  |
| filter | context | F1 | 0.969 (0.938 to 0.993) |  |  |
| rank | popularity | Spearman with 2024 page views | 0.649 (0.549 to 0.730) | 0.774 (0.704 to 0.829) | 0.199 (0.046 to 0.343) |
| rank | date | Spearman with release date | 0.795 (0.733 to 0.844) | 0.893 (0.858 to 0.920) | -0.055 (-0.203 to 0.096) |
| rank | reading-popularity | Spearman with 2024 page views | 0.802 (0.716 to 0.864) |  |  |
| rank | reading-date | Spearman with release date | 0.978 (0.966 to 0.985) |  |  |
| rank | popularity-context | Spearman with 2024 page views | 0.797 (0.733 to 0.847) |  |  |
| rank | date-context | Spearman with release date | 0.812 (0.754 to 0.858) |  |  |
| find | album | exact match | 0.487 (0.431 to 0.543) | 0.981 (0.899 to 0.997) | 0.115 (0.054 to 0.230) |
| find | reading | exact match | 1.000 (0.963 to 1.000) |  |  |
| find | context | exact match | 1.000 (0.987 to 1.000) |  |  |
| annotate | card | singer accuracy | 0.348 (0.278 to 0.425) | 0.924 (0.872 to 0.956) | 0.000 (0.000 to 0.024) |
| annotate | card | singer top pick right | 0.791 (0.721 to 0.847) | 0.965 (0.924 to 0.984) | 0.063 (0.035 to 0.113) |
| annotate | card | album accuracy | 0.566 (0.493 to 0.636) | 0.978 (0.945 to 0.991) | 0.115 (0.077 to 0.170) |
| annotate | card | year accuracy | 0.412 (0.343 to 0.485) | 0.989 (0.961 to 0.997) | 0.077 (0.046 to 0.125) |
| annotate | card | writers accuracy | 0.898 (0.831 to 0.941) |  |  |
| annotate | card | cover accuracy | 0.941 (0.883 to 0.971) |  |  |
| annotate | card | length accuracy | 0.847 (0.772 to 0.901) |  |  |
| annotate | reading | singer accuracy | 1.000 (0.958 to 1.000) |  |  |
| annotate | reading | singer top pick right | 1.000 (0.958 to 1.000) |  |  |
| annotate | reading | album accuracy | 1.000 (0.963 to 1.000) |  |  |
| annotate | reading | year accuracy | 1.000 (0.963 to 1.000) |  |  |
| annotate | context | singer accuracy | 0.956 (0.911 to 0.978) |  |  |
| annotate | context | singer top pick right | 1.000 (0.976 to 1.000) |  |  |
| annotate | context | album accuracy | 1.000 (0.979 to 1.000) |  |  |
| annotate | context | year accuracy | 1.000 (0.979 to 1.000) |  |  |
| annotate | context | writers accuracy | 0.975 (0.928 to 0.991) |  |  |
| annotate | context | cover accuracy | 0.983 (0.940 to 0.995) |  |  |
| annotate | context | length accuracy | 1.000 (0.968 to 1.000) |  |  |
| recognize | names-template | song precision | 1.000 (0.926 to 1.000) |  |  |
| recognize | names-template | song recall | 1.000 (0.926 to 1.000) |  |  |
| recognize | names-template | person precision | 1.000 (0.926 to 1.000) |  |  |
| recognize | names-template | person recall | 1.000 (0.926 to 1.000) |  |  |
| recognize | names-template | album precision | 0.844 (0.712 to 0.923) |  |  |
| recognize | names-template | album recall | 0.792 (0.657 to 0.883) |  |  |
| recognize | varied | song precision | 0.971 (0.851 to 0.995) |  |  |
| recognize | varied | song recall | 0.917 (0.782 to 0.971) |  |  |
| recognize | varied | person precision | 1.000 (0.904 to 1.000) |  |  |
| recognize | varied | person recall | 1.000 (0.904 to 1.000) |  |  |
| recognize | varied | album precision | 0.861 (0.713 to 0.939) |  |  |
| recognize | varied | album recall | 0.861 (0.713 to 0.939) |  |  |
| recognize | song-or-album | song precision | 0.923 (0.667 to 0.986) |  |  |
| recognize | song-or-album | song recall | 0.857 (0.601 to 0.960) |  |  |
| recognize | song-or-album | person precision | 1.000 (0.439 to 1.000) |  |  |
| recognize | song-or-album | person recall | 1.000 (0.439 to 1.000) |  |  |
| recognize | song-or-album | album precision | 1.000 (0.610 to 1.000) |  |  |
| recognize | song-or-album | album recall | 0.857 (0.487 to 0.974) |  |  |
| recognize | short-names | song precision | 1.000 (0.796 to 1.000) |  |  |
| recognize | short-names | song recall | 0.938 (0.717 to 0.989) |  |  |
| recognize | short-names | person precision | 1.000 (0.806 to 1.000) |  |  |
| recognize | short-names | person recall | 1.000 (0.806 to 1.000) |  |  |
| recognize | case | song precision | 0.900 (0.596 to 0.982) |  |  |
| recognize | case | song recall | 0.750 (0.468 to 0.911) |  |  |
| recognize | case | person precision | 1.000 (0.758 to 1.000) |  |  |
| recognize | case | person recall | 1.000 (0.758 to 1.000) |  |  |
| recognize | case | album precision | 0.778 (0.453 to 0.937) |  |  |
| recognize | case | album recall | 0.583 (0.320 to 0.807) |  |  |
| recognize | no-names | no name found | 1.000 (0.722 to 1.000) |  |  |
| recognize | paragraphs | song precision | 0.950 (0.835 to 0.986) |  |  |
| recognize | paragraphs | song recall | 0.950 (0.835 to 0.986) |  |  |
| recognize | paragraphs | person precision | 1.000 (0.898 to 1.000) |  |  |
| recognize | paragraphs | person recall | 1.000 (0.898 to 1.000) |  |  |
| recognize | paragraphs | album precision | 1.000 (0.901 to 1.000) |  |  |
| recognize | paragraphs | album recall | 0.972 (0.858 to 0.995) |  |  |
| recognize | punctuation | song precision | 0.846 (0.578 to 0.957) |  |  |
| recognize | punctuation | song recall | 0.786 (0.524 to 0.924) |  |  |
| recognize | punctuation | person precision | 1.000 (0.439 to 1.000) |  |  |
| recognize | punctuation | person recall | 1.000 (0.439 to 1.000) |  |  |
| recognize | punctuation | album precision | 0.786 (0.524 to 0.924) |  |  |
| recognize | punctuation | album recall | 0.786 (0.524 to 0.924) |  |  |
| recognize | relations | song precision | 0.973 (0.862 to 0.995) |  |  |
| recognize | relations | song recall | 0.900 (0.769 to 0.960) |  |  |
| recognize | relations | person precision | 1.000 (0.886 to 1.000) |  |  |
| recognize | relations | person recall | 1.000 (0.886 to 1.000) |  |  |
| recognize | relations | album precision | 1.000 (0.851 to 1.000) |  |  |
| recognize | relations | album recall | 1.000 (0.851 to 1.000) |  |  |
| recognize | relations | relation edge F1 | 0.854 (0.743 to 0.947) |  |  |
| recognize | relations | relation edge precision | 0.972 (0.858 to 0.995) |  |  |
| recognize | relations | relation edge recall | 0.761 (0.621 to 0.861) |  |  |
| recognize | varied-more | song precision | 0.983 (0.910 to 0.997) |  |  |
| recognize | varied-more | song recall | 0.967 (0.886 to 0.991) |  |  |
| recognize | varied-more | person precision | 1.000 (0.940 to 1.000) |  |  |
| recognize | varied-more | person recall | 1.000 (0.940 to 1.000) |  |  |
| recognize | varied-more | album precision | 0.964 (0.879 to 0.990) |  |  |
| recognize | varied-more | album recall | 0.900 (0.799 to 0.953) |  |  |
| recognize | paragraphs-more | song precision | 0.989 (0.941 to 0.998) |  |  |
| recognize | paragraphs-more | song recall | 0.948 (0.884 to 0.978) |  |  |
| recognize | paragraphs-more | person precision | 0.953 (0.886 to 0.982) |  |  |
| recognize | paragraphs-more | person recall | 0.965 (0.901 to 0.988) |  |  |
| recognize | paragraphs-more | album precision | 0.962 (0.893 to 0.987) |  |  |
| recognize | paragraphs-more | album recall | 0.938 (0.862 to 0.973) |  |  |
| recognize | short-names-more | song precision | 1.000 (0.851 to 1.000) |  |  |
| recognize | short-names-more | song recall | 0.917 (0.742 to 0.977) |  |  |
| recognize | short-names-more | person precision | 1.000 (0.862 to 1.000) |  |  |
| recognize | short-names-more | person recall | 1.000 (0.862 to 1.000) |  |  |
| recognize | case-more | song precision | 1.000 (0.722 to 1.000) |  |  |
| recognize | case-more | song recall | 0.833 (0.552 to 0.953) |  |  |
| recognize | case-more | person precision | 1.000 (0.758 to 1.000) |  |  |
| recognize | case-more | person recall | 1.000 (0.758 to 1.000) |  |  |
| recognize | case-more | album precision | 1.000 (0.758 to 1.000) |  |  |
| recognize | case-more | album recall | 1.000 (0.758 to 1.000) |  |  |
| recognize | punctuation-more | song precision | 0.889 (0.672 to 0.969) |  |  |
| recognize | punctuation-more | song recall | 0.800 (0.584 to 0.919) |  |  |
| recognize | punctuation-more | person precision | 1.000 (0.741 to 1.000) |  |  |
| recognize | punctuation-more | person recall | 1.000 (0.741 to 1.000) |  |  |
| recognize | punctuation-more | album precision | 0.944 (0.742 to 0.990) |  |  |
| recognize | punctuation-more | album recall | 0.895 (0.686 to 0.971) |  |  |
| recognize | relations-more | song precision | 1.000 (0.935 to 1.000) |  |  |
| recognize | relations-more | song recall | 0.917 (0.819 to 0.964) |  |  |
| recognize | relations-more | person precision | 0.978 (0.887 to 0.996) |  |  |
| recognize | relations-more | person recall | 1.000 (0.921 to 1.000) |  |  |
| recognize | relations-more | album precision | 0.935 (0.793 to 0.982) |  |  |
| recognize | relations-more | album recall | 0.879 (0.727 to 0.952) |  |  |
| recognize | relations-more | relation edge F1 | 0.826 (0.720 to 0.906) |  |  |
| recognize | relations-more | relation edge precision | 0.962 (0.870 to 0.989) |  |  |
| recognize | relations-more | relation edge recall | 0.725 (0.610 to 0.816) |  |  |
| relate | song to singer and album | edge F1 | 0.524 (0.488 to 0.563) |  |  |
| relate | song to singer and album | edge precision | 0.418 (0.379 to 0.458) |  |  |
| relate | song to singer and album | edge recall | 0.702 (0.652 to 0.747) |  |  |
| relate | song to singer and album | singer top pick right | 0.734 (0.660 to 0.797) |  |  |
| relate | song to singer and album | album top pick right | 0.516 (0.444 to 0.588) |  |  |
| relate | song to singer and album | duets: pick is a lead | 0.833 (0.552 to 0.953) |  |  |
| relate | solo | edge F1 | 0.701 (0.612 to 0.791) |  |  |
| relate | solo | edge precision | 0.653 (0.538 to 0.752) |  |  |
| relate | solo | edge recall | 0.758 (0.638 to 0.848) |  |  |
| relate | solo | singer top pick right | 0.613 (0.438 to 0.763) |  |  |
| relate | solo | album top pick right | 0.581 (0.408 to 0.736) |  |  |
| relate | solo | tuned cut | 0.490 |  |  |
| relate | solo | edge F1 at the tuned cut, held half | 0.667 |  |  |
| relate | duet | edge F1 | 0.677 (0.594 to 0.750) |  |  |
| relate | duet | edge precision | 0.759 (0.579 to 0.878) |  |  |
| relate | duet | edge recall | 0.611 (0.449 to 0.752) |  |  |
| relate | duet | singer top pick right | 0.917 (0.646 to 0.985) |  |  |
| relate | duet | album top pick right | 0.750 (0.468 to 0.911) |  |  |
| relate | duet | duets: pick is a lead | 0.917 (0.646 to 0.985) |  |  |
| relate | duet | tuned cut | 0.270 |  |  |
| relate | duet | edge F1 at the tuned cut, held half | 0.808 |  |  |
| relate | wrong-album-only | edge F1 | 0.367 (0.246 to 0.474) |  |  |
| relate | wrong-album-only | edge precision | 0.282 (0.190 to 0.395) |  |  |
| relate | wrong-album-only | edge recall | 0.526 (0.373 to 0.675) |  |  |
| relate | wrong-album-only | singer top pick right | 0.742 (0.568 to 0.863) |  |  |
| relate | wrong-album-only | duets: pick is a lead | 0.714 (0.359 to 0.918) |  |  |
| relate | wrong-album-only | tuned cut | 0.440 |  |  |
| relate | wrong-album-only | edge F1 at the tuned cut, held half | 0.414 |  |  |
| relate | links | edge F1 | 0.474 (0.426 to 0.520) |  |  |
| relate | links | edge precision | 0.333 (0.285 to 0.385) |  |  |
| relate | links | edge recall | 0.819 (0.746 to 0.874) |  |  |
| relate | links | composer top pick right | 0.611 (0.510 to 0.702) |  |  |
| relate | links | producer top pick right | 0.442 (0.346 to 0.542) |  |  |
| relate | links | tuned cut | 0.680 |  |  |
| relate | links | edge F1 at the tuned cut, held half | 0.583 |  |  |
| relate | more-solo | edge F1 | 0.693 (0.615 to 0.767) |  |  |
| relate | more-solo | edge precision | 0.653 (0.553 to 0.741) |  |  |
| relate | more-solo | edge recall | 0.738 (0.635 to 0.820) |  |  |
| relate | more-solo | singer top pick right | 0.714 (0.564 to 0.828) |  |  |
| relate | more-solo | album top pick right | 0.714 (0.564 to 0.828) |  |  |
| relate | more-solo | tuned cut | 0.470 |  |  |
| relate | more-solo | edge F1 at the tuned cut, held half | 0.713 |  |  |
| relate | more-duet | edge F1 | 0.552 (0.458 to 0.644) |  |  |
| relate | more-duet | edge precision | 0.615 (0.459 to 0.751) |  |  |
| relate | more-duet | edge recall | 0.500 (0.364 to 0.636) |  |  |
| relate | more-duet | singer top pick right | 0.938 (0.717 to 0.989) |  |  |
| relate | more-duet | album top pick right | 0.750 (0.505 to 0.898) |  |  |
| relate | more-duet | duets: pick is a lead | 0.938 (0.717 to 0.989) |  |  |
| relate | more-duet | tuned cut | 0.350 |  |  |
| relate | more-duet | edge F1 at the tuned cut, held half | 0.741 |  |  |
| relate | more-wrong-album-only | edge F1 | 0.495 (0.370 to 0.614) |  |  |
| relate | more-wrong-album-only | edge precision | 0.375 (0.267 to 0.497) |  |  |
| relate | more-wrong-album-only | edge recall | 0.727 (0.558 to 0.849) |  |  |
| relate | more-wrong-album-only | singer top pick right | 0.742 (0.568 to 0.863) |  |  |
| relate | more-wrong-album-only | duets: pick is a lead | 0.500 (0.095 to 0.905) |  |  |
| relate | more-wrong-album-only | tuned cut | 0.530 |  |  |
| relate | more-wrong-album-only | edge F1 at the tuned cut, held half | 0.455 |  |  |
| relate | more-links | edge F1 | 0.470 (0.425 to 0.515) |  |  |
| relate | more-links | edge precision | 0.329 (0.281 to 0.380) |  |  |
| relate | more-links | edge recall | 0.826 (0.754 to 0.880) |  |  |
| relate | more-links | composer top pick right | 0.600 (0.499 to 0.693) |  |  |
| relate | more-links | producer top pick right | 0.453 (0.356 to 0.553) |  |  |
| relate | more-links | tuned cut | 0.760 |  |  |
| relate | more-links | edge F1 at the tuned cut, held half | 0.524 |  |  |

A `card` test case holds the from-memory case's question and truth, and puts the facts into the record as a short card, one card per song the text names. A `context` case carries the fuller context the question ships with. The measure is the from-memory test's. GLM and Laya have no exact-context or extra-context rows. [questions/README.md](../questions/README.md#the-function-suite) describes the card.

The relate rows come from `results/runs/2026-09-30-all-jev`, under thinkthen main at aec7819bb (the build's SHA-256 is in that run's `run.txt`). They replace the pair planner's first run, `results/runs/2026-09-30-relate-jev` on build c22512868, whose edge F1 was 0.523. The 2026-09-26 run measured relate's old choice planner, at thinkthen main 02dc0b96. ThinkThen ticket 0167 replaced that planner: relate now asks one yes or no question for each pair a rule allows and prints the pairs that reach the bar. On the same entity set, the pair planner's edge recall rose (0.614 to 0.702) and its precision fell hard (0.867 to 0.418) at the 0.5 cut, for an F1 of 0.524 against the old 0.719. The historical rows, from the run of 2026-09-26: edge F1 0.719, edge precision 0.867, edge recall 0.614, singer top pick right 0.899, album top pick right 0.637, duets: pick is a lead 0.917.

A blank cell was not asked. GLM runs through `scripts/run/chat.py suite`. That command asks tag, score, filter, rank, find, and annotate. recognize and relate run through `thinkthen recognize` and `thinkthen relate`. Those commands read a probability for each token or option, and a chat model states one, so GLM skips them. Laya's run of 2026-09-23 asked the older recognize and relate tests, built from annotate. Those tests are gone, so its cells are blank. Laya runs only on a Mac through a local shim and was not asked again.

recognize scores the names `thinkthen recognize song person album` prints, one sentence per call, in named groups. The command's tokenizer splits `.`, `!`, `?`, `,`, `:`, and `;` from the end of each word (thinkthen `specification/recognize.md`, "Names"), so a name may keep or drop such a mark. The scorer trims those marks from the end of both the true name and the name said, and compares the rest exactly.

- `names-template`: the original 48 sentences, one name of each kind in one of four templates. Every song and person name came out right; the ten misses are all album names — nine times "The Beatles (White Album)", which Jev shortens to "White Album" or "The Beatles" or drops, and once "With the Beatles".
- `varied`: the same facts over twelve more templates, with the names in different positions.
- `song-or-album`: each of the seven titles that is both a song and an album, once as each ("the song Help!", "the album Help!").
- `short-names`: a first name or surname alone, such as "Paul" or "Lennon".
- `case`: the names written lower case or all caps. Album recall falls to 0.583.
- `no-names`: sentences with no song, person or album. Jev found none.
- `paragraphs`: four-sentence paragraphs, past the 40-piece window one step-1 request covers.
- `punctuation`: titles with marks inside, such as "Back in the U.S.S.R." and "Ob-La-Di, Ob-La-Da". Album precision and recall and song recall fall to 0.786.
- `relations`: 40 sentences run with `--relation sung_by=song:person --relation appears_on=song:album`, in the same direction as `relate-suite.json`. The edge rows score only the edges the sentence states; six sentences name a song and an album while stating no edge. Jev reads a stated edge at precision 0.972 and recall 0.761.
- `varied-more`, `paragraphs-more`, `short-names-more`, `case-more`, `punctuation-more` and `relations-more`: more sentences of the same kinds, added when the suite grew to its 400 texts.

relate scores the edges `thinkthen relate` prints, one entity set per call. An edge is right when its relation and both endpoint names match a truth edge. relate reads the names from memory alone — the set carries no text, so every edge comes from what the model knows of the names. For relations a text states, the `relations` group under recognize above scores the edges a sentence names. The tests:

- `song to singer and album`: the whole set — 182 songs, the four Beatles, and the 13 core albums — asked at the 0.5 cut in eight requests of at most 96,000 bytes.
- `solo` (16 sets) and `duet` (6): one to three songs sharing a first album, the four Beatles, and three albums, one of them the right one.
- `wrong-album-only` (16): the same shape, but the right album is left out, so the true `appears_on` edge set is empty. relate still names an album for every song, and every album offered is wrong, so no album pick row can be scored.
- `links` (8): about 20 entities each — a dozen songs and the seven people `data/links.tsv` names — scored on the Wikidata `composer` and `producer` pairs, asked as `composed_by` and `produced_by` under `relate-links.json`.
- `more-solo` (20 sets), `more-duet` (7), `more-wrong-album-only` (16) and `more-links` (10): more sets of the same shapes, added when the suite grew to its 100 sets.

The small and links tests ran at a 0.01 cut, so `thinkthen audit` could tune a bar across the whole range. Each such test's `tuned cut` row is the cut a seeded half of its cases tuned for F1, and the held-half rows score the other half at it. The rows, keys, and audit reports sit in the run's `relate-audit/` folder. `song to singer and album` is one case and splits into no halves, so it shows only the 0.5 cut.

Each strict measure for tag, annotate's singer, and relate has a top pick row beside it. For tag and annotate, the row counts the songs whose likeliest singer is a true lead. A tie at the top earns the share of its singers that are true. An extra singer the strict measure counts wrong does not cost the song. For relate, the pick is the pair with the top probability for each song and relation; under the old planner it was the planner's own pick, and a pick of none was wrong. The full table in `results/tables/` also keeps the older rows "top label right, single-lead songs". They give a tie at the top to the first singer in the list.

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

Before the merge, Jev's main runs cost 0.037 dollars and GLM's 0.14 dollars at Z.ai's price. The function suites then sent 1,776 Jev requests (0.040 dollars) and 87 more after the settled-lead rule (0.0011 dollars), 1,157 GLM requests (0.060 dollars, median 3.5 s), and 1,028 Laya requests at no charge. Each run folder holds its usage. A rerun answers every unchanged question from the recording. `results/history.tsv` gets one dated row per run and per function measure. The fresh Jev runs of 2026-09-25 sent 6,191,593 input tokens in all, about 0.26 dollars (ticket 0009 record). Those of 2026-09-26 sent 6,057,783, about 0.25 dollars (ticket 0014 record). The recognize run of 2026-09-30 sent 354 requests and 687,702 input tokens, about 0.03 dollars (ticket 0018 record). The reading run of 2026-09-30 sent 1,004 requests and 558,621 input tokens, about 0.02 dollars (ticket 0020 record).

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
