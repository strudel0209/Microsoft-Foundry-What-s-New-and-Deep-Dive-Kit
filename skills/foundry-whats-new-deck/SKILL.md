---
name: foundry-whats-new-deck
description: |
  Maintains the recurring "Microsoft Foundry — what's new" technical deck (one dated
  edition per refresh): detects new Foundry releases from Microsoft Learn, the Foundry blog
  and GitHub, drafts slide patches with source URLs, and applies approved patches in
  place to the existing .pptx without changing its layout, palette or slide map. Runs
  on a fortnightly detect / monthly patch cadence.
  Use when the user asks to "refresh the Foundry what's-new deck", "what changed in
  Foundry since the last deck", "patch the Foundry deck", "run the Foundry change log",
  "update the Foundry release deck", or "new version of the Foundry deck".
  Do NOT use for new decks on other topics (use azure-ai-deep-dive-deck or pptx
  instead), pitch decks, or written documents (use docx).
metadata:
  category: automation
  icon: SlideSearch
---

# Foundry "What's New" Deck — maintain and refresh

> Version 1.1.0 · 2026-10-22 · part of the Microsoft Foundry What's New and Deep-Dive Kit — history in
> `skills/CHANGELOG.md` of the kit repository.

## Overview

Keeps ONE recurring deliverable current: the **"Microsoft Foundry — what's new"**
technical deck (16:9; current slide count and map recorded in `CHANGELOG.md` and in the
slide map below). Each refresh is a **dated edition**, named
`Microsoft-Foundry-Whats-New-<yyyy>-<mm>.pptx`, located per Step 0 — the current edition is
the newest entry in the deck changelog (`kit.yaml` → `paths.deck_changelog`, default
`decks/CHANGELOG.md`; edition 2026-10-22 when this version was published). Internal iteration
counters never appear in file names, on slides or in the changelog.
The deck follows the Foundry layer model and its layout is fixed; never rebuild it —
the job is to **detect** what changed in
Microsoft Foundry, **propose** slide patches with sources, and **apply** approved
patches in place, producing the next dated edition plus a `CHANGELOG.md`.

This is the maintenance companion to `azure-ai-deep-dive-deck`, which builds new single-topic
decks from scratch and owns the canonical visual system.

