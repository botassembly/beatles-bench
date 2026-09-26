#!/bin/sh
# Run the bench with one command, then score every run and print the tables.
#   ./run.sh          with THINKTHEN_BASE_URL unset: replay the newest results/runs/DATE-thinkthen-jev run and every
#                     function folder in functions/ with no key and no network, each checked byte for byte
#   ./run.sh [NAME]   with THINKTHEN_BASE_URL set: ask that backend into results/runs/<today>-<NAME>, then ask each
#                     function folder's cases into results/runs/<today>-examples-<NAME>/<function>/
# NAME names the folders only. It defaults to BEATLES_BENCH_MODEL, else jev-latest.
# BEATLES_BENCH_MODEL, BENCH_WORKERS, and BENCH_MAX_INPUT_TOKENS pass through to scripts/run/ask.py and
# scripts/run/functions.py. BENCH_MAX_INPUT_TOKENS caps each step on its own: the 1,501 questions, then each example.
# No budget passes from one step to the next.
# This script never reads the key. The thinkthen command reads THINKTHEN_API_KEY itself.
set -eu
cd "$(dirname -- "$0")"
TT=${THINKTHEN_BIN:-thinkthen}
command -v "$TT" >/dev/null 2>&1 || {
  echo "run.sh: the thinkthen command is missing. Install it, or set THINKTHEN_BIN to its path." >&2
  exit 2
}
"$TT" audit --help >/dev/null 2>&1 || {
  echo "run.sh: this thinkthen has no audit command. Install a build from thinkthen main at 02dc0b96 or later." >&2
  exit 2
}
# same DIR FILE...: each file in DIR/replay/ equals the committed one in DIR, byte for byte.
same() {
  dir=$1; shift
  for f; do
    cmp -s "$dir/$f" "$dir/replay/$f" || { echo "run.sh: $dir/replay/$f differs from the committed $dir/$f." >&2; exit 1; }
  done
}
# names DIR PATTERN: the names under DIR matching PATTERN, one per line, empty when none.
names() { (cd "$1" 2>/dev/null && for f in $2; do [ -e "$f" ] && echo "$f"; done) || true; }
# The function folders in the talk's order. diff comes after audit, because it compares audit's answers.
FUNCTIONS="decide choose tag score filter rank find annotate recognize relate audit diff"
if [ -z "${THINKTHEN_BASE_URL:-}" ]; then
  [ $# -eq 0 ] || { echo "usage: ./run.sh (replay), or set THINKTHEN_BASE_URL and run ./run.sh [NAME]" >&2; exit 2; }
  run=$(python3 scripts/score/score.py newest thinkthen-jev)
  run=results/runs/$(basename "$run")
  (unset THINKTHEN_API_KEY THINKTHEN_BASE_URL BEATLES_BENCH_MODEL; exec scripts/run/thinkthen.sh replay "$run")
  cmp -s "$run/replay/answers.jsonl" "$run/answers.jsonl" || {
    echo "run.sh: the replay in $run/replay/ differs from the committed answers." >&2
    exit 1
  }
  echo "replayed $run: all answers match the committed run"
  for n in $FUNCTIONS; do
    d=functions/$n
    rm -rf "$d/replay"
    if [ "$n" = diff ]; then  # diff asks nothing: it compares the committed audit rows
      (unset THINKTHEN_API_KEY THINKTHEN_BASE_URL BEATLES_BENCH_MODEL; exec scripts/score/context_diff.sh functions/audit "$d/replay") > /dev/null
    else
      (unset THINKTHEN_API_KEY THINKTHEN_BASE_URL BEATLES_BENCH_MODEL; exec scripts/run/example.sh "$n" replay) > /dev/null
    fi
    if [ "$n" = diff ]; then
      same "$d" diff.jsonl
    else
      [ "$(names "$d" 'lists/* audit-*.json')" = "$(names "$d/replay" 'lists/* audit-*.json')" ] || {
        echo "run.sh: the replay in $d/replay/ writes other files than the committed ones." >&2
        exit 1
      }
      # shellcheck disable=SC2046
      same "$d" outputs.jsonl $(names "$d" 'lists/* rows.jsonl rows-context.jsonl audit-*.json')
    fi
    echo "replayed $d: every file matches the committed folder"
  done
else
  [ $# -le 1 ] || { echo "usage: ./run.sh [NAME]" >&2; exit 2; }
  name=$(printf '%s' "${1:-${BEATLES_BENCH_MODEL:-jev-latest}}" | tr '/ ' '--')
  day=$(date +%F)
  run=results/runs/$day-$name
  scripts/run/thinkthen.sh live "$run"
  echo "answers in $run"
  ex=results/runs/$day-examples-$name
  for n in $FUNCTIONS; do
    if [ "$n" = diff ]; then
      scripts/score/context_diff.sh "$ex/audit" "$ex/diff" > /dev/null
    else
      scripts/run/example.sh "$n" live "$ex/$n" > /dev/null
    fi
    echo "answers in $ex/$n"
  done
fi
python3 scripts/score/analyze.py >/dev/null
python3 scripts/score/table.py
