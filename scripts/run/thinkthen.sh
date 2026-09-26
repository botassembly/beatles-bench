#!/bin/sh
# Run every question through the ThinkThen command with --details, recording each exchange for replay.
#   scripts/run/thinkthen.sh live RUN_DIR     asks the backend for anything RUN_DIR/recording lacks (--cache)
#   scripts/run/thinkthen.sh replay RUN_DIR   answers from RUN_DIR/recording alone (--replay), with no key and no network
# Any ThinkThen-compliant backend works: THINKTHEN_BASE_URL names the address, BEATLES_BENCH_MODEL the model,
# THINKTHEN_BIN the command, and THINKTHEN_API_KEY the key. Only the command reads the key.
set -eu
[ $# -eq 2 ] || { echo "usage: scripts/run/thinkthen.sh live|replay RUN_DIR" >&2; exit 2; }
exec python3 "$(dirname -- "$0")/ask.py" "$1" "$2"
