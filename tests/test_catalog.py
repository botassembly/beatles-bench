"""scripts/run/catalog.py writes one line per song, grouped by first album in release order, with the singles apart."""
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "run"))
import catalog  # noqa: E402


def read(name):
    return list(csv.DictReader(open(ROOT / "data" / name, encoding="utf-8"), delimiter="\t"))


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.text = catalog.catalog(read("songs.tsv"), read("albums.tsv"))
        self.lines = self.text.splitlines()

    def test_a_song_line_carries_every_fact_under_its_album(self):
        at = self.lines.index("Abbey Road (1969-09-26)")
        self.assertIn("Octopus's Garden (lead: Starr; written: Starkey; 2:51; released 1969-09-26)", self.lines[at:])

    def test_albums_come_in_release_order(self):
        at = [self.lines.index(h) for h in ("Please Please Me (1963-03-22)", "Abbey Road (1969-09-26)", "Let It Be (1970-05-08)")]
        self.assertEqual(at, sorted(at))

    def test_a_song_first_out_on_a_single_sits_under_singles_with_its_first_album(self):
        at = self.lines.index("Singles")
        self.assertIn("Hey Jude (lead: McCartney; written: Lennon–McCartney; 7:08; released 1968-08-26; first album: Past Masters)",
                      self.lines[at:])

    def test_an_album_track_entry_gives_its_album_header_then_its_line(self):
        song = next(s for s in read("songs.tsv") if s["title"] == "Octopus's Garden")
        self.assertEqual(catalog.entry(song, read("albums.tsv")), "Abbey Road (1969-09-26)\n"
                         "Octopus's Garden (lead: Starr; written: Starkey; 2:51; released 1969-09-26; first album: Abbey Road)")

    def test_a_single_entry_sits_under_singles_and_names_its_first_album(self):
        song = next(s for s in read("songs.tsv") if s["title"] == "She Loves You")
        self.assertEqual(catalog.entry(song, read("albums.tsv")), "Singles\n"
                         "She Loves You (lead: Lennon, McCartney; written: Lennon–McCartney; 2:21; released 1963-08-23; first album: Past Masters)")

    def test_every_song_appears_once(self):
        songs = read("songs.tsv")
        self.assertEqual(sum(1 for l in self.lines if " (lead: " in l), len(songs))
        for s in songs:
            self.assertEqual(sum(1 for l in self.lines if l.startswith(s["title"] + " (lead: ")), 1, s["title"])


if __name__ == "__main__":
    unittest.main()
