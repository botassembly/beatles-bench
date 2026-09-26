#!/usr/bin/env python3
"""Figure 9: the wall time of every answer, per model. The baselines call no model, so they are left out."""
from common import kuva, systems, table

chosen = systems(models_only=True)
rows = [(r["system"], float(r["wall_s"])) for r in table("latency") if r["system"] in chosen]
kuva("box", ["system", "seconds"], rows, "9-latency", "--group-col", "system", "--value-col", "seconds", "--y-min", 0,
     "--y-label", "seconds per answer", "--title", "Time per answer", "--width", 700, "--height", 520)
