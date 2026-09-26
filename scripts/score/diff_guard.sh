#!/bin/sh
# Run thinkthen diff on two runs, and stop when the pairing cannot support the comparison.
# usage: scripts/score/diff_guard.sh A B [--allow-unpaired] [--no-digest] -- DIFF_ARGS
# It stops when the summary pairs no records. It stops when A or B holds an answer the other lacks (only_a or only_b),
# unless --allow-unpaired. It stops when a paired answer asked a different question (meta.question_sha256), or a row
# carries no digest, unless --no-digest. Use --no-digest only when the two runs word the question differently by design.
# Otherwise it prints what thinkthen diff prints for A B DIFF_ARGS. Sends no request and needs no key.
# THINKTHEN_BIN names the command (default: thinkthen on PATH).
set -eu
usage() { echo "usage: scripts/score/diff_guard.sh A B [--allow-unpaired] [--no-digest] -- DIFF_ARGS" >&2; exit 2; }
[ $# -ge 3 ] || usage
a=$1 b=$2
shift 2
unpaired=0 digest=1
while [ $# -gt 0 ]; do
  case $1 in
    --allow-unpaired) unpaired=1 ;;
    --no-digest) digest=0 ;;
    --) shift; break ;;
    *) usage ;;
  esac
  shift
done
tt=${THINKTHEN_BIN:-thinkthen}
stop() { echo "diff_guard: $*" >&2; exit 1; }

# The summary comes from the JSON form, so --table moves to the final run.
table=0 id=/id prev=
for arg; do
  shift
  case $arg in --table) table=1 ;; --id=*) id=${arg#--id=}; set -- "$@" "$arg" ;; *) set -- "$@" "$arg" ;; esac
  [ "$prev" = --id ] && id=$arg
  prev=$arg
done
out=$(mktemp)
trap 'rm -f "$out"' EXIT
"$tt" diff "$a" "$b" "$@" > "$out"
summary=$(tail -n 1 "$out")
records=$(printf '%s' "$summary" | jq -r '.summary.records')
only=$(printf '%s' "$summary" | jq -r '.summary.only_a + .summary.only_b')
[ "$records" -gt 0 ] || stop "no records pair between $a and $b"
[ "$unpaired" -eq 1 ] || [ "$only" -eq 0 ] || stop "$only answers have no partner (only_a and only_b); pass --allow-unpaired to compare the rest"
if [ "$digest" -eq 1 ]; then
  bad=$(jq -rn --slurpfile a "$a" --slurpfile b "$b" --arg ptr "$id" '
    def path: $ptr | ltrimstr("/") | split("/") | map(gsub("~1"; "/") | gsub("~0"; "~"));
    def key: [.name, (.input | getpath(path) | tostring)] | tojson;
    ($b | map({key: key, value: .meta.question_sha256}) | from_entries) as $bd
    | ([$a[], $b[] | select(.meta.question_sha256 == null) | "a row with no digest: \(key)"]
       + [$a[] | key as $k | select($bd | has($k) and $bd[$k] != null) | select(.meta.question_sha256 != $bd[$k]) | "a pair with different digests: \($k)"])
    | first // empty')
  [ -z "$bad" ] || stop "$bad (meta.question_sha256); pass --no-digest when the wordings differ by design"
fi
if [ "$table" -eq 1 ]; then
  exec "$tt" diff "$a" "$b" "$@" --table
fi
cat "$out"
