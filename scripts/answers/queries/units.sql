-- The scored units behind the pooled measures: filter's one per case, relate's one per relation and song
-- (meta holds rel, song and the pick where asked), recognize's one per name kind and one per edge set
-- (meta holds kind and the overlap tallies). Feeds the pooled F1, precision and recall and their
-- bootstrap intervals.
SELECT system, function, level, test, id, seq, tp, fp, fn, meta
FROM units
ORDER BY system, function, level, test, id, seq;
