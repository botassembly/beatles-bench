"""Shared by the figure scripts: read results/tables/, pick the systems to draw, run kuva, and set panels side by side.

kuva draws every chart (KUVA names the command; default kuva on PATH, else ~/.cargo/bin/kuva). kuva draws one chart
per call, so a figure with panels sets kuva's SVGs side by side in one SVG, and its PNGs in one PNG with Pillow.
Every figure draws the systems systems() returns: each model run (Jev first, then GLM-5.3 Flash, Laya, and any other
model whose run exists) and the best baseline, a vector search of the question against the options. A model with
no run is left out.
"""
import csv
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "results" / "tables"
OUT = ROOT / "reports" / "figures"
KUVA = os.environ.get("KUVA") or shutil.which("kuva") or str(Path.home() / ".cargo" / "bin" / "kuva")
ORDER = ["Jev", "GLM-5.3 Flash", "Laya"]  # models first, in this order; any other model follows


def table(name):
    with open(TABLES / f"{name}.tsv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def systems(models_only=False):
    """The systems to draw, in a fixed order, so each keeps its colour from figure to figure."""
    rows = table("systems")
    acc = {r["system"]: float(r["accuracy"]) for r in table("accuracy") if r["scope"] == "overall"}
    models = sorted((r["system"] for r in rows if r["family"] == "model"),
                    key=lambda s: (ORDER.index(s) if s in ORDER else len(ORDER), s))
    if models_only:
        return models
    best = max((r["system"] for r in rows if r["family"] != "model"), key=acc.get, default=None)
    return models + ([best] if best else [])


def kuva(kind, header, rows, stem, *args):
    """Write the rows to a TSV and draw them as reports/figures/STEM.svg and .png."""
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False, encoding="utf-8") as f:
        f.write("\t".join(header) + "\n")
        f.writelines("\t".join(str(v) for v in r) + "\n" for r in rows)
    for ext in ("svg", "png"):
        subprocess.run([KUVA, kind, f.name, *map(str, args), "-o", str(OUT / f"{stem}.{ext}")], check=True)
    os.unlink(f.name)
    return OUT / stem


def size(svg):
    head = svg[:svg.index(">")]
    w, h = (float(re.search(fr'\b{k}="([\d.]+)', head).group(1)) for k in ("width", "height"))
    return w, h


def panels(stems, stem, across=True):
    """Set the panels' SVGs and PNGs side by side (or stacked) as reports/figures/STEM.svg and .png."""
    from PIL import Image
    svgs = [Path(f"{s}.svg").read_text(encoding="utf-8") for s in stems]
    sizes = [size(s) for s in svgs]
    W = sum(w for w, _ in sizes) if across else max(w for w, _ in sizes)
    H = max(h for _, h in sizes) if across else sum(h for _, h in sizes)
    parts, at = [], 0.0
    for svg, (w, h) in zip(svgs, sizes):
        body = re.sub(r"^<\?xml[^>]*>\s*", "", svg)
        x, y = (at, 0) if across else (0, at)
        parts.append(f'<g transform="translate({x},{y})">{body}</g>')
        at += w if across else h
    (OUT / f"{stem}.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}" height="{H:g}" '
                                     f'viewBox="0 0 {W:g} {H:g}"><rect width="100%" height="100%" fill="white"/>'
                                     + "".join(parts) + "</svg>\n", encoding="utf-8")
    imgs = [Image.open(f"{s}.png").convert("RGB") for s in stems]
    Wp = sum(i.width for i in imgs) if across else max(i.width for i in imgs)
    Hp = max(i.height for i in imgs) if across else sum(i.height for i in imgs)
    canvas, at = Image.new("RGB", (Wp, Hp), "white"), 0
    for i in imgs:
        canvas.paste(i, (at, 0) if across else (0, at))
        at += i.width if across else i.height
    canvas.save(OUT / f"{stem}.png")
    for s in stems:
        for ext in ("svg", "png"):
            Path(f"{s}.{ext}").unlink()


def intervals(groups):
    """Rows for kuva box that draw each (group, accuracy, lo, hi) as a box spanning the 95% interval with its line at
    the accuracy: the five values lo, lo, accuracy, hi, hi put both quartiles on the interval's ends."""
    return [(g, v) for g, a, lo, hi in groups for v in (lo, lo, a, hi, hi)]
