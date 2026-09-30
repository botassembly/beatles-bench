-- The confidence and the outcome it should match, for every model-backend case whose answer carries a
-- probability. Feeds the expected calibration error per backend and function.
SELECT system, function, level, id, probability, cal_right
FROM case_rows
WHERE probability IS NOT NULL AND cal_right IS NOT NULL AND model_backend = 1
ORDER BY system, function, level, id;
