# 0015 Fix five scoring findings from the 2026-09-26 audit: record

Built on 2026-09-26 on `ticket/0015-scoring-audit-fixes` from main at an earlier commit. No model call ran. No key was set or read. The spend is $0.

## Result

1. **Relate wording.** The suite already asked "first appeared on the album" after ticket 0014. The generator now reads the two relations from `functions/relate/relate.json`. `relate-suite.json` kept its bytes. The existing generator test pins the suite to the example.
2. **Duets.** A new relate row, `duets: pick is a lead`, counts the 12 duets whose singer pick names one of their two leads. Jev's pick names a lead for 11 of 12. The strict edge F1, precision, and recall keep duets and keep their values.
3. **Top pick.** New main rows sit beside each strict measure: tag `top pick right`, annotate `singer top pick right`, and relate `singer top pick right` and `album top pick right`. The strict rows and the single-lead rows stay.
4. **US dates.** `data/README.md` "Known limits" names the three US dates that decide a question, with 13 question ids. It names two more US dates that decide none, and the album identity of Magical Mystery Tour. A one-off check found all 13 ids in the question files.
5. **Stale docstring.** No line outside `sdlc/` says the command lacks recognize. Ticket 0014 removed the last one.

## Numbers

No existing number moved. Old values stay: tag exact-set match 0.291, tag single-lead top label 0.753 of 146, annotate singer accuracy 0.310, relate edge F1 0.719, precision 0.867, and recall 0.614.

New rows, Jev, from `results/runs/2026-09-26-functions-jev`:

| Function | Measure | Value (95% interval) | n |
| --- | --- | --- | --- |
| tag | top pick right | 0.747 (0.674 to 0.808) | 158 |
| annotate | singer top pick right | 0.734 (0.660 to 0.797) | 158 |
| relate | singer top pick right | 0.899 (0.842 to 0.937) | 158 |
| relate | album top pick right | 0.637 (0.565 to 0.704) | 182 |
| relate | duets: pick is a lead | 0.917 (0.646 to 0.985) | 12 |

GLM-5.3 Flash: tag 0.997 and annotate singer 0.965. Laya: tag 0.070 and annotate singer 0.063. Neither asked relate.

A recount of the relate run gives the figures a downstream deck recounts: 340 picks, 12 duets, 42 right picks under the 0.5 bar, and 6 of those on duets.

## Proof

- `python3 -m unittest discover -s tests` with the pinned build (SHA-256 `eb4a5713`) and no key: 178 tests, OK, 2 skipped. With no build and no `thinkthen` on `PATH`: 178 tests, OK, 22 skipped.
- `./run.sh` with no key and no address exited 0. It printed 13 "replayed" lines, and every file matched. `git status` was clean after it.
- `TableTest` rescored the three function runs to the committed tables byte for byte. `table.py` prints the `reports/results.md` function table.
- `git diff --stat main` touches nothing under `questions/`, `results/runs/`, or `functions/*/recording`. Every request stays byte for byte, so no paid call was needed.
- `git grep -n -i -w "lacks" -- scripts tests docs questions 'functions/*/README.md'` names no missing recognize command.

## The deck

A downstream talk deck reads the first main row per function and the tag single-lead row. Neither moved. The deck repository's issue on the 0014 rerun gains a section for this ticket.

## Reviews

- Ticket review 1 returned eight findings. All are taken. The ticket lists them.
- Code review 1 recounted every new row from the run and checked the US-date table against the pinned pages and every dated question. It found no other deciding US date. It returned five findings. All are fixed:
  1. The record and a docstring edit were uncommitted. Both are committed.
  2. The `top_pick_right()` docstring read as if an extra label earned credit. It now says the extra label costs nothing.
  3. "At most one singer" overstated. The report and docstring now name the exact tie at 0.5.
  4. The generator comment names `--threshold 0.5`.
  5. The relate test adds a duet picked as a non-lead. The duet row expects 1 of 2.
