# Beatles Bench

A benchmark of what a small, fast model knows about Beatles songs, and how well it reads when you hand it the facts.

## The capability

- [ThinkThen](https://thinkthen.dev) gives code ten functions that answer a question about text with a probability: `decide`, `choose`, `tag`, `score`, `filter`, `rank`, `find`, `annotate`, `recognize`, and `relate`.
- Each function is one command over plain files. A program calls it the way it calls any other function.
- ThinkThen runs on Jev, a small one-step model from TypeSafe.
- The author of this bench builds ThinkThen. Weigh the Jev results with that in mind.

## The theory

- A small, fast model stores a lot of what it read. It stores the broad facts and loses the fine detail: an exact year, a first album, a shared lead vocal.
- The same model reads well. Put the facts in the text, and it finds the answer fast.
- So the bench asks two things. How much does Jev know from memory? How well does it do with the facts handed over?

## What the bench tests

- Beatles facts from memory: lead singers, first albums, songwriters, release dates, song lengths, and dated world events. 1,313 questions across 13 Beatles categories, plus 188 questions about famous pairs outside the Beatles.
- Traps and controls: options that share a word with the question, albums released next to the right one, "none of these", and questions asked in both directions.
- All ten functions, each on its own test: tag the lead singers, score and rank songs, filter by singer or album, find an album, annotate a song card, recognize names in a sentence, and relate songs to singers and albums.
- Open book: the same questions with a 306-song catalog pasted before each one.
- A script sets every question and every right answer from harvested Wikipedia and Wikidata tables. No person and no language model chose an answer.

## How it compares

Jev and three other kinds of system answer the same Beatles questions.

- String search compares the question with each option and picks the closest. It knows no facts. Vector search did no better, even with the relation named in the query ([reports/baselines.md](reports/baselines.md)).
- GLM-5.3 Flash is a large chat model from Z.ai. It answers from memory, with thinking off and no search tool.
- Laya is a small Jev-like model, run locally on a Mac.

| System | Beatles questions right | Median time per answer | Dollars per 1,000 answers |
| --- | --- | --- | --- |
| String search (BM25) | 33.8% | no model call | 0 |
| Laya, from memory | 35.0% | 0.07 s | 0 (local) |
| Jev, from memory | 67.0% | 0.21 s | 0.015 |
| GLM-5.3 Flash, from memory | 96.2% | 8.24 s | 0.056 |

A uniform guess gets 31.4%. The Jev time comes from `results/runs/2026-09-26-thinkthen-jev`. Its `loadavg.txt` records a load average of 3.83 at the start and 7.10 at the end, on 16 cores. The GLM-5.3 Flash and Laya times come from runs of 2026-09-23. Those runs recorded no load.

Open book: with the catalog in hand, Jev got 187 of 196 sampled questions right on 2026-09-23. From memory it got 62 of the same 196 on that date. The fresh run of 2026-09-26 got 184 with the catalog and 68 from memory. The 2026-09-23 run weighs back to the 1,075 questions the catalog covers. On those questions Jev moves from 68% from memory to about 97% with the catalog. The fresh run has no weighted figure. An open-book pass costs 0.51 dollars per 1,000 answers in both runs. The 2026-09-23 run had a median of 0.54 s per call on a machine at a load average near 400. The 2026-09-26 run had a median of 0.28 s at a load average near 6.

[reports/results.md](reports/results.md) has every category, the intervals, the tests, and the costs.

## The takeaways

The ladder, from the least knowledge to the most:

1. Search sits near chance. Matching words cannot tell which album a song came out on.
2. Jev from memory gets about two in three. It knows a lot and misses fine detail. Its misses are near misses: one year off, a sibling album.
3. GLM-5.3 Flash from memory gets 96%. A large chat model has read the pages the answers come from. It takes about 8 seconds per answer.
4. Jev with the facts handed over gets 184 of the 196 sampled questions right, or 94%, in the fresh run of 2026-09-26. From memory it got 68 of the same 196, or 35%. It reads nearly as well as the large model remembers.

The building blocks:

- Every bench question, every function test, and the open-book run is one plain command over plain files.
- `audit` grades a finished run: accuracy, calibration, and a cut tuned on one half and checked on the other. `diff` lists the answers that changed between two runs and tests whether the change is beyond noise. Neither calls a model.
- `audit` and `diff` reproduce the leaning-no report exactly. Jev leans toward "no" on yes/no questions. A cut of 0.42, tuned on one half, roughly doubled the true "yes" answers caught, from 31% to 61%, with no new calls ([reports/leaning-no.md](reports/leaning-no.md)).
- `audit` and `diff` are ThinkThen commands. They landed on thinkthen main on 2026-09-24. No release carries them yet.

## The data

- 306 Beatles songs, 20 albums, 100 months of dated world events, 142 Beatles pairs, and 254 pairs outside the Beatles.
- Harvested from English Wikipedia at pinned revisions, Wikidata, and the Wikimedia Pageviews API for 2024. Every input is pinned. An offline rebuild gives the same bytes.
- Licenses: the code is MIT. The data and questions are CC BY-SA 4.0, because they come from Wikipedia. Wikidata facts are CC0. No Wikipedia sentence and no lyric is committed.

[data/README.md](data/README.md) describes each file, its source, and its known limits.

## Run it yourself

Install the `thinkthen` command first. `./run.sh` needs a build with `audit`: thinkthen main at 02dc0b96 or later, until a release carries it. Then:

```sh
git clone https://github.com/botassembly/beatles-bench
cd beatles-bench
./run.sh
```

With no backend address set, `./run.sh` replays the newest recorded Jev run and every function folder in `functions/`. It needs no key, no network, and no spend. It checks every replayed answer and example file against the committed ones, byte for byte. It then rescores every run into `results/tables/` and prints the results tables.

To ask your own backend:

```sh
export THINKTHEN_BASE_URL=https://your-server/v1
export THINKTHEN_API_KEY=...
./run.sh
```

The answers go to `results/runs/<today>-<name>`, and the tables then include your run. `./run.sh` then asks each function folder's cases into `results/runs/<today>-examples-<name>/<function>/`. The examples add about 90,000 input tokens to the run. `./run.sh NAME` names the folders. Run `./run.sh` again the same day to resume a stopped run. `BENCH_MAX_INPUT_TOKENS` caps the input tokens of each step on its own: the 1,501 questions, then each example. No budget passes from one step to the next. Add a line to `scripts/score/prices.tsv` for your model's cost. Until then its cost cell stays blank.

`BEATLES_BENCH_MODEL` sets the model name each request carries. It defaults to `jev-latest`. The name matters only when one server offers several models or versions. A server with one model can ignore it.

## One function at a time

The talk shows one slide per function. Each has its own folder: [decide](functions/decide/), [choose](functions/choose/), [tag](functions/tag/), [score](functions/score/), [filter](functions/filter/), [rank](functions/rank/), [find](functions/find/), [annotate](functions/annotate/), [recognize](functions/recognize/), [relate](functions/relate/), [audit](functions/audit/), and [diff](functions/diff/).

A folder holds a short README with the slide and its lessons, one `run` script, and the example's data: the cases, the recorded answers, and the recording. `run` needs `thinkthen` and `jq`. Run it in the folder:

- `./run` answers the slide's question from the recording. It needs no key and no network.
- `./run threshold 0.7` reads the same answers at another bar. `decide`, `audit`, and `diff` also take a band such as `0.3:0.7`.
- `./run live` asks the server in `THINKTHEN_BASE_URL`, with no cache. `thinkthen` reads `THINKTHEN_API_KEY` itself. Live answers can differ by a few points from the recording.

[docs/walkthroughs/](docs/README.md) has a longer page per function. Each shows how its cases were built, what they assume, and why each answer is right or wrong.

[How to run the bench for free](docs/run-it-for-free.md) walks through one example by hand. `python3 -m unittest discover -s tests` runs the tests. Set `THINKTHEN_BIN` to include the replays. [scripts/README.md](scripts/README.md) covers every stage from harvest to figures, the GLM and Laya replays, and each step `./run.sh` runs.

## Map of the repository

- [data/](data/README.md): the harvested tables, the pins, the sources, and the licenses.
- [questions/](questions/README.md): the benchmark itself, one file per category, plus the function suite.
- [functions/](#one-function-at-a-time): one folder per function, as the ThinkThen talk shows it. `audit` grades 70 saved answers and suggests a bar. `diff` shows what changes when the answers get context.
- [docs/](docs/README.md): the walkthroughs in reading order, and how context changes the answers. [docs/context-article.md](docs/context-article.md) hands Jev a whole Wikipedia article.
- [scripts/](scripts/README.md): all the code, by stage: harvest, generate, run, score, and figures.
- [results/](results/README.md): every run with its recording, and the scored tables.
- [reports/](reports/README.md): the write-ups and the figures.
- [paper/](paper/notes.md): notes toward the paper.
- `tests/`: the test suite. It needs no network.

Reports:

- [reports/results.md](reports/results.md): the full results.
- [reports/baselines.md](reports/baselines.md): the search baselines.
- [reports/open-book.md](reports/open-book.md): Jev with the catalog in hand.
- [reports/rad.md](reports/rad.md): Jev picks the catalog sections it reads.
- [reports/leaning-no.md](reports/leaning-no.md): the lean toward "no" and how a tuned cut fixes it.
