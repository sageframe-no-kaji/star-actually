---
kamae: 1
document: seed
project: peko
parent: star-actually
status: draft
name: Peko — the *, Actually content front-end
slug: peko
---

# Kamae 1 — Peko (Seed)

*A component of the `star-actually` family. Peko is the front-end the engine
never had: the part that turns a subject you don't understand yet into spun
thread the Loom can weave.*

---

## The Problem

You cannot author a `*, Actually` about a subject you don't understand yet.
That's the whole obstacle, and it's not laziness — it's structural. The engine
is domain-blind by design; all the intelligence lives in the instance content,
which is a subject decomposed into question-shaped nodes, each written at five
altitudes, wired into a dependency graph, sequenced into chains, and — above all
— carrying an *editorial stance*: what people get wrong, and the correction.
That stance is the soul of a `*, Actually`. It is not in the facts. It is a
point of view *about* the facts.

Here is the trap. The single most valuable authoring asset — the depth-1/2
layers and the "actually"s — requires remembering what it was like to *not*
understand the thing. And **expertise destroys that memory.** Once you get ZFS,
you can no longer reconstruct which thing confused you, or why the naive model
felt right. Every expert-written doc fails at exactly this point; that failure
is the reason `*, Actually` exists at all.

So the naive model — the confusion-map of the person who doesn't get it yet —
is the richest raw material there is, and it is **perishable.** It evaporates on
contact with understanding. Right now there is no tool that captures it. You
either already understand the subject (too late — the memory's gone) or you
don't (and can't author anything). Both live instances so far (SSH, Ho) worked
only because a highly-ordered source already existed to decompose. When it
doesn't — when the subject is one *you* still have to learn — there is no path
from "I have questions" to "I have an instance."

## The Landscape

The honest precedent is **your own `ho-kamae-1-seed` collaborator** — a probing
Socratic skill that interrogates, tracks open threads, and is honest about gaps.
Peko is that proven pattern aimed at a new target: subject-matter instead of
project-scope. No novelty to defend; it's a known shape extended, which is a
strength, not a weakness.

The wider space is LLM tutors (Khanmigo and kin), spaced-repetition systems
(Anki), and "learn X" documentation sites. They teach. **They do not harvest.**
A tutor walks you to understanding and then forgets the walk; the naive model it
just helped you shed is thrown away. Spaced repetition assumes the material is
already structured. Doc sites assume an author who already knows. None of them
captures the learning path as a reusable, authored artifact — and none of them
was built to feed a downstream engine.

That's the gap Peko sits in: a tutor whose *exhaust* is an instance. It teaches
you the subject and, in the same motion, spins the byproduct of that teaching
into `star-actually`-shaped content. The learning and the authoring are one act.

## The Vision

Peko is a probing collaborator that takes a practitioner who wants a
`X, Actually` but doesn't yet understand X, and — through flow-first tutoring —
teaches them the subject while capturing everything the teaching throws off:
the confusion before it resolves, the questions in the order they actually
arose, the sources worth trusting, and the emerging shape of the subject as a
node graph.

The output is two living, git-tracked records that grow through the
conversation and persist across sessions:

1. **The spun thread** — engine-shaped *proto-nodes*: rough-but-real
   depth-layered markdown with `id`, `type`, `requires`, `related`. This is the
   raw instance, accreting node by node as understanding forms.
2. **The narrative record** — a human-readable running account, periodically
   rewritten by a note-taker, so a person can read the state of understanding as
   prose, not as a node dump.

Alongside them, two ledgers: a **source ledger** (every source, tiered and
confidence-marked) and a **question/need log** (the real questions, the shape of
each confusion, and *why* the subject is needed).

There is a second thing going on, and it's why this is more than a convenience.
Peko is a prototype of a claim: **the model is a better medium for learning than
the doc.** Flow-first tutoring, captured as an ordered learning path, is an
instrument for *how a person actually learns a thing* — the sequence of
not-knowing that a finished artifact erases. The `*, Actually` instance is the
primary product. The captured learning path is the interesting byproduct, and it
may turn out to be the more valuable of the two.

## Audience

Me, explicitly — for now. Peko is the tool I need to build the instances I can't
currently build (ZFS is the immediate case). It is not built for a general
audience yet. But the second axis — learning-path capture as a prototype of a
learning medium — points at a broader future, and the design should not
foreclose it.

## Identity

**Peko** — ぺこぺこ (*pekopeko*). Two meanings, both load-bearing:

- *Hungry* — "onaka ga pekopeko," starving. Peko is appetite for knowledge; it
  devours sources and questions.
- *Bowing / humble* — the repeated bow, the deferential posture. This is the
  **beginner's mind**: the naive reader who doesn't know yet and bows to learn.

A tool whose entire value is capturing the not-yet-knowing learner should be
named for hunger and humility. It also sits cleanly beside the engine's other
named parts — **Loom** (weaves nodes into a site), **Terminal** (the reading
experience), **Receptionist** (routes a question to a node), and now **Peko**
(spins raw subject and live confusion into thread the Loom can weave).

## Project Nature and Intent

A skill inside the `star-actually` repo — part of the project and the engine,
not Ho-framework machinery. Personal tool. Simultaneously a **production tool**
(it will produce real instances I ship) and a **learning vehicle / prototype**
(it tests the model-as-learning-medium claim). That dual nature is deliberate and
should be protected: if it becomes only a content-authoring utility, the more
interesting half is lost.

## Architecture Direction

