# Scripts

All the code, one folder per stage. The pipeline runs in this order: harvest, generate, run, score, figures. Run every command from the repository root.

| Folder | Stage | Main scripts |
| --- | --- | --- |
| `harvest/` | Fetch pinned Wikipedia pages, page views, and Wikidata answers, then write `data/`. | `harvest.py`, `wikitext.py`, and the Wikidata queries (`*.rq`, `reversal/`) |
| `generate/` | Turn `data/` into `questions/`, `questions/suite/`, and the cases in `examples/`. | `generate.py`, `make_suite.py`, `examples.py` |
| `run/` | Ask every question and record each exchange in `results/runs/RUN/`. | `thinkthen.sh` (wraps `ask.py`), `ask_suite.sh`, `example.sh`, `rad_pipeline.sh`, `chat.py`, `baselines.py`, `relation_vectors.py`, `catalog.py`, `rad.py`, `gaps.py`, `model_time.py`, `in_text_check.py` |
| `score/` | Score the runs into `results/tables/` and `results/history.tsv`. | `analyze.py`, `score_suite.py`, `relate_audit.py`, `table.py`, `score.py`, `stats.py`, `open_book.py`, `rad_table.py`, `prices.tsv`, `tune.sh`, `context_diff.sh`, `diff_guard.sh`, `context.jq` |
| `answers/` | Write `results/answers.jsonl` (one row per case per committed run) and report from it into `reports/generated/` and `results/by-question.jsonl`. | `build.py`, `report.py`, `queries/` |
| `figures/` | Draw `reports/figures/` from `results/tables/` with kuva. | `all.sh`, `common.py`, one numbered script per figure |

## Set up

Python 3.12. The harvest, the generators, the scoring, and the Jev replays need only the standard library, `jq`, and the `thinkthen` command. The chat backend, the embedding baselines, and the figures need a venv: `uv venv .venv && uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple --index-strategy unsafe-best-match -r requirements.txt`, plus `kuva` and `Pillow`. The CPU index keeps torch small.

## Replay

`./run.sh` at the repository root replays the newest `results/runs/DATE-thinkthen-jev` with no key and compares `replay/answers.jsonl` with the committed answers — only when `BENCH_BIN_<id>` names the build `results/builds.tsv` gives the run, else it prints a skip line. It then replays every folder in `examples/` under `THINKTHEN_BIN` and compares each replayed file with the committed one; a folder whose recording is not a question store replays under its `run.txt` build's `BENCH_BIN_<id>` or skips the same way. Last, it runs `analyze.py` and `table.py`. `./run.sh NAME` replays the newest `DATE-thinkthen-NAME` and the newest `DATE-examples-NAME` instead.

A replay writes `RUN/replay/` and leaves the committed files alone. It passes `--replay RUN/recording` with no key, so the command answers from the recording alone and stops on any request the recording lacks. A committed recording replays only under the build that made it — `results/builds.tsv` names it and `BENCH_BIN_<id>` hands it over. Each step also runs on its own with `THINKTHEN_BIN` set to that build's command:

```sh
env -u THINKTHEN_API_KEY scripts/run/thinkthen.sh replay "$(python3 scripts/score/score.py newest thinkthen-jev)"
# the function suite grew after the run: BENCH_SUITE_ONLY names the case-id prefixes it recorded (or the new groups'
# prefixes for results/runs/2026-09-30-recognize-jev, 2026-09-30-relate-jev and 2026-09-30-reading-jev)
env -u THINKTHEN_API_KEY BENCH_SUITE_ONLY="tag-lead-,score-popularity-,filter-singer-,filter-album-,rank-popularity-,rank-date-,find-album-0,find-album-1,annotate-card-,relate-songs,recognize-0,recognize-1,recognize-2,recognize-3,recognize-4" \
  scripts/run/ask_suite.sh replay "$(python3 scripts/score/score.py newest functions-jev)"
env -u THINKTHEN_API_KEY scripts/run/example.sh decide replay        # examples/decide/replay/
env -u ZAI_API_KEY .venv/bin/python scripts/run/chat.py replay results/runs/2026-09-23-glm-5.3-flash
python3 scripts/score/analyze.py                      # results/tables/
python3 scripts/score/table.py                        # the results tables
python3 scripts/answers/build.py                      # results/answers.jsonl
python3 scripts/answers/report.py                     # reports/generated/, results/by-question.jsonl
```

