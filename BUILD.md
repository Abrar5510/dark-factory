# BUILD.md — Double-Blind execution plan

> **What this is:** the dated, task-level plan that turns `IDEA.md` (design) into a
> submitted, gate-passing entry.
> **Precedence:** the official guide (`dark-factory-wearedevs/docs/participant-guide.md`)
> beats everything · `CHALLENGE.md` summarises it · `IDEA.md` wins on design · this file
> wins on *when and how*.
> **Revised:** Thu 2026-10-01, checked line by line against the guide and the harness
> source (`harness/check.py`, `harness/vocabulary.py`, `harness/cli.py`) at spec commit `803560d`.

---

## Changelog: corrections from the harness source (read before anything else)

Last revision: checked against the official participant guide and harness source, not
just CHALLENGE.md. Nothing has been run yet because there is no band output. "Passes"
means the exact official commands in §11.

**Mistakes in the previous draft that would have failed the checks:**

| # | Old plan said | Reality (source) | Where it's fixed |
|---|---|---|---|
| X1 | `room-export/` folder | **`room.json` at repo root**, from **Download full session**, unedited (`check.py: ROOM`) | §9 V1, §10 |
| X2 | Stage folders and root docs unspecified | Every `stage-N/` needs **`Dockerfile` + `RUN.md`**; repo root needs **`README.md`** + `FACTORY.md` | R3, R8, §10 |
| X3 | Mandates just "generic" | Each mandate **starts with `Harness:` and `Model:` lines** and its filename matches the seat's display name (case and punctuation ignored) | R1, §5 layout |
| X4 | Credential scan not considered for the room log | **`room.json` is scanned too.** Bearer tokens in seats' tool output fail `harness check`. Replace values with `[REDACTED]`, rotate any real key | R9, T6 (rehearsed on the toy), V1–V2 |
| X5 | `FROZEN.sha256` / lessons beside mandates | **Every `*.md` in `mandates/` is treated as a mandate.** Only the 5 seat files go there; hashes and lessons live outside | M8, M9 |
| X6 | "Stage-N must fail N+1" only | A folder claims N only if it passes **≥ 50 % of every suite 1..N** and **not all of suite N+1**. pocketful **also probes `stage-2/` against suite 3**. The chain counts contiguously | R10, V6 |
| X7 | Sandboxes "just configure" | macOS: Band Desktop only sees `sbx` after a **`launchctl config user path …` + REBOOT**. Blocker, do it early | B5 |
| X8 | Submit from this repo after pushing `reset-to-brief` | The submitted run needs a **fresh result repo**. Submission = **new public repo** from `~/band/band-work/result` | §2 paths, P2, V4 |

**Cut (rungs already covered by the official harness):**

- Gate scripts C1 (offline boot), C2 (shipped checks), C5 (overshoot probe) and C7 (vocabulary scanner). `harness run --mode isolated` already does boot + shipped checks + next-stage probe. `harness check` runs the **judges' own vocabulary list** (`vocabulary.py`).
- The whole `scripts/` folder **written by the human**. Hand-built code does not count. The human only commits `README.md`, `FACTORY.md`, `mandates/` and `room.json`. Quote checks (fixed-string grep) and commit tracing (`git log`) are one-liners the Referee's mandate describes.

**Added:**

- §1, a table of the **11 rules that decide the entry**, each mapped to the check that proves it.
- §8, a **ready-to-send dispatch** for the submitted run (all four stages, absolute paths).
- §9, the guide's **"Before you submit"** steps, run on a **fresh clone**.
- §10, a full **FACTORY.md checklist**, including "what we tried that failed" (the guide asks for it).
- §12, a **point of no return**: no dispatch by Sun 06:00 PKT → dispatch stages 1–2 only.

**⚠ This planning repo is PUBLIC** (`Abrar5510/dark-factory`). `notes/` is now in
`.gitignore`. **Don't push `IDEA.md` or `BUILD.md` here either.** They contain our
guesses about what judges check, and the hotspot statistics.

**Kickoff repo:** so far it's only cloned into Claude's scratchpad for reading. You
still need your own clone at `~/band/dark-factory-wearedevs` (B3).

