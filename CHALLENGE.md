# The Challenge: Build an AI Dark Factory

Reference copy of the hackathon brief (lablab.ai page, as of 2026-09-30).
Rules in **Submission requirements**, **Disqualifiers** and **Judging** are
copied closely. Partner and marketing sections are condensed.

> Authoritative spec: <https://github.com/band-ai/dark-factory-wearedevs>
> (`docs/participant-guide.md`, `pocketful/spec`, `tablekeeper/spec`; run checks with `python -m harness`).
> Kickoff Sat 2026-09-26. **Submissions close Mon 2026-10-05, 23:59 PDT.**
> If this file and the spec repo disagree, the spec repo wins.

---

## The idea

Build a software factory in **BAND Desktop**: a band of coding agents that
**plans** work, **implements** it, **hands off evidence**, and **independently
checks** its own results. You give it a job and decide whether to accept what
comes back.

**You submit three things: the factory, the run that produced the result, and the result.**

An AI dark factory is a software production process that keeps working without
a person directing every step. You design the team, its handoffs and its checks,
then see whether it can:

1. build a service,
2. repair failures,
3. extend what it built without breaking what already works.

## Tracks (pick one, stay in it)

Both are clean-room clones of a well-known product. You compete only against your track.

| Track | Clone of | The hard part |
|---|---|---|
| 🍽️ **tablekeeper** | OpenTable (restaurant reservations) | A table must **never be double-booked**, under concurrency, retries and time zones. |
| 💸 **pocketful** | Venmo (wallet & payments) | Money must **never be created, destroyed or spent twice**, under concurrent transfers, retries and rounding. |

**Our track: pocketful.**

---

## Submission requirements

### 1. Your band
- **At least three distinct coding-agent seats** in BAND Desktop, **each with a mandate file**.
- Seats may share a runtime and a model.
- A seat can be any runtime BAND supports, including one built on the BAND SDK and run on your own machine, a cloud box or a CI runner.
- Models: Featherless credits, or bring your own model-provider access.

### 2. Mandates must be generic ⚠️ (disqualifier)
A mandate is the standing instruction for a seat: what it owns, how it takes and
hands off work, when it rejects something.

- It **must not name anything specific to the track or challenge**: no endpoint paths, no field names, no error codes.
- Track detail belongs in the **task you paste into the room**, not in a seat's standing instructions.
- **The test:** could you hand these mandates to a team building something completely different, and would they still make sense? If not, it's a transcript of this problem, not a factory.
- **A mandate naming track-specific detail disqualifies the entry.**

### 3. Your repository
- One **public GitHub repo** a judge can clone **without BAND Desktop membership**.
- **One folder per completed stage**: `stage-1/` … `stage-4/`, each a **complete, buildable service**. Submit only stages you completed. **Minimum to be eligible: a complete stage 1.**
- Plus:
  - the seat **mandates**,
  - the **factory description** (`FACTORY.md`),
  - the **export of the BAND Desktop room** the band worked in.

### 4. Your video
- Must include a **recording of the BAND Desktop room** that generated the solution, **and a walkthrough**.
- **A video without the room recording disqualifies the team.**

### 5. Your service
- Must **build and serve from a clean container with no outbound network**. Test this before submitting. **A service that doesn't start scores zero.**
- CPU/memory caps, harness concurrency and per-request timeouts are published with the spec (see spec repo).

## Disqualifiers at a glance
- ❌ A mandate that names track-specific detail
- ❌ A video without the BAND Desktop room recording
- ❌ A service that does not start from a clean container

---

## Judging criteria

| Weight | Criterion | What it means |
|---|---|---|
| **50%** | **Factory** | Generic, effective, reusable mandates another team could point at a different problem. **How far through the four stages** it got with code that meets the spec. A `FACTORY.md` sufficient to stand it up: **seat setup, design rationale, measured costs, and how it catches and recovers from bad work.** |
| **25%** | **App** | What the factory built: a **coherent, presentation-ready, responsive UI** over **maintainable code**. |
| **25%** | **Agent Teamwork** | **Collaboration:** seats really shared the work — review changed something, handoffs carried the whole task, code traces to the room. **Autonomy:** in the submitted run, **the task dispatched for each stage is the only human input** — no steering, approvals or reruns. |

---

## lablab.ai submission form checklist

- [ ] Project title
- [ ] Short description
- [ ] Long description
- [ ] Technology & category tags
- [ ] Cover image
- [ ] Video presentation (with room recording!)
- [ ] Slide presentation
- [ ] Public GitHub repository link

## Repo deliverables checklist

- [ ] `stage-1/` complete, buildable, starts in a clean no-network container
- [ ] `stage-2/` … `stage-4/` (as far as we get)
- [ ] Mandate file per seat (≥ 3), generic — no track detail
- [ ] `FACTORY.md`: seat setup, design rationale, measured costs, catch/recover story
- [ ] BAND Desktop room export
- [ ] Clonable without BAND membership

---

## Platform & partners

**BAND** (presenter) — interaction layer for AI agents: a shared environment where
agents on any framework communicate, exchange context, coordinate work, recruit
other agents and involve humans. Your band lives in BAND Desktop, and **the room
it works in is part of your submission**.

| Resource | Link |
|---|---|
| Hacker guide | <https://www.band.ai/hacker-guide> |
| BAND Desktop (install, CLI, coding-agent plugin, readiness checks, live board) | <https://docs.band.ai/jam> |
| Docs | <https://docs.band.ai/> |
| Connect any agent | <https://docs.band.ai/getting-started/connect-remote-agent> |
| Agent API | <https://docs.band.ai/api/introduction> |
| SDK setup (adapters: Claude Code, Codex, LangGraph, CrewAI, Pydantic AI, Agno…) | <https://docs.band.ai/integrations/sdks/tutorials/setup> |
| Account / Discord | <https://app.band.ai/> · <https://discord.com/invite/5YkNXmYfjk> |

**Docker** — Docker Sandboxes: isolated, reproducible containers, customizable with kits.
[Benefits](https://www.docker.com/blog/benefits-of-sandbox-environments/) ·
[Get started](https://docs.docker.com/ai/sandboxes/) ·
[Kits](https://docs.docker.com/ai/sandboxes/customize/kits/)

**Featherless AI** — serverless, OpenAI-compatible inference over 30k+ open models
(DeepSeek, Llama, Qwen, Mistral, Kimi…). Can power any seat.
$25 per-request credits per participant (first 1,000), no model size limit, up to 256K context;
promo code emailed before kickoff. Signup needs a card — cancel before next billing cycle if not continuing.
[Docs](https://featherless.ai/docs/overview) · [Tech page](https://lablab.ai/tech/featherless)

**WeAreDevelopers World Congress North America** — San Jose, Sep 23–25. Hackathon
runs fully online; sign-ups are eligible for a free congress ticket.
