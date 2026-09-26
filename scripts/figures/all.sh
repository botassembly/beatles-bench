#!/bin/sh
# Draw every figure into reports/figures/ from results/tables/ (scripts/score/analyze.py writes them). Needs kuva and Pillow.
set -eu
cd "$(dirname -- "$0")"
for f in [0-9]_*.py; do "${PYTHON:-python3}" "$f"; done
