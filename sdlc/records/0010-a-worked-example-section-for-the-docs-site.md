# 0010 A worked-example section for the docs site: record

Ticket: [0010](../tickets/0010-a-worked-example-section-for-the-docs-site.md). Built on 2026-09-25 on `ticket/0010-worked-example-docs` from main f6065388. The pinned thinkthen build is ticket 0009's: main 02dc0b96, SHA-256 `eb4a5713...e255`. No paid call was made. Every page command ran with the key and the address unset.

## What landed

- `docs/README.md` lists 16 pages in reading order. `docs/run-it-for-free.md`, `docs/the-data.md`, and `docs/context-and-cost.md` are new. `docs/context.jq` marks the examples' cold and context answers for page 16.
- `examples/01-decide` to `12-diff`: each README is a how-to page. Each has The files, Run it, Read it, With context, What can go wrong, The slide, and Related. Each function page's "Run it" command calls `thinkthen` with `--replay recording`. The diff page runs `diff.sh` over committed answers. Each "Read it" command marks every answer right, wrong, or not sure against its case's `truth` from `data/songs.tsv`. Pages with no key say how to judge the answers.
- `tests/test_examples.py`:
  - Every command above an output block, on every listed page, prints that block. A command that runs `thinkthen` or `run.sh` runs only when a build is present, with no key and no address.
  - Every json block sits below the command that prints it.
  - Every number a `thinkthen` command prints in a json block is in the example's committed answers. This check needs no build.
  - Every decimal, and every whole number with thousands commas, in a page's prose appears in a block or code span on the same page.
  - Each function page has the seven headings in order, and `docs/README.md` names it.
- The README links the section. Ticket 0009's open gap 1 now reads closed: the main checkout's `data/raw/` holds all 302 pinned pages. The relate issue says the text is fixed and the image swap stays with the talk.
- No committed answer, recording, case file, or result changed.

## Proof

- `python3 -m unittest discover -s tests` with the pinned build: 173 tests, OK, 2 skipped. Without a build: 173 tests, OK, 22 skipped.
- `./run.sh` with no key printed 13 "replayed" lines and left `git status` clean.
- A fresh agent cloned the branch, put the pinned build on its PATH, and followed page 2 and the annotate page with no key. All eight output blocks matched byte for byte. It could say why Octopus's Garden's singer is right and its album comes back not sure.
- After the code review fixes, the suite ran again. With the pinned build: 173 tests, OK, 2 skipped. Without a build: 173 tests, OK, 22 skipped.
- Code review 2 (confirm) found six prose items: an unfiled issue, a dangling pointer, the diff page's run command, a claim on the diff page, the ticket's status and number rule, and a trailing clause on the score page. All six are fixed.

## Found on the way

- `thinkthen audit` exits 0 when no answer matches the key. Filed on thinkthen main as `2026-09-25-audit-exits-0-when-no-answer-matches-the-key.md`. The audit page warns readers.
- The site section is thinkthen issue `2026-09-25-a-worked-examples-section-pulled-from-beatles-bench.md`, pinned to the commit that lands this ticket.

## Open

- The talk's slides for 10-relate, 11-audit, and 12-diff still show older runs. The pages say so. The talk's ticket owns the images.
- `examples/context-article/` keeps no recording, so it does not replay.
- No page shows the cache. A cache hit needs a live first call.