Cadence: **DETECT every two weeks**, **PATCH roughly monthly** (or sooner when the
threshold in Step 2 is met). Run the baseline sweep QUARTERLY (or on request, or after
any change to the deck's scope statement). Record the date of the last sweep in
`CHANGELOG.md` as **Last sweep:** so the next run can tell whether one is due. A
fortnightly detect run without a due sweep does the dated diff only.

## When to Use

- "Refresh the Foundry what's-new deck" / "new version of the Foundry deck"
- "What changed in Foundry since the last deck?" / "run the Foundry change log"
- "Patch the Foundry deck with <item>" / "update the Foundry release deck"
- A scheduled fortnightly run of the Foundry detect cycle

## When NOT to Use

- A new deck on another Azure AI topic (Azure OpenAI, Copilot, AI Search, a customer
  reference architecture) — use `azure-ai-deep-dive-deck` (single topic) or `pptx` instead
- A from-scratch rebuild of the Foundry deck — build it with `azure-ai-deep-dive-deck`'s
  visual system, then hand the result back to this skill for maintenance
- Any generic slide work, pitch or sales decks — use `pptx` instead
- Written documents, release notes as prose, or emails — use `docx` or reply in chat
- Editing slide layout, palette or positions — that is a redesign, not a patch; ask
  the user to redesign explicitly (a new deck, built with `azure-ai-deep-dive-deck`)

## Quick Start

```
User: "What changed in Foundry since the last deck?"
1. Locate the current deck (latest dated edition — attached folder, then input/, then
   output/; see Step 0) and the last run baseline
   (CHANGELOG.md run date) — if none, baseline = the deck's footer month.
2. DETECT: web_fetch every source in Step 1, diff against the baseline date
   (catalog pages: diff by content, see Step 1), classify each item, map it to a
   slide number from the Slide Map.
3. Present the CHANGE LOG (markdown table) and whether the patch threshold is met.
4. If the user says "patch it": PROPOSE per-item patches → user approves per item
   → APPLY in place with python-pptx → save the new dated edition → render changed slides →
   write CHANGELOG.md → report.
```

## Kit and repository setup

Follow **"Kit and repository setup"** in `azure-ai-deep-dive-deck` (identical for all three kit
skills; if that skill is not installed, read `skills/azure-ai-deep-dive-deck/SKILL.md` in the kit
repository). In short: find the folder holding `kit.yaml` via `GetTaskFolders`, read it fresh,
take every path from it, deliver to `output/`, upload into the kit only on request, never push to
GitHub. Points specific to this skill:

- **Shared edition, many maintainers.** Before APPLY, re-read the deck changelog: if a newer
  edition than your baseline has appeared (another contributor ran the skill), stop and re-base on
  it — never fork the edition line. One edition per month; a second run in the same month appends
  `-<dd>`.
- **Presenter line on slide 1** stays as it is unless the running user asks to put their own name
  (from `GetMyDetails`) on the edition they present.
- **QA script:** `scripts/deck_qa.py <deck> --render <dir>` runs the text checks of Step 3 item
  10 and renders the slides; inspect the images of every changed slide.

## The Deck Contract (patches MUST respect this)

### Structure

16:9, 26 slides, five sections following the Foundry layer model:
**01 Microsoft Foundry architecture · 02 Foundry Models · 03 Foundry Tools and
Microsoft IQ · 04 Agent Service and Agent Framework · 05 Foundry Control Plane ·
Wrap-up.**
Section 03 holds four slides (11–14) since edition 2026-10-22 added the browser automation
slide at the user's direction (Step 2, "User-directed slide"). Section 04 holds six slides
(15–20): the documented exception, taken under the importance-override in Step 2.

### What this deck covers

In scope: Microsoft Foundry itself, across its five layers — platform and architecture,
Foundry Models, Foundry Tools and Microsoft IQ, Foundry Agent Service and Microsoft Agent
Framework, Foundry Control Plane — plus the developer surfaces (SDK, API, VS Code toolkit,
azd, Foundry Local) and the Azure services Foundry directly depends on (Azure AI Search for
Foundry IQ, Application Insights for tracing, API Management as AI gateway).

Out of scope by design: Microsoft Copilot Studio, Azure Machine Learning, Azure AI Content
Understanding, Microsoft 365 Copilot as a product, and non-Azure platforms. A finding in
these areas is classified "out of scope" with that reason, not dropped silently.

Use this statement to decide whether a new capability deserves placement in the deck or an
out-of-scope note.

### Slide map (number · title · what it holds · churn)

| # | Title | What it holds | Churn |
|---|-------|---------------|-------|
| 1 | Title (dark navy) | session title, presenter, "In this session" numbered list | low |
| 2 | Agenda | six numbered cards with slide ranges | update ranges ONLY if slides are added/removed |
| 3 | Microsoft Foundry — high-level architecture | build surfaces / three product columns (Models, Agent Service, Tools and Knowledge) / Control Plane band / Foundry resource strip / Foundry Local aside | low |
| 4 | Foundry AI workload — end-to-end reference architecture | channels → AI gateway → Foundry boundary (Agent Service, models, toolbox, standard setup) → tools/knowledge/peer agents → Control Plane; numbered flow 1–8 | low |
| 5 | Microsoft Foundry API and SDKs | client column / project endpoint with three surfaces (OpenAI-compatible, Anthropic Messages, Foundry-native) / why it matters / when to use which / **"New in 2026" band** | medium — the "New in" band churns |
| 6 | Developer tooling in 2026 | VS Code Toolkit, azd extension, DevPack, Foundry MCP Server, Foundry Local | medium |
| 7 | Foundry Models: catalog and offerings | two category cards (sold by Azure / partners and community, same four rows) + table **"What arrived in the catalog in 2026"** (Model · Provider · Category · Status/date · Context window · Notable) | **HIGH — main churn point** |
| 8 | Deployment types | matrix (Standard / Provisioned / Batch / Developer × Global / Data Zone / Regional), options and alternatives strip, how-to-choose, good-to-know | low |
| 9 | Priority and Flex processing | service tiers, latency targets table, downgrade rules, Flex processing* card (selection, price and service level, behaviour when capacity is short, supported models) | medium |
| 10 | Model Router | routing pool by provider, modes, subset/failover, billing, quota tiers, limits, retired models | **HIGH** |
| 11 | Tools, Toolboxes and Skills | three definitions, flow agents → toolbox → tools, chip grid (toolbox-capable / toolbox-only / direct-only) | medium |
| 12 | Browser automation tool | numbered flow agent → toolbox (browser automation tool) → Playwright Workspace → websites, with the return loop as step 4; numbered step captions; human oversight band (Live View, Take control, screenshot recording); four setup-path cards; right-hand cards: before connecting, regions, governance, comparison with computer use | medium — regions and private-browsing status churn |
| 13 | Foundry IQ | knowledge base pipeline, indexed vs remote sources, status/access/billing cards | medium |
| 14 | Microsoft IQ | what each layer knows / connection matrix (direct · via Toolbox · via Foundry IQ KB) / identity-billing-setup cards | medium |
| 15 | Foundry Agent Service | callers → Agent Runtime (prompt agent — text or voice*, hosted, Responses call) → Models/Toolbox/Memory/Observability, identity band, Agents API card, hosted runtime facts, basic vs standard setup | medium |
| 16 | Protocols and APIs an agent speaks | inbound/outbound lanes, tool availability classic→new table | medium |
| 17 | Publishing a hosted agent to Teams and Microsoft 365 | hosted agent capability and status table; the source-IP filtered Activity Protocol route for a project with public network access disabled; enable_m365_public_endpoint; reachability-not-authorization cautions | medium |
| 18 | Agent Service vs Agent Framework | comparison table + "how they meet" band | medium — versions churn |
| 19 | Routines: running an agent without a person | three trigger types (timer, recurring cron, event — GitHub issue and Teams message); one-agent action with run history; the Microsoft routines-versus-workflows decision table; dispatch identity, region and CMK limits; the reminder tool as the agent-scheduled follow-up | medium |
| 20 | Long-running agents | why they matter / comparison table / six-step recovery ring / what you get / use when | low |
| 21 | Foundry Control Plane: the four pillars | Observe (incl. Insights*) · Evaluate · Protect · Govern, "built on" strip; each pillar ends with a "→ slide n" link to slides 24, 23 and 22 — update the links whenever slides move | low |
| 22 | Guardrails and Azure AI Content Safety | three actors with four numbered intervention points on the arrows, control = risk × point × action cards, how Content Safety fits | low |
| 23 | Evaluations | four-column pipeline (what to evaluate / dataset / evaluators chip grid / results), lifecycle band | medium — evaluator list churns |
| 24 | Tracing | four columns (sources / one standard / where they land / where you read them), four-step enablement | low |
| 25 | Changes since Build 2026 | timeline with eight dated dots in two rows (newest right) + "still preview" band | **HIGH — rewrite every cycle** |
| 26 | References | Learn URLs left, blog and code right, "staying current"; cumulative verify list in the notes | medium |

### Visual rules (hard constraints)

- **Typography:** Segoe UI everywhere. Kicker 8pt spaced caps teal `#00B39F` above
  every title; title 26pt semibold navy `#101A3C` at x=0.6in y=0.55in; one-line
  subtitle 12.5pt grey `#44495B`. Footer left `Source: learn.microsoft.com/…` 9pt;
  footer right `Microsoft Foundry · <Month Year> · <n>` 9pt right-aligned. Identical
  positions on every content slide.
- **Palette:** navy `#0B1229` (title slide, governance bands), `#101A3C` (headers,
  product boxes), teal `#00B39F` (accents, step numbers), card `#F6F8FD`, border
  `#E1E7F4`, band `#EBEFF7`, ink `#141B33`, muted `#44495B`. Max four colours per
  slide. No shadows, gradients, clip art, photos or logos.
- **Semantic colours in diagrams, always with a legend:** navy = Foundry product;
  white = capability / Azure resource; light band = channel / customer-owned;
  dark navy = governance layer; dashed = boundary.
- **Status labelling:** NO "GA" / "Preview" badges. Preview = single asterisk after
  the name, with the footnote `* preview — no service level agreement.` Unmarked = GA.
- **Text density:** body text minimum 7.5pt; never overflow a box; prefer chips,
  tables and key-value rows over paragraphs; one idea per card; no URLs inside diagram
  boxes (the source URL belongs in the footer only).
- **Terminology:** Microsoft product names only — Microsoft Foundry, Foundry Models,
  Foundry Agent Service, Foundry IQ, Foundry Tools, Foundry Control Plane, Toolbox,
  Microsoft IQ (= Work IQ + Foundry IQ + Fabric IQ). Never "Toolkit" for tools (the
  Toolkit is the VS Code extension). No pitch words (unlock, empower, seamless,
  game-changing, industry-leading). No box titles that are sentences.
- **Nothing production-related on slides:** no `[verify: …]` markers, no "verified
  against …", no status-label explanations. All of that lives ONLY in speaker notes, as a
  plain sentence that ends "… should be confirmed before presenting".
- **Speaker notes on every slide** (the presenter's own style, adopted in edition 2026-10-22):
  flowing spoken prose in British English, roughly 230–500 words, that complements the slide
  rather than reading it out. Structure:
  1. An opening line saying what the slide does, optionally "Read it …" (top to bottom, left to right).
  2. "The core idea is that …".
  3. A walk-through in ordinal steps: a bold line ("First, Foundry Models.") followed by a
     paragraph that starts with a space and explains it.
  4. Customer questions folded into the prose — "A common question is whether …" — never a
     "Likely question:" label.
  5. Facts still to verify as one sentence ending "should be confirmed before presenting";
     the cumulative list sits in the slide 26 notes.
  6. A closing line: "The key takeaway is …", "The architectural principle is …", "The overall
     narrative is simple: …" or "From a CSA perspective, …".
  Never "Likely question:", "Presenter note:", "Learn says/lists" or "you/your" aimed at the
  audience. Notes the presenter wrote by hand are kept: a patch adds or amends sentences in the
  same style; only notes the presenter has not rewritten are replaced as a whole.

### Slide wording (tone and language)

Applies to every title, subtitle and text line written or patched onto a slide.

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

## Core Instructions

### Step 0: Locate the baseline

1. Find the current deck, in this order: (a) a folder attached to the task (call
   `GetTaskFolders`; when it holds `kit.yaml`, look in its `paths.decks` folder; list it and pick
   the latest
   `Microsoft-Foundry-Whats-New-<yyyy>-<mm>[-<dd>].pptx` by date in the name); (b) files
   attached to the task in `input/` that match the edition naming pattern
   `Microsoft-Foundry-Whats-New-<yyyy>-<mm>[-<dd>].pptx`; ignore any other .pptx in
   `input/` (an unrelated deck must never be treated as the baseline) and mention the
   skipped file in the report; (c) the task's own `output/` folder from an earlier
   run in the same task. If the user names a path, use that. If no deck is found
   anywhere, stop and ask the user to attach the current edition — never build a new
   one here.
2. Read the deck changelog — `kit.yaml` → `paths.deck_changelog` when a kit is attached, else
   `CHANGELOG.md` next to the deck; the **Run date** field of
   its newest edition entry is the baseline (older entries may label it 'Facts verified'
   — treat that as the run date). If there is
   no changelog, use the month/year in the deck footer as the baseline and say so.
3. Extract the deck's current text per slide with `python-pptx` (or the workspace
   office helper `python scripts/office/unpack.py`) so patches can be diffed against
   real current text.

### Step 1: DETECT (every two weeks)

Fetch each source with `web_fetch` (use `web_search` only to locate a moved page) and
diff against the baseline date:

| Source | What to look for |
|--------|------------------|
| `https://learn.microsoft.com/en-us/azure/foundry/whats-new-foundry` | (i) updates to facts already on slides 5, 6, 25 (API surfaces, tooling versions, dated timeline entries); (ii) entirely new Foundry capabilities announced anywhere on the page — read the "new articles" / "updated articles" lists, not only the dated highlights. The page can lag by a month or more: when it still shows an older month, rely on the blog roundup and on each feature page's "Last updated" date |
| `devblogs.microsoft.com/foundry` — monthly "What's new in Microsoft Foundry" roundups **and** single-feature announcement posts (for example "Browser automation tool in Microsoft Foundry is now GA", 19 October 2026) | (i) restated or corrected facts behind slides 25, 26; (ii) newly announced capabilities the deck has never mentioned (e.g. autopilots, private skill catalog, content provenance, multi-agent orchestration patterns) |
| `https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure` and `https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-from-partners` | (i) changes to models already in the slide 7 table (status, context window, provider); (ii) new model *classes* the deck has no row or card for (reasoning models, model migration paths, deprecation waves) |
| `https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router` (routing pool by provider; retired models where the page lists them) | (i) pool, mode, billing and quota changes behind slide 10; (ii) new routing or selection capabilities that slide 10 does not model at all |
| `github.com/microsoft/agent-framework/releases` | (i) version and feature-parity changes on slide 18; (ii) new framework capabilities with no slide — orchestration patterns, workflow primitives, new hosting surfaces |
| `https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate` (tool availability) | (i) tool-availability rows on slides 11 and 16; (ii) whole new agent surfaces or APIs (e.g. multi-agent orchestration with the Responses API) that the deck does not cover |
| `https://learn.microsoft.com/en-us/azure/foundry/concepts/capability-reference` | The authoritative capability inventory: (i) corrections to capabilities already shown; (ii) any capability listed there with NO coverage anywhere in the deck — the primary source for the baseline sweep below |
| Optional internal sources the user names (Teams channels via `ListChannelMessages`, SharePoint via `SearchM365` / `ReadFileContent`) | (i) internal confirmation of facts on slides; (ii) capabilities named internally that have no deck coverage — subject to the internal-source guardrail |

A source's job is to report everything new, not only what fits the current slides. Map to a slide AFTER classifying, never before.

Fetch Learn pages with the `/en-us/` locale segment; an unprefixed URL can return an
empty page on first try — retry with `/en-us/` before marking a source unreachable.

Model catalog pages (models sold by Azure, models from partners, Model Router) do not
date every row. For these, do not diff by date alone: compare the fetched page against
the deck's extracted slide 7 and slide 10 text. Report each model or router-pool entry
that is on the page but absent from the deck, and each entry on the deck that is no
longer on the page.

For every new or changed item:

1. **Classify** as one of: `GA` · `preview` · `retirement` ·
   `breaking change — service/Foundry SDK` · `breaking change — open-source SDK` ·
   `new model` · `new capability — no home in the deck` (a real Foundry capability
   that maps to no existing slide) · `docs-only`.
2. **Map** it to a slide number from the Slide Map (an item may hit two slides,
   e.g. a new model → 7 and 24). An item classified `new capability — no home in the
   deck` is NOT mapped to an existing slide and is NEVER dropped: it goes to the
   change log's "New capabilities with no place in the deck" section with a proposed
   placement, or an explicit out-of-scope reason from the deck scope statement.
3. **Record** the exact source URL fetched *in this run* and the date shown on it.
4. **Baseline sweep — run QUARTERLY (or on request, or after any change to the deck's
   scope statement):** in addition to the date diff, list Foundry capabilities that are
   documented but are not covered to the required depth anywhere in the deck, regardless
   of their date. Record the date of the last sweep in `CHANGELOG.md` as **Last sweep:**
   so the next run can tell whether one is due; a fortnightly detect run without a due
   sweep does the dated diff only. Read the capability reference
   (https://learn.microsoft.com/en-us/azure/foundry/concepts/capability-reference) and
   the new-article lists on the what's-new pages, and rate each capability with the depth
   test below against the extracted deck text including speaker notes. Report these in
   the "New capabilities with no place in the deck" section marked 'pre-baseline', with
   the depth level.

**Depth test — how deeply is a topic covered?**

Coverage is never binary. Wherever this skill decides whether a capability is "covered"
— the baseline sweep above, the gaps list, and every new-capability judgement — rate it
on this scale instead of a covered/not-covered keyword match.

Rate every capability against the extracted deck text (slides AND speaker notes) on this scale:

| Level | Meaning |
|---|---|
| 0 | Absent — no mention anywhere |
| 1 | Named only — appears in a chip, list, diagram box or timeline dot, with no definition |
| 2 | Defined — at least one line stating what it is |
| 3 | Treated — a card or block giving what it is, why it matters, and its status |
| 4 | Owns a slide |

Rule: a GA capability that is a distinct concept a customer would ask about must reach
**level 2 or higher**. Level 0 or 1 on such a capability IS a finding, reported as 'thin
coverage' in the New capabilities section with its current level. A preview sub-feature
of a capability already at level 3 or 4 may sit at level 1 and is not a finding.

Disambiguation: a string match counts only if it refers to the SAME concept. Check the
surrounding text before accepting a match — for example 'MAI-Voice-2' (a text-to-speech
model) is not coverage of 'Voice Live' (the agent voice capability), and 'workflows and
routines' inside a chip is level 1 for routines, not coverage.

Output the **CHANGE LOG** (see Output) and state whether the patch threshold is met.
Store this run's date as the new baseline (in the CHANGE LOG header; it moves into
`CHANGELOG.md` when a patch is applied).

If a source cannot be fetched, list it under "Not checked this run" with the error —
never infer what it might say.

### Step 2: PROPOSE (when the threshold is met)

**Materiality — does a finding deserve space?**

A 25-slide deck cannot absorb every documented capability. Before proposing a patch for a
new capability or a thin-coverage finding, apply this test. It is material if ANY of:
(a) it is a new concept a customer in an architecture session would ask about;
(b) it changes an architecture or procurement decision (cost, residency, identity,
networking, SLA, deployment choice);
(c) it corrects or contradicts something the deck currently states;
(d) it is a GA capability sitting at depth level 0 or 1.

It is NOT material if it is: portal convenience or notification surfaces, generic Azure
platform capabilities that are not Foundry-specific (cost management, high availability
and disaster recovery, Azure Government, CI/CD pipelines, diagnostic plumbing), a
domain-specific model family outside the deck's audience, or a preview sub-feature of a
capability already treated at level 3 or 4.

Findings that fail the materiality test are still logged — in a subsection 'Known, not
included' with a one-line reason — but they are NOT proposed as patches and do NOT count
toward the threshold. Only material findings count as notable items.

**Promotion ladder — row, card, or slide?**

Always choose the SMALLEST container that fits the finding. Work down this ladder and stop
at the first that applies.

1. **Table row** — the item is another instance of something the deck already tabulates: a
   model (slide 7), a deployment type or SKU (slide 8), a routing-pool entry (slide 10), a
   tool availability row (slide 16), a dated event (slide 25). Add the row; prune the
   oldest row if the table would overflow.
2. **Card** — the item is a capability belonging to a topic that already has a slide, and
   that slide has room. This is the default outcome for most findings. Example: a new
   built-in evaluator is an Evaluations capability, so it is a card on slide 23, not a slide
   of its own.
3. **New slide** — propose one by EITHER route; the routes are independent.
   **Route A — crowding.** ALL THREE hold:
   (a) **Distinct concept** — it is not a feature or option of something already on a
   slide; a customer would ask about it by name and could confuse it with a neighbouring
   concept.
   (b) **No room** — the host slide's section is already full (four cards, or a fifth would
   push any text below 7.5pt), so a card would degrade the layout.
   (c) **Needs more than one idea** — a single line cannot make it useful; it needs at
   least what it is, when to use it, and how it differs from the concept it is confused
   with.
   **Route B — importance override.** The finding passes the importance test below, EVEN
   WHEN the host slide has room for a card: a capability Microsoft documents as its own
   topic is not served by a chip.
   Example that passes Route A: autopilots (distinct agent concept, slide 15 is full, and it
   only makes sense alongside 'how is this different from a hosted agent?'). Example that
   fails Route A clause (a): routines — but routines passes Route B, which is what promoted
   it to its own slide in the September 2026 edition.

