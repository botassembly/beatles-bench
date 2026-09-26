# Jev picks its own catalog sections

Written 2026-09-23. Model: Jev 1.13.0 from TypeSafe, called through the `thinkthen` command. Idea: retrieval-augmented decisions (RAD).

## Setup

The open-book catalog splits into 28 sections: one per album, as `scripts/run/catalog.py` groups it, plus "Singles". Each question takes two steps. First a pick ranks the sections. Then one answer call sends the top k sections as the catalog, in catalog order, with the question's own wording and options. In the Jev arm, the pick is one `choose` call. Its text is the question's wording and input, and its options are the 28 section headers. It asks "Which section of the Beatles catalog holds the facts needed to answer the question in the text?" The BM25 arm ranks the sections by BM25 against the same text. The MiniLM arm ranks them by cosine with `sentence-transformers/all-MiniLM-L6-v2`, run at nice 19 on one thread (20 s, 1 GB). The questions are the 196 from the open-book run. `scripts/run/rad.py` builds the picks and answer questions, and `scripts/score/rad_table.py table results/runs/2026-09-23-thinkthen-jev-rad --closed results/runs/2026-09-23-thinkthen-jev --open results/runs/2026-09-23-thinkthen-jev-open-book` prints the table below. A pick holds a question when its sections hold every catalog line the truth rests on, read from the question's `fields`. A tie at the top counts as wrong.

## Results

| Context | Right | Pick recall | Median input tokens | Median time | Dollars per 1,000 |
| --- | --- | --- | --- | --- | --- |
| Full catalog (open-book run) | 187 of 196 (95%) | 100% | 12,214 | 0.54 s | 0.513 |
| Jev picks, k = 1 | 150 of 196 (77%) | 56% | 2,048 | 0.66 s | 0.093 |
| Jev picks, k = 2 | 167 of 196 (85%) | 72% | 2,656 | 0.71 s | 0.122 |
| Jev picks, k = 3 | not asked | 80% | | | |
| BM25 picks, k = 2 | 163 of 196 (83%) | 61% | 1,942 | 0.35 s | 0.077 |
| MiniLM picks, k = 2 | 125 of 196 (64%) | 28% | 1,715 | 0.33 s | 0.068 |
| Jev picks, k = 2, full catalog below 0.5 | 182 of 196 (93%) | 90% | 3,232 | 0.72 s | 0.215 |
| Closed book | 62 of 196 (32%) | none | 362 | 0.28 s | 0.015 |

- Tokens and time for a Jev arm add the pick call to the answer call. A vector pick calls no model, so its row counts the answer call alone.
- The pick call costs about 1,130 input tokens. That is 43% of the k = 2 cost. The 28 headers take most of it.
- Jev picks beat BM25 on recall (72% against 61%). They do not beat it on right answers: 21 questions only Jev's arm got right and 17 only BM25's got right (exact McNemar p = 0.63). Jev's arm still answered 29 of its 54 wrong picks right. BM25 does well here because every section spells out its song titles, and most questions name a song.
- MiniLM reads only the first 256 word pieces of a section. Most sections run longer, so most titles never reach it.
- The fallback row sends the full catalog when Jev's top two sections hold less than half its pick probability. That happened on 42 questions. Wrong picks carry a median top-two share of 0.42 and right picks 0.84. The cut was chosen on these same questions, so the row overstates what a fresh set would show. It calls nothing new: it reuses the open-book answers.
- k = 3 was not asked. Its new answers needed about 440,000 tokens, past the cap.

## Five misses from Jev picks, k = 2

Jev's arm missed 29 questions. By the recall rule, 25 are wrong picks and 4 are misreads. Six of the wrong picks are reverse or reversal questions. Their answer song appears only in the options, and the pick never sees the options.

