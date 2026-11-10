# 0027 — validate-0-2-find-candidate-migration

Status: OPEN.

## Outcome

The existing benchmark runner/scorer supports the 0.2 per-record find contract with one identity-preserving packed document and one typed outcome per case. This is the benchmark counterpart of ThinkThen ticket 0702.

## Why

Ian authorized implementing the November 10 ThinkThen assessment plan and assigned its combined PM/build coordinator ticket-only coordination. The old aggregate-find runner cannot measure the new per-record function without adapting its inputs and scoring.

## Proof

- Proof: validate all 700 suite cases offline, retaining 300 memory, 300 context and 100 card cases, including 90 gold-none and 400 multiline-candidate cases. Installed-command loopback cases prove one result per case, exact selected candidate identity with duplicate text, Unicode, escaped newlines, none, unsure and backend failures. No credentials or paid calls.

## Starts from

- Starts from: questions/suite/find.jsonl, scripts/run/ask_suite.py and the existing scorer. The full reviewed packing and scoring specification is ThinkThen sdlc/tickets/0702-validate-find-candidate-migration.md; depend on its shared threshold repair 0694 before integrated execution.
- Pack one document per case in original candidate order. Preserve nonblank single-line text when every candidate qualifies; otherwise encode every candidate as compact single-line JSON with id and text, escaping CR/LF. Maintain a final Unicode-scalar span-to-ID map and presentation version. Duplicate text is valid; duplicate IDs are refused. Encode empty candidates; fail oversized cases explicitly rather than truncating.
- Record exit and typed result status before scoring. Missing output, failure and unsure never become successful none. Retain original truth and historical result identities.

## Keeps

- Keeps: candidate IDs/order, original data, honest denominators and one engine function contract. Extend existing runner/scorer rather than duplicate them in ThinkThen.

## Defers

- Defers: live model comparison until separately approved concrete budget; public packing helper until evidence warrants it. Backend discrimination is not a product correctness gate.

## Changes

- Changes: scripts/run/ask_suite.py, its existing scorer, a narrow shared packing helper, focused offline tests and a short migration protocol. Coordinator owns this ticket and linked ThinkThen 0702; no mail handoff required.
