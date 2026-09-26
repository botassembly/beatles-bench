#!/usr/bin/env python3
"""Harvest Beatles facts into data/ from pinned Wikipedia revisions, Wikipedia page views, and Wikidata.

usage: harvest.py [--offline] [RAW PINS OUT]
  Default paths: data/raw/ (the page cache, never committed), data/pins/, data/.
  Online, it fetches what the cache lacks: each page at its pinned revision (pinning the current one for a page
  not yet pinned), redirect targets, page views, and the Wikidata query. New pins are written to PINS.
  --offline reads only RAW and PINS and fails on anything missing. Both modes build OUT the same way.
"""
import csv
import html as htmllib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from wikitext import MONTHS, balanced, cell_text, clean, dates, infobox_field, links, strip_refs, table_rows

ROOT = Path(__file__).resolve().parents[2]
UA = "beatles-bench/0.1 (https://github.com/botassembly/beatles-bench)"
WINDOW = ("20240101", "20241231")  # page views: all of 2024, all access, users only
EVENT_YEARS = [str(y) for y in range(1962, 1971)]  # the year articles events come from
NOT_EVENT = re.compile(r"\b(country|sovereign state|organi[sz]ation|company|political party|person|treaty|currency|law)\b", re.I)  # on title + description
FREE = re.compile(r"^(pd|cc0|cc-by-\d|cc-by-sa-\d)", re.I)  # Commons license codes kept: public domain, CC0, CC BY, CC BY-SA
EXTRA = [("Elvis Presley meets Richard Nixon", "Elvis-nixon.jpg")]  # photo rows outside the release months, never asked
FAME_RATIO = 10  # a reversal pair keeps only when one end has this many times the other's views
LIST = "List of songs recorded by the Beatles"
ALBUMS = {  # release name in the list -> album article
    "Please Please Me": "Please Please Me",
    "With the Beatles": "With the Beatles",
    "A Hard Day's Night": "A Hard Day's Night (album)",
    "Beatles for Sale": "Beatles for Sale",
    "Help!": "Help!",
    "Rubber Soul": "Rubber Soul",
    "Revolver": "Revolver (Beatles album)",
    "Sgt. Pepper's Lonely Hearts Club Band": "Sgt. Pepper's Lonely Hearts Club Band",
    "Magical Mystery Tour": "Magical Mystery Tour",
    "The Beatles (White Album)": "The Beatles (album)",
    "Yellow Submarine": "Yellow Submarine (album)",
    "Abbey Road": "Abbey Road",
    "Let It Be": "Let It Be (album)",
    "Past Masters": "Past Masters",
    "Anthology 1": "Anthology 1",
    "Anthology 2": "Anthology 2",
    "Anthology 3": "Anthology 3",
    "Anthology 4": "Anthology 4",
    "Live at the BBC": "Live at the BBC (Beatles album)",
    "On Air – Live at the BBC Volume 2": "On Air – Live at the BBC Volume 2",
}
OCCURRENCE_QUERY = """SELECT ?title ?occ ?desc ?time ?precision WHERE {
  VALUES ?title { %s }
  ?a schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> ; schema:name ?title .
  OPTIONAL { ?item wdt:P31 ?c . ?c wdt:P279* wd:Q1190554 . hint:Prior hint:gearing "forward" . BIND(true AS ?occ) }
  OPTIONAL { ?item schema:description ?desc . FILTER(LANG(?desc) = "en") }
  OPTIONAL { { ?item p:P585/psv:P585 ?v } UNION { ?item p:P580/psv:P580 ?v } UNION { ?item p:P619/psv:P619 ?v }
             ?v wikibase:timeValue ?time ; wikibase:timePrecision ?precision . }
}"""
PAIR = "Lennon–McCartney"  # the published credit the pair shares; its Wikipedia article answers for both
ALIAS = {"starr": "starkey"}  # Wikidata names Ringo Starr, and the published credit names Richard Starkey
RELATIONS = {"P921": "main subject", "P138": "named after", "P162": "producer", "P86": "composer",
             "P483": "recorded at", "P737": "influenced by"}


IMAGE_QUERY = """SELECT ?title ?img WHERE {
  VALUES ?title { %s }
  ?a schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> ; schema:name ?title .
  ?item wdt:P18 ?img .
}"""


def plain(html):
    """Text of an extmetadata value: tags dropped, entities decoded, whitespace collapsed."""
    return " ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", str(html))).split())


def get(url, data=None):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** attempt)
        except OSError:
            time.sleep(2 ** attempt)
    sys.exit(f"harvest: {url} failed five times")


