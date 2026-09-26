"""Each number a reader or the talk quotes from the pages must equal its source. One row per claim: the page, the text
it quotes with {} where the number sits, and the source that computes the number from the data, the questions, or the
runs. Needs no thinkthen command and no network."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "score"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import open_book  # noqa: E402
import published  # noqa: E402
import table  # noqa: E402


def rows(name):
    """The rows of a data table, less its header, with thousands commas."""
    return f"{len((ROOT / 'data' / name).read_text(encoding='utf-8').splitlines()) - 1:,}"


def questions(beatles_only=False):
    """The questions in questions/*.jsonl. Beatles-only leaves out the two reversal-general categories."""
    qs = [json.loads(l) for f in sorted((ROOT / "questions").glob("*.jsonl")) for l in open(f, encoding="utf-8")]
    return f"{sum(1 for q in qs if not (beatles_only and q['category'].startswith('reversal-general'))):,}"


def open_book_all(cell):
    """A cell of the all row that open_book.py compare prints for the published Jev run and its open-book run."""
    text = open_book.compare(published.JEV_RUN, published.RUNS / f"{published.JEV}-thinkthen-jev-open-book")
    return next(l for l in text.splitlines() if l.startswith("| all |")).strip("|").split("|")[cell].strip()


def results(system):
    """The Beatles-only share table.py prints for a row of the results table, without its interval."""
    row = next(l for l in table.results().splitlines() if l.startswith(f"| {system} |"))
    return row.strip("|").split("|")[1].strip().split(" ")[0]


CLAIMS = [
    ("README.md", "{} Beatles songs", lambda: rows("songs.tsv")),
    ("README.md", "{} albums", lambda: rows("albums.tsv")),
    ("README.md", "The audited {} questions", questions),
    ("README.md", "{} questions sit across 13 Beatles categories", lambda: questions(beatles_only=True)),
    ("README.md", "it got {} from memory", lambda: open_book_all(2)),
    ("README.md", "and {} with the 306-song catalog", lambda: open_book_all(3)),
    ("data/README.md", "| `songs.tsv` | {} released Beatles songs", lambda: rows("songs.tsv")),
    ("data/README.md", "| `albums.tsv` | {} albums", lambda: rows("albums.tsv")),
    ("reports/results.md", "{} questions in 15 categories", questions),
    ("reports/results.md", "every category but the two reversal-general ones, {} questions", lambda: questions(beatles_only=True)),
    ("reports/results.md", "| Chance | {} |", lambda: results("Chance")),
    ("reports/results.md", "| Embeddings | {} (", lambda: results("Embeddings")),
    ("reports/open-book.md", "| all | 196 | {} |", lambda: f"{open_book_all(2)} | {open_book_all(3)}"),
]


class PublishedNumbersTest(unittest.TestCase):
    def test_each_quoted_number_equals_its_source(self):
        for page, quote, source in CLAIMS:
            with self.subTest(page=page, quote=quote):
                self.assertIn(quote.format(source()), (ROOT / page).read_text(encoding="utf-8"))

    def test_the_numbers_are_the_ones_the_talk_shows(self):
        """The talk quotes these values. A change here changes a slide."""
        self.assertEqual([rows("songs.tsv"), questions(), questions(beatles_only=True)], ["306", "1,501", "1,313"])
        self.assertEqual([open_book_all(2), open_book_all(3)], ["68 (35%)", "184 (94%)"])
        self.assertEqual([results("Chance"), results("Embeddings")], ["31.4%", "37.6%"])


if __name__ == "__main__":
    unittest.main()