| Question | Truth | Read | Answer | Cause |
| --- | --- | --- | --- | --- |
| Who sings the lead on "Soldier of Love"? | John Lennon | My Bonnie, Singles | Ringo Starr (0.36) | Wrong pick. The song sits under Live at the BBC. Jev spread the pick thin (top 0.16), and the fallback would catch it. |
| In what year was "Good Day Sunshine" first released? | 1966 | White Album, Sgt. Pepper | 1968 (0.50) | Wrong pick. The song sits under Revolver. Jev placed it confidently (0.44 and 0.43), and the answer followed the wrong sections. |
| In which month was "Yellow Submarine" first released? | August 1966 | Yellow Submarine, Singles | January 1967 (0.79) | Wrong pick. The title trap moved into the pick. Jev chose the album of the same name (0.53). The song sits under Revolver. |
| Which song is credited to Paul McCartney? | Dig It | Please Please Me, Singles | For You Blue (0.40) | Wrong pick. The pick saw only the name. Dig It sits under Let It Be, and only the options name it. |
| Does Paul McCartney sing a lead on "She Loves You"? | yes | Singles, With the Beatles | no (0.64) | Misread. The Singles line says "lead: Lennon, McCartney". The full catalog missed it the same way. |

## Load and cost

Four live jobs ran from 21:24 to 21:27 UTC. The one-minute load average stayed between 2.5 and 5 on 16 cores (`loadavg.txt`). The open-book run ran near 400, so its times are not comparable with these. The jobs sent 932 requests: 1,387,973 input tokens and 98,234 output tokens, or 0.058 dollars. The guard reserved 1,495,000 tokens. A replay with no key gives the same 980 answers byte for byte. The run lives in `results/runs/2026-09-23-thinkthen-jev-rad/`.

## Next

- Put the options into the pick text. Reverse and reversal questions need them.
- Keep the fallback, and tune its cut on one half of a fresh sample.
- Shorten the pick call. Short labels or one call per batch of questions would cut its 1,130 tokens.

## Second test

Written 2026-09-23. The second test changes two things. The pick text now ends with the answer options: "Options: a; b; c". A yes-or-no question has no options, so its pick text stays the same. The fallback cut is now tuned on one half of the questions and reported on the other.

`scripts/run/rad.py split` splits the 196 questions by topic with the fixed seed "rad2". Each topic splits within one question, and each half holds 98. The tune half picks each cut. The rule takes the lowest cut from 0, 0.05, ..., 1 whose right count comes within two of the full catalog's on the tune half. The full catalog got 93 of the tune half right. The rule chose 0.30 for the new pick and 0.40 for the first test's pick. All rows below cover the held-out half only. The old-pick rows reuse the first test's answers. `scripts/score/rad_table.py second results/runs/2026-09-23-thinkthen-jev-rad2 --closed results/runs/2026-09-23-thinkthen-jev --open results/runs/2026-09-23-thinkthen-jev-open-book --first results/runs/2026-09-23-thinkthen-jev-rad` prints the table and the tests.

| Context | Right | Pick recall | Median input tokens | Median time | Dollars per 1,000 |
| --- | --- | --- | --- | --- | --- |
| Full catalog | 94 of 98 (96%) | 100% | 12,213 | 0.60 s | 0.513 |
| New Jev pick (with options), k = 2 | 85 of 98 (87%) | 73% | 2,617 | 0.78 s | 0.119 |
| New Jev pick, full catalog below 0.30 | 85 of 98 (87%) | 76% | 2,620 | 0.78 s | 0.133 |
| Old Jev pick (no options), k = 2 | 83 of 98 (85%) | 71% | 2,623 | 0.71 s | 0.122 |
| Old Jev pick, full catalog below 0.40 | 89 of 98 (91%) | 82% | 2,822 | 0.72 s | 0.167 |
| BM25 with options, k = 2 | 82 of 98 (84%) | 58% | 1,910 | 0.38 s | 0.077 |
| Old BM25 (no options), k = 2 | 81 of 98 (83%) | 59% | 1,942 | 0.35 s | 0.076 |
| Closed book | 31 of 98 (32%) | none | 361 | 0.28 s | 0.015 |

Exact McNemar tests on the held-out half, for the new pick with its fallback:

- Against the full catalog: 1 question only the new pick got right, 10 only the full catalog got right, p = 0.012. The full catalog is better.
- Against BM25 with options: 12 against 9, p = 0.66. No difference shows.
- Against the old pick with its fallback: 3 against 7, p = 0.34. No difference shows.

