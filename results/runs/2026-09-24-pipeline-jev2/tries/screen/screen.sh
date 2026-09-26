#!/bin/sh
# Screen candidates from memory with the pipeline's own memory request, cached into the run's recording.
set -eu
REC=results/runs/2026-09-24-pipeline-jev2/recording
OUT=${OUT:-results/runs/2026-09-24-pipeline-jev2/tries/screen}
mkdir -p "$OUT"
YEARS='{"1962":"1962","1963":"1963","1964":"1964","1965":"1965","1966":"1966","1967":"1967","1968":"1968","1969":"1969","1970":"1970"}'
WRITERS='{"lennon_mccartney":"John Lennon and Paul McCartney","harrison":"George Harrison","starr":"Ringo Starr","other":"a songwriter outside the Beatles"}'
one() { # name question options
  jq -nc --arg q "$2" --argjson o "$3" '{id: "memory", input: ("Question: " + $q), options: $o}' \
    | "$THINKTHEN_BIN" choose "$2" --field /input --options /options --jsonl --details --model jev-latest --cache "$REC" > "$OUT/$1.jsonl"
}
one yesterday 'In what year was the Beatles song "Yesterday" first released?' "$YEARS"
one tomorrow 'In what year was the Beatles song "Tomorrow Never Knows" first released?' "$YEARS"
one michelle 'In what year was the Beatles song "Michelle" first released?' "$YEARS"
one taxman 'Who wrote the Beatles song "Taxman"?' "$WRITERS"
one piggies 'Who wrote the Beatles song "Piggies"?' "$WRITERS"
one act_naturally 'Which album first included the Beatles song "Act Naturally"?' '{"beatles_for_sale":"Beatles for Sale","please_please_me":"Please Please Me","help":"Help!","abbey_road":"Abbey Road"}'
one and_i_love_her 'Which album first included the Beatles song "And I Love Her"?' '{"sgt_pepper_s_lonely_hearts_club_band":"Sgt. Pepper'"'"'s Lonely Hearts Club Band","please_please_me":"Please Please Me","magical_mystery_tour":"Magical Mystery Tour","a_hard_day_s_night":"A Hard Day'"'"'s Night"}'
