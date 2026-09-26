"""functions/ holds one folder per function, then audit and diff. The site links each folder by its name. Each folder
replays with no key. Each page quotes only numbers its committed answers or its own blocks hold, and each command on a
page prints the block below it. The pages are each folder's README.md and the walkthroughs docs/README.md lists in order.

The number check reads every fenced json block in those pages, and the prose of every page. docs/context-article.md is
the one exception: its runs keep no recording, because a recording would store Wikipedia text (data/SOURCES.md)."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FUNCTIONS = ROOT / "functions"
FOLDERS = ["annotate", "audit", "choose", "decide", "diff", "filter", "find", "rank", "recognize", "relate", "score", "tag"]
TUNING = ["audit", "diff"]  # only thinkthen main at e70bddab or later has audit and diff
RUN = ("README.md", "slide.png", "run", "outputs.jsonl", "timing.tsv", "recording")
PARTS = {"audit": RUN + ("key.jsonl", "audit-context.jsonl", "rows.jsonl", "rows-context.jsonl", "audit-asrun.json"),
         "diff": ("README.md", "slide.png", "run", "diff.jsonl")}
DOCS = ROOT / "docs"
WALKS = DOCS / "walkthroughs"
EXAMPLE = ROOT / "scripts" / "run" / "example.sh"
SITE = "https://thinkthen.dev/learn/beatles-bench/{}/"
LESSONS = ("- **You control the bar.** ", "- **The number is the number.** ")
FORM = ["## The files", "## Run it", "## Read it", "## With context", "## What can go wrong", "## The slide", "## Related"]
FENCE = re.compile(r"^```(\w*)\n(.*?)^```\n?", re.S | re.M)
CODE = re.compile(r"`[^`\n]+`")
BUILD = re.compile(r"(?:^|[\s|])thinkthen\s|run\.sh|example\.sh|^\./run\b")  # a command that runs the thinkthen command
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
DECIMAL = re.compile(r"-?\d+\.\d+")
GROUPED = re.compile(r"(?<![\d.,])\d{1,3}(?:,\d{3})+(?![\d,]\d)")
EXPONENT = re.compile(r"-?\d+(?:\.\d+)?e-?\d+")  # thinkthen writes a small p as 2e-6; jq prints 0.000002
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
import examples as gen  # noqa: E402


def answers(folder):
    """Every committed file a page may quote: the answers and the lists, or what audit and diff wrote from them."""
    if folder.name == "diff":
        return [folder / "diff.jsonl", *answers(FUNCTIONS / "audit")]
    tuned = []
    if folder.name == "audit":
        tuned = [folder / "rows.jsonl", folder / "rows-context.jsonl", *sorted(folder.glob("audit-*.json"))]
    return [folder / "outputs.jsonl", *sorted((folder / "lists").glob("*.jsonl")), *tuned]


def pairs(text):
    """Each sh block that sits right above a json or text block, with that block: (command, output, json or text)."""
    blocks = list(FENCE.finditer(text))
    return [(a[2], b[2], b[1]) for a, b in zip(blocks, blocks[1:])
            if a[1] == "sh" and b[1] in ("json", "text") and not text[a.end():b.start()].strip()]


def listed():
    """Every page of the docs section, from docs/README.md, in order."""
    links = re.findall(r"^\d+\. \[[^]]+\]\(([^)]+)\)", (DOCS / "README.md").read_text(encoding="utf-8"), re.M)
    return [(DOCS / link).resolve() for link in links]


def folder(page):
    """The function folder a README or a walkthrough belongs to, or None for another page."""
    if page.parent == WALKS:
        return FUNCTIONS / page.stem
    return page.parent if page.parent.parent == FUNCTIONS else None


def pages():
    """Every page whose commands the tests run, as (page, folder its commands run in): the docs section, then each
    folder's README."""
    return [(p, folder(p) or ROOT) for p in listed() + [FUNCTIONS / n / "README.md" for n in FOLDERS]]


def tunes(bin):
    """True when this thinkthen has audit and diff."""
    return subprocess.run([bin, "audit", "--help"], capture_output=True).returncode == 0


