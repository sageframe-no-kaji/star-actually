# The `*, Actually` Ethos

*The canonical statement of what a `*, Actually` is, why it exists, and what makes one good. This is the soul the engine is built to serve and the source of every question Peko asks. If a design decision anywhere in the family contradicts this document, this document wins.*

---

## I. The failure it answers

Most technical documentation is written by the people who built the thing, for
the people who already understand the field. It is organized around the product's
surface — its commands, its config keys, its API — because that is how the
builder holds it in their head. And it fails the one job that matters: getting
someone from *"I have a question"* to *"I understand enough to act."*

The man page is the pure form of this failure. It is complete, correct, and
useless to the person who doesn't already know what they're looking for. It
answers questions you can only ask once you no longer need to.

The deeper reason the failure persists is not laziness. It is that **expertise
destroys the memory of not-understanding.** The moment you understand a thing,
you lose the ability to remember what confused you about it, or why the naive
model felt right. So the people most equipped to write the documentation — the
experts — are the people least able to write the part that would actually help.

`*, Actually` is the answer to that failure.

## II. The parti — reader agency

The reader of a man page has no agency. They get one altitude — usually the
wrong one — and no way to ask for more or less. `*, Actually` is what reader
agency looks like when the architecture is built to support it.

Every concept is given **depth layers** the reader dials through at will: a name
when a name is all they need, a definition when they want the shape of it, the
full theory when they mean to master it. The reader chooses their own altitude,
concept by concept, and changes it whenever they like. That choice — *the reader
deciding how deep to go* — is the whole point. Everything else is machinery in
service of it.

## III. Organized by question and relationship, not product surface

A `*, Actually` is not a tour of a product. It is a graph of **question-shaped
atoms** wired together by how they actually depend on and relate to each other.

The organizing question is never "what are the features of this thing?" It is
"what does a person arrive *wondering*, and what must they understand for the
answer to land?" The structure follows the shape of understanding, not the shape
of the product. This is why two `*, Actually` sites about the same tool could
look completely different: they serve different arrivals.

## IV. The node — the atom

A node is one concept: one thing a person can wonder about, answered at whatever
depths it warrants. One markdown file. It carries an identity and a body.

Its identity (frontmatter):

- **`id`** — kebab-case, unique, matches the filename. The node's address.
- **`title`** — the human name of the concept.
- **`type`** — what *kind* of knowledge it carries (see VI). The type constrains
  how it should be presented.
- **`summary`** — one line, for the reader deciding whether this is the node they
  want.
- **`requires`** *(optional)* — nodes you must understand *first*.
- **`related`** *(optional)* — nodes worth knowing *alongside* this one.
- **`entry_points`** *(optional)* — the questions that should *land* here (what
  the Receptionist routes to this node).

Its body is the depth layers.

## V. The five depths — progressive disclosure the reader dials

Depth is fixed by the system. A node need not reach the bottom — it stops where
it honestly stops — but the ladder is always the same, and it always starts at 1:

1. **Name.** *Just the name of the thing.* This layer is the title, nothing more.
   It exists so the reader who only needed to be pointed at the word gets pointed
   and leaves.
2. **Definition.** The shape of the concept in a sentence or two a novice
   actually gets. Not the dictionary definition — the *working* one. **This is
   where the "actually" usually first bites** (see IX): where the naive model gets
   corrected.
3. **Usage / context.** How it shows up in practice. When you meet it, what you
   do with it, what it looks like in the wild.
4. **Relationships.** How it sits against the neighbouring concepts — what it's
   often confused with, what it depends on, what depends on it. The prose
   companion to the `requires`/`related` graph.
5. **Theory.** The full model. Why it works the way it does, the mechanism
   underneath. For the reader who means to master it, not merely use it.

A node with only depths 1–2 is complete and valid — it simply doesn't go deep,
because the concept doesn't warrant it. **The discipline: a node that wants a
sixth depth is two nodes.** Depth is not a place to pour everything; it is a
ladder the reader climbs only as far as they choose.

## VI. Node types

The type declares what kind of knowledge the node carries, which constrains how
it should read:

- **`concept`** — an idea, a model, a "what *is* this."
- **`procedure`** — a how-to; steps toward an outcome.
- **`definition`** — a term pinned precisely; the shortest kind of node.
- **`scenario`** — a situated walk-through; "here's a real case and how it goes."
- **`troubleshooting`** — a failure and its resolution; organized around what
  went wrong.

Choosing the type is an act of understanding: it forces you to say what *kind* of
question this node answers.