If a finding fails the new-slide test but cannot fit as a card, propose it as a card on the
nearest slide WITH a named trade-off: which existing card is shortened or merged to make
room. Never silently shrink the visual rules.

**Importance test — when a topic outranks the budget**

The override is narrow. A finding takes a slide over the budget only when BOTH gates pass.

**Gate 1 — no existing correspondence in the deck.** The capability sits at depth level 0 or
1 on the depth test in Step 1, measured against the extracted deck text INCLUDING speaker
notes. A capability already at level 2 or higher has a home — enrich that home instead. This
gate is what stops ordinary announcements earning slides: most findings are new facts about
topics the deck already treats, not new topics.

**Gate 2 — Learn-derived significance.** Judge importance from how Microsoft documents the
capability, not from how important it sounds.

| # | Signal | How to check |
|---|--------|--------------|
| 1 | Own capability-family row | Listed as its own row in `https://learn.microsoft.com/en-us/azure/foundry/concepts/capability-reference`, not as a clause inside another row |
| 2 | Own documentation subtree | Both a concept page and a how-to page (for example `agents/concepts/<thing>` and `agents/how-to/<thing>`); a section inside another article does not count |
| 3 | Own announcement | A dedicated Foundry blog post, or its own entry in the "New articles" list on the Learn what's-new page |
| 4 | Microsoft contrasts it with a neighbour | The concept page says "use X instead when …", or carries a decision table; Microsoft naming the confusion is the strongest evidence that a customer will ask about it |
| 5 | Generally available | Not preview |

