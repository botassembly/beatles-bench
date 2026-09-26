#!/bin/sh
# List the answers that change between the cold run (IN/rows.jsonl) and the context run (IN/rows-context.jsonl), both
# at 0.5, each marked against the answer key IN/key.jsonl, then a summary with its McNemar test.
# The two runs send different text, so each row's input first becomes {"id": title} in OUT/a.jsonl and OUT/b.jsonl.
# thinkthen diff runs behind scripts/score/diff_guard.sh with --no-digest, because the two runs word the question
# differently by design. Sends no request and needs no API key.
# usage: scripts/score/context_diff.sh [IN [OUT]]   (defaults: functions/audit and functions/diff; writes OUT/diff.jsonl)
set -eu
root=$(cd "$(dirname -- "$0")/../.." && pwd)
in=${1:-$root/functions/audit}
out=${2:-$root/functions/diff}
mkdir -p "$out"
title='.input = {id: (.input.input | split("\nText: ") | last)}'
jq -c "$title" "$in/rows.jsonl" > "$out/a.jsonl"
jq -c "$title" "$in/rows-context.jsonl" > "$out/b.jsonl"
"$root/scripts/score/diff_guard.sh" "$out/a.jsonl" "$out/b.jsonl" --no-digest -- --threshold 0.5 --key "$in/key.jsonl" > "$out/diff.jsonl"
