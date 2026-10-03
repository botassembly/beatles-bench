# Quick Fix qf-pm-mailroom: declare the bench's mailroom and its landing-proof cutoff

Built on 2026-10-03 on `qf/mailroom` from main `8e072c7e`. The bench's `pm` could not read its inbox, because `sdlc/pm.json` named no mailroom. The pm team's round 2 message of 2026-10-02 also asked where `landedProofFromTicketNumber` should sit for the bench.

## Changes

`sdlc/pm.json` gains two keys:

- `"mailroom": {"repo": "sdlc", "name": "beatles-bench"}`. The relative `repo` names a sibling checkout called `sdlc`, so the file holds no machine path. The bench's inbox folder in the mailroom is `inbox/beatles-bench/`. `PM_MAILROOM_REPO` overrides the declaration on any machine.
- `"landedProofFromTicketNumber": 26`. Ticket 0026 is the first bench landing whose merge subject reads `Land ticket NNNN: ...` (`8e072c7e`). Earlier landings read `Merge branch 'ticket/...'`, so pm cannot read a landing proof from them.

## Checks

With pm built from `dd4183b`, which descends from the pm team's stamped `bbbf56d`:

- `pm ping` printed `ping: 2 unread asks in 2 messages from pm, thinkthen`. Before the change it printed `ping: mailroom undeclared`.
- `pm inbox` listed all 21 messages in `inbox/beatles-bench/` on the mailroom's origin/main, with the two open asks.
- `pm status` findings fell from 26 to 6. The 20 cleared were `ticket-landed` findings on tickets before 0026. The 6 left are five evidence-label findings on ticket 0026 and one closed issue without a `Resolution:` line. They are separate cleanup.
- No test reads `sdlc/pm.json`. No live or paid call ran.
