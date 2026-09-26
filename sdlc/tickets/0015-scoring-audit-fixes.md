# 0015 Fix five scoring findings from the 2026-09-26 audit

Owner: the queue owner. Status: done 2026-09-26. Ticket review 1 returned eight findings. All are taken.

## Why

A correctness audit of the function suite on 2026-09-26 returned five findings. The queue owner relayed them with Ian's authority for paid calls up to $0.15:

1. **Relate wording.** The relate suite asks "appears on" but scores only the first album. So a song on a later album, such as "Yellow Submarine", counts wrong. The questions should read "first appeared on the album", as the relate example does.
2. **Duets.** relate asks one pick per song for the lead singer. It cannot score a duet fully. About 12 songs have two lead singers. The fix either asks for singers in a way that lets more than one be right, or reports duets as their own row. The simpler one wins, with its reason.
3. **Top pick.** The headline tables give only the strict score for relate, tag, and annotate's singer. A right answer under the 0.5 bar, or an extra singer, counts wrong and never shows. A "top pick right" measure goes beside each strict score. The strict score stays.
4. **US dates.** `data/README.md` should name each case where the catalog uses a US release date and that date decides a question. The first is Magical Mystery Tour: the US LP came out 1967-11-27, and the UK EP 1967-12-08.
5. **Stale docstring.** Any line that still says the command lacks recognize gets fixed.

## Prior evidence

- Ticket 0014 moved relate onto the shipped `thinkthen relate`. `scripts/generate/functions.py` `RELATE` sets `appears_on` to read "first appeared on the album". `questions/functions/relate-suite.json` holds that reading. `functions/relate/relate.json` holds the same two relations and readings, plus its own threshold of 0.01.
- The fresh relate call of 2026-09-26 sent that wording. Every `appears_on` question in its three recorded requests reads "Item N (song "...") first appeared on the album ___?". The request's `state.relation` also carries the name `appears_on`, as the example's does.
- The 2026-09-25 relate cases were built from `annotate` and read "appears on" (`RULES` at an earlier commit). Ticket 0014 removed them. So finding 1 describes the suite before 0014.
- `git grep -n -i -w "lacks"` finds no line outside `sdlc/` that says the command lacks recognize. Ticket 0014 removed the generator docstring's claim, and its proof grep holds. So finding 5 describes the suite before 0014 too.
- relate plans a `choice` question from each song to the four Beatles plus none (thinkthen `specification/relate.md` at 02dc0b96, "Different-kind relations use a choice"). The probabilities of one choice sum to 1. A probability equal to the cut is accepted. So two singers reach 0.5 only in an exact tie at 0.5, and a duet almost always gains at most one of its two edges.
- The relate truth holds 158 songs with a settled lead. Twelve are duets of Lennon and McCartney: Baby's in Black, Birthday, Drive My Car, Every Little Thing, I've Got a Feeling, Little Child, Love Me Do, Misery, There's a Place, Two of Us, Wait, and Words of Love. The tag and annotate tests hold the same 12 among their 158 songs.
- In the fresh relate run, Jev said one singer for 6 of the 12 duets, each right. Its pre-threshold pick named one of the two leads for 11 of the 12.
- `tag` and `annotate` print a probability for each label, and several labels can pass the bar. So a duet can be fully right there. The strict `exact-set match` and `singer accuracy` fail a song with an extra singer or with no singer at 0.5 or more.
- `scripts/score/functions.py` already writes "top label right, single-lead songs" for tag (0.753 of 146) and annotate's singer (0.733 of 146). Neither is a main row, so neither reaches the headline tables. Both take `max()` over the labels, so a tie at the top goes to the first label in the dict, john. The fresh Jev run holds seven tag ties and four annotate ties at the top. The GLM run holds 11 and 5, and Laya's none. A downstream talk deck quotes the tag row as "75% of 146".
- The relate result keeps, for each logical question, every candidate's probability and the command's pre-threshold `pick` (`answer.questions`). The command chooses the pick. A pick of none counts wrong.
- The headline tables are `results/tables/functions*.tsv` (main rows), the `reports/results.md` function table, and `scripts/score/table.py`, which prints it. `tests/test_functions.py` `TableTest` checks the tables byte for byte against a rescoring.
- `data/albums.tsv` gives Magical Mystery Tour 1967-11-27. `data/README.md` says only "A release date is the earliest date in the infobox, sometimes the US date."

## Retained behavior

- No question file, case, recording, or run folder changes. Every request stays byte for byte. So no paid call is needed, and `./run.sh` replays unchanged.
- The strict measures keep their names and their place as the first main row of each function: `exact-set match`, `singer accuracy`, and `edge F1`.
- The rows "top label right, single-lead songs" for tag and annotate stay, with their values. The deck quotes the tag row.
- The relate example in `functions/relate/` stays, with its name `appears_on`.
- `results/history.tsv` stays. Its rows record each run as it was scored then.
- GLM and Laya are rescored from their committed runs with the new rows. None is asked again.

## Changes

1. **Relate wording.** No wording change: the suite already sends "first appeared on the album". The generator reads the two relations from `functions/relate/relate.json` in place of its own copy. `relate-suite.json` keeps its bytes. The existing test that the committed questions equal the generator output then pins the suite to the example.
2. **Duets: their own row.** The strict edge F1, precision, and recall stay as they are, duets included. `results/history.tsv` then still compares. A new main row, `duets: pick is a lead`, counts the duets whose pre-threshold `sung_by` pick names one of their leads. A duet is a song with two `sung_by` truth edges. The scorer takes the duets from the truth. The case file does not change.
3. **Top pick right.** A new main row `top pick right` follows the strict row for each of the three:
   - tag, over its 158 songs: the likeliest label is a true lead.
   - annotate's singer, over the 158 cards with a singer truth: the same rule.
   - relate, in two rows: `singer top pick right` over 158 `sung_by` picks, and `album top pick right` over 182 `appears_on` picks. The command's `pick` is a true target. A pick of none counts wrong.
   The tag row is `top pick right`, and the annotate row is `singer top pick right`. For tag and annotate, a tie at the top earns the share of its tied labels that are true leads. relate uses the command's own pick. Duets count right when the top pick is either lead. `top_pick_right()` is one function for tag and annotate.
