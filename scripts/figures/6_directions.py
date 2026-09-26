#!/usr/bin/env python3
"""Figure 6: single facts against two chained facts, and forward against reverse, with 95% intervals, one panel per
system. Single hop asks each fact alone; multi-hop chains two. Reversal and reversal-general ask a pair from the
famous end (forward) and the obscure end (reverse)."""
from common import intervals, kuva, panels, systems, table

SCOPES = [("single-hop", "one fact"), ("multi-hop", "two facts"), ("reversal:forward", "Beatles forward"),
          ("reversal:reverse", "Beatles reverse"), ("reversal-general:forward", "general forward"),
          ("reversal-general:reverse", "general reverse")]
acc = {(r["system"], r["scope"]): r for r in table("accuracy")}
stems = []
for i, s in enumerate(systems()):
    groups = [(name, float(acc[s, sc]["accuracy"]), float(acc[s, sc]["lo"]), float(acc[s, sc]["hi"])) for sc, name in SCOPES]
    stems.append(kuva("box", ["scope", "accuracy"], intervals(groups), f"6-part{i}", "--group-col", "scope", "--value-col", "accuracy",
                      "--y-min", 0, "--y-max", 1, "--title", s, "--width", 700, "--height", 420))
half = (len(stems) + 1) // 2
from common import OUT  # noqa: E402
panels(stems[:half], "6-row0")
if stems[half:]:
    panels(stems[half:], "6-row1")
    panels([OUT / "6-row0", OUT / "6-row1"], "6-directions", across=False)
else:
    for ext in ("svg", "png"):
        (OUT / f"6-row0.{ext}").rename(OUT / f"6-directions.{ext}")
