# 0023 Run Jev and Liquid d1 on the whole bench, and compare them

Owner: the queue owner. Status: accepted after ticket review 1; waits for 0021 and 0022.

## Why

Ian wants Jev and Liquid's d1 compared across every function, not only the knowledge questions. Both backends speak the same System One wire, and d1:free is free today.

## Prior evidence

- Local experiment 413 ran the 1,501 knowledge questions on d1:free through the same command: 63.8% right against Jev's 70.2%, with Jev ahead on the hard half by an exact McNemar test. d1 reported input tokens only and billed nothing. One backend timeout cleared only at two workers.
- d1 refused a null `false` criterion with 422. ThinkThen main `6cbf465df` stopped sending null criteria. Build `0959ae374` includes it, and `thinkthen check` against d1 passed on it on 2026-09-30 with `--timeout 90`, after a first try timed out.
- ThinkThen ticket 0334 (ADR 0114) added named backends. `--backend liquid` reads the Liquid key from its own variable, and `thinkthen check --backend liquid` passed on build `aec7819bb` on 2026-09-30. `--backend typesafe` reads its own variable; the unnamed default still reads `THINKTHEN_API_KEY` at TypeSafe's address.
- A second agent on the M5 has Ollama 0.35 serving Nimble 9B and a Kev server, both speaking System One natively. Ollama refuses object-valued criteria descriptions, so it waits for ThinkThen's portable description rule.

## Retained behavior

- Earlier run folders and published tables keep their bytes. The new runs are new folders.
- A run never commits a key or a header. Recordings hold request and response bodies only.

## Changes

1. Pin ThinkThen main `aec7819bb` for every backend. Each run's `run.txt` names the build's SHA-256 and the model name each backend reports. `d1:free` is a name the vendor may repoint, so the report dates every d1 figure.
2. Probe first: 5 cases of every function and level on d1. A refused request shape goes to the run's `gaps.tsv`. A test that d1 refuses entirely gets no d1 cell and a note in the report.
3. Run every question in `questions/catalog/catalog.jsonl` on Jev, `jev-1.13.0` on the default backend, and on d1 with `--backend liquid`, into `results/runs/2026-09-30-all-jev` and `results/runs/2026-09-30-all-liquid-d1`. Each run starts from an empty recording and records every exchange. Each folder holds the knowledge `answers.jsonl` and the suite `outputs.jsonl` and `lists/`. d1 runs at 2 workers with `--timeout 90`. A run that stops resumes from its recording the same day.
4. The new Jev run becomes the Jev row in every table, and the 2026-09-26 run stays as history. `analyze.py` labels the d1 run "Liquid d1". `score_suite.py` reads the new Jev run. `results/runs/README.md` names both runs.
5. Rebuild the answers table and the generated reports from ticket 0022.
6. `reports/results.md` gains a short "Jev and Liquid d1" section. It points to the generated reports, names the three largest differences by function and level, and says each figure comes from one run.
7. The front `README.md` results table gains a Liquid d1 row.

## Proof

- A replay of each run with the key unset gives the same answers.
- The generated reports rebuild with no key and no network.
- Spend: Jev under a 20,000,000-input-token cap, about $0.84 at most. The estimate is 8 to 9 million tokens. d1 bills nothing. Each run's plan upper bound is checked first.

## Deferred gaps

- Repeat runs to measure run-to-run spread on each backend.
- GLM-5.3 Flash and Laya on the new levels.
- Nimble through Ollama and Kev, run from the M5 against the same catalog and build, in the same run-folder layout, so the answers table takes them in. They follow this ticket once the portable description rule lands.