**Rule:** signals 1 and 2 are mandatory. Gate 2 passes at **four of five**.

- Record which signals hold, each with the URL fetched in this run, in the patch proposal.
- Both gates pass → propose the new slide, and state in the proposal that the section grows
  beyond five slides and that this is the intended outcome, so the user approves the growth
  knowingly.
- Gate 1 passes, Gate 2 fails → the finding is a card; name which signals failed.
- Gate 1 fails → a text patch, or a card on the slide that already owns the topic.

Worked examples from the September 2026 run:

| Finding | Gate 1 | Gate 2 | Outcome |
|---|---|---|---|
| routines | passes — level 1 | 5/5 | new slide 18 (slide 19 since edition 2026-10-22) — took section 04 to six slides, the intended outcome the user approved |
| network egress controls | fails — already level 2 on the guardrails slide | — | speaker-notes enrichment on that slide |
| reminder tool | passes — level 1 | fails 1, 2 and 5 (no capability-reference row, no own subtree, preview) | stays a chip |

Worked examples from the 22 October 2026 run:

| Finding | Gate 1 | Gate 2 | Outcome |
|---|---|---|---|
| browser automation tool (GA 19 Oct) | passes — level 1 (a chip on slide 11) | 3/5 — 1 (own capability row) and 3 (own GA post) and 5 hold; 2 fails (how-to page only) | new slide 12 by **user direction** (see below); section 03 had room (three slides) |
| voice agents in Agent Service (preview) | passes — level 0 | 2/5 — own capability row and a Microsoft comparison with Voice Live, but no own post and preview | text patches on slides 3 and 15; the kit's Voice Live deep-dive deck carries the detail |
| Insights in Foundry (preview) | passes — level 0 | 1/5 — own announcement only | text patches on slides 3 and 21, notes on slide 24 |

