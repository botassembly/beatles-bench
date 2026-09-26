# 0004 Find a RAD example Jev does not already know, and test the grounding check on wrong answers

Owner: Claude marketing session. Status: landed 2026-09-24. Code review ACCEPT after two doc fixes at 68b908b.

## Why

Ticket 0001's single question, Octopus's Garden, proved nothing: Jev's pick missed Abbey Road and Jev answered from memory. The deck needs one question where Jev misses from memory, picks the right section, and then answers right. Ticket 0001's grounding check saw only right answers, so it never showed it can catch a wrong one. Ian also ruled on 2026-09-24 that marketing names no version, so the bench stops saying "after 0.1".

## Work

1. Search the recorded runs with no new calls: `results/runs/2026-09-23-thinkthen-jev` (closed book), `-rad`, and `-rad2`. List questions where closed book is wrong, the k = 2 pick holds the needed section, and the answer is right. Prefer a lead-singer question about a song a general audience knows. Record the candidates and the choice in `reports/rad.md`.
2. Add the chosen question to `scripts/run/rad_pipeline.sh` as a second single-question case beside Octopus's Garden. Keep Octopus's Garden as the control, and keep its report text saying Jev answered from memory.
3. Grounding on wrong answers: add a case to the pipeline's `annotate` step with the 18 Abbey Road records carrying a wrong singer in `/output`. The grounding check should say no. Report how many it catches.
4. Red first: the replay test fails until the new recordings exist.
5. Replace "after 0.1" in `README.md` and `paper/notes.md` with plain words: audit and diff are prototyped here and are coming to ThinkThen.

## Limits

Live cap: 100,000 input tokens.

## Done when

The replay test passes with no key, the full suite passes, a fresh reviewer accepts, and the work is committed and pushed.

## Ticket review 1 (fresh reviewer, 2026-09-24): four findings, all taken

- Join the runs on question id after stripping the `jev-k2/` and `pick/` prefixes. "Holds the needed section" uses `rad.py needed()` and `rank-jev.tsv`, as `scripts/score/rad_table.py` does.
- Make each case's question, needed section, and answer settings in `rad_pipeline.sh`. Remove the hardcoded `abbey_road` and `starr`.
- The pipeline asks in its own wording. Confirm the pick live. If it misses, move to the next recorded candidate and report each try.
- The wrong-singer case gets its own score row: "caught N of 18".
