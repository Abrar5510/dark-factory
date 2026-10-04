# Pocketful Dark Factory

**Track:** pocketful (Venmo clone — wallet & payments)  
**Repository:** Public GitHub clone at `Abrar5510/pocketful-double-blind`  
**BAND Desktop room:** Recording included in submission video  

## How to read this repository

This is a double-blind AI factory build. The band consists of 5 seats, each with a mandate file in `mandates/`. Work is organized into four stages (`stage-1/` through `stage-4/`), each a complete buildable service in its own Docker container with no outbound network.

- `mandates/lead.md` — Orchestrates the band, rules on divergences, writes the final report. Never writes product code.
- `mandates/builder.md` — Builds the service logic and storage from the requirements.
- `mandates/surface.md` — Creates the user-facing surface, every specified state at phone and desktop width.
- `mandates/second-reader.md` — Produces an independent executable reference model, input generators, and invariants.
- `mandates/referee.md` — Mechanical judge that runs the official checker in isolated mode and posts verdicts.

Each `stage-N/` folder contains: `Dockerfile`, `RUN.md`, and source code. The service builds and serves from a clean container with no outbound network.

`verification/` contains the Second Reader's conformance kit (imported as plain files at the end of the run).

`room.json` is the full-session export from BAND Desktop, unedited except credential values replaced with `[REDACTED]`.

`FACTORY.md` contains the seat setup, design rationale, measured costs, and catch-and-recover story.

## Submission deliverables (per guide)

- [x] `stage-1/` through `stage-4/` — complete buildable services
- [x] `mandates/` — 5 seat mandate files (generic, no track-specific detail)
- [x] `FACTORY.md` — seat setup, design rationale, costs, catch & recover
- [x] `README.md` — team, track, how to read the repo, video link
- [x] `room.json` — full-session download, credentials redacted
- [x] `verification/` — Second Reader's kit
- [x] Video — room recording + walkthrough showing the factory working
- [x] Slide presentation — design, cost, one bad result caught, stage reached