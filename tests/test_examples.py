"""examples/ holds one folder per talk slide that shows bench data. Twelve hold a function example: one per function,
then audit and diff. The site links each of those by its name. Each function folder replays with no key. The other ten
hold a README.md that names the slide's claims, their sources, their check, and their build. examples/README.md indexes
every slide of the talk in its order. Each page quotes only numbers its committed answers or its own blocks hold, and each command on a
page prints the block below it. The pages are each folder's README.md, data/README.md, and the section "Context and cost"
of reports/open-book.md. The website holds the longer walkthroughs.

The number check reads every fenced json block in those pages, and the prose of every page."""
import json
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
EXAMPLES = ROOT / "examples"
FOLDERS = ["annotate", "audit", "choose", "decide", "diff", "filter", "find", "rank", "recognize", "relate", "score", "tag"]
SLIDES = ["bench", "bench-run", "catches", "jev", "know-this", "open-book", "recognize-how", "sql", "strings", "what-jev-knows"]
# The talk's slides in its order on 2026-09-26. The index gives one row to each.
TALK = ["title", "strings", "jev", "bench", "runs-in", "decide", "choose", "tag", "score", "filter", "filter-live", "rank",
        "find", "annotate", "recognize", "recognize-how", "relate", "audit", "diff", "scripting", "systems", "sql", "frames",
        "what-jev-knows", "catches", "open-book", "know-this", "bench-run", "backends", "close"]
ROW = re.compile(r"^\| (\d+) \| ([a-z-]+) \| [^|]+ \| ([^|]+) \|", re.M)
SHA = re.compile(r"^THINKTHEN_BIN SHA-256: [0-9a-f]{64}$", re.M)
TUNING = ["audit", "diff"]  # only thinkthen main at e70bddab or later has audit and diff
RUN = ("README.md", "slide.png", "run", "outputs.jsonl", "timing.tsv", "recording")
PARTS = {"audit": RUN + ("key.jsonl", "audit-context.jsonl", "rows.jsonl", "rows-context.jsonl", "audit-asrun.json"),
         "diff": ("README.md", "slide.png", "run", "diff.jsonl")}
# Pages outside examples/ whose commands run from the top folder, each with the sections the checks read: the sections
# that once formed the pages "The data" and "Context and cost".
MERGED = [(ROOT / "data" / "README.md", ["## One row", "## From a row to a question", "## How Jev answered it", "## The catalog"]),
          (ROOT / "reports" / "open-book.md", ["## Context and cost"])]
EXAMPLE = ROOT / "scripts" / "run" / "example.sh"
SITE = "https://thinkthen.dev/learn/beatles-bench/{}/"
LESSONS = ("- **You control the bar.** ", "- **The number is the number.** ")
FENCE = re.compile(r"^```(\w*)\n(.*?)^```\n?", re.S | re.M)
CODE = re.compile(r"`[^`\n]+`")
BUILD = re.compile(r"(?:^|[\s|])thinkthen\s|run\.sh|example\.sh|^\./run\b")  # a command that runs the thinkthen command
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
DECIMAL = re.compile(r"-?\d+\.\d+")
GROUPED = re.compile(r"(?<![\d.,])\d{1,3}(?:,\d{3})+(?![\d,]\d)")
# thinkthen writes a small p as 2e-6; jq prints 0.000002. A whole token only, with at most three exponent digits: a hex
# request key holds runs like 7e9877975802, and formatting that as a decimal would build a string of billions of digits.
EXPONENT = re.compile(r"(?<![0-9A-Za-z_.])-?\d+(?:\.\d+)?e-?\d{1,3}(?![0-9A-Za-z_.])")
sys.path.insert(0, str(ROOT / "scripts" / "generate"))
sys.path.insert(0, str(ROOT / "tests"))
import examples as gen  # noqa: E402
from builds import bench_bin, bin_for, build_id, pinned_commit  # noqa: E402

# recognize and relate keep old-form recordings: 0.1.0's planners ask different questions, so their answers cannot
# be converted without changing them. They replay only under the build their run.txt names.
OLD_FORM = {"recognize", "relate"}