- The options lifted pick recall a little. Over all 196 questions, the new pick held the needed sections on 148 and the old pick on 142. Reversal questions went from 1 of 6 to 3 of 6, and reverse questions from 9 of 18 to 10. Forward questions fell from 25 of 36 to 22.
- The options made the pick surer. Its top two sections held more of its probability, so the 0.30 cut sent only 3 held-out questions to the full catalog. The old pick's 0.40 cut sent 10. That gap explains most of the difference between the two fallback rows.
- The cut is noisy at this size. On the tune half, cuts from 0.35 to 0.65 all scored 92, one more than 0.30. On the held-out half the new pick with a 0.50 cut would have scored 90, and with 0.55 it would have scored 92. Those held-out figures only describe the curve. They chose nothing.
- BM25 gained one right answer from the options. Its pick recall fell by one question. Option words match other sections as often as the right one.
- The fallback row costs 26% of the full catalog. The old pick's fallback costs 33%.

### Five misses from the new pick with its fallback

The new pick with its fallback missed 13 held-out questions: 10 wrong picks and 3 misreads.

| Question | Truth | Read | Answer | Cause |
| --- | --- | --- | --- | --- |
| Which was the first album to include "Please Mr. Postman"? | With the Beatles | Beatles for Sale, Please Please Me | Beatles for Sale (0.56) | Wrong pick. The options named Beatles for Sale first, and the pick moved to it (0.48). The old pick held With the Beatles in its top two. |
| In what year was "Yesterday" first released? | 1965 | Rubber Soul, Singles | 1966 (0.52) | Wrong pick. The song sits under Help!, the pick's third choice (0.17). |
| In which month was "Yellow Submarine" first released? | August 1966 | Yellow Submarine, Singles | January 1967 (0.79) | Wrong pick. The title trap stayed in the pick (0.42). The options list only months, so they gave no hint. |
| Does John Lennon sing a lead on "Little Child"? | yes | With the Beatles, Please Please Me | no (0.51) | Misread. The right section says "lead: Lennon, McCartney". This is the shared-lead slip from "She Loves You". |
| Which of these songs is credited to Ringo Starr? | Flying | full catalog | Misery (0.51) | Misread. The pick fell back. The Flying line credits "Starkey", Ringo's legal name, and the answer did not link the two. |

### Load and cost

Two live jobs ran from 22:09 to 22:11 UTC. The one-minute load average stayed between 6 and 8.4 on 16 cores (`loadavg.txt`). The run folder started from a copy of the first test's recording, so 199 identical requests cost nothing. The jobs sent 290 new requests: 411,549 input tokens and 64,960 output tokens, or 0.017 dollars. The guard reserved 510,000 tokens. A replay with no key gives the same 490 answers byte for byte. The run lives in `results/runs/2026-09-23-thinkthen-jev-rad2/`.

### Verdict

Options in the pick helped a little and not significantly. A held-out fallback keeps most of the full catalog's accuracy at a quarter of its cost. It still trails the full catalog (p = 0.012) and does not beat BM25 with options.

### Next

- Tune the cut on the fallback share as well as on right answers. The options changed how sure the pick is, and a fixed probability cut does not carry across pick texts.
- Test a pick that returns the song's section by name lookup before any model call. Most misses are songs Jev placed under the wrong album.

## With shipped commands

Written 2026-09-24. Model: Jev 1.13.0, called through `thinkthen` 0.0.1 (a local build). `scripts/run/rad_pipeline.sh` runs the whole pipeline with `thinkthen` and `jq` alone. No request is built in Python. A live run calls the backend only for exchanges its recording lacks (`--cache`), and a replay answers from the recording with `--replay`, no key, and no network:

```sh
THINKTHEN_BIN=path/to/thinkthen scripts/run/rad_pipeline.sh replay results/runs/2026-09-24-pipeline-jev2
```

The core of each step, as the script runs it:

