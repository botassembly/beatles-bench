#!/usr/bin/env python3
"""Figure 1: the song, singer, and album graph, drawn as flows: lead singer to first album, weighted by songs.
kuva has no node-link layout, so the graph is a Sankey diagram of the same edges (data/songs.tsv)."""
import csv
from collections import Counter

from common import ROOT, kuva

NAMES = {"Lennon": "John Lennon", "McCartney": "Paul McCartney", "Harrison": "George Harrison", "Starr": "Ringo Starr"}

with open(ROOT / "data" / "songs.tsv", encoding="utf-8", newline="") as f:
    songs = [s for s in csv.DictReader(f, delimiter="\t") if s["catalogue"] == "core 1962-1970"]
flows = Counter()
for s in songs:
    singer = NAMES.get(s["lead_vocals"], "shared lead" if "+" in s["lead_vocals"] else "other")
    album = "a single" if s["first_release"].startswith("single") else s["first_album"]
    flows[singer, album] += 1
rows = sorted(((a, b, n) for (a, b), n in flows.items()), key=lambda r: (-r[2], r[0], r[1]))
kuva("sankey", ["singer", "first release", "songs"], rows, "1-graph", "--source-col", "singer", "--target-col", "first release",
     "--value-col", "songs", "--title", f"Lead singer to first release, {len(songs)} songs of 1962 to 1970", "--width", 1100, "--height", 900)