**Next step:** §15. `caffeinate` → colima → kickoff clone + venv → sbx setup + **reboot** → seats.

---

## 0. The clock

| Fact | Value |
|---|---|
| Timezone | **PKT (UTC+5)** |
| **Hard deadline** | **Mon 2026-10-05 23:59 PDT = Tue 2026-10-06 11:59 PKT** |
| **Internal deadline** | **Mon 2026-10-05 16:00 PKT**: submitted, then verified from a second machine |
| Kickoff | Sat 2026-09-26 (all four stages and the toy were released then) |

`IDEA.md`'s day plan said "Wed Oct 1". Oct 1 is a **Thursday**, so Day 1 starts late
and Days 1 and 2 get compressed:

| Day | Work | Gate |
|---|---|---|
| **Thu Oct 1** | Blockers, harness running, seats + sandboxes, mandates drafted, **toy dispatched overnight** | G1, G2 |
| **Fri Oct 2** | Toy scored, mandates repaired (on the toy only), pocketful scratch run of stages 1–2, soak test, **freeze** | G3, G4 |
| **Sat Oct 3** | **SUBMITTED RUN.** Fresh room, fresh repo, one dispatch, hands off, recorded | G5, G6 |
| **Sun Oct 4** | Fresh-clone verification, `room.json`, FACTORY.md from measured data, video started. **Fallback run day** | G7 |
| **Mon Oct 5** | Video, slides, form, submit by 16:00 PKT | G8 |

---

## 1. Rules that decide the entry

Breaking any of these means **disqualified or unranked**, not a low score. Every one
maps to a check in §11.

| # | Rule (guide wording condensed) | How we prove it |
|---|---|---|
| **R1** | ≥ 3 distinct Band Desktop seats **you configured**, each with `mandates/<seat>.md` **named after the seat as the room shows it** (case and punctuation ignored), each opening with `Harness:` and `Model:` lines naming the real harness and exact model id | `harness check` (gate 1) |
| **R2** | Two of our seats exchange **typed `@handle` messages in both directions** (in chat text, not in tool output) | `harness check` (gate 2) |
| **R3** | `stage-1/` **builds and serves from a clean container by following its `RUN.md`**: a `Dockerfile` and `RUN.md` in every stage folder, runs with `-e PORT`, **no outbound network at runtime**, 2 vCPU / 2 GiB, healthy in 60 s | `harness run --mode isolated` (gate 3) |
| **R4a** | **Mandates are generic.** No endpoint paths, field names, error codes or test ids. The official list is in `harness/vocabulary.py`, and judges also run a *semantic* audit we can't see (`mandate_audit.py` isn't shipped) | `harness check` (gate 4, mandate part) + stranger test |
| **R4b** | **Code is written to the spec, not to the tests.** Enforced after the deadline | Builder works from the spec. Shipped checks are regression only |
| **R5** | **Hand-built code does not count.** Every line under `stage-N/` comes from the band in the room. The human commits nothing there | git authors = seat identities only |
| **R6** | **Autonomy.** In the submitted run, the dispatch is the only human input. No steering, approvals, hints, "continue" or reruns. Dispatching a stage twice counts as a rerun | Single dispatch message, visible in `room.json` |
| **R7** | **Video shows the factory working**: the room recording, a handoff between seats, and the result. A video with no room recording is disqualified, and slides alone don't count | Video edit checklist §10 |
| **R8** | Public GitHub repo a judge can clone **without Band membership**, with `README.md`, `FACTORY.md`, `mandates/`, `room.json` (full-session download), `stage-N/` | Fresh-clone `harness check` |
| **R9** | **No credentials anywhere**, including `room.json` (bearer tokens, `sk-…`, `ghp_…`, AKIA, `user:pass@`) | `harness check` credential scan |
| **R10** | **Stage claims.** `stage-N/` claims N only if it passes **≥ 50 % of every suite 1..N** and **does not pass all of suite N+1**. pocketful also probes `stage-2/` against suite 3. The chain counts contiguously from stage 1 | `harness run --all --mode isolated` |
| **R11** | Each stage folder is a **complete copy**, not a diff, with **no `.git` inside**, no submodules and no symlinks. History is pushed **as the seats made it**: no amend, rebase or squash | `harness check` + `git log` review |

