-- The numeric answers the ordering measures rank: score's value and rank's negated print position,
-- against the case's numeric truth. Feeds Spearman per test and the backend agreement on values.
SELECT system, function, level, test, id, value, truth
FROM case_rows
WHERE value IS NOT NULL AND function IN ('score', 'rank')
ORDER BY system, function, level, test, id;
