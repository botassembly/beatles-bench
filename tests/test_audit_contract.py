"""The contract with thinkthen audit. Python grades every published table. This test runs thinkthen audit with the key
files in questions/keys/ on the committed Jev and Laya runs, and checks that each cell audit can make equals the Python
table, rounded as the table prints it. It sends no request and needs no key. Skips without a thinkthen that has audit.

Covered cells:
- the one-text decide sets in decide.tsv: right at 0.5, yes recall at 0.5, AUC, and mean p(yes)
- the function-suite decide rows: n, right at 0.5, and TP FP TN FN at 0.3 and 0.5
- right answers as run for each question file where no tie holds the right answer
- Laya overall right answers

Cells audit cannot make yet, each with its thinkthen issue in sdlc/issues/:
- decide sets that span several question texts (multi-hop same-month, reverse singer-yes-no), and the scopes by
  category, kind, fact, and direction: 2026-09-25-audit-cannot-group-by-a-record-field.md
- right answers where a tie holds the right answer: 2026-09-25-audit-gives-no-share-to-a-tie-that-holds-the-right-answer.md
- the held-out tuned cut in decide.tsv: 2026-09-25-audit-tunes-its-cut-on-one-half-and-never-swaps.md
- ECE, its interval, and the calibration bins: 2026-09-25-audit-calibration-differs-from-the-benchs-ece-and-its-interval.md
- coverage at each confidence, and the choose coverage rows: 2026-09-25-audit-reports-coverage-at-one-rule-not-along-every-confidence.md
- the paired test between systems: 2026-09-25-diff-mcnemar-leaves-out-pairs-that-become-right-from-not-sure.md
- tag, score, filter, rank, find, annotate, recognize, and relate: 2026-09-25-audit-is-complete-for-0-1.md
"""
import csv
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from published import JEV_RUN  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BIN = os.environ.get("THINKTHEN_BIN") or shutil.which("thinkthen")
RUNS = ROOT / "results" / "runs"
TABLES = ROOT / "results" / "tables"
SYSTEMS = {"Jev": (JEV_RUN.name, "functions.tsv"),
           "Laya": ("2026-09-23-thinkthen-laya", "functions-laya.tsv")}
SPANS_SEVERAL_TEXTS = {("multi-hop", "same-month"), ("reverse", "singer-yes-no")}
COVERED_FILES = {"Jev": 7, "Laya": 15}  # question files where no tie holds the right answer, in the runs JEV names


def has_audit():
    return bool(BIN) and Path(BIN).exists() and subprocess.run([BIN, "audit", "--help"], capture_output=True).returncode == 0