def read_tsv(path):
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {r[0]: r[1] for r in list(csv.reader(f, delimiter="\t"))[1:]}


def write_tsv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            vals = [str(v) for v in row]
            assert not any("\t" in v or "\n" in v for v in vals), vals
            f.write("\t".join(vals) + "\n")


class Source:
    """Pinned inputs. Offline it reads RAW and PINS only. Online it fills what is missing and pins it."""

    def __init__(self, raw, pins, online):
        self.raw, self.pins, self.online = Path(raw), Path(pins), online
        self.revids = read_tsv(self.pins / "pages.tsv")
        self.targets = read_tsv(self.pins / "redirects.tsv")
        self.views = {k: int(v) for k, v in read_tsv(self.pins / "pageviews.tsv").items()}

    def need(self, what):
        if not self.online:
            sys.exit(f"harvest: offline and {what} is missing")

    def save(self):
        self.pins.mkdir(parents=True, exist_ok=True)
        write_tsv(self.pins / "pages.tsv", ["title", "revid"], sorted(self.revids.items()))
        write_tsv(self.pins / "redirects.tsv", ["link", "target"], sorted(self.targets.items()))
        write_tsv(self.pins / "pageviews.tsv", ["article", "views"], sorted(self.views.items()))

    def page(self, title):
        """Wikitext of a page at its pinned revision."""
        title = self.resolve([title])[title]
        if title not in self.revids:
            self.need(f"the pin for {title}")
            q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "ids", "titles": title,
                                        "format": "json", "formatversion": "2"})
            self.revids[title] = str(json.loads(get("https://en.wikipedia.org/w/api.php?" + q))["query"]["pages"][0]["revisions"][0]["revid"])
        path = self.raw / f"{self.revids[title]}.wiki"
        if not path.exists():
            self.need(f"raw/{path.name} ({title})")
            self.raw.mkdir(parents=True, exist_ok=True)
            path.write_bytes(get(f"https://en.wikipedia.org/w/index.php?oldid={self.revids[title]}&action=raw"))
            time.sleep(1)
        return path.read_text(encoding="utf-8")

    def resolve(self, titles):
        """Map each link title to the article it lands on, following redirects."""
        missing = sorted({t for t in titles if t not in self.targets})
        if missing:
            self.need(f"redirect pins for {missing[:3]}")
        for i in range(0, len(missing), 50):
            q = urllib.parse.urlencode({"action": "query", "titles": "|".join(missing[i:i + 50]), "redirects": "1",
                                        "format": "json", "formatversion": "2"})
            d = json.loads(get("https://en.wikipedia.org/w/api.php?" + q))["query"]
            hop = {n["from"]: n["to"] for n in d.get("normalized", [])}
            red = {r["from"]: r["to"] for r in d.get("redirects", [])}
            exists = {p["title"] for p in d["pages"] if not p.get("missing") and not p.get("invalid")}
            for t in missing[i:i + 50]:
                n = hop.get(t, t)
                n = red.get(n, n)
                self.targets[t] = n if n in exists else ""
        return {t: self.targets[t] for t in titles}

    def pageviews(self, article):
        if article not in self.views:
            self.need(f"page views for {article}")
            a = urllib.parse.quote(article.replace(" ", "_"), safe="")
            body = get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{a}/monthly/{WINDOW[0]}/{WINDOW[1]}")
            self.views[article] = sum(i["views"] for i in json.loads(body)["items"]) if body else 0
            time.sleep(0.05)
        return self.views[article]

    def parents(self):
        """Actor-parent pairs from scripts/harvest/parents.rq, with each end's English Wikipedia title."""
        path = self.pins / "parents.tsv"
        if not path.exists():
            self.need("pins/parents.tsv")
            q = urllib.parse.urlencode({"query": (ROOT / "scripts" / "harvest" / "parents.rq").read_text(), "format": "json"})
            rows = json.loads(get("https://query.wikidata.org/sparql?" + q))["results"]["bindings"]
            qid = lambda r, k: r[k]["value"].rsplit("/", 1)[1]
            trip = sorted({(qid(r, "child"), qid(r, "prop"), qid(r, "parent")) for r in rows})
            ids = sorted({c for c, _, _ in trip} | {p for _, _, p in trip})
            title = {}
            for i in range(0, len(ids), 50):
                q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids[i:i + 50]), "props": "sitelinks",
                                            "sitefilter": "enwiki", "format": "json"})
                for k, e in json.loads(get("https://www.wikidata.org/w/api.php?" + q))["entities"].items():
                    if "enwiki" in e.get("sitelinks", {}):
                        title[k] = e["sitelinks"]["enwiki"]["title"]
                time.sleep(0.5)
            write_tsv(path, ["child_item", "child_title", "property", "parent_item", "parent_title"],
                      [(c, title[c], p, a, title[a]) for c, p, a in trip if c in title and a in title])
            (self.pins / "parents-date.txt").write_text(time.strftime("%Y-%m-%d\n", time.gmtime()))
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))

    def excluded(self, kind):
        """Names data/pins/excluded.tsv drops, each with the reason a source check gave."""
        path = self.pins / "excluded.tsv"
        return {r["name"] for r in self.pinned("excluded.tsv") if r["kind"] == kind} if path.exists() else set()

    def pinned(self, name):
        with open(self.pins / name, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))

    def occurrences(self, articles):
        """For each article: whether its Wikidata item is an instance of a subclass of occurrence (Q1190554),
        its English description, and the months (YYYY-MM) its point in time (P585), start time (P580), or launch date
        (P619, the date a spaceflight carries) gives
        at month precision or finer."""
        path = self.pins / "wikidata-events.tsv"
        have = {}
        if path.exists():
            with open(path, encoding="utf-8", newline="") as f:
                have = {r["article"]: r for r in csv.DictReader(f, delimiter="\t")}
        missing = [a for a in articles if a not in have]
        if missing:
            self.need(f"Wikidata event facts for {missing[:3]}")
        for i in range(0, len(missing), 25):
            chunk = missing[i:i + 25]
            q = OCCURRENCE_QUERY % " ".join(json.dumps(a) + "@en" for a in chunk)
            body = urllib.parse.urlencode({"query": q, "format": "json"}).encode()
            rows = json.loads(get("https://query.wikidata.org/sparql", body))["results"]["bindings"]
            got = {a: {"article": a, "occurrence": "no", "description": "", "months": set()} for a in chunk}
            for r in rows:
                g = got[r["title"]["value"]]
                if r.get("occ", {}).get("value") == "true":
                    g["occurrence"] = "yes"
                g["description"] = r.get("desc", {}).get("value", "").replace("\t", " ").replace("\n", " ")
                if "time" in r and int(r["precision"]["value"]) >= 10:
                    g["months"].add(r["time"]["value"].lstrip("+")[:7])
            for a in chunk:
                have[a] = dict(got[a], months=";".join(sorted(got[a]["months"])))
            time.sleep(1)
            print(f"wikidata events {i + len(chunk)}/{len(missing)}", file=sys.stderr)
            write_tsv(path, ["article", "occurrence", "description", "months"],
                      [(r["article"], r["occurrence"], r["description"], r["months"]) for r in sorted(have.values(), key=lambda r: r["article"])])
        return {a: dict(have[a], months=have[a]["months"].split(";") if have[a]["months"] else []) for a in articles}

    def images(self, articles):
        """For each article, the Commons file its Wikidata item names as image (P18), or "" when it names none.
        An item with several images gives the first by file name."""
        path = self.pins / "wikidata-images.tsv"
        have = read_tsv(path)
        missing = [a for a in articles if a not in have]
        if missing:
            self.need(f"Wikidata images for {missing[:3]}")
        for i in range(0, len(missing), 50):
            chunk = missing[i:i + 50]
            q = IMAGE_QUERY % " ".join(json.dumps(a) + "@en" for a in chunk)
            rows = json.loads(get("https://query.wikidata.org/sparql", urllib.parse.urlencode({"query": q, "format": "json"}).encode()))
            got = {a: [] for a in chunk}
            for r in rows["results"]["bindings"]:
                got[r["title"]["value"]].append(urllib.parse.unquote(r["img"]["value"].rsplit("/", 1)[1]))
            have.update({a: min(got[a], default="") for a in chunk})
            time.sleep(1)
            write_tsv(path, ["article", "image"], sorted(have.items()))
        return {a: have[a] for a in articles}

    def commons(self, files):
        """For each Commons file: its license code and name, author, description page, and original date,
        from the Commons API's extmetadata."""
        path = self.pins / "commons.tsv"
        cols = ["file", "license_code", "license", "author", "link", "date"]
        have = {}
        if path.exists():
            with open(path, encoding="utf-8", newline="") as f:
                have = {r["file"]: r for r in csv.DictReader(f, delimiter="\t")}
        missing = [f for f in files if f not in have]
        if missing:
            self.need(f"Commons metadata for {missing[:3]}")
        for i in range(0, len(missing), 50):
            chunk = missing[i:i + 50]
            q = urllib.parse.urlencode({"action": "query", "prop": "imageinfo", "iiprop": "extmetadata|url",
                                        "titles": "|".join("File:" + f for f in chunk), "format": "json", "formatversion": "2"})
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q))["query"]
            back = {n["to"]: n["from"] for n in d.get("normalized", [])}
            for p in d["pages"]:
                name = back.get(p["title"], p["title"]).removeprefix("File:")
                info = (p.get("imageinfo") or [{}])[0]
                m = {k: plain(v.get("value", "")) for k, v in info.get("extmetadata", {}).items()}
                have[name] = {"file": name, "license_code": m.get("License", ""), "license": m.get("LicenseShortName", ""),
                              "author": m.get("Artist", ""), "link": info.get("descriptionurl", ""),
                              "date": m.get("DateTimeOriginal", "")[:10]}
            time.sleep(1)
            write_tsv(path, cols, [[r[c] for c in cols] for _, r in sorted(have.items())])
        return {f: have[f] for f in files}

    def event_dates(self, articles):
        """For each article: [(property, YYYY-MM-DD, precision)] for its Wikidata point in time (P585), start time
        (P580), end time (P582), and launch date (P619). Precision 11 is a day, 10 a month, 9 a year."""
        path = self.pins / "wikidata-event-dates.tsv"
        have = {}
        if path.exists():
            with open(path, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f, delimiter="\t"):
                    have.setdefault(r["article"], [])
                    if r["property"]:
                        have[r["article"]].append((r["property"], r["time"], int(r["precision"])))
        missing = [a for a in articles if a not in have]
        if missing:
            self.need(f"Wikidata event dates for {missing[:3]}")
        for i in range(0, len(missing), 50):  # the Wikidata API by English Wikipedia title, 50 at a time
            chunk = missing[i:i + 50]
            q = urllib.parse.urlencode({"action": "wbgetentities", "sites": "enwiki", "titles": "|".join(chunk),
                                        "props": "claims|sitelinks", "sitefilter": "enwiki", "format": "json"})
            got = {a: set() for a in chunk}
            for e in json.loads(get("https://www.wikidata.org/w/api.php?" + q))["entities"].values():
                title = e.get("sitelinks", {}).get("enwiki", {}).get("title")
                for prop in ("P585", "P580", "P582", "P619") if title in got else ():
                    for c in e.get("claims", {}).get(prop, []):
                        v = c["mainsnak"].get("datavalue", {}).get("value")
                        if v and c.get("rank") != "deprecated":
                            got[title].add((prop, v["time"].lstrip("+")[:10], int(v["precision"])))
            have.update({a: sorted(got[a]) for a in chunk})
            time.sleep(0.5)
            print(f"wikidata event dates {i + len(chunk)}/{len(missing)}", file=sys.stderr)
            write_tsv(path, ["article", "property", "time", "precision"],
                      sorted([(a, *d) for a in have for d in have[a]] + [(a, "", "", "") for a in have if not have[a]]))
        return {a: have[a] for a in articles}

    def wikidata(self):
        path = self.pins / "wikidata.tsv"
        if not path.exists():
            self.need("pins/wikidata.tsv")
            q = urllib.parse.urlencode({"query": (ROOT / "scripts" / "harvest" / "wikidata.rq").read_text(), "format": "json"})
            rows = json.loads(get("https://query.wikidata.org/sparql?" + q))["results"]["bindings"]
            val = lambda r, k: r[k]["value"] if k in r else ""
            out = sorted({(val(r, "songArticle"), val(r, "prop").rsplit("/", 1)[1], val(r, "otherArticle"), val(r, "other").rsplit("/", 1)[1])
                          for r in rows})
            write_tsv(path, ["song_article", "property", "other_article", "other_item"], out)
            (self.pins / "wikidata-date.txt").write_text(time.strftime("%Y-%m-%d\n", time.gmtime()))
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter="\t"))


