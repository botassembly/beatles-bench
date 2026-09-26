# Input: one example's case files, slurped. $out: its outputs.jsonl, slurped. $ex: its folder name.
# Prints the right answers and the input tokens of the cold side and the context side.
# A form counts each field. A score is right when its likeliest level names the whole minute nearest the real length.
def right($c; $row):
  if ($c.truth | type) == "object" then [$c.truth | keys[] as $k | select($row.value[$k] == $c.truth[$k])] | length
  elif ($c.truth | type) == "number" then
    if ($row.answer.level | capture("(?<n>[0-9]+)").n | tonumber) == ($c.truth | round) then 1 else 0 end
  elif $c.function == "find" then if $row.value.id == $c.truth then 1 else 0 end
  elif $row.value == $c.truth then 1 else 0 end;
($out | map({(.id): .}) | add) as $o
| map(select(.truth != null) | . as $c | $o[.id] as $r
    | {side: (if (.id | test("context")) then "context" else "cold" end), tokens: $r.input_tokens,
       right: right($c; $r.rows[0]), asked: (if (.truth | type) == "object" then (.truth | length) else 1 end)})
| group_by(.side)
| map({(.[0].side): {right: (map(.right) | add), of: (map(.asked) | add), input_tokens: (map(.tokens) | add)}})
| {example: $ex} + add
