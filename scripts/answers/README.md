# One answers table, and reports from it

`build.py` writes `results/answers.jsonl`: one row per case per committed run folder, normalized so every
measure can read the same columns. `report.py` loads the table into an in-memory SQLite database, runs the
queries in `queries/`, computes intervals and tests in Python, and writes `reports/generated/*.md` and
`results/by-question.jsonl`. Both steps run offline after scoring (`run.sh` calls them at the end).

## The row

```
{"run": "2026-09-26-thinkthen-jev", "date": "2026-09-26", "backend": "https://.../systemone",
 "model": "jev-1.13.0", "build": "02dc0b96...", "id": "reversal-001", "function": "choose",
 "test": "reversal", "level": "memory", "category": "reversal", "truth": "a", "answer": "a",
 "right": 1.0, "counts": null, "value": 1, "probability": 0.9897, "input_tokens": 2021, "ms": 468}
```

- `right` is the per-case score where the measure is a mean: accuracy with tie shares (decide, choose),
  the exact set (tag), the find pick, each annotate field, "no name found" (recognize). It is null where
  the measure pools counts or ranks values.
- `counts` holds the scored tp/fp/fn units for filter (one per case), relate (one per relation and song,
  with the case's `pick` where asked) and recognize (one per name kind, plus one per edge set). Sum them
  for the pooled precision, recall and F1.
- `value` is the number the measure needs: the score answer, rank's negated print position, decide's
  p(yes), choose's top tie width.
- `probability` is the probability the backend gave its answer. It is null for recognize, whose strength
  is not a probability, and for relate, whose answer is the edges with each one's probability (and the
  case's skipped songs, so an audited cut's said set re-derives the way the scorer's does).
- `id` is the case id; annotate's fields get one row each as `case:field`. `gap` marks a case the backend
  refused.
- `input_tokens`, `cached_input_tokens`, `output_tokens`, `ms` and `requests` are the recorded cost, where
  the run recorded it, so the tables' usage columns recompute.

## Read the file

The file is newline-delimited JSON, so DuckDB reads it directly. SQLite reads it after a load into a
table. Each SQLite example below starts with `db = load()` — paste this loader above the example, or run
the examples in one session after it:

```python
def load(path="results/answers.jsonl"):
    import json, sqlite3
    db = sqlite3.connect(":memory:")
    db.execute("""CREATE TABLE answers(run, date, backend, model, build, id, function, test, level,
                  category, truth, answer, right, counts, value, probability, input_tokens,
                  cached_input_tokens, output_tokens, ms, requests)""")
    for l in open(path, encoding="utf-8"):
        r = json.loads(l)
        db.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (r["run"], r["date"], r["backend"], r["model"], r["build"], r["id"], r["function"],
                    r["test"], r["level"], r["category"], json.dumps(r["truth"]),
                    json.dumps(r["answer"]), r["right"], json.dumps(r["counts"]), r["value"],
                    r["probability"], r["input_tokens"], r["cached_input_tokens"], r["output_tokens"],
                    r["ms"], r["requests"]))
    return db
```

(`truth`, `answer` and `counts` go in as JSON text — unpack with `json_extract` when a query needs inside.)

### Accuracy per run, one function

How each run scored the pick-one memory questions:

```sh
duckdb -c "
SELECT run, count(*) n, round(avg(\"right\"), 3) acc
FROM read_json_auto('results/answers.jsonl', format='newline_delimited')
WHERE function = 'choose' AND level = 'memory'
GROUP BY run ORDER BY run;"
```

```sh
python3 - <<'EOF'
db = load()
for row in db.execute("""
    SELECT run, count(*) n, round(avg("right"), 3) acc
    FROM answers WHERE function = 'choose' AND level = 'memory'
    GROUP BY run ORDER BY run"""):
    print(row)
EOF
```

### Two runs on the same cases

Where Jev and GLM disagree on a pick-one question: a self-join on the id. `report.py` uses the same join
per function and level for its head-to-head table.

```sh
duckdb -c "
SELECT j.id, j.answer jev, g.answer glm
FROM read_json_auto('results/answers.jsonl', format='newline_delimited') j
JOIN read_json_auto('results/answers.jsonl', format='newline_delimited') g ON g.id = j.id
WHERE j.run = '2026-09-26-thinkthen-jev' AND g.run = '2026-09-23-glm-5.3-flash'
  AND j.function = 'choose' AND j.\"right\" != g.\"right\"
ORDER BY j.id;"
```

```sh
python3 - <<'EOF'
db = load()
for row in db.execute("""
    SELECT j.id, j.answer jev, g.answer glm
    FROM answers j JOIN answers g ON g.id = j.id
    WHERE j.run = '2026-09-26-thinkthen-jev' AND g.run = '2026-09-23-glm-5.3-flash'
      AND j.function = 'choose' AND j."right" != g."right"
    ORDER BY j.id"""):
    print(row)
EOF
```

### What each run cost

```sh
duckdb -c "
SELECT run, sum(input_tokens) input_tokens, round(sum(ms)/1000) s
FROM read_json_auto('results/answers.jsonl', format='newline_delimited')
GROUP BY run ORDER BY run;"
```

```sh
python3 - <<'EOF'
db = load()
for row in db.execute("""
    SELECT run, sum(input_tokens) input_tokens, round(sum(ms)/1000) s
    FROM answers GROUP BY run ORDER BY run"""):
    print(row)
EOF
```

## Reports

```sh
python3 scripts/answers/build.py    # results/answers.jsonl
python3 scripts/answers/report.py   # reports/generated/{by-function,head-to-head,calibration}.md
                                    # and results/by-question.jsonl
```

- `by-function.md` pools each system's runs the way `score_suite.py` merges them, then reports the main
  measure per level: Wilson intervals for the shares, a seeded bootstrap for Spearman and F1.
- `head-to-head.md` pairs the model backends on the questions both answered: agreement plus an exact
  McNemar test per function and level, and a Spearman where the measure is a value.
- `calibration.md` reports the expected calibration error per backend, function and level over the answers
  that carry a probability.
- `results/by-question.jsonl` has one row per question with every run's answer, probability and score.

The same queries live in `queries/`: the report runs them over its in-memory database, and they stand on
their own as examples of what the table answers.