# --- the list of songs -------------------------------------------------------

def parse_list(text):
    """The two released-song tables: Main songs (core 1962-1970) and Other released songs (later releases)."""
    def section(name, nxt):
        s = text[text.index("==" + name + "=="):text.index("==" + nxt + "==")]
        return s[s.index("sticky-header-multi"):]

    out = []
    for kind, tab in (("main", section("Main songs", "Other released songs")),
                      ("other", section("Other released songs", "Film/documentary songs"))):
        for cells in table_rows(tab):
            if not cells[0].startswith("!"):
                continue
            _, title_raw = cell_text(cells[0])
            vals = [clean(cell_text(c)[1]) for c in cells[1:]]
            attrs = [cell_text(c)[0] for c in cells[1:]]
            title = re.sub(r"\s*;\s*\(.*$", "", clean(title_raw).replace('"', "").strip())
            row = {"title": title, "link": (links(title_raw) or [title])[0], "table": kind,
                   "nonalbum_single": "hash-tag" in cells[0].lower(), "cover": any("CCFFFF" in a for a in attrs),
                   "release": vals[0], "writers": vals[1], "vocals": vals[2], "noted": noted(cell_text(cells[3])[1]), "year": vals[3] if kind == "main" else vals[4]}
            out.append(row)
    return out


