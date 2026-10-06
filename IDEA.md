# Double-Blind: the factory concept

> **Specify it twice, blind. Neither side is presumed right.**
> One seat builds the service. A second seat, running a *different model family*
> and unable to see the first, builds an executable reference of the same spec.
> A referee runs both on the same generated traces. Every disagreement is either
> a bug in one of them or a gap in the spec, and the lead rules on it by quoting
> the spec word for word.

Named after the double-blind trial. The bias it removes is the **shared
misreading**: in a typical factory the tests and the code come from the same
reading of the spec, so a misread clause passes review every time.

---

## Why this wins

| Fact | Consequence |
|---|---|
| Shipped checks cover **79 / 35 / 9 / 16 %** of the graded suites | Stages 3–4 are graded almost blind. Hidden tests all come from the spec. |
| We found **137 spec requirements** that the shipped tests never exercise (`notes/spec-hotspots.md`) | "Green on the shipped checks" is close to meaningless past stage 1. |
| Most rival entries run planner → coder → reviewer, and the reviewer reruns the visible tests | They top out wherever the visible tests stop. |
| Judges already know StrongDM-style holdout scenarios | Hidden example tests alone are not novel. |

**What's new:** an executable reference model, written blind by another model
family, works as an **oracle for any input**, not just a fixed set of examples.
Disagreement is **symmetric**: the court may find the *reference* wrong, or the
*spec* silent. That turns ambiguity into a logged, autonomous decision, which is
exactly what the no-human-input rule demands.

## The three moves

1. **Two blind readings.** The Builder and the Second Reader each get the full spec
   in their handoff. The Builder writes the service. The Second Reader writes a
   *conformance kit*: a naive reference model, a trace generator, and invariants
   that need no close reading (money conserved, replays change nothing, past reads
   never change). Docker Sandboxes with separate working directories plus BAND's
   mention-scoped messages make the barrier real, not a promise.
2. **Mechanical diff.** The Referee boots the stage folder in a clean offline
   container and runs the kit against it. Sequential traces are compared step by
   step. Concurrent bursts are judged by invariants only, never by exact output.
   A divergence is posted as *two unattributed behaviours plus a minimal trace*.
   The Referee never gives opinions.
3. **Rule by quotation.** The Lead rules each divergence as *builder wrong*,
   *reference wrong* or *spec silent*, quoting the spec verbatim; the Referee greps
   to check the quote is real. A "spec silent" ruling goes into the **ambiguity
   ledger** with the chosen reading: prefer the reading that preserves the spec's
   stated invariants, then the earlier stage's behaviour. Every ruled trace becomes
   a permanent regression test for all later stages.

## Seats (5)

| Seat | Harness / model | Owns | Rejects when | Sees |
|---|---|---|---|---|
| **Lead** | Claude Code / claude-opus-5-5 | Intake, full-text handoffs, stage copy + tag, merge gate, rulings, stage report and spend table. Writes no product code. | A handoff or result lacks full requirements, a revision, or a clean boot | Everything except the reference source |
| **Builder** | Claude Code / claude-sonnet-5-5, sandboxed in the result repo | Service logic and storage | A fix would turn a ruled trace red | Spec, traces, rulings. Never the kit. |
| **Surface** | Claude Code / claude-sonnet-5-5, sandboxed | User-facing surface, design tokens, every specified state at phone and desktop widths | A specified state is unreachable or overflows at phone width | Spec, API, browser check output |
| **Second Reader** | Codex (GPT family), sandboxed in a separate verification repo · fallback: OpenCode + Featherless Kimi/DeepSeek | Conformance kit: reference, generators, invariants, self-mutation check | Its own seeded faults survive its generators | Spec, rulings that name it, traces. Never the service code. |
| **Referee** | Claude Code / claude-haiku-4-5 | Offline boot, shipped-check regression, kit runs, next-stage overshoot probe, quote verification | Boot fails, a ruled trace is red, a quote is not verbatim | Both repos, read-only. Relays only traces and verdicts. |

