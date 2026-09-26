# 0009 Rerun every Jev run fresh, and show that the replay repeats

Owner: the queue owner. Status: done 2026-09-25. Ticket 0011 landed at an earlier commit. The ticket review is done: four reviews. Reviews 1, 2, and 3 returned ten, twelve, and twelve findings. Review 4 returned two. All 36 are fixed. Code review 1 returned six findings, and the builder fixed them. Steps 4 to 8 ran on 2026-09-25. The fresh runs sit in an earlier commit. The step 7 commit is a later one. Code review 2 accepted all but two prose findings, and the builder fixed both. Record gives the numbers.

## Why

Ian ruled in a 2026-09-25 conversation with the queue owner: "Rerun everything and validate that everything passes, making sure that we get the same result every single time, so we can use the audit and the diff tools as well." He authorized the paid rerun in the same conversation. Later that day he set the ceiling: "Yes test everything with thinkthen. Create new issues if necessary $1 approved".

The rerun is part of the talk's QA. Every Jev run in scope runs again from an empty recording, on the paths that ticket 0011 settles. The fresh runs then replay the same way every time, and `thinkthen audit` and `thinkthen diff` measure them.

## What repeats

1. **Live answers vary.** A fresh live call can give a different probability than the old call. No one claims the live answers repeat.
2. **The replay repeats.** A replay of the fresh recording, with the key unset and one pinned `thinkthen` binary, gives the same bytes every time. `cmp` across two replays shows it. One of the two replays runs from a fresh clone of the branch commit that holds the results and downstream files.
3. **diff measures the change.** `thinkthen diff`, or the Python comparison where 0011 keeps one, counts what moved between each old run and its fresh run. The record names every number that moved.

## Scope and caps

Each row is one guard job with its own cap. Each fresh folder's recording starts empty. No fresh folder starts from a copied recording.

| Job | Old folder | Fresh folder | Recorded input tokens | Cap |
| --- | --- | --- | --- | --- |
| The 1,501 | `2026-09-23-thinkthen-jev` | `<date>-thinkthen-jev` | 534,901 | 600,000 |
| Open book, 196 questions | `2026-09-23-thinkthen-jev-open-book` | `<date>-thinkthen-jev-open-book` | 2,394,007 | 2,640,000 |
| RAD picks | `2026-09-23-thinkthen-jev-rad` | `<date>-thinkthen-jev-rad` | 191,308 | 211,000 |
| RAD Jev k=2 and BM25 k=2 answers | same | same | 678,534 | 747,000 |
| RAD MiniLM k=2 and Jev k=1 answers | same | same | 518,131 | 570,000 |
| RAD2 picks with options | `2026-09-23-thinkthen-jev-rad2` | `<date>-thinkthen-jev-rad2` | about 226,302 | 249,000 |
| RAD2 answers | same | same | about 508,398 | 560,000 |
| One line, 38 questions | `2026-09-24-thinkthen-jev-one-line` | `<date>-thinkthen-jev-one-line` | 13,171 | 15,000 |
| Function suite | `2026-09-23-functions-jev` | `<date>-functions-jev` | 972,967 | 1,071,000 |
| Pipeline | `2026-09-24-pipeline-jev2` | `<date>-pipeline-jev` | at most 123,371 | 136,000 |
| Examples 01 to 11, one job each | `examples/NN-name/` | `<date>-examples-jev/NN-name/` | 89,988 in all | 99,500 in all |
| Total | | | 6,251,078 | 6,898,500 |

The example caps, in order from 01 to 11: 5,500; 4,000; 3,100; 7,300; 8,500; 3,900; 1,900; 2,800; 9,000; 3,800; 49,700. `12-diff` sends no request.

All folders sit under `results/runs/`. `<date>` is the day the run starts. No code names a dated folder. Code finds its input folders by the newest-folder rule in code change 6.

How the recorded column was counted:

- The 1,501 row is the answers' usage in `results/tables/cost.tsv`. The old recording sums to 885,985, because it also holds a superseded first pass.
- The one-line row sums the old recording, 38 requests.
- The RAD rows come from the job lines in the old ledgers. The RAD2 rows sum `usage.input_tokens` over the old recording, split by pick and answer requests. They include the 199 requests the old run copied from the first RAD recording.
- The open-book row is the main pass. The old probe of `forward-singer-001` sat outside the 196 and is not rerun.
- The function row sums the old recording. It is lower than the 1,468,755 in `results/tables/functions.tsv`, because that table counts repeated cases once per record.
- The pipeline row sums the old `pipeline-jev2` recording. It includes the `tries/screen` calls, which are not rerun.
- The example rows sum each example's recording.

Each cap is at least 10% above its recorded use.

GLM-5.3 Flash, Laya, the four baselines, relation vectors, and the MiniLM and BM25 ranks stay at their old dates.

## Budget and stops

