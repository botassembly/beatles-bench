#!/usr/bin/env python3
"""Turn data/ into questions/suite/: one test per ThinkThen function, plus the reading tests. Deterministic.

usage: make_suite.py [DATA OUT]   (defaults: data/ questions/suite/)

Each case is one command call. Every case but relate sends one request. A case holds id, function, test, args (the
command's arguments after the function name, less --details, --model, and the recording flags), records (the JSONL
records sent on standard input), truth, and fields (the data rows it came from, as [file, row key, column, value]).
Some cases add key (the singer or album asked about), group (the list a filter or rank record belongs to), or skip.

The songs are the 1962 to 1970 catalogue whose first album is a core album (released by 1970) and whose lead singers
are all Beatles. The wording sits in templates here, and the data fills every slot, option, and truth. A test of lead
singers asks or scores a song only when generate.settled_lead() passes it, the rule the main questions follow: tag and
filter by singer skip the other songs, annotate gives them no singer truth, and relate's skip lists them. Their
sung_by edges are not scored. Ids keep their place in the whole song list, so a skipped song leaves a gap in the
numbers.

recognize asks `thinkthen recognize song person album` once per sentence. Each case's truth holds the sentence's
names as [start, end, kind, name], in characters with the end exclusive, as the command prints them. The cases sit in
tests: names-template is the original 48; varied, song-or-album, short-names, case, no-names, paragraphs and
punctuation are the harder sentences; relations runs the same kinds under --relation sung_by=song:person --relation
appears_on=song:album and its cases add edges, the [relation, source, target] triples the sentence states. relate asks
`thinkthen relate` once per entity set. `relate-songs` holds the whole catalogue: every song, the four Beatles, and
the core albums. The `solo`, `duet`, and `wrong-album-only` tests hold small sets of one to three settled songs, the
four Beatles, and three albums; `wrong-album-only` leaves each song's right album out, so its true appears_on edge
set is empty. `links` draws about 20 entities from links.tsv (about a dozen songs and the seven people Wikidata
names) and asks composed_by and produced_by under relate-links.json. The smaller tests run at a 0.01 cut so
`thinkthen audit` can tune a bar across the range; the scorer cuts the printed edges at 0.5. relate-songs keeps its
0.5 cut. A case's truth holds the edges, and relate-songs' skip lists the songs whose sung_by edges are not scored.
relate-profile.json caps each request at 96,000 bytes, the ceiling thinkthen main applies to relation requests at
its built-in address.

Each function but recognize and relate also gets a "reading" test: a seeded sample of eligible memory cases, at most
100 per function, with the facts the truth needs written into the record as a short card after the input. The
question stays the same. decide and choose draw their memory cases from the main questions generate() makes; the
other functions draw from this file's own cases. recognize already reads the text it is given, and relate has no
reading test (ticket 0019). A case carries needs, the songs.tsv columns its truth needs.
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import SONG, settled_lead, words, generate as main_questions  # noqa: E402

SEED = "beatles-bench-functions-1"
FUNCTIONS = ["tag", "score", "filter", "rank", "find", "annotate", "recognize", "relate"]
LEADS = {"Lennon": "john", "McCartney": "paul", "Harrison": "george", "Starr": "ringo"}
LEAD_OF = {v: k for k, v in LEADS.items()}
FULL = {"Lennon": "John Lennon", "McCartney": "Paul McCartney", "Harrison": "George Harrison", "Starr": "Ringo Starr"}
LABELS = ["--label", "john=John Lennon", "--label", "paul=Paul McCartney", "--label", "george=George Harrison",
          "--label", "ringo=Ringo Starr"]
JSONL = ["--jsonl", "--field", "/input"]
KINDS = ["song", "person", "album"]

TAG_Q = f"{SONG} Which Beatles sang its lead vocal? Name every one who did, since some songs share the lead."
SCORE_Q = f"{SONG} How well known is it today?"
SCORE_LEVELS = ["Almost unknown.", "Known mostly to fans.", "Well known.", "Very well known.", "One of the most famous songs ever recorded."]
FILTER_SINGER = f"{SONG} Does {{name}} sing the lead vocal on it, alone or with another Beatle?"
FILTER_ALBUM = f"{SONG} Was it first released on the album {{album}}?"
RANK = {"popularity": f"{SONG} Is it one of their most famous songs?",
        "date": f"{SONG} Was it released late in the Beatles' career, nearer 1970 than 1962?"}
FIND_Q = "Each unit is the title of a song by the Beatles. Which one was first released on the album {album}?"
TEMPLATES = ["{person} sang lead on {song} from the album {album} in {year}",
             "In {year} the album {album} carried {song} with {person} on lead vocals",
             "Listeners hear {person} sing lead on {song} which first appeared on {album} in {year}",
             "When {album} came out in {year} it included {song} sung by {person}"]
# The harder recognize groups, one test name each. names-template is the original 48. Every slot whose name is a kind,
# or a kind with digits on the end ({person2}), becomes a name span. Other slots, such as {year}, fill as literals.
VARIED = ["{song} is a {year} song sung by {person} on the album {album}",
          "On {album} the track {song} has {person} on lead vocals",
          "The album {album} includes {song} where {person} sings lead",
          "The song {song} sung by {person} first appeared on {album}",
          "{person} takes the lead on {song} a track from {album}",
          "{year} gave listeners {song} with {person} singing lead on the album {album}",
          "On the {year} album {album} {person} sings {song}",
          "{song} came out on {album} in {year} and {person} sings the lead",
          "From {album} in {year} comes {song} sung by {person}",
          "{person} is the lead singer on {song} which the album {album} carries",
          "The {year} album {album} holds {song} with {person} on lead",
          "{person} sings {song} on {album} which came out in {year}"]
SONG_OR_ALBUM = {"song": ["{person} sang lead on the song {song} in {year}", "the song {song} came out in {year}"],
                 "album": ["the album {album} came out in {album_year}",
                           "the {album_year} album {album} carried {song2}"]}
SHORT = ["{person} sang lead on {song} in {year}", "{song} has {person} on lead vocals since {year}"]
CASED = ["{person} sang lead on {song} from the album {album} in {year}",
         "on {album} the track {song} has {person} at the microphone"]
NO_NAMES = ["The band played its last concert on a rooftop in London",
            "Crowds waited outside the studio hoping to see the four musicians",
            "Their records sold faster than those of any other group at the time",
            "The four friends from Liverpool changed popular music forever",
            "Fans camped outside the hotel before the big show",
            "A documentary crew filmed the rehearsals for weeks on end",
            "Radio stations played the new single all day long",
            "The tour ended early because the screaming drowned out the music",
            "Their producer had trained as an engineer before he joined the studio",
            "The manager wanted one more tour but the band refused"]
PUNCT = ["{person} sang lead on {song} in {year}",
         "{song}, from {album}, has {person} on lead vocals",
         "the song {song} sits on the album {album} from {year}",
         "{song} first appeared on {album} in {year}"]
RELATION = ["{person} sang lead on {song}", "{person} takes the lead vocal on {song}", "{song} has {person} on lead",
            "{song} first appeared on the album {album}", "the album {album} carried {song} in {year}",
            "{person} sang lead on {song} from the album {album}", "{song} from the album {album} has {person} singing lead",
            "{person} and {person2} shared the lead vocal on {song}", "{song} is sung by {person} and {person2}",
            "the song {song} and the album {album} share a title",
            "the album {album} came out in {album_year} while {song} stayed a favourite"]
PEELED = ".!?,:;"  # the marks the command's tokenizer peels from a word's end (specification/recognize.md, "Names")
RECOGNIZE = ["song", "person", "album", "--jsonl", "--field", "/input"]
RECOGNIZE_REL = ["song", "person", "album", "--relation", "sung_by=song:person", "--relation", "appears_on=song:album",
                 "--jsonl", "--field", "/input"]
# relate: the relations are the function folder's, less its threshold. Every case passes --threshold 0.01: a saved
# edge list holds nothing under the run's cut, so a low cut lets `thinkthen audit` tune a bar. The scorer applies the
# published 0.5 cut itself. relate-links.json adds the links.tsv relations, song to person both.
RELATE = {"version": 1, "relate": json.loads((ROOT / "examples" / "relate" / "relate.json").read_text(encoding="utf-8"))["relate"]}
RELATE_LINKS = {"version": 1, "relate": {"relations": [
    {"name": "composed_by", "source": "song", "target": "person", "reads": "was composed by"},
    {"name": "produced_by", "source": "song", "target": "person", "reads": "was produced by"}]}}
PROFILE = {"schema": "thinkthen.backend-profile/1", "name": "request-96000", "max_request_bytes": 96000}
LINK_REL = {"composer": "composed_by", "producer": "produced_by"}
RELATE_RUN = ["--profile", "relate-profile.json", "--threshold", "0.01", "--jsonl", "--timeout", "180"]

# The decide and choose questions a card can answer: the song table covers every fact the truth needs. The first
# element says where the songs sit: "input" cards the song the input names, "pair" cards both sides of an "A / B"
# input, "options" cards each option song. The second names the songs.tsv columns the truth needs; each becomes a
# card line. Cases about world events (events.tsv), pairs (links.tsv, reversal-general.tsv), and album dates
# (albums.tsv) are not eligible.
READING_KINDS = {
    ("forward", "singer"): ("input", ("lead_vocals",)),
    ("forward", "album"): ("input", ("first_album",)),
    ("forward", "songwriter"): ("input", ("songwriters",)),
    ("forward", "year"): ("input", ("year",)),
    ("reverse", "singer-to-song"): ("options", ("lead_vocals",)),
    ("reverse", "album-to-song"): ("options", ("first_album",)),
    ("reverse", "singer-yes-no"): ("input", ("lead_vocals",)),
    ("single-hop", "song-album"): ("input", ("first_album",)),
    ("single-hop", "song-month"): ("input", ("release_date",)),
    ("comparison", "longer"): ("pair", ("length_s",)),
    ("shared-lead", "shared-lead"): ("input", ("lead_vocals",)),
    ("lead-set", "john"): ("input", ("lead_vocals",)),
    ("lead-set", "paul"): ("input", ("lead_vocals",)),
    ("lead-set", "george"): ("input", ("lead_vocals",)),
    ("lead-set", "ringo"): ("input", ("lead_vocals",)),
    ("near-neighbor", "album"): ("input", ("first_album",)),
    ("near-neighbor-control", "album"): ("input", ("first_album",)),
    ("lexical-trap", "song-to-album"): ("input", ("first_album",)),
    ("lexical-trap", "album-to-song"): ("options", ("first_album",)),
    ("lexical-trap-control", "song-to-album"): ("input", ("first_album",)),
    ("lexical-trap-control", "album-to-song"): ("options", ("first_album",)),
    ("none-of-these", "absent"): ("input", ("first_album",)),
    ("none-of-these", "present"): ("input", ("first_album",)),
}


def rng(name):
    return random.Random(f"{SEED}/{name}")


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def f(s, *cols):
    return [["songs.tsv", s["title"], c, s[c]] for c in cols]


def one(fn, test, cid, args, title, truth, fields, **extra):
    return {"id": cid, "function": fn, "test": test, "args": args, "records": [{"id": cid, "input": title}],
            "truth": truth, "fields": fields, **extra}


def fill(template, slots):
    """Render template into (sentence, names). A slot whose name, less its trailing digits, is a kind becomes a name
    span of that kind; other slots fill as literals. Marks closing a slot word join it with no space, and drop when
    the name already ends in a mark."""
    text, names = "", []
    for word in template.split():
        m = re.fullmatch(r"\{(\w+)\}([.,!?;:]*)", word)
        value, marks = (slots[m.group(1)], m.group(2)) if m else (word, "")
        if text:
            text += " "
        if m and m.group(1).rstrip("0123456789") in KINDS:
            names.append([len(text), len(text) + len(value), m.group(1).rstrip("0123456789"), value])
            text += value if value.endswith(tuple(PEELED)) else value + marks
        else:
            text += value + marks
    return text, names


def join(*sentences):
    """Join (text, names) pairs into one paragraph, a period after each sentence that does not end in a mark, and a
    capital letter at each sentence start unless a name opens it."""
    text, names = "", []
    for t, ns in sentences:
        if t[0].islower() and (not ns or ns[0][0] != 0):
            t = t[0].upper() + t[1:]
        t = t if t[-1] in PEELED else t + "."
        base = len(text) + (1 if text else 0)
        text += (" " if text else "") + t
        names += [[a + base, b + base, k, v] for a, b, k, v in ns]
    return text, names


class Suite:
    def __init__(self, data):
        self.data = data
        self.albums = [a for a in read(data / "albums.tsv")]
        core = {a["album"] for a in self.albums if a["release_date"][:4] <= "1970"}
        self.core = [a["album"] for a in self.albums if a["album"] in core]
        self.songs = [s for s in read(data / "songs.tsv") if s["catalogue"] == "core 1962-1970" and s["first_album"] in core
                      and all(x in LEADS for x in s["lead_vocals"].split("+"))]
        self.by_title = {s["title"]: s for s in read(data / "songs.tsv")}
        self.out = {}

    def leads(self, s):
        return s["lead_vocals"].split("+")

    def tag(self):
        self.out["tag"] = [one("tag", "lead", f"tag-lead-{i:03d}", [TAG_Q] + LABELS + JSONL, s["title"],
                               sorted(LEADS[x] for x in self.leads(s)), f(s, "lead_vocals", "article_lead"))
                           for i, s in enumerate(self.songs, 1) if settled_lead(s)]

    def score(self):
        self.out["score"] = [one("score", "popularity", f"score-popularity-{i:03d}", [SCORE_Q] + SCORE_LEVELS + JSONL,
                                 s["title"], int(s["views_2024"]), f(s, "views_2024"))
                             for i, s in enumerate([s for s in self.songs if s["views_2024"]], 1)]

    def filter(self):
        cases = []
        for test, keys, has, q in [
            ("singer", list(LEAD_OF), lambda s, k: LEAD_OF[k] in self.leads(s), lambda k: FILTER_SINGER.format(name=FULL[LEAD_OF[k]])),
            ("album", sorted(rng("filter/albums").sample(self.core, 4), key=self.core.index),
             lambda s, k: s["first_album"] == k, lambda k: FILTER_ALBUM.format(album=k))]:
            for n, k in enumerate(keys, 1):
                r = rng(f"filter/{test}/{k}")
                pool = [s for s in self.songs if test == "album" or settled_lead(s)]
                yes = r.sample([s for s in pool if has(s, k)], 8)
                no = r.sample([s for s in pool if not has(s, k)], 22)
                items = yes + no
                r.shuffle(items)
                group = f"filter-{test}-{n}"
                col = "lead_vocals" if test == "singer" else "first_album"
                cases += [one("filter", test, f"{group}-{i:02d}", [q(k)] + JSONL, s["title"], has(s, k), f(s, col),
                              key=k, group=group) for i, s in enumerate(items, 1)]
        self.out["filter"] = cases

    def rank(self):
        cases = []
        for test, col in [("popularity", "views_2024"), ("date", "release_date")]:
            pool = [s for s in self.songs if s[col]]
            rng(f"rank/{test}").shuffle(pool)
            cases += [one("rank", test, f"rank-{test}-{i:03d}", [RANK[test]] + JSONL, s["title"],
                          int(s[col]) if test == "popularity" else s[col], f(s, col), group=f"rank-{test}")
                      for i, s in enumerate(pool, 1)]
        self.out["rank"] = cases

    def find_set(self, album, cid, test, target, others, r):
        fair = [s for s in self.songs if not words(s["title"]) & words(album)]
        units = [target] + [r.choice([s for s in fair if s["first_album"] == o]) for o in others]
        r.shuffle(units)
        records = [{"id": f"u{i}", "input": s["title"]} for i, s in enumerate(units, 1)]
        return {"id": cid, "function": "find", "test": test, "args": [FIND_Q.format(album=album)] + JSONL,
                "records": records, "truth": f"u{units.index(target) + 1}", "key": album,
                "fields": [x for s in units for x in f(s, "first_album")]}

    def find(self):
        cases = []
        for album in self.core:
            r = rng(f"find/{album}")
            own = [s for s in self.songs if not words(s["title"]) & words(album) and s["first_album"] == album]
            for n, target in enumerate(r.sample(own, min(4, len(own))), 1):
                others = r.sample([a for a in self.core if a != album], 7)
                cases.append(self.find_set(album, f"find-album-{self.core.index(album) + 1:02d}-{n}", "album",
                                           target, others, r))
        self.find_more(cases)
        self.out["find"] = cases

    def find_more(self, cases):
        """More album sets, to about 150 in all: up to nine fresh targets per album, skipping the ones test album
        already took where it can. The new sets sit in test album-more so a run that asked only the first 52 still
        covers test album whole."""
        for album in self.core:
            r = rng(f"find-more/{album}")
            fair = [s for s in self.songs if not words(s["title"]) & words(album)]
            own = [s for s in fair if s["first_album"] == album]
            took = {next(u["input"] for u in c["records"] if u["id"] == c["truth"])
                    for c in cases if c["key"] == album}
            pool = [s for s in own if s["title"] not in took] or own
            for n, target in enumerate(r.sample(pool, min(9, len(pool))), 5):
                others = r.sample([a for a in self.core if a != album], 7)
                cases.append(self.find_set(album, f"find-more-{self.core.index(album) + 1:02d}-{n}", "album-more",
                                           target, others, r))

    def annotate(self):
        years = [str(y) for y in range(1962, 1971)]
        self.qsets["annotate-card.json"] = {"version": 1, "questions": {
            "singer": {"tag": f"{SONG} Which Beatles sang its lead vocal?", "labels": {LEADS[k]: v for k, v in FULL.items()}},
            "album": {"choose": f"{SONG} On which album was it first released?", "options": [a["album"] for a in self.albums]},
            "year": {"choose": f"{SONG} In what year was it first released?", "options": years}}}
        self.out["annotate"] = [one("annotate", "card", f"annotate-card-{i:03d}", ["annotate-card.json"] + JSONL, s["title"],
                                    {"singer": sorted(LEADS[x] for x in self.leads(s)) if settled_lead(s) else None,
                                     "album": s["first_album"], "year": s["year"]},
                                    f(s, "lead_vocals", "article_lead") + f(s, "first_album") + f(s, "year"))
                                for i, s in enumerate(self.songs, 1)]

    def recognize(self):
        r = rng("recognize")
        cases = []
        for n, s in enumerate(r.sample(self.songs, 48), 1):
            slots = {"song": s["title"], "person": FULL[self.leads(s)[0]], "album": s["first_album"], "year": s["year"]}
            text, names = "", []
            for piece in TEMPLATES[(n - 1) % len(TEMPLATES)].split():
                word = slots[piece[1:-1]] if piece.startswith("{") else piece
                text += " " if text else ""
                if piece[1:-1] in KINDS:
                    names.append([len(text), len(text) + len(word), piece[1:-1], word])
                text += word
            sid = f"recognize-{n:02d}"
            cases.append({"id": sid, "function": "recognize", "test": "names-template", "args": RECOGNIZE,
                          "records": [{"id": sid, "input": text}], "truth": names,
                          "fields": f(s, "title") + f(s, "lead_vocals") + f(s, "first_album") + f(s, "year")})
        cases += self.rec_groups()
        self.out["recognize"] = cases

    def settled(self):
        return [s for s in self.songs if settled_lead(s)]

    def slots(self, s, **over):
        return {"song": s["title"], "person": FULL[self.leads(s)[0]], "album": s["first_album"], "year": s["year"],
                **over}

    def rec(self, test, cid, text, names, fields, edges=None):
        """One recognize case. A relations case also carries edges: the [relation, source name, target name] triples
        the sentence states, run under --relation rules song:person and song:album."""
        c = one("recognize", test, cid, RECOGNIZE_REL if edges is not None else RECOGNIZE, text, names, fields)
        if edges is not None:
            c["edges"] = edges
        return c

    def rec_varied(self):
        r = rng("recognize/varied")
        return [self.rec("varied", f"recognize-varied-{n:02d}", *fill(VARIED[(n - 1) % len(VARIED)], self.slots(s)),
                         f(s, "title", "lead_vocals", "first_album", "year"))
                for n, s in enumerate(r.sample(self.settled(), len(VARIED) * 3), 1)]

    def rec_dual(self):
        """Every title that is both a song and an album, once as each. The sentence's own words name the kind."""
        by_title = {s["title"]: s for s in self.songs}
        albums = {a["album"]: a for a in self.albums}
        cases, n = [], 0
        for title in [a for a in self.core if a in by_title]:
            s = by_title[title]
            others = [x["title"] for x in self.songs if x["first_album"] == title and x["title"] != title]
            slots = self.slots(s, album=title, album_year=albums[title]["release_date"][:4],
                               song2=others[0] if others else "")
            song_t = SONG_OR_ALBUM["song"][0 if settled_lead(s) else 1]
            text, names = fill(song_t, slots)
            cases.append(self.rec("song-or-album", f"recognize-song-or-album-{n + 1:02d}", text, names,
                                  f(s, "title", "lead_vocals", "year") if settled_lead(s) else f(s, "title", "year")))
            n += 1
            album_t = SONG_OR_ALBUM["album"][1 if others and n % 2 else 0]
            text, names = fill(album_t, slots)
            fields = [["albums.tsv", title, "release_date", albums[title]["release_date"]]]
            fields += f(by_title[slots["song2"]], "first_album") if "{song2}" in album_t else []
            cases.append(self.rec("song-or-album", f"recognize-song-or-album-{n + 1:02d}", text, names, fields))
            n += 1
        return cases

    def rec_short(self):
        """A first name or surname alone, still a person."""
        r, cases, n = rng("recognize/short-names"), [], 0
        for last_name in LEADS:
            full = FULL[last_name]
            mine = [s for s in self.settled() if last_name in self.leads(s)]
            for short in (full.split()[0], last_name):
                for t in SHORT:
                    s = r.choice(mine)
                    n += 1
                    text, names = fill(t, self.slots(s, person=short))
                    cases.append(self.rec("short-names", f"recognize-short-names-{n:02d}", text, names,
                                          f(s, "title", "lead_vocals", "first_album", "year")))
        return cases

    def rec_case(self):
        r, cases = rng("recognize/case"), []
        for n, s in enumerate(r.sample(self.settled(), 12), 1):
            how = str.upper if n % 2 else str.lower
            slots = {k: how(v) if k in KINDS else v for k, v in self.slots(s).items()}
            text, names = fill(CASED[(n - 1) % len(CASED)], slots)
            cases.append(self.rec("case", f"recognize-case-{n:02d}", text, names,
                                  f(s, "title", "lead_vocals", "first_album", "year")))
        return cases

    def rec_none(self):
        return [self.rec("no-names", f"recognize-no-names-{n:02d}", text, [], [])
                for n, text in enumerate(NO_NAMES, 1)]

    def rec_paragraphs(self):
        r, cases = rng("recognize/paragraphs"), []
        for n in range(1, 11):
            picks = r.sample(self.settled(), 4)
            sents = [fill(r.choice(VARIED + RELATION[:7]), self.slots(s)) for s in picks]
            text, names = join(*sents)
            cases.append(self.rec("paragraphs", f"recognize-paragraphs-{n:02d}", text, names,
                                  [x for s in picks for x in f(s, "title", "lead_vocals", "first_album", "year")]))
        return cases

    def rec_punctuation(self):
        """Titles with marks inside: each command token of the name can end it early."""
        must = ["Back in the U.S.S.R.", "Ob-La-Di, Ob-La-Da", "Why Don't We Do It in the Road?", "Help!",
                "Sgt. Pepper's Lonely Hearts Club Band", "Being for the Benefit of Mr. Kite!", "Here, There and Everywhere"]
        by_title = {s["title"]: s for s in self.songs}
        r = rng("recognize/punctuation")
        pool = [s for s in self.songs if s["title"] not in must and any(m in s["title"] for m in PEELED + "-'")]
        picks = [by_title[t] for t in must if t in by_title] + r.sample(pool, 14 - len([t for t in must if t in by_title]))
        cases = []
        for n, s in enumerate(picks, 1):
            t = r.choice(PUNCT if settled_lead(s) else PUNCT[2:])
            text, names = fill(t, self.slots(s))
            cases.append(self.rec("punctuation", f"recognize-punctuation-{n:02d}", text, names,
                                  f(s, "title", "lead_vocals", "first_album", "year")))
        return cases

    def rec_relations(self):
        """About 40 sentences run with --relation rules in the bench's song-to-person direction. Truth holds the
        stated edges only: a song and album that share a title state none."""
        r, cases, n = rng("recognize/relations"), [], 0

        def add(template, s, edges, fields=None, **over):
            nonlocal n
            n += 1
            slots = self.slots(s, **over)
            text, names = fill(template, slots)
            edge_names = [[e[0], slots.get(e[1], e[1]), slots.get(e[2], e[2])] for e in edges]
            cases.append(self.rec("relations", f"recognize-relations-{n:02d}", text, names,
                                  fields or f(s, "title", "lead_vocals", "first_album", "year"), edges=edge_names))

        settled = self.settled()
        for i, s in enumerate(r.sample(settled, 12)):
            add(RELATION[i % 3], s, [["sung_by", "song", "person"]])
        for i, s in enumerate(r.sample(self.songs, 10)):
            add(RELATION[3 + i % 2], s, [["appears_on", "song", "album"]])
        for i, s in enumerate(r.sample(settled, 6)):
            add(RELATION[5 + i % 2], s, [["sung_by", "song", "person"], ["appears_on", "song", "album"]])
        for i, s in enumerate(r.sample([s for s in settled if len(self.leads(s)) == 2], 6)):
            one_, two = (FULL[x] for x in self.leads(s)[:2])
            add(RELATION[7 + i % 2], s, [["sung_by", "song", "person"], ["sung_by", "song", "person2"]],
                person=one_, person2=two)
        albums = {a["album"]: a for a in self.albums}
        dual = [a for a in self.core if a in {s["title"] for s in self.songs}]
        for i, title in enumerate(r.sample(dual, 4)):
            s = next(x for x in self.songs if x["title"] == title)
            add(RELATION[9], s, [], album=title)  # the same title as song and as album: the sentence states no edge
        for i, s in enumerate(r.sample(self.songs, 2)):
            other = r.choice([a for a in self.core if a != s["first_album"]])
            add(RELATION[10], s, [], album=other, album_year=albums[other]["release_date"][:4],
                fields=f(s, "title") + [["albums.tsv", other, "release_date", albums[other]["release_date"]]])
        return cases

    def rec_groups(self):
        return (self.rec_varied() + self.rec_dual() + self.rec_short() + self.rec_case() + self.rec_none()
                + self.rec_paragraphs() + self.rec_punctuation() + self.rec_relations())

    def relate(self):
        self.qsets["relate-suite.json"] = RELATE
        self.qsets["relate-profile.json"] = PROFILE
        self.qsets["relate-links.json"] = RELATE_LINKS
        ents = [(s["title"], "song") for s in self.songs] + [(v, "person") for v in FULL.values()] + [(a, "album") for a in self.core]
        truth = [["sung_by", s["title"], FULL[x]] for s in self.songs if settled_lead(s) for x in self.leads(s)]
        truth += [["appears_on", s["title"], s["first_album"]] for s in self.songs]
        # relate-songs keeps its 0.5 cut: its run is the published compare, and a one-case group has no halves for
        # audit to tune. The smaller tests run at RELATE_RUN's 0.01 cut so `thinkthen audit` can tune a bar.
        songs = {"id": "relate-songs", "function": "relate", "test": "song to singer and album",
                 "args": ["@relate-suite.json", "--profile", "relate-profile.json", "--threshold", "0.5",
                          "--jsonl", "--timeout", "180"],
                 "records": [{"name": n, "kind": k} for n, k in ents], "truth": truth,
                 "skip": [s["title"] for s in self.songs if not settled_lead(s)],
                 "fields": [x for s in self.songs for x in f(s, "lead_vocals", "first_album")]}
        self.out["relate"] = [songs] + self.rel_small() + self.rel_links()

    def rel_case(self, test, n, qset, ents, truth, fields):
        """One relate case: a command call over one complete entity set."""
        return {"id": f"relate-{test}-{n:02d}", "function": "relate", "test": test,
                "args": [f"@{qset}"] + RELATE_RUN,
                "records": [{"name": v, "kind": k} for v, k in ents], "truth": truth, "fields": fields}

    def rel_small(self):
        """Small sets of one to three settled songs, the four Beatles, and three albums. solo and duet keep the right
        album (each case's songs share one first album); wrong-album-only keeps three wrong albums, so its true
        appears_on edge set is empty."""
        r = rng("relate/small")
        people = [(v, "person") for v in FULL.values()]
        settled = self.settled()
        cases = []

        def small(test, picked, albums):
            albums = list(albums)
            r.shuffle(albums)
            ents = [(s["title"], "song") for s in picked] + people + [(a, "album") for a in albums]
            truth = [["sung_by", s["title"], FULL[x]] for s in picked for x in self.leads(s)]
            truth += [["appears_on", s["title"], s["first_album"]] for s in picked if s["first_album"] in albums]
            fields = [x for s in picked for x in f(s, "lead_vocals", "first_album")]
            cases.append(self.rel_case(test, sum(1 for c in cases if c["test"] == test) + 1,
                                       "relate-suite.json", ents, truth, fields))

        solo = {a: sorted([s for s in settled if s["first_album"] == a and len(self.leads(s)) == 1],
                          key=lambda s: s["title"]) for a in self.core}
        chunks = []
        for a in self.core:
            pool = solo[a]
            r.shuffle(pool)
            while pool:
                chunks.append((a, [pool.pop() for _ in range(min(len(pool), 1 + r.randrange(3)))]))
        r.shuffle(chunks)
        for a, picked in chunks[:16]:
            small("solo", picked, [a] + r.sample([x for x in self.core if x != a], 2))
        for a in self.core:
            duets = sorted([s for s in settled if s["first_album"] == a and len(self.leads(s)) == 2],
                           key=lambda s: s["title"])
            if duets:
                small("duet", duets, [a] + r.sample([x for x in self.core if x != a], 2))
        pool = list(settled)
        r.shuffle(pool)
        for i in range(16):
            picked = [pool.pop() for _ in range(min(len(pool), 1 + i % 3))]
            small("wrong-album-only", picked,
                  r.sample([a for a in self.core if a not in {s["first_album"] for s in picked}], 3))
        return cases

    def rel_links(self):
        """links.tsv sets of about 20 entities: about a dozen songs and the seven people the table names as composer
        or producer, asked under relate-links.json. Truth is the table's pairs."""
        rows = [x for x in read(self.data / "links.tsv") if x["relation"] in LINK_REL]
        by_song = {}
        for x in rows:
            by_song.setdefault(x["song"], []).append(x)
        people = sorted({x["other_article"] for x in rows})
        songs = sorted(by_song)
        rng("relate/links").shuffle(songs)
        per = -(-len(songs) // 8)  # 12: eight sets of about 19 entities
        cases = []
        for i in range(0, len(songs), per):
            chunk = songs[i:i + per]
            mine = [x for s in chunk for x in by_song[s]]
            truth = [[LINK_REL[x["relation"]], x["song"], x["other_article"]] for x in mine]
            fields = [["links.tsv", "|".join([x["song"], x["relation"], x["other_article"]]), col, x[col]]
                      for x in mine for col in ("relation", "other_article")]
            ents = [(s, "song") for s in chunk] + [(p, "person") for p in people]
            cases.append(self.rel_case("links", len(cases) + 1, "relate-links.json", ents, truth, fields))
        return cases

    # --- reading: the same asks with the facts on a card ----------------------------------------------------
    def card(self, s, needs=()):
        """A short card: the song's row as lines. needs names the songs.tsv columns the truth needs; each becomes
        a line, beside the five lines every card holds. Page views go on only where the question needs them."""
        lead = " and ".join(FULL.get(x, x) for x in s["lead_vocals"].split("+") if x) or "unknown"
        length = f"{int(s['length_s']) // 60}:{int(s['length_s']) % 60:02d}" if s["length_s"] else "unknown"
        lines = [f"Title: {s['title']}", f"Lead singers: {lead}"]
        if "songwriters" in needs:
            lines.append(f"Written: {s['songwriters']}")
        lines += [f"First album: {s['first_album']}", f"Year: {s['year']}"]
        if "release_date" in needs:
            lines.append(f"Released: {s['release_date']}")
        lines.append(f"Length: {length}")
        if "views_2024" in needs:
            lines.append(f"2024 page views: {s['views_2024'] or 'unknown'}")
        return "\n".join(lines)

    def read_one(self, c, cid, needs, group=None, test="reading"):
        """A reading case from one-record memory case c: the same question, truth and arguments, the song's card
        written after the input text."""
        title = c["records"][0]["input"].split("\n")[0]
        rec = {"id": cid, "input": f"{title}\n\n{self.card(self.by_title[title], needs)}"}
        out = {"id": cid, "function": c["function"], "test": test, "args": c["args"], "records": [rec],
               "truth": c["truth"], "fields": c["fields"], "needs": list(needs)}
        if "key" in c:
            out["key"] = c["key"]
        if group is not None:
            out["group"] = group
        return out

    def reading(self, data):
        """test "reading" cases for the eight card-answerable functions: a seeded sample of each memory test's
        cases, at most 100 a function (two lists of 100 for rank), with the facts on a card. decide and choose
        sample the eligible main questions READING_KINDS names."""
        r = rng("reading")
        out = self.out
        out["tag"] += [self.read_one(c, f"tag-reading-{i:03d}", ("lead_vocals",))
                       for i, c in enumerate(r.sample(self.out["tag"], 100), 1)]
        out["score"] += [self.read_one(c, f"score-reading-{i:03d}", ("views_2024",))
                         for i, c in enumerate(r.sample(self.out["score"], 100), 1)]
        for i, c in enumerate(r.sample(self.out["filter"], 100), 1):
            needs = ("lead_vocals",) if c["test"] == "singer" else ("first_album",)
            out["filter"].append(self.read_one(c, f"filter-reading-{i:03d}", needs, group=f"reading-{c['group']}"))
        for test, needs in (("popularity", ("views_2024",)), ("date", ("release_date",))):
            pool = [c for c in self.out["rank"] if c["test"] == test]
            out["rank"] += [self.read_one(c, f"rank-reading-{test}-{i:03d}", needs,
                                          group=f"rank-reading-{test}", test=f"reading-{test}")
                            for i, c in enumerate(r.sample(pool, min(100, len(pool))), 1)]
        for i, c in enumerate(r.sample(self.out["find"], min(100, len(self.out["find"]))), 1):
            records = [{"id": u["id"], "input": f"{u['input']}\n\n{self.card(self.by_title[u['input']])}"}
                       for u in c["records"]]
            out["find"].append({"id": f"find-reading-{i:03d}", "function": "find", "test": "reading",
                                "args": c["args"], "records": records, "truth": c["truth"], "key": c["key"],
                                "fields": c["fields"], "needs": ["first_album"]})
        out["annotate"] += [self.read_one(c, f"annotate-reading-{i:03d}", ("lead_vocals", "first_album", "year"))
                            for i, c in enumerate(r.sample(self.out["annotate"], 100), 1)]
        pools = {"decide": [], "choose": []}
        for q in main_questions(data):
            spec = READING_KINDS.get((q["category"], q["kind"]))
            if spec:
                pools[q["function"]].append((q, spec))
        for fn in ("decide", "choose"):
            made = []
            for q, (where, needs) in pools[fn]:
                titles = [q["input"]] if where == "input" else q["input"].split(" / ") if where == "pair" \
                    else list(q["options"].values())
                if all(t in self.by_title for t in titles):
                    made.append((q, needs, titles))
            for i, (q, needs, titles) in enumerate(r.sample(made, min(100, len(made))), 1):
                cid = f"{fn}-reading-{i:03d}"
                text = q["input"] + "\n\n" + "\n\n".join(self.card(self.by_title[t], needs) for t in titles)
                rec = {"id": cid, "input": text}
                if q["options"]:
                    rec["options"] = q["options"]
                args = [q["question"], "--jsonl", "--field", "/input"] + (["--options", "/options"] if fn == "choose" else [])
                out[fn] = out.get(fn, []) + [{"id": cid, "function": fn, "test": "reading", "args": args,
                                              "records": [rec], "truth": q["truth"], "fields": q["fields"],
                                              "needs": list(needs), "source": q["id"]}]


def main(data=ROOT / "data", out=ROOT / "questions" / "suite"):
    data, out = Path(data), Path(out)
    suite = Suite(data)
    suite.qsets = {}
    for name in FUNCTIONS:
        getattr(suite, name)()
    suite.reading(data)
    out.mkdir(parents=True, exist_ok=True)
    for name, cases in suite.out.items():
        with open(out / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in cases)
    for name, qset in suite.qsets.items():
        (out / name).write_text(json.dumps(qset, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
