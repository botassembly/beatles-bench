# The example pages describe the older talk slides

Status: Closed 2026-09-25. A Quick Fix copied the ten function slides and the audit and diff slides from a talk deck repository commit into `examples/*/slide.png`. Each "The slide" paragraph now describes its image. `README.md`, `reports/results.md`, and `paper/notes.md` now name the recorded load of the 2026-09-25 run. Two phrase checks in the talk deck's build quote the removed text. The talk deck's repo tracks them in `sdlc/issues/2026-09-25-deck-build-quotes-old-bench-slide-text.md`.

Found 2026-09-25 after the talk deck moved to the fresh bench run. The deck's ticket 0029 landed on the deck repo's main at `8839419`.

## What happens

The talk now draws every function slide, audit, and diff from the rerun of 2026-09-25. The relate slide shows only the links at 0.5 or more. The audit slide suggests a cut of 0.78. The diff slide shows 20 of 70 answers changed. The deck's current images sit in the deck repo at `decks/2026-09-24-thinkthen-beatles/slides/*/slide.png`. The deck builds them from the committed `outputs.jsonl`, `lists/`, `rows.jsonl`, and `diff.jsonl` of each example here. So their numbers now match each page.

Each `examples/*/slide.png` here is still the older image. Each "The slide" paragraph still says the slide shows an earlier call or the older run. Three pages outside `examples/` still say no run recorded its load.

## Each stale line and what it should say

The deck's slide for each example is named in brackets. Each `slide.png` should become a copy of that slide's `slide.png`.

- `examples/01-decide/README.md:149` [`06-decide`]: "The slide came from an earlier call of the same question. Separate calls move a few points." The slide now shows this page's answers: Taxman 0.05, Yesterday 0.56, Michelle 0.73, She Loves You 0.96. Drop both sentences.
- `examples/02-choose/README.md:128` [`07-choose`]: "The slide came from an earlier call of the same question, so its numbers differ by a few points." Drop it. The colour sentences stay true.
- `examples/03-tag/README.md:81` [`08-tag`]: "The slide came from an earlier call with a sixth label, "children's song". Separate calls move a few points." The slide now shows this page's five labels and six songs. Drop both sentences.
- `examples/04-score/README.md:154` [`09-score`]: "The slide shows an earlier run's scores for these eight songs. Its numbers differ a little from this call." Drop both sentences.
- `examples/05-filter/README.md:137` [`10-filter`]: "The slide came from an earlier call, so its numbers differ by a few points." Drop it. The slide shows Octopus's Garden kept at 0.75, as this page says.
- `examples/06-rank/README.md:100` [`11-rank`]: "The slide came from an earlier call, so its numbers differ by a few points." Drop it.
- `examples/07-find/README.md:106` [`12-find`]: "The slide came from an earlier call, so its numbers differ by a few points." Drop it.
- `examples/08-annotate/README.md:182` [`13-annotate`]: "The slide came from an earlier call, so its numbers differ by a few points." Drop it.
- `examples/09-recognize/README.md` [`14-recognize`]: the text makes no claim about the run. Only `slide.png` needs the copy.
- `examples/10-relate/README.md:180` [`15-relate`]: `sdlc/issues/2026-09-25-relate-readme-describes-the-old-slide.md` already covers this paragraph and its image. The paragraph should now say: the slide draws only the links Jev asserts at 0.5 or more. A link is green when `data/songs.tsv` agrees and red when it does not. The slide shows Yesterday linked to Help! in green and Octopus's Garden linked to Revolver in red. Drop "This image shows an earlier call, drawn with a bar of 0.8", the two sentences on 0.8 and dashed links, and "Its image swap belongs to the talk's own ticket." Close that issue with this one.
- `examples/11-audit/README.md:168` [`16-audit`]: drop "The slide shows the run before the rerun of 2026-09-25. That run asked the older wording "It appears on the album Abbey Road." Its redraw belongs to the talk's own ticket." Drop "Its numbers come from the older run. The numbers on this page come from the current answers." The table now lists the fourteen songs at 0.72 or more in `rows.jsonl`, from A Day in the Life at 0.97 down to The Ballad of John and Yoko at 0.72. The slide draws two dashed lines. Precision peaks at 75% at 0.93. Accuracy peaks at 94%, recall at 100%, and F1 at 78%, all at 0.78, the cut audit suggests. The paragraph should say so.
- `examples/12-diff/README.md:118` [`17-diff`]: drop "The slide shows the run before the rerun of 2026-09-25. That run asked the older wording. Its redraw belongs to the talk's own ticket." "The bright rows with an arrow are the five that diff listed then" should read: the bright rows with an arrow are the seven of these 12 that `diff.jsonl` lists. They are A Day in the Life, Get Back, Glass Onion, In My Life, Taxman, The Long and Winding Road, and Ticket to Ride. Diff lists 20 of the 70 in all. Blackbird now dims. The colour sentences depend on deck ticket 0030 (see below).
- `examples/02-choose/README.md:128` and `examples/07-find/README.md:106` describe a pick's colour. Check them against the 0030 slides.
- `README.md:41`: "Every time was taken on a loaded machine." The Jev time of 0.32 s comes from `results/runs/2026-09-25-thinkthen-jev`. Its `loadavg.txt` records a load average of 1.54 at the start and 6.10 at the end, on 16 cores. It should say that the Jev time comes from that run and its recorded load. Times from runs before 2026-09-25 carry no recorded load.
- `reports/results.md:23`: "Every time here was taken on a machine busy with other development work, at a load nobody recorded." The same change applies. The quiet-machine rerun is still to come, so that sentence stays.
- `paper/notes.md:80`, under "Still to add": "Every time so far was taken on a machine busy with other development work, at a load nobody recorded." It should say the times before 2026-09-25 carry no recorded load, and the rerun of 2026-09-25 recorded a load average from 1.54 to 6.10 on 16 cores. The quiet-machine item itself stays open. The rerun was not one call at a time on an idle machine.
- `paper/notes.md:82`: "Record the load average in every live run's folder, so a loaded run shows itself." `scripts/run/ask.py` now writes `loadavg.txt`, and each 2026-09-25 run folder holds one. This item can leave "Still to add".

## Timing with the talk's next ticket

Deck ticket 0030 recolours ten of these slides so their values stay white and only the marks carry colour: choose, tag, score, filter, rank, find, annotate, recognize, audit, and diff. Copy those images after 0030 lands. Only the decide and relate images can be copied from `8839419` now. Two paragraphs here describe colours that 0030 changes:

- `examples/03-tag/README.md:81`: "Each chip gets greener with every bar it clears" becomes a sentence on brightness. The chips above the bar are bright, and the ones below are muted.
- `examples/12-diff/README.md:118`: "Red marks a wrong answer at the bar of 0.5. Green marks a right answer Jev is sure of. Yellow marks a right answer Jev is unsure of." The colours move from the numbers to a mark beside each number: a red ✗, an amber ?, and a green ✓.

Check the landed 0030 slides before writing these two paragraphs.

## Why it matters

A reader who opens an example from the talk sees a picture and a paragraph that disagree with the slide and with the page's own numbers.

## The fix

Copy each deck `slide.png` into its example folder, at the time the section above gives. Apply the text changes above. Close the relate issue with this one.
