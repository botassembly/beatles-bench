# 0025 Convert the committed recordings to the question store

Owner: the queue owner. Status: draft; ticket review 1 returned findings, not yet folded in. Paused 2026-09-30 for the next checkpoint.

Review 1 findings to fold in before building:

1. The question store covers only decide, choose, tag, score, filter, rank and annotate. find, recognize and relate still replay from digest entries, so those entries must stay.
2. `timing.tsv` is keyed by request digest, but a store replay reports question keys. Every timed run's replay would lose `wall_s` and `sent`, and its byte check would fail. Either re-key the timing or narrow the scope.
3. Exclude the GLM chat recordings, which `chat.py` owns.
4. The replay tests' `same_build` gate would skip under the checkpoint binary.
5. Recordings outside the globs exist: `results/archive/in-text-check/` and `archive/probes/`.
6. `examples/audit` and `diff` outputs may differ under a newer build.
7. Folders holding both forms convert with the newer answer winning.
8. State the size impact.

Narrowest scope that meets the site's need: the site's `pull-bench` reads `examples/{decide,choose,tag,score,filter,rank,find,annotate}` and `results/runs/2026-09-26-thinkthen-jev`. So convert the `examples/` recordings of the seven store functions first, keep find's digest entries, and defer `results/runs/`.

## Why

Current ThinkThen replays only a question store: `thinkthen.jsonl`, or `thinkthen.sqlite`. It ignores the old digest entries (`DIGEST.json` files and folder markers) until `thinkthen cache convert` runs on them. Every committed recording in this repo is still in the old form, apart from some live `thinkthen.sqlite` files written beside the old entries. The thinkthen site copies bench files with `npm run pull-bench` and needs files that current ThinkThen can replay. The marketing lead asked for this on 2026-09-30.

## Prior evidence

- ThinkThen's specification (`specification/recording.md` at the first published checkpoint `checkpoint/surfaces/2026-09-30-1`, commit `1456300457`) says:
  - `cache convert DIR` writes `DIR/thinkthen.jsonl` from everything the folder holds: an existing `thinkthen.jsonl`, a `thinkthen.sqlite`, and every old `thinkthen.recording/1` entry.
  - A replay folder that holds both `thinkthen.jsonl` and `thinkthen.sqlite` is refused.
  - An entry that does not rejoin byte for byte is skipped, with a named message.
  - Converted answers take `taken_at` 0 and origin `converted`.
- The site converted its own copy of these files in its ticket 0031.
- Release QA converted a committed demo recording with that checkpoint's command. Replays hit afterwards (thinkthen-qa `cli/hostile/cache.md`).
- The published command is `thinkthen-0.0.1-x86_64-unknown-linux-gnu-debug.tar.gz` in `~/workspace/builds/thinkthen/checkpoint/surfaces/2026-09-30-1/`, checked against that folder's `SHA256SUMS`.

## Retained behavior

- Every run's answers, outputs, tables and reports keep their bytes. This ticket changes only the recording folders and the replay tooling.
- Each run's `run.txt` keeps its build line. A new line records the conversion: the command's tag and commit, the date, and the counts of answers written and entries skipped.

## Changes

1. For every recording folder under `results/runs/*/recording`, `results/archive/runs/*/recording` and `examples/*/recording`, run `thinkthen cache convert DIR` with the published checkpoint command. Commit the `thinkthen.jsonl` it writes. Then remove the old `DIGEST.json` entries, the folder markers, `.locks/` and any `thinkthen.sqlite`, because a folder holding both files is refused. Git history keeps the old form.
2. Record each folder's skipped entries in its run's `run.txt`, with the convert command's own message. A folder that skips any entry a committed answer depends on stops the ticket for that run. Report it instead of committing.
3. `run.sh` and `scripts/run/thinkthen.sh replay` take the command from `THINKTHEN_BIN` as today, and the README names the checkpoint folder as the supported source.
4. Replay every converted run with the checkpoint command, and compare it byte for byte with its committed outputs, as `run.sh` does today. A run whose replay differs stops. Its difference is reported, and that run stays unconverted.

## Proof

- A test asserts that no committed recording folder holds a `DIGEST.json`, a folder marker or a `thinkthen.sqlite`, and that each holds one `thinkthen.jsonl` whose lines parse.
- The replay tests that skip today for lack of a binary run with `THINKTHEN_BIN` set to the checkpoint command, and pass. The parent records the exact count.
- The full suite passes.
- No live call: conversion and replay read files only.

## Deferred gaps

- Liquid d1's 513 rate-limited gaps (ticket 0023) are asked again after this ticket, into a converted folder.
- A later checkpoint may change the fixture format. Conversion then reruns under that checkpoint.
