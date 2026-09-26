# Scripts

All the code, one folder per stage. The pipeline runs in this order: harvest, generate, run, score, figures. Run every command from the repository root.

| Folder | Stage | Main scripts |
| --- | --- | --- |
| `harvest/` | Fetch pinned Wikipedia pages, page views, and Wikidata answers, then write `data/`. | `harvest.py`, `wikitext.py`, and the Wikidata queries (`*.rq`, `reversal/`) |
| `generate/` | Turn `data/` into `questions/`, `questions/functions/`, and the cases in `functions/`. | `generate.py`, `functions.py`, `examples.py` |
| `run/` | Ask every question and record each exchange in `results/runs/RUN/`. | `thinkthen.sh` (wraps `ask.py`), `functions.sh`, `rad_pipeline.sh` (shipped commands and `jq` only), `chat.py`, `baselines.py`, `relation_vectors.py`, `catalog.py`, `rad.py`, `gaps.py`, `model_time.py`, `in_text_check.py` |
| `score/` | Score the runs into `results/tables/` and `results/history.tsv`. | `analyze.py`, `functions.py`, `table.py`, `score.py`, `stats.py`, `open_book.py`, `rad_table.py`, `prices.tsv`, `diff_guard.sh` |
| `figures/` | Draw `reports/figures/` from `results/tables/` with kuva. | `all.sh`, `common.py`, one numbered script per figure |

## Setup

Python 3.12. The harvest, the generators, the scoring, and the replays of Jev need only the standard library and the `thinkthen` command. The chat backend, the embedding baselines, and the figures need a venv: `uv venv .venv && uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple --index-strategy unsafe-best-match -r requirements.txt`, plus `kuva` and `Pillow`. The CPU index keeps torch small.

## Rerun

`./run.sh` at the repository root chains the steps below. With no `THINKTHEN_BASE_URL`, it replays the newest `results/runs/DATE-thinkthen-jev` with no key and compares `replay/answers.jsonl` with the committed answers. It then replays every folder in `functions/` and compares each replayed file with the committed one. Last, it runs `analyze.py` and `table.py`. With `THINKTHEN_BASE_URL` set, it runs `thinkthen.sh live` into `results/runs/<today>-<name>` in place of the replay. It then asks each function folder's cases into `results/runs/<today>-examples-<name>/<function>/`. The name is its argument, else `BEATLES_BENCH_MODEL`, else `jev-latest`. `BENCH_MAX_INPUT_TOKENS` caps each step on its own.

Code finds a dated run by its label: `python3 scripts/score/score.py newest LABEL` prints the newest `results/runs/DATE-LABEL` folder. `analyze.py` scores the newest run of each label. A fresh run of a label takes over, and the older folder stays and still replays.

Everything below runs offline with no key and no spend. The embedding baseline needs its model files once.

```sh
.venv/bin/python -m unittest discover -s tests       # no network; set THINKTHEN_BIN to run the replay tests
python3 scripts/harvest/harvest.py --offline          # rebuilds data/ from data/raw/ and data/pins/
python3 scripts/generate/generate.py && python3 scripts/generate/functions.py
.venv/bin/python scripts/run/baselines.py 2026-09-23  # the four baseline runs; --phrasing natural for the other wording
env -u THINKTHEN_API_KEY scripts/run/thinkthen.sh replay "$(python3 scripts/score/score.py newest thinkthen-jev)"   # no key, no network
env -u THINKTHEN_API_KEY scripts/run/functions.sh replay "$(python3 scripts/score/score.py newest functions-jev)"
env -u ZAI_API_KEY .venv/bin/python scripts/run/chat.py replay results/runs/2026-09-23-glm-5.3-flash
env -u ZAI_API_KEY .venv/bin/python scripts/run/chat.py functions replay results/runs/2026-09-23-functions-glm-5.3-flash
.venv/bin/python scripts/score/analyze.py             # results/tables/
python3 scripts/score/functions.py table "$(python3 scripts/score/score.py newest functions-jev)"   # results/tables/functions.tsv
python3 scripts/score/table.py                        # the results tables
PYTHON=$PWD/.venv/bin/python scripts/figures/all.sh   # reports/figures/
```

Each folder in `functions/` replays the same way with `run/example.sh NAME replay [OUT]`. It runs `functions.sh` with `BENCH_FUNCTIONS` set to the folder and `BENCH_TESTS` naming its case files. The replay writes to `OUT`, by default the folder's `replay/`. `run/example.sh NAME live OUT` asks every case into `OUT`, a fresh folder with its own recording. `live` refuses without `OUT`. A live run then never writes into a committed folder. For `audit`, `example.sh` then runs `score/tune.sh` for the audit files. `score/context_diff.sh [IN [OUT]]` runs `diff` on the rows in `IN`, by default `functions/audit`. Each folder's own `run` is separate. It runs the slide's command for a reader.

`scripts/score/diff_guard.sh A B [--allow-unpaired] [--no-digest] -- DIFF_ARGS` runs `thinkthen diff` on two runs. It stops when no records pair, when an answer has no partner, or when a pair asked a different question. `--allow-unpaired` and `--no-digest` turn off the last two checks. `diff` and the leaning-no report use `--no-digest`, because their two runs word the question differently by design.

