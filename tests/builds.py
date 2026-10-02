"""Which thinkthen build recorded each results/ folder, from results/builds.tsv, and the BENCH_BIN_<id>
environment variable that lets a check replay it. A replay or contract check that depends on a run's build runs
only when BENCH_BIN_<id> names a command for that build; otherwise it skips with a reason naming the build and
the variable. The examples replay under THINKTHEN_BIN instead; a folder whose recording is not a question store
is gated on the build its run.txt names."""
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "results" / "builds.tsv"
COMMIT = re.compile(r"(?:main at |thinkthen main )([0-9a-f]{7,40})")


def builds():
    """The folder -> build rows of results/builds.tsv."""
    rows = {}
    for line in TABLE.read_text(encoding="utf-8").splitlines()[1:]:
        folder, _, build = line.partition("\t")
        if folder and build:
            rows[folder] = build
    return rows


def commit_for(path):
    """The build results/builds.tsv names for PATH, the longest matching row; None when no row covers it."""
    p = Path(path)
    rel = str(p.relative_to(ROOT)) if p.is_absolute() else str(p)
    if rel.endswith("/recording"):
        rel = rel[: -len("/recording")]
    best = None
    for folder, build in builds().items():
        if rel == folder or rel.startswith(folder + "/"):
            if best is None or len(folder) > len(best[0]):
                best = (folder, build)
    return best


def pinned_commit(folder):
    """The commit a folder's run.txt names, or None."""
    f = Path(folder) / "run.txt"
    if not f.is_file():
        return None
    m = COMMIT.search(f.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def build_id(commit):
    """The id a BENCH_BIN_<id> variable uses: a full commit's first 8 hex, a recorded short id as is."""
    return commit[:8] if commit and len(commit) >= 20 else commit


def bench_bin(build):
    """The command BENCH_BIN_<id> sets for BUILD, or None."""
    if not build or build == "unknown":
        return None
    path = os.environ.get(f"BENCH_BIN_{build}")
    return shutil.which(path) if path else None  # a path or a command on PATH, as run.sh's `command -v` takes


def reason(folder, build):
    """The skip reason naming the build and the variable."""
    if build == "unknown":
        return f"{folder}: results/builds.tsv names no thinkthen build for it"
    return f"{folder} was recorded with thinkthen {build}; set BENCH_BIN_{build} to its command"


def bin_for(path):
    """(command, None) when BENCH_BIN_<id> covers the run folder PATH, else (None, skip reason)."""
    hit = commit_for(path)
    if hit is None:
        return None, f"results/builds.tsv has no row for {path}"
    folder, build = hit
    bin = bench_bin(build)
    return (bin, None) if bin else (None, reason(folder, build))
