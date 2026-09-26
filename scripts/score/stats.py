"""Statistics for the tables. Plain Python, no model, no network.

wilson        the 95% Wilson score interval for k right of n
mcnemar       the exact two-sided McNemar test for two systems on the same questions
calibration   accuracy by confidence bin and the expected calibration error (ECE)
ece_interval  a seeded bootstrap 95% interval for the ECE, resampling questions
coverage      accuracy against coverage as the cut on confidence moves down
cost          dollars per 1,000 questions and per 1,000 right answers from recorded tokens
quantile      a linear-interpolation quantile (the median and the 90th percentile of wall time)
edges, bin_of equal-share bins (quantile edges) for the popularity table
"""
import math
import random

Z = 1.959963984540054  # the two-sided 95% normal quantile


def wilson(k, n, z=Z):
    """The Wilson score interval for k successes of n. With n = 0 it is (0, 1)."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def mcnemar(a, b):
    """(questions only a got right, questions only b got right, exact two-sided p). a and b are lists of booleans over
    the same questions in the same order. The p value is the binomial test of the discordant pairs at one half."""
    assert len(a) == len(b)
    a_only = sum(1 for x, y in zip(a, b) if x and not y)
    b_only = sum(1 for x, y in zip(a, b) if y and not x)
    n = a_only + b_only
    if n == 0:
        return a_only, b_only, 1.0
    tail = sum(math.comb(n, i) for i in range(min(a_only, b_only) + 1)) / 2 ** n
    return a_only, b_only, min(1.0, 2 * tail)


def calibration(pairs, bins=10):
    """pairs: [(confidence, right)], where right is a share from 0 to 1. Equal-width bins over 0 to 1, the last one
    closed. A bin's right answers are the sum of its shares, as in coverage. Returns ([(low, high, n, right, mean
    confidence)], ECE), where the ECE is the size-weighted mean gap between each bin's accuracy and its mean confidence."""
    table, gap = [], 0.0
    for i in range(bins):
        lo, hi = i / bins, (i + 1) / bins
        sel = [(c, r) for c, r in pairs if lo <= c < hi or (i == bins - 1 and c == hi)]
        k = sum(r for _, r in sel)
        conf = sum(c for c, _ in sel) / len(sel) if sel else 0.0
        table.append((lo, hi, len(sel), k, conf))
        gap += abs(k - conf * len(sel))
    return table, gap / len(pairs) if pairs else 0.0


def ece_interval(pairs, bins=10, draws=1000, seed="beatles-bench"):
    """A seeded, bias-corrected bootstrap 95% interval for the ECE, resampling questions. Binned ECE grows under
    resampling, so the plain percentile interval can miss the estimate. Each resample's ECE is shifted by the mean
    resample minus the estimate before the 2.5th and 97.5th percentiles are taken. The interval covers sampling of
    questions only. It does not cover a backend giving other probabilities to the same request on a rerun."""
    r = random.Random(seed)
    _, est = calibration(pairs, bins)
    values = [calibration([pairs[r.randrange(len(pairs))] for _ in pairs], bins)[1] for _ in range(draws)]
    bias = sum(values) / len(values) - est
    shifted = sorted(max(0.0, v - bias) for v in values)
    return min(quantile(shifted, 0.025), est), max(quantile(shifted, 0.975), est)


def best_cut(pairs):
    """The cut on p(yes) with the most right answers over (p(yes), truth is yes) pairs: yes when p >= cut. The
    candidates are the distinct probabilities and 1.01 (always no). A tie goes to the cut nearest 0.5."""
    cands = sorted({p for p, _ in pairs} | {1.01})
    right = lambda c: sum((p >= c) == t for p, t in pairs)
    return max(cands, key=lambda c: (right(c), -abs(c - 0.5)))


def cross_cut(pairs, halves):
    """Two-fold cross-fitting: tune the cut on one half, score the other, and swap. Returns (right, n, [cut tuned
    on half 0, cut tuned on half 1])."""
    parts = [[p for p, h in zip(pairs, halves) if h == k] for k in (0, 1)]
    cuts = [best_cut(parts[k]) for k in (0, 1)]
    right = sum((p >= cuts[1 - k]) == t for k in (0, 1) for p, t in parts[k])
    return right, len(pairs), cuts


def coverage(pairs):
    """[(cut, answered, right)] for each distinct confidence taken as the cut, from the highest down. A question is
    answered when its confidence reaches the cut."""
    out = []
    for cut in sorted({c for c, _ in pairs}, reverse=True):
        kept = [r for c, r in pairs if c >= cut]
        out.append((cut, len(kept), sum(kept)))
    return out


def cost(questions, right, input_tokens, cached_tokens, output_tokens, price):
    """Dollars from recorded tokens. price holds dollars per million tokens: in (uncached input), cached (cached
    input), and out. cached_tokens is the part of input_tokens the backend served from its cache."""
    usd = ((input_tokens - cached_tokens) * price["in"] + cached_tokens * price["cached"] + output_tokens * price["out"]) / 1e6
    return {"usd": usd, "usd_per_1000_questions": 1000 * usd / questions if questions else None,
            "usd_per_1000_right": 1000 * usd / right if right else None}


def quantile(xs, q):
    """Linear interpolation between order statistics, as numpy's default."""
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    i = math.floor(pos)
    return xs[i] if i + 1 >= len(xs) else xs[i] + (pos - i) * (xs[i + 1] - xs[i])


def edges(values, k):
    """k + 1 quantile edges that split the values into k bins of equal share."""
    return [quantile(values, i / k) for i in range(k + 1)]


def bin_of(v, edges):
    """The bin index of v: bins are half-open [edge, next edge), and the last one is closed."""
    for i in range(len(edges) - 2, -1, -1):
        if v >= edges[i]:
            return i
    return 0
