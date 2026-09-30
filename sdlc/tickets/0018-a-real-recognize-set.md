# 0018 Give recognize a real test set, with text relations

Owner: the queue owner. Status: ready for review.

## Why

The recognize suite has 48 sentences, and every one uses the same template: "PERSON sang lead on SONG from the album ALBUM in YEAR." Jev scores 96 to 100 percent on it. That tells a reader little. The hard cases never appear: a title that is both a song and an album, a first name alone, lower case, a sentence with no names, a longer paragraph. The text relations `recognize --relation` finds are not measured at all.

## Prior evidence

- `reports/results.md`, "The function suite": recognize precision and recall from 0.959 to 1.000 over 144 names. Jev missed two: it split "Back in the U.S.S.R." and did not name the album "Help!".
- `scripts/generate/make_suite.py` builds the 48 sentences from one template.
- ThinkThen `specification/recognize.md`: names, kinds, tokenization, pieces for long text, and beta relations through `--relation`.
- `data/songs.tsv` and `data/albums.tsv` hold every fact the sentences need. Seven titles are both a song and an album: A Hard Day's Night, Help!, Let It Be, Magical Mystery Tour, Please Please Me, Sgt. Pepper's Lonely Hearts Club Band, and Yellow Submarine. The generator takes the list from the tables.

## Retained behavior

- The 48 existing cases, their recording, and their published scores stay as a separate test named `names-template`.
- Every truth comes from the tables by script. No person or model sets an answer.
- No Wikipedia sentence is committed. Sentences come from templates filled from the tables.

## Changes

1. `make_suite.py` adds about 150 recognize cases in named groups, each with a fixed seed:
   - `varied`: ten or more sentence templates, with names in different positions.
   - `song-or-album`: a title that is both, used once as a song and once as an album, with the kind clear from the sentence.
   - `short-names`: first names or surnames alone, such as "Paul" or "Lennon", where the kind is still person.
   - `case`: lower-case and all-caps names.
   - `no-names`: sentences with no song, person or album.
   - `paragraphs`: three to six sentences, long enough to cross ThinkThen's pieces.
   - `punctuation`: titles with marks inside, such as "Back in the U.S.S.R." and "Ob-La-Di, Ob-La-Da".
2. A `relations` group of about 40 sentences runs `recognize --relation sung_by=person:song --relation appears_on=song:album`. The sentence states each edge, and some sentences state a fact about one entity and none about another. Truth holds the stated edges only.
3. `score_suite.py` scores names by group and kind, and relations by precision and recall. It writes rows into `results/tables/functions*.tsv` with the group in the test name.
4. `reports/results.md` gains the new rows, with a line saying what each group tests.

## Proof

- `tests/test_suite.py` checks every new case: truth offsets slice the sentence to the name, every group has its planned count, and a rebuild gives the same bytes.
- A live run through the current ThinkThen main records every exchange. A replay with no key gives the same answers.
- Token cap: 2,000,000 input tokens for this ticket, about $0.08. The plan's upper bound is checked before the run.

## Deferred gaps

- Kinds beyond song, person and album.
- GLM and Laya runs of the new groups.
