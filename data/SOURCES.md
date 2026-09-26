# Sources, rules, and license

`scripts/harvest/harvest.py` writes every file in this folder. No person and no model chose a row.

## License

- The code in this repository is MIT licensed (`LICENSE`).
- The tables in `data/` and `data/pins/` are compiled from English Wikipedia and Wikidata. Wikipedia text is licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Wikidata is [CC0](https://creativecommons.org/publicdomain/zero/1.0/). Plain facts such as a title, a date, a singer, or a track length are not copyrightable. Some countries protect a database as a whole, so the tables in `data/` are offered under CC BY-SA 4.0 with this attribution:

  > Song, album, and event facts compiled from English Wikipedia (List of songs recorded by the Beatles, the Beatles' album and single articles, and the year articles 1962 to 1970) at the revisions listed in `data/pins/pages.tsv`, CC BY-SA 4.0. Page view counts from the Wikimedia Pageviews API. Song relations from Wikidata, CC0. Photo credits from Wikimedia Commons; each photo keeps its own license.

- No Wikipedia sentence is stored here. The page cache (`data/raw/`) is never committed. No lyrics appear anywhere.

## Pages

Every page is read at a pinned revision: `https://en.wikipedia.org/w/index.php?oldid=REVID`. `data/pins/pages.tsv` lists the title and revision of each page. The list and album revisions are those of 2026-09-23. `data/pins/redirects.tsv` pins where each link landed on 2026-09-23.

## How each table is filled

- `songs.tsv`: one row per song in the list's two released-song tables ("Main songs", the 1962 to 1970 core, and "Other released songs"). Film-only and unreleased songs are out.
  - `songwriters` is the published credit, so most originals read "Lennon–McCartney". `lead_vocals` joins the lead singers with `+`. `with_vocals` holds the singers the list marks "with" beside the lead (A Day in the Life: Lennon, with McCartney), and the singers the list marks with a footnote (Cry Baby Cry: McCartney sings only its coda).
  - `article_lead` joins the Beatles the Personnel section of the song's own article names on lead vocal. A role counts as lead when it names a vocal part with no backing, harmony, falsetto, additional, spoken, shouted, chorus, or ad-lib qualifier, or when it says "lead vocal" outside a backing or harmony phrase. It is empty when the song has no own article or its article has no Personnel section. The lead questions ask a song only when `lead_vocals` and `article_lead` name the same Beatles. A shared lead needs the article to confirm it, and a solo lead also passes when `article_lead` is empty.
  - `article` is the article the list links. It is the song's own article only when its title, less a trailing parenthesis, equals the song title exactly. "Can You Take Me Back?" links Cry Baby Cry's article, and "Can You Dig It?" links Dig It's, so neither takes a fact from it. Every fact read from a song's article (`views_2024`, a song-page `release_date`, and the rows of `links.tsv`) is read only from the song's own article.
  - `views_2024` is the own article's user page views over 2024, and is empty without an own article.
  - `first_release` is the first release the list names. A UK non-album single reads "single". `first_album` is the first album or release the list names.
  - `length_s` comes from the first track listing on the release's album page that holds the title, else Past Masters.
  - `release_date` is the first release date anywhere in the world. For a song first released on an album it is the album's date, unless the song's own article gives an earlier date: then that date wins (Can't Buy Me Love came out as a single on 16 March 1964, before A Hard Day's Night). For a non-album single it is the own article's date. A song's own date is the earliest full date, in any country, in the "released" field of the first song or single infobox whose artist is the Beatles, so a page that opens with another artist's recording is read at the Beatles' infobox. Covers take the album's date, because a cover's article dates the original. A date is left empty when its year differs from the list's year. `date_from` names the article the date came from.
- `albums.tsv`: the albums the harvest reads, with the earliest full date in each infobox "released" field.
- `events.tsv` holds the most significant event of each month from 1962 to 1970. The multi-hop questions use the months near a song's release. "Most significant" means most viewed on Wikipedia, by this rule:
  1. Take the dated event lines of each month from the Events section of the year article ("1962" to "1970"). Lines that link The Beatles are skipped.
  2. Follow each link through redirects. A linked article counts as an event when all three hold:
     - Its Wikidata item is an instance (P31) of occurrence (Q1190554) or of any subclass of it (P279*).
     - Wikidata dates it to the line's month by point in time (P585), start time (P580), or launch date (P619), at month precision or finer. P619 lets a spaceflight such as Apollo 11 count.
     - Neither its title nor its English Wikidata description matches the regular expression `\b(country|sovereign state|organi[sz]ation|company|political party|person|treaty|currency|law)\b`, ignoring case.
     - It is discrete: Wikidata dates it to one day of the month. It has a point in time (P585) or launch date (P619) at day precision in that month, or a start time (P580) at day precision with an end time (P582) in the same month, and every start and end time it has falls in that month. A war, a movement, or a currency starts in one month and ends in another or never, so none counts. `data/pins/wikidata-event-dates.tsv` pins every P585, P580, P582, and P619 value with its precision, read from the Wikidata API on 2026-09-23.
  3. A line's event is its first link that counts. The event with the most user page views over 2024-01-01 to 2024-12-31 wins its month (Wikimedia Pageviews API, all access, monthly, summed). A tie goes to the earlier date, then the article title in code-point order.
  - `data/pins/wikidata-events.tsv` pins each linked article's occurrence flag, description, and months. `event` is the article title. `event-candidates.tsv` lists every candidate with its view count. A test checks that Apollo 11 wins July 1969.
  - `commons_file` names the event's Wikidata image (P18) when its license is free by the rule below, and is empty otherwise.
- `event-photos.tsv` lists free-license photos for every release month from 1962 to 1970. A release month is the month of any `release_date` in `songs.tsv` or `albums.tsv`.
  - Every event any line of that month links (step 2 above) with a free image appears once, at its first date, ranked by 2024 page views. A release month with no free photo keeps its picked event with the photo columns empty.
  - The image is the item's Wikidata image (P18), pinned in `data/pins/wikidata-images.tsv`. An item with several images gives the first by file name. The license, author, page link, and original date come from the Commons API's `extmetadata`, pinned in `data/pins/commons.tsv`.
  - Free means the Commons license code starts with `pd`, `cc0`, `cc-by-` followed by a version, or `cc-by-sa-` followed by a version: public domain, CC0, CC BY, and CC BY-SA.
  - Rows marked `extra` lie outside the release months and never enter a question. The one extra row is the National Archives photo of Elvis Presley meeting Richard Nixon (`Elvis-nixon.jpg`, named in `scripts/harvest/harvest.py`). Its date comes from Commons.
  - The release months end at May 1970 (Let It Be). Later release dates in the data belong to archive releases from 1988 on. A test checks both.
- `links.tsv` holds song relations from Wikidata for the reversal category. `scripts/harvest/wikidata.rq` is the query. It ran on the date in `data/pins/wikidata-date.txt`, and `data/pins/wikidata.tsv` pins the answer. A pair is kept when the Wikidata song article is the own article of a song in `songs.tsv`, the other end has an English Wikipedia article, and one end had at least 10 times the other's 2024 page views. `famous` names the side with more views.
  - A composer (P86) must agree with the published credit, which `credit` repeats. Wikidata names Lennon or McCartney alone for most songs credited "Lennon–McCartney". For those songs the composer becomes the pair, read from the article "Lennon–McCartney". Any other composer is kept only when a last name in the credit matches the composer's last name (Starr matches the credit's Starkey).
- `reversal-general.tsv` holds pairs outside the Beatles, all from Wikidata:
  - Actors and their parents: `scripts/harvest/parents.rq` (actors with more than 60 sitelinks and a father, P22, or mother, P25), run on the date in `data/pins/parents-date.txt`, with each end's English Wikipedia title (`data/pins/parents.tsv`). A pair is kept when the actor had at least 10 times the parent's 2024 page views.
  - 40 pairs from four relations (film and composer, building and architect, invention and inventor, song and writer), a seeded sample of the queries in `scripts/harvest/reversal/` run on 2026-09-23 (`data/pins/reversal-wikidata.tsv`, with the true links among them in `reversal-links.tsv`). A pair is kept when the famous end had at least 10 times the other end's 2024 page views. 36 of the 40 pass.
  - `not_forward` and `not_reverse` list other true answers, which never appear as wrong options.
- `data/pins/pageviews.tsv` pins every view count the harvest read.
- `data/pins/excluded.tsv` drops three items a source check found ambiguous: an event whose article covers two fights in different months, and two reversal pairs where Wikidata and the Wikipedia article name different people. Each row gives its reason and the date of the check. An audit of wrong answers found them, and each reason was checked against the article. No row adds or changes an answer.
