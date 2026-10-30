---
name: azure-ai-deep-dive-deck
description: |
  Builds an in-depth technical deck on a single Azure AI topic — A2A, AI gateway,
  evaluations, Content Understanding, Foundry IQ, guardrails, hosted agents, Model Router,
  agentic retrieval, reference architectures — with editable shape-built diagrams, facts
  verified against Microsoft Learn and public GitHub repos, one consistent modern 16:9
  layout and speaker notes on every slide.
  Use when the user asks to "build a deep-dive deck on X", "technical deck on X", "slides
  explaining how X works", "I'm presenting X to a customer", or asks for an Azure AI
  reference-architecture deck.
  Do NOT use for the recurring "Microsoft Foundry — what's new" deck (use
  foundry-whats-new-deck), pitch or sales decks or generic slide work (use pptx), or
  written documents (use docx).
metadata:
  category: writing
  icon: SlideLayout
---

# Azure AI Deep-Dive Deck

> Version 1.2.0 · 2026-10-30 · part of the Microsoft Foundry What's New and Deep-Dive Kit — history in
> `skills/CHANGELOG.md` of the kit repository.

## Overview

Builds a **new** in-depth technical deck on **ONE** Azure AI topic, from scratch, for a mixed
technical audience. The deliverable is a `.pptx` in `output/` (and, on request, the kit's `decks/`
folder) with editable shape-built
diagrams, every fact traced to a page fetched during the run, one fixed visual system, and
120–200 words of speaker notes on every slide.

Two shapes of topic are in scope, and both use the same arc and the same visual system:

1. **Explain this capability in depth** — Agent-to-Agent (A2A), AI gateway, evaluations,
   Content Understanding, Foundry IQ, guardrails, hosted agents, Model Router, Azure AI Search
   agentic retrieval, and comparable single capabilities.
2. **Present this reference architecture** — an Azure AI reference-architecture deck whose
   central diagram is modelled on a published Azure Architecture Center pattern (Section 3).

## Quick Start

```
User: "Build me a deep-dive deck on Model Router — I'm presenting to a customer."

1. SCOPE     → topic boundary + defaults (mixed technical audience, 45 min → 15 slides),
               stated in one line; ask at most one question, then proceed.
2. SOURCES   → web_search / web_fetch the Learn hub, overview, quotas/limits, what's-new,
               Architecture Center pattern, Azure-Samples GitHub. Record a URL per fact.
3. GATE      → unverified facts never reach a slide; they become
               "Presenter note: verify … before presenting" in the notes.
4. OUTLINE   → map onto the Section 1 arc, drop what does not apply, show the slide map.
5. BUILD     → slide-by-slide spec built with scripts/deck_lib.py (python-pptx);
               save "output/Microsoft Foundry Model Router.pptx"
6. QA        → scripts/deck_qa.py + render every slide to an image and inspect; fix;
               max three passes.
7. HANDOFF   → file name, slide count, defaults applied, pattern + Learn URL, verify list;
               offer kit registration and a companion notebook.
```

## When to Use

- "Build a deep-dive deck on Model Router" / "technical deck on Foundry IQ"
- "Slides explaining how A2A works" / "how does agentic retrieval work — make it a deck"
- "I'm presenting AI gateway to a customer next week"
- "A deck with the baseline Foundry chat reference architecture"
- Any request for a single-topic Azure AI technical session, 30–60 minutes

## When NOT to Use

- **The recurring "Microsoft Foundry — what's new" deck → `foundry-whats-new-deck`.** That skill
  MAINTAINS one recurring deck by patching dated editions in place. This skill BUILDS new decks
  on new topics. Never rebuild the what's-new deck here.
- **Pitch decks, sales decks, generic slide work → `pptx`.**
- **Written deliverables — briefs, reports, one-pagers → `docx`.**
- **Non-Azure or non-AI topics → `pptx`.**
- Multi-topic roundups: one deck, one topic. Split them.