def first_release(r):
    rel = r["release"]
    albums = [a.strip().replace('("White Album")', "(White Album)") for a in rel.split(";")
              if a.strip() and not a.strip().startswith("(")]
    side = re.search(r'\((A-side of|B-side of|Double A-side with) "([^"]+)"', rel)
    if r["table"] == "main" and r["nonalbum_single"]:
        return (f'single: {side.group(1)} "{side.group(2)}"' if side else "single"), albums
    return (albums[0] if albums else rel), albums


def noted(cell):
    """The singers in a vocals cell whose name carries a footnote ({{efn}}), such as McCartney on Cry Baby Cry:
    "'Can You Take Me Back?' section only". A footnoted singer sings a part, so he is a helper, not a lead."""
    out = []
    for part in re.split(r"<br\s*/?>", cell):
        if re.search(r"\{\{\s*efn", part, flags=re.I):
            out.append(clean(re.sub(r"\{\{\s*efn.*", "", part, flags=re.I | re.S)).strip(" ,;").removeprefix("and ").strip())
    return [n for n in out if n]


PERSON = {"John Lennon": "Lennon", "Paul McCartney": "McCartney", "George Harrison": "Harrison", "Ringo Starr": "Starr"}


def personnel_leads(text):
    """The Beatles the Personnel section of a song's own article names on lead vocal, joined by + in list order, or ""
    when the article has no Personnel section or names no lead. A role counts as lead when it holds "vocal" and no
    backing, harmony, falsetto, additional, spoken, shouted, chorus, or ad-lib part, or when it says "lead vocal" not
    after "backing" or "harmony". Follows the audit rule of a local experiment."""
    m = re.search(r"==+\s*Personnel\s*==+(.*?)(\n==[^=]|\Z)", text, flags=re.S | re.I)
    if not m:
        return ""

    def lead(seg):
        t = re.sub(r"\[\[[^]|]*\|([^]]*)\]\]", r"\1", seg)
        t = re.sub(r"\[\[|\]\]|\{\{[^}]*\}\}|&ndash;|&nbsp;", " ", t).lower().strip(" –-:")
        if "vocal" not in t or re.search(r"backing|harmony|falsetto|additional|spoken|shout|chorus|ad-lib|ad lib", t):
            return "lead" in t and "vocal" in t and not re.search(r"backing|harmony", t.split("lead")[0][-15:])
        return True

    leads = []
    for line in m.group(1).splitlines():
        for full, short in PERSON.items():
            if re.match(r"\*\s*(\[\[)?" + full, line) and any(lead(g) for g in re.split(r",|;| and ", line.split(full, 1)[1])):
                leads.append(short)
    order = ["Lennon", "McCartney", "Harrison", "Starr"]
    return "+".join(sorted(set(leads), key=order.index))


