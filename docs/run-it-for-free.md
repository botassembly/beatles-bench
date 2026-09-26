# How to run the bench for free

Use this page to run every Beatles Bench answer on your own machine with no key, no network, and no spend. Every answer comes from a committed recording of a real call. Then point the same commands at any ThinkThen-compatible server.

## What you need

- `git`, `python3`, and `jq`.
- The `thinkthen` command. [thinkthen.dev/install](https://thinkthen.dev/install/) shows how to get it. `./run.sh` needs a build with `audit`: thinkthen main at 02dc0b96 or later, until a release carries it. `thinkthen audit --help` succeeds on such a build.

## Replay everything

```sh
git clone https://github.com/botassembly/beatles-bench
cd beatles-bench
./run.sh
```

With no server address set, `./run.sh` replays the newest recorded Jev run of every bench question and every worked example. It checks every replayed answer against the committed one, byte for byte. It prints 13 lines that start with "replayed": one for the bench questions and one for each of the twelve function folders, such as "replayed functions/annotate: every file matches the committed folder". It then rescores every run into `results/tables/` and prints the results tables. Nothing under git changes.

A replay sends no request, so it needs no key and costs nothing.

## Replay one example

`scripts/run/example.sh NAME replay` answers every case in `functions/NAME/` from its recording. It writes the answers to `replay/` in that folder. Run this from the top folder:

```sh
scripts/run/example.sh annotate replay && cmp functions/annotate/replay/outputs.jsonl functions/annotate/outputs.jsonl && echo same
```

```text
same
```

Each walkthrough gives `thinkthen` commands with `--replay recording`. Run them in the function's folder. Each prints the block shown below it on the page. Start with [How to fill in a form with annotate](walkthroughs/annotate.md).

## Read a case line

Each example keeps its cases in JSONL files, one case per line, such as `annotate-cold.jsonl`. The worked example scripts read them. Here is the second case of the annotate example:

```sh
sed -n 2p functions/annotate/annotate-cold.jsonl | jq .
```

```json
{
  "id": "annotate-cold-02",
  "function": "annotate",
  "args": [
    "annotate-cold-card.json",
    "--jsonl",
    "--field",
    "/input"
  ],
  "records": [
    {
      "id": "annotate-cold-02",
      "input": "Octopus's Garden"
    }
  ],
  "title": "Octopus's Garden",
  "truth": {
    "singer": "Ringo",
    "album": "Abbey Road",
    "year": "1969"
  },
  "fields": [
    [
      "songs.tsv",
      "Octopus's Garden",
      "lead_vocals",
      "Starr"
    ],
    [
      "songs.tsv",
      "Octopus's Garden",
      "first_album",
      "Abbey Road"
    ],
    [
      "songs.tsv",
      "Octopus's Garden",
      "year",
      "1969"
    ]
  ]
}
```

- `id` names the case. The answer in `outputs.jsonl` carries the same `id`.
- `function` is the ThinkThen command that answers it.
- `args` are the arguments the bench passes to that command.
- `records` are the records the command reads, one JSON object per line.
- `title` is the song, where the case has one song.
- `truth` is the right answer, or `null` when the bench holds no key.
- `fields` names where the truth came from: the file, the row, the column, and the value. [The data](the-data.md) shows the row.

## Ask your own server

Any ThinkThen-compatible server works. Set its address and key:

```sh
export THINKTHEN_BASE_URL=https://your-server/v1
export THINKTHEN_API_KEY=...
```

Then choose how much to ask:

- **One page's command.** Leave out `--replay recording`. The command asks your server and prints its answers. They can differ by a few points from the page.
- **One slide.** `./run live` in a function's folder asks the slide's command and prints the answers.
- **One example.** `scripts/run/example.sh annotate live OUT` asks every case into a new folder `OUT` with its own recording. It never writes into the committed folder.
- **The whole bench.** `./run.sh NAME` asks every bench question into `results/runs/<today>-NAME`, then every example. It adds your run to the results tables.

`thinkthen check` runs four fixed requests against the server and says whether it works with the command. `BEATLES_BENCH_MODEL` or `--model` names the model when one server offers several. The bench README gives the token cap and the price file.

## What can go wrong

These traps apply to every command in the worked examples.

| What you see | Exit | Why | The fix |
| --- | --- | --- | --- |
| "the replay folder holds no entry" | 5 | The request differs from every recorded one. A changed word, song, option, or trailing newline makes a new request. | Copy the command exactly, or leave out `--replay recording` to ask a server. |
| "`THINKTHEN_API_KEY` is unset or blank" | 4 | A live run has no key. | Set `THINKTHEN_API_KEY`, or add `--replay recording`. |
| A refusal that names the cache or "the recording folder" | 5 | The default answer cache binds to the first server it meets. A second server gets refused. | Add `--no-cache`, or set `THINKTHEN_CACHE` to another folder. |
| "this thinkthen has no audit command" | 2 | `./run.sh` needs a build with `audit`. | Install a build from thinkthen main at 02dc0b96 or later. |
| "the replay in ... differs from the committed answers" | 1 | A replayed answer differs from the committed file. | Check that no case or recording file changed. |

## Related

- [Beatles Bench](../README.md): what the bench measures and the headline results.
- [The data](the-data.md): where each right answer comes from.
- [Context and cost](context-and-cost.md): what the catalog fixes and what it costs.
