"""The results table prints a row for a model with no price in scripts/score/prices.tsv. A reader's own model has none
on its first run, and the table must still print. The front page's table shows the cells table.py prints."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for d in ("score", "figures"):
    sys.path.insert(0, str(ROOT / "scripts" / d))
import analyze  # noqa: E402
import common  # noqa: E402
import table  # noqa: E402

SONGS = {s["title"]: s for s in analyze.read_tsv(ROOT / "data" / "songs.tsv")}
JEV = ROOT / "results" / "archive" / "runs" / "2026-09-23-thinkthen-jev"


class UnpricedModelTest(unittest.TestCase):
    def test_a_model_with_no_price_prints_a_blank_cost_cell(self):
        qs = analyze.questions()
        t = analyze.tables(qs, analyze.systems(qs, [JEV]), SONGS, lambda model, backend: (None, "no price"))
        out = Path(tempfile.mkdtemp())
        analyze.write(t, out)
        saved, common.TABLES = common.TABLES, out
        try:
            text = table.results()
        finally:
            common.TABLES = saved
        row = next(l for l in text.splitlines() if l.startswith("| Jev |"))
        self.assertEqual(row.split(" | ")[3:], ["", "0.29 s |"])


class ReadmeTableTest(unittest.TestCase):
    """README.md's headline table is pasted by hand from table.py. Each shown cell must equal table.py's: the Beatles-only
    share, the median time before its note, and the dollars per 1,000 rounded to three places."""
    NAMES = {"String search (BM25)": "BM25", "Laya, from memory": "Laya", "Jev, from memory": "Jev",
             "GLM-5.3 Flash, from memory": "GLM-5.3 Flash", "Liquid d1, from memory": "Liquid d1"}

    def test_the_readme_table_equals_table_py(self):
        printed = {}
        for line in table.results().splitlines():
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) == 5:
                printed[cells[0]] = cells
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in readme.splitlines()
                if l.startswith("| ") and l.split("|")[1].strip() in self.NAMES]
        self.assertEqual(sorted(r[0] for r in rows), sorted(self.NAMES))
        for name, share, time, dollars in rows:
            system, beatles, _, cost, median = printed[self.NAMES[name]]
            with self.subTest(system=system):
                self.assertEqual(share, beatles.split(" ")[0])
                self.assertEqual(time.split(" (")[0], median)  # a note on the build and load may follow
                want = f"{float(cost):.3f}".rstrip("0").rstrip(".")
                self.assertEqual(dollars.split(" ")[0], want)


class ResultsFunctionTableTest(unittest.TestCase):
    """reports/results.md's function table is pasted from `python3 scripts/score/table.py`. The block from the
    table's header row to the next blank line must equal what table.functions() prints, byte for byte."""

    def test_the_function_table_equals_table_py(self):
        page = (ROOT / "reports" / "results.md").read_text(encoding="utf-8")
        start = page.index("| Function | Test | Measure |")
        block = page[start:page.index("\n\n", start)]
        self.assertEqual(block, table.functions())


if __name__ == "__main__":
    unittest.main()
