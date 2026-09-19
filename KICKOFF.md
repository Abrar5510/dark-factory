# Kickoff day runbook (Sep 26)

Everything here is the part that could not be done in advance. Work top to
bottom; the first three items are the disqualifier guards.

## Before the first task is pasted

1. **Start the screen recording** of BAND Desktop and keep it running all day.
   A video without the room recording disqualifies the entry. Save raw files to
   `recordings/` (git-ignored) and never rely on re-staging a run later.
2. **Read all four SPECs end to end** before writing anything. Note for each
   stage: routes and response shapes, error codes, required test ids, the port
   and health convention, CPU/memory caps, harness concurrency, request timeout.
3. **Extend the denylist** with every proper noun, path segment, field name,
   error code and test id the SPEC introduces:
   ```bash
   $EDITOR scripts/denylist.txt && scripts/check-mandates.sh
   ```
   Then read each mandate once by eye and ask: would a team building something
   unrelated still be able to use this? Fix anything that fails that question.
4. **Install and run the harness**, then reconcile it with what is here:
   ```bash
   harness check
   ```
   - If it wants mandates in a particular location or format, move the content
     of `mandates/*.md` into it verbatim. The words are what matter.
   - If it wants a different stage folder layout or entrypoint, adapt
     `scripts/snapshot-stage.sh` once, now, not at submission.
   - If it publishes caps, set them in the gate:
     `CPUS=<n> MEMORY=<m> scripts/offline-build.sh service`

## Bringing the band up

1. Three Claude Code windows. In each: `/jam`, then bind it to the room and
   give it its mandate as the standing instruction.
2. Confirm in BAND Desktop that all three show connected before pasting work.
3. Paste the Stage 1 task into the room and mention the planning seat. The task
   carries every SPEC detail: routes, shapes, codes, ids, and the check command
   (`npm test`, run from the stage folder).

## Per stage

```bash
# once the planning seat posts TASK COMPLETE and the checking seat is green:
scripts/offline-build.sh service        # the gate, before anything is frozen
scripts/snapshot-stage.sh <n>           # freeze stage-<n>/
scripts/offline-build.sh stage-<n>      # the gate again, on the frozen copy
```

Then write `evidence/stage-<n>.md` with the commands run and their output, and
confirm the frozen folder does **not** contain anything the next stage
introduces. Commit, and do not touch that folder again.

## Watch for

- A seat that accepts its own work. That is the one failure that makes the
  whole factory worthless to a judge; reject the run and fix the mandate.
- A handoff with no command output in it. The checking seat rejects these.
- Work items too large to check. Two rejections means re-split, not grind.
- The scaffolded probe route in `service/tests/scaffold.test.js` is a transport
  check, not a domain route. It stays; it costs nothing and guards the envelope.