- The planned spend is 6.5M input tokens, about $0.27 at $0.042 per million. The recorded use is 6.25M. The caps add to 6.9M, because each carries its margin.
- The ceiling is $1, about 23.8M input tokens. The space above the plan covers retries and reruns of failed jobs. Spend that would pass $1 needs Ian. Spend that passes 6.5M is named in the record.
- **The stop.** thinkthen's live guard only reserves tokens, and `thinkthen` has no token flag. The real stop is `BENCH_MAX_INPUT_TOKENS` in `ask.py` and `functions.py`. Each job sets it to the job's cap. Unset means no cap. A set value of 0 or below starts no call. A job that stops at its cap halts. It waits for the owner's decision, recorded in `ledger.txt`, before it runs again. The guard's `--max-tokens` is the cap plus `BENCH_WORKERS` times the largest recorded request of that job, so calls already in flight fit.
- **The pipeline.** `rad_pipeline.sh` has no token stop. Its case list is fixed, so its requests are bounded. Its guard reservation is 136,000. Ticket review 3 put its worst case at about $0.048.
- **Spent.** `ledger.txt` logs the recording's input-token total before and after every attempt, first and resume alike. The total is `find RUN -path '*/recording/*.json' -not -path '*/replay/*' -exec cat {} + | jq -s 'map(.response.usage.input_tokens // 0) | add // 0'`. A job's spent is the sum of its after-minus-before differences. On the committed runs the command gives 13,171 for the one-line run and 89,988 for `examples/`, the recorded numbers in Scope.
- **Resume.** A job that stops early is run again into the same folder. `--cache` answers every request already in that folder's recording, so nothing paid is paid twice. On resume, `BENCH_MAX_INPUT_TOKENS` is the job's cap minus its spent. The guard reserves that remaining cap plus `BENCH_WORKERS` times the job's largest recorded request. A resume never gets a full new cap. When the remaining cap is 0 or below, the job starts no call. Each resume is logged in the folder's `ledger.txt`.
- **Gaps.** `scripts/run/gaps.py` records any refused call as a permanent gap, 401 and 429 included. Those two mean a bad key or a rate limit, not a refused question. Before a resume, the owner removes 401 and 429 rows from `gaps.tsv` and logs the removal in `ledger.txt`. A finished run needs an empty `gaps.tsv`.

## Prior evidence

- Ticket 0008 added `./run.sh`. Its replay is fixed to `results/runs/2026-09-23-thinkthen-jev`. `tests/test_run_sh.py` checks that folder's Jev row.
- `open_book.py pick` draws the 196 open-book questions from the closed-book run's hits and misses. A fresh closed-book run would redraw them. The sample draws misses and hits from the 2026-09-23 closed-book run within each topic. `reports/open-book.md` weights the fixed rate and the kept rate back to the 1,075 covered questions and gets about 97%. `rad.py split` wrote `split.tsv` for RAD2. The one-line run's `questions.jsonl` and `ids.txt` came from `results/runs/2026-09-24-thinkthen-laya-one-line/build.py`.
- `rad_pipeline.sh` today writes the `pipeline-jev2` case set. It cannot rebuild the first `pipeline-jev` run.
- The old RAD run used three guard jobs. RAD2 used two. `pipeline-jev2` used five, one of them `tries/screen/screen.sh`.
- The guard is `sdlc/scripts/live` in a thinkthen checkout. It needs `target/debug/thinkthen` built there. It puts `target/debug` first on `PATH` and passes the rest of the environment through, `THINKTHEN_BIN` included. It runs the job from the thinkthen checkout, so job paths are absolute.
- Old Jev paths sit in `run.sh` line 17, `scripts/run/rad.py` line 29, `scripts/run/rad_pipeline.sh` line 24, `scripts/score/functions.py` line 31, `scripts/score/rad_table.py` lines 31 and 34, `scripts/README.md`, and the one-line build command in `reports/open-book.md`.
- Each old Jev run used model `jev-1.13.0`. The model sits in each recording's `response.model`.
- `data/raw/` holds the harvest's page cache. It is not committed. It sits in the main checkout on the local machine, so a worktree has none. `scripts/harvest/harvest.py --offline [RAW PINS OUT]` rebuilds `data/` from it and `data/pins/`.
- `scripts/generate/examples.py` line 47 defines one `ABBEY` wording. 01-decide (line 109), 05-filter (line 118), and 11-audit (lines 148 and 149) all use it.
- `functions.py` names `cached` and `requests_sent` as the only fields a replay reports differently from a live run (`VOLATILE`). `ask.py`'s `details.jsonl` carries `meta.cached` and `meta.requests_sent` too.
- `scripts/run/gaps.py` treats every exit 4 as a refused question and never asks it again. That includes 401 and 429.
- `.gitignore` ignores `results/runs/*/replay/`, `examples/*/replay/`, and `examples/12-diff/a.jsonl` and `b.jsonl`. It does not cover folders one level deeper, as in `results/runs/<date>-examples-jev/NN-name/replay/`.
- The local experiment's `07-bench-run.sh` line 14 clones the main checkout, not `bench/`.
- A local experiment holds seven claim scripts, `01-ten-functions.sh` to `07-bench-run.sh`. `common.sh` pins the binary and a clone of this repository in `bench/`. Each command's exit code lands in `out/NN-name/LABEL.rc`. Every replay claim passed on 2026-09-25. Three slide images differ from the replay. That is slide work.
- `scripts/figures/` draws with `kuva` and joins panels with Pillow. On the local machine `kuva` is in Cargo's bin folder. The system `python3` has Pillow 10.2.0. The repository's `.venv` has none.
- `README.md`'s headline table is pasted from `python3 scripts/score/table.py`. The reports and example READMEs are written by hand. `score.py history` and `functions.py history` append rows to `results/history.tsv`.
- The divide by zero in `open_book.py compare`, Hey Jude's length, and the diff behavior each have an issue. The audit example asks "The text is the title of a song by the Beatles. It appears on the album Abbey Road." Its README puts it as "is this song on the album Abbey Road?"

## Order

1. Ticket 0011 lands on main.
2. The owner builds the pinned binary from thinkthen main and records its commit and SHA-256.
3. The builder makes every code change below on `ticket/0009-rerun-fresh` in the ticket's worktree. The changes are committed. A fresh reviewer accepts them in code review 1.
4. The local experiment gate passes against that reviewed commit.
5. The data lockdown passes on that commit.
6. The paid jobs run in the order of the Scope table. Later jobs read earlier fresh folders. Results are committed on the branch.
7. The builder swaps the fresh examples in, regenerates the downstream files, and commits them. The record names this commit's hash.
8. The replay proof runs, including a fresh clone of the step 7 commit.
9. A fresh reviewer accepts the step 7 commit, by its hash, in code review 2.
10. The branch lands on main and is pushed.

## Code changes

1. **Hey Jude.** One line in "Known limits" in `data/README.md`: Hey Jude's length follows the track-listing rule (7:08), and its song page gives 7:12. Close the issue with a pointer here.
2. **Divide by zero.** `open_book.py compare` prints a blank cell for a topic with no questions. One edge-case test covers it. Close the issue with a pointer here.
3. **Audit wording.** `scripts/generate/examples.py` gets a separate `AUDIT_WORDING`, "Is this song on the album Abbey Road?", the plainest wording in the audit README. Only 11-audit uses it. 01-decide and 05-filter keep `ABBEY`. The talk's runs-in slide can then replay its `filter` command from the audit recording.
4. **Fixed inputs.** The fresh open-book folder takes the old `ids.txt` and `catalog.txt`. The fresh RAD folder takes the old `rank-bm25.tsv` and `rank-minilm.tsv`. The fresh RAD2 folder takes the old `split.tsv` and `rank-bm25opt.tsv`. The fresh one-line folder takes the old `questions.jsonl` and `ids.txt`. Each is copied in as an input. None is a recording. The 196 and the 38 stay the same, so diff pairs them and the Laya comparison stays valid.
5. **Old paths.** Each old Jev path in Prior evidence finds its folder by the newest-folder rule in change 6, or takes it as an argument. No code names a dated folder. `reports/open-book.md` names the build command for the fresh run.
6. **Newest folder.** One helper in `scripts/score/score.py` returns the newest `results/runs/*-LABEL` folder. `analyze.py`, `table.py`, and every path in change 5 use it. The old Jev folders stay in place and still replay. A test covers the newest-folder rule.

   Tests pinned to old numbers never use the rule. `rad_table.py`, and each function in it that `tests/test_score_rad.py` calls (`arm`, `fallback`, `candidates`, `table`, `choose_cut`, `picker`, and `second`), take the closed-book and open-book folders as arguments. The tests pass the 2026-09-23 folders by name. `choose_cut` reads no folder, so it takes none. `rad_table.py`'s command line takes optional `--closed`, `--open`, and `--first` folders. `reports/rad.md` passes the 2026-09-23 folders in its old-run commands.

   One constant, `JEV` in `tests/published.py`, names the date of the `thinkthen-jev` and `functions-jev` runs behind the published tables. It still points at 2026-09-23. It reaches `SYSTEMS["Jev"]` in `tests/test_audit_contract.py`, the Jev row of `TableTest`, and `RUN` in `tests/test_functions.py`. Laya and GLM keep their named folders. Step 7 moves that one line in the same commit that rewrites the tables. Code review 1 checks this.
7. **`./run.sh`.** Its replay points at the fresh `<date>-thinkthen-jev` and replays every example folder, each checked byte for byte. With an address set, it also asks each example into `results/runs/<date>-examples-<name>/NN-name/`. `BENCH_MAX_INPUT_TOKENS` then applies to each step separately: the 1,501, then each example. The README says so, and says the examples add about 90,000 input tokens to a reader's live run. No budget passes from one step to the next. `tests/test_run_sh.py` follows.
8. **Token stop test.** One case in `tests/test_run.py` runs `ask.py live` with `tests/fixtures/fake-thinkthen` and `BENCH_MAX_INPUT_TOKENS=15`. The fake reports 10 input tokens a call. The run stops after two calls and says so. Rows for a cap of 0 and of -5 start no call. One case in `tests/test_functions.py` shows `functions.py` starts no call at a cap of 0.
9. **Ignore rules.** `.gitignore` adds `results/runs/*/*/replay/` and `results/runs/*/12-diff/[ab].jsonl`.
10. **Clutter.** Remove the ignored folder `results/runs/2026-09-23-thinkthen/`, which holds an empty recording and a stray replay. An agent's worktree is deferred. A sweep of leftover worktrees does not list it (see Deferred). Its `open-book` branch holds no work that main lacks: the open-book run and report are on main. Move `examples/context-article.md` to `examples/context-article/README.md`, and update the README link and the exception in `tests/test_examples.py`.

## The local experiment gate

Command, from the experiment folder:

```sh
cp -r out out-2026-09-25
rm -rf bench && git clone -q "$WORKTREE" bench
cp PINNED thinkthen
for s in 01 02 03 04 05 06; do sh "$s"-*.sh; done
sed "s#git clone -q --no-hardlinks [^ ]* #git clone -q --no-hardlinks $WORKTREE #" 07-bench-run.sh > 07-worktree.sh
sh 07-worktree.sh
```

`WORKTREE` is the branch worktree. `PINNED` is the pinned binary. The copy of 07 clones the worktree in place of the main checkout. Pass rule: for every `.rc` file under `out-2026-09-25/`, the new `out/` holds the same file with the same exit code. The record lists any difference with its reason. A difference that follows from this ticket, such as `./run.sh` replaying the fresh folder, is allowed only when the record names it. Loopback results count the same way.

### The wording window

Code change 3 lands before the rerun. From then until step 7 swaps the fresh examples in, the committed 11-audit recording lacks the new wording. These failures are expected in that window, and only these:

- the 11-audit replay in `tests/test_examples.py` and in `./run.sh`
- the 12-diff replay, which reads the 11-audit rows
- the local experiment's commands in `02-filter-085.sh`, `03-cache-record-replay.sh`, `04-diff.sh`, and `05-audit.sh` that replay the 11-audit recording or read its rows

The gate's pass rule allows these and no others. Code review 1 runs the suite with them named.

## Data lockdown

1. On the reviewed commit, from the worktree, run `harvest.py --offline MAIN/data/raw data/pins data`, where `MAIN` is the main checkout on the local machine. Then run `generate.py`, `scripts/generate/functions.py`, and `scripts/generate/examples.py`. `git status --porcelain` must stay empty.
2. Write `inputs.sha256` into each fresh folder. It lists the SHA-256 of every file in `git ls-files data questions`, plus every case file and key that `scripts/generate/examples.py` writes, plus the fixed inputs copied into that folder. It leaves out `data/raw/`.
3. The replay checks it with `sha256sum -c inputs.sha256`.

## Run record

The pinned binary is a local build. It is a release build of thinkthen main at 02dc0b9672dea909d64d6dd0e44820814e93d9de. Its SHA-256 is `eb4a571370527ec56c5fe0e10aec410ae906799c05b4de3d9a97ba6eaf48e255`. Every job checks it before it starts and stops on a mismatch:

```sh
echo "eb4a571370527ec56c5fe0e10aec410ae906799c05b4de3d9a97ba6eaf48e255  $THINKTHEN_BIN" | sha256sum -c -
```

Every job runs with `THINKTHEN_BIN` set to the pinned binary's absolute path. Each fresh folder gets `run.txt`: the thinkthen version and commit, the binary's SHA-256, the model the backend reported, the machine, the date, each guard job with its cap and `BENCH_MAX_INPUT_TOKENS`, and the input tokens sent. The ledger keeps the guard's status before and after.

## Measure

Each pair runs `thinkthen diff` behind 0011's guard, or the Python comparison where 0011 keeps one.

| Old | Fresh | Tool | Expected pairs |
| --- | --- | --- | --- |
| `2026-09-23-thinkthen-jev` | `<date>-thinkthen-jev` | diff | 1,501 |
| `2026-09-23-thinkthen-jev-open-book` | fresh open book | diff | 196 |
| `2026-09-23-thinkthen-jev-rad` | fresh RAD | diff | 980 |
| `2026-09-23-thinkthen-jev-rad2` | fresh RAD2 | diff | 490 |
| `2026-09-24-thinkthen-jev-one-line` | fresh one line | diff | 38 |
| `2026-09-23-functions-jev` | fresh function suite | Python, `scripts/score/functions.py` | 2,024 records |
| `2026-09-24-pipeline-jev2` | fresh pipeline | Python, `checks.tsv` and `scores.tsv` | 18 songs |
| `examples/01-decide` | fresh 01 | diff | 16 |
| `examples/02-choose` | fresh 02 | diff | 10 |
| `examples/03` to `10` | fresh 03 to 10 | Python, tag and annotate included | 6, 16, 24, 12, 2, 4, 1, 1 records |
| `examples/11-audit` cold and context | fresh 11 | diff with `--no-digest` | 70 and 70 |

The old example files come from the branch's base commit on main, read with `git show BASE:examples/NN-name/FILE` into a scratch folder before the swap. The audit wording changes, so the 11-audit pairs cross wordings. The record reports them as a new question and not as a change. 0011's contract test also runs on each fresh Jev run, so `thinkthen audit` checks the fresh tables.

## Replay proof

For each fresh folder, the loop replays twice. The two replays must match byte for byte. Each replay must match the live output once the fields a replay reports differently are removed:

```sh
strip='del(.. | .cached?, .requests_sent?)'
for f in FILES; do
  cmp "$RUN/replay/$f" "$CLONE_RUN/replay/$f" || exit 1
  case $f in *.jsonl) cmp <(jq -cS "$strip" "$RUN/$f") <(jq -cS "$strip" "$RUN/replay/$f") || exit 1 ;;
             *) cmp "$RUN/$f" "$RUN/replay/$f" || exit 1 ;; esac
done
```

The loop runs under `bash`.

The files, by runner:

- `thinkthen.sh`: `answers.jsonl`, `details.jsonl`.
- `functions.sh` and each example: `outputs.jsonl` and every file under `lists/`. `11-audit` adds `rows.jsonl`, `rows-context.jsonl`, and each `audit-*.json`. `12-diff` compares `diff.jsonl`.
- `rad_pipeline.sh`: every `*.jsonl`, `checks.tsv`, and `scores.tsv`. `times.tsv` is left out, because it holds wall times.

`CLONE_RUN` is the same folder in a fresh clone of the step 7 commit.

For the examples, `RUN` is `results/runs/<date>-examples-jev`. After the swap, each example replays from its committed recording into the fresh folder, and 12-diff reads that 11-audit replay. The inputs check runs from the repository root:

```sh
for n in 01-decide 02-choose 03-tag 04-score 05-filter 06-rank 07-find 08-annotate 09-recognize 10-relate 11-audit; do
  examples/$n/run.sh replay "$RUN/$n/replay"
done
examples/12-diff/run.sh "$RUN/11-audit/replay" "$RUN/12-diff/replay"
sha256sum -c "$RUN/inputs.sha256"
```

Each other fresh folder checks `sha256sum -c "$RUN/inputs.sha256"` from the repository root the same way.

## The example swap

Step 7 copies each fresh example into its committed folder:

```sh
for d in "$RUN"/0[1-9]-* "$RUN"/1[01]-*; do
  n=$(basename "$d")
  rm -rf "examples/$n/recording" "examples/$n/lists"
  cp -r "$d/recording" "$d/outputs.jsonl" "$d/timing.tsv" "examples/$n/"
  [ -d "$d/lists" ] && cp -r "$d/lists" "examples/$n/"
done
rm -f examples/11-audit/audit-*.json examples/11-audit/rows.jsonl examples/11-audit/rows-context.jsonl
examples/11-audit/tune.sh
examples/12-diff/diff.sh
```

`RUN` is `results/runs/<date>-examples-jev`. The `rm` clears the old audit files first, because the fresh suggested cut can name a different `audit-CUT.json`. `tune.sh` rebuilds the 11-audit rows and audit files. `diff.sh` rebuilds `12-diff/diff.jsonl` from them.

## Downstream

- `results/tables/`: `analyze.py` and `scripts/score/functions.py table`.
- `results/history.tsv`: rows appended by `score.py history` and `functions.py history`. No row is replaced.
- Figures: `scripts/figures/all.sh` on the local Linux machine, with `kuva` on the path and the system `python3` for Pillow.
- `README.md` headline table: pasted by hand from `table.py`. A new case in `tests/test_table.py` checks that the README table equals `table.py`'s output.
- Example READMEs: hand edits. `tests/test_examples.py` checks every decimal in each fenced block against that folder's outputs.
- Reports: hand edits. Each moved number cites the record. Code review 2 checks them against the record.

## Retained behavior

- Every old run folder stays byte for byte and still replays.
- The example folders are carved out. Their recordings, outputs, READMEs, and 11-audit wording change on purpose.
- GLM, Laya, the baselines, relation vectors, and the MiniLM and BM25 ranks keep their old dates and rows.
- `data/` and `questions/` stay the same, except the Hey Jude line.
- `./run.sh` keeps its arguments. The scripts never read, print, or pass the key.
- No harvest refetch runs.

## Proof

- Code review 1 accepted the code before the lockdown. The lockdown left `git status` empty before the first paid call.
- The local experiment gate passed by its rule.
- Each job stayed under its cap. The total stayed under $1. The record lists each job's tokens and the total.
- The names of the committed `examples/11-audit/audit-*.json` files equal the names in the fresh `11-audit` folder.
- `tests/test_score_rad.py` passes with the 2026-09-23 folders named in it. The contract test and the function-table test pass with `JEV` in `tests/published.py` naming the fresh date, moved in the step 7 commit.
- Every job's ledger shows the pinned binary's `sha256sum -c` passed before it started.
- Each fresh folder holds `run.txt` and `inputs.sha256`. `sha256sum -c` passes in replay. `sha256sum` of `THINKTHEN_BIN` equals the SHA-256 in every `run.txt`.
- The replay loop passes for every fresh folder, in the worktree and in the fresh clone of the step 7 commit. The record names that hash.
- Every fresh `gaps.tsv` is empty. `ledger.txt` logs every 401 or 429 row removed before a resume.
- Every diff pairs the expected count from the Measure table. The record names every number that moved.
- `git grep -nE "2026-09-2[34]-(thinkthen-jev|functions-jev|pipeline-jev)" -- scripts run.sh` prints nothing.
- `./run.sh` with no key passes. `python3 -m unittest discover -s tests` passes with and without `THINKTHEN_BIN`.
- `git status` is clean after the suite. A check for uncommitted work lists nothing for this repository.

## Owner's decisions (Ian can overturn each)

- Ian's ruling is cited from a 2026-09-25 conversation with the queue owner, as quoted in Why.
- Scope: the Jev runs in the Scope table. GLM, Laya, and the baselines stay at their old dates. No fresh folder starts from a copied recording.
- Budget: a planned 6.5M input tokens and a cap per guard job. A $1 ceiling covers retries and reruns.
- `BENCH_MAX_INPUT_TOKENS` is the real stop for each job, tested once with the fake command.
- Open-book, RAD2, and one-line inputs are reused as fixed inputs, not redrawn. The open-book sample keeps its 2026-09-23 sampling groups: the misses and hits of the 2026-09-23 closed-book run. The about-97% weighting uses those groups. The rad-family caps sit at least 10% above recorded use.
- The first `pipeline-jev` run is not rerun. One fresh pipeline row runs the current case set. `tries/screen` is out of scope.
- A job that stops resumes from its own folder's partial recording, with its cap minus what it already spent. A stop at the cap waits for a recorded decision.
- Code finds dated folders by the newest-folder rule. No dated path goes in the code.
- `./run.sh` applies the token cap per step. It passes no budget between steps.
- Every job sets `THINKTHEN_BIN` to the pinned binary. `run.txt` records its SHA-256, and a proof line checks it.
- Code review 1 comes before the lockdown and the first paid call. The fresh-clone replay clones the reviewed branch commit.
- Ticket 0011 lands first.
- The McNemar issue moved to thinkthen. The bench's copy is closed with a pointer.
- The divide by zero is fixed here, because the one-line run is rerun.
- Hey Jude takes option 1, the known-limits line, before the data locks.
- The audit example asks "Is this song on the album Abbey Road?", the plainest wording in its README.
- Old Jev folders stay in place. Scoring takes the newest folder for each label.
- Fresh examples run into `<date>-examples-jev/NN-name/`, and their recordings replace the committed ones in `examples/`.
- The tag and annotate pairs use the Python comparison.
- `history.tsv` gains rows. None is replaced.
- Hand-written prose is a hand edit that a named test checks, where a test can.
- `examples/context-article.md` moves into its own folder.
- The pinned binary sits in a second local experiment folder, because the folder code review 1 named was taken.
- One test constant names the Jev runs behind the published tables. Step 7 moves it with the tables.
- A cap of 0 or below starts no call. Spent comes from the recording's token totals in the ledger.
- The cold audit question is exactly "Is this song on the album Abbey Road?", so the slide's `filter` command replays from the 11-audit recording. The context question keeps the context opening before it: "The text gives a catalog entry and then names a song by the Beatles. Is this song on the album Abbey Road?" The 11-audit and 12-diff READMEs change to the new wording in step 7.
- `table.py` reads only `results/tables/`, so it takes the newest-folder rule through `analyze.py`. It needs no change.
- Change 4's copies are commands in `scripts/README.md`, "Fixed inputs for a fresh run", which `reports/open-book.md` names. They read the old folders before the fresh folders exist. No script copies them.

## Deferred

- Every `examples/*/slide.png` redraw. The talk's own ticket owns the slides.
- The first `2026-09-24-pipeline-jev` run. The current script cannot rebuild its case set.
- `results/runs/2026-09-24-pipeline-jev2/tries/`, including `tries/screen`.
- RAD Jev k=3, which the old run never asked.
- `results/in-text-check/jev-recording`, `results/probes/2026-09-23-jev-headers`, and the archive runs in `results/archive/`, the seed included.
- The open-book probe of `forward-singer-001`.
- GLM, Laya, and the baselines stay at their old dates.
- No harvest refetch. The pinned revisions stand.
- The thinkthen audit features planned for 0.1 stay unused. The pinned binary keeps audit's output fixed.
- A local experiment's recordings in `tests/fixtures/audit/249/` are not rerun.
- The McNemar rule is thinkthen's to settle.
- The context-article flips are not rerun. They fetch Wikipedia text and keep no recording.
- Other backends.
- Which of the local experiment's claim scripts earn a place in this repository's tests.
- Removing an agent's worktree. A sweep of leftover worktrees lists it as registered but leaves it out: its `open-book` branch landed on main as rewritten commits, so it counts 39 unmerged commits. The open-book run folder matches main. Filed in Ian's tooling repository.

## Done when

The proof passes, code review 2 accepts, and the branch is landed on main and pushed.

## Ticket review 1 (fresh reviewer, 2026-09-25): ten findings, all taken

1. Retained behavior and Proof are added. The ruling is cited.
2. Scope is a fixed table with a cap per job and a total.
3. Ticket 0011 takes the goal that every ask and grade runs through thinkthen. This ticket depends on it.
4. What repeats is stated in three parts. Each folder records the thinkthen commit and the Jev model. The binary is pinned.
5. The key files, the measures, the diff guard, and the example folders are in 0011. This ticket applies them.
6. Ticket 0011 retires `measure.py`, its text, and its tests.
7. Each open issue has a place.
8. The data lockdown runs before any paid call. Each folder holds `inputs.sha256`. `data/raw/` sits on the local Linux machine.
9. The downstream files, `./run.sh`, its test, the examples path, and the clutter each have a step.
10. The start gate no longer waits on the slides. Done when drops the slides. Deferred is complete.

## Ticket review 2 (fresh reviewer, 2026-09-25): twelve findings, all taken

1. `BENCH_MAX_INPUT_TOKENS` is the stop for each job, with one cheap test. The pipeline's bound is stated.
2. The open-book, RAD2, and one-line inputs are reused. The rad-family caps sit at least 10% above recorded use.
3. The first `pipeline-jev` run is deferred. One fresh pipeline row runs the current case set.
4. Each guard job has its own cap. A stopped job resumes from its own recording.
5. Every job sets `THINKTHEN_BIN`. `run.txt` records its SHA-256, and a proof line checks it. The guard's path and behavior are named.
6. Every old Jev path is listed. The grep runs over `scripts run.sh` and must print nothing.
7. The replay loop lists its files by runner, leaves out `times.tsv`, and compares each replay with the live outputs.
8. The hash list comes from `git ls-files data questions`, the example cases and keys, and the fixed inputs.
9. Code review 1 comes before the lockdown and the first paid call.
10. The fresh clone takes the reviewed branch commit, so the proof comes before the push. The local experiment gate has a command and a pass rule.
11. Slides are deferred. The README table, reports, and example READMEs are hand edits with named checks. `history.tsv` appends. The figures name `kuva` and Pillow.
12. Deferred names the extra recordings. Each diff pair has an expected count. Tag and annotate use the Python comparison. The README says `./run.sh` live now asks every example.

## Ticket review 3 (fresh reviewer, 2026-09-25): twelve findings, all taken

1. The live comparison strips `cached` and `requests_sent` with `jq`. The two replays compare exactly. The loop exits on the first failure.
2. The fresh clone takes the step 7 commit. The record names its hash, and code review 2 reviews that hash.
3. The audit wording gets its own constant, so 01-decide and 05-filter keep theirs. The swap command and the `diff.sh` rebuild are named. The old example files come from the base commit. The examples are carved out of Retained behavior. The expected failures in the wording window are named.
4. Code finds dated folders by the newest-folder rule. No dated path goes in the code.
5. A resume gets the cap minus what was spent. A stop at the cap waits for a recorded decision.
6. 401 and 429 rows are cleared before a resume and logged. A finished run needs an empty `gaps.tsv`.
7. The function cap is 1,071,000. 08-annotate is 2,800 and 09-recognize is 9,000. The totals follow. The 1,501 and one-line rows have counting lines.
8. The gate runs a copy of `07-bench-run.sh` that clones the worktree.
9. `.gitignore` covers replays one level deeper and the 12-diff scratch files in run folders.
10. The offline harvest names its three paths, with `data/raw` read from the main checkout.
11. The README says the `./run.sh` cap applies per step. No budget passes between steps.
12. The open-book sample keeps its 2026-09-23 sampling groups, and the ticket says so.

## Ticket review 4 (fresh reviewer, 2026-09-25): two findings, both fixed

The reviewer confirmed that spend is bounded, the grep covers every path, the `jq` strip works, and the pair counts match.

1. Tests pinned to old numbers would fail once the fresh runs land. `rad_table.py` and the functions `tests/test_score_rad.py` calls take the closed-book and open-book folders as arguments, and the tests pass the 2026-09-23 folders. 0011's contract and function-table tests read the named 2026-09-23 folders. Code review 1 checks this.
2. The example swap left a stale audit file. The swap now removes the old 11-audit audit files and rows before `tune.sh`. A proof line checks the committed `audit-*.json` names against the fresh folder.

## Code review 1 (fresh reviewer, 2026-09-25): code sound, six findings, all fixed

1. The pinned binary is copied to a local experiment folder, with its commit and SHA-256 in Run record. Every job checks `sha256sum` first.
2. A cap of 0 or below starts no call in `ask.py` and `functions.py`, with test rows. The ledger logs recording totals before and after each attempt. A resume reserves the remaining cap plus `BENCH_WORKERS` times the largest request.
3. `JEV` in `tests/published.py` names the runs behind the published tables. Step 7 moves it with the tables.
4. The builder's departures are recorded under Owner's decisions. The agent worktree cleanup is deferred and filed in Ian's tooling repository.
5. Replay proof names the example replay commands and the inputs check.
6. `rad_table.py` takes optional `--closed`, `--open`, and `--first` folders. `reports/rad.md` passes the 2026-09-23 folders.

## Record

### Gate (step 4)

The local experiment gate ran against an earlier commit with the pinned binary. Eight `.rc` files changed. All eight sit in the named wording window: seven in `04-diff.sh` and the `./run.sh` replay in `07-bench-run.sh`.

- `07-bench-run/R01-run`: 0 to 1. The 11-audit replay has no entry for the new wording. This is the named failure.
- `04-diff/D01-example`: 0 to 2. `D01-table`, `D04-duplicate`, `D05-only-a`, `D13-two-cuts`, and `D15-no-probabilities` fail after it, and `D07-two-questions-one-file` flips from 2 to 0 on an empty file. All read `d01/a.jsonl`, built from the 11-audit rows. The cause is ticket 0011's change to `12-diff/diff.sh`, which now takes `[IN [OUT]]`. The claim script still passes the output folder first. With the new order, `diff.sh` rebuilds the committed `diff.jsonl` byte for byte and the table diff exits 0. The claim script needs its call updated. That is experiment work.

### Data lockdown (step 5)

`harvest.py --offline RAW data/pins data`, then `generate.py`, `scripts/generate/functions.py`, and `scripts/generate/examples.py`, left `git status --porcelain` empty. RAW departs from the ticket: the main checkout's `data/raw/` holds 63 of the 302 pinned pages and fails on `1373687907.wiki`. The complete cache sits in another worktree's `raw/` folder (302 pages). An offline harvest from it rebuilt every generated file under `data/` byte for byte. Each fresh folder holds `inputs.sha256`, written before its first paid call.

### Paid jobs (step 6)

Each job checked the pinned binary with `sha256sum -c` first, ran through `sdlc/scripts/live` with `BENCH_WORKERS=4`, and logged the recording's input-token total and the guard's status before and after in its `ledger.txt`. `--max-tokens` is the cap plus 4 times the job's largest recorded request. Input tokens are summed from the fresh recordings, at 0.042 dollars per million.

| Job | Cap | Input tokens sent | Dollars |
| --- | --- | --- | --- |
| The 1,501 | 600,000 | 534,901 | 0.0225 |
| Open book, 196 questions | 2,640,000 | 2,394,007 | 0.1005 |
| RAD picks | 211,000 | 191,308 | 0.0080 |
| RAD Jev k=2 and BM25 k=2 answers | 747,000 | 684,059 | 0.0287 |
| RAD MiniLM k=2 and Jev k=1 answers | 570,000 | 516,769 | 0.0217 |
| RAD2 picks with options | 249,000 | 226,302 | 0.0095 |
| RAD2 answers | 560,000 | 506,055 | 0.0213 |
| One line, 38 questions | 15,000 | 13,171 | 0.0006 |
| Function suite, two attempts | 1,071,000 | 933,854 | 0.0392 |
| Pipeline | no stop, 136,000 reserved | 101,879 | 0.0043 |
| Examples 01 to 11 | 99,500 in all | 89,288 | 0.0038 |
| Total | 6,898,500 | 6,191,593 | 0.26 |

- No job stopped at its cap. The total stayed under the planned 6.5M and the 1 dollar ceiling. The guard charged 7,737,361 tokens of reservations (431,499,418 to 439,236,779).
- The function suite's first attempt stopped early on a backend timeout (`recognize-15-w06`, exit 4) after 775,879 tokens. No gap was written. It resumed into the same folder with a cap of 295,121, the cap minus spent, and sent 157,975 more. The timed-out request may have been billed without a recording. It is one request, at most 48,300 tokens.
- A runner fault stopped the first pass of the eleven example jobs before any guard call. No charge was made. The examples ledger says so.
- Every fresh `gaps.tsv` is absent: no call was refused. No 401 or 429 row was removed.
- Every response names model `jev-1.13.0`. No fresh file holds the key. Recordings hold `adapter`, `request`, `response`, `schema`, and `url`, and no header.

### Measure

The old example files come from an earlier commit. `thinkthen diff` ran through `scripts/score/diff_guard.sh`, with the question keys where the run has them.

| Old against fresh | Tool | Pairs | Changed | Right, old to new |
| --- | --- | --- | --- | --- |
| The 1,501 | diff | 1,501 | 78 | 1,058 to 1,061 (23 gained, 17 lost, p = 0.43) |
| Open book | diff | 196 | 1 | 187 to 186 |
| RAD | diff | 980 | 61 | 605 to 616 of 784 keyed |
| RAD2 | diff | 490 | 31 | 253 to 250 of 294 keyed |
| One line | diff | 38 | 1 | 36 to 37 |
| Function suite | Python | 2,024 records | 961 with any value or probability moved | table below |
| Pipeline | Python | 18 songs | 2 memory rows | memory arm 4 to 5 of 18. Other arms and all checks the same |
| 01-decide | diff | 16 | 1 | Taxman, cold, 0.55 to 0.48, yes to no |
| 02-choose | diff | 10 | 0 | |
| 03 to 10 | Python | 6, 16, 24, 12, 2, 4, 1, 1 | 5, 13, 11, 11, 2, 0, 1, 1 with any value or probability moved | |
| 11-audit cold | diff `--no-digest` | 70 | 10 | a new question: 56 right under the old wording, 50 under the new |
| 11-audit context | diff `--no-digest` | 70 | 0 | a new question: 70 and 70 |

The 11-audit pairs cross wordings, so they compare a new question and measure no change. The 12-diff example now lists 20 fixes, against 14. The suggested cut moved from 0.85 to 0.78, so `audit-0.85.json` gave way to `audit-0.78.json`. The committed audit names equal the fresh folder's.

### Numbers that moved (step 7)

- Front page, Jev from memory: Beatles-only 67.5% to 68.0%, median time 0.29 s to 0.32 s. Overall 70.8% to 71.2%. Dollars per 1,000 stay 0.015.
- Function table, Jev: decide 0.680 to 0.693, choose 0.712 to 0.715, tag 0.291 to 0.272, score 0.695 to 0.683, filter 0.627 to 0.644, rank popularity 0.639 to 0.636, rank date 0.804 to 0.811, find 0.635 to 0.654, annotate singer 0.278 to 0.304, annotate year 0.418 to 0.390, recognize song precision 0.226 to 0.194, person precision 0.980 to 0.960, album precision 0.389 to 0.359, relate F1 0.719 to 0.704, precision 0.867 to 0.864, recall 0.614 to 0.594. Annotate album, song recall, person recall, and album recall stay the same.
- `reports/results.md`: the McNemar counts, Jev's ECE (0.020 to 0.028), popularity (49% to 51%, 73% to 74%), multi-hop (22 to 25 of 60), and controls (lexical-trap control 69% to 67%, near neighbor 80% and 82% to 73% and 83%).
- `reports/open-book.md` and `reports/rad.md` keep their 2026-09-23 sections and add "Fresh run of 2026-09-25".
- Example READMEs: every fenced block is the output of the jq command above it. The prose follows it. `11-audit` and `12-diff` take the new wording and cut. Their slide paragraphs say the slide shows the older run.

### Downstream files and checks

- `results/tables/` from `analyze.py` and `scripts/score/functions.py table`. `results/history.tsv` gained 12 rows. None was replaced. Figures from `scripts/figures/all.sh` with kuva and the system `python3`.
- `JEV` in `tests/published.py` moved to 2026-09-25. `COVERED_FILES["Jev"]` in `tests/test_audit_contract.py` moved from 11 to 7: the fresh run has more ties that hold the right answer, so audit covers fewer question files. Every covered file still matches.
- `tests/test_table.py` gained `ReadmeTableTest`. The front page's table is a short form of `table.py`'s, so the test checks each shown cell: the Beatles-only share, the median time, and the dollars rounded to three places.
- `tests/test_examples.py` reads a number written as `2e-6` as `0.000002`. The fresh 12-diff McNemar p is 2e-6, and jq prints it in decimals.
- `python3 -m unittest discover -s tests` passes with and without `THINKTHEN_BIN`. `./run.sh` with no key replays the fresh 1,501 and every example. The path grep prints nothing.

### Step 7 commit

The step 7 commit swaps in the fresh examples and holds the downstream files. Code review 2 reviews it by its hash.

### Replay proof (step 8)

The proof ran with the key and address unset and `THINKTHEN_BIN` set to the pinned binary. It replayed every fresh folder in the worktree and in a fresh clone of the step 7 commit, with the commands in Replay proof. The loop compared the two replays byte for byte, and each replay with the live files once `cached` and `requests_sent` were stripped. It passed for all 19 folders: the five `thinkthen.sh` runs (2 files each), the function suite (11), the pipeline (16), and the twelve examples. `sha256sum -c inputs.sha256` passed in all eight fresh folders in both checkouts. Every `run.txt` names the pinned binary's SHA-256.

### Code review 2 fixes

Code review 2 accepted the code and the numbers and returned two prose findings. Both are fixed. `reports/baselines.md` now gives Jev against embeddings as 488 against 95 discordant pairs on Beatles-only questions. The figure comes from the rebuilt `results/tables/mcnemar.tsv`. The open-book paragraph in `README.md` now names the run behind each number. It gives the fresh 186, 76, and 0.42 s beside the 2026-09-23 187, 62, and 0.54 s. The 68% to 97% weighting belongs to the 2026-09-23 run only. The tests pass with `THINKTHEN_BIN` set to the pinned binary: 170 run and 2 skip. `./run.sh` with no key passes.

### Gaps for Ian

1. Closed 2026-09-25. The main checkout's `data/raw/` now holds all 302 pinned pages.
2. The talk's slides for 11-audit and 12-diff and the local experiment's `02-filter-085.sh` use the old cut of 0.85 and the old wording. The talk's ticket owns them.