`scripts/run/example.sh NAME replay [OUT] [FROM]` replays one function folder. The cases come from `examples/NAME/`. The recording comes from FROM, a run folder, or else from the folder's own `recording/`. The replay writes to OUT, by default the folder's `replay/`. For `audit`, `example.sh` then runs `score/tune.sh` for the audit files. `score/context_diff.sh [IN [OUT]]` runs `diff` on the audit rows in `IN`, by default `examples/audit`.

The open-book and section-picking runs replay the same way. [reports/open-book.md](../reports/open-book.md) and [reports/rad.md](../reports/rad.md) give the commands that print their tables. The Laya runs replay with no Mac: `tests/test_replay_laya.py` replays them from their recordings.

Code finds a dated run by its label: `python3 scripts/score/score.py newest LABEL` prints the newest `results/runs/DATE-LABEL` folder. `analyze.py` scores the newest run of each label. [results/runs/README.md](../results/runs/README.md) lists the labels.

## Rerun

With `THINKTHEN_BASE_URL` set, `./run.sh [NAME]` asks that backend into `results/runs/<today>-thinkthen-NAME` in place of the replay. It then asks each function folder's cases into `results/runs/<today>-examples-NAME/<function>/`. NAME defaults to `jev`. `BEATLES_BENCH_MODEL` sets the model, and a live run with it set must name the run. The run writes `backend.txt` into both folders: the base URL and the model, never the key. `./run.sh NAME` with no address replays both folders with that base URL and model.

A live run stops with exit 2 when its folders hold a file git tracks, so it never writes into a committed run. Outside a git checkout, such as a ZIP download, it stops when a folder already holds files. `BENCH_MAX_INPUT_TOKENS` caps each step on its own, and `BENCH_WORKERS` sets the calls in flight.

Only the `thinkthen` command reads `THINKTHEN_API_KEY`, and a recording holds request and response bodies, never headers. A rerun answers unchanged questions from the recording and sends only the new ones.

```sh
DAY=$(date +%F); RUN=results/runs/$DAY-thinkthen-jev
scripts/run/thinkthen.sh live "$RUN"
python3 scripts/score/score.py history "$RUN" "$DAY"  # one dated row in results/history.tsv
```

A fresh open-book, RAD, RAD2, or one-line run asks the same questions as the run before it. Copy its fixed inputs from the newest run of its label before the first call. None of them is a recording. Read the old folders before the fresh ones exist, because `newest` then names the fresh folder:

```sh
old() { python3 scripts/score/score.py newest "$1"; }
OB=$(old thinkthen-jev-open-book) RAD=$(old thinkthen-jev-rad) RAD2=$(old thinkthen-jev-rad2) ONE=$(old thinkthen-jev-one-line)
NEW=results/runs/$(date +%F)-thinkthen-jev
mkdir -p "$NEW-open-book" "$NEW-rad" "$NEW-rad2" "$NEW-one-line"
cp "$OB/ids.txt" "$OB/catalog.txt" "$NEW-open-book/"
cp "$RAD/rank-bm25.tsv" "$RAD/rank-minilm.tsv" "$NEW-rad/"
cp "$RAD2/split.tsv" "$RAD2/rank-bm25opt.tsv" "$NEW-rad2/"
cp "$ONE/questions.jsonl" "$ONE/ids.txt" "$NEW-one-line/"
```

The rest of the pipeline rebuilds offline:

```sh
python3 scripts/harvest/harvest.py --offline          # rebuilds data/ from data/raw/ and data/pins/
python3 scripts/generate/generate.py && python3 scripts/generate/make_suite.py
.venv/bin/python scripts/run/baselines.py 2026-09-23  # the four baseline runs
```

## Add a backend

Any backend the `thinkthen` command can reach works with `./run.sh`. Give each run its own name, because a recording binds to one address and one model. Kev (github.com/jaredpalmer/kev) serves the System One API on a Mac:

```sh
(cd ../kev && KEV_DTYPE=bf16 uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009 &)
THINKTHEN_BASE_URL=http://127.0.0.1:8009/v1 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=kev-latest ./run.sh kev
```

`scripts/score/analyze.py` picks up every run that answers every question. Add the run's model to `scripts/score/prices.tsv` for its cost. Until then its cost cell stays blank.

## Draw figures

Each figure is one script, drawn with kuva into `reports/figures/` as SVG and PNG. kuva has no error bars and no node-link diagrams. So intervals are box plots built from each interval, the graph and the pipeline are sankey diagrams, and Pillow places panels side by side.

```sh
PYTHON=$PWD/.venv/bin/python scripts/figures/all.sh   # reports/figures/
```
