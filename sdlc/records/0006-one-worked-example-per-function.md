# 0006 One worked example per function, cold and with context

Ticket: [0006](../tickets/0006-one-worked-example-per-function.md). Branch `ticket/0006-worked-examples`. Built 2026-09-25 by the builder on the local Linux machine. A fresh review on 2026-09-25 returned three wording and record findings, all taken, and no code finding.

## What landed

- `examples/01-decide/` to `examples/10-relate/`, in the talk's order. Each folder holds its case files, any card the cases name, `recording/`, `outputs.jsonl`, `timing.tsv`, `lists/` for filter and rank, `run.sh live|replay`, `slide.png`, and `README.md`. No case was refused, so no folder has `gaps.tsv`.
- Each README gives the question in plain words, the slide, a plain `thinkthen` command that replays from the folder's recording, an output excerpt with the `jq` command that prints it, and a "With context" section or the reason for none. The choose and relate pages carry the photo credits for the four 1964 faces, taken from the talk's credits.
- `examples/context-article.md` covers the three Wikipedia flips: the pinned revisions, the fetch rule with its script, the commands, and the labels and probabilities only.
- `scripts/generate/examples.py` writes every case file and card from `data/songs.tsv` and `catalog.entry()`, with each case's truth.
- `scripts/run/catalog.py` gains `entry(song, albums)`: the section header, then the song's line with its first album. `catalog()` output is byte for byte unchanged.
- `scripts/run/functions.py` reads `BENCH_TESTS`, the case files to ask. Unset, it keeps the suite's eight, so the existing runs replay unchanged.
- `tests/test_examples.py`: the ten folders exist and hold their parts; the committed cases equal the generator's output; every decimal in a page's fenced json block appears in that folder's `outputs.jsonl` or `lists/`; each `jq` command on a page prints the block below it; with `THINKTHEN_BIN` set, each folder replays with no key and its answers and lists match byte for byte. The number check names `context-article.md` as its one exception.
- `tests/test_catalog.py` gains `entry()` cases for a single (She Loves You) and an album track (Octopus's Garden).
- `.gitignore` adds `examples/*/replay/`. The root README and `scripts/README.md` point to `examples/`.

## Decisions (the owner can overturn these)

- decide keeps the slide's own question too. `decide-love.jsonl` asks "It is a love song." of the four slide songs, so the slide's query and output are stored. The ticket's Abbey Road question runs cold and with context over the four slide songs plus A Day in the Life (the talk's context slide) and Something (a true yes).
- score uses ten levels, "about 0 minutes" to "about 9 minutes", per Ian's change of 2026-09-25. The score reads as minutes. No band run was recorded.
- tag runs the slide's five labels. The scratch run had a sixth, "children's song".
- find with context sends each of the ten songs as its own record in the context shape. All ten go out in one request, so the ten entries form one text.
- annotate uses the talk's card: three `choose` fields, each with `"threshold": 0.8`. The context card changes only the opening sentence.
- recognize keeps the talk's `--threshold 0.01`. relate keeps the talk's fourteen names, their order, and its question file.
- The article demo reuses the three calls made for the talk on 2026-09-25 (jev-1.13.0, `--no-cache`). The page's fetch rule rebuilds their text byte for byte from the saved parse API answers, and the annotate card equals the talk's. Rerunning them would have cost about 14,700 tokens and pushed the total to within 500 of the cap. Ian confirmed on 2026-09-25 that no Wikipedia text enters the repository.
- Each page's prose says the slide came from an earlier call. The slides were drawn from the talk's scratch runs. Their numbers differ from the committed ones by a few points.

## Commands and results

- Live: the thinkthen guard `sdlc/scripts/live --max-tokens 60000 JOB`. The job ran each folder's `run.sh live` with `THINKTHEN_BIN` set to a release build of thinkthen 0.0.1 made on 2026-09-24 (model jev-1.13.0), `BENCH_WORKERS=4`, and `BENCH_MAX_INPUT_TOKENS` set to what remained of 44,000. Ledger before: 427,934,418 charged. After: 427,994,418.
- Spend: 92 calls, 93 requests, 44,874 input and 6,096 output tokens. recognize took 8,092 input tokens and relate 3,453. The ticket's cap is 60,000.
- Replay: `env -u THINKTHEN_API_KEY examples/NN-FUNCTION/run.sh replay` for all ten matched `outputs.jsonl` and `lists/` byte for byte. Every plain command on the pages also replays with `--replay recording`.
- Suite: `python3 -m unittest discover -s tests` ran 179 tests, OK, 10 skipped. `THINKTHEN_BIN=.../release/thinkthen env -u THINKTHEN_API_KEY python3 -m unittest discover -s tests` ran 179 tests, OK, 2 skipped. The existing function runs replay unchanged.
- No credential text in any recording (`grep -ril` for authorization and bearer found none).

