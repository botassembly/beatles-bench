-- One row per question per run that answered it, for results/by-question.jsonl. The join is inner: a
-- catalog question no run answered has no by-question row. Questions come from the catalog when it
-- exists, else from the question files through the answers table itself, so a run-only id (the
-- section-picking questions) still appears.
SELECT q.id, q.function, q.test, q.level, q.category, q.truth, a.run, a.answer, a.probability, a.right
FROM questions q
JOIN answers a ON a.id = q.id
ORDER BY q.id, a.run;