def helpers(v):
    """The singers the list marks "with" beside the lead, joined by +: "Lennon (with McCartney)" gives McCartney."""
    m = re.search(r"\(with (.*?)\)", v)
    names = [re.sub(r"^and ", "", n.strip(" ,")) for n in re.split(r";|,| and ", m.group(1))] if m else []
    return "+".join(n for n in names if n)


def clean_lead(v):
    """Main lead singer(s) joined by +, dropping (with ...) helpers."""
    if v == "Instrumental":
        return "instrumental"
    if v in ("Sound Collage", "–", ""):
        return "none"
    v = re.sub(r"\(with .*$", "", v)
    names = [re.sub(r"^and ", "", n.strip(" ,")) for n in re.split(r";|,", v)]
    return "+".join(n for n in names if n)


# --- album pages ---------------------------------------------------------------

def track_lengths(text):
    """(title, seconds) from every {{Track listing}} template of a page, in page order."""
    out = []
    for m in re.finditer(r"\{\{\s*track ?list(ing)?", text, flags=re.I):
        t = text[m.start():balanced(text, m.start())]
        f = {}
        for g in re.finditer(r"\|\s*(title|length)(\d+)\s*=\s*(.*?)(?=\n\s*\||\n\}\}|\}\}\s*$)", t, flags=re.S):
            f.setdefault(int(g.group(2)), {})[g.group(1)] = g.group(3).strip()
        for n, d in sorted(f.items()):
            s = re.match(r"^(\d+):(\d\d)$", clean(d.get("length", "")))
            if "title" in d and s:
                out.append((clean(d["title"]).strip('"'), int(s.group(1)) * 60 + int(s.group(2))))
    return out


