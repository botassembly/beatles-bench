# sdlc/

The system of record for Beatles Bench. The Claude marketing session owns this queue (Ian, 2026-09-24).

| Folder | What it is |
| --- | --- |
| [issues/](issues/) | Problems found. An issue authorizes no work. A closed issue keeps its status line and moves to [issues/closed/](issues/closed/) |
| [tickets/](tickets/) | Work a ticket authorizes, numbered from 0001 |
| [records/](records/) | What landed, with its review and checks |

## Checks

- `python3 -m unittest discover -s tests` runs with no network. Set `THINKTHEN_BIN` to add the replay tests.
- A live run needs a token cap in its ticket and a replay that gives the same answers with no key.

## Budgets

A live Jev run within a ticket's cap needs no further approval. A new outside service needs Ian's approval through `notes/todos/`.

Asks for the ThinkThen team collect in the marketing session's queue first. An ask moves to the ThinkThen repository's `sdlc/issues/` once its evidence is in and it names one change.