```sh
# 1. Pick two sections, glue them before the question, answer.
jq -Rsc "$SECTIONS"' | {id: "pick", input: ("Question: " + $q), options: (map({(.label): .header}) | add)}' < catalog.txt \
  | thinkthen choose "$PICK" --jsonl --field /input --options /options --details
jq '.answer.probabilities | to_entries | sort_by(-.value) | .[:2] | map(.key)'    # the top two, then glued as "Catalog:\n...\n\nQuestion: ..."
# 2. One context over 18 records, three ways.
thinkthen tag "$LEAD" --label Lennon=... --jsonl --details --field /song                   # memory
thinkthen tag "$LEAD" --label Lennon=... --jsonl --details --field /text                   # glued: "Catalog:\n<section>\n\nText: <song>"
thinkthen tag "$LEAD" --label Lennon=... --jsonl --details --field /context --field /song  # apart
# 3. Check each apart answer.
thinkthen annotate scripts/run/rad_pipeline.checks.json --jsonl --details --input grounding.jsonl
```

| Arm | Right | Input tokens | Time |
| --- | --- | --- | --- |
| One question: Jev pick | Abbey Road not in the top two | 1,115 | 0.34 s |
| One question: answer from the two picked sections | 1 of 1 (Starr, 0.90) | 2,181 | 0.32 s |
| Abbey Road songs, memory | 4 of 18 | 8,439 | 1.19 s |
| Abbey Road songs, glued | 18 of 18 | 20,317 | 1.12 s |
| Abbey Road songs, apart | 18 of 18 | 20,463 | 1.39 s |
| `annotate` correctness and grounding over the apart answers | 18 of 18 checks agree with the truth | 22,952 | 2.11 s |

- `scores.tsv`, `checks.tsv`, and `times.tsv` in `results/runs/2026-09-24-pipeline-jev/` hold these numbers. That run came from the script before ticket 0004. The current script replays `results/runs/2026-09-24-pipeline-jev2/`, which holds the same answers for these arms. A time covers the whole call for all of an arm's records, with four requests in flight.
- The pick gave the White Album 0.44 and Revolver 0.33. Abbey Road got 0.04. The answer still named Starr at 0.90, from memory. The "Jev picks, k = 2" row above shows the same pattern: Jev answered 29 of its 54 wrong picks right. This pair cost 3,296 input tokens against that row's median of 2,656.
- The Abbey Road section spells out "lead:" for every song. The two context arms are a lookup, so 18 of 18 shows that the context reached the model. It says nothing about harder questions.
- From memory, Jev added a second or third singer on 13 songs. On Polythene Pam it named McCartney alone.
- Every apart answer was right, so the grounding check saw no unsupported claim. It answered yes on all 18. This run does not show that it catches a bad answer.
- The one-minute load stood at 14.5 on 16 cores during the run, from other work on the machine. The times run high for that reason.
- The job sent 92 requests: 75,467 input and 5,054 output tokens, or 0.0032 dollars. The guard reserved 200,000 tokens. The replay test in `tests/test_rad_pipeline.py` gives the same `scores.tsv` and `checks.tsv` with no key.

The three open questions:

- Gluing reads cleanly. One `jq` expression builds the glued text for every record, and the apart records need the same expression with one field fewer.
- Apart does not score differently from glued here: 18 of 18 each, at 20,463 and 20,317 input tokens. The lookup ceiling leaves no room for a difference to show.
- The grounding check needs the context under its own pointer in the record, and `jq` puts it there. `annotate`'s `on: ["/context", "/output"]` read it with no new command input.

## A question Jev does not know

Written 2026-09-24, ticket 0004. Octopus's Garden proved nothing: the pick missed Abbey Road, and Jev answered from memory. The pipeline now asks each single question three ways: from memory, the pick, and the answer from the two picked sections. It also plants a wrong singer in each Abbey Road answer to test the grounding check.

### Candidates

`scripts/score/rad_table.py candidates results/runs/2026-09-23-thinkthen-jev-rad results/runs/2026-09-23-thinkthen-jev-rad2 --closed results/runs/2026-09-23-thinkthen-jev --open results/runs/2026-09-23-thinkthen-jev-open-book` lists them with no new calls. It joins the closed-book run (`2026-09-23-thinkthen-jev`) with each run on question id. It keeps questions where closed book was wrong, the k = 2 Jev pick held every section `rad.py needed()` names (from `rank-jev.tsv`), and the k = 2 answer was right. 103 questions passed in at least one run. Six singer questions name a song with one lead singer. Five more name songs with a shared lead, and one pick of four singers cannot answer those. The pipeline asks in its own wording, and Jev knew all six from memory in that wording:

| Song | Truth | Bench closed book | Pipeline memory | Pipeline pick, top two | Pipeline answer |
| --- | --- | --- | --- | --- | --- |
| Boys | Starr | Lennon (0.54) | Starr (0.88) | With the Beatles 0.65, Please Please Me 0.21 | Starr (1.0) |
| Chains | Harrison | Lennon (0.34) | Harrison (0.53) | With the Beatles 0.44, Please Please Me 0.35 | Harrison (1.0) |
| For No One | McCartney | "Does Lennon sing lead?" yes (0.53) | McCartney (0.98) | Revolver 0.48, Sgt. Pepper 0.19 | McCartney (1.0) |
| Martha My Dear | McCartney | "Does Lennon sing lead?" yes (0.67) | McCartney (0.98) | White Album 0.98, Sgt. Pepper 0.01 | McCartney (1.0) |
| Good Night | Starr | "Is Starr the only lead?" no (0.52) | Starr (0.94) | White Album 0.97, Rubber Soul 0.02 | Starr (1.0) |
| Dizzy Miss Lizzy | Lennon | "Does Lennon sing lead?" no (0.59) | Lennon (0.50) | Help! 0.22, Beatles for Sale 0.15 | Lennon (1.0) |

The bench asks "The text is the title of a song by the Beatles. Who sings the lead vocal on it?" with the title as the text. The pipeline asks "Who sang lead on the Beatles song "Boys"?". Naming the song in the question was enough for Jev on all six. Every pick held the needed section.

So the search moved to well-known songs among the other forward questions. A screen sent only the pipeline's memory call for seven of them (`tries/screen/`):

| Song | Question | Truth | Pipeline memory |
| --- | --- | --- | --- |
| Yesterday | year | 1965 | 1965 (0.58) |
| Tomorrow Never Knows | year | 1966 | 1967 (0.59) |
| Michelle | year | 1965 | 1966 (0.39) |
| Taxman | songwriter | Harrison | Harrison (0.99) |
| Piggies | songwriter | Harrison | Harrison (0.98) |
| Act Naturally | first album | Help! | Beatles for Sale (0.70) |
| And I Love Her | first album | A Hard Day's Night | A Hard Day's Night (0.86) |

Tomorrow Never Knows has the most page views of the three misses, and its miss is the surest. The bench closed book also said 1967 (0.77), and both recorded picks held Revolver. It is the chosen case. Michelle and Act Naturally were next in line and were not needed.

### Results

`results/runs/2026-09-24-pipeline-jev2/` holds the run. `tries/` holds the six singer tries and the screen.

| Arm | Right | Input tokens |
| --- | --- | --- |
| Octopus's Garden, memory | 1 of 1 (Starr, 0.99) | 361 |
| Octopus's Garden, pick | Abbey Road not in the top two | 1,115 |
| Octopus's Garden, answer | 1 of 1 (Starr, 0.90) | 2,181 |
| Tomorrow Never Knows, memory | 0 of 1 (1967, 0.59) | 472 |
| Tomorrow Never Knows, pick | Revolver first (0.91) | 1,121 |
| Tomorrow Never Knows, answer | 1 of 1 (1966, 1.0) | 1,522 |
| Abbey Road songs, memory | 4 of 18 | 8,439 |
| Abbey Road songs, glued | 18 of 18 | 20,317 |
| Abbey Road songs, apart | 18 of 18 | 20,463 |
| `annotate` over the apart answers | 18 of 18 checks agree with the truth | 22,952 |
| `annotate` over a wrong singer per song | caught 18 of 18 | 22,936 |

- Octopus's Garden stays as the control. Jev knows it from memory at 0.99, so its right answer says nothing about the pick.
- Tomorrow Never Knows is the deck's example. From memory Jev says 1967. The pick puts Revolver first at 0.91. With the Revolver and Sgt. Pepper sections before the question, Jev says 1966 at 1.0.
- The wrong-singer case names, for each Abbey Road song, one Beatle who did not sing lead there, taken in turn by song. `grounded` said no on all 18, and `correct` also said no on all 18. The Abbey Road section spells out "lead:" for every song, so this shows the check catches a plain contradiction. It says nothing about subtler errors.
- `times.tsv` comes from the last live run, which answered most calls from the recording. Those times do not measure the backend.

