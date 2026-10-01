# 0024 Publish the five-model report on the knowledge questions, with its statistics

Owner: the queue owner. Status: accepted after ticket review 1; waits for 0023.

## Why

The deck and the thinkthen site will cite one bench report for the field of models. The marketing lead asked for it on 2026-09-30 (a mailroom message). Ian approved four steps the same day: land the new Jev and Liquid runs; commit the Kev and Nimble runs with their build and date, and keep the older Liquid run as history; move the five-model scoring into the bench's own scripts; and publish one report the site can cite. Ian also asked for the statistics in the bench: intervals, paired tests, and the hard and easy split.

Today the figures exist only in the local experiment `~/workspace/experiments/418-beatles-five/RESULTS.md`, made by its `score.py`. Three of its runs are not committed.

## Prior evidence

- Experiment 418 scored six runs on the 1,501 knowledge questions with the bench's credit rule (`scripts/score/score.py`) and Wilson intervals. Its figures: Jev 70.5% (aec7819bb), Liquid d1 63.8% (2c5ac772b, 2026-09-29), Nimble 9B through Ollama 51.9% (aec7819bb), Kev 4B 47.2% (2c5ac772b), Laya 35.8%, GLM-5.3 Flash 96.7%.
- Experiment 413 defined the hard set of 505 questions: the lexical traps and their controls, multi-hop, none-of-these, reversal, shared lead, and the year questions. Its id list is `results/runs/2026-09-29-thinkthen-liquid-d1free-hard/ids.txt`, untracked.
- Ticket 0023 commits `2026-09-30-all-jev` and `2026-09-30-all-liquid-d1`, both on build aec7819bb. The new Liquid run scores 64.3% on the knowledge questions. That run is the Liquid row; the deck does not keep 63.8.
- `scripts/score/stats.py` already holds `wilson` and an exact `mcnemar`. `scripts/answers/report.py` already writes `head-to-head.md` from the answers table.
- Untracked on the build machine: `results/runs/2026-09-29-thinkthen-kev-4b` (8 MB), `2026-09-29-thinkthen-liquid-d1free-full` (8.2 MB), `2026-09-29-thinkthen-liquid-d1free-hard` (2.9 MB), and `2026-09-30-thinkthen-nimble-taste` (a small taste run). The full Nimble run is in `~/workspace/experiments/418-beatles-five/runs/nimble` (3.1 MB).

## Retained behavior

- Every committed run folder keeps its bytes. The published tables keep their values, except the new rows and columns this ticket adds.
- `score.py` stays the authority for the credit rule. A tie at the top that holds the truth earns its share.
- Reader-facing level names stay "From memory", "Extra context" and "Exact context".

## Changes

1. Commit `2026-09-29-thinkthen-kev-4b` and the full Nimble run, as `results/runs/2026-09-30-thinkthen-nimble-9b`. Commit each run's recording as it stands; the Nimble run holds `recording/thinkthen.sqlite`. Each gets a `run.txt` in the fields of `2026-09-30-all-jev/run.txt`: the model, the backend (a loopback System One address), the machine described as its `machine:` line does, the ThinkThen build, the date, and a line saying the recording was not replay-checked here. Commit `2026-09-29-thinkthen-liquid-d1free-full` under `results/archive/runs/`, outside `analyze.py`'s discovery, labeled with its build 2c5ac772b. Leave out `2026-09-30-thinkthen-nimble-taste`, which is a probe.
2. Commit the hard set, the 505 ids of `results/runs/2026-09-29-thinkthen-liquid-d1free-hard/ids.txt`, as `questions/hard.txt`. A short header or README line says how it was chosen and cites experiment 413. The other 996 questions are the easy set. `2026-09-29-thinkthen-liquid-d1free-hard` stays out; it is a subset rerun the full run supersedes.
3. Extend `scripts/score/table.py` so a second table, the five-model table, prints from committed runs only. Keep `table.results()`'s five-column shape for the README headline and its test. Each model row of the new table shows:
   - Beatles-only (1,313), overall (1,501), hard (505) and easy (996), each with its 95% Wilson interval;
   - the exact McNemar p against Jev, paired by question id over the 1,501 questions, right or wrong by the scorer's `default()` verdict (a tied pick counts wrong), with the counts only one side got right. These are the values `results/tables/mcnemar.tsv` already computes;
   - the run folder, the ThinkThen build ("chat script" for GLM-5.3 Flash) and the date.

   Rows: Jev and Liquid d1 on aec7819bb first, then Nimble, Kev and Laya, then the GLM-5.3 Flash reference, then the baselines and chance as today. The older Liquid run appears in a history line, not as a second row.
4. `reports/results.md` "Main results" keeps its current table, with the new Jev and Liquid rows, and adds the five-model table below it. A short note says: each figure is one run; builds differ across rows; the knowledge questions ask from memory only; Liquid d1 left three questions unanswered (rate-limited), and they score wrong. The McNemar and calibration bullets beneath are recomputed from the new runs.
5. Add `reports/models.md`, the page the deck and site cite. It holds the table from change 3, one paragraph per model naming its run, build, machine and date, and the hard set's definition. It contains no figure absent from the generated table. The front `README.md` and `reports/README.md` link it.
6. Leave out the OpenAI Decisions API. It is announced but unreleased. The bench has no run of it and no readable source.

## Proof

- A test regenerates the table from committed runs and matches `reports/models.md` and the "Main results" table byte for byte.
- A test checks `questions/hard.txt`: 505 unique ids, each in `questions/*.jsonl`, and its complement there is 996.
- The Jev, Nimble, Kev, Laya and GLM-5.3 Flash overall, Beatles-only, hard and easy figures match experiment 418's `scores.json` for the same run folders within rounding. Liquid uses the new run, which 418 did not score, so only its overall figure is pinned, at 64.3%.
- The full test suite passes, apart from failures recorded in ticket 0023 with their reason.
- No live call.

## Deferred gaps

- Liquid d1's function-suite table waits for its 513 rate-limited gaps to be asked again (ticket 0023).
- Kev, Nimble and Laya on the function questions and on build aec7819bb or later run on the M5, one at a time.
- Converting the committed recordings to the question store is ticket 0025.
