#!/bin/sh
# Retrieval-augmented decisions with shipped ThinkThen commands and jq alone. No request is built in Python.
#   scripts/run/rad_pipeline.sh live RUN_DIR     calls the backend for any exchange RUN_DIR/recording lacks (--cache)
#   scripts/run/rad_pipeline.sh replay RUN_DIR   answers from RUN_DIR/recording alone (--replay) into RUN_DIR/replay/
# 1. Each single-question case (CASES below): choose answers from memory, then picks two of the 28 catalog sections,
#    jq glues them before the question, and choose answers again. Octopus's Garden is the control: its pick misses.
# 2. The 18 Abbey Road songs, tagged with their lead singers from memory, glued (section and song in one text),
#    and apart ({context, song} records sent with --field /context --field /song). Truth: lead_vocals in data/songs.tsv.
# 3. annotate checks each apart answer for correctness and for grounding in the context (rad_pipeline.checks.json).
#    It then checks the same 18 songs with a wrong singer planted in /output. A caught one has grounded = false.
# Writes scores.tsv (arm, right, of, input_tokens), checks.tsv (one row per song), times.tsv, and one .jsonl per call.
# The catalog is catalog.txt in the newest results/runs/DATE-thinkthen-jev-open-book folder (score.py newest).
# THINKTHEN_BIN names the command and BEATLES_BENCH_MODEL the model. Only the command reads THINKTHEN_API_KEY.
set -eu
usage() { echo "usage: scripts/run/rad_pipeline.sh live|replay RUN_DIR" >&2; exit 2; }
[ $# -eq 2 ] || usage
case $1 in live) flag=--cache ;; replay) flag=--replay ;; *) usage ;; esac
mkdir -p "$2"
HERE=$(cd "$(dirname -- "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
RUN=$(cd "$2" && pwd)
OUT=$RUN; [ "$1" = replay ] && OUT=$RUN/replay
mkdir -p "$OUT"
TT=${THINKTHEN_BIN:-thinkthen}
CATALOG=$(python3 "$ROOT/scripts/score/score.py" newest thinkthen-jev-open-book)/catalog.txt   # the newest open-book run
SINGERS='{"lennon":"John Lennon","mccartney":"Paul McCartney","harrison":"George Harrison","starr":"Ringo Starr"}'
YEARS='{"1962":"1962","1963":"1963","1964":"1964","1965":"1965","1966":"1966","1967":"1967","1968":"1968","1969":"1969","1970":"1970"}'
# One case per line: name, question, the section that holds the answer, the right option, the options. Tabs separate them.
TAB=$(printf '\t')
CASES="octopus${TAB}Who sang lead on Octopus's Garden?${TAB}abbey_road${TAB}starr${TAB}$SINGERS
tomorrow${TAB}In what year was the Beatles song \"Tomorrow Never Knows\" first released?${TAB}revolver${TAB}1966${TAB}$YEARS"
PICK="Which section of the Beatles catalog holds the facts needed to answer the question in the text?"
LEAD="Which of the Beatles sang lead vocals on the song?"
SECTIONS='rtrimstr("\n") | split("\n\n") | map({header: split("\n")[0], text: .})
  | map(.label = (.header | sub(" \\(\\d{4}-\\d\\d-\\d\\d\\)$"; "") | ascii_downcase | gsub("[^a-z0-9]+"; "_") | gsub("^_+|_+$"; "")))'

tt() { # verb question [args...] < records > details: one call with the shared flags
  verb=$1; shift
  "$TT" "$verb" "$@" --jsonl --details --model "${BEATLES_BENCH_MODEL:-jev-latest}" "$flag" "$RUN/recording"
}
now() { date +%s.%N; }
printf 'arm\twall_s\n' > "$OUT/times.tsv"
timed() { # arm verb question [args...]: run tt into OUT/arm.jsonl and log its wall time
  arm=$1; shift
  start=$(now); tt "$@" > "$OUT/$arm.jsonl"; end=$(now)
  printf '%s\t%s\n' "$arm" "$(jq -n "($end - $start) * 1000 | round / 1000")" >> "$OUT/times.tsv"
}
tag_arm() { # arm field...: tag the song records by lead singer, sending only the named fields
  arm=$1; shift
  fields=""
  for f; do fields="$fields --field $f"; done
  # shellcheck disable=SC2086
  timed "$arm" tag "$LEAD" --label Lennon="John Lennon sang lead." --label McCartney="Paul McCartney sang lead." \
    --label Harrison="George Harrison sang lead." --label Starr="Ringo Starr sang lead." $fields --input "$OUT/songs.jsonl"
}

# 1. Each case: answer from memory, pick two sections, glue them before the question, answer.
single_case() { # name question options
  name=$1 q=$2 opts=$3
  jq -nc --arg q "$q" --argjson o "$opts" '{id: "memory", input: ("Question: " + $q), options: $o}' \
    | timed "${name}_memory" choose "$q" --field /input --options /options
  jq -Rsc --arg q "$q" "$SECTIONS"' | {id: "pick", input: ("Question: " + $q), options: (map({(.label): .header}) | add)}' \
    < "$CATALOG" | timed "${name}_pick" choose "$PICK" --field /input --options /options
  jq -Rsc --arg q "$q" --argjson o "$opts" --slurpfile pick "$OUT/${name}_pick.jsonl" "$SECTIONS"'
    | ($pick[0].answer.probabilities | to_entries | sort_by(-.value) | .[:2] | map(.key)) as $top
    | {id: "answer", top: $top, input: ("Catalog:\n" + (map(select(.label | IN($top[]))) | map(.text) | join("\n\n")) + "\n\nQuestion: " + $q),
       options: $o}' < "$CATALOG" | timed "${name}_answer" choose "$q" --field /input --options /options
}
printf '%s\n' "$CASES" | while IFS=$TAB read -r name q needed gold opts; do single_case "$name" "$q" "$opts"; done

# 2. One context over many records: the Abbey Road songs, three ways.
jq -Rsc --rawfile songs "$ROOT/data/songs.tsv" "$SECTIONS"'
  | (map(select(.header | startswith("Abbey Road ("))) | .[0].text) as $context
  | $songs | rtrimstr("\n") | split("\n") | map(split("\t")) | .[0] as $h
  | .[1:] | map([$h, .] | transpose | map({(.[0]): .[1]}) | add) | map(select(.first_album == "Abbey Road"))
  | .[] | {id: .title, song: .title, gold: (.lead_vocals | split("+") | sort), context: $context,
           text: ("Catalog:\n" + $context + "\n\nText: " + .title)}' < "$CATALOG" > "$OUT/songs.jsonl"
tag_arm memory /song
tag_arm glued /text
tag_arm apart /context /song

# 3. Grounding: annotate each apart answer against the gold answer and against the context.
jq -c '{id: .input.id, song: .input.song, context: .input.context, gold: (.input.gold | join(", ")),
        output: ("Lead vocals on " + .input.song + ": " + (if .value == [] then "none" else .value | join(", ") end) + ".")}' \
  "$OUT/apart.jsonl" > "$OUT/grounding.jsonl"
