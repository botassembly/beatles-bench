#!/bin/sh
# Ask one function folder's cases through scripts/run/ask_suite.sh, the way ./run.sh checks and reruns them.
# live OUT asks every case into OUT, a fresh run folder with its own recording. live refuses without OUT, so a live run
# never writes into the committed folder. replay answers from a recording alone and writes to OUT (default: replay/ in
# the folder). FROM names the run folder whose recording answers, such as a live run's OUT. It defaults to the folder
# itself. The cases always come from examples/NAME. For audit, scripts/score/tune.sh then writes the rows and the audit
# files into OUT. diff asks nothing. scripts/score/context_diff.sh compares audit's rows.
# usage: scripts/run/example.sh NAME live OUT | replay [OUT] [FROM]
set -eu
root=$(cd "$(dirname -- "$0")/../.." && pwd)
usage() { echo "usage: $0 NAME live OUT | replay [OUT] [FROM]" >&2; exit 2; }
[ $# -ge 2 ] || usage
name=$1; shift
case $name in
  decide) tests=decide-love,decide-cold,decide-context ;;
  choose|score|filter|find|annotate) tests=$name-cold,$name-context ;;
  tag|rank|recognize|relate) tests=$name-cold ;;
  audit) tests=audit-cold,audit-context ;;
  *) usage ;;
esac
here=$root/examples/$name
run=$root/scripts/run/ask_suite.sh
export BENCH_FUNCTIONS="$here" BENCH_TESTS="$tests"
case $1:$# in
  live:2) "$run" live "$2"; out=$2 ;;
  live:1) echo "$0: live needs an output folder, so a live run never writes into $here" >&2; exit 2 ;;
  replay:1) "$run" replay "$here"; out=$here/replay ;;
  replay:2) "$run" replay "$here" "$2"; out=$2 ;;
  replay:3) "$run" replay "$3" "$2"; out=$2 ;;
  *) usage ;;
esac
[ "$name" != audit ] || exec "$root/scripts/score/tune.sh" "$out"
