#!/usr/bin/env python3
"""Turn data/ into questions/suite/: one test per ThinkThen function beyond choose and decide. Deterministic.

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
names as [start, end, kind, name], in characters with the end exclusive, as the command prints them. relate asks
`thinkthen relate` once over the whole entity set: every song, the four Beatles, and the core albums. Its truth holds
the edges, and skip lists the songs whose sung_by edges are not scored. relate-profile.json caps each request at
96,000 bytes, the ceiling thinkthen main applies to relation requests at its built-in address.
"""
import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import SONG, settled_lead, words  # noqa: E402

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
RECOGNIZE = ["song", "person", "album", "--jsonl", "--field", "/input"]
# relate: one choice per song over the people, and one over the albums. The relations are the function folder's, less
# its threshold of 0.01. The case passes --threshold 0.5.
RELATE = {"version": 1, "relate": json.loads((ROOT / "examples" / "relate" / "relate.json").read_text(encoding="utf-8"))["relate"]}
PROFILE = {"schema": "thinkthen.backend-profile/1", "name": "request-96000", "max_request_bytes": 96000}


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


class Suite:
    def __init__(self, data):
        self.albums = [a for a in read(data / "albums.tsv")]
        core = {a["album"] for a in self.albums if a["release_date"][:4] <= "1970"}
        self.core = [a["album"] for a in self.albums if a["album"] in core]
        self.songs = [s for s in read(data / "songs.tsv") if s["catalogue"] == "core 1962-1970" and s["first_album"] in core
                      and all(x in LEADS for x in s["lead_vocals"].split("+"))]
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

    def find(self):
        cases = []
        for album in self.core:
            r = rng(f"find/{album}")
            fair = [s for s in self.songs if not words(s["title"]) & words(album)]
            own = [s for s in fair if s["first_album"] == album]
            for n, target in enumerate(r.sample(own, min(4, len(own))), 1):
                others = r.sample([a for a in self.core if a != album], 7)
                units = [target] + [r.choice([s for s in fair if s["first_album"] == o]) for o in others]
                r.shuffle(units)
                cid = f"find-album-{self.core.index(album) + 1:02d}-{n}"
                records = [{"id": f"u{i}", "input": s["title"]} for i, s in enumerate(units, 1)]
                cases.append({"id": cid, "function": "find", "test": "album", "args": [FIND_Q.format(album=album)] + JSONL,
                              "records": records, "truth": f"u{units.index(target) + 1}", "key": album,
                              "fields": [x for s in units for x in f(s, "first_album")]})
        self.out["find"] = cases

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
            cases.append({"id": sid, "function": "recognize", "test": "names", "args": RECOGNIZE,
                          "records": [{"id": sid, "input": text}], "truth": names,
                          "fields": f(s, "title") + f(s, "lead_vocals") + f(s, "first_album") + f(s, "year")})
        self.out["recognize"] = cases

    def relate(self):
        self.qsets["relate-suite.json"] = RELATE
        self.qsets["relate-profile.json"] = PROFILE
        ents = [(s["title"], "song") for s in self.songs] + [(v, "person") for v in FULL.values()] + [(a, "album") for a in self.core]
        truth = [["sung_by", s["title"], FULL[x]] for s in self.songs if settled_lead(s) for x in self.leads(s)]
        truth += [["appears_on", s["title"], s["first_album"]] for s in self.songs]
        self.out["relate"] = [{"id": "relate-songs", "function": "relate", "test": "songs",
                               "args": ["@relate-suite.json", "--profile", "relate-profile.json", "--threshold", "0.5", "--jsonl", "--timeout", "180"],
                               "records": [{"name": n, "kind": k} for n, k in ents], "truth": truth,
                               "skip": [s["title"] for s in self.songs if not settled_lead(s)],
                               "fields": [x for s in self.songs for x in f(s, "lead_vocals", "first_album")]}]


def main(data=ROOT / "data", out=ROOT / "questions" / "suite"):
    data, out = Path(data), Path(out)
    suite = Suite(data)
    suite.qsets = {}
    for name in FUNCTIONS:
        getattr(suite, name)()
    out.mkdir(parents=True, exist_ok=True)
    for name, cases in suite.out.items():
        with open(out / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            fh.writelines(json.dumps(c, ensure_ascii=False) + "\n" for c in cases)
    for name, qset in suite.qsets.items():
        (out / name).write_text(json.dumps(qset, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
