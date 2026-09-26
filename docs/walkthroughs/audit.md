# How to find your bar with audit

Use `audit` when you have saved answers and an answer key, and you want to know which bar to use. It grades the saved answers against the key. It reports how many are right at any bar, and it suggests a bar. It tunes that bar on one half of the records and checks it on the other half. It sends no request and needs no API key.

Jev answered one question about 70 Beatles songs: "Is this song on the album Abbey Road?" Seven of the 70 are on it. Which bar turns the most of those answers into right ones?

A bar can go wrong two ways. A low bar says yes too often, so songs from other albums get in. A high bar misses real ones, so Abbey Road songs get left out. The best bar makes the fewest mistakes of both kinds together.

## The files

- `rows.jsonl` holds Jev's 70 saved answers, one line per song.
- `key.jsonl` holds the key, one line per song, taken from `first_album` in `data/songs.tsv`.
- `recording/` holds the saved requests and answers, so you can ask again with no key.

The first two lines of each:

```sh
jq -c '{input, yes: .answer.probability}' rows.jsonl | head -2
```

```json
{"input":{"id":"audit-01","input":"Here Comes the Sun"},"yes":0.97}
{"input":{"id":"audit-02","input":"Come Together"},"yes":0.96}
```

```sh
head -2 key.jsonl
```

```json
{"id": "Here Comes the Sun", "value": "yes"}
{"id": "Come Together", "value": "yes"}
```

Each answer line keeps its record as `{"id": "audit-01", "input": "Here Comes the Sun"}`. The key names each song by its title, and audit reads the key's field `value`. `scripts/score/tune.sh` writes `rows.jsonl` from `outputs.jsonl`.

Everything in the folder:

- `audit-cold.jsonl` and `audit-context.jsonl`: the 70 cases each, one song per case, with `truth` from `first_album`. `key.jsonl`: the key. `scripts/generate/examples.py` writes both. It holds the 70 titles as a fixed list. They were chosen by hand for the talk.
- `recording/`: every request and response. `outputs.jsonl` and `timing.tsv`: the committed answers and wall times.
- `rows.jsonl` and `rows-context.jsonl`: the cold and context answer lines audit and diff read. `audit-asrun.json`: the grade at the bar each answer was asked with (0.5), with the suggested bar. `audit-BAR.json`: the grade at each bar.
- `run`: the slide's command, as the folder's README gives it. `scripts/run/example.sh audit live OUT | replay [OUT]` asks both cases through `scripts/run/functions.sh` for the full bench, then runs `scripts/score/tune.sh`. `tune.sh [DIR]` writes the rows and the audit files. It copies `key.jsonl` into a `DIR` other than `functions/audit`.

## Run it

Run this in `functions/audit`:

```sh
thinkthen audit rows.jsonl key.jsonl --id /input --table
```

```text
Is this song on the album Abbey Road?  (decide, 70 rows, 70 labeled, 0 failed, rule as run)
  agreement 0.714 (95% 0.599 to 0.807): 50 right, 20 wrong, 0 unresolved, 0 tied
  said yes, key no: 20   said no, key yes: 0   yes recall 1.000   mean p(yes) 0.443   AUC 0.971
  calibration error 0.343 (95% 0.293 to 0.406); the interval resamples the records; it does not cover rerun noise, so compare two runs of the same records
  suggested cut 0.78 (most agreement on the tuning part; seeded split, tuned on 35, checked on 35 held out): held agreement 0.771 as run -> 0.943 at the cut, yes recall 1.000 -> 1.000
    cut  threshold  answered coverage accuracy
    0.5  0.5              70    1.000    0.714
   0.55  0.45:0.55        63    0.900    0.730
    0.6  0.4:0.6          55    0.786    0.782
   0.65  0.35:0.65        46    0.657    0.804
    0.7  0.3:0.7          37    0.529    0.811
   0.75  0.25:0.75        30    0.429    0.800
    0.8  0.2:0.8          23    0.329    0.870
   0.85  0.15:0.85        17    0.243    0.882
    0.9  0.1:0.9          13    0.186    0.846
   0.95  0.05:0.95         6    0.086    0.833
    1.0  0:1               0    0.000        -
```

- `--id /input` matches each answer to the key by its title.
- `--table` prints the report for a person. Without it, audit prints one JSON object.
- `--threshold 0.78` grades every answer again at that bar. No new call goes out.

audit sends no request and needs no key. It reads only the two files.

To ask the 70 questions again from the committed recording with no key:

```sh
jq -c '.records[]' audit-cold.jsonl |
  thinkthen decide 'Is this song on the album Abbey Road?' --jsonl --field /input --details --replay recording
```

`scripts/run/example.sh audit replay` asks every case from the recording, then runs `scripts/score/tune.sh`, and writes it all to `replay/`. To ask your own server, run `scripts/run/example.sh audit live OUT` with `THINKTHEN_BASE_URL` and `THINKTHEN_API_KEY` set. The answers can then differ by a few points from these.

## Read it

audit graded the answers at seven bars. Each file holds one bar:

```sh
jq -c '{bar: .threshold, right, said_yes_wrong: .false_yes, said_no_wrong: .false_no}' audit-0.5.json audit-0.6.json audit-0.7.json audit-0.78.json audit-0.8.json audit-0.9.json audit-0.95.json
```

