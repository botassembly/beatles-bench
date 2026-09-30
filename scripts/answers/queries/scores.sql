-- Every pooled case's per-case scores: the mean-measure share, the pick share where the case has one, the
-- binary outcome for the paired tests, and the calibration pair. Feeds the Wilson measures and the
-- McNemar and ECE computations.
SELECT system, function, level, test, id, right, pick_right, correct, probability, cal_right
FROM case_rows
ORDER BY system, function, level, test, id;