> **Shared visual system.** Section 2 below is the **canonical definition** of the visual
> system, shared with `foundry-whats-new-deck` and implemented in `scripts/deck_lib.py`. Any change to the palette, geometry, typography
> or status-marking rules **must be mirrored in both skills** in the same pass, or the two decks
> drift apart.

---

## Kit and repository setup (shared by all three kit skills)

This skill ships in the **Microsoft Foundry What's New and Deep-Dive Kit** — a Git repository whose root holds
`kit.yaml`. Contributors clone the repository into a OneDrive-synced folder and attach that
folder to the Cowork task. The skill works with or without the kit:

1. **Find the kit.** Call `GetTaskFolders`; the kit is the attached folder (or sub-folder) that
   contains `kit.yaml`. Else look for `kit.yaml` in `input/`. If neither exists, work
   **standalone**: deliver to `output/` only and skip every registration step.
2. **Read `kit.yaml` fresh on every run** — it is the source of truth for folder paths
   (`paths.decks`, `paths.deck_changelog`, `paths.deep_dive_register`), deck naming, the
   deck ↔ notebook pairs, environment variables and known issues. Never rely on a copy from an
   earlier session.
3. **Presenter line.** The title slide carries a presenter line in a shape named `Presenter`
   (`deck_lib.title_slide` creates it; `deck_lib.set_presenter` fills it, adding it at the
   standard position when the deck has none, or removes it when given no text).
   - **Personal copy (`output/`).** Fill it for the person running the skill: `presenter` in
     their git-ignored `kit.local.yaml` when set, otherwise their Microsoft 365 profile
     (`GetMyDetails`: display name · job title). Ask nothing; the date line stays as built.
   - **Shared copy (kit `decks/`).** Never carries a person's name. After the upload, open the
     kit file on `live`, find the presenter line on slide 1 with `GetArtifactModel` and remove
     it (`delete_shape`; live editing refuses an empty `set_text`), then confirm it is gone.
     Editing in place keeps any sensitivity label; never upload an unlabelled copy to achieve
     this.
   - **Personalise a kit deck.** On "put my name on <deck>" (or before presenting any deck from
     `decks/`), copy the deck from `decks/` to `output/` and fill the `Presenter` shape as for a
     personal copy. Nothing else changes and nothing is uploaded back to the kit.
   Never hard-code a person's name in a shared file, script or deck.
4. **Layout code.** Build new slides with `scripts/deck_lib.py` (python-pptx; once installed, at
   `/mnt/user-config/skills/azure-ai-deep-dive-deck/scripts/`); it implements the
   visual system exactly. Run `scripts/deck_qa.py <deck> --render <dir>` before inspecting the
   rendered slides; its checks are necessary, not sufficient.
5. **Delivery.** Always save to `output/`. Upload into the kit's `decks/` folder only when the
   user asks, with `UploadFileContent`, after re-reading the target folder. Never overwrite a
   file there: the what's-new deck gets a new dated name for every edition
   (`naming.whats_new_deck`); a deep-dive deck is named `Microsoft Foundry <Subject>.pptx`
   (`naming.deep_dive_deck`, see Step 5), so when that name already exists in `decks/` the new
   edition stays in `output/` and the contributor replaces the kit file in the pull request —
   git history is the rollback. Cowork never pushes to GitHub: the contributor commits on a
   branch and opens a pull request.
   **Sensitivity labels.** OneDrive or Office can apply a Microsoft Purview sensitivity label,
   sometimes with encryption, when a file is saved. Cowork cannot read policy intent or change a
   label, and never removes or works around one (for example by uploading an unlabelled copy
   instead of the labelled file). After every upload, report the label shown on the file; when
   it is encrypted or not suitable for a public repository, tell the contributor to set the
   correct label in PowerPoint (Home → Sensitivity) before committing, and add a
   `known_issues` line to `kit.yaml` until it is done.
6. **Optional companions.** Hand-offs to other kit skills (`azure-ai-deep-dive-deck`,
   `foundry-whats-new-deck`, `deck-companion-notebook`) are offered only when that skill is
   installed; otherwise name it and point to `skills/` in the kit repository.

---

## Section 1: The narrative arc (default spine)