def answers(folder):
    """Every committed file a page may quote: the answers and the lists, or what audit and diff wrote from them."""
    if folder.name == "diff":
        return [folder / "diff.jsonl", *answers(EXAMPLES / "audit")]
    tuned = []
    if folder.name == "audit":
        tuned = [folder / "rows.jsonl", folder / "rows-context.jsonl", *sorted(folder.glob("audit-*.json"))]
    return [folder / "outputs.jsonl", *sorted((folder / "lists").glob("*.jsonl")), *tuned]


def pairs(text):
    """Each sh block that sits right above a json or text block, with that block: (command, output, json or text)."""
    blocks = list(FENCE.finditer(text))
    return [(a[2], b[2], b[1]) for a, b in zip(blocks, blocks[1:])
            if a[1] == "sh" and b[1] in ("json", "text") and not text[a.end():b.start()].strip()]


def folder(page):
    """The function folder a README belongs to, or None for another page."""
    return page.parent if page.parent.parent == EXAMPLES else None


def checked(page, headings):
    """The part of a page the checks read: all of it, or the named sections, each up to the next heading of its level."""
    text = page.read_text(encoding="utf-8")
    if headings is None:
        return text
    parts = []
    for heading in headings:
        part = text[text.index(heading + "\n"):]
        end = part.find("\n" + heading.split(" ")[0] + " ", 1)
        parts.append(part if end == -1 else part[:end + 1])
    return "".join(parts)


def pages():
    """Every page whose commands the tests run, as (page, folder its commands run in, the text checked): the merged
    pages, then each folder's README."""
    return ([(p, ROOT, checked(p, h)) for p, h in MERGED]
            + [(p, p.parent, checked(p, None)) for p in (EXAMPLES / n / "README.md" for n in FOLDERS)])


def tunes(bin):
    """True when this thinkthen has audit and diff."""
    return subprocess.run([bin, "audit", "--help"], capture_output=True).returncode == 0


