#!/usr/bin/env python3
"""Figure 4: accuracy by category with 95% Wilson intervals, one panel per system. kuva has no error bars, so each
box spans the interval and its line marks the accuracy."""
from common import intervals, kuva, panels, systems, table

acc = table("accuracy")
cats = [r["scope"] for r in acc if r["system"] == "chance" and ":" not in r["scope"]]
NAMES = {"beatles-only": "Beatles only", "near-neighbor": "near neighbor", "near-neighbor-control": "near control",
         "lexical-trap": "trap", "lexical-trap-control": "trap control", "none-of-these": "none of these",
         "reversal-general": "general", "reversal-general-shared-name": "general, shared name"}
stems = []
for i, s in enumerate(systems()):
    groups = [(NAMES.get(r["scope"], r["scope"]), float(r["accuracy"]), float(r["lo"]), float(r["hi"])) for c in cats for r in acc if r["system"] == s and r["scope"] == c]
    stems.append(kuva("box", ["scope", "accuracy"], intervals(groups), f"4-part{i}", "--group-col", "scope", "--value-col", "accuracy",
                      "--y-min", 0, "--y-max", 1, "--title", f"{s}: accuracy by category, 95% intervals", "--width", 2200, "--height", 420))
panels(stems, "4-accuracy", across=False)
