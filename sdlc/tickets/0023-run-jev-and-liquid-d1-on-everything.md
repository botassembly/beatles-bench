# 0023 Run Jev and Liquid d1 on the whole bench, and compare them

Owner: the queue owner. Status: waits for 0021 and 0022.

## Why

Ian wants Jev and Liquid's d1 compared across every function, not only the knowledge questions. Both backends speak the same System One wire, and d1:free is free today.

## Prior evidence

- Local experiment 413 ran the 1,501 knowledge questions on d1:free through the same command: 63.8% right against Jev's 70.2%, with Jev ahead on the hard half by an exact McNemar test. d1 reported input tokens only and billed nothing.
- d1 refused a null `false` criterion with 422. ThinkThen main `6cbf465df` stopped sending null criteria. Build `0959ae374` includes it.
- The address is `https://api.liquid.ai/decisions/v1` and the model `d1:free`. The key lives in `LIQUIDAI_API_KEY` and is passed as `THINKTHEN_API_KEY` for d1 runs only.

## Retained behavior

- Earlier run folders and published tables keep their bytes. The new runs are new folders.
- A run never commits a key or a header. Recordings hold request and response bodies only.

## Changes

1. Pin ThinkThen main `0959ae374` for both backends. Each run's `run.txt` names the build's SHA-256.
2. Run every question in `questions/catalog.jsonl` on Jev, `jev-1.13.0`, and on Liquid, `d1:free`, into `results/runs/2026-09-30-all-jev` and `results/runs/2026-09-30-all-liquid-d1`. Each run starts from an empty recording and records every exchange.
3. Rebuild the answers table and the generated reports from ticket 0022.
4. `reports/results.md` gains a short "Jev and Liquid d1" section that points to the generated reports and names the three largest differences by function and level.
5. The front `README.md` results table gains a d1 row.

## Proof

- A replay of each run with the key unset gives the same answers.
- The generated reports rebuild with no key and no network.
- Spend: Jev under a 20,000,000-input-token cap, about $0.84 at most. d1 bills nothing. Each run's plan upper bound is checked first.

## Deferred gaps

- Repeat runs to measure run-to-run spread on each backend.
- GLM-5.3 Flash and Laya on the new levels.