12–18 slides. **30-minute slot = 12 slides, 45-minute = 15, 60-minute = 18.** Sections flex by
topic — drop what does not apply — but **the order is fixed**:

| # | Slide | Purpose |
|---|-------|---------|
| 1 | Title | Topic, audience, date, presenter |
| 2 | Agenda | Numbered cards with slide ranges |
| 3 | What it is, and the problem it solves | Plain language, one slide, no jargon |
| 4 | Where it sits | Context diagram placing the topic among its neighbours in the platform |
| 5 | Anatomy | The 3–5 terms the rest of the deck depends on, each defined in one line |
| 6–7 | How it works | The mechanism as a numbered flow — numbers **ON the arrows**, not on the boxes |
| 8 | Reference architecture | Shape-built diagram — only when the topic has a published pattern |
| 9 | The decision surface | Modes, tiers, options, deployment choices as a matrix or parallel rows |
| 10 | How to choose | Three numbered questions, each with its answer — only when slide 9 exists |
| 11 | Identity, network and data boundaries | Only when the topic touches them |
| 12 | Operations | Limits, quotas, latency, cost drivers, what to monitor |
| 13 | **Compared with what it is confused with** | **MANDATORY on every deck** |
| 14 | When to use / when not to | Honest boundaries |
| 15 | Implementation path | Phases, prerequisites, what to prove first — when actionable |
| 16 | Status | What is GA, what is preview, what changed recently |
| 17 | References | The Learn and GitHub pages used |

**The "Slide" column gives each slide's PURPOSE, not its title.** Titles follow the noun-phrase
rule in Section 6 — e.g. purpose "What it is, and the problem it solves" → title "<Topic>
overview"; "Compared with what it is confused with" → "Comparison of <topic> and
<alternatives>"; "How to choose" → "Selection guidance".

**Slide 13 is never dropped.** Every topic is confused with something: A2A vs MCP; AI gateway vs
guardrails; Foundry IQ vs file search; Agent Service vs Agent Framework; evaluations vs
monitoring. Build it as **parallel rows with the same dimensions on both sides** — same
questions asked of each, never a column of features for one and prose for the other.

**Rule: one concept per slide.** The moment a concept needs two slides, it becomes a sub-section
with its own contrast slide.

---

## Section 2: Visual system (hard constraints — canonical)

- **16:9, 13.333 × 7.5 in.** Margins 0.6 in. Content area y = 1.35–6.75 in.
- **Segoe UI** throughout (fallback Aptos, Arial).
- **Every content slide:** kicker 8pt spaced caps in teal `#00B39F` at x=0.5 y=0.24; slide title
  26pt semibold navy `#101A3C` at x=0.5 y=0.51; one-line technical subtitle 12.5pt grey
  `#44495B` at y=1.02; footer left `Source: <short learn path>` 9pt grey at y=6.34; footer right
  `<Topic> · <Month Year> · <n>` 9pt grey right-aligned at x=9.2. **Identical positions on every
  content slide — a reader flipping through must see no drift.**
- **Palette:** title slide and dark bands `#0B1229`; headers, product boxes and titles `#101A3C`;
  accents, step numbers and kickers `#00B39F` (darker text variant `#008173`); card fill
  `#F6F8FD`; card border `#E1E7F4`; light band `#EBEFF7`; ink `#141B33`; muted `#44495B`; white
  `#FFFFFF`. **Maximum four colours on one slide.**
- **Semantic colours in every diagram, ALWAYS with a legend:** navy fill = the product or service
  being described; white fill with border = a capability or Azure resource; light band fill = a
  channel, caller or customer-owned element; dark navy band = a governance or control layer;
  dashed border = a boundary (subscription, VNet, service boundary).
- **Status marking:** **NO "GA"/"Preview" badges anywhere.** Preview = a single asterisk after the
  name, with one footnote per slide: `* preview — no service level agreement.` Anything unmarked
  is GA.
- **Body text minimum 7.5pt.** Never shrink below it — cut text to the speaker notes instead.
- Prefer **chips, key-value rows, parallel-row comparison tables and numbered cards** over
  paragraphs. A card holds one idea: a bold title of ≤5 words and one line of body.
