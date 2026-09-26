#!/usr/bin/env python3
"""Figure 7: cost per 1,000 right answers against accuracy, beside median time per answer against accuracy.
Cost comes from recorded tokens and scripts/score/prices.tsv; a baseline calls no model and costs nothing. The time panel
shows the models only, because a baseline's time is its scoring time on this machine, not an answer's."""
from common import kuva, panels, systems, table

acc = {r["system"]: float(r["accuracy"]) for r in table("accuracy") if r["scope"] == "overall"}
cost = {r["system"]: r for r in table("cost")}
chosen = [s for s in systems() if cost[s]["usd_per_1000_right"] and cost[s]["median_s"]]
a = kuva("scatter", ["system", "usd", "accuracy"], [(s, float(cost[s]["usd_per_1000_right"]), acc[s]) for s in chosen], "7-cost",
         "--x", "usd", "--y", "accuracy", "--color-by", "system", "--legend", "--size", 7, "--y-min", 0, "--y-max", 1, "--x-min", 0,
         "--x-label", "dollars per 1,000 right answers", "--y-label", "accuracy", "--title", "Cost", "--width", 700, "--height", 520)
b = kuva("scatter", ["system", "seconds", "accuracy"], [(s, float(cost[s]["median_s"]), acc[s]) for s in chosen if s in systems(models_only=True)], "7-speed",
         "--x", "seconds", "--y", "accuracy", "--color-by", "system", "--legend", "--size", 7, "--y-min", 0, "--y-max", 1, "--log-x",
         "--x-label", "median seconds per answer (log)", "--y-label", "accuracy", "--title", "Time", "--width", 700, "--height", 520)
panels([a, b], "7-cost-time")