A replay writes `RUN/replay/` and leaves the committed files alone. Compare `RUN/replay/answers.jsonl` with `RUN/answers.jsonl` to check a run byte for byte. The open-book and section-picking runs replay the same way (`results/runs/DATE-thinkthen-jev-open-book`, `-rad`, and `-rad2`). [reports/open-book.md](../reports/open-book.md) and [reports/rad.md](../reports/rad.md) give the commands that print their tables.

## A live run

A live Jev run goes through the ThinkThen live guard. The guard reserves the tokens first. `BENCH_MAX_INPUT_TOKENS` stops a run at a cap, and `BENCH_WORKERS` sets the calls in flight. Only the `thinkthen` command reads `THINKTHEN_API_KEY`, and a recording holds request and response bodies, never headers. A rerun answers unchanged questions from the recording and sends only the new ones.

```sh
DAY=$(date +%F); RUN=results/runs/$DAY-thinkthen-jev
scripts/run/thinkthen.sh live "$RUN"                  # under the guard: sdlc/scripts/live --max-tokens N JOB
CHAT_MODEL=glm-5.3-flash CHAT_MAX_USD=1.00 .venv/bin/python scripts/run/chat.py live results/runs/$DAY-glm-5.3-flash   # key from ZAI_API_KEY
python3 scripts/score/score.py history "$RUN" "$DAY"  # one dated row in results/history.tsv
python3 scripts/score/functions.py history results/runs/$DAY-functions-jev "$DAY"
```

## Fixed inputs for a fresh run

A fresh open-book, RAD, RAD2, or one-line run asks the same questions as the run before it. Its fixed inputs are copied in from the newest run of its label before the first call. None of them is a recording. Read the old folders before the fresh ones exist, because `newest` then names the fresh folder:

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

The 196 open-book questions and the 38 one-line questions then stay the same, so `thinkthen diff` pairs the old and fresh runs.

## Laya

The bench reached the Laya shim on a Mac with an Apple M5 chip through an SSH tunnel, with one call in flight. The shim needs no key, so `local` is a dummy. The shim is `shim.py` from the workspace experiment `experiments/220-thinkthen-second-backend`, installed with its venv and model on the Mac. Below, `MAC` is the Mac's ssh host and `SHIM_DIR` is that experiment folder on the Mac. The shim's log goes to a temporary file, copied into the run folder as `shim.log` and then removed:

```sh
ssh MAC 'cd SHIM_DIR && nohup .venv/bin/python shim.py --port 8791 --log /tmp/laya-shim.log > /tmp/laya-shim.out 2>&1 &'   # wait for "listening on 127.0.0.1:8791" in /tmp/laya-shim.out
ssh -f -N -L 8791:127.0.0.1:8791 MAC                  # the tunnel
# ...the runs below, then:
scp MAC:/tmp/laya-shim.log RUN/shim.log
ssh MAC 'pkill -f "^.venv/bin/python shim.py --port 8791"; rm -f /tmp/laya-shim.log /tmp/laya-shim.out'; pkill -f '^ssh -f -N -L 8791'
```

The patterns are anchored. The shell that runs `pkill` then cannot match itself.

The runs:

```sh
THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/thinkthen.sh live results/runs/2026-09-23-thinkthen-laya
THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/functions.sh live results/runs/2026-09-23-functions-laya
THINKTHEN_BASE_URL=http://127.0.0.1:8791 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=laya-mlx BENCH_WORKERS=1 scripts/run/thinkthen.sh live results/runs/2026-09-24-thinkthen-laya-one-line
python3 scripts/run/model_time.py RUN RUN/shim.log   # pairs each call with the shim's log lines
THINKTHEN_BASE_URL=http://127.0.0.1:8791 python3 -m unittest tests.test_replay_laya   # replays the Laya runs and the one-line runs, no key, no tunnel
```

The one-line runs ask each lead-singer question of the open-book sample with only its song's catalog line in the question's `context` field. A question that names four songs has no one line and is left out. [reports/open-book.md](../reports/open-book.md), section "One line for Laya", gives the command that writes `questions.jsonl` and `ids.txt` for `results/runs/2026-09-24-thinkthen-laya-one-line` and `-jev-one-line`.

## Add a System One backend

Any backend the `thinkthen` command can reach works with the same script, or with `./run.sh`. Give it its own base URL and its own run folder, because a recording binds to one address. Kev (github.com/jaredpalmer/kev) serves the System One API on a Mac:

```sh
(cd ../kev && KEV_DTYPE=bf16 uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009 &)
THINKTHEN_BASE_URL=http://127.0.0.1:8009/v1 THINKTHEN_API_KEY=local BEATLES_BENCH_MODEL=kev-latest scripts/run/thinkthen.sh live results/runs/$(date +%F)-thinkthen-kev
```

`scripts/score/analyze.py` picks up every run that answers the current questions. Add the run's model to `scripts/score/prices.tsv` for its cost.

## Figures

Each figure is one script, drawn with kuva into `reports/figures/` as SVG and PNG. kuva has no error bars and no node-link diagrams. So intervals are box plots built from each interval, the graph and the pipeline are sankey diagrams, and Pillow places panels side by side.
