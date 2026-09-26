# How to see what changed with diff

Use `diff` when you have two runs of the same records and want to know what changed. It lists the saved answers that changed between the two runs. It needs no answer key. With an answer key, it marks each change as fixed or broken. It ends with a summary and a McNemar test of whether the change is beyond chance. It sends no request.

[`audit`](audit.md) asked 70 Beatles songs one question, "Is this song on the album Abbey Road?", in two runs. The cold run sends the title alone, so Jev answers from memory. The context run sends each song's catalog entry before the title. Which answers change when the facts are in the text, and does each change fix a mistake or make one?

Cold answers can go wrong two ways. Jev can say yes to a song from another album, or no to a real Abbey Road song. diff counts both kinds of change.

## The files

- `../audit/rows.jsonl` holds the cold answers, one line per song.
- `../audit/rows-context.jsonl` holds the answers with the catalog entry.
- `../audit/key.jsonl` holds the key, taken from `first_album` in `data/songs.tsv`.

[How to find your bar with audit](audit.md) shows a line of each. diff needs no recording. It reads saved answers and sends no request.

Everything in the folder:

- `diff.jsonl`: each change, then the summary, as `diff` prints them.
- `run`: the slide's command, as the folder's README gives it.

`scripts/score/context_diff.sh [IN [OUT]]` writes `OUT/a.jsonl` and `OUT/b.jsonl` from `IN/rows.jsonl` and `IN/rows-context.jsonl`, then `OUT/diff.jsonl` through `scripts/score/diff_guard.sh --no-digest`. `IN` defaults to `functions/audit` and `OUT` to `functions/diff`. Only `diff.jsonl` is committed. It needs no mode, no API key, and no recording.

## Run it

Run this in `functions/diff`. `context_diff.sh` reads both answer files and the key from `functions/audit`. The two runs send different text, so it first sets each line's input to the song's title. That gives both runs and the key one shared id:

```sh
title='.input = {id: (.input.input | split("\nText: ") | last)}'
jq -c "$title" ../audit/rows.jsonl > a.jsonl
jq -c "$title" ../audit/rows-context.jsonl > b.jsonl
thinkthen diff a.jsonl b.jsonl --threshold 0.5 --key ../audit/key.jsonl --table
```

```text
A Day in the Life  yes -> no  p 0.97 -> 0.12  key no: gained
The Long and Winding Road  yes -> no  p 0.92 -> 0.18  key no: gained
Martha My Dear  yes -> no  p 0.79 -> 0.02  key no: gained
Piggies  yes -> no  p 0.75 -> 0.02  key no: gained
Lovely Rita  yes -> no  p 0.81 -> 0.02  key no: gained
The Ballad of John and Yoko  yes -> no  p 0.72 -> 0.33  key no: gained
Get Back  yes -> no  p 0.66 -> 0.11  key no: gained
Good Night  yes -> no  p 0.52 -> 0.02  key no: gained
In My Life  yes -> no  p 0.59 -> 0.06  key no: gained
Julia  yes -> no  p 0.64 -> 0.02  key no: gained
Taxman  yes -> no  p 0.77 -> 0.03  key no: gained
Back in the U.S.S.R.  yes -> no  p 0.58 -> 0.02  key no: gained
Don't Pass Me By  yes -> no  p 0.67 -> 0.02  key no: gained
Glass Onion  yes -> no  p 0.62 -> 0.02  key no: gained
Penny Lane  yes -> no  p 0.58 -> 0.06  key no: gained
Eleanor Rigby  yes -> no  p 0.52 -> 0.04  key no: gained
Let It Be  yes -> no  p 0.51 -> 0.10  key no: gained
Ob-La-Di, Ob-La-Da  yes -> no  p 0.57 -> 0.02  key no: gained
Michelle  yes -> no  p 0.63 -> 0.03  key no: gained
Ticket to Ride  yes -> no  p 0.57 -> 0.02  key no: gained
A -> B (at 0.5 and 0.5): 20 of 70 changed; yes -> no 20; gained 20, lost 0 (50 -> 70 right of 70); McNemar p 0.000 on right answers
```

- `--threshold 0.5` reads each answer as yes or no at 0.5 in both runs.
- `--key` marks each change as gained or lost.
- `--table` prints the report for a person. Without it, diff prints one JSON object per change and then a summary.

Leave out `--key`, and diff still lists every change and counts the moves from yes to no. `context_diff.sh` writes the JSON form to `diff.jsonl`. `./run.sh` writes it to `replay/`.

## Read it

```sh
jq -c 'select(.id) | {song: .id, cold: .probability[0], context: .probability[1], key, effect}' diff.jsonl
```