*Opinions, not commitments. System Design commits these.*

- **Capture-before-resolve.** The instinct will be to answer the question
  immediately. That overwrites the specimen. Discipline: log the question and the
  *shape of the not-knowing* before teaching. The confusion is the thing being
  harvested; pin it before it dissolves.
- **Flow-first, source-harvesting tutoring.** Resolve confusions model-first to
  keep momentum — flow is at least as important as grounding, because the flow
  *is* the prototype of the learning medium. But while teaching, Peko actively
  surfaces and logs quality sources, so grounding accretes continuously without
  gating the flow. Sources are woven in, not deferred to a batch and not made a
  precondition of answering.
- **Source tiering, always visible.** Three tiers: **canonical spine** (official
  docs, named books/experts), **web-found** (marked, unverified), and
  **operational reality** (the practitioner's own lived usage — first-class, not
  a footnote). Confidence is never hidden.
- **Two records, one note-taker.** Proto-nodes accrete continuously; the
  narrative record is rewritten periodically (cadence TBD — likely at phase
  boundaries or on demand, not every turn).
- **The records are the continuity.** Learning a subject like ZFS is a
  multi-session arc. The two records + two ledgers *are* the cross-session state
  — Peko resumes from them the way the State Memory discipline resumes a build.
- **Convergence condition.** A subject is "ready to author" when the
  confusion-map is resolved, the node graph has stabilized, and the spine sources
  are vetted. At that point Peko hands off.

## Constraints

- Records target the **engine schema directly** (proto-nodes: `id` / `type` /
  `requires` / `related` / depth-layered body). Not an intermediate form that
  needs translating later.
- Everything **git-tracked** from day one; records live in the instance repo
  (e.g. `zfs-actually/`).
- **Flow must not be gated** — no discipline (sourcing, validation, structure)
  may be allowed to stall the learning conversation.
- Must speak the engine's vocabulary (nodes, depth layers, chains, the named
  parts) so its output drops into `star-actually` without impedance.

## Scope Boundaries

Peko **is** the harvest: learn → capture → converge, emitting rough-but-real
proto-nodes plus the records and ledgers.

Peko is **NOT**:

- **The finishing pass.** It does not guarantee its proto-nodes pass
  `star-actually validate` / `build`. Polishing proto-nodes into a validated,
  buildable instance is a downstream step (a finishing pass, possibly an adapted
  Kamae authoring collaborator). Peko hands off; it does not close.
- **A general LMS or a spaced-repetition system.** It captures one learning arc
  toward one instance; it does not schedule review or teach a curriculum.
- **Multi-practitioner (yet).** One practitioner, one subject at a time.

The MVP line: a subject the practitioner could not author before is now a
stabilized proto-node graph + narrative record + vetted source ledger, ready to
hand to a finishing pass.

## Success Criteria

Observable, testable by someone other than me:

1. Starting from a subject I demonstrably don't understand (ZFS), a session
   series produces a proto-node graph that a *finishing pass* can turn into a
   buildable `star-actually` instance without re-doing the decomposition.
2. The captured question/need log contains "actually"s I could not have written
   from a position of expertise — corrections tied to specific confusions I
   actually had.
3. The source ledger lets me *act* — I can go verify a destructive operation
   against a cited spine source before I run it on real hardware.
4. After the arc, I can explain the subject's core mental model in my own words —
   i.e. Peko actually taught me, it didn't just extract from me.

## Where I'm Starting From

I built `star-actually` — I know the node schema, chains, the Loom/Terminal/
Receptionist split, and the depth-layer semantics cold. The proven pattern
(`ho-kamae-1-seed`) is mine. What's genuinely new territory is **the subject**
(ZFS is the first real test) and **the flow-vs-capture tension** — running a
fluid tutoring conversation while silently harvesting structure underneath it,
without the harvesting deadening the flow. That balance is the hard part and I
haven't built anything like it before.

## What I Want to Learn

Whether the model-as-learning-medium claim holds. Building Peko is how I find
out if flow-first tutoring, instrumented as a captured learning path, is
genuinely a better way to learn than a document — and whether the map of *how* I
learned a subject is an artifact with value beyond the instance it produced.
This is the reason to build Peko carefully rather than fast: the interesting
result is the learning experience, not just the content it emits.

## Open Questions

1. **Flow vs. safety.** Model-first teaching + a subject where mistakes lose data
   (ZFS `destroy`, resilver, pool import) = real hazard. The flag discipline
   ("unconfirmed — verify before you run it") plus mandatory spine-citation on
   destructive operations is the current answer. Is the flag enough, or do
   destructive claims need a hard inline gate that *is* allowed to interrupt flow?
2. **Note-taker cadence.** When does the narrative record get rewritten? Phase
   boundaries, turn count, on demand, all three?
3. **How rough is "rough-but-real"?** What's the minimum a proto-node must have to
   be worth keeping, without turning capture into a validation burden that gates
   flow?
4. **Convergence detection.** How does Peko *know* the confusion-map is resolved
   and the graph has stabilized — practitioner declaration, coverage heuristic, or
   both?
5. **Does the learning path have standalone value?** If yes, it may deserve its
   own record shape rather than being folded into the narrative record.
6. **Single vs. multi-subject.** Is the arc always one-subject-per-repo, or can
   Peko hold adjacent subjects (ZFS + general storage) in one session?

---

*Parti: **capture the naive model before expertise erases it.** Everything Peko
does serves that one act — the tutoring is the bait, the confusion-map is the
catch.*