## VII. The graph — dependency and lateral structure

Two edge kinds carry the structure of understanding:

- **`requires`** is the **dependency graph** — the honest prerequisite order. You
  cannot understand *snapshots* before *datasets*; you cannot understand
  *send/recv* before *snapshots*. Asserting a `requires` edge is asserting a
  claim about the shape of learning the subject. It is one of the highest-value
  judgments an author makes, and it is invisible in ordinary docs.
- **`related`** is the **lateral graph** — concepts worth holding side by side,
  the ones people conflate or that illuminate each other.

`entry_points` are where the graph meets a human arrival: the questions that
should route *to* this node.

## VIII. Chains — curated ordered paths

A chain is an explicit, ordered reading path through the graph — a sequence of
node ids someone decided belongs in that order. *Set up your first pool. Build a
backup strategy. Recover a failed disk.* The graph says what depends on what;
a chain says **here is a route worth walking, in this order, for this purpose.**

Chains are where authorial intent about *journeys* lives. The graph is the
terrain; chains are the trails.

## IX. The "actually" — the soul

Everything above is machinery. This is the soul.

The name is a promise. **"X, *Actually*"** means: *here is what's actually true —
correcting what you thought, or what you'd have assumed.* A node earns its place
in a `*, Actually` when it corrects a **naive model** — when it takes the thing
the reader wrongly believes, or would reasonably assume, and replaces it with
what's true.

- "Dedup saves space" — *actually*, it eats your RAM and rarely pays for itself.
- "RAIDZ is just RAID5" — *actually*, the write hole and the IOPS math make it a
  different animal.
- "You need ECC or your data rots" — *actually*, that's contested, and here's the
  real shape of the risk.

The "actually" is **not a field in the schema.** There is no `actually:` key. It
is a *posture* woven through the layers — sharpest in depth 2 and depth 4, where
the naive model gets named and corrected. It is the thing the facts do not
contain: a point of view *about* the facts, held by someone who knows where the
newcomer's intuition goes wrong.

And it is the thing **only the practitioner can supply**, because it comes from
having *had* the naive model. This is why capturing it is perishable and urgent:
the correction is only writable while the memory of believing the wrong thing is
still warm. A `*, Actually` with no "actually"s is a man page with nicer
navigation. The "actually"s are why it exists.

## X. What makes one good — and how they fail

**A good node:** answers one real question; corrects a naive model; goes exactly
as deep as the concept warrants and no deeper; declares honest `requires` edges;
carries a summary that lets the reader decide in one line whether to enter.

**A good instance:** is navigable by the question you actually arrived with;
lets you choose your altitude everywhere; has trails (chains) for the common
journeys; and — above all — is opinionated, because the opinions are the value.

**The failure modes:**

- **The knowledge dump.** Facts poured in at one altitude, no correction, no
  stance. A man page in new clothes. *The most common failure and the one the
  whole system exists to prevent.*
- **The feature tour.** Organized by the product's surface instead of the
  reader's question.
- **The bottomless node.** Everything crammed into depth 5 because the author
  wouldn't decide what the reader needs first.
- **The stanceless node.** Correct, complete, and soulless — it never tells you
  what you were about to get wrong.
- **The false prerequisite.** `requires` edges asserted by habit rather than by
  the real shape of understanding, forcing the reader through nodes they didn't
  need.

## XI. The questions this ethos asks

Because this document is the source of the interrogation, its convictions become
questions — the ones an author (and Peko on the author's behalf) must keep
asking of every concept:

- **What does a person *arrive wondering* here?** (→ the node, the `entry_points`)
- **What's the naive model of this — what would a smart newcomer wrongly assume?**
  (→ the "actually")
- **Where does the standard explanation fail?** (→ the correction, depth 2)
- **What must you already understand for this to land?** (→ `requires`)
- **What is this in one line? In a sentence a novice gets? In full theory?**
  (→ depths 1, 2, 5 — and where does this node honestly stop?)
- **What is it constantly confused with?** (→ `related`, depth 4)
- **What kind of question is this — a concept, a procedure, a failure?** (→ type)
- **What breaks if you get it wrong?** (→ why the node earns its place)
- **Is there a journey people take through several of these?** (→ chains)

If the answers are thin, the understanding is thin — and a thin instance is a
man page. The point of asking is to make the understanding thick enough that the
soul has somewhere to live.

---

*Parti: **give the reader the agency the man page denies them — and spend the
authorial judgment where it counts, on the "actually" that only someone who
once didn't understand can write.***
