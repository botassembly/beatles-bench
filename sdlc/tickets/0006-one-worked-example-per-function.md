# 0006 One worked example per function, cold and with context

Owner: Claude marketing session. Status: done. Ticket review 1 returned nine findings, and review 2 returned six. This version takes all fifteen.

## Why

Ian asked on 2026-09-25 for each function slide in the ThinkThen talk to store its query and its output here, in the bench. A section of the ThinkThen docs site will then walk through each slide. Each page shows the picture, the code, and the output. Each page also shows how context fills that function's gap.

The slides currently run in a scratch folder of the marketing session. The session made live Jev calls by hand (jev-1.13.0, `--no-cache`) and noted every source. No recording replays them.

## Prior evidence

- The scratch notes give each slide's command, question wording, input list, and truth check against `data/songs.tsv`.
- Workspace experiment 258 scored all 276 songs that have a length:
  - Cold: mean error 0.65 minutes. 217 of 276 land within a minute. Spearman 0.52.
  - With the song's catalog line as context: all 276 land in the right one-minute band. Spearman 0.91.
- Three cold misses flipped once the song's Wikipedia article went in as context:
  - Octopus's Garden, album: Revolver 0.49 and White Album 0.49 became Abbey Road 1.00.
  - She Loves You, singer: John 0.30 became John and Paul 0.99.
  - A Day in the Life, on Abbey Road: yes 0.94 became p(yes) 0.02.
- Ticket 0004 and `reports/open-book.md` hold the bench-wide open-book numbers.

## Retained behavior

The question set, the runs under `results/runs/`, the tables, the reports, and `catalog()` output all stay as they are. The rule in `data/SOURCES.md` stands: no Wikipedia sentence is stored in the repo.

## Design

- **Runner.** Each example is a case folder for `scripts/run/functions.py`, run through `BENCH_FUNCTIONS=examples/<NN>-<fn>`.
  - The runner already strips `cached` and `requests_sent`.
  - It writes a replay to `replay/` and leaves the committed files alone.
  - It accepts the absolute paths the live guard uses.
  - A new `BENCH_TESTS` variable names the case files, comma-separated. When unset, `TESTS` stays as it is, so the existing runs replay byte for byte.
  - Cold and context cases share one `recording/` per folder.
  - `.gitignore` adds `examples/*/replay/`.
- **Context entry.** Add `entry(song, albums)` to `catalog.py`. It returns the album header line and then the song's `line(s, True)`, so every song names its album.
- **Context record.** A context record takes the shape `ask.py` sends: `{"id": ..., "input": "Catalog:\n<entry>\nText: <title>"}`, passed with `--field /input`. The question opens "The text gives a catalog entry and then names a song by the Beatles." A cold record is the title alone.
- **Article demo.** One file, `examples/context-article.md`, covers the three Wikipedia flips.
  - It names each pinned revision and the fetch rule: prose paragraphs from the parse API.
  - The article runs use `--no-cache` and keep no recording.
  - The committed output keeps only each answer's labels and probabilities.
  - Tests skip this demo, and the number check names it as the one exception.
  - Ian can overturn this and allow article text under CC BY-SA with attribution.

## Work

1. Add `examples/<NN>-<fn>/` in the talk's order: decide, choose, tag, score, filter, rank, find, annotate, recognize, relate.
2. Each folder holds:
   - the case file or files
   - any card the cases name, such as `annotate-card.json`, `recognize.json`, or `relate-01.json`, because the runner runs from the case folder
   - `recording/`
   - everything the runner commits:
     - `timing.tsv`
     - the answers
     - `lists/` for filter, rank, and find
     - `gaps.tsv` when a case is refused
   - `run.sh live|replay`, which calls `functions.sh`
   - `slide.png`
   - `README.md`, the article:
     - the question in plain words
     - the slide
     - the command
     - an output excerpt in a fenced block
     - a "With context" section, or a line saying why none
     - the image credits for any Commons photo on the slide, taken from the talk's credits
3. Cases for each function:

| Function | Cold | With context |
| --- | --- | --- |
| decide | "It appears on the album Abbey Road." over the slide songs | The same songs with their entries. Catalog entries give no signal for "love song", so decide uses this question |
| choose | Lead singer, five options, the slide songs | The same songs with their entries |
| tag | The six songs and five labels | No context. No entry says whether a song is sad, psychedelic, or about the sea |
| score | Length in minutes, the eight slide songs | The same songs with their entries |
| filter | Abbey Road, bar 0.7, the twelve slide songs | The same songs with their entries |
| rank | Biggest hits | No context. Taste is not in any entry |
| find | First release among ten early songs | The ten entries as one text |
| annotate | Singer, album, and year for Blackbird and Octopus's Garden | The same two songs with their entries |
| recognize | The slide sentence | None. The text is the input, and the page says so |
| relate | The slide graph: 4 people, 7 songs, 3 albums | None. The full catalog passes Jev's input limit (thinkthen issue `2026-09-24-relate-sends-a-request-over-jevs-input-token-limit.md`) |

4. Add `tests/test_examples.py`. It checks two things:
   - Each folder replays with no key, and the answers and `lists/` match the committed files byte for byte.
   - Every probability or score inside a README's fenced output block appears in that folder's committed answers. Numbers in the prose are not checked.
   `tests/test_catalog.py` adds a case for `entry()` on a song first released as a single, and one on an album track.
5. File an issue in thinkthen `sdlc/issues/` asking for a Beatles Bench section on thinkthen.dev. The site pulls each page from `examples/*/README.md` and copies no text by hand. The thinkthen queue owns the site.

## Limits

Jev live cap is 60,000 input tokens through the live guard. The planned calls are:

- Catalog runs: about 110 records at up to 200 tokens each. That is about 22,000 tokens.
- relate: the slide graph was about 10,000 tokens in scratch.
- The article demo: three songs at about 7,000 tokens each. That is about 21,000 tokens.

## Proof

- `python3 -m unittest discover -s tests` passes with no network.
- `tests/test_catalog.py` still passes.
- The example replays pass with `THINKTHEN_BIN` set and no key.
- The existing function runs replay unchanged.

## Deferred

- The docs pages, which belong to the thinkthen queue.
- Article text in the repo, pending Ian.
- Other models on the examples.

## Done when

The proof passes, a fresh reviewer accepts, and the work is committed and pushed.

## Ticket review 1 (fresh reviewer, 2026-09-25): nine findings, all taken

1. The rule's path is `data/SOURCES.md`.
2. A song's line names no album. The context entry is now the header plus the line, and decide uses the Abbey Road question.
3. The context record's shape is now stated.
4. Replay goes through `functions.py` for its volatile fields, replay folder, and absolute paths.
5. relate runs cold only.
6. The article runs keep no recording and commit only labels and probabilities.
7. The cap is set from a call count.
8. Slide images carry their photo credits.
9. A test checks the numbers on each page.

## Ticket review 2 (fresh reviewer, 2026-09-25): six findings, all taken

1. `BENCH_TESTS` names the case files. The default stays unchanged.
2. The folder path is `examples/<NN>-<fn>` everywhere.
3. The context record now takes the `ask.py` shape.
4. The number check reads only the fenced output block.
5. The folder list now includes `timing.tsv`, `lists/`, `gaps.tsv`, and the cards. The test compares `lists/`.
6. `.gitignore` ignores `examples/*/replay/`. `entry()` gets its own `test_catalog.py` cases.