---

## 2. Blockers: fix first (target Thu 18:00 PKT)

| ID | Blocker | Fix | Done when |
|---|---|---|---|
| **B1** | Docker daemon down (colima) | `colima start --cpu 4 --memory 8` | `docker run --rm hello-world` |
| **B2** | Band Desktop not installed / unverified | Install **Band Desktop ≥ 0.4.10** per <https://docs.band.ai/jam>, sign in | Runtime check passes in Settings → Runtime |
| **B3** | Kickoff repo not cloned | Clone `band-ai/dark-factory-wearedevs` to `~/band/dark-factory-wearedevs` (**outside** every result repo) | `python -m harness --help` runs in its venv |
| **B4** | Harness deps | In the kickoff repo: `python3.14 -m venv .venv && . .venv/bin/activate && pip install -r harness/requirements.txt && python -m playwright install chromium` | `harness --help` lists `run` and `check` |
| **B5** | Docker Sandboxes (`sbx`) for seats | `brew trust docker/tap && brew install docker/tap/sbx` → `sbx login` → `sbx daemon start --detach` → `sbx policy ls` (if empty, `sbx policy init balanced`; never reset an existing policy) → claude credential via `sbx secret set anthropic` or the `sbx run --name sbx-login claude` → `/login` flow → **`sudo launchctl config user path "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"` and REBOOT** (Band Desktop only sees `sbx` after a reboot) → Settings → Experiments → Docker Sandboxes → Runtime → Re-check | Band shows sandboxes available |
| **B6** | Codex auth for the Second Reader | `codex login`; note the **exact model id** for its `Model:` line | Codex completes a one-line task |
| **B7** | **This planning repo is PUBLIC** (`Abrar5510/dark-factory`) and `notes/` is untracked | `notes/` added to `.gitignore` (done). **Don't push `IDEA.md`/`BUILD.md` here** until §9 decides. They contain judge-anticipation and hotspot statistics | `git check-ignore notes/spec-hotspots.md` prints the path |

> Keep-awake: run `caffeinate -dimsu` in its own terminal for the whole plan.
> `pmset -g assertions` should show it.

