# Beatles Bench

A benchmark of what a small, fast model knows about Beatles songs, and how well it reads when you hand it the facts.

## What it is

- [ThinkThen](https://thinkthen.dev) gives code ten functions that answer a question about text with a probability: `decide`, `choose`, `tag`, `score`, `filter`, `rank`, `find`, `annotate`, `recognize`, and `relate`. Each function is one command over plain files.
- ThinkThen runs on Jev, a small one-step model from TypeSafe. The author of this bench builds ThinkThen. Weigh the Jev results with that in mind.
- A small, fast model stores the broad facts it read and loses the fine detail: an exact year, a first album, a shared lead vocal. The same model reads well. So the bench asks two things. How much does Jev know from memory? How well does it do with the facts handed over?
- The questions cover lead singers, first albums, songwriters, release dates, song lengths, and dated world events. 1,313 questions sit across 13 Beatles categories, and 188 more ask about famous pairs outside the Beatles. Traps and controls add options that share a word with the question, albums released next to the right one, "none of these", and questions asked in both directions.
- Every function has its own test: tag the lead singers, score and rank songs, filter by singer or album, find an album, annotate a song card, recognize names in a sentence, and relate songs to singers and albums.
- A script sets every question and every right answer from harvested Wikipedia and Wikidata tables. No person and no language model chose an answer.

## Results

Jev and four other kinds of system answer the same 1,313 Beatles questions. The Jev and Liquid d1 rows come from the all-runs of 2026-09-30. The other rows come from the runs of 2026-09-23.

- String search compares the question with each option and picks the closest. It knows no facts. Vector search did no better, even with the relation named in the query ([reports/baselines.md](reports/baselines.md)).
- GLM-5.3 Flash is a large chat model from Z.ai. It answers from memory, with thinking off and no search tool.
- Laya is a small Jev-like model, run locally on a Mac.
- Liquid d1 (`d1:free`) is a small model from Liquid AI on the same System One wire, asked through `thinkthen --backend liquid`.

| System | Beatles questions right | Median time per answer | Dollars per 1,000 answers |
| --- | --- | --- | --- |
| String search (BM25) | 33.8% | no model call | 0 |
| Laya, from memory | 35.0% | 0.07 s (build and load not recorded) | 0 (local) |
| Jev, from memory | 67.4% | 0.20 s (load average 6.74 to 11.18 on 16 cores) | 0.016 |
| Liquid d1, from memory | 64.3% | 0.31 s (load average 11.15 to 15.15 on 16 cores) | 0 (d1:free billed nothing) |
| GLM-5.3 Flash, from memory | 96.2% | 8.24 s (build and load not recorded) | 0.056 |

A uniform guess gets 31.4%. Jev's time comes from `results/runs/2026-09-30-all-jev`, and Liquid d1's from `results/runs/2026-09-30-all-liquid-d1`; each folder's `loadavg.txt` records the load.

- Search sits near chance. Matching words cannot tell which album a song came out on.
- Jev from memory gets about two in three. It knows a lot and misses fine detail. Its misses are near misses: one year off, a sibling album.
- GLM-5.3 Flash from memory gets 96%. A large chat model has read the pages the answers come from. It takes about 8 seconds per answer.
- Jev with the facts handed over reads nearly as well as the large model remembers. On 196 sampled questions, drawn mostly from its misses, it got 68 (35%) from memory and 184 (94%) with the 306-song catalog in the text, in the open-book run of 2026-09-26 ([reports/open-book.md](reports/open-book.md)).

[reports/results.md](reports/results.md) has every category, the intervals, the tests, and the costs.

## Run it

Install the `thinkthen` command first. `./run.sh` needs thinkthen 0.1.0, the current checkpoint: the example folders hold question-store recordings it replays, and it ships `audit` and `diff`. The runs under `results/` keep the form their builds wrote: `results/builds.tsv` names each run's build, and a run replays only when `BENCH_BIN_<id>` names that build's command. `BENCH_BIN_02dc0b96` covers the runs through 2026-09-26. `BENCH_BIN_c22512868` covers the recognize, relate, and reading runs of 2026-09-30. `BENCH_BIN_aec7819bb` covers the all-runs of 2026-09-30. Each run's `run.txt` names the SHA-256. Two examples keep their first recordings: `thinkthen` 0.1.0's recognize and relate ask different questions than the recorded ones, so `examples/recognize` and `examples/relate` replay under `BENCH_BIN_02dc0b96` too. Then:

```sh
git clone https://github.com/botassembly/beatles-bench
cd beatles-bench
./run.sh
```

With no backend address set, `./run.sh` replays the converted folders in `examples/` under `thinkthen`. Three recordings keep the old form: the newest committed run and the `recognize` and `relate` examples. `./run.sh` replays each of them when `BENCH_BIN_<id>` names its build. Otherwise it prints one line naming the build and skips it. It needs no key, no network, and no spend. It checks every replayed answer and example file against the committed ones, byte for byte. A replay holds only under the build that made the recording: another build can replay every answer and still change an output's bytes. It then rescores every run into `results/tables/` and prints the results tables.

To ask your own backend:

```sh
export THINKTHEN_BASE_URL=https://your-server/v1
export THINKTHEN_API_KEY=...
./run.sh my-rerun
```

`./run.sh NAME` names the folders. The answers go to `results/runs/<today>-thinkthen-NAME`, and the tables then include your run. `./run.sh` then asks each function folder's cases into `results/runs/<today>-examples-NAME/<function>/`. The examples add about 90,000 input tokens, as in the example run of 2026-09-25. NAME defaults to `jev`. `BEATLES_BENCH_MODEL` sets the model name each request carries. A live run with it set must name the run. Run the same command again the same day to resume a stopped run. A live run never writes into a folder git tracks. Outside a git checkout, such as a ZIP download, it stops when its folder already holds files. `BENCH_MAX_INPUT_TOKENS` caps the input tokens of each step on its own.

`./run.sh NAME` with no address replays that run the same way. It sends the base URL and model the live run saved in `backend.txt`, never a key.

Each function folder in `examples/` also runs by hand. `./run` in the folder answers its question from the recording with no key. [scripts/README.md](scripts/README.md) covers every stage from harvest to figures. [tests/README.md](tests/README.md) says how to run the tests.

## What's new

- 2026-09-30: Five models answered the same 1,501 knowledge questions; [reports/models.md](reports/models.md) is the citable report, with the hard and easy split and the paired tests.
- 2026-09-30: Every card-answerable function gained a reading test: the same questions with the facts written into the record as a short card. [reports/results.md](reports/results.md) opens with a by-function table of memory beside reading.
- 2026-09-26: The function folders moved to `examples/`, and each slide of the ThinkThen talk that shows bench data has a folder there. The function suite moved to `questions/suite/`.
- 2026-09-26: The walkthroughs moved to the website. Superseded runs moved to `results/archive/runs/`. `./run.sh NAME` names and replays a run of any backend.
- 2026-09-26: Every Jev run was asked again from an empty recording. `recognize` and `relate` are scored from the shipped commands, and the function table gained top pick rows.
- 2026-09-25: Each function has its own folder in `examples/`, with its slide, its cases, and its recording.
- 2026-09-24: `audit` and `diff` landed on thinkthen main. They grade a run and compare two runs with no model call.
- 2026-09-23: The audited 1,501 questions, with the GLM-5.3 Flash, Laya, and search runs.

## Learn more

The website's Beatles Bench section walks through each function and the open-book run: [thinkthen.dev/learn/beatles-bench](https://thinkthen.dev/learn/beatles-bench/).

- [reports/results.md](reports/results.md): the full results.
- [reports/models.md](reports/models.md): the five-model table on the knowledge questions, with intervals, the hard and easy split, and the paired tests — the page to cite.
- [reports/baselines.md](reports/baselines.md): the search baselines.
- [reports/open-book.md](reports/open-book.md): Jev with the catalog in hand, and what context costs.
- [reports/rad.md](reports/rad.md): Jev picks the catalog sections it reads.
- [reports/leaning-no.md](reports/leaning-no.md): Jev leans toward "no" on yes/no questions, and `audit` tunes a cut that fixes it with no new calls.

## Repository map

- [data/](data/README.md): the harvested tables, the pins, the sources, and the licenses.
- [questions/](questions/README.md): the benchmark itself, one file per category, plus the function suite.
- [examples/](examples/README.md): one folder for each slide of the ThinkThen talk that shows bench data, indexed in the talk's order. Twelve hold a function example: [decide](examples/decide/), [choose](examples/choose/), [tag](examples/tag/), [score](examples/score/), [filter](examples/filter/), [rank](examples/rank/), [find](examples/find/), [annotate](examples/annotate/), [recognize](examples/recognize/), [relate](examples/relate/), [audit](examples/audit/), and [diff](examples/diff/).
- [scripts/](scripts/README.md): all the code, by stage: harvest, generate, run, score, and figures.
- [results/](results/README.md): every run with its recording, the scored tables, and the archive. [results/runs/README.md](results/runs/README.md) explains the run names.
- [reports/](reports/README.md): the write-ups and the figures.
- [paper/](paper/README.md): notes toward the paper.
- [tests/](tests/README.md): the test suite. It needs no network.
- [sdlc/](sdlc/README.md): the tickets, records, and issues behind every change.

## Data and licenses

- 306 Beatles songs, 20 albums, 100 months of dated world events, 142 Beatles pairs, and 254 pairs outside the Beatles.
- Harvested from English Wikipedia at pinned revisions, Wikidata, and the Wikimedia Pageviews API for 2024. Every input is pinned. An offline rebuild gives the same bytes.
- The code is MIT. The data and questions are CC BY-SA 4.0, because they come from Wikipedia. Wikidata facts are CC0. No Wikipedia sentence and no lyric is committed.

[data/README.md](data/README.md) describes each file, its source, and its known limits.
