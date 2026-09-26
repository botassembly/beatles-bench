# recognize-how

The recognize-how slide. It opens up the recognize slide's sentence word by word. One call asks two questions of every word. Is it part of a name? Which kind is it? `recognize` then joins each run of in-name words into one name.

## Run it

The slide reads the recognize folder's recording with `--details`. Run this in [`../recognize/`](../recognize/) with no key:

```sh
printf '%s' "Ringo Starr wrote Octopus's Garden on a boat off Sardinia, and the band recorded it at Abbey Road Studios for the album Abbey Road." |
  thinkthen recognize person song album place --threshold 0.01 --replay recording --details
```

Each word's answers sit under `answer.tokens`. `detection_probability` is the "in a name" answer. `kind_probabilities` gives person, song, album, and place in that order.

## What the slide shows

Each word, its "in a name" probability, and its top kind:

| # | Word | In a name | Top kind |
| --- | --- | --- | --- |
| 1 | Ringo | 1.0 | person |
| 2 | Starr | 1.0 | person |
| 3 | wrote | 0.0 | person |
| 4 | Octopus's | 0.99 | song |
| 5 | Garden | 0.99 | song |
| 6 | on | 0.0 | song |
| 7 | a | 0.01 | song |
| 8 | boat | 0.0 | place |
| 9 | off | 0.0 | place |
| 10 | Sardinia | 0.98 | place |
| 11 | , | 0.0 | place |
| 12 | and | 0.0 | place |
| 13 | the | 0.01 | person |
| 14 | band | 0.05 | person |
| 15 | recorded | 0.0 | place |
| 16 | it | 0.02 | song |
| 17 | at | 0.0 | place |
| 18 | Abbey | 0.99 | place |
| 19 | Road | 1.0 | place |
| 20 | Studios | 0.99 | place |
| 21 | for | 0.0 | place |
| 22 | the | 0.01 | album |
| 23 | album | 0.04 | album |
| 24 | Abbey | 0.99 | album |
| 25 | Road | 0.99 | album |
| 26 | . | 0.11 | album |

A word is in a name when its probability is above one half. Each run of in-name words is one name, and its kind is the kind most of its words picked. The runs give the five names `recognize` prints:

| Name | Kind |
| --- | --- |
| Ringo Starr | person |
| Octopus's Garden | song |
| Sardinia | place |
| Abbey Road Studios | place |
| Abbey Road | album |

The call used `8092` input tokens and `1918` output tokens, from `meta.usage`. The model was `jev-1.13.0`. `--dry-run` in place of `--replay recording --details` sends nothing and plans one request.

## The build

[`../recognize/run.txt`](../recognize/run.txt).

## The check

`tests/test_examples.py`, `RecognizeHowTest`, replays the command above with no key. It checks each word row, each name, and both token counts against this page. It skips with no `THINKTHEN_BIN` and no `thinkthen` on `PATH`.
