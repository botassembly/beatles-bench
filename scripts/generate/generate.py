#!/usr/bin/env python3
"""Turn data/ into questions/*.jsonl. Deterministic: every draw comes from a random.Random seeded by a fixed string.

usage: generate.py [DATA OUT]   (defaults: data/ questions/)

Each question: id, category, kind, function (the ThinkThen command), question, input (the text the question is
asked of), options (label -> description, for choose; null for decide), truth (a label, or yes/no), and fields
(the data rows it came from, as [file, row key, column, value]). Two optional keys tie questions together:
group (a lead-set song's four questions share it; a control question names the question it controls) and hops
(a multi-hop question lists the single-hop questions that ask its two facts).
Every lettered choose question (options a, b, c, ...) has its right letter spread evenly within its category and kind.

Each question file also gets an answer key for thinkthen audit and diff, OUT/keys/NAME.jsonl: one {"id", "value"}
line per question. value is the truth: "yes" or "no" for decide, the option label for choose. A key line has no part,
so audit makes its own seeded split.
"""
import csv
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "harvest"))
from harvest import display, surnames  # noqa: E402

SEED = "beatles-bench-1"
CATEGORIES = ["forward", "reverse", "multi-hop", "single-hop", "comparison", "shared-lead", "lead-set", "near-neighbor",
              "near-neighbor-control", "lexical-trap", "lexical-trap-control", "none-of-these", "reversal",
              "reversal-general", "reversal-general-shared-name"]
GENERAL_CATEGORIES = ["reversal-general", "reversal-general-shared-name"]  # outside the Beatles
NONE = "none of these"
SONG = "The text is the title of a song by the Beatles."
BEATLES = {"Lennon": ("john", "John Lennon"), "McCartney": ("paul", "Paul McCartney"),
           "Harrison": ("george", "George Harrison"), "Starr": ("ringo", "Ringo Starr")}
WRITERS = {"lennon-mccartney": "John Lennon and Paul McCartney", "harrison": "George Harrison",
           "starr": "Ringo Starr", "other": "a songwriter outside the Beatles"}
STOP = set("a an the of to in on and or for with my me you your it its is i be at from by this that all do don t we why "
           "let s he she her his him they them what when where who how there here got get so no not up out now can will "
           "just o if beatles".split())
GENERAL = {  # relation -> (question asked from the famous end, question asked from the obscure end)
    "father": ("The text names a person. Who is this person's father?", "The text names a person. This person is the father of which of these people?"),
    "mother": ("The text names a person. Who is this person's mother?", "The text names a person. This person is the mother of which of these people?"),
    "film composer": ("The text names a film. Who composed its music?", "The text names a composer. This person composed the music for which of these films?"),
    "building architect": ("The text names a building or structure. Who was an architect of it?", "The text names an architect. This person was an architect of which of these?"),
    "invention inventor": ("The text names an invention. Who is credited with inventing it?", "The text names an inventor. This person is credited with inventing which of these?"),
    "song writer": ("The text names a song and its performer. Who is a credited writer of it?", "The text names a songwriter. This person is a credited writer of which of these songs?"),
}
RELATION = {  # relation -> (question asked from the other end, question asked from the song)
    "composer": ("The text names a songwriter or a songwriting partnership. Which of these songs by the Beatles is credited to it?",
                 "Who is credited with writing it?"),
    "producer": ("The text names a record producer. Which of these songs by the Beatles did this person produce?", "Who produced it?"),
    "main subject": ("The text names a subject. Which of these songs by the Beatles is about it?", "What is it about?"),
    "named after": ("The text names a person, place, or thing. Which of these songs by the Beatles is named after it?", "What is it named after?"),
    "recorded at": ("The text names a recording studio. Which of these songs by the Beatles was recorded there?", "Where was it recorded?"),
    "influenced by": ("The text names a work or a person. Which of these songs by the Beatles was influenced by it?", "What influenced it?"),
}


def rng(name):
    return random.Random(f"{SEED}/{name}")


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def words(s):
    """Content words, lower case, with possessive 's and a plural s dropped."""
    toks = re.findall(r"[a-z]+", s.lower().replace("'s", "").replace("’s", ""))
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in toks if w not in STOP}


