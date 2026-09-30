"""The Jev runs behind the published tables in results/tables/. Tests that check those tables read these folders by
name and never take the newest folder. Ticket 0009 step 7 moves JEV in the same commit that rewrites the tables."""
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent / "results" / "runs"
JEV = "2026-09-26"  # the date of the thinkthen-jev and functions-jev runs the tables come from
JEV_RUN, JEV_FUNCTIONS = RUNS / f"{JEV}-thinkthen-jev", RUNS / f"{JEV}-functions-jev"
JEV_RECOGNIZE = RUNS / "2026-09-30-recognize-jev"  # the new recognize groups; its rows join functions.tsv beside them
JEV_RELATE = RUNS / "2026-09-30-relate-jev"  # the relate run of ticket 0019, all 47 cases under the pair planner