class ExamplesTest(unittest.TestCase):
    def test_one_folder_per_function_each_complete(self):
        self.assertEqual(sorted(p.name for p in EXAMPLES.iterdir()), sorted(FOLDERS + SLIDES + ["README.md"]))
        for name in FOLDERS:
            for part in PARTS.get(name, RUN):
                self.assertTrue((EXAMPLES / name / part).exists(), f"{name}/{part}")
        for name in SLIDES:
            self.assertEqual([p.name for p in (EXAMPLES / name).iterdir()], ["README.md"], name)

    def test_the_index_gives_each_slide_one_row_in_the_talks_order(self):
        rows = ROW.findall((EXAMPLES / "README.md").read_text(encoding="utf-8"))
        self.assertEqual([(int(n), name) for n, name, _ in rows], list(enumerate(TALK, 1)))
        linked = {}
        for _, name, cell in rows:
            m = re.fullmatch(r"\[([a-z-]+)/\]\(([a-z-]+)/\)", cell.strip())
            if m:
                self.assertEqual((m[1], m[2]), (name, name), name)
                self.assertTrue((EXAMPLES / name / "README.md").exists(), name)
                linked[name] = linked.get(name, 0) + 1
            else:
                self.assertIn(cell.strip(), ("the deck holds it", "no bench data"), name)
        self.assertEqual(linked, {n: 1 for n in FOLDERS + SLIDES})

    def test_each_recording_is_a_question_store_or_its_pinned_old_form(self):
        """0.1.0 replays a question store: one thinkthen.jsonl, every line parsing, no old entries, folder markers,
        .locks, or thinkthen.sqlite. The folders in OLD_FORM keep the old form because 0.1.0 asks other questions."""
        for name in FOLDERS:
            rec = EXAMPLES / name / "recording"
            if not rec.is_dir():
                continue
            names = [p.name for p in rec.iterdir()]
            if name in OLD_FORM:
                self.assertNotIn("thinkthen.jsonl", names, name)
                self.assertTrue(any(n.endswith(".json") for n in names), name)
                continue
            self.assertEqual(names, ["thinkthen.jsonl"], name)
            for i, line in enumerate(rec.joinpath("thinkthen.jsonl").open(encoding="utf-8"), 1):
                self.assertIsInstance(json.loads(line), dict, f"{name} line {i}")

    def test_each_recorded_folder_names_its_build(self):
        recorded = [n for n in FOLDERS if (EXAMPLES / n / "recording").is_dir()]
        self.assertEqual(len(recorded), 11)
        for name in recorded:
            text = (EXAMPLES / name / "run.txt").read_text(encoding="utf-8")
            self.assertRegex(text, SHA, name)
            self.assertRegex(text, r"(?m)^thinkthen: thinkthen ", name)
            self.assertRegex(text, r"(?m)^model the backend reported: \S+$", name)
            self.assertRegex(text, r"(?m)^date: \d{4}-\d{2}-\d{2}$", name)
        self.assertIn("../audit/run.txt", (EXAMPLES / "diff" / "README.md").read_text(encoding="utf-8"))

    def test_the_committed_cases_are_the_generator_output(self):
        out = Path(tempfile.mkdtemp())
        gen.main(out)
        for p in out.rglob("*"):
            if p.is_file():
                self.assertEqual(p.read_bytes(), (EXAMPLES / p.relative_to(out)).read_bytes(), str(p))

    def test_every_json_block_on_a_page_sits_below_the_command_that_prints_it(self):
        for page, _, text in pages():
            printed = [block for _, block, _ in pairs(text)]
            for m in FENCE.finditer(text):
                if m[1] == "json":
                    self.assertIn(m[2], printed, f"{page.relative_to(ROOT)}: a json block with no command above it")

    def test_a_small_p_is_read_and_a_hex_key_is_not(self):
        """A hex request key once matched as 7e9877975802, and formatting it ran the suite out of memory."""
        for text, found in [("2e-6", ["2e-6"]), ("-1.5e3", ["-1.5e3"]), ('"p": 4e-05}', ["4e-05"]),
                            ('"ab17e9877975802c"', []), ('"4e880cdf6"', []), ("1e9877975802", []), ("x2e-6", [])]:
            self.assertEqual(EXPONENT.findall(text), found, text)

    def test_every_number_thinkthen_prints_on_a_page_is_in_its_answers(self):
        """The command check runs thinkthen only when a build is present. This check needs none."""
        for page, cwd, page_text in pages():
            if folder(page) is None:
                continue
            text = "".join(p.read_text(encoding="utf-8") for p in answers(cwd))
            said = set(DECIMAL.findall(text)) | {format(Decimal(x), "f") for x in EXPONENT.findall(text)}
            for command, block, kind in pairs(page_text):
                if kind == "json" and BUILD.search(command):
                    for number in DECIMAL.findall(block):
                        self.assertTrue(number in said, f"{page.relative_to(ROOT)} quotes {number}")

    def test_every_number_in_a_pages_prose_is_shown_in_a_block_or_code_on_it(self):
        """A decimal, or a whole number with thousands commas, in a page's prose must appear in a fenced block or a code
        span on the same page. The blocks are proven by the command check, so the prose cannot drift from the run."""
        for page, _, text in pages():
            prose = FENCE.sub("", text)
            shown = "".join(m[0] for m in FENCE.finditer(text)) + "".join(CODE.findall(prose))
            known = set(DECIMAL.findall(shown)) | {format(Decimal(x), "f") for x in EXPONENT.findall(shown)}
            for number in DECIMAL.findall(CODE.sub("", prose)):
                self.assertTrue(number in known, f"{page.relative_to(ROOT)} says {number}")
            for number in GROUPED.findall(CODE.sub("", prose)):
                self.assertTrue(number in shown or number.replace(",", "") in shown,
                                f"{page.relative_to(ROOT)} says {number}")

    def test_each_readme_links_its_site_page_and_states_both_lessons(self):
        """The site links each folder by name, and each README links back to its page."""
        for name in FOLDERS:
            text = (EXAMPLES / name / "README.md").read_text(encoding="utf-8")
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
            before = sorted((p, p.stat().st_mtime_ns) for p in (EXAMPLES / name).rglob("*"))
            done = subprocess.run([str(EXAMPLE), name, "live"], env=self.env, capture_output=True, text=True)
            self.assertEqual(done.returncode, 2, name)
            self.assertIn("live needs an output folder", done.stderr, name)
            self.assertEqual(sorted((p, p.stat().st_mtime_ns) for p in (EXAMPLES / name).rglob("*")), before, name)

    def test_run_refuses_what_it_does_not_take_with_its_usage(self):
        bad = [(n, args) for n in FOLDERS for args in (["bogus"], ["threshold"], ["live", "threshold"],
                                                         ["threshold", "high"], ["threshold", "0.5 --no-cache"])]
        bad += [(n, ["threshold", "0.3:0.7"]) for n in ("score", "rank", "find", "annotate")]  # one cut only
        for name, args in bad:
            done = subprocess.run([str(EXAMPLES / name / "run"), *args], env=self.env, capture_output=True, text=True)
            self.assertEqual((done.returncode, done.stdout), (2, ""), f"{name} {args}")
            self.assertTrue(done.stderr.startswith("usage: ./run "), f"{name} {args}: {done.stderr}")


