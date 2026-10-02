# Datasheet for Beatles Bench

The questions follow Gebru et al., "Datasheets for Datasets" (arXiv 1803.09010). The answers describe the question set in `questions/` and the tables in `data/` as generated on 2026-09-23.

## Motivation

- **Purpose.** The bench measures what a system knows about the thing a short string names. A song title does not hold its singer, album, or date, so string search and vector search over the title alone can only match the look of the words. The bench also measures where that knowledge fails (direction, two chained facts, popularity) and whether a system's probabilities mean what they say.
- **Who made it.** Ian Maurer, with coding agents. The author builds ThinkThen, the command every Jev question passes through, and ThinkThen builds on Jev, the first model measured. A reader should weigh the Jev results with that in mind.
- **Funding.** No grant. Model calls were paid from the author's accounts.

## Composition

- **Instances.** 1,501 questions in 15 categories, each one JSON line with `id`, `category`, `kind`, `function` (`choose` or `decide`), `question`, `input`, `options`, `truth`, and `fields`. Some carry `group` (a lead-set song, or the question a control mirrors) or `hops` (the single-hop questions behind a multi-hop question). [questions/README.md](../questions/README.md) lists the categories.
- **What an instance is.** A multiple-choice or yes/no question about a Beatles song, album, or dated event, or, in the two reversal-general categories, about a pair outside the Beatles (actors and parents, films and composers, buildings and architects, inventions and inventors, songs and writers).
- **Sample or whole.** The songs are every released song in Wikipedia's "List of songs recorded by the Beatles" (306). Each category draws from them with a seeded random draw, so a category is a sample. The draws and their sizes are in `scripts/generate/generate.py`.
- **Labels.** Every truth label comes from a script over the harvested tables. No person and no model chose an answer. People and coding agents wrote the question templates, the category rules, the album list, the stop words, the event rule, and the fame ratio. Some rules changed after scores were seen: the event rule twice, the surname rule once, and on 2026-09-23 the fixes listed in [reports/results.md](../reports/results.md#audit-history-fixes-on-2026-09-23). An audit of wrong answers then led to three more changes: the lead questions ask only songs whose own article agrees with the list on the lead singers, the album questions ask for the first album, and `data/pins/excluded.tsv` drops three ambiguous items. The exclusion list removes items and never sets an answer. [`results/archive/2026-09-23-seed/`](https://github.com/botassembly/beatles-bench/tree/a6a6be71/results/archive/2026-09-23-seed) keeps the runs over the seed set.
- **Balance.** Yes/no sets hold equal yes and no. Before/after holds equal before and after. The right letter of every lettered question is spread evenly over the letters within its category and kind. Forward singer draws up to 15 songs per Beatle, so the class balance is set by design, not by how often each Beatle sang lead.
- **Errors and noise.** The truth is Wikipedia's and Wikidata's at the pinned revisions. The known limits in [README.md](README.md#known-limits) list what is left: loose Wikidata classes, US or UK dates, weak lexical traps, recognition with random distractors in reversal-general.
- **Self-contained.** The tables and questions are in the repository. The page cache (`data/raw/`) and the embedding cache of the baselines (`cache/`) are not committed. The pins name every revision, so the harvest can refill the pages.
- **Confidential or offensive content.** None. The questions name public songs, public figures, and historical events, some of them violent (assassinations, disasters).
- **People.** The questions name musicians, actors and their parents, architects, composers, and inventors, all with Wikipedia articles. No private person is named on purpose. The parent pairs are public in Wikidata.

## Collection

- **How.** `scripts/harvest/harvest.py` reads Wikipedia pages at pinned revisions, the Wikimedia Pageviews API for 2024, and Wikidata through its query service and API. `data/pins/` holds every revision, redirect, view count, and Wikidata answer, so an offline rebuild gives the same bytes. `data/SOURCES.md` states every rule.
- **When.** The pages are the revisions current on 2026-09-23. The page views cover 2024-01-01 to 2024-12-31.
- **Who.** Scripts. No crowd work and no annotation.
- **Consent.** Not applicable: the sources are public encyclopedic data.

## Preprocessing

- The harvest keeps released songs, joins a Wikidata fact to a song only through the song's own article (exact title), reconciles Wikidata composers with the published songwriting credit, dates each song by its first release anywhere, and keeps only discrete events that Wikidata dates to one day of a month.
- The raw pages stay in the local cache and are never published. No Wikipedia sentence and no lyric is stored in the repository.

## Uses

- **Intended.** Comparing systems on entity knowledge, calibration, coverage at a cut, cost, and time, on the same replayable questions.
- **Not intended.** A general measure of language-model knowledge: one catalog, a few thousand questions, and multiple choice. A claim about free recall: the reversal categories are recognition.
- **Contamination.** The facts and the pages are on the public web, and so will this repository be. A model trained after 2026-09-23 may have seen the questions.

## Distribution

- Code: MIT (`LICENSE`). Data (`data/`, `data/pins/`, `questions/`, `results/`): CC BY-SA 4.0 with the attribution in `data/LICENSE`, because they are compiled from Wikipedia. Wikidata facts are CC0.
- The recordings hold model outputs from the vendors' APIs. Their terms govern any reuse beyond reproducing these results.

## Maintenance

- The author maintains the repository. A rerun adds a dated row to `results/history.tsv` with accuracy, time per answer, and cost per 1,000 questions, so drift in a model shows over time. A change to the truth changes the pins and the question files, and git keeps every version.
