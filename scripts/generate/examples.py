#!/usr/bin/env python3
"""Write the case files of functions/: one worked example per function, as the ThinkThen talk shows them.

usage: examples.py [OUT_DIR]   (default: functions/)
Each folder functions/FUNCTION/ gets its case files (one JSONL per case set) and any card a case names.
functions/audit/ also gets key.jsonl, the answer key audit and diff read: {"id": title, "value": "yes"|"no"}. The song
lists and the question wording are the talk's. A cold record sends the title alone. A context record sends
"Catalog:\\n<entry>\\nText: <title>", the shape scripts/run/ask.py sends, where the entry comes from
scripts/run/catalog.py. Each case carries its truth from data/songs.tsv where the table has one.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "run"))
import catalog  # noqa: E402

SONGS = {s["title"]: s for s in catalog.read("songs.tsv")}
ALBUMS = catalog.read("albums.tsv")
OUT = ROOT / "functions"  # main() may point it elsewhere
COLD = "The text is the title of a song by the Beatles. "
CONTEXT = "The text gives a catalog entry and then names a song by the Beatles. "
RECORD = ["--jsonl", "--field", "/input"]

SINGER = {"Lennon": "John", "McCartney": "Paul", "Harrison": "George", "Starr": "Ringo",
          "Lennon+McCartney": "John and Paul duet", "McCartney+Lennon": "John and Paul duet"}
LOVE = ["She Loves You", "Michelle", "Yesterday", "Taxman"]
ABBEY_DECIDE = LOVE + ["A Day in the Life", "Something"]
CHOOSE = ["Come Together", "Yesterday", "Something", "Octopus's Garden", "She Loves You"]
TAG = ["Michelle", "Yesterday", "Eleanor Rigby", "Penny Lane", "Octopus's Garden", "Lucy in the Sky with Diamonds"]
LABELS = ["love song", "sad", "psychedelic", "about a place", "about the sea"]
SCORE = ["Her Majesty", "Yesterday", "Octopus's Garden", "Something", "Come Together", "A Day in the Life", "Hey Jude", "Revolution 9"]
MINUTES = ["about 0 minutes", "about 1 minute"] + [f"about {m} minutes" for m in range(2, 10)]
FILTER = ["Octopus's Garden", "Yellow Submarine", "Something", "Here Comes the Sun", "Yesterday", "Come Together",
          "Hey Jude", "Penny Lane", "A Day in the Life", "Her Majesty", "Let It Be", "Maxwell's Silver Hammer"]
RANK = ["Something", "Hey Jude", "Blackbird", "Help!", "Octopus's Garden", "She Loves You", "Piggies", "Yesterday",
        "Penny Lane", "Her Majesty", "Can't Buy Me Love", "Good Night"]
FIND = ["She Loves You", "I Saw Her Standing There", "From Me to You", "All My Loving", "Love Me Do",
        "I Want to Hold Your Hand", "Please Please Me", "Can't Buy Me Love", "A Hard Day's Night", "I Feel Fine"]
ANNOTATE = ["Blackbird", "Octopus's Garden"]
SENTENCE = ("Ringo Starr wrote Octopus's Garden on a boat off Sardinia, "
            "and the band recorded it at Abbey Road Studios for the album Abbey Road.")
PEOPLE = {"John Lennon": "Lennon", "Paul McCartney": "McCartney", "George Harrison": "Harrison", "Ringo Starr": "Starr"}
RELATE_SONGS = ["Octopus's Garden", "Something", "Come Together", "Here Comes the Sun", "Yesterday", "Eleanor Rigby", "Taxman"]
RELATE_ALBUMS = ["Abbey Road", "Help!", "Revolver"]
ABBEY = "It appears on the album Abbey Road."
# The audit example asks the plainest wording its walkthrough gives. Only audit uses it, so a filter command with this
# question replays from the audit recording.
AUDIT_WORDING = "Is this song on the album Abbey Road?"
# The 70 titles of the audit and diff examples. They were chosen by hand for the talk, so they sit here as a fixed
# list. Seven of them first appeared on Abbey Road.
AUDIT = ["Here Comes the Sun", "Come Together", "Maxwell's Silver Hammer", "A Day in the Life",
         "The Long and Winding Road", "Mean Mr. Mustard", "Her Majesty", "Martha My Dear", "Piggies", "Lovely Rita",
         "Something", "Octopus's Garden", "Blackbird", "The Ballad of John and Yoko", "Get Back", "Hello, Goodbye",
         "Good Night", "In My Life", "Julia", "Taxman", "Back in the U.S.S.R.", "Don't Pass Me By", "Glass Onion",
         "Being for the Benefit of Mr. Kite!", "Blue Jay Way", "Rain", "Penny Lane", "Across the Universe",
         "Eleanor Rigby", "Strawberry Fields Forever", "Can't Buy Me Love", "Lucy in the Sky with Diamonds",
         "Let It Be", "Hey Jude", "Boys", "Paperback Writer", "Dear Prudence", "All You Need Is Love",
         "Helter Skelter", "Rocky Raccoon", "Nowhere Man", "Day Tripper", "Within You Without You", "Revolution",
         "Lady Madonna", "Ob-La-Di, Ob-La-Da", "Tomorrow Never Knows", "Yellow Submarine",
         "With a Little Help from My Friends", "Michelle", "Ticket to Ride", "While My Guitar Gently Weeps",
         "We Can Work It Out", "Act Naturally", "Love You To", "Yesterday", "When I'm Sixty-Four", "I Feel Fine",
         "Money (That's What I Want)", "Eight Days a Week", "I Am the Walrus", "I Want to Hold Your Hand",
         "She Loves You", "Magical Mystery Tour", "Norwegian Wood (This Bird Has Flown)", "From Me to You", "Help!",
         "Twist and Shout", "A Hard Day's Night", "Roll Over Beethoven"]


def text(title, context):
    return f"Catalog:\n{catalog.entry(SONGS[title], ALBUMS)}\nText: {title}" if context else title


def fields(title, *names):
    return [["songs.tsv", title, n, SONGS[title][n]] for n in names]


def one_each(prefix, function, args, titles, context, truth, names, **extra):
    """One case per song, so each call sends one request and keeps its own time."""
    return [{"id": f"{prefix}-{i:02d}", "function": function, "args": args,
             "records": [{"id": f"{prefix}-{i:02d}", "input": text(t, context)}], "title": t,
             **({"truth": truth(t)} if truth else {}), "fields": fields(t, *names), **extra}
            for i, t in enumerate(titles, 1)]


def write(folder, name, rows):
    path = OUT / folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if name.endswith(".jsonl"):
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    else:
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def card(prefix):
    albums = {"Help!": "Help! (1965)", "Rubber Soul": "Rubber Soul (1965)", "Revolver": "Revolver (1966)",
              "White Album": "The Beatles, the White Album (1968)", "Abbey Road": "Abbey Road (1969)"}
    singers = {"John": "John Lennon", "Paul": "Paul McCartney", "George": "George Harrison", "Ringo": "Ringo Starr"}
    return {"version": 1, "questions": {
        "singer": {"choose": prefix + "Who sings the lead vocal on it?", "options": singers, "threshold": 0.8},
        "album": {"choose": prefix + "On which album did it first appear?", "options": albums, "threshold": 0.8},
        "year": {"choose": prefix + "In which year was it first released?", "options": [str(y) for y in range(1965, 1970)],
                 "threshold": 0.8}}}


def main(out=None):
    global OUT
    OUT = Path(out) if out else ROOT / "functions"
    on_abbey = lambda t: SONGS[t]["first_album"] == "Abbey Road"
    singer = lambda t: SINGER[SONGS[t]["lead_vocals"]]
    write("decide", "decide-love.jsonl", one_each("decide-love", "decide", [COLD + "It is a love song.", *RECORD], LOVE, False, None, ["title"]))
    for kind, prefix in (("cold", COLD), ("context", CONTEXT)):
        write("decide", f"decide-{kind}.jsonl", one_each(f"decide-{kind}", "decide", [prefix + ABBEY, *RECORD],
                                                            ABBEY_DECIDE, kind == "context", on_abbey, ["first_album"]))
        write("choose", f"choose-{kind}.jsonl", one_each(
            f"choose-{kind}", "choose", [prefix + "Who sings the lead vocal on it?", "John", "Paul", "George", "Ringo",
                                         "John and Paul duet", *RECORD], CHOOSE, kind == "context", singer, ["lead_vocals", "article_lead"]))
        write("score", f"score-{kind}.jsonl", one_each(
            f"score-{kind}", "score", [prefix + "How long is the recording?", *MINUTES, *RECORD], SCORE, kind == "context",
            lambda t: round(int(SONGS[t]["length_s"]) / 60, 2), ["length_s"]))
        write("filter", f"filter-{kind}.jsonl", one_each(
            f"filter-{kind}", "filter", [prefix + ABBEY, "--threshold", "0.7", *RECORD], FILTER, kind == "context", on_abbey,
            ["first_album"], group=f"filter-{kind}"))
        find_prefix = "These are songs by the Beatles. " if kind == "cold" else \
            "Each one gives a catalog entry and then names a song by the Beatles. "
        write("find", f"find-{kind}.jsonl", [{
            "id": f"find-{kind}", "function": "find", "args": [find_prefix + "Which one did they release first?", *RECORD],
            "records": [{"id": f"u{i:02d}", "input": text(t, kind == "context")} for i, t in enumerate(FIND, 1)],
            "truth": f"u{FIND.index(min(FIND, key=lambda t: SONGS[t]['release_date'])) + 1:02d}",
            "fields": [f for t in FIND for f in fields(t, "release_date")]}])
        write("annotate", f"annotate-{kind}-card.json", card(prefix))
        write("annotate", f"annotate-{kind}.jsonl", one_each(
            f"annotate-{kind}", "annotate", [f"annotate-{kind}-card.json", *RECORD], ANNOTATE, kind == "context",
            lambda t: {"singer": singer(t), "album": {"The Beatles (White Album)": "White Album"}.get(SONGS[t]["first_album"], SONGS[t]["first_album"]),
                       "year": SONGS[t]["year"]}, ["lead_vocals", "first_album", "year"]))
    write("tag", "tag-cold.jsonl", one_each("tag-cold", "tag", [COLD + "Which of these describe it?", *LABELS, *RECORD], TAG, False, None, ["title"]))
    write("rank", "rank-cold.jsonl", one_each("rank-cold", "rank", [COLD + "It is one of the Beatles' biggest hits.", *RECORD], RANK, False,
                                                 lambda t: int(SONGS[t]["views_2024"]), ["views_2024"], group="rank-cold"))
    write("recognize", "recognize-cold.jsonl", [{
        "id": "recognize-cold", "function": "recognize", "args": ["person", "song", "album", "place", "--threshold", "0.01", *RECORD],
        "records": [{"id": "recognize-cold", "input": SENTENCE}]}])
    write("relate", "relate.json", {"version": 1, "relate": {"relations": [
        {"name": "sung_by", "source": "song", "target": "person", "reads": "has its lead vocal sung by"},
        {"name": "appears_on", "source": "song", "target": "album", "reads": "first appeared on the album"}]}, "threshold": 0.01})
    entities = ([{"name": p, "kind": "person"} for p in PEOPLE] + [{"name": s, "kind": "song"} for s in RELATE_SONGS]
                + [{"name": a, "kind": "album"} for a in RELATE_ALBUMS])
    truth = [["sung_by", s, p] for s in RELATE_SONGS for p, last in PEOPLE.items() if last in SONGS[s]["lead_vocals"].split("+")]
    truth += [["appears_on", s, SONGS[s]["first_album"]] for s in RELATE_SONGS if SONGS[s]["first_album"] in RELATE_ALBUMS]
    write("relate", "relate-cold.jsonl", [{
        "id": "relate-cold", "function": "relate", "args": ["@relate.json", "--jsonl"], "records": entities, "truth": truth,
        "fields": [f for s in RELATE_SONGS for f in fields(s, "lead_vocals", "first_album")]}])
    write("audit", "audit-cold.jsonl", one_each("audit", "decide", [AUDIT_WORDING, *RECORD], AUDIT, False, on_abbey, ["first_album"]))
    write("audit", "audit-context.jsonl", one_each("audit-context", "decide", [CONTEXT + AUDIT_WORDING, *RECORD], AUDIT, True, on_abbey,
                                                      ["first_album"]))
    write("audit", "key.jsonl", [{"id": t, "value": "yes" if on_abbey(t) else "no"} for t in AUDIT])


if __name__ == "__main__":
    main(*sys.argv[1:])