timed annotate annotate "$HERE/rad_pipeline.checks.json" --input "$OUT/grounding.jsonl"
# The same songs with one wrong singer each: the singers not in the truth, taken in turn by song.
jq -sc 'to_entries[] | .key as $i | .value | (["Lennon", "McCartney", "Harrison", "Starr"] - .gold) as $wrong
  | {id, song, context, gold: (.gold | join(", ")), output: ("Lead vocals on " + .song + ": " + $wrong[$i % ($wrong | length)] + ".")}' \
  "$OUT/songs.jsonl" > "$OUT/wrong.jsonl"
timed wrong_singer annotate "$HERE/rad_pipeline.checks.json" --input "$OUT/wrong.jsonl"

# Score. A song is right when its tag set matches the truth exactly. A check is right when it agrees with that match.
# A case's pick is right when its top two hold the needed section. A wrong singer is caught when grounded is false.
S() { jq -nr --slurpfile memory "$OUT/memory.jsonl" --slurpfile glued "$OUT/glued.jsonl" --slurpfile apart "$OUT/apart.jsonl" \
  --slurpfile checks "$OUT/annotate.jsonl" --slurpfile wrong "$OUT/wrong_singer.jsonl" "$@"; }
DEFS='def tokens: map(.meta.usage.input_tokens // 0) | add;
  def ok: (.value | sort) == .input.gold;
  def arm($name): [$name, (map(select(ok)) | length), length, tokens];
  ($apart | map(ok)) as $truth'
printf 'arm\tright\tof\tinput_tokens\n' > "$OUT/scores.tsv"
printf '%s\n' "$CASES" | while IFS=$TAB read -r name q needed gold opts; do
  jq -nr --arg n "$name" --arg need "$needed" --arg gold "$gold" --slurpfile m "$OUT/${name}_memory.jsonl" \
    --slurpfile p "$OUT/${name}_pick.jsonl" --slurpfile a "$OUT/${name}_answer.jsonl" \
    'def tokens: map(.meta.usage.input_tokens // 0) | add;
     [$n + "_memory", (if $m[0].value == $gold then 1 else 0 end), 1, ($m | tokens)],
     [$n + "_pick", (if $a[0].input.top | index($need) then 1 else 0 end), 1, ($p | tokens)],
     [$n + "_answer", (if $a[0].value == $gold then 1 else 0 end), 1, ($a | tokens)] | @tsv' >> "$OUT/scores.tsv"
done
S "$DEFS"' | ($memory | arm("memory")), ($glued | arm("glued")), ($apart | arm("apart")),
  ["annotate", ([range($checks | length) | select($checks[.].value.correct == $truth[.] and $checks[.].value.grounded == $truth[.])] | length),
   ($checks | length), ($checks | tokens)],
  ["wrong_singer", ($wrong | map(select(.value.grounded == false)) | length), ($wrong | length), ($wrong | tokens)] | @tsv' >> "$OUT/scores.tsv"
S "$DEFS"' | ["song", "gold", "memory", "glued", "apart", "apart_right", "correct", "grounded", "wrong_output", "wrong_correct", "wrong_grounded"],
  (range($apart | length) as $i | [$apart[$i].input.song, ($apart[$i].input.gold | join("+")),
    ($memory[$i].value | join("+")), ($glued[$i].value | join("+")), ($apart[$i].value | join("+")),
    $truth[$i], $checks[$i].value.correct, $checks[$i].value.grounded,
    $wrong[$i].input.output, $wrong[$i].value.correct, $wrong[$i].value.grounded]) | map(tostring) | @tsv' > "$OUT/checks.tsv"
cat "$OUT/scores.tsv"
