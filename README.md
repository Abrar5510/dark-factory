# Dark Factory — BAND hackathon submission

A band of three coding-agent seats that plans work, implements it, hands off
evidence, and checks its own results. Built in a BAND Desktop room.

**Track:** pocketful — the hard part is that value is never created, destroyed
or spent twice under concurrency, retries and rounding.

| What | Where |
|---|---|
| The factory, and how to stand it up elsewhere | [FACTORY.md](FACTORY.md) |
| Seat mandates (generic by rule) | [mandates/](mandates/) |
| The room the band worked in | [room-export/](room-export/) |
| Per-stage verification evidence | [evidence/](evidence/) |
| The stages | `stage-1/` … `stage-4/` |
| Video walkthrough | _link added at submission_ |

Each stage folder is a complete, standalone service. A stage is graded against
every suite up to its own number, so each folder holds that stage's answer and
not a later one.

## Running a stage

Nothing to install: the service uses only the Node standard library, so the
image builds and runs with the network switched off.

```bash
cd stage-1 && node server.js      # listens on $PORT, default 3000
curl localhost:3000/health
```

```bash
cd stage-1 && npm test            # the project's check command
```

In a clean, isolated container, which is how it is graded:

```bash
scripts/offline-build.sh stage-1
```

That builds with `--network=none`, runs with no network under a CPU and memory
cap, waits for the service to answer, and runs the checks inside that same
container.

## Repository layout

```
mandates/      one standing instruction per seat; names nothing domain-specific
scripts/       check-mandates.sh · offline-build.sh · snapshot-stage.sh
service/       the working copy the band builds in
stage-N/       frozen snapshot of the service as it stood when stage N passed
evidence/      what the checking seat ran, and what it saw, per stage
room-export/   export of the BAND Desktop room
```

## Checks anyone can re-run

```bash
scripts/check-mandates.sh --selftest   # the guard itself is checked
scripts/check-mandates.sh              # no mandate names this track or stack
scripts/offline-build.sh service       # builds, starts and passes with no network
```
