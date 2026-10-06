# FACTORY.md — Double-Blind

> **Specify it twice, blind. Neither side is presumed right.**
> One seat builds the service. A second seat, on a different model family and unable
> to see the first, builds an executable reference from the same requirements. A
> referee compares them mechanically. Every disagreement is a defect in one of them or
> a gap in the requirements, and the lead rules on it by quoting the requirements word
> for word.

<!-- Every TODO(after run) below is filled from the submitted run's room.json, git log
     and harness output. Nothing in this file is estimated. -->

## Seat setup

Five seats, all Band **Remote Agents** driven through `band-sdk[opencode]`
(`OpencodeAdapter`) by one local OpenCode server, with models served by Featherless.

| Seat | Harness / model | Working directory | Writes | Git identity |
|---|---|---|---|---|
| Lead | OpenCode / `moonshotai/Kimi-K2.5` | `band-work/` | rulings, ambiguity ledger, stage folders (copy only) | `Lead <lead@factory.invalid>` |
| Builder | OpenCode / `deepseek-ai/DeepSeek-V3.2` | `band-work/result` | service logic and storage | `Builder <builder@factory.invalid>` |
| Surface | OpenCode / `deepseek-ai/DeepSeek-V3.2` | `band-work/result` | user-facing surface | `Surface <surface@factory.invalid>` |
| Second Reader | OpenCode / `moonshotai/Kimi-K2.5` | `band-work/verify` | conformance kit | `Second Reader <second-reader@factory.invalid>` |
| Referee | OpenCode / `deepseek-ai/DeepSeek-V3.2` | `band-work/` | nothing (read-only by mandate) | `Referee <referee@factory.invalid>` |

The Builder and the Second Reader are on different model families on purpose: that is
what makes the two readings fail independently.

### Standing it up

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

TODO(after run): per-seat tokens in / out and USD from the `usage` events in
`room.json` and the Featherless dashboard; wall-clock per stage from the first and
last commit under each stage folder; share of tokens spent by Second Reader + Referee.

| Seat | Tokens in | Tokens out | USD |
|---|---:|---:|---:|
| Lead | | | |
| Builder | | | |
| Surface | | | |
| Second Reader | | | |
| Referee | | | |

| Stage | Wall-clock | Result |
|---|---|---|
| 1 | | |

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

TODO(after run): one row per divergence from `room.json`, with the ruling type, the
quoted clause, the commit that fixed it and minutes from report to green. If there
were none, say so.

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
- **Time-boxed.** The dispatch capped the run at 8 hours and excluded stage 4.
- TODO(after run): stages not reached, open deferrals from the Lead's final report.

## Final harness output

```text
python -m harness check --track pocketful <repo>
python -m harness run --track pocketful --repo <repo> --all --mode isolated --out <new>
```

TODO(after run): paste both outputs, from a fresh clone.