All seat names and mandate lines stay generic. The Referee is cheap because its
job is mechanical. The Second Reader uses a different family so the two readings
fail independently.

## Stage loop

1. **Intake:** the Lead copies the previous stage folder, pastes the full stage
   spec to the Builder, Surface and Second Reader (split into numbered messages),
   and quotes the previous stage's lessons.
2. **Blind build:** all three work in parallel. Nobody waits.
3. **Gate:** for each revision, the Referee runs clean offline boot → all earlier
   ruled traces → shipped checks (as regression only; failures are reported next to
   the spec text they relate to) → the kit → the next-stage probe, which should fail.
4. **Court:** a divergence must reproduce twice (an invariant break only once),
   then gets a ruling, a fix via the room, and proof it fails before and passes after.
5. **Close:** at the time cap, or when fresh seeds stop producing divergences, tag
   the last green revision, write five lines of lessons, post the spend row. Open
   items carry forward as costed deferrals. A stage is never held hostage to perfection.

Dispatch **all four stages in one message** to the Lead (the guide allows it), so no
human touches anything between stages.

## Catch and recover

| Bad work | What happens |
|---|---|
| Builder misread the spec | Divergence → ruling quoting the clause → fix → trace kept forever |
| Reference misread the spec | Second Reader corrects it from the quoted clause and regenerates. The wasted effort is logged as oracle calibration. |
| Spec is ambiguous | Both readings logged. The invariant-preserving reading wins, then the prior stage's behaviour. Tagged as a judgement call. |
| Flaky / unreproducible | Voided with a reason after two failed reruns, so a harness bug can't freeze the line |
| Stage N breaks stage N−1 | Replayed ruled traces plus earlier suites block the merge |
| Folder solves stage N+1 | The Referee's overshoot probe flags it |
| Stall / silent seat | Time cap per stage, then tag last green and move on. The chain beats perfection. |

## What we deliberately cut (from the red-team pass)

- **A custom no-model SDK referee seat.** Too much new code for five days. A cheap
  LLM seat running scripts the band itself writes gives the same determinism.
- **File leases, per-commit message-id trailers, a rotating cross-family judge
  panel, LLM screenshot review.** Ceremony that costs tokens and can deadlock.
- **Diffing concurrent runs.** Legitimately nondeterministic. Invariants judge
  those runs instead.
- **Rules that hard-block on unruled traces.** Only verbatim-quoted rulings gate merges.

## Rubric mapping