def needed(command, cwd):
    """The thinkthen a page command needs: BIN, or the BENCH_BIN_<build> for the run or folder whose recording the
    command replays. Returns (command path, None) or (None, a reason naming the build and the variable)."""
    m = re.search(r"--replay\s+(\S+)", command)
    if m:
        rec = (cwd / m.group(1)).resolve()
        if str(rec).startswith(str(ROOT / "results")):
            return bin_for(rec)
        if rec.name == "recording" and rec.parent.is_dir():
            if (rec / "thinkthen.jsonl").exists():
                return BIN, None
            commit = build_id(pinned_commit(rec.parent))
            if commit:
                bin = bench_bin(commit)
                return (bin, None) if bin else (None, f"{rec.parent.relative_to(ROOT)} binds to thinkthen "
                                                      f"{commit}; set BENCH_BIN_{commit}")
        return BIN, None
    fld = cwd if cwd.parent == EXAMPLES else None
    if fld and (fld / "recording").is_dir() and not (fld / "recording" / "thinkthen.jsonl").exists():
        commit = build_id(pinned_commit(fld))
        if commit:
            bin = bench_bin(commit)
            return (bin, None) if bin else (None, f"{fld.relative_to(ROOT)} binds to thinkthen {commit}; "
                                                  f"set BENCH_BIN_{commit}")
    return BIN, None


@unittest.skipUnless(shutil.which("jq"), "jq is missing")
class ExamplePageTest(unittest.TestCase):
    def test_each_command_on_a_page_prints_the_block_below_it(self):
        """A command that calls thinkthen runs only when a build is present, with no key and no address. Every such
        command answers from a recording or reads saved answers, so it sends no request. A command that replays a
        results/ recording or an old-form example folder runs only under the build that recorded it."""
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        bin_dirs = {}
        skipped = []
        for page, cwd, text in pages():
            found = pairs(text)
            if folder(page) is not None:
                self.assertTrue(found, page)
            for command, block, _ in found:
                bin = None
                if BUILD.search(command):
                    bin, why = needed(command, cwd)
                    if not bin:
                        skipped.append(why or f"{page.relative_to(ROOT)}: no thinkthen")
                        continue
                if bin:
                    key = str(Path(bin).resolve())
                    if key not in bin_dirs:
                        d = Path(tempfile.mkdtemp())
                        (d / "thinkthen").symlink_to(Path(bin).resolve())
                        bin_dirs[key] = d
                    env["PATH"] = f"{bin_dirs[key]}{os.pathsep}{os.environ.get('PATH', '')}"
                got = subprocess.run(["sh", "-c", command], cwd=cwd, env=env, capture_output=True, text=True)
                self.assertEqual(got.stdout, block, f"{page.relative_to(ROOT)}: {command}\n{got.stderr}")
        if skipped:
            self.skipTest("; ".join(skipped))


def example_bin(name):
    """The command an example's recording replays under: BIN for a question store, else the BENCH_BIN_<build> of the
    build its run.txt names. Returns (command, None) or (None, a reason naming the build and the variable)."""
    here = EXAMPLES / name
    if not (here / "recording").is_dir() or (here / "recording" / "thinkthen.jsonl").exists():
        return BIN, None
    commit = build_id(pinned_commit(here))
    if not commit:
        return BIN, None
    bin = bench_bin(commit)
    return (bin, None) if bin else (None, f"examples/{name} binds to thinkthen {commit}; set BENCH_BIN_{commit}")


