# 0010 A worked-example section for the docs site

Owner: Claude marketing session. Status: done 2026-09-25. The site issue is filed on thinkthen main right after this ticket lands. Ticket 0009 landed at f6065388, so every page shows the fresh run of 2026-09-25. Ticket review 1 returned fourteen findings, all taken. Code review 1 returned eleven, all fixed. Code review 2 confirmed them and returned six prose items, all fixed. The record is `sdlc/records/0010-a-worked-example-section-for-the-docs-site.md`.

Superseded in part on 2026-09-26. Ian ruled that the site's Beatles Bench pages sit under Learn as short articles that do not walk through bench files, JSONL, pins, or run folders. Ticket 0013 moved the worked examples from `examples/` into `functions/`. The pages this ticket wrote live on as `docs/walkthroughs/`.

## Why

Ian asked on 2026-09-25 for a section of about 15 pages on the ThinkThen docs site, drawn from this bench. The talk slides assume knowledge. The annotate slide shows the answer. It does not show the question file, the command, or why an answer is right or wrong. Each page shows a reader three things:

- the two or three files they need
- the command that runs them
- how to read the result, including why one answer is right and another wrong

Every command goes through `thinkthen`. It works against any ThinkThen-compatible server. With `--replay recording` it answers from the committed recording with no key.

## Prior evidence

- `examples/01-decide` to `examples/12-diff` each hold a README, the case files, `run.sh live|replay`, a committed recording, and the outputs. Ticket 0009 swapped in the fresh answers.
- Each README already pairs a `jq` command with the block it prints. `tests/test_examples.py` runs every such command and checks every number in a `json` block against the committed answers. No check reads the prose. The ticket's first draft quoted a stale prose figure for Octopus's Garden. The fresh run gives White Album 0.6, Revolver 0.36, and Abbey Road 0.04.
- Every page command in the READMEs replays from `recording/` with the key unset. The builder checked each one with the pinned build of ticket 0009.
- Each case line carries `truth` and `fields`. `fields` names the `data/songs.tsv` row and column behind the truth.
- The talk deck draws one slide per example from these outputs. Its build replays them byte for byte.

## Pages

Sixteen pages. `docs/README.md` lists them in order. The site reads that list.

| # | Page | File |
| --- | --- | --- |
| 1 | Beatles Bench | `README.md` |
| 2 | How to run the bench for free | `docs/run-it-for-free.md` (new) |
| 3 | The data | `docs/the-data.md` (new) |
| 4 to 13 | One page per function: decide, choose, tag, score, filter, rank, find, annotate, recognize, and relate | `examples/01-decide/README.md` to `examples/10-relate/README.md` |
| 14 | How to find your bar with audit | `examples/11-audit/README.md` |
| 15 | How to see what changed with diff | `examples/12-diff/README.md` |
| 16 | Context and cost | `docs/context-and-cost.md` (new) |

Audit and diff keep a page each. Each already stands alone, and one page for both would run past 200 lines.

## The page form

A function page follows thinkthen ADR 0011's how-to form, adapted to the bench. The title starts with "How to". One paragraph says when to use the function. Then come these parts:

1. **The files.** The two or three files the reader needs. A question file (`annotate`, `relate`) is shown in full, with each field explained. A case file shows one line.
2. **Run it.** One `thinkthen` command with `--replay recording`, and the block it prints. Leave out `--replay recording` and set `THINKTHEN_BASE_URL` and `THINKTHEN_API_KEY`, and the same command asks your server.
3. **Read it.** A `jq` command joins the answers to each case's `truth` and prints right, wrong, or not sure beside each answer. The prose then traces one wrong or not-sure answer to its cause. For example, the annotate page shows why Octopus's Garden gets its singer right and its album not sure. Pages with no answer key say so and say how to judge the answers. `tag` and `rank` hold matters of taste. `recognize` is read against its own sentence. `12-diff` reads each change as gained or lost against `11-audit`'s key.
4. **With context.** The same question with the catalog entry in the text, where the example has one.
5. **What can go wrong.** The traps a reader meets: a replay miss when the text or question changes (exit 5), no key (exit 4), a cache bound to another server (exit 5), and a bar that hides a wrong answer.
6. **The slide and related pages.** The slide stays, with its note when it shows an older run. Links go to the related pages.

Page 2 is a how-to too. Pages 1, 3, and 16 explain the bench, so they keep plain titles.

## Changes

1. Rewrite `examples/01-decide/README.md` to `examples/10-relate/README.md` in the page form. Retitle and add the new parts to `11-audit` and `12-diff`.
2. Write `docs/README.md`, `docs/run-it-for-free.md`, `docs/the-data.md`, and `docs/context-and-cost.md`. Page 2 covers the free replay and how to point the same commands at any ThinkThen-compatible server. Page 3 draws from `data/README.md` and shows one `songs.tsv` row. Page 16 draws its token counts from the examples' `outputs.jsonl` and its open-book cost from `reports/open-book.md`.
3. Extend `tests/test_examples.py`:
   - The command check runs every `sh` block that sits right above a `json` or `text` block, in examples and in `docs/`. A block that calls `thinkthen` runs only when a build is present, with the key and address unset.
   - The number check reads the prose too. Every decimal, and every whole number with thousands commas, in a page's prose must appear in one of that page's fenced blocks or code spans.
   - Each function page has the parts of the form. The docs list names every page, and every file it names exists.