| Example | Cold | With context |
| --- | --- | --- |
| decide, Abbey Road | 4 of 6 right at 0.5; A Day in the Life yes 0.94, Taxman yes 0.55 | 6 of 6; Something 0.95, the rest 0.03 to 0.04 |
| choose, lead singer | 4 of 5; She Loves You John 0.3, duet 0.29 | 5 of 5; duet 0.88 |
| score, minutes | 5 of 8 within 30 s, 7 of 8 within a minute | 8 of 8 within 30 s |
| filter, Abbey Road at 0.7 | keeps 6, 5 right; misses Octopus's Garden (0.66) | keeps the 6 right songs |
| find, first release | Love Me Do 0.55, right | Love Me Do 0.74, right |
| annotate, bar 0.8 | 4 fields filled, all right; 2 not sure | 6 of 6 filled and right |
| relate, bar 0.8 | 12 of 13 bright edges right; Octopus's Garden to Revolver 0.81 | none |

## Stopped or changed from the ticket

- Work item 5: the thinkthen issue already exists. `sdlc/issues/2026-09-25-the-site-needs-a-beatles-bench-section.md` landed on thinkthen main at e70bddab and asks for the section this ticket feeds. No second issue was filed.
- Work item 2: `07-find` has no `lists/`. find returns one row, so `outputs.jsonl` already holds the whole answer.

## Bench data checked

The truth for every example comes from `data/songs.tsv`. None was found wrong. Three points to know:

- Hey Jude's 7:08 (428 s) comes from the Past Masters track listing. Other sources list the single at 7:11. The score page uses 7:08.
- She Loves You's entry names Past Masters as its first album, because the bench follows the UK albums. It sits under "Singles".
- The recognize sentence is the talk's own. It says Abbey Road Studios, and in 1969 the studio still had the name EMI Studios. The page says so.

## ThinkThen issues found (thinkthen 0.0.1, the release build of 2026-09-24)

For the queue owner to file. None blocked the work.

1. `recognize --dry-run` does not print what would be sent. Command: `printf '%s' "Ringo Starr wrote Octopus's Garden on a boat off Sardinia, and the band recorded it at Abbey Road Studios for the album Abbey Road." | thinkthen recognize person song album place --threshold 0.01 --dry-run`. It printed `{"tokens":26,"detection_questions":26,"kind_questions":26,"requests":1}`. The help says "Print what would be sent and stop." Expected: the request, as `decide --dry-run` prints it, or at least its size. The real request held 52 questions and cost 8,092 input tokens, and nothing in the dry run warned of that.
2. `find --details` names each line by its place, and the output never lists the places. Command: `jq -c '.records[]' examples/07-find/find-cold.jsonl | thinkthen find 'These are songs by the Beatles. Which one did they release first?' --jsonl --field /input --details`. The records carry ids u01 to u10. The answer keys its probabilities and its pick as u001 to u010, and `value` is the record with id u05. Expected: probabilities keyed by the record's own id, or the details list which line each key means. A reader has to rebuild the map from the input order.
3. recognize's detection question says the snippet comes "from a news document" and lists organizations, events, and products, whatever kinds the call names. Seen in the recorded request for the command in item 1. Expected: wording that fits any text, and the kinds the user gave.
4. Not filed. recognize rounds strength unevenly. The same output gives 1.0, 0.99, and 0.97 for three names, and 0.9702 and 0.9455 for Abbey Road Studios and Abbey Road. Expected: one precision throughout. The queue owner checked the spec. It rounds strength to four places, and 0.97 equals 0.9700, so this is not a bug.

## Left open

- The slides were drawn from the talk's scratch runs. Redrawing them from the committed outputs would make each slide match its page. The talk's owner decides.
- The docs pages belong to the thinkthen queue. Other models on the examples are deferred.
