#!/usr/bin/env python3
"""Figure 5: accuracy against the song's 2024 page views, in four bins of equal share (log scale)."""
from common import kuva, systems, table

rows = [(r["system"], float(r["median_views"]), float(r["accuracy"])) for s in systems() for r in table("popularity") if r["system"] == s]
kuva("line", ["system", "views", "accuracy"], rows, "5-popularity", "--x", "views", "--y", "accuracy", "--color-by", "system",
     "--legend", "--log-x", "--y-min", 0, "--y-max", 1, "--x-label", "median 2024 page views of the song, per quarter",
     "--y-label", "accuracy", "--title", "Accuracy against song popularity", "--width", 900, "--height", 600)