**User-directed slide.** When the user explicitly asks for a new slide whenever a topic is new
or needs an extended explanation, a finding that passes Gate 1 and the materiality test may take
a new slide even if Gate 2 fails. Record the user direction and the Gate 2 tally in the change
log. The placement rules, the one-new-slide-per-edition budget and the five-slide section limit
still apply; a request that would break them is reported instead of applied.

**Placement — where a new slide goes**

Derive the position; never guess it.
1. **Section** — the slide belongs to the section that owns its layer: platform,
   architecture and developer surfaces → 01; models, deployment and routing → 02; tools,
   toolbox and the IQs → 03; Agent Service, Agent Framework, agent runtime concepts → 04;
   observability, evaluation, guardrails, governance → 05.
2. **Position within the section** — immediately AFTER the slide it is most often confused
   with, so the deck reads as a contrast rather than a list. Autopilots goes after slide 15
   (Foundry Agent Service), because the first audience question is how it differs from a
   hosted agent.
3. **Never split a pair** — never insert between a topic slide and its detail slide,
   between a diagram and the slide that walks its numbered flow, or inside the wrap-up
   (slides 25–26).
4. **State the cost in the proposal** — which slides renumber, how slide 2's agenda ranges
   change, and that every later footer number shifts. The user confirms section and
   position before anything is applied.