- **No** shadows, gradients, clip art, photos, third-party logos, or URLs inside diagram boxes
  (URLs belong in the footer or the notes).
- **Cards:** fill `#F6F8FD`, 0.75pt border `#E1E7F4`, optional 3–5px accent bar in teal or navy on
  the top or left edge.
- **Flow diagrams:** numbered teal circles placed **ON the connector**, not inside the boxes;
  orthogonal connectors; **solid = data path, dashed = identity, control or telemetry**; legend
  bottom-left whenever more than one line style is used.

---

## Section 3: Reference-architecture diagrams (absorbed capability)

When the topic has a published reference architecture, **slide 8 is built from it**:

- Start from the closest pattern in the **Azure Architecture Center browse index**
  (`https://learn.microsoft.com/en-us/azure/architecture/browse/`) — e.g. "Baseline Microsoft
  Foundry chat", "AI landing zone", "Retrieval-augmented generation". Follow its component set,
  topology and flow direction. **Never invent a topology.**
- Diagrams are **ALWAYS native PowerPoint shapes with real, selectable text.** Never a generated
  image, never a screenshot, never a pasted bitmap. The user must be able to move a box and edit
  a label.
- Use **exact current Microsoft product names.** No retired names; expand acronyms on first use.
- Draw the boundaries the published pattern shows, **nested correctly**: subscription/resource
  group, region, virtual network and subnets, private endpoint, identity boundary.
- **Numbered steps 1..n on the connectors**, matching a "data flow" walkthrough on the following
  slide.
- **Max ~12 components per diagram.** Split a busy architecture into a **logical view** and a
  **network/security view** rather than shrinking text.
- Attribute the source pattern with its Learn URL **in the speaker notes**, and say where the
  drawn version simplifies it.

---

## Section 4: Workflow

### Step 1 — SCOPE (one exchange, then proceed; do not interrogate)
Confirm: the topic boundary; the audience (**default: mixed technical** — architects, developers,
technical decision makers); the slot length (**default 45 min → 15 slides**); and what the deck is
explicitly **NOT** about. If the user gave a topic and nothing else, **apply the defaults and
state them in one line on delivery.**

### Step 2 — SOURCE DISCOVERY
Find the topic's canonical pages before writing anything, using `web_search` / `web_fetch`:
the service's Learn hub and overview, its "what's new" page if it has one, its Architecture
Center pattern, its SDK reference, its quotas/limits page, and public GitHub samples
(`Azure/*`, `Azure-Samples/*`, `microsoft/*`, `microsoft-foundry/*`).
**Fetch Learn pages with the `/en-us/` locale segment** — an unprefixed URL can return an empty
page; retry with `/en-us/` before marking a source unreachable. **Record the URL for every fact.**

### Step 3 — ACCURACY GATE
Nothing reaches a slide until it is verified against a page fetched **in this run**. Never guess a
number, limit, model name, GA date, region list or preview status. Anything unverifiable goes to
the speaker-notes presenter checklist as `Presenter note: verify … before presenting`, **NEVER
onto a slide.** Note GA vs preview status for every feature, and prefer durable statements over
volatile ones.

### Step 4 — OUTLINE
Map the topic onto the arc in Section 1; drop the slides that do not apply; state the resulting
**slide map** (number, title, one-line purpose) and get it approved before building if the user is
present.

### Step 5 — BUILD
Write a **complete slide-by-slide spec** — exact text, shape geometry for diagrams, colours, fonts,
and the notes for every slide — and build it with `scripts/deck_lib.py` (`set_deck_footer`,
`title_slide`, `chrome`, `card`, `box`, `labelled`, `legend`, `step`, `rowtable`, `pfoot`, …).
If the build is delegated to the `pptx` capability, pass it the spec **and** the path of
`deck_lib.py`. **Set notes at build time, not afterwards.** Save as
`output/Microsoft Foundry <Subject>.pptx` (`kit.yaml` → `naming.deep_dive_deck`):