def norm(t):
    t = t.lower().replace("&", "and").replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def base(t):
    return norm(re.sub(r"\s*[\(\[].*?[\)\]]", "", t))


def release_date(text):
    """The earliest full date in the infobox's released field."""
    d = dates(infobox_field(text, "released"))
    return min(d) if d else ""


def song_date(text):
    """The earliest full date, in any country, in the released field of the page's first song or single infobox whose
    artist is the Beatles. A song page may open with another artist's recording, as I Wanna Be Your Man does."""
    for m in re.finditer(r"\{\{\s*Infobox (song|single)\b", text, flags=re.I):
        box = text[m.start():balanced(text, m.start())]
        if re.search(r"the Beatles", infobox_field(box, "artist"), flags=re.I):
            return release_date(box)
    return ""


# --- year articles -------------------------------------------------------------

def year_events(text, year):
    """Every dated event line in a year article's Events section, as (YYYY-MM-DD, [link targets in order])."""
    m = re.search(r"^==\s*Events\s*==\s*$", text, flags=re.M)
    body = text[m.end():]
    nxt = re.search(r"^==[^=].*$", body, flags=re.M)
    body = strip_refs(body[:nxt.start()] if nxt else body)
    mon = "|".join(MONTHS)
    skip = re.compile(r"^((" + mon + r") \d{1,2}|\d{1,4}( BC)?|(" + mon + r") \d{4}|(File|Image|Category|Wikipedia|Wikt|Wiktionary|Template|Help):.*)$", re.I)
    lines, date = [], None
    for line in body.split("\n"):
        top = re.match(r"^\*(?!\*)\s*\[\[(" + mon + r") (\d{1,2})\]\](.*)$", line)
        if top:
            date = f"{year}-{MONTHS.index(top.group(1)) + 1:02d}-{int(top.group(2)):02d}"
            rest = re.sub(r"^\s*(?:[–—-]|&ndash;|&mdash;)\s*\[\[(" + mon + r") \d{1,2}(\|[^\]]*)?\]\]", "", top.group(3))
            if re.sub(r"[\s–—-]|&ndash;|&mdash;", "", rest):
                lines.append((date, rest))
        elif line.startswith("**") and date:
            lines.append((date, line.lstrip("*")))
        elif line.startswith("*") or line.startswith("="):
            date = None
    return [(d, [t for t in dict.fromkeys(links(s)) if not skip.match(t)]) for d, s in lines]


# --- the build -------------------------------------------------------------------