**Slide budget**

The deck's value is that it stays tight; these limits hold unless the importance test above
overrides them.
- At most **one new slide per edition**, with or without an override. If two findings both
  pass the new-slide test, propose the stronger one as a slide and the other as a card, and
  say why.
- A section SHOULD hold at most **five slides**. A finding that passes the importance test
  MAY take a section to six. Two overrides in the same section across consecutive editions
  is a signal to propose a merge instead — say so in the proposal.
- Without an override, a section already at five slides takes no new slide: propose either a
  merge of two existing slides in that section, or a demotion of the finding to a card, and
  let the user choose.
- A new slide never reduces an existing slide's content to make room; content moves to
  speaker notes only with the user's approval, stated in the proposal.

Threshold met when ANY of: (a) three or more notable items; (b) any GA or retirement of
a Foundry SERVICE feature, model or deployment type; (c) any breaking change in the
Foundry API, the Foundry SDK (azure-ai-projects and equivalents) or a Foundry service
behaviour. A breaking change in an OPEN-SOURCE SDK release (Microsoft Agent Framework,
LangGraph adapters, agent-server libraries) counts as ONE notable item for slide 18 and
does NOT by itself meet the threshold.
Below the threshold, report the change log and stop unless the user asks to patch anyway.
Gaps and new capabilities (including thin-coverage findings) count as notable items for
the threshold ONLY IF they pass the materiality test above; non-material findings are
logged under 'Known, not included' and counted nowhere.

For each accepted item draft ONE proposal, of one of two kinds:

**Text patch** — changes text inside an existing shape, card, table row or speaker note.
Fields: slide · shape · current text → new text · status marker · speaker-note change ·
source.

