# recognize

![recognize labels things it finds](slide.png)

The slide finds the people, songs, albums, and places in one sentence. `recognize` names each span, its kind, and a strength. `./run` keeps every name at `0.01` or more.

`thinkthen 0.1.0` recorded these answers on 2026-10-02. It asks where each word stands in a name: the first word, a middle word, the last word, a one-word name, or outside any name. The slide shows the answers of an earlier planner, recorded on 2026-09-25 with thinkthen main at 02dc0b96. Git history keeps that recording.

## Run it

```sh
./run
```

```json
{"text":"Ringo Starr","start":0,"end":11,"length":11,"kind":"person","strength":0.9943}
{"text":"Octopus's Garden","start":18,"end":34,"length":16,"kind":"song","strength":0.9886}
{"text":"Sardinia","start":49,"end":57,"length":8,"kind":"place","strength":0.9694}
{"text":"Abbey Road Studios","start":87,"end":105,"length":18,"kind":"place","strength":0.8247}
{"text":"Abbey Road","start":120,"end":130,"length":10,"kind":"album","strength":0.664}
```

A higher bar keeps fewer names:

```sh
./run threshold 0.99
```

```json
{"text":"Ringo Starr","start":0,"end":11,"length":11,"kind":"person","strength":0.9943}
```

`./run live` asks your own server. It sends 2 calls.

## The lessons

- **You control the bar.** At `0.99`, only Ringo Starr stays. Octopus's Garden, at 0.9886, falls just under it.
- **The number is the number.** The same words, Abbey Road, name part of a place at 0.8247 and an album at 0.664. Each span gets its own kind and strength.

## The files

- `recognize-cold.jsonl`: the case.
- `outputs.jsonl`, `timing.tsv`, and `recording/`: the recorded answers.
- `run.txt`: the thinkthen build and the model that recorded the answers.

The talk's page for this slide: [thinkthen.dev/learn/beatles-bench/recognize](https://thinkthen.dev/learn/beatles-bench/recognize/).
