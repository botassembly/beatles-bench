#!/usr/bin/env python3
"""Figure 3: calibration. Accuracy against mean probability in ten bins, per model, beside the diagonal of perfect
calibration. Bins with fewer than 10 answers are left out. The baselines' scores are not probabilities, so only the
models are drawn. results/tables/ece.tsv holds every system's expected calibration error."""
from decimal import ROUND_HALF_UP, Decimal

from common import kuva, systems, table


def three(text):
    """A table value rounded half up to three places. Formatting the float would round 0.0305 down to 0.030."""
    return Decimal(text).quantize(Decimal("0.001"), ROUND_HALF_UP)


ece = {r["system"]: r for r in table("ece")}
rows = [("perfect calibration", 0, 0), ("perfect calibration", 1, 1)]
for s in systems(models_only=True):
    e = ece[s]
    name = f"{s} (ECE {three(e['ece'])}, {three(e['lo'])} to {three(e['hi'])})"
    rows += [(name, float(r["mean_confidence"]), float(r["accuracy"])) for r in table("calibration") if r["system"] == s and int(r["n"]) >= 10]
kuva("line", ["system", "probability", "accuracy"], rows, "3-calibration", "--x", "probability", "--y", "accuracy",
     "--color-by", "system", "--legend", "--x-min", 0, "--x-max", 1, "--y-min", 0, "--y-max", 1,
     "--x-label", "mean probability of the answer given", "--y-label", "share right", "--title", "Calibration", "--width", 900, "--height", 650)
