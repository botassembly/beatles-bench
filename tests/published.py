"""The Jev runs behind the published tables in results/tables/. Tests that check those tables read these folders by
name and never take the newest folder. Ticket 0009 step 7 moves JEV in the same commit that rewrites the tables."""
import re
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent / "results" / "runs"
JEV = "2026-09-26"  # the date of the thinkthen-jev-open-book run the open-book page compares
JEV_ALL = RUNS / "2026-09-30-all-jev"  # ticket 0023: the whole bench on build aec7819bb; the Jev row comes from it
JEV_RUN, JEV_FUNCTIONS = JEV_ALL, JEV_ALL
JEV_RECOGNIZE = RUNS / "2026-09-30-recognize-jev"  # the new recognize groups; the all-run covers them
JEV_RELATE = RUNS / "2026-09-30-relate-jev"  # the relate run of ticket 0019, all 47 cases under the pair planner
JEV_READING = RUNS / "2026-09-30-reading-jev"  # the reading tests and the album-more find sets
D1_ALL = RUNS / "2026-09-30-all-liquid-d1"  # ticket 0023: the same cases on Liquid's d1:free


def pending(run):
    """The reason a run's function table is deferred, when its run.txt carries a `function table: pending; REASON`
    line, else None. The run still answers every other check; only its suite table stays unwritten."""
    f = Path(run) / "run.txt"
    if not f.is_file():
        return None
    m = re.search(r"^function table: pending; (.+)$", f.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None