@unittest.skipUnless(BIN and Path(BIN).exists(), "the thinkthen command is missing")
class ExampleReplayTest(unittest.TestCase):
    def setUp(self):
        self.env = {k: v for k, v in os.environ.items() if k != "THINKTHEN_API_KEY"}
        self.env["THINKTHEN_BIN"] = BIN

    def test_each_example_replays_with_no_key_byte_for_byte(self):
        skipped = []
        for name in [n for n in FOLDERS if n not in TUNING]:
            bin, why = example_bin(name)
            if not bin:
                skipped.append(why)
                continue
            here = EXAMPLES / name
            shutil.rmtree(here / "replay", ignore_errors=True)
            subprocess.run([str(EXAMPLE), name, "replay"], check=True, env={**self.env, "THINKTHEN_BIN": bin},
                           capture_output=True)
            for committed in answers(here):
                replayed = here / "replay" / committed.relative_to(here)
                self.assertEqual(replayed.read_bytes(), committed.read_bytes(), str(committed.relative_to(ROOT)))
            self.assertEqual(sorted(p.name for p in (here / "replay" / "lists").glob("*")),
                             sorted(p.name for p in (here / "lists").glob("*")), name)
        if skipped:
            self.skipTest("; ".join(skipped))

    def test_audit_replays_and_regrades_with_no_key_byte_for_byte(self):
        if not tunes(BIN):
            self.skipTest("this thinkthen has no audit or diff")
        here = EXAMPLES / "audit"
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
        here = EXAMPLES / "diff"
        shutil.rmtree(here / "replay", ignore_errors=True)
        subprocess.run([str(ROOT / "scripts" / "score" / "context_diff.sh"), str(EXAMPLES / "audit"), str(here / "replay")],
                       check=True, env=self.env, capture_output=True)
        self.assertEqual((here / "replay" / "diff.jsonl").read_bytes(), (here / "diff.jsonl").read_bytes())


class RecognizeHowTest(unittest.TestCase):
    """The recognize-how slide: each word's answers and the names they join into, from a replay with --details."""

    def setUp(self):
        bin, why = example_bin("recognize")
        if not bin:
            self.skipTest(why)
        self.bin = bin

    def run_recognize(self, *args):
        here = EXAMPLES / "recognize"
        case = json.loads((here / "recognize-cold.jsonl").read_text(encoding="utf-8").splitlines()[0])
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        done = subprocess.run([self.bin, "recognize", "person", "song", "album", "place", "--threshold", "0.01", *args],
                              input=case["records"][0]["input"], cwd=here, env=env, capture_output=True, text=True, check=True)
        return json.loads(done.stdout.splitlines()[0])

    def test_the_page_shows_the_replayed_words_names_and_tokens(self):
        page = (EXAMPLES / "recognize-how" / "README.md").read_text(encoding="utf-8")
        got = self.run_recognize("--replay", "recording", "--details")
        kinds = list(got["question"]["kinds"])
        words = []
        for i, t in enumerate(got["answer"]["tokens"], 1):
            kp = t["kind_probabilities"]
            self.assertEqual(sorted(kp)[-1] > sorted(kp)[-2], True, t["token"])  # one top kind
            words.append((t["token"], t["detection_probability"], kinds[kp.index(max(kp))]))
            self.assertIn(f"| {i} | {words[-1][0]} | {words[-1][1]} | {words[-1][2]} |\n", page)
        self.assertEqual(len(re.findall(r"(?m)^\| \d+ \| ", page)), len(words))
        names, i = [], 0
        while i < len(words):  # each run of words above one half is one name, of its most common kind
            if words[i][1] <= 0.5:
                i += 1
                continue
            j = i
            while j + 1 < len(words) and words[j + 1][1] > 0.5:
                j += 1
            ks = [w[2] for w in words[i:j + 1]]
            names.append((" ".join(w[0] for w in words[i:j + 1]), max(ks, key=ks.count)))
            i = j + 1
        self.assertEqual(names, [(e["name"], e["kind"]) for e in got["value"]["entities"]])
        for name, kind in names:
            self.assertIn(f"| {name} | {kind} |\n", page)
        usage = got["meta"]["usage"]
        self.assertIn(f"`{usage['input_tokens']}` input tokens and `{usage['output_tokens']}` output tokens", page)
        self.assertIn(f"`{got['meta']['model']}`", page)
        plan = self.run_recognize("--dry-run")
        self.assertEqual(plan.get("request_count", plan.get("requests")), 1)


if __name__ == "__main__":
    unittest.main()
