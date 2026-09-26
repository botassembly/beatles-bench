"""A gap is a call the backend refused: the command reports an HTTP 4xx status and exits 4, and prints no answer.
Live mode records each gap in RUN/gaps.tsv (the id and the command's message) and never asks it again. Replay reads
the file and asks nothing for a gap, because a refused request leaves no entry in the recording."""
import re
from pathlib import Path

REFUSED = re.compile(r"the backend answered with status 4\d\d")


def refusal(code, stderr):
    """The command's message when the backend refused the call, else None."""
    if code != 4:
        return None
    return next((l.strip() for l in stderr.splitlines() if REFUSED.search(l)), None)


def read(path):
    path = Path(path)
    if not path.exists():
        return {}
    return dict(l.split("\t", 1) for l in path.read_text(encoding="utf-8").splitlines()[1:] if l.strip())


def append(path, key, message):
    path = Path(path)
    new = not path.exists()
    with open(path, "a", encoding="utf-8") as f:
        f.write(("id\tmessage\n" if new else "") + f"{key}\t{message}\n")
