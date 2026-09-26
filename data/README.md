# Data

Every table here comes from `scripts/harvest/harvest.py`. No person and no model chose a row. The harvest reads English Wikipedia at pinned revisions, the Wikimedia Pageviews API for 2024, Wikidata, and Wikimedia Commons. An offline rebuild from the pins gives the same bytes, and a test checks it.

Every right answer in the bench comes from one table, `songs.tsv`, one row per song. Run every command on this page from the top folder of the bench.

## Files

| File | What it holds |
| --- | --- |
| `songs.tsv` | 306 released Beatles songs: lead singers, songwriting credit, first album, first release date, length, and 2024 page views. |
| `albums.tsv` | 20 albums with their release dates. |
| `events.tsv` | 100 months from 1962 to 1970, each with its most viewed dated world event. |
| `event-candidates.tsv` | Every candidate event behind `events.tsv`, with its page views. |
| `event-photos.tsv` | Free-license Commons photos for the release months: file name, license, author, and page link. |
| `links.tsv` | 142 Beatles pairs from Wikidata for the reversal questions: mostly song and composer or song and producer. |
| `reversal-general.tsv` | 254 pairs outside the Beatles from Wikidata: actors and parents, films and composers, buildings and architects, inventions and inventors, songs and writers. |
| `pins/` | Every harvested input: page revisions, redirects, page views, Wikidata answers, Commons metadata, and the three excluded items. |
| `raw/` | The local page cache the harvest fills. It is never committed. |

## One row

Here is the row for Octopus's Garden, one column per line:

```sh
awk -F '\t' 'NR == 1 { split($0, head) } $1 == "Octopus\047s Garden" { for (i = 1; i <= NF; i++) print head[i] "=" $i }' data/songs.tsv
```

```text
title=Octopus's Garden
article=Octopus's Garden
year=1969
first_release=Abbey Road
first_album=Abbey Road
songwriters=Starkey
lead_vocals=Starr
with_vocals=
article_lead=Starr
length_s=171
release_date=1969-09-26
date_from=Abbey Road
cover=no
views_2024=103246
catalogue=core 1962-1970
```

The columns the questions and the examples use most:

- `first_album` is the first album or release the list of songs names. A song first out on a single can name Past Masters, the album that collected the singles.
- `lead_vocals` names the lead singers from the list of songs. `article_lead` names them from the song's own article.
- `songwriters` gives the credit. Ringo Starr's credit reads Starkey, his birth name.
- `length_s` is the length in seconds.
- `year` and `release_date` give the first release.
- `views_2024` counts the song article's page views in 2024.

## From a row to a question

A script writes each question from a template, and the row fills its slots. Here is one question about Octopus's Garden:

```sh
jq -c 'select(.id == "forward-year-030") | {id, function, question, input, options: (.options | keys), truth, fields}' questions/forward.jsonl
```

```json
{"id":"forward-year-030","function":"choose","question":"The text is the title of a song by the Beatles. In what year was it first released?","input":"Octopus's Garden","options":["1962","1963","1964","1965","1966","1967","1968","1969","1970"],"truth":"1969","fields":[["songs.tsv","Octopus's Garden","year","1969"]]}
```

- `function` names the ThinkThen command that answers it.
- `question` is the text Jev reads. `input` is the text the question is about.
- `options` are the choices.
- `truth` is the right answer. `fields` names the file, row, column, and value it came from.

[questions/README.md](../questions/README.md) lists the 15 categories and how each truth is set.

## How Jev answered it

The fresh run of 2026-09-26 recorded Jev's answer to every question. This command asks the question again from that recording, with no key:

```sh
jq -c 'select(.id == "forward-year-030")' questions/forward.jsonl |
  thinkthen choose 'The text is the title of a song by the Beatles. In what year was it first released?' \
    --jsonl --field /input --options /options --details --replay results/runs/2026-09-26-thinkthen-jev/recording |
  jq -c '{song: .input.input, pick: .value, p: .answer.probabilities}'
```

```json
{"song":"Octopus's Garden","pick":"1967","p":{"1962":0.0,"1963":0.0,"1964":0.0,"1965":0.01,"1966":0.18,"1967":0.47,"1968":0.25,"1969":0.09,"1970":0.0}}
```

- `--jsonl` takes the question line as one record.
- `--field /input` sends only the song title. The rest of the record stays on the machine.
- `--options /options` reads the options from the record.

Jev picks 1967 at 0.47, and it is wrong. The right year, 1969, gets 0.09. Jev gets the singer of Octopus's Garden right in [the choose example](../functions/choose/). It misses the year here and the album in [the annotate example](../functions/annotate/).

## The catalog

The context runs send a catalog entry built from the same row. `scripts/run/catalog.py` writes every song as one line under its first album:

```sh
grep -F "Octopus's Garden (" results/runs/2026-09-26-thinkthen-jev-open-book/catalog.txt
```

```text
Octopus's Garden (lead: Starr; written: Starkey; 2:51; released 1969-09-26)
```

The line carries `lead_vocals`, `songwriters`, `length_s` as minutes and seconds, and `release_date`. The album header above it, "Abbey Road (1969-09-26)", gives `first_album`. The examples in `functions/` send one song's header and line, and they add "first album:" to the line. [Context and cost](../reports/open-book.md#context-and-cost) in the open-book report shows one.

## Where it comes from

- Wikipedia: "List of songs recorded by the Beatles", the album and single articles, each song's own article, and the year articles 1962 to 1970. `pins/pages.tsv` names every revision, all as of 2026-09-23.
- Wikidata: song relations, event dates, and the pairs outside the Beatles, queried on 2026-09-23.
- Wikimedia Pageviews API: user page views over 2024. They decide an event of a month and the fame of each end of a pair.
- Wikimedia Commons: photo licenses and authors.

[SOURCES.md](SOURCES.md) states every rule the harvest applies, table by table. [datasheet.md](datasheet.md) answers the standard datasheet questions: purpose, composition, collection, uses, and maintenance.

## Licenses

- The tables, the pins, the questions, and the results are offered under CC BY-SA 4.0, because they are compiled from Wikipedia. [LICENSE](LICENSE) holds the attribution.
- Wikidata facts are CC0.
- Each Commons photo keeps its own license. Only public domain, CC0, CC BY, and CC BY-SA files are listed, and no image is stored.
- No Wikipedia sentence and no lyric is committed.
- The code is MIT ([../LICENSE](../LICENSE)).

## Known limits

- The truth is Wikipedia's at the pinned revisions and Wikidata's on 2026-09-23. A release date is the earliest date in the infobox, sometimes the US date. The US dates below decide a question. Each named answer would change under the UK date.

| Item | Catalog date (US) | UK date | Questions the US date decides |
| --- | --- | --- | --- |
| Magical Mystery Tour: the album, and the songs Magical Mystery Tour, Blue Jay Way, Flying, The Fool on the Hill, and Your Mother Should Know | 1967-11-27, the US LP | 1967-12-08, the UK EP | `single-hop-song-month-028`, `-036`, and `-056`; `multi-hop-same-month-001` |
| I'm Only Sleeping, And Your Bird Can Sing, and Doctor Robert | 1966-06-20, the US album Yesterday and Today | 1966-08-05, Revolver | `single-hop-song-month-022`; `multi-hop-same-month-019`; the function suite's `rank-date-108`, `-132`, and `-159` |
| Tell Me What You See and You Like Me Too Much | 1965-06-14, the US album Beatles VI | 1965-08-06, Help! | `single-hop-song-month-074`; `multi-hop-same-month-025`; the function suite's `rank-date-104` and `-172` |

- Two more cases use a US date. No answer changes under the UK date. The Yellow Submarine album and its four new songs take 1969-01-13, and the UK date is 1969-01-17. The article's prose gives both, and the infobox gives only the US date. Can't Buy Me Love and You Can't Do That take the US single's 1964-03-16, and the UK date is 1964-03-20. Both stay in the same month and year.
- Magical Mystery Tour counts as an album from its US LP. It is then the first album of five 1967 singles: Penny Lane, Strawberry Fields Forever, All You Need Is Love, Baby, You're a Rich Man, and Hello, Goodbye. That sets their first-album truth in the function suite's find, filter, annotate, and relate tests, and in the audit and filter examples.
- The scan reads each album's and each song's source page at its revision in `pins/pages.tsv`: the infobox "released" field and the prose. A US date decides a question when the question's truth would change under the UK date. The scan checks every question that reads a date: the song month, the same month as an event, before or after an event, the album year, and the function suite's rank by date and annotate year. A one-date infobox that names no country is taken as it stands.
- The event of a month is the most viewed discrete event on Wikipedia in 2024 among those the year article links. Views measure attention today. A month with no qualifying event has none.
- Wikidata holds few Beatles relations. The Beatles reversal pairs are mostly composer and producer, and the famous end is always the person or place.
- The lead questions skip songs whose own article has no Personnel section and disagrees with the list, or names no lead.
- A model trained after this repository is public may have seen the facts and the questions.
- Hey Jude's length follows the track-listing rule in `SOURCES.md`: Past Masters gives 7:08 (428 seconds). The song's own page gives 7:12.

## Rebuild

```sh
python3 scripts/harvest/harvest.py --offline    # rebuilds data/ from data/raw/ and data/pins/
```

Without `--offline` the harvest fetches any page or answer that is not yet pinned and pins it.
