# 0001 Show retrieval-augmented decisions with shipped ThinkThen commands

Owner: Claude marketing session. Status: landed 2026-09-24. Code review ACCEPT at a7beabc. Ticket review 1 (fresh reviewer, 2026-09-24) returned seven findings, all taken below.

## Why

The talk's pitch moves from "Jev knows things" to "Jev decides well when you hand it the facts." A reader needs to see that pipeline written with commands they can run today. The run also answers the three open questions in the deck repo's `sdlc/planning/thinkthen-asks.md` about a context input.

## Work

Red first. A test drives `scripts/run/rad_pipeline.sh` with the fake binary in `tests/fixtures/`, as `tests/test_run.py` does, and fails before the script exists.

`scripts/run/rad_pipeline.sh` calls `${THINKTHEN_BIN:-thinkthen}` and `jq` only, with `--record` on a live run and `--replay` otherwise. It builds no request in Python. The committed recording lets a clean checkout replay it with no key.

1. One question. `choose --details` picks among the 28 catalog sections for "Who sang lead on Octopus's Garden?". `jq` sorts the pick's probabilities, takes the top two sections, and glues them before the question. `choose` answers. Compare with the "Jev picks, k = 2" row of `reports/rad.md`.
2. One context over many records: the 18 Abbey Road songs, tagged with Lennon, McCartney, Harrison, Starr. Three arms:
   - no context (memory),
   - glued: the Abbey Road section and the song in one text,
   - apart: `{context, song}` records sent with `tag --jsonl --field /context --field /song`.
   Truth is the `lead_vocals` column of `data/songs.tsv`. A song counts right when its tag set matches exactly. The section spells out "lead:" for each song, so the context arms are a lookup. The report says so.
3. Grounding. One `annotate --jsonl` case over the apart records, with a correctness check and the grounding check `{"decide": "Is every claim in the output supported by the context?", "on": ["/context", "/output"]}` from `specification/annotate.md`.
4. `reports/rad.md` gets a section "With shipped commands": the script, a table of right answers, input tokens, and time per arm, and one sentence per open question: does gluing read cleanly, does apart score differently from glued, does the grounding check need the context as its own field.

## Limits

- Live cap: 200,000 input tokens. The section is about 450 tokens. Three arms over 18 songs plus the single question sit far under it.
- No change to ThinkThen. A clean-checkout run sets `THINKTHEN_BIN` to a local build.

## Done when

The red test turns green, the replay test passes with no key, the full unit suite passes, a fresh reviewer accepts the code, and the asks file says send or drop for the context input, with the evidence. Committed and pushed.
