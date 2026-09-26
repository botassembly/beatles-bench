#!/bin/sh
# Run the function suite through the ThinkThen command, recording every exchange for replay.
#   scripts/run/ask_suite.sh live RUN_DIR     asks the backend for anything RUN_DIR/recording lacks (--cache)
#   scripts/run/ask_suite.sh replay RUN_DIR [OUT_DIR]   answers from RUN_DIR/recording alone (--replay), with no key and
#                                                       no network, into OUT_DIR (default: RUN_DIR/replay)
# Paths may be absolute: the paid-call door (thinkthen's sdlc/scripts/live) starts a job in its own checkout.
# scripts/run/ask_suite.py lists the settings. Only the command reads THINKTHEN_API_KEY.
set -eu
[ $# -eq 2 ] || { [ $# -eq 3 ] && [ "$1" = replay ]; } || {
  echo "usage: scripts/run/ask_suite.sh live RUN_DIR | replay RUN_DIR [OUT_DIR]" >&2; exit 2; }
exec python3 "$(dirname -- "$0")/ask_suite.py" "$@"