4. File a thinkthen issue on main for the site change: a "Worked examples" section that pulls the pages in `docs/README.md` from a pinned bench commit, with their images. The issue is `2026-09-25-a-worked-examples-section-pulled-from-beatles-bench.md`.

The script that wrote each page's result and reading, from the first draft, is dropped. The pages keep one copy. The tests prove each block.

## Retained behavior

- `./run.sh` with no key replays the 1,501 and every example byte for byte.
- `tests/test_examples.py` keeps its folder list, its part list, its generator check, and its replay checks.
- The talk deck's byte-for-byte replay of the example outputs. No committed answer, recording, or case file changes.
- Slide paragraphs still say when a slide shows an older run.

## Proof

- `python3 -m unittest discover -s tests` passes with no key, with and without `THINKTHEN_BIN` set to the pinned build of ticket 0009.
- `./run.sh` with no key passes.
- A fresh agent with no context follows page 2 and the annotate page in a fresh clone of the branch, with the key unset. It passes when every command it runs prints the block on the page, byte for byte.
- A fresh read-only code review, then a confirm review.

## Deferred

- Other backends.
- `examples/context-article/` keeps no recording, so it does not replay. Page 16 names it and draws no number from it.
- The cache. A cache hit needs a live first call, so no page shows one.
- The talk's slides and experiment 259's claim script still use the older run. The talk's ticket owns them.
- The site's own change sits in the thinkthen issue.

## Done when

The pages pass a fresh review, land here, and the thinkthen site issue is filed.

## Ticket review 1 (fresh reviewer, 2026-09-25): fourteen findings, all taken

1. The Octopus's Garden figures were stale. Prior evidence now gives the fresh ones.
2. A page writer would copy the READMEs. It is dropped. The prose number check takes its place.
3. Not every page has a `songs.tsv` key. The form says how to read `recognize` and `12-diff`.
4. No example shows the cache. The cache is deferred, and page 16 draws on the open-book report and the examples.
5. Pages 1, 2, 3, and 16 had no file. The page table names each.
6. The site path was unclear. `docs/README.md` is the list the site reads. The thinkthen issue names the rest.
7. The form now follows ADR 0011: "How to" titles and "What can go wrong".
8. Page 2 shows how to point the commands at any ThinkThen-compatible server.
9. The proof is now checkable. It names the pages and the pass rule.
10. The tests to add are named.
11. Retained behavior is listed.
12. The deferred gaps are fuller.
13. The deck path is gone. The ticket says "the talk deck".
14. The status line and the colon glosses are fixed.

## Code review 1 (fresh reviewer, 2026-09-25): eleven findings, all fixed

1. The prose number check passed by chance through the answer files. It now reads only the page's own blocks and code spans.
2. Whole numbers with thousands commas are now checked too.
3. The form check now covers all seven headings, in order.
4. Guesses about causes are cut: the score, filter, rank, recognize, and data pages.
5. Numbers from older runs are cut: the catalog's token count and the workspace experiment.
6. Internal references are cut from the pages.
7. The relate page no longer cites the slide's figure. It says an earlier run put the edge over 0.8, and the fresh run puts it at 0.73.
8. "Files" merged into "The files". The server paragraph links to page 2. The cost command lost a no-op.
9. The find page says why the pick reads `u05` and the keys read `u001` to `u010`.
10. Two plain-language slips are fixed, and the data page now says the album sits in the catalog's header line.
11. The thinkthen site issue is filed after landing, pinned to the landed commit. The record holds the proof.

A fresh reader followed page 2 and the annotate page in a fresh clone with no key. All eight output blocks matched byte for byte. Its five notes are folded in: how to check for `audit`, the count of lines `./run.sh` prints, which run `outputs.jsonl` holds, and two wording fixes.

## Code review 2 (confirm, fresh reviewer, 2026-09-25): six findings, all fixed

The reviewer confirmed the eleven fixes, the suite both ways, the 302 pages in `data/raw/`, and the 13 replayed lines. It found six prose items.

1. The record named the audit issue as filed before it was. It is now filed on thinkthen main.
2. The record's proof pointed to numbers it did not give. It now gives them.
3. The record said every "Run it" command uses `--replay recording`. The diff page runs `diff.sh`. The record now says so.
4. The diff page said every context answer lands near 0 or near 1. The Ballad of John and Yoko sits at 0.33. The page now says every answer sits far from the bar and links the audit page.
5. The ticket's status and its number rule were stale. Both now match what landed.
6. The score page had a trailing clause. It is now two sentences.
