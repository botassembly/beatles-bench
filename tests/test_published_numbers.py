"""Each number a reader or the talk quotes from the pages must equal its source. One row per claim: the page, the text
it quotes with {} where the number sits, and the source that computes the number from the data, the questions, or the
runs. Needs no thinkthen command and no network."""
import csv
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
    """A cell of the all row that open_book.py compare prints for the Jev run open-book.md pairs with its run."""
    text = open_book.compare(published.RUNS / f"{published.JEV}-thinkthen-jev",
                             published.RUNS / f"{published.JEV}-thinkthen-jev-open-book")
    return next(l for l in text.splitlines() if l.startswith("| all |")).strip("|").split("|")[cell].strip()


def results(system):
    """The Beatles-only share table.py prints for a row of the results table, without its interval."""
    row = next(l for l in table.results().splitlines() if l.startswith(f"| {system} |"))
    return row.strip("|").split("|")[1].strip().split(" ")[0]


def tsv(path, **match):
    """The one row of a results table whose columns equal match."""
    got = [r for r in csv.DictReader(open(ROOT / path, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)
           if all(r[k] == v for k, v in match.items())]
    assert len(got) == 1, (path, match, len(got))
    return got[0]


def cell(path, column, **match):
    return tsv(path, **match)[column]


def load(line, field):
    """A load average of the 2026-09-26 Jev run: the second start line, the one that finished, or the end line."""
    lines = (published.JEV_RUN / "loadavg.txt").read_text(encoding="utf-8").splitlines()
    return {"start": [l for l in lines if l.startswith("start ")][-1], "end": lines[-1]}[line].split()[field]


def output(folder, case):
    """The answer row of one case in an example folder's outputs.jsonl."""
    for l in open(ROOT / "examples" / folder / "outputs.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["id"] == case:
            return r["rows"][0]
    raise KeyError(case)


def jev(qid, option):
    """Jev's probability for one option of a bench question, named by its text, in the 2026-09-26 Jev run."""
    q = next(json.loads(l) for f in sorted((ROOT / "questions").glob("*.jsonl")) for l in open(f, encoding="utf-8")
             if json.loads(l)["id"] == qid)
    a = next(json.loads(l) for l in open(published.JEV_RUN / "answers.jsonl", encoding="utf-8") if json.loads(l)["id"] == qid)
    key = option.lower() if q["options"] is None else next(k for k, v in q["options"].items() if v == option)
    return a["probabilities"][key]


def band(p, low=0.3, high=0.7):
    """decide under a band: yes at or above the high side, no below the low side, else not sure (SQL NULL)."""
    return "1" if p >= high else "0" if p < low else "NULL"


def sql_rows():
    """The sql slide's rows: each cold filter song, its probability, and its answer at the band 0.3:0.7."""
    out = []
    for l in open(ROOT / "examples" / "filter" / "outputs.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["id"].startswith("filter-cold-"):
            row = r["rows"][0]
            p = row["answer"]["probability"]
            out.append((row["input"]["input"], p, band(p)))
    return out


def chained(kind):
    row = tsv("results/tables/composition.tsv", system="Jev", kind=kind)
    return str(int(row["both_hops_right"]) - int(row["wrong_with_both_hops"]))


COST = "results/tables/cost.tsv"
ACC = "results/tables/accuracy.tsv"
FUN = "results/tables/functions.tsv"
# The By function table's memory, reading and context cells, pulled from functions.tsv. Each entry is the memory
# (test, measure), the reading (test, measure), the context (test, measure), and the row's question text.
BY_FUNCTION = [
    ("decide", "yes/no questions", "accuracy at 0.5", "reading", "accuracy at 0.5", "context", "accuracy at 0.5",
     "yes or no about one song"),
    ("choose", "pick-one questions", "accuracy", "reading", "accuracy", "context", "accuracy",
     "the right one of four or five options"),
    ("tag", "lead singers", "exact-set match", "reading", "exact-set match", "context", "exact-set match",
     "every Beatle who sang the lead, and who wrote or played how long"),
    ("filter", "lead singer or album", "F1", "reading", "F1", "context", "F1", "whether a song keeps or drops"),
    ("find", "album", "exact match", "reading", "exact match", "context", "exact match",
     "the one song of the set that fits"),
]
by_function = lambda f, t, m: cell(FUN, "value", function=f, test=t, measure=m)
suite_cases = lambda name, level=None: str(
    sum(1 for l in open(ROOT / "questions" / "suite" / name, encoding="utf-8")
        if level is None or json.loads(l)["level"] == level))
SPEARMAN_VIEWS, SPEARMAN_LEN, SPEARMAN_DATE = ("Spearman with 2024 page views", "Spearman with length in seconds",
                                             "Spearman with release date")


def reading_run(field):
    """The all-run's knowledge answers plus suite cases, or its input tokens sent, from its committed outputs."""
    outs = [json.loads(l) for l in open(published.JEV_ALL / "outputs.jsonl", encoding="utf-8")]
    ans = [json.loads(l) for l in open(published.JEV_ALL / "answers.jsonl", encoding="utf-8")]
    tok = sum(o["input_tokens"] for o in outs if o.get("sent")) + sum(a["input_tokens"] for a in ans)
    return {"questions": len(ans), "cases": len(outs), "tokens": tok}[field]
CHOOSE = lambda option: lambda: output("choose", "choose-cold-04")["answer"]["probabilities"][option]
EX = "examples/{}/README.md".format
# The slide folders of examples/: each row names a folder's page, the text it quotes, and the source of the value.
SLIDE_CLAIMS = [
    (EX("strings"), "| `lead_vocals` `{}` |", lambda: cell("data/songs.tsv", "lead_vocals", title="Octopus's Garden")),
    (EX("strings"), "| `first_album` `{}` |", lambda: cell("data/songs.tsv", "first_album", title="Octopus's Garden")),
    (EX("strings"), "| A random guess | `{}` |", lambda: results("Chance")),
    (EX("strings"), "| Vector search | `{}` |", lambda: results("Embeddings")),
    (EX("jev"), "| John for Octopus's Garden | `{}` |", CHOOSE("John")),
    (EX("jev"), "| Paul for Octopus's Garden | `{}` |", CHOOSE("Paul")),
    (EX("jev"), "| George for Octopus's Garden | `{}` |", CHOOSE("George")),
    (EX("jev"), "| Ringo for Octopus's Garden | `{}` |", CHOOSE("Ringo")),
    (EX("jev"), "| John and Paul duet for Octopus's Garden | `{}` |", CHOOSE("John and Paul duet")),
    (EX("jev"), "`median_s` `{}`", lambda: cell(COST, "median_s", system="Jev")),
    (EX("jev"), "`usd` `{}`", lambda: cell(COST, "usd", system="Jev")),
    (EX("jev"), "| The load at the start of the run | `{}` |", lambda: load("start", 2)),
    (EX("jev"), "| The load at the end of the run | `{}` |", lambda: load("end", 2)),
    (EX("jev"), "`usd_per_m_input` `{}`", lambda: cell("scripts/score/prices.tsv", "usd_per_m_input", model_prefix="jev")),
    (EX("bench"), "| Songs | `{}` |", lambda: rows("songs.tsv")),
    (EX("bench"), "| Albums | `{}` |", lambda: rows("albums.tsv")),
    (EX("bench"), "| Questions | `{}` |", questions),
    (EX("sql"), "{}", lambda: "".join(f"| {s} | {p} | {a} |\n" for s, p, a in sql_rows())),
    (EX("what-jev-knows"), "| Random guess | `{}` |", lambda: results("Chance")),
    (EX("what-jev-knows"), "| Vector search | `{}` |", lambda: cell(ACC, "accuracy", system="Embeddings", scope="beatles-only")),
    (EX("what-jev-knows"), "| Jev from memory | `{}` |", lambda: cell(ACC, "accuracy", system="Jev", scope="beatles-only")),
    (EX("what-jev-knows"), "| Big chat model | `{}` |", lambda: cell(ACC, "accuracy", system="GLM-5.3 Flash", scope="beatles-only")),
    (EX("what-jev-knows"), "the `{}` Beatles-only questions", lambda: questions(beatles_only=True)),
    (EX("catches"), "| John Lennon | `{}` |", lambda: jev("forward-singer-033", "John Lennon")),
    (EX("catches"), "| George Harrison | `{}` |", lambda: jev("forward-singer-033", "George Harrison")),
    (EX("catches"), "| Yellow Submarine | `{}` |", lambda: jev("lexical-trap-album-to-song-001", "Yellow Submarine")),
    (EX("catches"), "| It's All Too Much | `{}` |", lambda: jev("lexical-trap-album-to-song-001", "It's All Too Much")),
    (EX("catches"), "| No | `{}` |", lambda: jev("multi-hop-same-month-050", "No")),
    (EX("catches"), "| Yes | `{}` |", lambda: jev("multi-hop-same-month-050", "Yes")),
    (EX("catches"), "| Least viewed quarter of songs | `{}` |", lambda: cell("results/tables/popularity.tsv", "accuracy", system="Jev", bin="1")),
    (EX("catches"), "| Most viewed quarter of songs | `{}` |", lambda: cell("results/tables/popularity.tsv", "accuracy", system="Jev", bin="4")),
    (EX("catches"), "| Word traps right | `{}` of", lambda: cell("results/tables/controls.tsv", "test_right", system="Jev", test="lexical-trap")),
    (EX("catches"), "| Their controls right | `{}` of", lambda: cell("results/tables/controls.tsv", "control_right", system="Jev", test="lexical-trap")),
    (EX("catches"), "of `{}` |", lambda: cell("results/tables/controls.tsv", "n", system="Jev", test="lexical-trap")),
    (EX("catches"), "| Same-month questions with both hops right | `{}` |", lambda: cell("results/tables/composition.tsv", "both_hops_right", system="Jev", kind="same-month")),
    (EX("catches"), "| Of those, chained right | `{}` |", lambda: chained("same-month")),
    (EX("open-book"), "| From memory | `{}` |", lambda: open_book_all(2)),
    (EX("open-book"), "| With the catalog | `{}` |", lambda: open_book_all(3)),
    (EX("open-book"), "the same `{}` questions", lambda: open_book_all(1)),
    (EX("know-this"), "| Jev's price per million input tokens | `{}` |", lambda: cell("scripts/score/prices.tsv", "usd_per_m_input", model_prefix="jev")),
    (EX("know-this"), "`usd_per_m_output` `{}`", lambda: cell("scripts/score/prices.tsv", "usd_per_m_output", model_prefix="jev")),
    (EX("know-this"), "`usd` `{}`", lambda: cell(COST, "usd", system="Jev")),
    (EX("bench-run"), "| Questions | `{}` |", lambda: f"{int(cell(COST, 'questions', system='Jev')):,}"),
    (EX("bench-run"), "`usd` `{}`", lambda: cell(COST, "usd", system="Jev")),
    (EX("bench-run"), "`median_s` `{}`", lambda: cell(COST, "median_s", system="Jev")),
    (EX("bench-run"), "| Jev per 1,000 questions | `usd_per_1000_questions` `{}` |", lambda: cell(COST, "usd_per_1000_questions", system="Jev")),
    (EX("bench-run"), "| GLM-5.3 Flash per 1,000 questions | `usd_per_1000_questions` `{}` |", lambda: cell(COST, "usd_per_1000_questions", system="GLM-5.3 Flash")),
    (EX("bench-run"), "| The load at the start of the run | `{}` |", lambda: load("start", 2)),
    (EX("bench-run"), "| The load at the end of the run | `{}` |", lambda: load("end", 2)),
]

CLAIMS = [
    ("README.md", "{} Beatles songs", lambda: rows("songs.tsv")),
    ("README.md", "{} albums", lambda: rows("albums.tsv")),
    ("README.md", "The audited {} questions", questions),
    ("README.md", "{} questions sit across 13 Beatles categories", lambda: questions(beatles_only=True)),
    ("README.md", "it got {} from memory", lambda: open_book_all(2)),
    ("README.md", "and {} with the 306-song catalog", lambda: open_book_all(3)),
    ("data/README.md", "| `songs.tsv` | {} released Beatles songs", lambda: rows("songs.tsv")),
    ("data/README.md", "| `albums.tsv` | {} albums", lambda: rows("albums.tsv")),
    *[( "reports/results.md", "{}",
         lambda f=f, t=t, m=m, rt=rt, rm=rm, ct=ct, cm=cm, what=what:
             f"| {f} | {int(cell(FUN, 'n', function=f, test=t, measure=m)):,} | {what} "
             f"| {by_function(f, t, m)} | {by_function(f, rt, rm)} | {by_function(f, ct, cm)} |")
      for f, t, m, rt, rm, ct, cm, what in BY_FUNCTION],
    ("reports/results.md", "{}",
     lambda: "| score | {} | how well known the song is today, 1 to 5, and its length | {} / {} | {} | {} / {} |".format(
         int(suite_cases("score.jsonl", "memory")),
         by_function("score", "popularity", SPEARMAN_VIEWS), by_function("score", "length", SPEARMAN_LEN),
         by_function("score", "reading", SPEARMAN_VIEWS),
         by_function("score", "popularity-context", SPEARMAN_VIEWS),
         by_function("score", "length-context", SPEARMAN_LEN))),
    ("reports/results.md", "{}",
     lambda: "| rank | {} | the songs in order by fame, and by date | {} / {} | {} / {} | {} / {} |".format(
         int(cell(FUN, "n", function="rank", test="popularity", measure=SPEARMAN_VIEWS))
         + int(cell(FUN, "n", function="rank", test="date", measure=SPEARMAN_DATE)),
         by_function("rank", "popularity", SPEARMAN_VIEWS), by_function("rank", "date", SPEARMAN_DATE),
         by_function("rank", "reading-popularity", SPEARMAN_VIEWS), by_function("rank", "reading-date", SPEARMAN_DATE),
         by_function("rank", "popularity-context", SPEARMAN_VIEWS),
         by_function("rank", "date-context", SPEARMAN_DATE))),
    ("reports/results.md", "{}",
     lambda: "| annotate | {} | singer, first album and year, or writers, cover and length | {} | {} | {} |".format(
         suite_cases("annotate.jsonl", "memory"), by_function("annotate", "card", "singer accuracy"),
         by_function("annotate", "reading", "singer accuracy"), by_function("annotate", "context", "singer accuracy"))),
    ("reports/results.md", "| recognize | 400 | the song, person and album names in a sentence | — | {} | — |",
     lambda: by_function("recognize", "names-template", "song precision")),
    ("reports/results.md", "{}",
     lambda: "| relate | {} | the edges between a set's songs, people and albums | {} | — | — |".format(
         sum(1 for l in open(ROOT / "questions" / "suite" / "relate.jsonl", encoding="utf-8")),
         by_function("relate", "song to singer and album", "edge F1"))),
    ("reports/results.md", "results/runs/2026-09-30-all-jev`: the {} questions and ", lambda: f"{reading_run('questions'):,}"),
    ("reports/results.md", " and {} cases, ", lambda: f"{reading_run('cases'):,}"),
    ("reports/results.md", "{} input tokens, about $0.40", lambda: f"{reading_run('tokens'):,}"),
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

    def test_each_slide_folder_quotes_its_source(self):
        for page, quote, source in SLIDE_CLAIMS:
            with self.subTest(page=page, quote=quote):
                self.assertIn(quote.format(source()), (ROOT / page).read_text(encoding="utf-8"))

    def test_the_slide_values_are_the_ones_the_talk_shows(self):
        """The talk shows these values. A change here changes a slide."""
        self.assertEqual([cell(COST, c, system="Jev") for c in ("median_s", "usd")], ["0.195", "0.023347"])
        self.assertEqual([load("start", 2), load("end", 2)], ["6.74", "11.18"])
        self.assertEqual([CHOOSE(o)() for o in ("John", "Paul", "George", "Ringo", "John and Paul duet")],
                         [0.01, 0.02, 0.13, 0.84, 0.0])
        self.assertEqual([jev("forward-singer-033", "John Lennon"), jev("forward-singer-033", "George Harrison"),
                          jev("lexical-trap-album-to-song-001", "Yellow Submarine"),
                          jev("lexical-trap-album-to-song-001", "It's All Too Much"),
                          jev("multi-hop-same-month-050", "No"), jev("multi-hop-same-month-050", "Yes")],
                         [0.28, 0.17, 0.52, 0.34, 0.79, 0.21])
        self.assertEqual([a for _, _, a in sql_rows()], "1 0 1 1 0 1 0 NULL 1 1 0 1".split())
        truth = {s: cell("data/songs.tsv", "first_album", title=s) == "Abbey Road" for s, _, _ in sql_rows()}
        wrong = [s for s, _, a in sql_rows() if a != "NULL" and (a == "1") != truth[s]]
        self.assertEqual(wrong, ["A Day in the Life"])

    def test_the_numbers_are_the_ones_the_talk_shows(self):
        """The talk quotes these values. A change here changes a slide."""
        self.assertEqual([rows("songs.tsv"), questions(), questions(beatles_only=True)], ["306", "1,501", "1,313"])
        self.assertEqual([open_book_all(2), open_book_all(3)], ["68 (35%)", "184 (94%)"])
        self.assertEqual([results("Chance"), results("Embeddings")], ["31.4%", "37.6%"])


if __name__ == "__main__":
    unittest.main()
