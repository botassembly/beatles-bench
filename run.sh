#!/bin/sh
# Run the bench with one command.
#   ./run.sh          with THINKTHEN_BASE_URL unset: replay every function folder in examples/ under THINKTHEN_BIN with no
#                     key and no network, check each replay byte for byte, then print the published results tables.
#   ./run.sh NAME     with THINKTHEN_BASE_URL unset: replay the newest results/runs/DATE-thinkthen-NAME and
#                     results/runs/DATE-examples-NAME a live run left, checking each byte for byte. It stops when no
#                     thinkthen-NAME run exists. With NAME jev it then replays examples/ too.
#   ./run.sh [NAME]   with THINKTHEN_BASE_URL set: ask that backend into results/runs/<today>-thinkthen-NAME, then ask
#                     each function folder's cases into results/runs/<today>-examples-NAME/<function>/, then print the
#                     new run's scores (scripts/score/score.py report).
# NAME defaults to jev. BEATLES_BENCH_MODEL sets only the model each request carries.
# A live run with BEATLES_BENCH_MODEL set must name the run, so another model never lands in the Jev folders.
# A live run writes backend.txt into both folders: the base URL and the model, never the key. The replay passes the same
# two back, because a recording binds to both.
# A live run stops when its folders hold a file git tracks, so it never writes into a committed run. Outside a git
# checkout, such as a ZIP download, it stops when a folder already holds files.
# BENCH_WORKERS and BENCH_MAX_INPUT_TOKENS pass through to scripts/run/ask.py and scripts/run/ask_suite.py.
# BENCH_MAX_INPUT_TOKENS caps each step on its own: the 1,501 questions, then each example. No budget passes from one
# step to the next.
# The published tables in results/tables/ are frozen from the runs of 2026-09-23 to 2026-09-30, which moved to Git
# history (results/README.md). This script never rewrites them.
# This script never reads the key. The thinkthen command reads THINKTHEN_API_KEY itself.
set -eu
cd "$(dirname -- "$0")"
TT=${THINKTHEN_BIN:-thinkthen}
command -v "$TT" >/dev/null 2>&1 || {
  echo "run.sh: the thinkthen command is missing. Install it, or set THINKTHEN_BIN to its path." >&2
  exit 2
}
"$TT" audit --help >/dev/null 2>&1 || {
  echo "run.sh: this thinkthen has no audit command. Install thinkthen 0.1.0 or set THINKTHEN_BIN to a build with audit." >&2
  exit 2
}
[ $# -le 1 ] || { echo "usage: ./run.sh [NAME]" >&2; exit 2; }
# same DIR OUT FILE...: each file in OUT equals the one in DIR, byte for byte.
same() {
  dir=$1 out=$2; shift 2
  for f; do
    cmp -s "$dir/$f" "$out/$f" || { echo "run.sh: $out/$f differs from $dir/$f." >&2; exit 1; }
  done
}
# names DIR PATTERN: the names under DIR matching PATTERN, one per line, empty when none.
names() { (cd "$1" 2>/dev/null && for f in $2; do [ -e "$f" ] && echo "$f"; done) || true; }
# newest LABEL: the newest results/runs/DATE-LABEL folder, empty when none.
newest() { python3 scripts/score/score.py newest "$1" 2>/dev/null | sed 's|.*/results/runs/|results/runs/|' || true; }
# quiet DIR CMD...: run CMD with no key, and with the base URL and model DIR/backend.txt names (the defaults when none).
quiet() {
  dir=$1; shift
  (
    unset THINKTHEN_API_KEY THINKTHEN_BASE_URL BEATLES_BENCH_MODEL
    if [ -f "$dir/backend.txt" ]; then
      THINKTHEN_BASE_URL=$(sed -n 's/^THINKTHEN_BASE_URL=//p' "$dir/backend.txt")
      BEATLES_BENCH_MODEL=$(sed -n 's/^BEATLES_BENCH_MODEL=//p' "$dir/backend.txt")
      export THINKTHEN_BASE_URL BEATLES_BENCH_MODEL
    fi
    exec "$@"
  ) > /dev/null
}
# example NAME SRC FROM BACKEND: replay one example into SRC/replay and check it against SRC, the folder that holds its
# answers. FROM is the run folder whose recording answers, empty for the committed folder. BACKEND holds backend.txt.
example() {
  n=$1 src=$2 from=$3 backend=$4 out=$2/replay
  rm -rf "$out"
  if [ "$n" = diff ]; then  # diff asks nothing: it compares audit's rows
    quiet "$backend" scripts/score/context_diff.sh "${src%/diff}/audit" "$out"
    same "$src" "$out" diff.jsonl
  else
    quiet "$backend" env THINKTHEN_BIN="$TT" scripts/run/example.sh "$n" replay "$out" ${from:+"$from"}
    [ "$(names "$src" 'lists/* audit-*.json')" = "$(names "$out" 'lists/* audit-*.json')" ] || {
      echo "run.sh: the replay in $out writes other files than $src." >&2
      exit 1
    }
    # shellcheck disable=SC2046
    same "$src" "$out" outputs.jsonl $(names "$src" 'lists/* rows.jsonl rows-context.jsonl audit-*.json')
  fi
}
# examples EX: replay each example folder a live run wrote into EX.
examples() {
  for n in $FUNCTIONS; do
    [ -d "$1/$n" ] || continue
    example "$n" "$1/$n" "$1/$n" "$1"
    echo "replayed $1/$n: every file matches the live run"
  done
}
# The function folders in the talk's order. diff comes after audit, because it compares audit's answers.
FUNCTIONS="decide choose tag score filter rank find annotate recognize relate audit diff"
if [ -z "${THINKTHEN_BASE_URL:-}" ]; then
  if [ $# -eq 1 ]; then
    name=$(printf '%s' "$1" | tr '/ ' '--')
    run=$(newest "thinkthen-$name")
    [ -n "$run" ] || { echo "run.sh: no results/runs/DATE-thinkthen-$name run to replay." >&2; exit 2; }
    quiet "$run" env THINKTHEN_BIN="$TT" scripts/run/thinkthen.sh replay "$run"
    cmp -s "$run/replay/answers.jsonl" "$run/answers.jsonl" || {
      echo "run.sh: the replay in $run/replay/ differs from $run/answers.jsonl." >&2
      exit 1
    }
    echo "replayed $run: all answers match its answers.jsonl"
  else
    name=jev
  fi
  if [ "$name" = jev ]; then
    for n in $FUNCTIONS; do
      example "$n" "examples/$n" "" "examples/$n"
      echo "replayed examples/$n: every file matches the committed folder"
    done
  fi
  if [ $# -eq 1 ]; then
    ex=$(newest "examples-$name")
    if [ -n "$ex" ]; then
      examples "$ex"
    fi
  fi
  # The steps that follow read the bench's own files only: no key, no network.
  python3 scripts/score/table.py
else
  if [ $# -eq 0 ] && [ -n "${BEATLES_BENCH_MODEL:-}" ]; then
    echo "run.sh: name the run: ./run.sh NAME" >&2
    exit 2
  fi
  name=$(printf '%s' "${1:-jev}" | tr '/ ' '--')
  day=$(date +%F)
  run=results/runs/$day-thinkthen-$name
  ex=results/runs/$day-examples-$name
  if [ "$(git rev-parse --show-toplevel 2>/dev/null || true)" = "$(pwd -P)" ]; then
    [ -z "$(git ls-files -- "$run" "$ex")" ] || {
      echo "run.sh: $run or $ex holds a file git tracks. A live run never writes into a committed run." >&2
      exit 2
    }
  else  # no git history to read, such as a ZIP download
    for d in "$run" "$ex"; do
      [ -z "$(ls -A "$d" 2>/dev/null)" ] || { echo "run.sh: $d already holds files." >&2; exit 2; }
    done
  fi
  mkdir -p "$run" "$ex"
  printf 'THINKTHEN_BASE_URL=%s\nBEATLES_BENCH_MODEL=%s\n' "$THINKTHEN_BASE_URL" "${BEATLES_BENCH_MODEL:-jev-latest}" > "$run/backend.txt"
  cp "$run/backend.txt" "$ex/backend.txt"
  scripts/run/thinkthen.sh live "$run"
  echo "answers in $run"
  for n in $FUNCTIONS; do
    if [ "$n" = diff ]; then
      scripts/score/context_diff.sh "$ex/audit" "$ex/diff" > /dev/null
    else
      scripts/run/example.sh "$n" live "$ex/$n" > /dev/null
    fi
    echo "answers in $ex/$n"
  done
  python3 scripts/score/score.py report "$run"
fi
