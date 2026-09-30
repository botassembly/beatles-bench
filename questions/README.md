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

`suite/` holds the tests for all ten functions. `decide.jsonl` and `choose.jsonl` hold only reading cases, sampled from the memory questions in this folder. Each JSONL line carries the command's arguments and its records. The JSON files hold the question sets the arguments name. A recognize case holds one sentence and its names as character offsets; the cases sit in tests, one per group, and a `relations` case adds `edges`, the stated [relation, source, target] triples. A relate case holds one entity set and its true edges; `relate-suite.json` holds the singer and album relations and `relate-links.json` the composer and producer ones from `data/links.tsv`.

A `reading` test case reuses a memory case's question and truth but writes the facts into the record: the input text, then one short card per song it names — the song's title, lead singers, first album, year, and length, plus the writers, release date, or 2024 page views where the truth needs them. A find set's records carry one card each. A case's `needs` lists the `songs.tsv` columns its truth needs, and `source` names the memory question a decide or choose case reuses. Cases whose truth needs another table (world events, pairs outside the Beatles, album dates) are not eligible.
