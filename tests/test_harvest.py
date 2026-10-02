"""The harvest is a pure function of the pinned inputs: the same raw pages and pins give the same data, byte for byte."""
import csv
import re
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "harvest"))
import harvest  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "harvest"
FILES = ["songs.tsv", "albums.tsv", "events.tsv", "event-candidates.tsv", "event-photos.tsv", "links.tsv", "reversal-general.tsv"]


def build(raw, pins, albums=harvest.ALBUMS, years=harvest.EVENT_YEARS):
    out = Path(tempfile.mkdtemp())
    harvest.build(harvest.Source(raw, pins, online=False), out, albums, years)
    return out


class HarvestTest(unittest.TestCase):
    def test_fixture_matches_expected(self):
        out = build(FIX / "raw", FIX / "pins", {"Album One": "Album One", "Album Two": "Album Two"}, ["1963", "1995"])
        for name in FILES:
            with self.subTest(name):
                self.assertEqual((out / name).read_text(), (FIX / "expected" / name).read_text())

    def test_the_moon_landing_is_july_1969s_event(self):
        with open(ROOT / "data" / "events.tsv", encoding="utf-8") as f:
            events = {r["month"]: r["event"] for r in csv.DictReader(f, delimiter="\t")}
        self.assertEqual(events["1969-07"], "Apollo 11")

    def test_no_band_era_release_month_falls_after_may_1970(self):
        """Every release month the event window holds ends at Let It Be. Later months are archive releases."""
        months = {r["release_date"][:7] for name in ("songs.tsv", "albums.tsv") for r in read(name) if r["release_date"]}
        self.assertEqual(max(m for m in months if m <= "1970-12"), "1970-05")
        self.assertEqual(sorted(m for m in months if m > "1970-05"),
                         ["1988-03", "1994-11", "1995-11", "1996-03", "1996-10", "2013-11", "2025-11"])

    def test_every_photo_is_free_and_the_extra_row_is_never_asked(self):
        photos = read("event-photos.tsv")
        self.assertTrue(all(p["license"] == "" or re.match(r"(Public domain|CC0|CC BY(-SA)? [0-9.]+)( \w+)?$", p["license"])
                            for p in photos), {p["license"] for p in photos})
        extra = [p["event"] for p in photos if p["extra"] == "yes"]
        self.assertEqual(extra, ["Elvis Presley meets Richard Nixon"])
        asked = (ROOT / "questions").glob("*.jsonl")
        self.assertFalse(any("Elvis Presley meets" in f.read_text(encoding="utf-8") for f in asked))


class DataTest(unittest.TestCase):
    """Correctness checks over the committed tables."""

    def test_no_two_songs_share_facts_by_accident(self):
        songs = read("songs.tsv")
        by_title = {s["title"]: s for s in songs}
        own = [s for s in songs if s["views_2024"] or (s["date_from"] and s["date_from"] == s["article"])]
        for s in own:  # a fact read from a song's article is read only from an article about that song
            self.assertEqual(harvest.display(s["article"]), s["title"], s["title"])
        self.assertEqual(len({s["article"] for s in own}), len(own))
        for link in read("links.tsv"):
            self.assertEqual(harvest.display(link["song_article"]), link["song"])
            self.assertEqual(by_title[link["song"]]["article"], link["song_article"])
        linked = {link["song"] for link in read("links.tsv")}
        self.assertFalse(linked & {"Can You Take Me Back?", "Can You Dig It?", "Revolution 1"})
        self.assertIn("Cry Baby Cry", linked)

    def test_the_composer_agrees_with_the_published_credit(self):
        credit = {s["title"]: s["songwriters"] for s in read("songs.tsv")}
        composers = [link for link in read("links.tsv") if link["relation"] == "composer"]
        self.assertTrue(composers)
        for link in composers:
            with self.subTest(link["song"]):
                self.assertEqual(link["credit"], credit[link["song"]])
                if credit[link["song"]] == harvest.PAIR:
                    self.assertEqual(link["other_article"], harvest.PAIR)
                else:
                    self.assertTrue(harvest.surnames(harvest.display(link["other_article"])) & harvest.surnames(link["credit"]))

    def test_a_single_released_before_its_album_carries_the_single_date(self):
        """A hand-checked sample: each song's own infobox, read on 2026-09-23."""
        date = {s["title"]: s["release_date"] for s in read("songs.tsv")}
        self.assertEqual(date["Can't Buy Me Love"], "1964-03-16")
        self.assertEqual(date["You Can't Do That"], "1964-03-16")
        self.assertEqual(date["Let It Be"], "1970-03-06")

    def test_events_are_discrete_and_dated_to_the_day(self):
        events = {r["event"] for r in read("events.tsv")}
        self.assertFalse(events & {"Cultural Revolution", "Nigerian Civil War", "Cambodian Civil War", "Australian dollar",
                                   "Colombian conflict", "Indonesian mass killings of 1965–66"})
        self.assertIn("Assassination of John F. Kennedy", events)


def read(name):
    with open(ROOT / "data" / name, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


if __name__ == "__main__":
    unittest.main()