def tsv(name):
    with open(TABLES / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def question_files():
    return {p.stem: [json.loads(l) for l in open(p, encoding="utf-8")] for p in sorted((ROOT / "questions").glob("*.jsonl"))}


def audit(rows, key, *args):
    """thinkthen audit on the given answer lines and key file. Returns its groups by name."""
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", encoding="utf-8") as f:
        f.writelines(rows)
        f.flush()
        env = {k: v for k, v in os.environ.items() if k not in ("THINKTHEN_API_KEY", "THINKTHEN_BASE_URL")}
        done = subprocess.run([BIN, "audit", f.name, str(key), *args], capture_output=True, text=True, env=env)
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return {g["group"]: g for g in map(json.loads, done.stdout.splitlines())}


def cell(value, places):
    return "" if value is None else round(value, places)


def num(text):
    return "" if text == "" else float(text)


def tie_holds_the_answer(row, truth):
    p = row["answer"].get("probabilities") or {}
    if row["question"]["verb"] != "choose" or not p:
        return False
    top = max(p.values())
    return sum(v == top for v in p.values()) > 1 and p.get(truth) == top


@unittest.skipUnless(has_audit(), "no thinkthen with audit")
class AuditContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = question_files()
        cls.tmp = Path(tempfile.mkdtemp())
        cls.key = cls.tmp / "key.jsonl"
        cls.key.write_bytes(b"".join((ROOT / "questions" / "keys" / f"{name}.jsonl").read_bytes() for name in cls.files))
        cls.lines = {s: open(RUNS / run / "details.jsonl", encoding="utf-8").readlines() for s, (run, _) in SYSTEMS.items()}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_one_text_decide_sets_match_decide_tsv(self):
        qs = [q for rows in self.files.values() for q in rows if q["function"] == "decide"]
        for system in SYSTEMS:
            groups = audit(self.lines[system], self.key, "--threshold", "0.5")
            covered, spans = 0, set()
            for r in (r for r in tsv("decide.tsv") if r["system"] == system):
                texts = {q["question"] for q in qs if (q["category"], q["kind"]) == (r["category"], r["kind"])}
                if len(texts) > 1:
                    spans.add((r["category"], r["kind"]))
                    continue
                g = groups[texts.pop()]
                with self.subTest(system=system, set=(r["category"], r["kind"])):
                    self.assertEqual(g["rows"], int(r["n"]))
                    self.assertEqual(g["right"], int(r["right_at_0.5"]))
                    self.assertEqual(cell(g["yes_recall"], 4), num(r["yes_recall_at_0.5"]))
                    self.assertEqual(cell(g["auc"], 3), num(r["auc"]))
                    self.assertEqual(cell(g["mean_probability"], 4), num(r["mean_p_yes"]))
                covered += 1
            self.assertEqual((covered, spans), (5, SPANS_SEVERAL_TEXTS), system)

    def test_the_function_suite_decide_rows_match(self):
        for system, (_, table) in SYSTEMS.items():
            rows = {r["measure"]: r for r in tsv(table) if r["function"] == "decide"}
            for cut in ("0.3", "0.5"):
                g = audit(self.lines[system], self.key, "--by", "verb", "--threshold", cut)["decide"]
                with self.subTest(system=system, cut=cut):
                    confusion = rows[f"TP FP TN FN at {cut}"]
                    self.assertEqual(g["rows"], int(confusion["n"]))
                    self.assertEqual(f"{g['true_yes']} {g['false_yes']} {g['true_no']} {g['false_no']}", confusion["value"])
                    if cut == "0.5":
                        accuracy = rows["accuracy at 0.5"]
                        self.assertEqual(g["rows"], int(accuracy["n"]))
                        self.assertEqual(f"{g['right'] / g['rows']:.3f}", accuracy["value"])

    def test_right_answers_per_question_file_where_no_tie_holds_the_answer(self):
        for system in SYSTEMS:
            python = {r["scope"]: r for r in tsv("accuracy.tsv") if r["system"] == system}
            by_id = {json.loads(l)["input"]["id"]: l for l in self.lines[system]}
            covered = 0
            for name, qs in self.files.items():
                if any(tie_holds_the_answer(json.loads(by_id[q["id"]]), q["truth"]) for q in qs):
                    continue
                groups = audit([by_id[q["id"]] for q in qs], ROOT / "questions" / "keys" / f"{name}.jsonl", "--by", "verb")
                with self.subTest(system=system, file=name):
                    self.assertEqual(sum(g["right"] for g in groups.values()), float(python[name]["right"]))
                covered += 1
            self.assertEqual(covered, COVERED_FILES[system], system)

    def test_laya_overall_right_answers(self):
        python = next(r for r in tsv("accuracy.tsv") if r["system"] == "Laya" and r["scope"] == "overall")
        groups = audit(self.lines["Laya"], self.key, "--by", "verb")
        self.assertEqual(sum(g["right"] for g in groups.values()), float(python["right"]))
        self.assertEqual(sum(g["tied"] for g in groups.values()), int(python["ties"]))
        self.assertEqual(sum(g["rows"] for g in groups.values()), int(python["n"]))


if __name__ == "__main__":
    unittest.main()