def build(src, out, albums=ALBUMS, event_years=EVENT_YEARS, extra=EXTRA):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = parse_list(src.page(LIST))

    album_text = {a: src.page(p) for a, p in albums.items()}
    tracks = {a: track_lengths(t) for a, t in album_text.items()}
    album_date = {a: release_date(t) for a, t in album_text.items()}
    write_tsv(out / "albums.tsv", ["album", "article", "release_date"],
              [(a, albums[a], album_date[a]) for a in albums])

    def length_for(title, releases):
        for name in releases + ["Past Masters"]:
            for key in (norm, base):
                for tt, s in tracks.get(name, []):
                    if key(tt) == key(title):
                        return s
        return ""

    articles = src.resolve([r["link"] for r in rows])
    songs = []
    for r in rows:
        fr, rel = first_release(r)
        mine = own(r["title"], articles[r["link"]])
        day, date_from = "", ""
        if fr.startswith("single"):
            if mine:
                day, date_from = song_date(src.page(r["link"])), articles[r["link"]]
        elif rel and rel[0] in albums:
            day, date_from = album_date[rel[0]], albums[rel[0]]
            if mine and not r["cover"]:  # a song issued before its album, often as a single, keeps its own first date
                d = song_date(src.page(r["link"]))
                if d[:4] == r["year"] and d < day:
                    day, date_from = d, articles[r["link"]]
        if day[:4] != r["year"]:
            day, date_from = "", ""
        songs.append({"title": r["title"], "article": articles[r["link"]], "year": r["year"],
                      "first_release": fr, "first_album": rel[0] if rel else "",
                      "songwriters": r["writers"], "lead_vocals": "+".join(n for n in clean_lead(r["vocals"]).split("+") if n not in r["noted"]),
                      "with_vocals": "+".join([*filter(None, helpers(r["vocals"]).split("+")), *r["noted"]]),
                      "article_lead": personnel_leads(src.page(r["link"])) if mine else "",
                      "length_s": length_for(r["title"], rel), "release_date": day, "date_from": date_from,
                      "cover": "yes" if r["cover"] else "no", "views_2024": src.pageviews(articles[r["link"]]) if mine else "",
                      "catalogue": "core 1962-1970" if r["table"] == "main" else "later release"})
    cols = list(songs[0])
    write_tsv(out / "songs.tsv", cols, [[s[c] for c in cols] for s in songs])

    lines = [(d, ts) for y in event_years for d, ts in year_events(src.page(y), y)]
    target = src.resolve(sorted({t for _, ts in lines for t in ts}))
    lines = [(d, list(dict.fromkeys(target[t] for t in ts if target[t]))) for d, ts in lines]
    occ = src.occurrences(sorted({t for _, ts in lines for t in ts}))

    occurring = sorted(a for a in occ if occ[a]["occurrence"] == "yes")
    dropped = src.excluded("event")
    when = src.event_dates(occurring)

    def event(day, article):
        """A discrete occurrence: dated to the day's month by P585, P580, or P619, not marked as a country,
        organization, or person, and discrete by discrete()."""
        o = occ[article]
        return (article not in dropped and o["occurrence"] == "yes" and day[:7] in o["months"] and not NOT_EVENT.search(article + " " + o["description"])
                and discrete(when[article], day[:7]))

    cands = sorted({(d, t) for d, ts in lines if "The Beatles" not in ts
                    for t in [next((t for t in ts if event(d, t)), None)] if t})
    scored = [(d[:7], d, a, src.pageviews(a)) for d, a in cands]
    best = {}
    for c in scored:  # most views wins; a tie goes to the earlier date, then the article title
        m, d, a, v = c
        if m not in best or (-v, d, a) < (-best[m][3], best[m][1], best[m][2]):
            best[m] = c
    write_tsv(out / "event-candidates.tsv", ["month", "date", "article", "views_2024", "chosen"],
              [(*c, "yes" if best[c[0]] == c else "no") for c in scored])
    first = {}
    for d, ts in sorted(lines):
        for a in ts:
            if "The Beatles" not in ts and event(d, a):
                first.setdefault((d[:7], a), d)
    every = sorted(first)
    image = src.images(sorted({a for _, a in every}))
    meta = src.commons(sorted({f for f in image.values() if f} | {f for _, f in extra}))
    free = {a: meta[f] for a, f in image.items() if f and FREE.match(meta[f]["license_code"])}
    write_tsv(out / "events.tsv", ["month", "date", "event", "views_2024", "commons_file"],
              [(m, d, a, v, free[a]["file"] if a in free else "") for m, d, a, v in (best[k] for k in sorted(best))])
    release = {s["release_date"][:7] for s in songs if s["release_date"]} | {d[:7] for d in album_date.values() if d}
    photo = lambda p: (p["file"], p["license"], p["author"], p["link"])
    ranked = sorted(((m, first[m, a], a, src.pageviews(a)) for m, a in every if m in release and a in free),
                    key=lambda c: (c[0], -c[3], c[1], c[2]))  # every occurrence the month's lines link, once, at its first date
    rows_out = [(m, a, d, v, *photo(free[a]), "no") for m, d, a, v in ranked]
    rows_out += [(m, best[m][2], best[m][1], best[m][3], "", "", "", "", "no")  # a month with no free photo keeps its pick
                 for m in sorted(release & set(best)) if not any(r[0] == m for r in rows_out)]
    rows_out.sort(key=lambda r: r[0])
    rows_out += [(meta[f]["date"][:7], name, meta[f]["date"], "", *photo(meta[f]), "yes")
                 for name, f in extra if FREE.match(meta[f]["license_code"])]
    write_tsv(out / "event-photos.tsv", ["month", "event", "date", "views_2024", "commons_file", "license", "author", "link", "extra"],
              rows_out)

    by_article = {s["article"]: s for s in songs if own(s["title"], s["article"])}  # exact titles only
    pair = src.resolve([PAIR])[PAIR]
    pairs = set()
    for w in src.wikidata():
        s, other = by_article.get(w["song_article"]), w["other_article"]
        if not s or not other or w["property"] not in RELATIONS:
            continue
        if w["property"] == "P86":  # the composer must agree with the published credit
            if s["songwriters"] == PAIR and pair and surnames(display(other)) <= surnames(PAIR):
                other = pair
            elif not surnames(display(other)) & surnames(s["songwriters"]):
                continue
        sv, ov = src.pageviews(w["song_article"]), src.pageviews(other)
        if max(sv, ov) >= FAME_RATIO * max(min(sv, ov), 1):
            pairs.add((s["title"], w["song_article"], RELATIONS[w["property"]], other, sv, ov, "song" if sv > ov else "other",
                       s["songwriters"]))
    write_tsv(out / "links.tsv", ["song", "song_article", "relation", "other_article", "song_views_2024",
                                  "other_views_2024", "famous", "credit"], sorted(pairs))

    reversal_general(src, out)


