# Questions

The benchmark: 1,501 questions in 15 categories, one JSONL file per category. `scripts/generate/generate.py` writes them from `data/`, and `scripts/generate/make_suite.py` writes the function suite in `suite/`. Every draw uses a fixed seed, so a rebuild gives the same bytes.

## Categories

The Beatles-only headline covers every category but the two reversal-general ones: 1,313 questions.

- `forward` (224): one fact about a song: lead singer, first album, credited songwriter, or year.
- `reverse` (112): the answer is the song, given a Beatle or an album.
- `single-hop` (248): each hop of a multi-hop question asked alone.
- `multi-hop` (180): two facts chained, such as song to first album to year, or a song against a dated world event.
- `comparison` (60): which of two songs is longer, when they differ by 30 seconds or more.
- `shared-lead` (32): do two or more Beatles share the lead vocal?
- `lead-set` (104): one yes/no question per Beatle per song: does this Beatle sing a lead vocal on it?
- `near-neighbor` (60): the first album, where the wrong options are the albums released nearest in time.
- `near-neighbor-control` (60): the same songs, with wrong options drawn from all albums.
- `lexical-trap` (54): a wrong option shares a word with the question and the right one does not.
- `lexical-trap-control` (54): the same songs, with the trap swapped for a plain wrong option.
- `none-of-these` (60): the first album, with "none of these" as a legal answer.
- `reversal` (65): a Beatles pair where one end has at least 10 times the other's page views, asked from each end.
- `reversal-general` (146): the same test outside the Beatles.
- `reversal-general-shared-name` (42): pairs whose two ends share a surname, kept apart because word overlap can answer them from the name alone.

## The fields of a question

Each line is one JSON object.

- `id`: the question's name, such as `forward-singer-001`.
- `category` and `kind`: the file it sits in and the fact it asks.
- `function`: the ThinkThen command that answers it. `choose` picks one option. `decide` answers yes or no.
- `question`: the question text. `input`: the text the question is about, such as a song title.
- `options`: the choices, keyed by letter or name. Only the input leaves the machine. The options travel as option descriptions.
- `truth`: the right answer.
- `fields`: the data rows the question came from, as `[file, row, column, value]`.
- `group`: a lead-set question's song, or the question a control mirrors. `hops`: the single-hop questions behind a multi-hop question.

`keys/` holds one answer key per file for `thinkthen audit` and `thinkthen diff`. Each line is `{"id", "value"}`, and `value` is the `truth`. The key lines carry no `part`, so audit makes its own seeded split. The generator writes them.

## How truths are set

- A script sets every truth from the harvested tables in `data/`. No person and no language model wrote a question or chose an answer.
- Templates hold the wording. The data fills the slots and the options.
- Yes/no sets hold equal yes and no. The right letter of every lettered question is spread evenly over the letters.
- A lead question asks a song only when the list and the song's own article name the same Beatles.
- `data/pins/excluded.tsv` drops three items a source check found ambiguous. It never sets an answer.
- [reports/results.md](../reports/results.md#audit-history-fixes-on-2026-09-23) lists the label fixes of 2026-09-23. [data/datasheet.md](../data/datasheet.md) describes the set in full.

## The function suite

`suite/` holds the tests for all ten functions. Each JSONL line carries the command's arguments and its records, and every case names a `level`: `memory` asks from the model's memory, `card` writes the needed facts on a short card after the input text, `context` buries the needed cards among fillers — 20 cards in a seeded order, with no filler that could make a second right answer — and `text` is the recognize level, where names sit inside running text. The JSON files hold the question sets the arguments name.

The eight card-answerable functions each hold 300 distinct questions, asked the same way at every level: memory and context run all 300, card runs 100 of them. `decide` and `choose` take their memory and most of their context asks from the 1,501 main questions in this folder; a `source` key on a card or context case names the question it reuses, and `songs` names the cards the truth needs.

| function | memory | card | context | text | total |
|---|---|---|---|---|---|
| decide | 132 + 168 mains | 100 | 300 | — | 532 |
| choose | 300 mains | 100 | 300 | — | 400 |
| tag | 300 | 100 | 300 | — | 700 |
| score | 300 | 100 | 300 | — | 700 |
| filter | 300 | 100 | 300 | — | 700 |
| rank | 353 | 200 | 353 | — | 906 |
| find | 300 | 100 | 300 | — | 700 |
| annotate | 300 | 100 | 300 | — | 700 |
| recognize | — | — | — | 400 | 400 |
| relate | 100 | — | — | — | 100 |

`decide` holds its 168 card-answerable main questions plus 132 album asks; `rank` keeps all 353 of its asks at memory and context, because the committed 2026-09-26 run scores each ask as one full ordered list, and samples 100 per ask kind for its two card tests, hence 200 card cases. Controls: decide runs half yes, half no; filter keeps its kept/dropped mix; 30 of choose's 300 questions are `none of these`; 21 of tag's 142 trait asks have an empty truth; 45 of find's 300 sets hold no right unit and run with `--none`.

A `reading` test is a card case: it reuses a memory case's question and truth but writes the facts into the record — the input text, then one short card per song it names: the song's title, lead singers, first album, year, and length, plus the writers, release date, cover flag, or 2024 page views where the truth needs them. A find set's records carry one card each. A case's `needs` lists the `songs.tsv` columns its truth needs. Cases whose truth needs another table (world events, pairs outside the Beatles, album dates) are not eligible.

A recognize case holds one sentence and its names as character offsets; the cases sit in tests, one per group, and a `relations` case adds `edges`, the stated [relation, source, target] triples. A relate case holds one entity set and its true edges; `relate-suite.json` holds the singer and album relations and `relate-links.json` the composer and producer ones from `data/links.tsv`.

`catalog/catalog.jsonl` lists every question the bench asks — the 1,501 mains and every suite case — as `{id, file, function, test, level, category, truth}`, one JSON object a line. It sits in a subfolder so the `questions/*.jsonl` globs in scripts and tests do not pick it up.
