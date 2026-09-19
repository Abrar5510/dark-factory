# The factory

Three coding-agent seats in a BAND Desktop room. A task goes in, work items and
evidence move between the seats, and nothing is called done until a seat that
did not write the code has run the checks itself.

The seats are generic. Nothing in a mandate names this challenge, this domain
or this stack: the whole of that lives in the task pasted into the room. Another
team could point these three seats at an unrelated product and the factory would
behave the same way.

## Seats

| Seat | Owns | Never |
|---|---|---|
| **Planner** | Splits the task into numbered work items with checkable acceptance criteria, orders them, releases one at a time, declares the task complete | Writes code; accepts work |
| **Builder** | Implements one work item, runs the project's check command, hands off an evidence block with the verbatim output | Accepts its own work; edits the checks that judge it |
| **Verifier** | Re-runs everything from a clean state, writes checks that encode the criteria, runs the isolated-container gate, returns ACCEPT or REJECT with a reproduction | Edits implementation code; accepts on the strength of a claim |

Mandates: [planner](mandates/planner.md), [builder](mandates/builder.md),
[verifier](mandates/verifier.md).

## How work moves

```
human ──task──▶ Planner ──WI-n──▶ Builder ──evidence──▶ Verifier
                   ▲                  ▲                     │
                   │                  └──REJECT + repro──────┤
                   └──────────ACCEPT──────────────────────────┘
                                        │
                   DECISION NEEDED ─────┴────▶ human (only the human answers)
```

Each arrow is a message shape, fixed in the mandates so a handoff cannot be
vague:

- **Work item** — id, scope, acceptance criteria as checkable statements,
  dependencies. One at a time, and only after the previous is accepted.
- **Evidence block** — files changed, the exact command run, the verbatim tail
  of its output, how each criterion is met, and what was skipped. A builder that
  cannot get the check passing hands off the failure rather than hiding it.
- **Verdict** — ACCEPT with what was run, or REJECT with expected, observed and
  the shortest reproduction. A rejection goes back to the builder; an acceptance
  goes to the planner, which releases the next work item.
- **Decision** — the one path out to a human, used when the task is genuinely
  ambiguous rather than when the work is hard.

## Why this holds up

- **The checker is not the author.** Acceptance is structurally out of the
  builder's reach, and the verifier cannot quietly repair what it is judging.
  Neither seat can close the loop alone.
- **Evidence is a command and its output**, never a summary. A handoff without
  output in it is rejected on that basis alone.
- **Criteria outlive the work item.** The verifier turns each one into an
  automated check, so work item 3 cannot silently break work item 1.
- **Clean-environment start is part of acceptance**, not a release-day
  discovery: `scripts/offline-build.sh` builds and runs with the network
  switched off entirely.
- **Scope failures are visible.** Two rejections on one work item send it back
  to the planner to re-split, rather than letting a builder grind.

## Standing this up somewhere else

1. Three sessions, one BAND room, one mandate each as its standing instruction.
2. Give the project a single check command and say what it is in the task.
3. Paste the task, mention the planning seat, and answer only what comes back
   as a decision.

The mandates carry no assumption about language, framework or domain. The
guard against drift is automated: `scripts/check-mandates.sh` fails the commit
if a mandate starts naming this challenge's nouns, paths, codes or stack.

## Known limits

- One work item in flight. Throughput is not the goal; a clean audit trail is.
- The builder and verifier share a working copy, so isolation between them is a
  rule rather than a sandbox boundary.
- The human is the only tie-breaker. The factory escalates rather than guesses.