- `<Subject>` is the deck's topic in Title Case, as on the title slide but without the leading
  "Microsoft" or "Microsoft Foundry" — e.g. "Microsoft Foundry Copilot Harness Prompt Agents.pptx",
  "Microsoft Foundry Hosted Agents.pptx", "Microsoft Foundry Voice Live-Voice Agents.pptx".
- No "deep dive", no date and no version in the file name; the edition date lives in the
  deep-dive register and in `kit.yaml` → `decks[].edition`.
- Spaces are allowed; a hyphen joins two names of one subject; never use `\ / : * ? " < > |`.
- If that name already exists in `output/`, append ` <yyyy-mm-dd>` for the working copy only;
  the kit file keeps the plain name (Delivery, rule 5 of the kit setup).

### Step 6 — QA (mandatory, never skip)
Run `python scripts/deck_qa.py <deck> --render working/render/` (text checks: fonts below 7.5pt,
second person, pitch words, "Learn says", ambiguous actors, verify markers on slides, asterisk
without footnote, notes length, sentence-like titles), then **inspect every rendered slide
image.** Check for: text overflow or clipping; any font
below 7.5pt; titles out of position; overlapping or orphaned diagram shapes; detached connectors;
a missing legend; a missing footnote where an asterisk is used; slides without notes; any
unresolved verify marker left on a slide; any slide-wording breach — a title that is a sentence, clause or dash-joined pair of ideas, a subtitle with jargon, an unexplained term or an unexpanded acronym, "you"/"your" anywhere in slide text, a "Learn says/lists" attribution, an ambiguous actor label, or a table row of a different type from its siblings. Fix and re-render, **maximum three passes**, then
deliver with any remaining issue stated honestly. **A text-level patch is not proof — only the
rendered image is.**