## Fresh run of 2026-09-26

Ticket 0014 asked the RAD, RAD2, and pipeline runs again from empty recordings (`sdlc/records/0014-shipped-recognize-and-relate.md`). Ticket 0009 had done the same on 2026-09-25. The BM25 and MiniLM ranks and the RAD2 split are the old files, copied in. The Jev picks are asked again. The commands above print these tables when given the fresh folders: `results/runs/2026-09-26-thinkthen-jev`, `-open-book`, `-rad`, and `-rad2`.

| Context | Right | Pick recall | Median input tokens | Median time | Dollars per 1,000 |
| --- | --- | --- | --- | --- | --- |
| Full catalog | 184 of 196 (94%) | 100% | 12,214 | 0.28 s | 0.513 |
| Jev picks, k = 1 | 153 of 196 (78%) | 57% | 2,049 | 0.46 s | 0.094 |
| Jev picks, k = 2 | 170 of 196 (87%) | 73% | 2,639 | 0.44 s | 0.121 |
| Jev picks, k = 3 | not asked | 81% | | | |
| BM25 picks, k = 2 | 162 of 196 (83%) | 61% | 1,942 | 0.22 s | 0.077 |
| MiniLM picks, k = 2 | 127 of 196 (65%) | 28% | 1,715 | 0.23 s | 0.068 |
| Jev picks, k = 2, full catalog below 0.5 | 182 of 196 (93%) | 89% | 3,232 | 0.46 s | 0.217 |
| Closed book | 68 of 196 (35%) | none | 362 | 0.22 s | 0.015 |

The second test, held-out half:

| Context | Right | Pick recall | Median input tokens | Median time | Dollars per 1,000 |
| --- | --- | --- | --- | --- | --- |
| Full catalog | 91 of 98 (93%) | 100% | 12,213 | 0.28 s | 0.513 |
| New Jev pick (with options), k = 2 | 86 of 98 (88%) | 77% | 2,610 | 0.42 s | 0.117 |
| New Jev pick, full catalog below 0.35 | 87 of 98 (89%) | 82% | 2,619 | 0.42 s | 0.140 |
| Old Jev pick (no options), k = 2 | 85 of 98 (87%) | 72% | 2,610 | 0.45 s | 0.121 |
| Old Jev pick, full catalog below 0.40 | 88 of 98 (90%) | 83% | 2,822 | 0.46 s | 0.174 |
| BM25 with options, k = 2 | 82 of 98 (84%) | 58% | 1,910 | 0.21 s | 0.077 |
| Old BM25 (no options), k = 2 | 80 of 98 (82%) | 59% | 1,942 | 0.22 s | 0.076 |
| Closed book | 34 of 98 (35%) | none | 361 | 0.23 s | 0.015 |

- `thinkthen diff` pairs all 980 RAD answers and all 490 RAD2 answers with the 2026-09-25 runs. 70 RAD answers and 31 RAD2 answers changed.
- Jev picks, k = 2, moved from 172 to 170 right. The fallback row stayed at 182.
- The tune half chose 0.35 for the new pick and 0.40 for the old one. The 2026-09-25 run chose 0.35 for both.
- One McNemar verdict on the held-out half changed. The new pick with its fallback against the full catalog: 3 against 7, p = 0.34. On 2026-09-25 it was 0 against 9, p = 0.004. Against BM25 with options: 12 against 7, p = 0.36. Against the old pick with its fallback: 5 against 6, p = 1.
- The pipeline (`results/runs/2026-09-26-pipeline-jev`) kept every score and all 18 checks. From memory, Jev again got 5 of 18 Abbey Road lead singers right. Its answer for The End changed from McCartney and Starr to Lennon, McCartney, and Starr. Both are wrong.
- The jobs sent 1,389,958 input tokens for RAD, 729,438 for RAD2, and 101,879 for the pipeline, about 0.09 dollars in all.