4. **US dates.** `data/README.md` "Known limits" gains a table of each item whose catalog date is a US release date and decides a question. A US date decides a question when the question's truth would change under the UK date. Each entry gives the item, the US and UK dates, and the question ids. The scan reads each album's and each song's source page at its pinned revision (`pins/pages.tsv`): the infobox "released" field and the prose. It checks every question kind that reads a date: the song month, same month, before or after an event, the album year, the function suite's rank by date and annotate's year, and the function folders' cases. The README states the method. A reader can repeat it. Items with a US date that decides nothing get one line. One more line names the album identity: Magical Mystery Tour counts as the first album of five 1967 singles from its US LP. That sets their first-album truth in the function suite and in the audit and filter examples.
5. **Stale docstring.** No line to fix. The proof grep stays.
6. **Downstream.** `results/tables/functions.tsv`, `functions-glm.tsv`, and `functions-laya.tsv` from `functions.py table`. The `reports/results.md` function table from `table.py`. Its relate paragraph says why duets get their own row. It names each row's tie rule. `results/history.tsv` stays: `history()` records only main rows with a request count. `scripts/score/functions.py` docstrings say what each new row counts.

## Tests

- One edge-case table test on `top_pick_right()`: a single lead picked, a single lead under 0.5 still on top, an extra singer above the bar with the true lead on top, a duet with either lead on top, a tie of one true and one wrong label at the top (half credit), and a tie of two true leads (full credit).
- One test on `relate_rows()` with a small fake result: the strict counts keep a duet's edges, the duet row counts a pick of either lead, and a pick of none counts wrong in the album row.
- `TableTest` checks the rescored tables byte for byte.

## The run

No paid call is planned. Every request stays byte for byte, so nothing needs to be asked again. The dry run is the replay: the function suite, relate included, replays from `results/runs/2026-09-26-functions-jev/recording` with no key and gives its committed outputs. If a change turned out to need a new request, the work would stop, dry-run it, and stay under the $0.15 cap at $0.042 per million input tokens. The key would come only from the environment.

## Proof

- `python3 -m unittest discover -s tests` passes with no key and no network, with and without `THINKTHEN_BIN` set to the pinned build (SHA-256 `eb4a5713`).
- `./run.sh` with no key and no address replays every run and function folder byte for byte.
- `functions.py table` on the committed runs gives the committed tables twice.
- `git status` is clean after the suite.
- `git diff --stat main` touches no file under `questions/`, `results/runs/`, or `functions/*/recording`.
- A one-off check finds every question id the `data/README.md` table names in the question files. The record gives its output.
- `git grep -n -i -w "lacks" -- scripts tests docs questions functions/*/README.md` names no missing recognize command.

## Owner's decisions (Ian can overturn each)

- Duets become their own row. A plan that lets two singers be right would bend the shipped `relate`. Its choice plan admits one pick. A yes/no plan would need a profile fallback or a changed kind, a new paid call, and a different relate from the one the example shows. The row needs no call and keeps the relate call byte for byte.
- The strict relate measures keep duets. Their meaning and history stay. The duet row and the singer top pick row show what one pick can reach.
- relate's top pick is the command's own `pick`. tag and annotate print no pick, so the bench uses the likeliest label. A tie at the top earns the share of its labels that are right. Ticket 0012 grades a tie the same way, as thinkthen `audit` does.
- The relation name stays `appears_on`, as in the example. The model reads "first appeared on the album" in each question.
- The single-lead rows stay beside the new ones. The deck quotes the tag row. They still break a tie by label order. `reports/results.md` names each row's tie rule. Deferred records the gap.

## Deferred

- The single-lead "top label right" rows break a tie at the top by label order. A later ticket can apply the tie rule there and move the deck quote once.
- The decide and filter examples in `functions/decide` and `functions/filter` ask "It appears on the album Abbey Road." and score the first album. No song in those cases is on Abbey Road after first appearing elsewhere, so no answer changes. Changing the wording would change every request and slide. Left for the next rerun of the examples.

## Downstream deck

Every deck-quoted number that moves goes into the deck repository's issue `sdlc/issues/2026-09-26-bench-numbers-moved-in-the-0014-rerun.md`, committed on its main. The deck itself is not edited.

## Done when

The proof passes, a fresh reviewer accepts the code, the bench lands on main by fast-forward and is pushed, and the deck issue lists the moved numbers on its main.

## Ticket review 1 (fresh reviewer, 2026-09-26): eight findings, all taken

1. The strict relate measures keep duets. Their name, meaning, and history stay.
2. relate's top pick splits into a singer row and an album row.
3. The annotate row is named `singer top pick right`.
4. The GLM tie counts join the evidence. `reports/results.md` names each row's tie rule.
5. The 0.5 claim names the exact tie the command accepts.
6. The US-dates change defines "decides", lists the question kinds, names the pinned pages as the source, covers the album identity of Magical Mystery Tour, and adds a proof line.
7. The generator reads the example's relations. The copy and the new contract test go.
8. Three trailing clauses and one contrastive phrase are split.
