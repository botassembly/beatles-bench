# recognize-how

The recognize-how slide. It opens up the recognize slide's sentence piece by piece. `recognize` in `thinkthen 0.1.0` asks in two steps. First it asks where each piece stands in a name. Then it asks which kind each name is.

## Run it

The page reads the recognize folder's recording with `--details`. Run this in [`../recognize/`](../recognize/) with no key:

```sh
printf '%s' "Ringo Starr wrote Octopus's Garden on a boat off Sardinia, and the band recorded it at Abbey Road Studios for the album Abbey Road." |
  thinkthen recognize person song album place --threshold 0.01 --model jev-latest --replay recording --details
```

Each piece's answers sit under `answer.pieces`, and each name's under `answer.names`. A piece is a word or a punctuation mark.

## What the page shows

Each piece, and the place in a name it most likely holds. BEGIN is the first piece of a name of two or more pieces. INSIDE is a middle piece, and END is the last. SINGLE is a one-piece name. OUT is outside any name.

| # | Piece | Place | Probability |
| --- | --- | --- | --- |
| 1 | Ringo | BEGIN | 0.93 |
| 2 | Starr | END | 0.89 |
| 3 | wrote | OUT | 0.94 |
| 4 | Octopus | BEGIN | 0.81 |
| 5 | ' | INSIDE | 0.73 |
| 6 | s | INSIDE | 0.67 |
| 7 | Garden | END | 0.87 |
| 8 | on | OUT | 0.99 |
| 9 | a | OUT | 0.93 |
| 10 | boat | OUT | 0.97 |
| 11 | off | OUT | 0.98 |
| 12 | Sardinia | SINGLE | 0.95 |
| 13 | , | OUT | 0.42 |
| 14 | and | OUT | 1.0 |
| 15 | the | OUT | 0.99 |
| 16 | band | OUT | 0.95 |
| 17 | recorded | OUT | 1.0 |
| 18 | it | OUT | 0.99 |
| 19 | at | OUT | 1.0 |
| 20 | Abbey | BEGIN | 0.83 |
| 21 | Road | INSIDE | 0.43 |
| 22 | Studios | END | 0.79 |
| 23 | for | OUT | 0.99 |
| 24 | the | OUT | 0.99 |
| 25 | album | OUT | 0.48 |
| 26 | Abbey | BEGIN | 0.87 |
| 27 | Road | END | 0.62 |
| 28 | . | END | 0.63 |

The pieces group into names, such as Ringo through Starr. Each name then gets its kind, with "none of these" as a fifth choice:

| Name | Kind | Probability |
| --- | --- | --- |
| Ringo Starr | person | 1.0 |
| Octopus's Garden | song | 1.0 |
| Sardinia | place | 1.0 |
| Abbey Road Studios | place | 0.97 |
| Abbey Road | album | 1.0 |

The two steps used `6871` input tokens and `1846` output tokens, from `meta.usage`. The model was `jev-1.13.0`. `--plan` in place of `--replay recording --details` sends nothing and plans the first request.

The slide shows an earlier planner, which asked two questions of every word in one call. Git history keeps that recording, from thinkthen main at 02dc0b96.

## The build

[`../recognize/run.txt`](../recognize/run.txt).

## The check

`tests/test_examples.py`, `RecognizeHowTest`, replays the command above with no key. It checks each piece row, each name, and both token counts against this page.
