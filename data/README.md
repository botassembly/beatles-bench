# Data

Every table here comes from `scripts/harvest/harvest.py`. No person and no model chose a row. The harvest reads English Wikipedia at pinned revisions, the Wikimedia Pageviews API for 2024, Wikidata, and Wikimedia Commons. An offline rebuild from the pins gives the same bytes, and a test checks it.

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