**Structural proposal** — adds a card, a table row, or a whole slide. Fields: what is
added · where exactly (slide and position, or section and insertion point) · the drafted
content written to the deck's visual rules (card title ≤5 words, body ≤ the length of its
neighbours, asterisk if preview) · which ladder rung was chosen and why the smaller
container was rejected · for a new slide: the section, the slide it follows, and the
confusion it resolves · the drafted speaker note · slide-map impact (which
slides renumber, which agenda ranges on slide 2 change, footer numbering) · source. A
structural proposal is NEVER applied without explicit per-item approval, and a new slide
additionally requires the user to confirm the section and position.

Present all proposals as ONE review document (markdown), text patches and structural
proposals in separate groups, and ask the user to approve **per item**
(approve / edit / drop). Never patch without approval.

**Direct update request.** When the user explicitly asks to update the deck with the latest
announcements (not only to detect them), that request is the approval: run DETECT, PROPOSE and
APPLY in one pass. Apply material text patches and user-directed structural changes to a NEW
dated edition, never in place, and report the change log — including a "Detected but not
applied" list with a reason per item — for review afterwards. Anything outside the request's
scope (for example rewording slides that did not change) is offered, not applied.

### Step 3: APPLY (approved items only)

Edit the existing `.pptx` **in place** with `python-pptx` (the `pptx` capability; the
workspace office helpers `python scripts/office/unpack.py` and `python
scripts/office/pack.py` for raw XML when a shape needs surgery):

1. Change text inside existing shapes — keep the shape, its position, size, font and
   colour; replace runs, do not recreate text frames.
2. Slides **7, 10, 25**: add, edit or prune table rows / timeline dots; keep row
   height and column widths; if a table would overflow, prune the oldest row first
   and move the fact to speaker notes.
3. Slide **25**: rewrite the timeline every cycle and the "still preview" band. It keeps
   eight dots in two rows of four: drop the oldest dot, shift the others left, put the newest
   window in dot 8, and give every dot body the same height (0.9 in) so five lines fit. Update
   the band's closing line with the newest sources and their dates.
4. Slide **5**: refresh the "New in 2026" band.
5. Slide **2**: change slide ranges ONLY if slides were added or removed (rare — and
   adding a slide requires the user to say so explicitly).
6. Footer right on every content slide: `Microsoft Foundry · <Month Year> · <n>`.
7. Slide **26**: refresh the reference URLs and the "staying current" card; put the
   "verify before presenting" list in its speaker notes.
8. Speaker notes for every changed slide follow the speaker-notes rule in the Deck
   Contract: keep the presenter's hand-written notes and add or amend sentences in the same
   style; write full notes only for new slides and for notes the presenter has not rewritten.
   When slides are added or removed, also update the "→ slide n" links on slide 21 and every
   "slide n" reference in the notes.
9. **Save as the new dated edition**: `Microsoft-Foundry-Whats-New-<yyyy>-<mm>.pptx` in
   `output/`, where `<yyyy>-<mm>` is the run month. If an edition for that month already
   exists, append the run day (`-<dd>`). Never overwrite the previous edition. Save into
   the task's `output/` folder, and if the deck came from an attached folder, also upload
   the new edition and the updated `CHANGELOG.md` into that folder with
   `UploadFileContent` (drive id and parent id from `GetTaskFolders`). If the upload
   fails, keep the `output/` copy and tell the user it did not land in the attached folder.
10. **Render every changed slide** to an image (LibreOffice via
    `python scripts/office/soffice.py` or `python scripts/thumbnail.py`) and inspect
    for text overflow, wrong font size (<7.5pt), a fifth colour, or any slide-wording breach — a title that is a sentence, clause or dash-joined pair of ideas, a subtitle with jargon, an unexplained term or an unexpanded acronym, "you"/"your" anywhere in slide text, a "Learn says/lists" attribution (slides or notes), an ambiguous actor label, or a table row of a different type from its siblings (`scripts/deck_qa.py` flags most of these);
    fix and re-render.
11. Write the edition entry into the deck changelog (`kit.yaml` → `paths.deck_changelog`, else
    `CHANGELOG.md` alongside the deck; format in Output). When a kit is attached, also propose the
    `kit.yaml` update of the what's-new deck entry (file name and edition) as a diff.
12. After the new edition is saved, if `deck-companion-notebook` is installed, offer its DECK REFRESH MODE for the paired notebook (slide references and new steps; it logs to `NOTEBOOKS-CHANGELOG.md`, never to this `CHANGELOG.md`).

Do not rebuild slides; do not change layout, palette or positions. The slide map changes
only through a structural proposal the user approved per item (and, for a new slide, whose
section and position the user confirmed); apply the slide-map impact it stated — agenda
ranges on slide 2 and footer numbering included.

### Step 4: PROVENANCE (applies to every step)

- Every fact placed on a slide carries a Learn / GitHub URL fetched **in this run**;
  the URL goes in the speaker notes and the footer source, never in a diagram box.
- An item that cannot be verified against a fetched source goes to the speaker-notes
  notes as a sentence ending "should be confirmed before presenting" — never onto
  the slide.
- Slide 26's notes hold the cumulative "verify before presenting" list; prune items
  once verified.

## Output

**CHANGE LOG** (Step 1, markdown, returned in chat and saved as
`working/foundry-change-log-<yyyy-mm-dd>.md`):

