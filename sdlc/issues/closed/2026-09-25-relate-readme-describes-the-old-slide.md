# The relate README describes the old slide

Status: Closed 2026-09-25. Ticket 0010 fixed the text around the 0.5 cut. A Quick Fix with `2026-09-25-example-pages-describe-the-older-talk-slides.md` copied the current relate slide from the talk deck's repo at `538b217` and rewrote "The slide" to describe it.

Found 2026-09-25 by the code review of a talk deck's relate slide.

## What happens

`examples/10-relate/README.md` line 13 reads "Edges at 0.8 or more are bright green. Edges under 0.8 are dashed." The talk's relate slide changed on 2026-09-25. It now draws only the edges Jev asserts, at 0.5 or more, the command's default cut for yes. An edge is green when `data/songs.tsv` agrees and red when it does not. The slide has no 0.8 bar and no dashed edges. Its song and album pills carry one muted outline.

The same README still frames the result around 0.8. Line 59 says "Five of the seven albums clear 0.8 and are right". Line 61 compares an older call against "the bar". `slide.png` in the folder may show the old look too.

## Why it matters

A reader who opens the example from the talk sees a description that does not match the slide.

## The fix

Rewrite "The slide" to describe the current rule: only edges at 0.5 or more, green when right, red when wrong. Recast lines 59 and 61 around the 0.5 cut. Replace `slide.png` with the current slide if it shows the old look.