def last(name):
    """The last word of a name, ignoring Jr., Sr., and Roman numerals."""
    toks = [t for t in re.findall(r"[\w'-]+", name) if t.lower().rstrip(".") not in {"jr", "sr", "ii", "iii", "iv"}]
    return toks[-1].lower() if toks else ""


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()


def related(a, b):
    """True when two names share a name, so one gives the other away. A word of 4 or more letters in one name appears
    in the other's letters run together (De Palma and DePalma, Hagen and Oliva-Hagen), or two words of 6 or more
    letters share their first 6 (Plisetski and Plisetskaya)."""
    ta, tb = ([t for t in re.findall(r"[a-z]+", fold(n)) if t not in {"jr", "sr", "ii", "iii", "iv"}] for n in (a, b))
    ja, jb = "".join(ta), "".join(tb)
    if any(len(t) >= 4 and t in jb for t in ta) or any(len(t) >= 4 and t in ja for t in tb):
        return True
    return any(len(x) >= 6 and len(y) >= 6 and x[:6] == y[:6] for x in ta for y in tb)


def month_name(m):
    return f"{MONTH_NAMES[int(m[5:7]) - 1]} {m[:4]}"


MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]


def settled_lead(s):
    """True when a lead question may ask about the song. The list names the lead singers, and all are Beatles. A song
    with a helper singer beside the lead is left out. A solo song whose own article names other leads is left out,
    and a shared lead counts only when the article agrees."""
    names = lambda v: set(filter(None, v.split("+")))
    leads, article = names(s["lead_vocals"]), names(s.get("article_lead", ""))
    if s.get("with_vocals") or not leads or not leads <= set(BEATLES):
        return False
    return article == leads or (len(leads) == 1 and not article)


def pick(r, pool, k):
    return r.sample(pool, min(k, len(pool)))


def lettered(r, right, wrong):
    """Shuffle the right text among the wrong ones under labels a, b, c, ... and return (options, truth label)."""
    texts = [right] + list(wrong)
    r.shuffle(texts)
    opts = {chr(97 + i): t for i, t in enumerate(texts)}
    return opts, next(k for k, v in opts.items() if v == right)


