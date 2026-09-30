-- The paired outcomes for the head-to-head report: every question two model backends both answered,
-- each side's binary outcome (fully right or not). Baselines are not backends and stay out.
SELECT a.system AS a_system, b.system AS b_system, a.function, a.level, a.id, a.correct, b.correct
FROM case_rows a
JOIN case_rows b
  ON b.function = a.function AND b.level = a.level AND b.id = a.id
WHERE a.system < b.system AND a.model_backend = 1 AND b.model_backend = 1
  AND a.correct IS NOT NULL AND b.correct IS NOT NULL
ORDER BY a.system, b.system, a.function, a.level, a.id;
