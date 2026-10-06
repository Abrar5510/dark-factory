# Double-Blind — a dark factory

**Team:** Abrar Ahmad
**Track:** pocketful
**Video:** TODO(after run)

Five coding-agent seats take a written specification and build the service with no
human input after the task is dispatched. Two of the seats read the specification
blind to each other: one builds the service, the other builds an executable reference
of it on a different model family. A referee compares the two, and the lead settles
each disagreement by quoting the specification word for word.

## How to read this repository

| Path | What it is |
|---|---|
| `FACTORY.md` | The factory: seats, design choices, what failed, what it cost, how bad work gets caught. **Start here.** |
| `mandates/` | One standing instruction per seat. Each opens with the harness and model the seat runs. |
| `stage-N/` | One complete, buildable service per finished stage: `Dockerfile`, `RUN.md`, source. |
| `verification/` | The Second Reader's conformance kit, written without sight of the service. |
| `room.json` | The full room export from Band. The handoffs, rulings and usage are in here. |

Stage reached: TODO(after run)

## Run a stage

Follow `stage-N/RUN.md`. To grade it the way the judges do, from the kickoff
repository:

```sh
python -m harness check --track pocketful /path/to/this/repo
python -m harness run --track pocketful --repo /path/to/this/repo --all --mode isolated --out /tmp/df-check
```

## What a human did

Wrote `mandates/`, `README.md` and `FACTORY.md`, and sent one message to `@Lead`.
Everything under `stage-*/` and `verification/` was written by the seats; `git log
--format='%an %s'` shows which seat wrote each commit.