class Bench:
    def __init__(self, data):
        data = Path(data)
        self.songs = read(data / "songs.tsv")
        self.albums = read(data / "albums.tsv")
        self.events = read(data / "events.tsv")
        self.links = read(data / "links.tsv")
        general = data / "reversal-general.tsv"
        self.general = read(general) if general.exists() else []
        self.core = [a for a in self.albums if a["release_date"][:4] <= "1970"]
        self.album = {a["album"]: a for a in self.albums}
        self.song = {s["title"]: s for s in self.songs}
        core = {a["album"] for a in self.core}
        self.studio = [s for s in self.songs if not s["first_release"].startswith("single") and s["first_album"] in core
                       and self.album[s["first_album"]]["release_date"][:4] == s["year"]]
        self.solo = [s for s in self.songs if settled_lead(s) and "+" not in s["lead_vocals"]]
        self.shared = [s for s in self.songs if settled_lead(s) and "+" in s["lead_vocals"]]
        self.dated = [s for s in self.songs if s["release_date"]]
        self.out = []
        self.hop = {}  # (kind, key) -> id of the single-hop question already asked

    def add(self, category, kind, function, question, input, options, truth, fields, **extra):
        n = sum(1 for q in self.out if q["category"] == category and q["kind"] == kind)
        q = {"id": f"{category}-{kind}-{n + 1:03d}", "category": category, "kind": kind, "function": function,
             "question": question, "input": input, "options": options, "truth": truth, "fields": fields, **extra}
        self.out.append(q)
        return q

    @staticmethod
    def f(song, *cols):
        return [["songs.tsv", song["title"], c, song[c]] for c in cols]

    def wrong_albums(self, r, s, k, avoid=()):
        """k core albums other than the song's own, none sharing a word with the title or released in the same year."""
        year = self.album[s["first_album"]]["release_date"][:4]
        pool = [a["album"] for a in self.core if a["release_date"][:4] != year and a["album"] not in avoid
                and not words(a["album"]) & words(s["title"])]
        return pick(r, pool, k)

    # --- forward: one fact about the song in hand -----------------------------------------
    def forward(self):
        r = rng("forward/singer")
        opts = {k: v for k, v in BEATLES.values()}
        for name in BEATLES:
            for s in pick(r, [s for s in self.solo if s["lead_vocals"] == name], 15):
                self.add("forward", "singer", "choose", f"{SONG} Who sings the lead vocal on it?", s["title"], opts,
                         BEATLES[name][0], self.f(s, "lead_vocals"))
        r = rng("forward/album")
        for s in pick(r, self.studio, 60):
            o, t = lettered(r, s["first_album"], self.wrong_albums(r, s, 3))
            self.add("forward", "album", "choose", f"{SONG} Which was the first album to include it?", s["title"], o, t,
                     self.f(s, "first_album"))
        r = rng("forward/songwriter")
        credit = lambda s: ({"Lennon–McCartney": "lennon-mccartney", "Harrison": "harrison", "Starkey": "starr"}.get(s["songwriters"])
                            or ("other" if s["cover"] == "yes" else None))
        for label in WRITERS:
            for s in pick(r, [s for s in self.songs if credit(s) == label], 15):
                self.add("forward", "songwriter", "choose", f"{SONG} Who is credited with writing it?", s["title"], WRITERS,
                         label, self.f(s, "songwriters", "cover"))
        r = rng("forward/year")
        years = {y: y for y in map(str, range(1962, 1971))}
        for s in pick(r, [s for s in self.songs if s["catalogue"] == "core 1962-1970"], 60):
            self.add("forward", "year", "choose", f"{SONG} In what year was it first released?", s["title"], years,
                     s["year"], self.f(s, "year"))

    # --- reverse: the answer is the song -------------------------------------------------
    def reverse(self):
        r = rng("reverse/singer-to-song")
        for name, (_, full) in BEATLES.items():
            for s in pick(r, [s for s in self.solo if s["lead_vocals"] == name], 10):
                wrong = [w["title"] for w in pick(r, [w for w in self.solo if w["lead_vocals"] != name], 3)]
                o, t = lettered(r, s["title"], wrong)
                self.add("reverse", "singer-to-song", "choose",
                         "The text names a member of the Beatles. Which of these songs by the Beatles has this member as its only lead singer?",
                         full, o, t, self.f(s, "lead_vocals"))
        r = rng("reverse/album-to-song")
        for s in pick(r, [s for s in self.studio if not words(s["title"]) & words(s["first_album"])], 40):
            pool = [w["title"] for w in self.studio if w["first_album"] != s["first_album"] and not words(w["title"]) & words(s["first_album"])]
            o, t = lettered(r, s["title"], pick(r, pool, 3))
            self.add("reverse", "album-to-song", "choose",
                     "The text names an album by the Beatles. Which of these songs did it include before any other album did?",
                     s["first_album"], o, t, self.f(s, "first_album"))
        r = rng("reverse/singer-yes-no")
        for name in ("Harrison", "Starr"):
            full = BEATLES[name][1]
            yes = pick(r, [s for s in self.solo if s["lead_vocals"] == name], 8)
            no = pick(r, [s for s in self.solo if s["lead_vocals"] != name], 8)
            for s in sorted(yes + no, key=lambda s: r.random()):
                self.add("reverse", "singer-yes-no", "decide", f"{SONG} Is {full} its only lead singer?", s["title"], None,
                         "yes" if s in yes else "no", self.f(s, "lead_vocals"))

    # --- multi-hop: two facts chained, each also asked alone ------------------------------------
    def single(self, kind, key, make):
        """The id of the single-hop question for key, asking it once."""
        if (kind, key) not in self.hop:
            self.hop[kind, key] = make()["id"]
        return self.hop[kind, key]

    def month_hop(self, r, kind, key, text, question, month, fields):
        near = [f"{y}-{m:02d}" for y in range(1961, 1972) for m in range(1, 13)]
        mon = lambda d: int(d[:4]) * 12 + int(d[5:7])
        wrong = [m for m in near if m != month and abs(mon(m) - mon(month)) <= 12]
        o, t = lettered(r, month_name(month), [month_name(m) for m in pick(r, wrong, 3)])
        return self.single(kind, key, lambda: self.add("single-hop", kind, "choose", question, text, o, t, fields))

    def song_month(self, r, s):
        return self.month_hop(r, "song-month", s["title"], s["title"], f"{SONG} In which month was it first released?",
                              s["release_date"][:7], self.f(s, "release_date"))

    def event_month(self, r, e):
        return self.month_hop(r, "event-month", e["event"], e["event"], "The text names an event. In which month did it happen?",
                              e["month"], [["events.tsv", e["month"], c, e[c]] for c in ("event", "date")])

    def multi_hop(self):
        r = rng("multi-hop/album-year")
        hr = rng("single-hop")
        years = {y: y for y in map(str, range(1963, 1971))}
        for s in pick(r, self.studio, 60):
            a = self.album[s["first_album"]]
            o, t = lettered(hr, s["first_album"], self.wrong_albums(hr, s, 3))
            hops = [self.single("song-album", s["title"], lambda: self.add(
                        "single-hop", "song-album", "choose", f"{SONG} Which was the first album to include it?", s["title"], o, t,
                        self.f(s, "first_album"))),
                    self.single("album-year", a["album"], lambda: self.add(
                        "single-hop", "album-year", "choose", "The text names an album by the Beatles. In what year was it first released?",
                        a["album"], years, a["release_date"][:4], [["albums.tsv", a["album"], "release_date", a["release_date"]]]))]
            self.add("multi-hop", "album-year", "choose", f"{SONG} In what year did the first album to include it come out?",
                     s["title"], years, a["release_date"][:4],
                     self.f(s, "first_album") + [["albums.tsv", a["album"], "release_date", a["release_date"]]], hops=hops)
        mon = lambda d: int(d[:4]) * 12 + int(d[5:7])
        ev = lambda e: [["events.tsv", e["month"], c, e[c]] for c in ("event", "date")]
        r = rng("multi-hop/before-after")
        pairs = {"before": [], "after": []}
        for e in self.events:
            near = [s for s in self.dated if 0 < abs(mon(s["release_date"]) - mon(e["date"])) <= 24]
            for side in pairs:
                pool = [s for s in near if (s["release_date"] < e["date"]) == (side == "before")]
                if pool:
                    pairs[side].append((e, r.choice(pool)))
        k = min(30, *map(len, pairs.values()))  # as many before as after
        chosen = pick(r, pairs["before"], k) + pick(r, pairs["after"], k)
        for e, s in sorted(chosen, key=lambda p: r.random()):
            self.add("multi-hop", "before-after", "choose", f"{SONG} Was it first released before or after this event: {e['event']}?",
                     s["title"], {"before": "first released before the event", "after": "first released after the event"},
                     "before" if s["release_date"] < e["date"] else "after", self.f(s, "release_date") + ev(e),
                     hops=[self.song_month(hr, s), self.event_month(hr, e)])
        r = rng("multi-hop/same-month")
        pairs = {"yes": [], "no": []}
        for e in self.events:
            yes = [s for s in self.dated if s["release_date"][:7] == e["month"]]
            no = [s for s in self.dated if 0 < abs(mon(s["release_date"]) - mon(e["date"])) <= 6]
            if yes:
                pairs["yes"].append((e, r.choice(yes)))
            if no:
                pairs["no"].append((e, r.choice(no)))
        k = min(30, *map(len, pairs.values()))
        chosen = pick(r, pairs["yes"], k) + pick(r, pairs["no"], k)
        for e, s in sorted(chosen, key=lambda p: r.random()):
            self.add("multi-hop", "same-month", "decide", f"{SONG} Was it first released in the same month as this event: {e['event']}?",
                     s["title"], None, "yes" if s["release_date"][:7] == e["month"] else "no", self.f(s, "release_date") + ev(e),
                     hops=[self.song_month(hr, s), self.event_month(hr, e)])

    # --- comparison ------------------------------------------------------------------------------
    def comparison(self):
        r = rng("comparison/longer")
        pool = [s for s in self.songs if s["length_s"] and s["catalogue"] == "core 1962-1970"]
        seen = set()
        while len(seen) < 60:
            a, b = r.sample(pool, 2)
            if abs(int(a["length_s"]) - int(b["length_s"])) < 30 or {(a["title"], b["title"]), (b["title"], a["title"])} & seen:
                continue
            seen.add((a["title"], b["title"]))
            longer = a if int(a["length_s"]) > int(b["length_s"]) else b
            self.add("comparison", "longer", "choose", "The text names two songs by the Beatles. Which one is longer?",
                     f"{a['title']} / {b['title']}", {"a": a["title"], "b": b["title"]}, "a" if longer is a else "b",
                     self.f(a, "length_s") + self.f(b, "length_s"))

    # --- shared lead, and the lead singers as a set ---------------------------------------------------
    def shared_lead(self):
        r = rng("shared-lead")
        k = min(30, len(self.shared))
        chosen = pick(r, self.shared, k) + pick(r, self.solo, k)
        for s in sorted(chosen, key=lambda s: r.random()):
            self.add("shared-lead", "shared-lead", "decide", f"{SONG} Do two or more Beatles share the lead vocal on it?",
                     s["title"], None, "yes" if "+" in s["lead_vocals"] else "no", self.f(s, "lead_vocals", "with_vocals"))

    def lead_set(self):
        """Each Beatle asked on his own, so the answer is the set of lead singers. Scored name by name and as a set."""
        r = rng("lead-set")
        chosen = pick(r, self.shared, 20) + pick(r, self.solo, 10)
        for i, s in enumerate(sorted(chosen, key=lambda s: r.random()), 1):
            for name, (key, full) in BEATLES.items():
                self.add("lead-set", key, "decide", f"{SONG} Does {full} sing a lead vocal on it?", s["title"], None,
                         "yes" if name in s["lead_vocals"].split("+") else "no", self.f(s, "lead_vocals", "with_vocals"),
                         group=f"lead-set-{i:03d}")

    # --- near neighbor: the wrong albums are the nearest in release date, and a control with far ones --------
    def near_neighbor(self):
        r = rng("near-neighbor")
        days = lambda d: int(d[:4]) * 372 + int(d[5:7]) * 31 + int(d[8:10])
        for s in pick(r, self.studio, 60):
            a = self.album[s["first_album"]]
            near = sorted((abs(days(b["release_date"]) - days(a["release_date"])), b["album"]) for b in self.core if b is not a)
            wrong = [n for _, n in near[:2]]
            o, t = lettered(r, a["album"], wrong)
            q = self.add("near-neighbor", "album", "choose", f"{SONG} Which was the first album to include it?", s["title"], o, t,
                         self.f(s, "first_album") + [["albums.tsv", n, "release_date", self.album[n]["release_date"]] for n in [a["album"]] + wrong])
            far = [n for _, n in near[2:]]
            o, t = lettered(r, a["album"], pick(r, far, 2))
            self.add("near-neighbor-control", "album", "choose", f"{SONG} Which was the first album to include it?", s["title"], o, t,
                     self.f(s, "first_album"), group=q["id"])

    # --- lexical trap: a wrong option shares a word with the question, the right one does not ----------
    def lexical_trap(self):
        r = rng("lexical-trap")
        found = {}  # (kind, what the question names) -> candidate questions
        for s in self.studio:  # the song's title matches a wrong album
            traps = [a["album"] for a in self.core if a["album"] != s["first_album"] and words(a["album"]) & words(s["title"])]
            if traps and not words(s["first_album"]) & words(s["title"]):
                found.setdefault(("song-to-album", s["title"]), []).append(("song-to-album", s, traps))
        for a in self.core:  # the album's name matches a song from another album
            traps = [w["title"] for w in self.studio if w["first_album"] != a["album"] and words(w["title"]) & words(a["album"])]
            for s in [s for s in self.studio if s["first_album"] == a["album"] and not words(s["title"]) & words(a["album"])] if traps else []:
                found.setdefault(("album-to-song", a["album"]), []).append(("album-to-song", s, traps))
        for e in self.events:  # the event's name matches a song from another month
            traps = [w["title"] for w in self.dated if w["release_date"][:7] != e["month"] and words(w["title"]) & words(e["event"])]
            for s in [s for s in self.dated if s["release_date"][:7] == e["month"] and not words(s["title"]) & words(e["event"])] if traps else []:
                found.setdefault(("event-to-song", e["month"]), []).append(("event-to-song", s, traps, e))
        found = [c for key in sorted(found, key=str) for c in pick(r, found[key], 6)]
        for kind, s, traps, *e in pick(r, found, 60):
            trap = r.choice(traps)
            if kind == "song-to-album":
                fill = [a["album"] for a in self.core if a["album"] not in (s["first_album"], trap) and not words(a["album"]) & words(s["title"])]
                args = ("song-to-album", f"{SONG} Which was the first album to include it?", s["title"], s["first_album"], self.f(s, "first_album"))
            elif kind == "album-to-song":
                a = s["first_album"]
                fill = [w["title"] for w in self.studio if w["first_album"] != a and w["title"] != trap and not words(w["title"]) & words(a)]
                args = ("album-to-song", "The text names an album by the Beatles. Which of these songs did it include before any other album did?", a,
                        s["title"], self.f(s, "first_album"))
            else:
                e = e[0]
                fill = [w["title"] for w in self.dated if w["release_date"][:7] != e["month"] and w["title"] != trap and not words(w["title"]) & words(e["event"])]
                args = ("event-to-song", "The text names an event. Which of these songs by the Beatles was first released in the same month?",
                        e["event"], s["title"], self.f(s, "release_date") + [["events.tsv", e["month"], "event", e["event"]]])
            kind, question, given, right, fields = args
            wrong = pick(r, fill, 3)  # two fill the trap question, and the third stands in for the trap in its control
            o, t = lettered(r, right, [trap] + wrong[:2])
            q = self.add("lexical-trap", kind, "choose", question, given, o, t, fields)
            q["_swap"] = (trap, wrong[2])

    def controls(self):
        """The lexical-trap control: the same question with the trap swapped for a neutral option in the same place."""
        for q in [q for q in self.out if "_swap" in q]:
            trap, neutral = q.pop("_swap")
            opts = {k: neutral if v == trap else v for k, v in q["options"].items()}
            self.add("lexical-trap-control", q["kind"], "choose", q["question"], q["input"], opts, q["truth"], q["fields"],
                     group=q["id"])

    # --- none of these: a legal answer, right for half the questions ------------------------------------
    def none_of_these(self):
        r = rng("none-of-these")
        for i, s in enumerate(pick(r, self.studio, 60)):
            absent = i % 2 == 0
            wrong = self.wrong_albums(r, s, 3 if absent else 2)
            if absent:
                o = {chr(97 + j): a for j, a in enumerate(wrong)}
                t = "none"
            else:
                o, t = lettered(r, s["first_album"], wrong)
            o["none"] = NONE
            self.add("none-of-these", "absent" if absent else "present", "choose",
                     f"{SONG} Which was the first album to include it?", s["title"], o, t, self.f(s, "first_album"))

    # --- reversal: a pair asked from the famous end and from the obscure end ----------------------------
    def reversal(self):
        r = rng("reversal")
        rows = self.links
        credit = {l["song"]: l.get("credit") or self.song[l["song"]]["songwriters"] for l in rows}
        chosen = []
        for key in sorted({(l["relation"], l["other_article"]) for l in rows}):
            chosen += pick(r, [l for l in rows if (l["relation"], l["other_article"]) == key], 5)
        for l in chosen:
            same = [x for x in rows if x["relation"] == l["relation"]]
            composer = l["relation"] == "composer"
            clash = lambda song, other: composer and bool(surnames(credit[song]) & surnames(display(other)))  # both true by the credit
            from_other, from_song = RELATION[l["relation"]]
            songs = sorted({x["song"] for x in same} - {x["song"] for x in same if x["other_article"] == l["other_article"]}
                           - {x["song"] for x in same if clash(x["song"], l["other_article"])})
            others = sorted({x["other_article"] for x in same} - {x["other_article"] for x in same if x["song"] == l["song"]}
                            - {x["other_article"] for x in same if clash(l["song"], x["other_article"])})
            fields = [["links.tsv", l["song"], c, l[c]] for c in ("relation", "other_article", "song_views_2024", "other_views_2024", "famous")]
            asks = {"other": (from_other, l["other_article"], l["song"], songs), "song": (f"{SONG} {from_song}", l["song"], l["other_article"], others)}
            for kind, side in (("forward", l["famous"]), ("reverse", "song" if l["famous"] == "other" else "other")):
                question, given, right, pool = asks[side]
                if pool:
                    o, t = lettered(r, right, pick(r, pool, 3))
                    self.add("reversal", kind, "choose", question, given, o, t, fields)

    def reversal_general(self):
        """Pairs outside the Beatles, asked from the famous end (forward) and the obscure end (reverse). A pair whose
        ends share a name by related() goes to the shared-name control instead. A wrong option that shares a name with
        the asked name is always offered when the data holds one."""
        r = rng("reversal-general")
        for rel in sorted({g["relation"] for g in self.general}):
            same = [g for g in self.general if g["relation"] == rel]
            used, chosen = set(), {"reversal-general": [], "reversal-general-shared-name": []}
            for g in r.sample(same, len(same)):
                cat = "reversal-general-shared-name" if related(g["famous"], g["obscure"]) else "reversal-general"
                if len(chosen[cat]) < (20 if cat == "reversal-general" else 10) and not {g["famous"], g["obscure"]} & used:
                    used |= {g["famous"], g["obscure"]}
                    chosen[cat].append(g)
            fwd, rev = GENERAL[rel]
            for cat, gs in chosen.items():
                for g in gs:
                    fields = [["reversal-general.tsv", g["famous"], c, g[c]] for c in ("relation", "obscure", "famous_views_2024", "obscure_views_2024")]
                    for kind, question, given, right, end, skip in (
                            ("forward", fwd, g["famous"], g["obscure"], "obscure", g["not_forward"]),
                            ("reverse", rev, g["obscure"], g["famous"], "famous", g["not_reverse"])):
                        bad = {right, given, *filter(None, skip.split(";"))}
                        pool = sorted({x[end] for x in same} - bad)
                        traps = [x for x in pool if related(x, given)]
                        trap = [r.choice(traps)] if traps else []
                        o, t = lettered(r, right, trap + pick(r, [x for x in pool if x not in trap and not related(x, right)], 3 - len(trap)))
                        self.add(cat, kind, "choose", question, given, o, t, fields)


