# 0004 Find a RAD example Jev does not already know, and test the grounding check on wrong answers

Ticket: [0004](../tickets/0004-a-rad-example-jev-does-not-know.md). Branch `ticket/0004-rad-example`. Built 2026-09-24 by a Claude build session on the local Linux machine.

## What landed

- `scripts/run/rad_pipeline.sh` reads its single-question cases from `CASES`. Each line holds a name, the question, the needed section, the right option, and the options. The hardcoded `abbey_road` and `starr` are gone. Each case asks from memory, then picks, then answers. Octopus's Garden stays as the control. Tomorrow Never Knows is the new case.
- A second `annotate` call checks the 18 Abbey Road songs with a wrong singer planted in `/output`. Its score row is `wrong_singer`, and `checks.tsv` gains three columns for it.
- A live run now uses `--cache`, so a rerun sends only the requests its recording lacks.
- `scripts/score/rad_table.py candidates RUN...` lists the candidate questions with no new calls.
- `results/runs/2026-09-24-pipeline-jev2/` holds the run, its recording, `ledger.txt`, and `tries/` with every rejected try.
- `reports/rad.md` gains "A question Jev does not know". `README.md` and `paper/notes.md` no longer say "after 0.1".

## Decisions

Ian can overturn either one.

- Each case asks from memory in the pipeline's own wording. The ticket asked only for the pick to be confirmed live. The memory call cost about 370 tokens per case and showed that Jev knew all six single-singer candidates when the question names the song.
- The chosen question asks for a year. The ticket preferred a lead-singer question, and none of the recorded singer candidates missed from memory in the pipeline's wording. A screen of seven well-known forward questions found three misses. Tomorrow Never Knows had the most page views and the surest miss.

## Commands and results

- Red: `THINKTHEN_BIN=<thinkthen>/target/release/thinkthen env -u THINKTHEN_API_KEY python3 -m unittest tests.test_rad_pipeline` failed 2 of 2 before the script changed. The replay test failed with "no recording in .../2026-09-24-pipeline-jev2". It no longer skips when the recording is missing.
- Red: `python3 -m unittest tests.test_score_rad` failed with 1 error before `candidates` existed. It passed after.
- Live: five jobs under `<thinkthen>/sdlc/scripts/live`, listed in `ledger.txt`, all exited 0. Tries in order: Boys, Chains, then For No One, Martha My Dear, Good Night, and Dizzy Miss Lizzy. Every pick held the needed section, and every memory answer was right. The screen then found Tomorrow Never Knows, Michelle, and Act Naturally wrong from memory. The last job ran Tomorrow Never Knows.
- Tomorrow Never Knows: memory said 1967 (0.59). The pick put Revolver first (0.91) and Sgt. Pepper second. The answer said 1966 (1.0), the truth.
- Octopus's Garden: memory said Starr (0.99), the pick missed Abbey Road, and the answer said Starr (0.90).
- Wrong singer: `grounded` said no on 18 of 18, and `correct` said no on 18 of 18. The right-answer `annotate` row still agrees with the truth on 18 of 18.
- Replay: with `THINKTHEN_BIN` set and the key unset, `python3 -m unittest tests.test_rad_pipeline` ran 2 tests, OK.
- Full suite: `env -u THINKTHEN_BIN python3 -m unittest discover -s tests` ran 170 tests, OK, 8 skipped. With `THINKTHEN_BIN` set and the key unset it ran 170, OK, 2 skipped.

- The ticket 0001 run `2026-09-24-pipeline-jev/` still replays with the script at origin/main 48d9be7, before this ticket. The reviewer replayed it that way with no key, and its `scores.tsv` matched exactly. The new run `2026-09-24-pipeline-jev2/` reproduces every number in the "With shipped commands" table.

## Tokens spent

64 new requests: 47,904 input and 4,653 output tokens, or 0.0020 dollars. The ticket's cap was 100,000 input tokens. The guard reserved 135,000 across the five jobs, from 427,769,418 to 427,904,418 charged. The reservations passed the cap. The tokens sent did not.

## Open

- Code review by a fresh reviewer has not run yet.
- The lesson for the deck: a question that names the song lets Jev answer singer questions from memory. The bench wording gives the title as the text and asks about "it".