class ExamplesTest(unittest.TestCase):
    def test_one_folder_per_function_each_complete(self):
        self.assertEqual(sorted(p.name for p in FUNCTIONS.iterdir()), FOLDERS)
        for name in FOLDERS:
            for part in PARTS.get(name, RUN):
                self.assertTrue((FUNCTIONS / name / part).exists(), f"{name}/{part}")

    def test_the_committed_cases_are_the_generator_output(self):
        out = Path(tempfile.mkdtemp())
        gen.main(out)
        for p in out.rglob("*"):
            if p.is_file():
                self.assertEqual(p.read_bytes(), (FUNCTIONS / p.relative_to(out)).read_bytes(), str(p))

    def test_every_json_block_on_a_page_sits_below_the_command_that_prints_it(self):
        for page, _ in pages():
            text = page.read_text(encoding="utf-8")
            printed = [block for _, block, _ in pairs(text)]
            for m in FENCE.finditer(text):
                if m[1] == "json":
                    self.assertIn(m[2], printed, f"{page.relative_to(ROOT)}: a json block with no command above it")

    def test_every_number_thinkthen_prints_on_a_page_is_in_its_answers(self):
        """The command check runs thinkthen only when a build is present. This check needs none."""
        for page, cwd in pages():
            if folder(page) is None:
                continue
            text = "".join(p.read_text(encoding="utf-8") for p in answers(cwd))
            said = set(DECIMAL.findall(text)) | {format(Decimal(x), "f") for x in EXPONENT.findall(text)}
            for command, block, kind in pairs(page.read_text(encoding="utf-8")):
                if kind == "json" and BUILD.search(command):
                    for number in DECIMAL.findall(block):
                        self.assertTrue(number in said, f"{page.relative_to(ROOT)} quotes {number}")

    def test_every_number_in_a_pages_prose_is_shown_in_a_block_or_code_on_it(self):
        """A decimal, or a whole number with thousands commas, in a page's prose must appear in a fenced block or a code
        span on the same page. The blocks are proven by the command check, so the prose cannot drift from the run."""
        for page, _ in pages():
            if page == ROOT / "README.md":
                continue  # the front page's numbers are checked against table.py in test_table.py
            text = page.read_text(encoding="utf-8")
            prose = FENCE.sub("", text)
            shown = "".join(m[0] for m in FENCE.finditer(text)) + "".join(CODE.findall(prose))
            known = set(DECIMAL.findall(shown)) | {format(Decimal(x), "f") for x in EXPONENT.findall(shown)}
            for number in DECIMAL.findall(CODE.sub("", prose)):
                self.assertTrue(number in known, f"{page.relative_to(ROOT)} says {number}")
            for number in GROUPED.findall(CODE.sub("", prose)):
                self.assertTrue(number in shown or number.replace(",", "") in shown,
                                f"{page.relative_to(ROOT)} says {number}")

    def test_the_docs_list_names_every_walkthrough_and_each_has_the_form(self):
        pages_listed = listed()
        for p in pages_listed:
            self.assertTrue(p.exists(), p)
        for name in FOLDERS:
            page = WALKS / f"{name}.md"
            self.assertIn(page, pages_listed)
            text = page.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# How to "), name)
            self.assertEqual([h for h in text.splitlines() if h in FORM], FORM, name)

    def test_each_readme_links_its_site_page_and_states_both_lessons(self):
        """The site links each folder by name, and each README links back to its page."""
        for name in FOLDERS:
            text = (FUNCTIONS / name / "README.md").read_text(encoding="utf-8")
            self.assertIn(f"]({SITE.format(name)})", text, name)
            for lesson in LESSONS:
                self.assertIn(lesson, text, name)


class ArgumentTest(unittest.TestCase):
    def setUp(self):
        self.env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        self.env["THINKTHEN_BIN"] = "/nonexistent/thinkthen"
        self.env["PATH"] = "/usr/bin:/bin"  # no thinkthen: a run that got past its arguments would fail another way

    def test_a_live_example_run_without_an_output_folder_refuses_and_writes_nothing(self):
        for name in [n for n in FOLDERS if n != "diff"]:
            before = sorted((p, p.stat().st_mtime_ns) for p in (FUNCTIONS / name).rglob("*"))
            done = subprocess.run([str(EXAMPLE), name, "live"], env=self.env, capture_output=True, text=True)
            self.assertEqual(done.returncode, 2, name)
            self.assertIn("live needs an output folder", done.stderr, name)
            self.assertEqual(sorted((p, p.stat().st_mtime_ns) for p in (FUNCTIONS / name).rglob("*")), before, name)

    def test_run_refuses_what_it_does_not_take_with_its_usage(self):
        bad = [(n, args) for n in FOLDERS for args in (["bogus"], ["threshold"], ["live", "threshold"],
                                                         ["threshold", "high"], ["threshold", "0.5 --no-cache"])]
        bad += [(n, ["threshold", "0.3:0.7"]) for n in ("score", "rank", "find", "annotate")]  # one cut only
        for name, args in bad:
            done = subprocess.run([str(FUNCTIONS / name / "run"), *args], env=self.env, capture_output=True, text=True)
            self.assertEqual((done.returncode, done.stdout), (2, ""), f"{name} {args}")
            self.assertTrue(done.stderr.startswith("usage: ./run "), f"{name} {args}: {done.stderr}")


