#!/usr/bin/env python3
"""Write a compact Beatles catalog from data/songs.tsv and data/albums.tsv for the open-book run.

usage: catalog.py > RUN_DIR/catalog.txt
One header per first album, in release order, then one line per song:
  Octopus's Garden (lead: Starr; written: Starkey; 2:51; released 1969-09-26)
A song first released on a single sits under "Singles" in date order and names its first album. Albums missing from
albums.tsv carry no date and follow the dated ones. A song with no release date gives its year.
entry(song, albums) gives one song's context: its section header, then its line with its first album named.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def line(s, first_album=False):
    facts = [f"lead: {s['lead_vocals'].replace('+', ', ')}", f"written: {s['songwriters'].replace('; ', ', ')}"]
    if s["length_s"]:
        facts.append(f"{int(s['length_s']) // 60}:{int(s['length_s']) % 60:02d}")
    facts.append(f"released {s['release_date'] or s['year']}")
    if first_album and s["first_album"] != "Non-album single":
        facts.append(f"first album: {s['first_album']}")
    return f"{s['title']} ({'; '.join(facts)})"


def single(s):
    return s["first_release"].startswith("single") or s["first_album"] == "Non-album single"


def header(album, dated):
    return f"{album} ({dated[album]})" if album in dated else album


def entry(song, albums):
    """The header of the song's catalog section, then its line with its first album, so every entry names its album."""
    head = "Singles" if single(song) else header(song["first_album"], {a["album"]: a["release_date"] for a in albums})
    return f"{head}\n{line(song, True)}"


def catalog(songs, albums):
    when = lambda s: s["release_date"] or s["year"]
    dated = {a["album"]: a["release_date"] for a in sorted(albums, key=lambda a: a["release_date"])}
    rest = sorted({s["first_album"] for s in songs if not single(s)} - set(dated),
                  key=lambda a: min(when(s) for s in songs if s["first_album"] == a))
    out = []
    for album in list(dated) + rest:
        group = [s for s in songs if s["first_album"] == album and not single(s)]
        if group:
            out += [""] * bool(out) + [header(album, dated)] + [line(s) for s in group]
    out += ["", "Singles"] + [line(s, True) for s in sorted(filter(single, songs), key=when)]
    return "\n".join(out) + "\n"


def read(name):
    return list(csv.DictReader(open(ROOT / "data" / name, encoding="utf-8"), delimiter="\t"))


if __name__ == "__main__":
    sys.stdout.write(catalog(read("songs.tsv"), read("albums.tsv")))
