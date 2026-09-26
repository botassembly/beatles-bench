#!/usr/bin/env python3
"""Wiring check: questions whose answer is written in the text, from ThinkThen's customer-service examples (2026-09-21).
usage: check.py laya|jev
  laya  asks the shim at THINKTHEN_BASE_URL, recording into laya-recording/
  jev   replays jev-recording/ with no key: Jev's answers to 12 of these requests, recorded on 2026-09-21. A request
        it never sent is reported as not recorded
Writes RESULTS-{laya,jev}.tsv. Each case is its own call, so one missing entry does not stop the rest.
THINKTHEN_BIN names the command (default: thinkthen on PATH). BEATLES_BENCH_MODEL names the model (default: laya-mlx for
laya, jev-latest for jev). THINKTHEN_BASE_URL names the backend a laya run asks."""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2] / "results" / "in-text-check"
TT = os.environ.get("THINKTHEN_BIN", "thinkthen")
JEV = HERE / "jev-recording"
REFUND, COMPLAINT, URGENT = "Does the customer ask for a refund?", "Is this a complaint?", "Is this urgent?"
TEAMS = ["billing=Invoices, fees, and refunds.", "shipping=Parcels and delivery.", "account=Logins and passwords."]
DECIDE = [(REFUND, "Please refund my order. It arrived broken.", "yes"),
          (REFUND, "Thanks for the quick help yesterday!", "no"),
          (REFUND, "I renewed once this morning, but my card shows two charges.\nPlease refund the duplicate.", "yes"),
          (COMPLAINT, "Arrived a day early. Thank you!", "no"),
          (COMPLAINT, "The zipper broke the first time I used it.", "yes"),
          (COMPLAINT, "Does this come in blue?", "no"),
          (COMPLAINT, "The strap snapped on day two.", "yes"),
          (URGENT, "Newsletter: our autumn catalog is here. No reply needed.", "no"),
          (URGENT, "Our checkout page is down and customers cannot pay", "yes"),
          (URGENT, "Reminder: your invoice is due in 30 days", "no")]
CHOOSE = [("Please refund the extra fee on my invoice.", "billing"),  # the first three are in jev-recording/
          ("My parcel went to the wrong address.", "shipping"),
          ("I cannot reset my password.", "account"),
          ("I was charged twice for one order.", "billing"),
          ("The courier left my box at the wrong house.", "shipping"),
          ("My account is locked after three wrong passwords.", "account"),
          ("Please send me a copy of last month's invoice.", "billing"),
          ("Where is my package? Tracking has not moved in a week.", "shipping"),
          ("I forgot the email I log in with.", "account"),
          ("The late fee on my bill is wrong.", "billing")]


def ask(args, text, mode):
    flag = ["--cache", str(HERE / "laya-recording")] if mode == "laya" else ["--replay", str(JEV)]
    rec = json.dumps({"id": "x", "input": text}) + "\n"
    d = subprocess.run([TT, *args, "--jsonl", "--field", "/input", "--details", *flag], input=rec, capture_output=True, text=True)
    if d.returncode not in (0, 1, 3):
        return None, d.stderr.strip().splitlines()[0][:90]
    return json.loads(d.stdout), ""


def main(mode):
    model = os.environ.get("BEATLES_BENCH_MODEL") or ("laya-mlx" if mode == "laya" else "jev-latest")
    if mode == "jev":
        os.environ.pop("THINKTHEN_API_KEY", None)
        os.environ.pop("THINKTHEN_BASE_URL", None)
    else:
        os.environ["THINKTHEN_API_KEY"] = "local"
    rows = []
    for q, text, truth in DECIDE:
        r, err = ask(["decide", q, "--model", model], text, mode)
        got = None if r is None else ("yes" if r["value"] else "no")
        rows.append(["decide", q, text, truth, got or "", f"{r['answer']['probability']:.3f}" if r else "", err])
    for text, truth in CHOOSE:
        args = ["choose", "Which team owns this?", *[a for t in TEAMS for a in ("--option", t)]]
        r, err = ask(args + ["--model", model], text, mode)
        rows.append(["choose", "Which team owns this?", text, truth, (r or {}).get("value") or "",
                     json.dumps(r["answer"]["probabilities"]) if r else "", err])
    with open(HERE / f"RESULTS-{mode}.tsv", "w", encoding="utf-8") as f:
        f.write("function\tquestion\ttext\ttruth\tanswer\tprobability\terror\n")
        f.writelines("\t".join(c.replace("\n", "\\n").replace("\t", " ") for c in r) + "\n" for r in rows)
    done = [r for r in rows if r[4]]
    print(mode, f"{sum(r[3] == r[4] for r in done)}/{len(done)} right of {len(rows)} asked")
    for fn in ("decide", "choose"):
        d = [r for r in done if r[0] == fn]
        print(" ", fn, f"{sum(r[3] == r[4] for r in d)}/{len(d)}")


if __name__ == "__main__":
    main(sys.argv[1])