```json
{"song":"A Day in the Life","cold":0.97,"context":0.12,"key":"no","effect":"gained"}
{"song":"The Long and Winding Road","cold":0.92,"context":0.18,"key":"no","effect":"gained"}
{"song":"Martha My Dear","cold":0.79,"context":0.02,"key":"no","effect":"gained"}
{"song":"Piggies","cold":0.75,"context":0.02,"key":"no","effect":"gained"}
{"song":"Lovely Rita","cold":0.81,"context":0.02,"key":"no","effect":"gained"}
{"song":"The Ballad of John and Yoko","cold":0.72,"context":0.33,"key":"no","effect":"gained"}
{"song":"Get Back","cold":0.66,"context":0.11,"key":"no","effect":"gained"}
{"song":"Good Night","cold":0.52,"context":0.02,"key":"no","effect":"gained"}
{"song":"In My Life","cold":0.59,"context":0.06,"key":"no","effect":"gained"}
{"song":"Julia","cold":0.64,"context":0.02,"key":"no","effect":"gained"}
{"song":"Taxman","cold":0.77,"context":0.03,"key":"no","effect":"gained"}
{"song":"Back in the U.S.S.R.","cold":0.58,"context":0.02,"key":"no","effect":"gained"}
{"song":"Don't Pass Me By","cold":0.67,"context":0.02,"key":"no","effect":"gained"}
{"song":"Glass Onion","cold":0.62,"context":0.02,"key":"no","effect":"gained"}
{"song":"Penny Lane","cold":0.58,"context":0.06,"key":"no","effect":"gained"}
{"song":"Eleanor Rigby","cold":0.52,"context":0.04,"key":"no","effect":"gained"}
{"song":"Let It Be","cold":0.51,"context":0.1,"key":"no","effect":"gained"}
{"song":"Ob-La-Di, Ob-La-Da","cold":0.57,"context":0.02,"key":"no","effect":"gained"}
{"song":"Michelle","cold":0.63,"context":0.03,"key":"no","effect":"gained"}
{"song":"Ticket to Ride","cold":0.57,"context":0.02,"key":"no","effect":"gained"}
```

```sh
jq -c '.summary // empty | {records, changed, right_a, right_b, gained, lost, mcnemar_p}' diff.jsonl
```

```json
{"records":70,"changed":20,"right_a":50,"right_b":70,"gained":20,"lost":0,"mcnemar_p":0.000002}
```

Twenty answers change, all from yes to no. All twenty were songs from other albums, so every change is a fix. None breaks. Right answers go from 50 to 70 of 70. A Day in the Life drops from 0.97 to 0.12, and The Long and Winding Road from 0.92 to 0.18. No bar on the cold run could fix A Day in the Life without losing real Abbey Road songs. McNemar's test compares the 20 fixes with no breaks. A p of 0.000002 says a split that lopsided would be very rare by chance.

## With context

The context run is the second side of this comparison. [`audit`](audit.md) shows its answers. With the catalog entry, every answer sits far from the 0.5 bar. [`audit`](audit.md#with-context) gives the gap between the yes and no answers. [`decide`](decide.md) shows the same effect on six of these songs.

## What can go wrong

- **The shared traps.** A replay miss, a missing key, and a cache bound to another server can stop any command. [How to run the bench for free](../run-it-for-free.md#what-can-go-wrong) gives each exit code and its fix.
- **The ids must pair.** diff pairs answers by record id. The two runs here have different ids (`audit-01` and `audit-context-01`), so `context_diff.sh` first sets each id to the song's title. Without that step nothing pairs, and diff still exits 0.
- **Different questions pair without a word.** diff does not check that both runs asked the same question. `context_diff.sh` passes `--no-digest` to its guard because these two runs word the question differently by design.
- **No key, no verdict.** Leave out `--key`, and diff lists the changes without saying which fixed a mistake.

## The slide

![diff shows what changed](../../functions/diff/slide.png)

The slide shows 12 of the 70 songs, by title. The answer column gives the truth from `data/songs.tsv` (`first_album`). The next two columns give the probability of yes with no context and with the catalog entry. Every value is white, or muted on a dim row. A mark beside each value carries the colour.

The slide reads every answer at the band `0.2:0.8`. Its label at the top right says "THRESHOLD 0.2:0.8". A value of 0.8 or more reads yes. A value under 0.2 reads no. Any other value reads not sure. A red ✗ marks an answer Jev is sure of and gets wrong. An amber ? marks an answer Jev is not sure of. A green ✓ marks an answer Jev is sure of and gets right.

This page's own command runs at `--threshold 0.5`. The slide runs diff at `--threshold 0.2:0.8`. The bright rows with an arrow are the nine of these 12 that diff lists at the band. Two go from wrong to right. They are A Day in the Life and The Long and Winding Road. Seven go from not sure to right. They are Blackbird, Get Back, Glass Onion, In My Life, Something, Taxman, and Ticket to Ride. The dim rows kept the same answer in both runs.

Run it at the band. This command reads `a.jsonl` and `b.jsonl` from [Run it](#run-it) and prints the summary line:

```sh
thinkthen diff a.jsonl b.jsonl --threshold 0.2:0.8 --key ../audit/key.jsonl --table | tail -1
```

```text
A -> B (at 0.2:0.8 and 0.2:0.8): 48 of 70 changed; unresolved -> no 44; yes -> no 3; unresolved -> yes 1; gained 3, lost 0 (20 -> 68 right of 70); McNemar p 0.250 on right answers
```

At the band, 48 of 70 answers change. Three go from wrong to right, and diff counts them as gained. The other 45 go from not sure to right. diff calls them resolved. None goes wrong. Right answers go from 20 to 68 of 70. McNemar's test here counts only the three gained. Its p of 0.250 leaves out the 45 resolved answers.

## Related

- [How to find your bar with audit](audit.md): the two runs and the key.
- [Context and cost](../context-and-cost.md): what the catalog entry fixes and what it costs.