```json
{"bar":0.5,"right":50,"said_yes_wrong":20,"said_no_wrong":0}
{"bar":0.6,"right":58,"said_yes_wrong":12,"said_no_wrong":0}
{"bar":0.7,"right":63,"said_yes_wrong":7,"said_no_wrong":0}
{"bar":0.78,"right":66,"said_yes_wrong":4,"said_no_wrong":0}
{"bar":0.8,"right":66,"said_yes_wrong":3,"said_no_wrong":1}
{"bar":0.9,"right":65,"said_yes_wrong":2,"said_no_wrong":3}
{"bar":0.95,"right":65,"said_yes_wrong":1,"said_no_wrong":4}
```

At 0.5, Jev says yes to 20 songs that are not on Abbey Road. It misses none. As the bar rises, those wrong yeses fall away. At 0.78, audit's suggested bar, four wrong yeses remain and no real Abbey Road song is missed. At 0.8, one real Abbey Road song falls below the bar. At 0.95, four are missed. The bars 0.78 and 0.8 tie at 66 right.

The suggested bar comes with the numbers behind it:

```sh
jq -c '{cut: .suggested.cut, auc, tuned: .suggested.tune.at_cut.agreement, held: .suggested.held.at_cut.agreement}' audit-asrun.json
```

```json
{"cut":0.78,"auc":0.970522,"tuned":0.942857,"held":0.942857}
```

audit tuned the bar on a seeded half of 35 songs and checked it on the other 35. It got 0.943 right on both halves. An AUC of 0.971 says Jev nearly always gives a real Abbey Road song a higher probability than a song from another album. The order is good. The default bar of 0.5 sits in the wrong place for this question.

Four answers stay wrong at 0.78:

```sh
jq -c --slurpfile key key.jsonl '($key | map({(.id): .value}) | add) as $k | {song: .input.input, yes: .answer.probability, key: $k[.input.input]} | select((.yes >= 0.78) != (.key == "yes"))' rows.jsonl
```

```json
{"song":"A Day in the Life","yes":0.97,"key":"no"}
{"song":"The Long and Winding Road","yes":0.92,"key":"no"}
{"song":"Martha My Dear","yes":0.79,"key":"no"}
{"song":"Lovely Rita","yes":0.81,"key":"no"}
```

All four are songs from other albums. A Day in the Life first came out on Sgt. Pepper's Lonely Hearts Club Band, and so did Lovely Rita. The Long and Winding Road came out on Let It Be, and Martha My Dear on The Beatles (White Album). Jev is sure of the first two from memory. A Day in the Life sits at 0.97, level with Here Comes the Sun and Maxwell's Silver Hammer, so no bar removes it without losing them. A bar of 0.95 already misses four real Abbey Road songs. [`diff`](diff.md) compares these cold answers with the context run below.

## With context

The bar matters most when Jev answers from memory. The context case, `audit-context.jsonl`, asks the same question of the same 70 songs. Each record sends the song's catalog entry and then the title:

```text
Catalog:
Abbey Road (1969-09-26)
Maxwell's Silver Hammer (lead: McCartney; written: Lennon–McCartney; 3:27; released 1969-09-26; first album: Abbey Road)
Text: Maxwell's Silver Hammer
```

The question opens "The text gives a catalog entry and then names a song by the Beatles." `scripts/score/tune.sh` writes those answer lines to `rows-context.jsonl`:

```sh
jq -sc 'map(.answer.probability) | {songs: length, yes: map(select(. >= 0.5)) | length, lowest_yes: (map(select(. >= 0.5)) | min), highest_no: (map(select(. < 0.5)) | max)}' rows-context.jsonl
```

```json
{"songs":70,"yes":7,"lowest_yes":0.98,"highest_no":0.33}
```

With the entries, seven songs get a yes, all at 0.98 or more. The other 63 sit at 0.33 or less. Any bar above 0.33 and up to 0.98 gives the same answers. The choice of bar stops mattering. [`diff`](diff.md) checks each answer against the key and finds all 70 right. The audit files grade the cold run alone.

## What can go wrong

- **The shared traps.** A replay miss, a missing key, and a cache bound to another server can stop any command. [How to run the bench for free](../run-it-for-free.md#what-can-go-wrong) gives each exit code and its fix.
- **The ids must match the key.** Without `--id /input`, audit matches by the record's `id`, such as `audit-11`. The key names songs by title, so no answer matches. audit then reports "0 labeled" and still exits 0. Check the labeled count before you read a grade.
- **A suggested bar comes from half the records.** audit tunes on one seeded half and checks on the other. With 70 records, each half holds 35. Read the held-out number before you trust the bar.
- **A bar cannot fix a sure miss.** A Day in the Life at 0.97 stays wrong at any bar that keeps the real Abbey Road songs.

## The slide

![audit finds your bar](../../functions/audit/slide.png)

The table lists the fourteen songs with the highest probability of yes in `rows.jsonl`. It runs from A Day in the Life at 0.97 down to The Ballad of John and Yoko, and by title within a tie. A green check marks each song on Abbey Road (`data/songs.tsv`, `first_album`), and a red cross each song that is not. Each dashed line marks the bar that gives one score its best value. The bar sits on the left and the score on the right. The slide draws two dashed lines. The upper line sits just under Come Together. Precision peaks there at 75%. Accuracy peaks at 94%, recall at 100%, and F1 at 78%, all at 0.78. That is the cut audit suggests.

Today audit picks its bar only by the most right answers. That measure is accuracy. It does not yet pick a bar by precision, recall, or F1. The slide works out those three by hand from `rows.jsonl` and `key.jsonl`.

## Related

- [How to see what changed with diff](diff.md): compare these answers with the context run.
- [How to answer yes or no with decide](decide.md): the command that made these answers.
- [How to keep the records that match with filter](filter.md): a bar in use.