**Paths used below (absolute paths go into dispatches; seats can't resolve relative ones):**

| Path | Holds |
|---|---|
| `~/band/dark-factory-wearedevs` | kickoff repo, read-only, the harness lives here |
| `~/band/band-work/toy-result` | rehearsal repo |
| `~/band/band-work/result` | **the submission repository** (fresh git repo, created on Sat) |
| `~/band/band-work/verify` | Second Reader's repo (kit), never readable by the Builder |
| `~/band/band-work/checks/` | every `harness run --out` dir (each must be **new**) |

The submission is a **new** public repo (e.g. `Abrar5510/pocketful-double-blind`),
pushed from `band-work/result`. It is **not** this planning repo, because the guide
requires the submitted run to start in a fresh result repository.

---

## 3. Critical path

```
B1–B7 → A: seats/sandboxes/identities → M: mandates drafted → T: toy run (overnight)
      → toy scored + mandates repaired + scratch pocketful stages 1–2 + soak → FREEZE
      → E: SUBMITTED RUN (one dispatch, recorded) → V: fresh-clone verification
      → P: room.json + README + FACTORY.md + video + slides → SUBMIT
```

Owners: **H** = human, **L** Lead · **B** Builder · **S** Surface · **2R** Second Reader ·
**R** Referee. Seats work only inside runs (T, scratch, E). Everything else is H.

---

## 4. Workstream A: seats and infrastructure (Thu, by 21:00 PKT)

| ID | Task | Done when |
|---|---|---|
| A1 | Create 5 seats with **plain-word display names**: `Lead`, `Builder`, `Surface`, `Second Reader`, `Referee`. Mandate slugs: `lead`, `builder`, `surface`, `second-reader`, `referee` (check.py strips non-alphanumerics, so "Second Reader" ↔ `second-reader.md` match) | All 5 visible; direct `@handle` reaches each and each replies |
| A2 | Harness/model per seat as in `IDEA.md`. Lead `claude-opus-5-5`, Builder and Surface `claude-sonnet-5-5`, Referee `claude-haiku-4-5-20251001` (all **Claude Code**), Second Reader **Codex** with its exact model id. The `Model:` line must be the **exact id Band shows** | Each `Test runtime` passes |
| A3 | Sandboxes: Builder and Surface are **New local agent → headless Claude Code, Docker Sandbox on, Direct host workspace, working dir = absolute `band-work/result`**. Second Reader is a Codex sandbox with working dir = `band-work/verify`. Referee and Lead run **on the host**, because they need both repos and Docker for `harness run` | "Which repo are you in / can you read X" probe confirms the Builder can't open `verify/` |
| A4 | One provider key per seat, so spend is measured per key. Fallback model configured where Band allows | Usage dashboard shows a separate line per seat |
| A5 | Pre-approve every permission the loop needs (git, Docker, browser, file writes in their dir, harness commands) | A dry task needs **zero** human clicks |
| A6 | Git identity per seat in its working dir (`user.name "Builder"`, `user.email builder@factory.invalid`, …). Commit messages name the handoff they answer (mandate rule, not a script) | `git log --format='%an %s'` on the toy shows seat names |
| A7 | Time the **first isolated run** on the toy (it builds the runner image and browser in Docker, and is slow the first time) | Duration noted for stage time caps |

---

## 5. Workstream M: mandates (draft Thu, freeze Fri 22:00)

**Every mandate's file layout:**

```text
Harness: Claude Code            ← exact harness name as Band shows it
Model: claude-sonnet-5-5        ← exact model id

<role in abstract terms> · <band roster with literal @handles> · <toy boilerplate> · <Double-Blind rules for this seat>
```

**Boilerplate every mandate carries** (taken from the official toy mandates, which set the minimum):

1. This is a dark-factory run. Never ask the human anything, never wait on a human; decide from the supplied requirements and evidence.
2. Blockers and evidence go to the Lead, who puts them in the final report.
3. You see only messages addressed to you. A message id, task id or "read the room" is not a handoff.
4. Handoffs are self-contained: paste the complete task, requirements, absolute repo path, revision and checks.
5. Long handoffs go in numbered parts, with the last one marked.
6. **Lead only:** before the first handoff, add every listed seat to the room with Jam's participant tool, verify the add, and retry a handoff Jam rejects as absent.
7. Use only the listed seats' literal `@handles`. Never search for, recruit or substitute agents.
8. Never amend, rebase or squash after a handoff. Never overwrite another seat's work.

**Double-Blind rules on top** (phrased generically, so they fit any spec):

- *Two blind readings:* Builder and Second Reader each get the full requirements. Neither reads the other's work area.
- *Divergence report:* two unattributed behaviours plus a minimal reproducing input. No opinions.
- *Rulings:* the Lead rules each divergence as *implementation wrong*, *reference wrong* or *requirements silent*, quoting the requirement word for word. The Referee checks the quote with a fixed-string search of the requirements text and rejects it if it's not verbatim.
- *Silent requirements:* the ruling picks the reading that keeps the stated invariants, then earlier-stage behaviour, and records it in an ambiguity ledger in the result repo.
- *Ruled cases* become permanent regression checks for later stages.
- *Folder discipline:* each stage is a full copy of the previous one with no nested `.git`, and must not implement a later stage.
- *Close a stage* at its time cap: tag the last green revision, post five lines of lessons, and carry open items forward as deferrals.

| ID | Task | Owner | Done when |
|---|---|---|---|
| M1 | Draft `lead.md`: intake, numbered full-text handoffs, stage copy-forward and tag, merge gate, rulings, stage report, spend row. **Writes no product code**, never reads reference source. Rejects a result without a full revision, a clean isolated boot, or a Referee verdict | H | File exists |
| M2 | Draft `builder.md`: service logic and storage in the result repo. Rejects a change that turns a ruled case red. Never reads the verification work area | H | File exists |
| M3 | Draft `surface.md`: user-facing surface, every state the requirements name, checked at phone and desktop widths, no runtime external assets. Rejects work where a named state is unreachable or overflows | H | File exists |
| M4 | Draft `second-reader.md`: independent executable reference, input generators, invariants, plus a self-check that seeded faults are caught. Never reads the implementation. Rejects its own kit if seeded faults survive | H | File exists |
| M5 | Draft `referee.md`: runs the official checker in **isolated mode** for each revision (boot, earlier stages, this stage, next-stage overshoot), replays ruled cases, runs the kit, verifies quotes, checks commits trace to a handoff. Read-only, relays only cases and verdicts, never fixes code. **Never edits the official checker or its tests** | H | File exists |
| M6 | **Vocabulary scan = the official one.** On a repo holding only `mandates/` + stub `README.md`/`FACTORY.md`/`stage-1/`, run `python -m harness check <repo> --track pocketful`. **Zero `gate 4:` lines.** No custom scanner (vocabulary.py *is* the judges' list). Also keep **no snake_case, kebab-case or `/path` tokens tied to the task**, and no track nouns ("wallet", "payment", "restaurant") | H | 0 gate-4 problems |
| M7 | **Semantic stranger test** (judges run one we can't see): read each mandate as if the team were building a CMS. Does every sentence still make sense? Rewrite any that don't. Same mandates also run the toy unchanged (portability proof) | H | 5/5 pass, recorded for FACTORY.md |
| M8 | Only seat mandates in `mandates/` (`check.py` treats **every `*.md` there as a mandate**). Lessons, ledgers and notes live elsewhere | H | `ls mandates/*.md` = 5 files |
| M9 | **Freeze:** `shasum -a 256 mandates/*.md > ~/band/mandates.FROZEN.sha256` (kept outside `mandates/`; record the hashes in FACTORY.md). No edits after this. Repairs happen on the toy only | H | Hash file exists Fri 22:00 |

---

## 6. Workstream T: toy rehearsal (Thu night → Fri 14:00)

| ID | Task | Done when |
|---|---|---|
| T1 | Set up `toy-result` per the guide (`mkdir -p …/stage-1 …/mandates`, `git init -b main`); copy **our** 5 mandates (not the toy's 3). The scaffold is optional | Repo exists |
| T2 | **One dispatch** to `@Lead` with all four toy stages and absolute paths (§8 template with `Track: toy`). Then hands off, same as the real run | Lead adds seats, first handoff lands |
| T3 | Check each stage as it lands: `python -m harness run --track toy --repo ~/band/band-work/toy-result --stage N --out ~/band/band-work/checks/toy-sN` | `claimed stage: N` for N = 1..4 |
| T4 | **Confirm the Referee ran the checks** (not the Builder), and that a seat posted the committed revision in the room | Visible in room |
| T5 | Download the toy room (**Download full session**) → `toy-result/room.json`, add stub README/FACTORY, run `python -m harness check ~/band/band-work/toy-result --track toy` | `ok — gates 1, 2 …` |
| T6 | **Credential-scan rehearsal:** if `check` flags `room.json` (seats' tool output can contain the service's bearer tokens), replace each value with `[REDACTED]` (the guide allows this) and re-run. Note how many hits so Sunday has no surprises | Procedure proven |
| T7 | Repair mandates from what broke (stalls, missing handoff content, seat asking the human). Re-run M6 + M7 | 0 gate-4 hits, stranger test passes |

## 7. Workstream S: scratch pocketful + soak (Fri 10:00 → 22:00)

| ID | Task | Done when |
|---|---|---|
| S1 | Scratch room + scratch repo: dispatch pocketful **stages 1–2** with the repaired mandates. Steering is allowed here because it's not judged, but **log every time you had to step in**. Each one is a mandate defect to fix | Stage 1 `claimed stage: 1` in isolated mode |
| S2 | **Hotspot yardstick:** score which `notes/spec-hotspots.md` stage-1/2 items the Second Reader's kit exercised **on its own**. Never show the file to any seat | % recorded (FACTORY.md metric) |
| S3 | **Soak:** leave the room idle 1 h, then send a task: does every seat still respond (sleep, socket drop, rate limit, key fallback)? | No dead seat, or documented recovery |
| S4 | Final mandate repair → M6 → M7 → **M9 freeze**. Write `~/band/lessons.md` (generic lessons, quoted only in the dispatch, never in mandates) | Frozen by 22:00 |

**G3/G4 fail → Saturday becomes a repair day; the run moves to Sunday 06:00 and verification gets compressed into Monday.**

---

## 8. Workstream E: THE SUBMITTED RUN (Sat Oct 3, dispatch 09:00 PKT)

### Pre-flight (08:00–09:00, all green or don't dispatch)

- [ ] P1 **Fresh room**, all 5 seats configured (the Lead adds them to the room itself)
- [ ] P2 **Fresh** `band-work/result` (`git init -b main`, empty, nothing committed by H in `stage-*/`) + fresh `band-work/verify`
- [ ] P3 `shasum -c ~/band/mandates.FROZEN.sha256` passes; `mandates/` copied into `result/` by H (before dispatch; mandates are H-authored, which is allowed)
- [ ] P4 Docker healthy, `caffeinate` on, keys funded, sbx daemon up, harness venv works
- [ ] P5 **Screen recording started** covering the Band room for the whole run (R7)
- [ ] P6 Dispatch text is final (below). Send it **once**

### Dispatch (the only human input, all four stages in one message)

```text
You are the lead seat for our factory. Build all four stages sequentially, coordinating
the other seats and keeping every stage in its own complete, buildable folder.

Workspace root: /Users/abrar/band
Working folder: /Users/abrar/band/dark-factory-wearedevs
Track: pocketful
Result repository: /Users/abrar/band/band-work/result
Verification repository: /Users/abrar/band/band-work/verify
Checks: python -m harness run --track pocketful --repo <result> --stage N --mode isolated --out /Users/abrar/band/band-work/checks/<new-name>
(run from the working folder with its .venv activated; the run for stage N also runs the N+1 suite, which must fail)

For stage N (1..4), the full spec is at <working folder>/pocketful/spec/stage-N.md.
Stage 1 goes in <result>/stage-1/. When a stage is done, copy the folder to stage-N+1/
(delete any nested .git), and extend the copy to the next spec. Each folder needs its own
Dockerfile and RUN.md and must not implement a later stage.

Paste the complete spec text into every delegated handoff.
<lessons.md quoted verbatim>
```

### Time caps per stage (a stage is never held hostage to perfection)

| Stage | Cap | Shipped coverage | 2R depth |
|---|---|---|---|
| 1 | 4.5 h | 79 % | light (shipped checks cover most) |
| 2 | 5 h | 35 % | full API + UI states |
| 3 | 6 h | 9 % | full (the oracle pays off here) |
| 4 | 5 h | 16 % | full |

The caps are written into the dispatch's lessons, **not** into mandates (they are
task-specific). Target finish is Sun 06:00 PKT.

### During the run: the human may only

Watch, take notes, and keep the machine alive (power, network). **No messages to the
room. No approvals, no restarts of a seat's task, no edits.** If it dies of an
infrastructure fault, it's a **new room + new repo** fallback run on Sunday. Never
re-dispatch in the same room, because that counts as a rerun.

---

## 9. Workstream V/P: verify and package (Sun → Mon)

Follow the guide's **"Before you submit"** list on a **fresh clone**, in order:

| ID | Task | Done when |
|---|---|---|
| V1 | Download the room: Band Desktop → room ⋮ → Open in Band → ⋮ → **Download → Download full session** → `mv ~/Downloads/<Room>.json result/room.json`. **Don't edit it**, except replacing credential values with `[REDACTED]` | File at repo root |
| V2 | **Read `room.json`** for anything private the scanner misses. If a real key is in it, **rotate** that key | Read end to end |
| V3 | H writes `README.md` (team, track, how to read the repo, link to the video) and `FACTORY.md` (§10). These are the only human-written files besides `mandates/` | Not placeholders |
| V4 | Commit (H's commits touch only root docs, `mandates/` and `room.json`). Create the **new public repo**, push **without** amend, rebase or squash | `git log` shows seat-authored commits untouched |
| V5 | `git clone <public url> /tmp/fresh && python -m harness check /tmp/fresh --track pocketful` | **`ok`**, 0 problems |
| V6 | `python -m harness run --track pocketful --repo /tmp/fresh --all --mode isolated --out ~/band/band-work/checks/final-all` | Every submitted folder **claims its own stage** and the chain is contiguous from stage 1. **Delete any folder that doesn't claim** (and everything above it, since it counts for nothing) |
| V7 | Follow each folder's `RUN.md` **by hand** (`docker build` → `docker run --network none -e PORT=8080 -p 8080:8080`), then use the UI at 375 px and desktop (stage 2+) | Starts, `/health` ok, UI usable |
| V8 | Confirm the reciprocal `@handle` exchange in `room.json`, and that no history was rewritten | Seen |
| V9 | Re-read every mandate with the stranger test one last time | Pass |
| V10 | Grep the public repo for leaks: `git ls-files \| xargs grep -il hotspot` is empty, and `notes/` is absent | Empty |

**Visibility decision for this planning repo** (`Abrar5510/dark-factory`, public): keep
`IDEA.md`, `BUILD.md` and `notes/` **local/untracked** through submission. FACTORY.md in
the submission repo carries the polished rationale.

---

## 10. Deliverables

### Submission repo tree (exactly what the guide specifies)

```text
pocketful-double-blind/
├── README.md        team, track, how to read this repo, video link        (H)
├── FACTORY.md       seats, setup, design choices, costs, failure handling (H)
├── mandates/        lead.md builder.md surface.md second-reader.md referee.md (H, frozen)
├── room.json        full-session download, unedited except [REDACTED]
├── stage-1/         Dockerfile, RUN.md, source                            (band)
├── stage-2/         …only folders that claim their stage                 (band)
├── stage-3/
├── stage-4/
└── verification/    the Second Reader's kit, ledger, ruled cases          (band)
```

The Second Reader's kit goes in at the end, **copied as files** from `verify/` (no
nested `.git`, no submodule), by a seat in the room, so it traces to the room too. The
ambiguity ledger and ruled cases live in it. **No `scripts/` written by H.** The official
harness already does offline boot, shipped checks, the overshoot probe and the
vocabulary scan. Quote verification (fixed-string grep) and commit tracing (`git log`)
are one-line commands the Referee's mandate describes generically.

### FACTORY.md must contain (rubric: "enough to stand it up")

- [ ] **Seat setup:** for each seat, its harness, model, sandbox mode, working dir, permissions, and git identity. Plus the exact steps to recreate the band (Band Desktop version, sbx steps, reboot note)
- [ ] **Design rationale:** the double-blind argument, why a different model family, why invariants judge concurrent runs
- [ ] **What we tried that failed** (toy and scratch-run findings, mandate repairs). The guide asks for this explicitly
- [ ] **Measured costs:** tokens, $ and wall-clock per seat per stage from the per-key dashboards, plus the share spent on verification. **Never invented**
- [ ] **Catch and recover:** a table with **real examples from the run**. Divergences split into implementation wrong / reference wrong / requirements silent, defects the shipped checks never asked about, minutes from divergence to green, ledger size, ruled-case count, and the Second Reader's seeded-fault kill rate
- [ ] **Portability proof:** the same frozen mandates ran the toy (results + hash)
- [ ] **Honest limits:** correlated misreads, stages not reached, open deferrals
- [ ] Final `harness run --all --mode isolated` output pasted

### lablab form (all required)

- [ ] Title · [ ] short description · [ ] long description · [ ] tech/category tags · [ ] cover image
- [ ] **Video**: room recording + walkthrough. It must show **the room, a handoff between seats, and the result** (R7). Use the "video moment" from IDEA (split blind threads → real divergence → verbatim-quote ruling → fix → green → per-stage table). **Never stage a conflict.** If the run was clean, show the seeded-fault kill table instead
- [ ] **Slide presentation**: design, cost, one bad result it caught, stage reached
- [ ] Public GitHub repo URL · then **keep the receipt**

---

## 11. "Passes all the tests": the exact commands

Run from `~/band/dark-factory-wearedevs` with `.venv` active. Every `--out` must be a new dir.

| What | Command | Pass looks like |
|---|---|---|
| Gates 1, 2, 4 (mandates) + layout + credentials | `python -m harness check <repo> --track pocketful` | `ok — gates 1, 2 and the mandate part of gate 4 pass` |
| Gate 3 + stage N claim (grading conditions) | `python -m harness run --track pocketful --repo <repo> --stage N --mode isolated --out <new>` | `claimed stage: N on the shipped checks` (the N+1 suite line **fails**; that's correct) |
| Whole chain | `python -m harness run --track pocketful --repo <repo> --all --mode isolated --out <new>` | each folder `claims stage N`, contiguous from 1 |
| Hand check | Follow `stage-N/RUN.md` with `docker run --network none` | `/health` = `{"status":"ok"}`, UI loads with no external assets |

**Shipped checks are a floor, not a target.** They cover 79/35/9/16 % of stages 1–4.
Judges run the full suites plus a pristine harness. "Green here" means
*directionally OK*. The Second Reader's kit is what covers the remainder, and
`notes/spec-hotspots.md` measures (privately) how much it covered.

---

## 12. Go / No-Go checkpoints

| Gate | Time (PKT) | Go looks like |
|---|---|---|
| **G1 Infra** | Thu 18:00 | B1–B7 done, harness `--help` runs, sandboxes visible after reboot |
| **G2 Drafts** | Thu 23:00 | 5 mandates, `harness check` 0 gate-4 hits, toy dispatched |
| **G3 Toy** | Fri 14:00 | Toy `claimed stage` ≥ 2, `harness check` ok on toy repo, ≥ 1 divergence→ruling→fix cycle seen (or kill-table proof) |
| **G4 Freeze** | Fri 22:00 | Scratch pocketful stage 1 claims in isolated mode, soak passed, hashes frozen |
| **G5 Dispatch** | Sat 09:00 | P1–P6 green, recording on, **one** dispatch sent |
| **G6 Health** | Sat 13:30 | Stage 1 closed or Referee actively gating; **zero human input given** |
| **G7 Verify** | Sun 16:00 | V5 + V6 green on fresh clone |
| **G8 Ship** | Mon 16:00 | Form submitted, video live, repo verified from a second machine |

**Point of no return:** if the submitted run hasn't dispatched by **Sun 06:00 PKT**,
run a 2-stage dispatch (stages 1–2 only) so a complete `stage-1/` + honest FACTORY.md
still ships.

---

## 13. Cut-scope ladder (in order, only when behind)

1. Stop at stage 3 (cap stage 4 at whatever claims).
2. Second Reader at full depth on stages 3–4 only.
3. Surface: only the states the stage-2 spec names; no polish beyond "no overflow at 375 px, visible labels, focus rings".
4. Slides: title, how it works, metrics.
5. Video: room recording + short walkthrough; cut the split-screen edit last.

**Never cut:** R1–R11, a claimed `stage-1/`, the room recording, `harness check` = ok.

---

## 14. Risks (trigger → action)

| Risk | Trigger | Action |
|---|---|---|
| Mandate vocabulary / semantic audit | any gate-4 line; any track noun | Fix on the toy only, re-freeze before Sat |
| Code written to tests (R4b) | Builder reads or quotes shipped test files | Mandate: the Builder works from the requirements; official check logs are regression feedback |
| Barrier leak | Builder can open `verify/` | Separate sandboxes (A3); Codex for 2R (OpenCode can't be sandboxed) |
| Credentials in `room.json` | `check` flags it | `[REDACTED]` the values, rotate if real, rehearsed in T6 |
| Nested `.git` in a stage | `check` reports a gitlink | The dispatch says to delete it; V5 catches it on the fresh clone |
| Folder overshoots | stage N passes suite N+1 | The Referee's isolated run reports it; the Lead rejects |
| Autonomy stall | a seat asks the human / waits | Boilerplate rule 1; caps; pre-approved perms; never answer it |
| Sandbox / Band regressions | Runtime re-check fails | Fall back to a host Claude Code seat (guide's advice), note it in FACTORY.md |
| Deadline | G3 slips past Fri 18:00 | Cut ladder step 1 immediately |

---

## 15. Next actions (now, in order)

1. `caffeinate -dimsu` in its own terminal
2. B1 colima → B3/B4 clone kickoff repo to `~/band`, venv, playwright
3. B2 Band Desktop + B5 sbx (**reboot needed: do it early**) + B6 codex login
4. A1–A6 seats, sandboxes, keys, identities
5. M1–M6 mandates → `harness check` 0 gate-4
6. T1–T2 toy dispatched before bed
