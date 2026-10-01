# examples

One folder for each slide of the ThinkThen talk that shows bench data. Each folder names the slide's claims, their sources, the test that checks them, and the thinkthen build that made its answers. The table follows the talk's order. The numbers are the talk's on 2026-09-26, and the talk renumbers its slides when one joins. The folder names carry no number.

Twelve folders hold a function example: its cases, its recording, its answers, and `./run`. `./run.sh` replays them in this order, with `diff` after `audit`. The other ten folders hold a `README.md` only. Their sources live elsewhere in the bench. "The deck holds it" marks a slide that shows a run the talk recorded itself.

| # | Slide | What it shows | Folder | Sources | Check | Build |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | title | A prism: ten functions, each with one recorded input and output | the deck holds it | the deck's own recordings | the deck | the deck |
| 2 | strings | Three strings against the things they name, with the chance and vector search shares | [strings/](strings/) | `data/songs.tsv`, `reports/results.md` | `test_published_numbers.py` | no model call |
| 3 | jev | One choose answer from Jev, its time, and its price | [jev/](jev/) | `choose/outputs.jsonl`, `results/tables/cost.tsv`, the 2026-09-30 all-jev run's `loadavg.txt`, `scripts/score/prices.tsv` | `test_published_numbers.py`, `./run.sh` | `choose/run.txt`, the 2026-09-30 all-jev run's `run.txt` |
| 4 | bench | Six rows of the song table and the bench's size | [bench/](bench/) | `data/songs.tsv`, `data/albums.tsv`, `questions/` | `test_published_numbers.py` | no model call |
| 5 | runs-in | One function run in a terminal, and the surfaces ThinkThen runs on | the deck holds it | the deck's own run | the deck | the deck |
| 6 | decide | Four yes or no answers and a bar | [decide/](decide/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `decide/run.txt` |
| 7 | choose | Pick one singer | [choose/](choose/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `choose/run.txt` |
| 8 | tag | Every label that fits | [tag/](tag/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `tag/run.txt` |
| 9 | score | A level for each song | [score/](score/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `score/run.txt` |
| 10 | filter | Keep the songs that clear a bar | [filter/](filter/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `filter/run.txt` |
| 11 | filter-live | The filter slide's command run live | the deck holds it | the deck's recorded terminal session | the deck | the deck |
| 12 | rank | Order songs by a question | [rank/](rank/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `rank/run.txt` |
| 13 | find | Pull a value out of text | [find/](find/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `find/run.txt` |
| 14 | annotate | Fill a form from text | [annotate/](annotate/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `annotate/run.txt` |
| 15 | recognize | Names and their kinds in one sentence | [recognize/](recognize/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `recognize/run.txt` |
| 16 | recognize-how | The recognize sentence word by word | [recognize-how/](recognize-how/) | `recognize/recording`, replayed with `--details` | `test_examples.py`, `RecognizeHowTest` | `recognize/run.txt` |
| 17 | relate | How the names connect | [relate/](relate/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `relate/run.txt` |
| 18 | audit | Accuracy and calibration of a run | [audit/](audit/) | the folder's cases and `recording/` | `test_examples.py`, `./run.sh` | `audit/run.txt` |
| 19 | diff | The answers that changed between two runs | [diff/](diff/) | `audit/` rows | `test_examples.py`, `./run.sh` | `audit/run.txt`; `diff` calls no model |
| 20 | scripting | Code in each scripting language | no bench data | none | none | none |
| 21 | systems | Code in each systems language | no bench data | none | none | none |
| 22 | sql | One SQL query with a band, and its 1, 0, and NULL answers | [sql/](sql/) | `filter/outputs.jsonl` | `test_published_numbers.py` | `filter/run.txt` |
| 23 | frames | Code in each data frame language | no bench data | none | none | none |
| 24 | what-jev-knows | Four bars: chance, vector search, Jev, and a big chat model | [what-jev-knows/](what-jev-knows/) | `results/tables/accuracy.tsv`, `reports/results.md` | `test_published_numbers.py` | the 2026-09-30 all-jev run's `run.txt`; GLM build not recorded |
| 25 | catches | Three weak spots, each with one question Jev missed | [catches/](catches/) | the 2026-09-30 all-jev run's `answers.jsonl`, `results/tables/popularity.tsv`, `controls.tsv`, `composition.tsv` | `test_published_numbers.py` | the 2026-09-30 all-jev run's `run.txt` |
| 26 | open-book | From memory against the song catalog in the text | [open-book/](open-book/) | `reports/open-book.md`, the 2026-09-26 Jev and open-book runs | `test_published_numbers.py` | both runs' `run.txt` |
| 27 | know-this | The price, the cache, batching, and caps | [know-this/](know-this/) | `results/tables/cost.tsv`, `scripts/score/prices.tsv`; batching has no bench source | `test_published_numbers.py` | the 2026-09-30 all-jev run's `run.txt`; batching build not recorded |
| 28 | bench-run | Three facts and the steps to run the bench | [bench-run/](bench-run/) | `results/tables/cost.tsv`, the 2026-09-30 all-jev run's `loadavg.txt`, the README's "Run it" | `test_published_numbers.py` | the 2026-09-30 all-jev run's `run.txt`; GLM build not recorded |
| 29 | backends | A `thinkthen check` run against a server | the deck holds it | the deck's saved output | the deck | the deck |
| 30 | close | The speaker and the ThinkThen links | no bench data | none | none | none |

Paths in the Sources, Check, and Build columns start at this folder, `tests/`, or the top of the bench.
