# FACTORY.md — Double-Blind

> **Specify it twice, blind. Neither side is presumed right.**
> One seat builds the service. A second seat, on a different model family and unable
> to see the first, builds an executable reference from the same requirements. A
> referee compares them mechanically. Every disagreement is a defect in one of them or
> a gap in the requirements, and the lead rules on it by quoting the requirements word
> for word.

> **Result of the submitted run, stated first: the factory did not complete stage 1.**
> The committed `stage-1/` does not compile, so it does not start, and the official
> harness scores it stage 0. Two of five seats never acted, no divergence was ever
> compared, and `harness check` fails gate 2. The sections below describe the design
> as intended and then, under each heading, what actually happened. Nothing here is
> estimated; where something was not measured it says so.

## Seat setup

Five seats. In the submitted run they ran as **Band Desktop-hosted OpenCode seats**
(OpenCode 2.0.22, launched by Band Desktop's own daemon), not as SDK-driven Remote
Agents as first designed. Models were served by Featherless.

| Seat | Working directory | Writes (by mandate) | Model in the mandate | Model the directory's OpenCode config selects |
|---|---|---|---|---|
| Lead | `band-work/` | rulings, ledger, stage folders (copy only) | `moonshotai/Kimi-K2.5` | `deepseek-ai/DeepSeek-V3.2` |
| Builder | `band-work/result` | service logic and storage | `deepseek-ai/DeepSeek-V3.2` | `deepseek-ai/DeepSeek-V3.2` |
| Surface | `band-work/result` | user-facing surface | `deepseek-ai/DeepSeek-V3.2` | `deepseek-ai/DeepSeek-V3.2` |
| Second Reader | `band-work/verify` | conformance kit | `moonshotai/Kimi-K2.5` | `moonshotai/Kimi-K2.5` |
| Referee | `band-work/` | nothing (read-only) | `deepseek-ai/DeepSeek-V3.2` | `deepseek-ai/DeepSeek-V3.2` |

Two caveats about the submitted run that a reader should know before trusting the
mandates as a description of it:

- **The Lead's model does not match its mandate.** `band-work/opencode.json` selects
  DeepSeek, so the Lead most likely ran on DeepSeek, not Kimi. This is read from the
  config files, not from a model log.
- **We could not confirm the Band-hosted seats loaded their mandate files.** The
  SDK launcher passed each mandate as the seat's standing instruction; the switch to
  Band-hosted seats happened shortly before the run and we found no equivalent
  wiring. The Lead's behaviour is consistent with it not having its mandate: it
  wrote and committed product code, which its mandate forbids.

### Standing it up (the SDK-driven design, as rehearsed)

1. Create five Remote Agents at `app.band.ai/agents` named exactly `Lead`, `Builder`,
   `Surface`, `Second Reader`, `Referee`. Mandate filenames are the seat names with
   non-alphanumerics stripped to a slug, and `harness check` matches them.
2. Install OpenCode **1.18.x** in its own directory. `band-sdk` 4.0.0 speaks the 1.18
   API; OpenCode 2.x moved the routes and breaks every adapter call.
3. Put the provider key in the environment of the `opencode serve` process and
   reference it from the OpenCode config as `{env:FEATHERLESS_API_KEY}`. Start the
   server on loopback.
4. Run one adapter process per seat. Each one passes its mandate file as the seat's
   standing instruction, sets its working directory from the table above, sets
   `approval_mode="auto_accept"` and a 900 s turn timeout, and exports
   `GIT_AUTHOR_*` / `GIT_COMMITTER_*` so `git log --format=%an` shows seat names even
   though several seats commit to one repository.
5. Keep agent credentials and the provider key outside every git repository.
6. Create a room, add the five seats, and send the stage task to `@Lead` once.

No seat is sandboxed. Only seats Band Desktop launches itself can be, and these are
SDK-driven. See [Honest limits](#honest-limits).

## Design rationale

**The failure we designed against is the shared misreading.** In a planner → coder →
reviewer line, the tests and the code come from one reading of the requirements, so a
misread clause passes review every time. The track ships only 79 / 35 / 9 / 16 % of
its graded checks for stages 1–4, so a factory that iterates until the visible checks
are green stops being measured almost immediately.

Three moves, all of them in the mandates and none of them specific to this track:

1. **Two blind readings.** The Lead pastes the complete requirements to the Builder
   and, separately, to the Second Reader. The Second Reader writes a conformance kit
   from the text alone: a reference model that answers any input, generators, and
   invariants. It must seed faults into its own reference and prove its kit catches
   them, so the oracle is itself tested.
2. **Mechanical comparison.** The Referee boots the stage folder offline, runs earlier
   suites, this stage's suite, the next stage's suite (which must fail, or the folder
   has overreached), then the kit. It reports a divergence as two unattributed
   behaviours and one minimal input. It never gives an opinion and never fixes code.
3. **Rule by quotation.** The Lead rules each divergence as *implementation wrong*,
   *reference wrong* or *requirements silent*, quoting the deciding sentence. The
   Referee checks the quote with a fixed-string search and rejects a paraphrase. A
   "silent" ruling picks the reading that preserves stated invariants and goes into
   an ambiguity ledger. Every ruled case becomes a regression check for later stages.

Why this suits a run with no human in it: ambiguity is the thing a person normally
resolves. Here it becomes a logged, checkable decision, and a seat cannot win an
argument by asserting something the requirements do not say.

**Handoffs are self-contained** because a seat only sees messages addressed to it.
Every mandate requires the full requirements, repository path, committed revision and
commands run to be pasted, never referenced.

**Stages are time-capped.** At the cap the Lead closes on the last green revision and
carries open items forward. A finished earlier stage outranks a half-built later one.

## What we tried that failed

- **Claude Code and Codex seats in Docker Sandboxes** was the first design: the
  sandbox would have enforced the barrier between the two readings. We moved every
  seat to OpenCode on Featherless, and SDK-driven seats cannot be sandboxed, so the
  barrier is now enforced by working directories, mention scoping and the mandates.
- **A third model family for the Second Reader** (`MiniMaxAI/MiniMax-M2.5`) returned
  `capacity_exhausted` on three of three calls. A model that fails unattended is
  worse than a slower one; the blind pair became DeepSeek and Moonshot.
- **OpenCode 2.x** with `band-sdk` 4.0.0: different routes, wrapped responses and a
  forced server password broke the adapter. Pinned 1.18.x.
- **A long-lived `opencode serve`** started without the key in its environment
  resolved `{env:…}` to an empty string and failed as "must be signed in".
- **An escalate-to-human step** in the original scaffold. The rules allow no human
  input after dispatch, so every mandate now forbids asking and routes blockers to
  the final report.
- **The toy rehearsal did not finish.** One partial stage-1 folder scored 2 of 8
  shipped checks and no later stage was attempted. The submitted run is therefore the
  first complete run of this factory, and the mandates were not tuned on a rehearsal.

## Measured costs

From `room.json` and the git history of the submitted run.

| Measure | Value |
|---|---|
| Human messages in the room | 1 (the dispatch, 04:04:06 UTC) |
| Dispatch to first commit | 24 min (04:28 UTC) |
| Dispatch to the Lead closing the stage | 33 min (04:37 UTC) |
| Room events | 445 |
| Tool calls | 188 (Lead 106, Builder 62, Second Reader 20, Surface 0, Referee 0) |
| Isolated harness checks run by the seats | 3, all failed at the Docker build |
| Commits | 4, all authored by Lead |

**Tokens and USD were not measured.** The Band-hosted seats did not write usage
events into `room.json`, and we did not capture the Featherless dashboard for this
run, so we report no model spend rather than estimate one.

| Stage | Wall-clock | Result |
|---|---|---|
| 1 | 33 min to close | does not compile; harness stage 0 |

## Catch and recover

How bad work is caught, by design:

| Bad work | Caught by | Recovery |
|---|---|---|
| Builder misread a requirement | kit diverges from the service | ruling quoting the clause, fix, case kept as a regression check |
| Second Reader misread a requirement | same divergence, ruled the other way | reference corrected from the quoted clause |
| Requirements are ambiguous | neither quote decides it | invariant-preserving reading chosen, recorded in the ambiguity ledger |
| Ruling not grounded in the text | Referee's fixed-string search on the quote | ruling rejected and returned to the Lead |
| Stage N breaks stage N−1 | earlier suites and ruled cases replayed on every revision | revision rejected |
| Folder implements stage N+1 | next-stage suite passes when it must fail | folder claims nothing until trimmed |
| Service needs the network | clean offline boot in isolated mode | revision rejected |
| Weak oracle | Second Reader's own seeded faults survive | Second Reader rejects its own kit |
| Stalled seat or stage | stage time cap | close on last green revision, defer the rest |

What it actually caught in the submitted run:

**Nothing.** There were no divergences and no rulings, because the comparison never
ran:

- The Builder's service never compiled, so there was nothing to run the kit against.
- The Lead never handed anything to the Referee. The Referee and Surface seats joined
  the room and made zero tool calls.
- The only checks that caught anything were the three isolated harness runs the Lead
  started itself. Each failed at the Docker build (missing lockfile, then missing
  TypeScript compiler, then compile errors). The Lead closed the stage at its time
  cap with those failures recorded in `stage-1/FINAL_REPORT.md`.
- The Second Reader did produce a reference model, generators, invariants and a
  self-test from the spec alone (`verification/`). They were never exercised against
  a service.

So the catch-and-recover design above is untested by this run. What the run does
show is the stage cap working: the Lead stopped, committed, and reported honestly
that the build was red instead of claiming a result.

## Portability

The mandates name no endpoint, field, error code or product. `harness check` reports
no vocabulary problems for these five files against all three tracks (`pocketful`,
`tablekeeper`, `toy`). We did not complete a second build with them, so portability is
shown by inspection and by the scanner, not by a second result.

## Honest limits

- **The barrier is conventional, not enforced.** Nothing technically stops the
  Builder opening `band-work/verify`. `room.json` and the git history are the evidence
  of whether it held.
- **No completed rehearsal** before the submitted run (see above).
- **Two model families is weak independence.** Both can share a misreading; a ruling
  only happens when they disagree.
- **Stage 1 not reached.** Stages 2 to 4 not attempted. The Lead's ten deferrals are
  in `stage-1/FINAL_REPORT.md`; the first is "complete all API endpoints".
- **Gate 2 fails.** Only the Lead posted text messages. Builder and Second Reader
  worked from their handoffs but never replied with an `@handle`, so there is no
  two-way exchange in `room.json`.
- **Provenance is weak.** All four commits are authored by Lead, including product
  code, so the git history does not show the split of work the design intends.
- **The run was cut to 45 minutes** (30 to a first green build), down from the 8
  hours first planned, and stopped by the human at the cap while the Builder was
  still editing. Uncommitted work at that point is not in this repository.

## Final harness output

Run against the committed submission.

```text
$ python -m harness check --track pocketful <repo>
gate 2: two of your own seats must exchange messages using each other's @handles, with a reply in each direction
1 problem(s)

$ python -m harness run --track pocketful --repo <repo> --stage 1 --mode isolated --out <new>
src/database.ts(1,8): error TS2395: Individual declarations in merged declaration 'Database' must be all exported or all local.
...
The command '/bin/sh -c npm run build' returned a non-zero code: 2
highest contiguous stage: 0
claimed stage: none (a suite passed under 50% of its checks)
```