- **Factory (50%):** generic by construction ("write an independent executable
  reference from the task text" fits any spec). Reaching stages 3–4 on hidden tests
  is where the oracle pays off. FACTORY.md gets real numbers (below).
  **Portability proof:** run the *same, unchanged* mandates on the official `toy`
  track (needed as rehearsal anyway) and report it. Rivals claim genericness; we show it.
- **App (25%):** a dedicated Surface seat, spec'd states at 375px and desktop, and
  model-free browser checks (no horizontal overflow, no console errors, every state reachable).
- **Teamwork (25%):** five seats with real lanes. Code comes from two seats
  (service plus the kit, imported with its history at the end). Every ruling is a
  review that changed the work. The trail stays traceable: divergence → ruling →
  fix commit.

## FACTORY.md numbers to measure (one API key per seat, so spend is per-key, not self-reported)

- Divergences per stage split by *builder wrong / reference wrong / spec silent*
- **Defects caught that the shipped checks never asked about**, by stage
- Tokens, $ and wall-clock per seat per stage, and the share spent on verification
- Minutes from divergence to green; ambiguity-ledger size; ruled-trace corpus size
- Second Reader's self-mutation kill rate (proof its kit can fail)
- Rehearsal yardstick: share of `notes/spec-hotspots.md` the Second Reader found
  **on its own**

## The video moment

Split screen: the Builder's thread and the Second Reader's thread, which never see
each other. The Referee posts a real divergence (two behaviours, one trace), the
Lead rules on it quoting the spec, the verified-quote check passes, the fix is
committed, and the trace turns green. End on the per-stage table. If the submitted
run happens to be clean, show the mutation-kill table instead. **Never stage a
conflict.**

## 5-day plan

| Day | Work |
|---|---|
| Wed Oct 1 | Create 5 seats, sandboxes, per-seat keys, pre-approve every permission and contact. Write mandates. Run the **toy** end to end (rehearsal + portability proof). |
| Thu Oct 2 | Repair mandates *on the toy only* (keeps track vocabulary out). Practice pocketful stages 1–2 in a scratch room and score against the hotspot yardstick. Soak-test an hour idle (sleep, socket drops, rate limits). |
| Fri Oct 3 | Freeze mandates (`harness check`). **Submitted run**: fresh room, fresh repo, one dispatch, hands off. Screen-record the room. |
| Sat Oct 4 | Isolated `--all` check on a fresh clone. FACTORY.md from measured data. Fallback day if the run died from an infrastructure fault. |
| Sun–Mon Oct 5 | Video (room recording + walkthrough), slides, submission. |

## Refinements from the spec repo (`band-ai/dark-factory-wearedevs`)

1. **The toy mandates set the minimum every mandate must include.** Start each
   mandate from that boilerplate:
   - no questions to the human after dispatch;
   - blockers go into the final report;
   - assume you see only messages addressed to you;
   - paste content, never a message id or task id;
   - split long handoffs into numbered parts and mark the last one;
   - the Lead adds each listed seat with Jam's participant tool and retries if a seat is absent;
   - never recruit or substitute agents;
   - never amend or rebase after a handoff.

   Double-Blind adds its rules on top of that.
2. **Gate 1 derives seats from message senders** in `room.json`. Every seat that
   ever speaks needs a `mandates/<slug>.md`. So seat display names should be
   plain words that slug cleanly (Lead, Builder, Surface, Second Reader, Referee).
3. **Gate 2 counts only what a seat *said*.** An `@handle` echoed inside tool
   output doesn't count. The Builder ↔ Referee loop (revision → verdict → fix)
   gives the two-way exchange naturally.
4. **Judges have tooling the kit doesn't ship.** The harness's digest code excludes
   `mandate_audit.py`, `evidence.py` and `reference_submission.py`, so expect:
   - **A semantic mandate audit, not just the regex.** Keep ownership abstract
     ("service logic", "user-facing surface", "independent reference"). Never
     describe the domain.
   - **Machine-checked traceability between the room and git.** Give each seat its
     own git author name, and require every commit message to name the handoff it
     answers. The Referee rejects a revision whose commits don't.
   - **A reference submission to compare against.** Another reason not to fit the
     shipped tests.
5. **Shipped tests can be edited locally without being detected, but judges run a
   pristine harness.** The Referee runs the harness from a read-only checkout and
   never changes it.

## Top risks

1. **Mandate vocabulary.** Ownership stays abstract (for example "service logic"
   versus "user-facing surface"). Lessons live in a separate file that is quoted
   only in handoffs. Mandates are hash-frozen before the run.
2. **Barrier leaks.** OpenCode seats can't be sandboxed, so prefer Codex for the
   Second Reader. The kit repo is imported into the submission only at the end.
3. **The Second Reader is late or wrong.** Scale its scope to the risk: light at
   stage 1 (79% of checks are shipped), full at stages 3–4. "Reference wrong" rulings are expected and measured.
4. **Correlated misreads still slip through.** Report that honestly. The
   different model family is the mitigation.
5. **Autonomy stalls.** Pre-approve all permissions, keep the machine awake
   (`caffeinate`), use keys with fallback models, and cap time per stage.
