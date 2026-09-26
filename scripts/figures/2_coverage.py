#!/usr/bin/env python3
"""Figure 2 (the main figure): accuracy against coverage as the cut on each system's probability moves."""
from common import kuva, systems, table

chosen = systems()
rows = [(r["system"], float(r["coverage"]), float(r["accuracy"])) for s in chosen for r in table("coverage") if r["system"] == s]
kuva("line", ["system", "coverage", "accuracy"], rows, "2-coverage", "--x", "coverage", "--y", "accuracy", "--color-by", "system",
     "--legend", "--x-min", 0, "--x-max", 1, "--y-min", 0.3, "--y-max", 1, "--x-label", "share of questions answered",
     "--y-label", "accuracy of the answered", "--title", "Accuracy against coverage as the bar rises", "--width", 900, "--height", 600)
