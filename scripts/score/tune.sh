#!/bin/sh
# Split the saved answers in DIR/outputs.jsonl into DIR/rows.jsonl (cold) and DIR/rows-context.jsonl, the answer lines
# audit and diff read. Then grade the cold rows against key.jsonl. Sends no request and needs no API key.
# Writes DIR/audit-asrun.json (with the suggested cut) and DIR/audit-BAR.json for each bar below plus the suggested cut.
# A DIR other than examples/audit also gets a copy of key.jsonl, so context_diff.sh can read DIR as its input folder.
# usage: scripts/score/tune.sh [DIR]   (default: examples/audit)
set -eu
here=$(cd "$(dirname -- "$0")/../../examples/audit" && pwd)
out=${1:-$here}
tt=${THINKTHEN_BIN:-thinkthen}
[ "$out" -ef "$here" ] || cp "$here/key.jsonl" "$out/key.jsonl"
jq -c 'select(.id|startswith("audit-context-")|not)|.rows[]' "$out/outputs.jsonl" > "$out/rows.jsonl"
jq -c 'select(.id|startswith("audit-context-"))|.rows[]' "$out/outputs.jsonl" > "$out/rows-context.jsonl"
"$tt" audit "$out/rows.jsonl" "$here/key.jsonl" --id /input > "$out/audit-asrun.json"
cut=$(jq -r '.suggested.cut' "$out/audit-asrun.json")
for bar in 0.5 0.6 0.7 0.8 0.9 0.95 "$cut"; do
  "$tt" audit "$out/rows.jsonl" "$here/key.jsonl" --id /input --threshold "$bar" > "$out/audit-$bar.json"
done
