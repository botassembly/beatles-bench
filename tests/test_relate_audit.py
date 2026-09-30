"""relate_audit.py builds audit's rows and key lines from a run's relate outputs and splits cases with a seed."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("relate_audit", ROOT / "scripts" / "score" / "relate_audit.py")
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)


def suite_cases(test):
    return [json.loads(l) for l in open(ROOT / "questions" / "suite" / "relate.jsonl", encoding="utf-8")
            if json.loads(l)["test"] == test]


def kinds_for(case):
    qset = next(a[1:] for a in case["args"] if a.startswith("@"))
    qfile = json.loads((ROOT / "questions" / "suite" / qset).read_text(encoding="utf-8"))
    return {r["name"]: (r["source"], r["target"]) for r in qfile["relate"]["relations"]}


class RelateAuditTest(unittest.TestCase):

    def test_rows_and_key_lines_carry_what_audit_reads(self):
        asked = suite_cases("solo")[:2]
        outs = {c["id"]: {"rows": [{"value": [{"relation": "sung_by",
                                               "source": {"name": "Taxman", "kind": "song"},
                                               "target": {"name": "George Harrison", "kind": "person"},
                                               "p": 0.9}],
                                    "question": {}, "meta": {}}]}
                for c in asked}
        kinds = {c["id"]: kinds_for(c) for c in asked}
        rows, key = ra.group_files("solo", asked, outs, kinds)
        self.assertEqual([r["input"]["id"] for r in rows], [c["id"] for c in asked])  # --id finds each case
        for r in rows:
            self.assertIn("value", r)  # the low-cut edges the audit grades
        self.assertEqual(len(key), len(asked))
        for k, c in zip(key, asked):
            self.assertEqual(k["id"], c["id"])
            self.assertIn(k["part"], ("tune", "held"))
            self.assertEqual([(e["relation"], e["source"]["name"], e["target"]["name"]) for e in k["value"]],
                             [tuple(t) for t in c["truth"]])
            rels = kinds[c["id"]]
            for e in k["value"]:
                self.assertEqual(e["source"]["kind"], rels[e["relation"]][0])
                self.assertEqual(e["target"]["kind"], rels[e["relation"]][1])

    def test_the_seeded_split_is_half_and_stable_across_runs(self):
        ids = [c["id"] for c in suite_cases("solo")]
        tune = ra.tune_ids("solo", ids)
        self.assertEqual(tune, ra.tune_ids("solo", ids))  # the same call answers the same way
        self.assertEqual(len(tune), len(ids) // 2)
        self.assertTrue(tune <= set(ids))
        # the committed suite's order pins the split: these tune halves score the run's published held rows
        self.assertEqual(tune, {"relate-solo-02", "relate-solo-06", "relate-solo-07", "relate-solo-08",
                                "relate-solo-12", "relate-solo-14", "relate-solo-15", "relate-solo-16"})
        for test in ("duet", "wrong-album-only", "links"):
            ids = [c["id"] for c in suite_cases(test)]
            self.assertEqual(len(ra.tune_ids(test, ids)), len(ids) // 2)


if __name__ == "__main__":
    unittest.main()
