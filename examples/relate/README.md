# relate

![relate links names into a graph](slide.png)

The slide links seven songs to singers and albums. `relate.json` names the two relations, `sung_by` and `appears_on`. `relate` gives each possible edge a probability. `./run` keeps the edges at `0.5` or more, as the slide does.

`thinkthen 0.1.0` recorded these answers on 2026-10-02. relate asks one yes or no question for each pair a rule allows, all in one request. The slide shows the answers of an older planner, recorded on 2026-09-25 with thinkthen main at 02dc0b96. Git history keeps that recording.

## Run it

```sh
./run
```

```json
["sung_by","Octopus's Garden","Ringo Starr",0.92]
["sung_by","Something","George Harrison",0.79]
["sung_by","Come Together","John Lennon",0.72]
["sung_by","Here Comes the Sun","George Harrison",0.79]
["sung_by","Yesterday","Paul McCartney",0.86]
["sung_by","Eleanor Rigby","Paul McCartney",0.53]
["sung_by","Taxman","George Harrison",0.72]
["appears_on","Octopus's Garden","Abbey Road",0.74]
["appears_on","Octopus's Garden","Revolver",0.7]
["appears_on","Something","Abbey Road",0.93]
["appears_on","Come Together","Abbey Road",0.91]
["appears_on","Here Comes the Sun","Abbey Road",0.94]
["appears_on","Yesterday","Help!",0.77]
["appears_on","Yesterday","Revolver",0.71]
["appears_on","Eleanor Rigby","Revolver",0.91]
["appears_on","Taxman","Revolver",0.95]
```

A lower bar shows the edges under `0.5`. Here are Yesterday's:

```sh
./run threshold 0.01 | grep Yesterday
```

```json
["sung_by","Yesterday","John Lennon",0.37]
["sung_by","Yesterday","Paul McCartney",0.86]
["sung_by","Yesterday","George Harrison",0.06]
["sung_by","Yesterday","Ringo Starr",0.06]
["appears_on","Yesterday","Abbey Road",0.02]
["appears_on","Yesterday","Help!",0.77]
["appears_on","Yesterday","Revolver",0.71]
```

`./run live` asks your own server. It sends 1 call.

## The lessons

- **You control the bar.** At `0.5`, Yesterday links to Paul McCartney, to Help! and to Revolver. At `0.01`, John Lennon joins at 0.37.
- **The number is the number.** Octopus's Garden links to Abbey Road at 0.74 and to Revolver at 0.7. The first is right and the second is wrong, and the two numbers sit close. Yesterday's edge to Revolver is 0.71, and it is wrong too.

## The files

- `relate.json`: the two relations.
- `relate-cold.jsonl`: the case, with its names.
- `outputs.jsonl`, `timing.tsv`, and `recording/`: the recorded answers.
- `run.txt`: the thinkthen build and the model that recorded the answers.

The talk's page for this slide: [thinkthen.dev/learn/beatles-bench/relate](https://thinkthen.dev/learn/beatles-bench/relate/).