def balance(questions):
    """Move the right option of every lettered choose question (options a, b, c, ...; comparison keeps the input's
    order) so the right letter falls evenly across the letters within each category, kind, and option count. The
    wrong options keep their drawn order, and a "none" option stays last. A control keeps its question's letters."""
    r = rng("balance")
    lettered_ = lambda q: [k for k in (q["options"] or {}) if k != "none"]
    groups = {}
    for q in questions:
        ks = lettered_(q)
        if (q["function"] == "choose" and q["category"] not in ("comparison", "lexical-trap-control") and q["truth"] in ks
                and ks == [chr(97 + i) for i in range(len(ks))]):
            groups.setdefault((q["category"], q["kind"], len(ks)), []).append(q)
    for (_, _, k), g in sorted(groups.items()):
        slots = [i % k for i in range(len(g))]
        r.shuffle(slots)
        for q, slot in zip(g, slots):
            texts = [q["options"][c] for c in lettered_(q) if c != q["truth"]]
            texts.insert(slot, q["options"][q["truth"]])
            opts = {chr(97 + i): t for i, t in enumerate(texts)}
            if "none" in q["options"]:
                opts["none"] = q["options"]["none"]
            q["options"], q["truth"] = opts, chr(97 + slot)


def generate(data):
    b = Bench(data)
    for step in (b.forward, b.reverse, b.multi_hop, b.comparison, b.shared_lead, b.lead_set, b.near_neighbor,
                 b.lexical_trap, b.none_of_these, b.reversal, b.reversal_general):
        step()
    balance(b.out)
    b.controls()
    return b.out


def main(argv):
    data, out = (Path(a) for a in argv) if argv else (ROOT / "data", ROOT / "questions")
    out.mkdir(parents=True, exist_ok=True)
    qs = generate(data)
    for c in CATEGORIES:
        rows = [q for q in qs if q["category"] == c]
        if rows:
            with open(out / f"{c}.jsonl", "w", encoding="utf-8") as f:
                f.writelines(json.dumps(q, ensure_ascii=False) + "\n" for q in rows)
            (out / "keys").mkdir(exist_ok=True)
            with open(out / "keys" / f"{c}.jsonl", "w", encoding="utf-8") as f:
                f.writelines(json.dumps({"id": q["id"], "value": q["truth"]}) + "\n" for q in rows)
    print("\n".join(f"{c}\t{sum(q['category'] == c for q in qs)}" for c in CATEGORIES), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
