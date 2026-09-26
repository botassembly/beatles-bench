#!/usr/bin/env python3
"""Figure 8: the pipeline, as flows of questions from each source through the data table they came from to their
category. kuva has no box-and-arrow diagrams, so the pipeline is a Sankey diagram weighted by questions."""
import glob
import json
from collections import Counter

from common import ROOT, kuva

SOURCE = {"songs.tsv": "Wikipedia", "albums.tsv": "Wikipedia", "events.tsv": "Wikipedia and Wikidata",
          "links.tsv": "Wikidata", "reversal-general.tsv": "Wikidata"}
qs = [json.loads(l) for f in sorted(glob.glob(str(ROOT / "questions" / "*.jsonl"))) for l in open(f, encoding="utf-8")]
flows = Counter()
for q in qs:
    table = q["fields"][0][0]
    flows[SOURCE[table], table] += 1
    flows[table, q["category"]] += 1
rows = sorted(((a, b, n) for (a, b), n in flows.items()), key=lambda r: (-r[2], r[0], r[1]))
kuva("sankey", ["from", "to", "questions"], rows, "8-pipeline", "--source-col", "from", "--target-col", "to", "--value-col", "questions",
     "--title", f"Pinned sources to data tables to {len(qs)} questions", "--width", 1200, "--height", 900)
