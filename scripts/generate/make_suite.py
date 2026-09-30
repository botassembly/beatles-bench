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
names) and asks composed_by and produced_by under relate-links.json; the `more-` tests hold more sets of the same
kinds under fresh seeds, and recognize's kinds each have a -more test likewise. The smaller tests run at a 0.01 cut so
`thinkthen audit` can tune a bar across the range; the scorer cuts the printed edges at 0.5. relate-songs keeps its
0.5 cut. A case's truth holds the edges, and relate-songs' skip lists the songs whose sung_by edges are not scored.
relate-profile.json caps each request at 96,000 bytes, the ceiling thinkthen main applies to relation requests at
its built-in address.

Each function but recognize and relate also gets a "reading" test: a seeded sample of eligible memory cases, at most
100 per function, with the facts the truth needs written into the record as a short card after the input. The
question stays the same. decide and choose draw their memory cases from the main questions generate() makes; the
other functions draw from this file's own cases. recognize already reads the text it is given, and relate has no
reading test (ticket 0019). A case carries needs, the songs.tsv columns its truth needs.

Every case carries level: memory, card or context for the eight card-answerable functions, text for recognize, and
memory for relate. A question is asked once per level: the memory case, the card case (the old "reading" test, kept
for a seeded 100; 100 of each of rank's two asks), and the context case, whose record holds 20 cards in a seeded
order — the cards the truth needs plus fillers from the catalogue that cannot make a second right answer. A card or
context case's source names the memory question it reuses: for decide and choose that is a question in
questions/*.jsonl (their memory level lives there); for the others it is a memory case of this file. A context
case's songs lists the titles whose cards the truth needs. Each function's question set is 300 distinct asks (rank
keeps all 353 of its two tests): where a function had fewer, one more kind from songs.tsv joins it — tag traits,
score length, filter and find on more albums or a lead singer, annotate's details card, and decide's first-album
yes/no. Cases added after the first runs carry new test names and ids that share no prefix with the old ones, so a
run that asked only an old test still covers it whole.
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import SONG, WRITERS, settled_lead, words, generate as main_questions  # noqa: E402

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
FIND_SINGER = ("Each unit is the title of a song by the Beatles. Which one has {name} on lead vocal, "
               "alone or with another Beatle?")
TRAITS_Q = f"{SONG} Which of these does it have? Name every one it has, if any."
TRAITS_LABELS = ["--label", "cover=a cover of another artist's song", "--label", "long=runs over four minutes",
                 "--label", "lennon-mccartney=a Lennon–McCartney writing credit"]
SCORE_LENGTH_Q = f"{SONG} How long does it run?"
SCORE_LENGTH = ["Under two minutes.", "About two minutes.", "About three minutes.", "Four or five minutes.",
                "Well over five minutes."]
DECIDE_ALBUM = f"{SONG} Did it first appear on the album {{album}}?"
WRITER_CREDIT = {"Lennon–McCartney": "lennon-mccartney", "Harrison": "harrison", "Starkey": "starr"}
TRAIT_NEEDS = ("cover", "length_s", "songwriters")
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


def credit(s):
    """The songwriter-credit label of a song row, as the main bench maps it: a plain Beatles credit, other for a
    cover, None for a multi-way credit neither rule settles."""
    return WRITER_CREDIT.get(s["songwriters"]) or ("other" if s["cover"] == "yes" else None)


def one(fn, test, cid, args, title, truth, fields, level="memory", **extra):
    return {"id": cid, "function": fn, "test": test, "level": level, "args": args,
            "records": [{"id": cid, "input": title}], "truth": truth, "fields": fields, **extra}


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
        return {"id": cid, "function": "find", "test": test, "level": "memory",
                "args": [FIND_Q.format(album=album)] + JSONL,
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
            cases.append({"id": sid, "function": "recognize", "test": "names-template", "level": "text",
                          "args": RECOGNIZE, "records": [{"id": sid, "input": text}], "truth": names,
                          "fields": f(s, "title") + f(s, "lead_vocals") + f(s, "first_album") + f(s, "year")})
        cases += self.rec_groups()
        cases += self.rec_more()
        self.out["recognize"] = cases

    def settled(self):
        return [s for s in self.songs if settled_lead(s)]

    def slots(self, s, **over):
        return {"song": s["title"], "person": FULL[self.leads(s)[0]], "album": s["first_album"], "year": s["year"],
                **over}

    def rec(self, test, cid, text, names, fields, edges=None):
        """One recognize case. A relations case also carries edges: the [relation, source name, target name] triples
        the sentence states, run under --relation rules song:person and song:album."""
        c = one("recognize", test, cid, RECOGNIZE_REL if edges is not None else RECOGNIZE, text, names, fields,
                level="text")
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

    def relation_cases(self, test, idbase, seed, counts):
        """Sentences run with --relation rules in the bench's song-to-person direction, counted by kind: sung_by,
        appears_on, both, a shared lead, a shared song-and-album title, and an album named beside a song. Truth holds
        the stated edges only: a song and album that share a title state none."""
        r, cases, n = rng(seed), [], 0
        n_sung, n_appear, n_both, n_duet, n_dual, n_year = counts

        def add(template, s, edges, fields=None, **over):
            nonlocal n
            n += 1
            slots = self.slots(s, **over)
            text, names = fill(template, slots)
            edge_names = [[e[0], slots.get(e[1], e[1]), slots.get(e[2], e[2])] for e in edges]
            cases.append(self.rec(test, f"{idbase}-{n:02d}", text, names,
                                  fields or f(s, "title", "lead_vocals", "first_album", "year"), edges=edge_names))

        settled = self.settled()
        for i, s in enumerate(r.sample(settled, n_sung)):
            add(RELATION[i % 3], s, [["sung_by", "song", "person"]])
        for i, s in enumerate(r.sample(self.songs, n_appear)):
            add(RELATION[3 + i % 2], s, [["appears_on", "song", "album"]])
        for i, s in enumerate(r.sample(settled, n_both)):
            add(RELATION[5 + i % 2], s, [["sung_by", "song", "person"], ["appears_on", "song", "album"]])
        for i, s in enumerate(r.sample([s for s in settled if len(self.leads(s)) == 2], n_duet)):
            one_, two = (FULL[x] for x in self.leads(s)[:2])
            add(RELATION[7 + i % 2], s, [["sung_by", "song", "person"], ["sung_by", "song", "person2"]],
                person=one_, person2=two)
        albums = {a["album"]: a for a in self.albums}
        dual = [a for a in self.core if a in {s["title"] for s in self.songs}]
        for i, title in enumerate(r.sample(dual, n_dual)):
            s = next(x for x in self.songs if x["title"] == title)
            add(RELATION[9], s, [], album=title)  # the same title as song and as album: the sentence states no edge
        for i, s in enumerate(r.sample(self.songs, n_year)):
            other = r.choice([a for a in self.core if a != s["first_album"]])
            add(RELATION[10], s, [], album=other, album_year=albums[other]["release_date"][:4],
                fields=f(s, "title") + [["albums.tsv", other, "release_date", albums[other]["release_date"]]])
        return cases

    def rec_relations(self):
        """The original 40 relation sentences (ticket 0018)."""
        return self.relation_cases("relations", "recognize-relations", "recognize/relations", (12, 10, 6, 6, 4, 2))

    def rec_more(self):
        """The 0018 sentence kinds again under fresh seeds: 140 more name sentences and 60 more relations, for 300
        and 100 in all. New test names and id prefixes keep each old test whole for its recorded run."""
        r = rng("recognize/more")
        cases = []
        for n, s in enumerate(r.sample(self.settled(), 60), 1):
            text, names = fill(VARIED[(n - 1) % len(VARIED)], self.slots(s))
            cases.append(self.rec("varied-more", f"recognize-more-varied-{n:02d}", text, names,
                                  f(s, "title", "lead_vocals", "first_album", "year")))
        for n in range(1, 25):
            picks = r.sample(self.settled(), 4)
            sents = [fill(r.choice(VARIED + RELATION[:7]), self.slots(s)) for s in picks]
            text, names = join(*sents)
            cases.append(self.rec("paragraphs-more", f"recognize-more-paragraphs-{n:02d}", text, names,
                                  [x for s in picks for x in f(s, "title", "lead_vocals", "first_album", "year")]))
        for n in range(1, 25):
            lead = list(LEADS)[(n - 1) % len(LEADS)]
            s = r.choice([s for s in self.settled() if lead in self.leads(s)])
            text, names = fill(SHORT[(n - 1) % len(SHORT)],
                               self.slots(s, person=FULL[lead].split()[0] if n % 2 else lead))
            cases.append(self.rec("short-names-more", f"recognize-more-short-names-{n:02d}", text, names,
                                  f(s, "title", "lead_vocals", "first_album", "year")))
        for n, s in enumerate(r.sample(self.settled(), 12), 1):
            how = str.upper if n % 2 else str.lower
            slots = {k: how(v) if k in KINDS else v for k, v in self.slots(s).items()}
            text, names = fill(CASED[(n - 1) % len(CASED)], slots)
            cases.append(self.rec("case-more", f"recognize-more-case-{n:02d}", text, names,
                                  f(s, "title", "lead_vocals", "first_album", "year")))
        pool = [s for s in self.songs if any(m in s["title"] for m in PEELED + "-'")]
        for n, s in enumerate(r.sample(pool, 20), 1):
            text, names = fill(r.choice(PUNCT if settled_lead(s) else PUNCT[2:]), self.slots(s))
            cases.append(self.rec("punctuation-more", f"recognize-more-punctuation-{n:02d}", text, names,
                                  f(s, "title", "lead_vocals", "first_album", "year")))
        cases += self.relation_cases("relations-more", "recognize-more-relations", "recognize/relations-more",
                                     (18, 15, 9, 9, 6, 3))
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
        songs = {"id": "relate-songs", "function": "relate", "test": "song to singer and album", "level": "memory",
                 "args": ["@relate-suite.json", "--profile", "relate-profile.json", "--threshold", "0.5",
                          "--jsonl", "--timeout", "180"],
                 "records": [{"name": n, "kind": k} for n, k in ents], "truth": truth,
                 "skip": [s["title"] for s in self.songs if not settled_lead(s)],
                 "fields": [x for s in self.songs for x in f(s, "lead_vocals", "first_album")]}
        self.out["relate"] = [songs] + self.rel_small() + self.rel_links() + self.rel_more()

    def rel_case(self, test, n, qset, ents, truth, fields):
        """One relate case: a command call over one complete entity set."""
        return {"id": f"relate-{test}-{n:02d}", "function": "relate", "test": test, "level": "memory",
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

    def rel_more(self):
        """More sets of the 0019 kinds under fresh seeds, for 100 entity sets in all: 20 solo, 7 duet, 16
        wrong-album-only and 10 links sets. The more- test names keep each old test whole for its recorded run."""
        r = rng("relate/more")
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
                chunks.append([pool.pop() for _ in range(min(len(pool), 1 + r.randrange(3)))])
        r.shuffle(chunks)
        for picked in chunks[:20]:
            a = picked[0]["first_album"]
            small("more-solo", picked, [a] + r.sample([x for x in self.core if x != a], 2))
        duet_sets = []
        for a in self.core:
            duets = sorted([s for s in settled if s["first_album"] == a and len(self.leads(s)) == 2],
                           key=lambda s: s["title"])
            for i in range(len(duets)):
                for j in range(i + 1, len(duets)):
                    duet_sets.append([duets[i], duets[j]])
            if len(duets) > 2:
                duet_sets.append(duets)
        for picked in r.sample(duet_sets, 7):
            small("more-duet", picked, [picked[0]["first_album"]] + r.sample([x for x in self.core if x != picked[0]["first_album"]], 2))
        pool = list(settled)
        r.shuffle(pool)
        for i in range(16):
            picked = [pool.pop() for _ in range(min(len(pool), 1 + i % 3))]
            small("more-wrong-album-only", picked,
                  r.sample([a for a in self.core if a not in {s["first_album"] for s in picked}], 3))
        rows = [x for x in read(self.data / "links.tsv") if x["relation"] in LINK_REL]
        by_song = {}
        for x in rows:
            by_song.setdefault(x["song"], []).append(x)
        people_l = sorted({x["other_article"] for x in rows})
        songs = sorted(by_song)
        rng("relate/links-more").shuffle(songs)
        per = -(-len(songs) // 10)
        for i in range(0, len(songs), per):
            chunk = songs[i:i + per]
            mine = [x for s in chunk for x in by_song[s]]
            truth = [[LINK_REL[x["relation"]], x["song"], x["other_article"]] for x in mine]
            fields = [["links.tsv", "|".join([x["song"], x["relation"], x["other_article"]]), col, x[col]]
                      for x in mine for col in ("relation", "other_article")]
            ents = [(s, "song") for s in chunk] + [(p, "person") for p in people_l]
            cases.append(self.rel_case("more-links", sum(1 for c in cases if c["test"] == "more-links") + 1,
                                       "relate-links.json", ents, truth, fields))
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
        if "cover" in needs:
            lines.append(f"Cover: {s['cover'] or 'unknown'}")
        if "views_2024" in needs:
            lines.append(f"2024 page views: {s['views_2024'] or 'unknown'}")
        return "\n".join(lines)

    def read_one(self, c, cid, needs, group=None, test="reading"):
        """A card-level case from one-record memory case c: the same question, truth and arguments, the song's
        card written after the input text."""
        title = c["records"][0]["input"].split("\n")[0]
        rec = {"id": cid, "input": f"{title}\n\n{self.card(self.by_title[title], needs)}"}
        out = {"id": cid, "function": c["function"], "test": test, "level": "card", "args": c["args"],
               "records": [rec], "truth": c["truth"], "fields": c["fields"], "needs": list(needs), "source": c["id"]}
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
                                "level": "card", "args": c["args"], "records": records, "truth": c["truth"],
                                "key": c["key"], "fields": c["fields"], "needs": ["first_album"],
                                "source": c["id"]})
        out["annotate"] += [self.read_one(c, f"annotate-reading-{i:03d}", ("lead_vocals", "first_album", "year"))
                            for i, c in enumerate(r.sample(self.out["annotate"], 100), 1)]
        for fn in ("decide", "choose"):
            made = self.eligible_mains(data, fn)
            for i, (q, needs, titles) in enumerate(r.sample(made, min(100, len(made))), 1):
                cid = f"{fn}-reading-{i:03d}"
                text = q["input"] + "\n\n" + "\n\n".join(self.card(self.by_title[t], needs) for t in titles)
                rec = {"id": cid, "input": text}
                if q["options"]:
                    rec["options"] = q["options"]
                args = [q["question"], "--jsonl", "--field", "/input"] + (["--options", "/options"] if fn == "choose" else [])
                out[fn] = out.get(fn, []) + [{"id": cid, "function": fn, "test": "reading", "level": "card",
                                              "args": args, "records": [rec], "truth": q["truth"],
                                              "fields": q["fields"], "needs": list(needs), "source": q["id"]}]


    def eligible_mains(self, data, fn):
        """The main questions of function fn a card can answer: (question, needs, needed titles), in generate()
        order. needs and titles follow READING_KINDS."""
        made = []
        for q in main_questions(data):
            spec = READING_KINDS.get((q["category"], q["kind"]))
            if not spec or q["function"] != fn:
                continue
            where, needs = spec
            titles = [q["input"]] if where == "input" else q["input"].split(" / ") if where == "pair" \
                else list(q["options"].values())
            if all(t in self.by_title for t in titles):
                made.append((q, needs, titles))
        return made

    # --- one more kind per function that had fewer than 300 asks ----------------------------------------------
    def traits_of(self, s):
        """The song's trait labels: a cover, runs over four minutes, a Lennon–McCartney writing credit."""
        out = []
        if s["cover"] == "yes":
            out.append("cover")
        if s["songwriters"] == "Lennon–McCartney":
            out.append("lennon-mccartney")
        if int(s["length_s"]) > 240:
            out.append("long")
        return sorted(out)

    def tag_traits(self):
        """tag's second kind: which of three song traits the song has. All 21 songs with no trait are asked, so the
        empty-truth share is about 15% of the 142."""
        r = rng("tag/traits")
        empty = [s for s in self.songs if not self.traits_of(s)]
        rest = r.sample([s for s in self.songs if self.traits_of(s)], 142 - len(empty))
        self.out["tag"] += [one("tag", "traits", f"tag-traits-{i:03d}", [TRAITS_Q] + TRAITS_LABELS + JSONL,
                                s["title"], self.traits_of(s), f(s, "cover", "length_s", "songwriters"))
                            for i, s in enumerate(empty + rest, 1)]

    def score_length(self):
        """score's second kind: running time on a five-level scale, 129 songs to bring score to 300 asks."""
        r = rng("score/length")
        self.out["score"] += [one("score", "length", f"score-length-{i:03d}", [SCORE_LENGTH_Q] + SCORE_LENGTH + JSONL,
                                  s["title"], int(s["length_s"]), f(s, "length_s"))
                              for i, s in enumerate(r.sample([s for s in self.songs if s["length_s"]], 129), 1)]

    def filter_more(self):
        """filter on two more albums, 60 asks to bring filter to 300, with the kept/dropped mix the other groups
        hold."""
        used = {c["key"] for c in self.out["filter"]} - set(LEAD_OF)
        albums = sorted(rng("filter/albums-more").sample([a for a in self.core if a not in used], 2),
                        key=self.core.index)
        for n, k in enumerate(albums, 1):
            r = rng(f"filter/album-more/{k}")
            yes = r.sample([s for s in self.songs if s["first_album"] == k], 8)
            no = r.sample([s for s in self.songs if s["first_album"] != k], 22)
            items = yes + no
            r.shuffle(items)
            group = f"filter-more-{n}"
            self.out["filter"] += [one("filter", "album-more", f"{group}-{i:02d}",
                                       [FILTER_ALBUM.format(album=k)] + JSONL, s["title"], s["first_album"] == k,
                                       f(s, "first_album"), key=k, group=group)
                                   for i, s in enumerate(items, 1)]

    def find_singer(self):
        """find's second kind: the unit with a named Beatle on lead, alone or with another. 45 sets hold no right
        unit and run with --none — about 15% of the 300 find sets. Each target is a settled song, asked once a
        singer."""
        quotas = {"Lennon": (55, 17), "McCartney": (54, 17), "Harrison": (25, 8), "Starr": (10, 3)}
        for name, (quota, n_none) in quotas.items():
            r = rng(f"find/singer/{name}")
            out_pool = [s for s in self.songs
                        if name not in s["lead_vocals"].split("+") and name not in s["article_lead"].split("+")]
            targets = r.sample([s for s in self.settled() if name in self.leads(s)], quota - n_none)
            for n in range(1, quota + 1):
                target = targets[n - 1] if n <= len(targets) else None
                others = r.sample(out_pool, 7 if target else 8)
                units = ([target] if target else []) + others
                r.shuffle(units)
                cid = f"find-singer-{LEADS[name]}-{n:02d}"
                args = [FIND_SINGER.format(name=FULL[name])] + JSONL + ([] if target else ["--none"])
                self.out["find"].append({"id": cid, "function": "find", "test": "singer", "level": "memory",
                                         "args": args, "truth": f"u{units.index(target) + 1}" if target else "none",
                                         "records": [{"id": f"u{i}", "input": s["title"]}
                                                     for i, s in enumerate(units, 1)],
                                         "key": LEADS[name],
                                         "fields": [x for s in units for x in f(s, "lead_vocals", "article_lead")]})

    def annotate_details(self):
        """annotate's second kind: a card of writers, cover and length, 118 songs to bring annotate to 300 asks. A
        song whose credit is neither a plain Beatles one nor a cover (a multi-way credit) gets a null writers
        truth."""
        self.qsets["annotate-details.json"] = {"version": 1, "questions": {
            "writers": {"choose": f"{SONG} Who is credited with writing it?", "options": list(WRITERS.values())},
            "cover": {"choose": f"{SONG} Is it a cover of another artist's song, or one they wrote themselves?",
                      "options": ["a cover of another artist's song", "a song the Beatles wrote themselves"]},
            "length": {"choose": f"{SONG} How long does it run?",
                       "options": ["under three minutes", "three minutes or longer"]}}}
        r = rng("annotate/details")
        cover = lambda s: "a cover of another artist's song" if s["cover"] == "yes" else "a song the Beatles wrote themselves"
        length = lambda s: "under three minutes" if int(s["length_s"]) < 180 else "three minutes or longer"
        self.out["annotate"] += [one("annotate", "details", f"annotate-details-{i:03d}",
                                     ["annotate-details.json"] + JSONL, s["title"],
                                     {"writers": WRITERS.get(credit(s)), "cover": cover(s), "length": length(s)},
                                     f(s, "songwriters", "cover", "length_s"))
                                 for i, s in enumerate(r.sample(self.songs, 118), 1)]

    def decide_album(self, data):
        """decide's second kind: did the song first appear on the named album. 132 asks bring decide to 300, with
        the yes/no split that keeps its questions half yes, half no."""
        mains = self.eligible_mains(data, "decide")
        n_yes = 150 - sum(q["truth"] == "yes" for q, _, _ in mains)
        n_no = 300 - len(mains) - n_yes
        r = rng("decide/album")
        pairs = [(s, s["first_album"], "yes") for s in r.sample(self.songs, n_yes)]
        for s in r.sample(self.songs, n_no):
            wrong = r.choice([a for a in self.core if a != s["first_album"] and not words(a) & words(s["title"])])
            pairs.append((s, wrong, "no"))
        r.shuffle(pairs)
        self.out["decide"] = self.out.get("decide", []) + [
            one("decide", "album", f"decide-album-{i:03d}", [DECIDE_ALBUM.format(album=a)] + JSONL, s["title"],
                truth, f(s, "first_album"))
            for i, (s, a, truth) in enumerate(pairs, 1)]

    def more(self, data):
        """The one more kind for each function under 300 asks. rank keeps its 353: the 2026-09-26 run recorded
        each kind as one ranked list, and the scorer checks that list against every case of the test, so no rank
        ask may drop while the committed tables stand."""
        self.tag_traits()
        self.score_length()
        self.filter_more()
        self.find_singer()
        self.annotate_details()
        self.decide_album(data)

    # --- context: the same asks with the needed cards among fillers ------------------------------------------
    def cards_in(self, titles, needs, r, skip=lambda s: False):
        """20 cards in a seeded order: the cards of the songs the truth needs, then fillers drawn from the
        catalogue. skip() keeps a filler out — for find, every song that would make a second right unit."""
        taken = set(titles)
        pool = [s for s in self.songs if s["title"] not in taken and not skip(s)]
        cards = [self.card(self.by_title[t], needs) for t in titles]
        cards += [self.card(s, needs) for s in r.sample(pool, 20 - len(cards))]
        r.shuffle(cards)
        return cards

    def context_one(self, m, needs, cid):
        """The context twin of a one-record memory case: the same arguments and truth, the record grown to the
        input text plus 20 cards."""
        r = rng(f"context/{cid}")
        title = m["records"][0]["input"]
        rec = {"id": cid, "input": f"{title}\n\n" + "\n\n".join(self.cards_in([title], needs, r))}
        out = {"id": cid, "function": m["function"], "test": f"{m['test']}-context", "level": "context",
               "args": m["args"], "records": [rec], "truth": m["truth"], "fields": m["fields"],
               "needs": list(needs), "source": m["id"], "songs": [title]}
        if "key" in m:
            out["key"] = m["key"]
        if "group" in m:
            out["group"] = f"{m['group']}-context"
        return out

    def context_find(self, m, cid):
        """The context twin of a find set: the eight units keep their cards, and 12 filler songs that can never be
        a right unit join them — for an album set no filler was first released on the asked album."""
        r = rng(f"context/{cid}")
        key = m["key"]
        if key in LEAD_OF:
            match = lambda s: LEAD_OF[key] in s["lead_vocals"].split("+") or LEAD_OF[key] in s["article_lead"].split("+")
            needs = ("lead_vocals",)
        else:
            match = lambda s: s["first_album"] == key
            needs = ("first_album",)
        taken = [u["input"] for u in m["records"]]
        units = [{"id": u["id"], "input": f"{u['input']}\n\n{self.card(self.by_title[u['input']], needs)}"}
                 for u in m["records"]]
        fillers = r.sample([s for s in self.songs if s["title"] not in taken and not match(s)], 12)
        records = units + [{"id": f"u{9 + i}", "input": f"{s['title']}\n\n{self.card(s, needs)}"}
                           for i, s in enumerate(fillers)]
        r.shuffle(records)
        return {"id": cid, "function": "find", "test": f"{m['test']}-context", "level": "context",
                "args": m["args"], "records": records, "truth": m["truth"], "key": key,
                "fields": m["fields"], "needs": list(needs), "source": m["id"], "songs": taken}

    def context_mains(self, fn, picked, start=1):
        """Context cases for main-question asks of decide or choose: the question's wording, options and truth, the
        input text then 20 cards."""
        out = []
        for i, (q, needs, titles) in enumerate(picked, start):
            cid = f"{fn}-context-{i:03d}"
            r = rng(f"context/{cid}")
            rec = {"id": cid, "input": q["input"] + "\n\n" + "\n\n".join(self.cards_in(titles, needs, r))}
            if q["options"]:
                rec["options"] = q["options"]
            args = [q["question"], "--jsonl", "--field", "/input"] + (["--options", "/options"] if fn == "choose" else [])
            out.append({"id": cid, "function": fn, "test": f"{q['category']}-context", "level": "context",
                        "args": args, "records": [rec], "truth": q["truth"], "fields": q["fields"],
                        "needs": list(needs), "source": q["id"], "songs": list(titles)})
        return out

    def choose_questions(self, data):
        """The 300 main choose questions of choose's question set: the 100 already asked at the card level, every
        eligible question whose right answer is none of these (the pool holds 30 — as near 15% as the data allows),
        and a seeded fill."""
        made = self.eligible_mains(data, "choose")
        forced = {c["source"] for c in self.out["choose"] if c["level"] == "card"}
        forced |= {q["id"] for q, _, _ in made if q["truth"] == "none"}
        r = rng("choose/questions")
        rest = r.sample([m for m in made if m[0]["id"] not in forced], 300 - len(forced))
        return [m for m in made if m[0]["id"] in forced] + rest

    CONTEXT_NEEDS = {"tag": {"lead": ("lead_vocals",), "traits": TRAIT_NEEDS},
                     "score": {"popularity": ("views_2024",), "length": ("length_s",)},
                     "filter": {"singer": ("lead_vocals",), "album": ("first_album",),
                                "album-more": ("first_album",)},
                     "rank": {"popularity": ("views_2024",), "date": ("release_date",)},
                     "annotate": {"card": ("lead_vocals", "first_album", "year"),
                                  "details": ("songwriters", "cover", "length_s")},
                     "decide": {"album": ("first_album",)}}

    def context(self, data):
        """Every distinct question of the eight card-answerable functions, again at the context level."""
        out = self.out
        for fn in ("tag", "score", "filter", "rank", "annotate", "decide"):
            mem = [c for c in out.get(fn, []) if c["level"] == "memory"]
            out[fn] += [self.context_one(m, self.CONTEXT_NEEDS[fn][m["test"]], f"{fn}-context-{i:03d}")
                        for i, m in enumerate(mem, 1)]
        mem = [c for c in out["find"] if c["level"] == "memory"]
        out["find"] += [self.context_find(m, f"find-context-{i:03d}") for i, m in enumerate(mem, 1)]
        ctx = sum(1 for c in out["decide"] if c["level"] == "context")
        out["decide"] += self.context_mains("decide", self.eligible_mains(data, "decide"), start=ctx + 1)
        out["choose"] += self.context_mains("choose", self.choose_questions(data))


def write_catalog(suite_out, mains, path):
    """One row per question the bench asks: every main question, then every suite case. file names the JSONL the
    question lives in; a suite row's category is its ask's family — a memory case's test, or the source's for a
    card or context case."""
    mem_cat = {c["id"]: c["test"] for cases in suite_out.values() for c in cases if c["level"] == "memory"}
    main_cat = {q["id"]: q["category"] for q in mains}
    rows = [{"id": q["id"], "file": f"{q['category']}.jsonl", "function": q["function"], "test": q["kind"],
             "level": "memory", "category": q["category"], "truth": q["truth"]} for q in mains]
    for name, cases in suite_out.items():
        for c in cases:
            cat = mem_cat.get(c.get("source")) or main_cat.get(c.get("source")) or c["test"]
            rows.append({"id": c["id"], "file": f"suite/{name}.jsonl", "function": c["function"],
                         "test": c["test"], "level": c["level"], "category": cat, "truth": c["truth"]})
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def main(data=ROOT / "data", out=ROOT / "questions" / "suite", catalog=None):
    data, out = Path(data), Path(out)
    suite = Suite(data)
    suite.qsets = {}
    for name in FUNCTIONS:
        getattr(suite, name)()
    suite.reading(data)  # before more(): the seeded card draws sample the original memory tests only
    suite.more(data)
    suite.context(data)
    out.mkdir(parents=True, exist_ok=True)
    for name, cases in suite.out.items():
        with open(out / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in cases)
    for name, qset in suite.qsets.items():
        (out / name).write_text(json.dumps(qset, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_catalog(suite.out, main_questions(data), Path(catalog) if catalog else out.parent / "catalog" / "catalog.jsonl")


if __name__ == "__main__":
    main(*sys.argv[1:])
