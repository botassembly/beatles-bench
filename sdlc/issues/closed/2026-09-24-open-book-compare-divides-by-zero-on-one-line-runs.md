# open_book.py compare divides by zero on the one-line runs

Status: Closed 2026-09-25. Ticket 0009 fixed it: `compare` prints blank cells for a topic with no questions, and `tests/test_open_book.py` covers it.

`scripts/score/open_book.py compare` fails with a division by zero when pointed at the ticket 0005 runs (`results/runs/2026-09-24-*-one-line`). The report's table came from `scripts/score/table.py` instead. A topic with no closed-book hits or misses in the sample likely leaves a zero denominator.