def discrete(dates, month):
    """True when Wikidata dates the item to a day of the month: a point in time (P585) or launch date (P619) at day
    precision in that month, or a start time (P580) at day precision with an end time (P582) in that month. Every start
    and end time must fall in the month. A war, a movement, or a currency starts in one month and ends in another, or
    has no end."""
    ends = [t for p, t, _ in dates if p == "P582"]
    day = any(prec >= 11 and t[:7] == month and (p in ("P585", "P619") or (p == "P580" and ends)) for p, t, prec in dates)
    return day and all(t[:7] == month for p, t, _ in dates if p in ("P580", "P582"))


def surnames(names):
    """The lower-case last names in a credit ("Lennon–McCartney", "Gerry Goffin; Carole King") or a person's name."""
    out = set()
    for part in re.split(r"[;–]", names):
        toks = [t for t in re.findall(r"[\w'-]+", part) if t.lower().rstrip(".") not in {"jr", "sr", "ii", "iii", "iv"}]
        if toks:
            out.add(ALIAS.get(toks[-1].lower(), toks[-1].lower()))
    return out


def own(title, article):
    """True when the article is about this song: the article title, less a trailing parenthesis, is the song title."""
    return bool(article) and display(article) == title


def display(title):
    return re.sub(r" \([^()]*\)$", "", title)


def reversal_general(src, out):
    """Pairs outside the Beatles for the reversal-general category. One end must have FAME_RATIO times the other's views."""
    rows = []
    famous = lambda a, b: src.pageviews(a) >= FAME_RATIO * max(src.pageviews(b), 1)
    pairs = src.pinned("reversal-wikidata.tsv") if (src.pins / "reversal-wikidata.tsv").exists() else []
    links = src.pinned("reversal-links.tsv") if pairs else []
    label = {(p["relation"], p["famous_item"]): p["famous"] for p in pairs} | {(p["relation"], p["obscure_item"]): p["obscure"] for p in pairs}
    dropped = src.excluded("pair")
    for p in pairs:
        if famous(p["famous_title"], p["obscure_title"]) and not {p["famous"], p["obscure"]} & dropped:
            nf = sorted({label[(p["relation"], l["obscure_item"])] for l in links if l["relation"] == p["relation"]
                         and l["famous_item"] == p["famous_item"] and l["obscure_item"] != p["obscure_item"]})
            nr = sorted({label[(p["relation"], l["famous_item"])] for l in links if l["relation"] == p["relation"]
                         and l["obscure_item"] == p["obscure_item"] and l["famous_item"] != p["famous_item"]})
            rows.append((p["relation"].replace("_", " "), p["famous"], p["obscure"], src.pageviews(p["famous_title"]),
                         src.pageviews(p["obscure_title"]), ";".join(nf), ";".join(nr)))
    kin = src.parents() if (src.pins / "parents.tsv").exists() or src.online else []
    rel = {"P22": "father", "P25": "mother"}
    for k in kin:
        if famous(k["child_title"], k["parent_title"]):
            nf = sorted({display(x["parent_title"]) for x in kin if x["child_item"] == k["child_item"]
                         and x["property"] == k["property"] and x["parent_item"] != k["parent_item"]})
            nr = sorted({display(x["child_title"]) for x in kin if x["parent_item"] == k["parent_item"]
                         and x["child_item"] != k["child_item"]})
            rows.append((rel[k["property"]], display(k["child_title"]), display(k["parent_title"]), src.pageviews(k["child_title"]),
                         src.pageviews(k["parent_title"]), ";".join(nf), ";".join(nr)))
    write_tsv(out / "reversal-general.tsv", ["relation", "famous", "obscure", "famous_views_2024", "obscure_views_2024",
                                              "not_forward", "not_reverse"], sorted(rows))


def main(argv):
    online = "--offline" not in argv
    args = [a for a in argv if a != "--offline"]
    raw, pins, out = args if args else (ROOT / "data" / "raw", ROOT / "data" / "pins", ROOT / "data")
    src = Source(raw, pins, online)
    try:
        build(src, out)
    finally:
        if online:
            src.save()


if __name__ == "__main__":
    main(sys.argv[1:])