@unittest.skipUnless(shutil.which("jq"), "jq is missing")
class ExamplePageTest(unittest.TestCase):
    def test_each_command_on_a_page_prints_the_block_below_it(self):
        """A command that calls thinkthen runs only when a build is present, with no key and no address. Every such
        command answers from a recording or reads saved answers, so it sends no request."""
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        bin_dir = Path(tempfile.mkdtemp())
        if BIN and Path(BIN).exists():
            (bin_dir / "thinkthen").symlink_to(Path(BIN).resolve())
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        for page, cwd in pages():
            found = pairs(page.read_text(encoding="utf-8"))
            if folder(page) is not None:
                self.assertTrue(found, page)
            for command, block, _ in found:
                if BUILD.search(command) and not (bin_dir / "thinkthen").exists():
                    continue
                got = subprocess.run(["sh", "-c", command], cwd=cwd, env=env, capture_output=True, text=True)
                self.assertEqual(got.stdout, block, f"{page.relative_to(ROOT)}: {command}\n{got.stderr}")


@unittest.skipUnless(BIN and Path(BIN).exists(), "the thinkthen command is missing")
class ExampleReplayTest(unittest.TestCase):
    def setUp(self):
        self.env = {k: v for k, v in os.environ.items() if k != "THINKTHEN_API_KEY"}
        self.env["THINKTHEN_BIN"] = BIN

    def test_each_example_replays_with_no_key_byte_for_byte(self):
        env = self.env
        for name in [n for n in FOLDERS if n not in TUNING]:
            here = FUNCTIONS / name
            shutil.rmtree(here / "replay", ignore_errors=True)
            subprocess.run([str(EXAMPLE), name, "replay"], check=True, env=env, capture_output=True)
            for committed in answers(here):
                replayed = here / "replay" / committed.relative_to(here)
                self.assertEqual(replayed.read_bytes(), committed.read_bytes(), str(committed.relative_to(ROOT)))
            self.assertEqual(sorted(p.name for p in (here / "replay" / "lists").glob("*")),
                             sorted(p.name for p in (here / "lists").glob("*")), name)

    def test_audit_replays_and_regrades_with_no_key_byte_for_byte(self):
        if not tunes(BIN):
            self.skipTest("this thinkthen has no audit or diff")
        here = FUNCTIONS / "audit"
        shutil.rmtree(here / "replay", ignore_errors=True)
        subprocess.run([str(EXAMPLE), "audit", "replay"], check=True, env=self.env, capture_output=True)
        self.assertEqual(sorted(p.name for p in (here / "replay").glob("audit-*.json")),
                         sorted(p.name for p in here.glob("audit-*.json")))
        for committed in answers(here):
            replayed = here / "replay" / committed.name
            self.assertEqual(replayed.read_bytes(), committed.read_bytes(), str(committed.relative_to(ROOT)))

    def test_diff_writes_the_committed_flips_with_no_key(self):
        if not tunes(BIN):
            self.skipTest("this thinkthen has no audit or diff")
        here = FUNCTIONS / "diff"
        shutil.rmtree(here / "replay", ignore_errors=True)
        subprocess.run([str(ROOT / "scripts" / "score" / "context_diff.sh"), str(FUNCTIONS / "audit"), str(here / "replay")],
                       check=True, env=self.env, capture_output=True)
        self.assertEqual((here / "replay" / "diff.jsonl").read_bytes(), (here / "diff.jsonl").read_bytes())


if __name__ == "__main__":
    unittest.main()
