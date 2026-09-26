# sdlc/

The system of record for Beatles Bench. One agent owns this queue under Ian (Ian, 2026-09-24).

This folder is public. It is the repository's only record of what was decided, built, and checked. ThinkThen keeps its own `sdlc/` public the same way.

| Folder | What it is |
| --- | --- |
| [issues/](issues/) | Problems found. An issue authorizes no work. A closed issue keeps its status line and moves to [issues/closed/](issues/closed/) |
| [tickets/](tickets/) | Work a ticket authorizes, numbered from 0001 |
| [records/](records/) | What landed, with its review and checks |

## Checks

- `python3 -m unittest discover -s tests` runs with no network. Set `THINKTHEN_BIN` to add the replay tests.
- A live run needs a token cap in its ticket and a replay that gives the same answers with no key.

## Budgets

A live Jev run within a ticket's cap needs no further approval. A new outside service needs Ian's approval on his todo list.

Asks for the ThinkThen team collect in the queue owner's queue first. An ask moves to the ThinkThen repository's `sdlc/issues/` once its evidence is in and it names one change.