### Step 7 — HANDOFF
State: the file name; the slide count; the defaults applied; the diagram pattern followed with its
Learn URL; and every open verify item. When a kit is attached, offer to **register the deck**:
an entry in the deep-dive register (`kit.yaml` → `paths.deep_dive_register`, default
`decks/DEEP-DIVE-DECKS.md`) using its template — **one entry per edition, never rewritten** — plus a
`decks:` entry for `kit.yaml`, both shown as a diff and applied only on approval.
If `deck-companion-notebook` is installed, offer a companion Python notebook for the kit (one step
per slide concept, paired to this deck's slide numbers).

---

## Section 5: Speaker notes (non-negotiable)

**Every slide gets 120–200 words of spoken prose that COMPLETE the slide rather than repeat it:**

- The one takeaway.
- The detail that did not fit: limits, quotas, latency, cost drivers, preview status, region
  availability.
- Why this design choice, and what was rejected.
- Known caveats and failure modes.
- The backing Learn or GitHub URL — cited by URL or "as per official documentation", never
  "Learn says".
- **Closing sentence: one likely customer question with its short answer.**

For diagram slides, **walk the numbered flow in words.**

---

## Section 6: Tone

Technical and specific, plainly spoken, written for a competent engineer who does not work with
this service every day.

- **No pitch framing.** Banned: "unlock", "empower", "seamless", "game-changing",
  "industry-leading", "revolutionary", "supercharge".
- No ROI claims, no competitive comparisons, no customer-logo slides.
- **Expand every acronym on first use.** Use **one term for one thing** throughout.
- **Never use a sentence as a slide, box or card title.**
- Use exact Microsoft product names.

**Slide wording (hard constraints — identical in `azure-ai-deep-dive-deck` and `foundry-whats-new-deck`; mirror any change):**

1. **Slide titles are short noun phrases, never sentences or clauses.** Good: "Voice Live API
   overview", "Voice Live session flow", "Model architectures and pricing tiers", "Comparison of
   real-time voice options", "Selection guidance, limits and status". Bad: "What it is, and the
   problem it solves", "How a Voice Live session works", "Native speech-to-speech or cascaded — the
   model decides", "Compared with what it is confused with", "Three ways to build…". No dashes
   joining two ideas, no rhetorical phrasing.
2. **Subtitles: one plain, logical, factual line that states what the slide shows.** No jargon, no
   clever framing, no unexplained internal terms — e.g. say "single speech model — audio in, audio
   out" / "three stages — speech recognition, text model, speech synthesis" on the slide rather than
   "native speech-to-speech" / "cascaded"; the Learn term may be given in the speaker notes. Expand
   or avoid acronyms on the slide.
3. **No second person on slides.** Never address the audience as "you"/"your" in any slide text —
   titles, subtitles, boxes, cards, chips, tables, questions. Use neutral subjects: "client
   application" not "your application"; "built by the application team" not "you build it";
   question cards as noun questions ("Existing Foundry agent in place?") not "Do you…?". Exception:
   official product/feature names keep their wording only where unavoidable — prefer a neutral
   equivalent on the slide and give the official name in the notes. Speaker notes are spoken by the
   presenter and may use natural spoken phrasing.
4. **Neutral sourcing.** Never write "Learn says", "Learn lists" or any similar attribution on
   slides **or in speaker notes**. Write "as per official documentation", or drop the attribution
   when the fact stands on its own — the URL already sits in the footer or the notes.
5. **Named actors.** No ambiguous actor labels such as "agent team" or "AI team". Name the role
   that acts: "development team", "platform team", "operators", "client application".
6. **One question per table.** Every row of a slide table answers the table's own question, with
   the same type of entry in every row. Never append a descriptive or summary row (for example
   "They handle …" under a list of libraries); put descriptions in a section label or caption.

---

## Output format

- **File:** `output/Microsoft Foundry <Subject>.pptx` (same name in the kit's `decks/`; Step 5)
- **Size:** 12–18 slides per Section 1; 16:9; Segoe UI; the Section 2 palette and geometry.
- **Slide bodies:** chips, key-value rows, numbered cards and parallel-row comparison
  tables — never paragraphs. Bullet lines are one idea each, minimum 7.5pt.
- **Every slide** carries 120–200 words of notes; every diagram is shapes-with-text plus a legend.
- **Handoff message sections:** file name and slide count; defaults applied; architecture
  pattern followed and its Learn URL; open verify items; offer kit registration (deep-dive
  register entry + `kit.yaml` deck entry) and, if installed, a companion notebook; after an
  upload, the sensitivity label the file carries.

---

## Guardrails

- **Never state an unverified fact.** Unverifiable → presenter checklist in the notes, never a
  slide.
- **Never render a diagram as a generated or pasted image** — real shapes with real text, always.
- **Never put GA/Preview badges, verify markers, internal iteration numbers, or any production
  scaffolding on a slide.**
- **Never reproduce Learn or GitHub content verbatim** beyond a short quoted snippet — summarise
  and link.
- **Never copy third-party logos or licensed imagery.**
- **Never overwrite an existing deck in `output/` or in the kit's `decks/`** — append a date to the
  `output/` copy; a kit file is replaced only by the contributor's pull request.
- **Never change, remove or work around a sensitivity label** — report it and leave the change
  to the file's owner.
- **No confidential, unannounced or roadmap material.** Public documentation only.
- **If research tools are unavailable, say so and stop** rather than producing an unverified deck.
- **Deliver the file and its caveats together;** never report the deck complete while QA is
  failing.
- **Never break the slide-wording rules** — slide titles are short noun phrases (never sentences,
  clauses or dash-joined ideas), subtitles are one plain factual line, and no slide text uses
  "you"/"your"; spoken phrasing belongs in the speaker notes only.
- **Never attribute with "Learn says/lists"** on slides or in notes, never use an ambiguous actor
  label ("agent team"), and never mix row types in a slide table — see Slide wording rules 4–6.
- **Never hard-code a presenter, a personal OneDrive path or an internal package feed** in a
  deck, a script or a kit file.
- Section 2 is canonical and shared — mirror any visual-system change into
  `foundry-whats-new-deck` and into `scripts/deck_lib.py`; Slide wording rules 1–6 are mirrored in
  `foundry-whats-new-deck`, and rules 4–6 in `deck-companion-notebook` Section 2.6.