```
# Foundry change log — run <yyyy-mm-dd> (baseline <yyyy-mm-dd>, edition <yyyy>-<mm>)
| Item | Status | Date | Source (fetched this run) | Target slide (or NEW) | Proposed patch |
|------|--------|------|---------------------------|-----------------------|----------------|
Threshold met: yes/no (<n> material notable, <n> logged as known-not-included, <n> GA, <n> retirement, <n> breaking)
Not checked this run: <source> — <reason>

### Gaps versus the deck (present on the source page, absent from the deck, regardless of date)
| Item | Source page | Target slide | Note |
|------|-------------|--------------|------|

### New capabilities with no place in the deck (mandatory section — never omit, write 'none' if empty)
| Capability | What it is (one line) | Status | Depth | Signals | Source (fetched this run) | Proposed placement |
|---|---|---|---|---|---|---|

### Known, not included (failed the materiality test)
| Item | Why not included |
|---|---|
```

Proposed placement is one of: `new card on slide <n>`, `new row in the table on slide <n>`,
`new slide in section <01-05>`, or `out of scope — <reason>`. Every new capability gets a
row; none may be dropped for lack of a home. **Depth** holds the level 0-4 from the depth
test in Step 1 (a GA capability at level 0 or 1 is reported as 'thin coverage'); **Signals**
holds the Gate 2 tally from the importance test in Step 2 as `4/5`, or `—` when Gate 1
already failed.

Gaps and new capabilities count as notable items for the threshold ONLY IF they pass the
materiality test in Step 2; material ones are proposed as patches like any other item,
and the rest go to "Known, not included" with a one-line reason instead.

**PATCH REVIEW** (Step 2, markdown): one section per patch — `Slide · Shape ·
Current text → New text · Status marker · Speaker note · Source`, followed by an
approval table the user fills per item.

**DECK** (Step 3): `Microsoft-Foundry-Whats-New-<yyyy>-<mm>.pptx` in the task's `output/`
folder and, when applicable, the attached folder (26 slides unless the user asked
for a structural change) plus rendered PNGs of changed slides.

**`CHANGELOG.md`** (Step 3, next to the deck): what changed since the previous edition (one line per
patch with slide number), source per change, run date, date of the last baseline sweep,
open "verify" items. Every edition entry must carry a `**Run date:**` field — Step 0 reads
the newest entry's Run date as the baseline for the next run — and a
`**Last sweep:** <yyyy-mm-dd>` field, which the next run reads to tell whether a quarterly
baseline sweep is due. Edition-entry template:

```
## Edition <yyyy>-<mm>
**Run date:** <yyyy-mm-dd>
**Last sweep:** <yyyy-mm-dd>
- Slide <n> — <what changed> — <source URL>
Open verify items: <list or none>
```

**Final chat report** (≤15 lines): edition produced, slides changed, items applied /
dropped, open verify items, and the next detect date (run date + 14 days).

## Guardrails

- **Never patch without approval** — DETECT and PROPOSE are read-only; APPLY runs only on
  items the user approved in this conversation, or under a direct update request (Step 2),
  which always produces a new dated edition.
- **Never overwrite the previous edition** — always save a new dated file; the prior
  edition is the rollback. Never expose internal iteration numbers (v1, v2 …) in file
  names, slides, notes or the changelog — the audience sees editions, not builds.
- **Never APPLY a structural change without explicit approval** — new slides, new cards,
  new table rows and any slide-map change are proposed, or applied only under a direct update
  request that asks for them, and always listed in the change log. Layout, palette, positions, fonts and the visual rules are never altered.
- **Never DROP an item because it has no home in the deck.** Every new Foundry
  capability found in a run appears in the change log's "New capabilities with no place
  in the deck" section, with a proposed placement or an explicit out-of-scope reason.
  Discarding a finding because it does not fit an existing slide is a defect.
- **Never put a fact on a slide without a source URL fetched in this run**; if a
  source is unavailable or ambiguous, say so and route the item to the presenter
  checklist in speaker notes — never fabricate a date, status or model name.
- **Never use "GA" / "Preview" badges**, `[verify]` markers or production notes on a
  slide — asterisk convention on slides, verify sentences in notes only.
- **Always render changed slides before reporting done**; if rendering fails, say the
  visual check could not be completed instead of claiming it passed.
- **Never break the slide-wording rules** — slide titles are short noun phrases (never sentences,
  clauses or dash-joined ideas), subtitles are one plain factual line, and no slide text uses
  "you"/"your"; spoken phrasing belongs in the speaker notes only.
- **Never attribute with "Learn says/lists"** on slides or in notes, never use an ambiguous actor
  label ("agent team"), and never mix row types in a slide table — see Slide wording rules 4–6.
- **Never hard-code a presenter, a personal OneDrive path or an internal package feed** in the
  deck, the changelog or a kit file.
- **Always use Microsoft product terminology** from the contract; if a source uses an
  older name (Azure AI Foundry, Azure OpenAI Service), map it to the current name and
  note the old name in speaker notes.
- If the deck or the baseline is missing, ask for the file rather than building a
  new deck — from-scratch builds belong to `azure-ai-deep-dive-deck`.
- Internal sources (Teams, SharePoint) are optional inputs only: read them, never
  post to them, and never copy internal-only content onto a customer-facing slide.
