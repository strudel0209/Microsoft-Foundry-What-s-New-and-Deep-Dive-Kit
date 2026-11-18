---
name: interactive-deck-story
description: |
  Turns an existing slide deck (.pptx) with decision content (decision trees, compared
  options, flows), such as a Microsoft Foundry kit deep-dive deck, into one offline
  interactive HTML story page: a main animated decision tree that unfolds into the deck's own
  decision trees and diagrams, with sources, presenter notes and deep links; no hosting.
  Use only when a source deck is named or attached AND the result is an interactive HTML
  story built from it: "make an interactive story from this deck", "turn the <topic> deck
  into an interactive HTML page", "refresh the interactive story for the new deck edition",
  "add the interactive story to the kit".
  Do NOT use without a source deck, to create or edit a deck or animate slides inside
  PowerPoint (azure-ai-deep-dive-deck, foundry-whats-new-deck, azure-ai-architecture-decks,
  pptx), for notebooks (deck-companion-notebook), for HTML pages, reports or apps not built
  from a deck (create, html), for hosted web apps, or for video and images (image-operations).
metadata:
  category: custom
  domain: "presentations / Azure AI"
  icon: Play
---

# Interactive Deck Story

> Version 1.4.0 · 2026-11-18 · part of the Microsoft Foundry What's New and Deep-Dive Kit — history in
> `skills/CHANGELOG.md` of the kit repository.

## Overview

Builds the **interactive companion of a kit deck**: one offline HTML file, no hosting, no
external assets, that tells the deck as a story. The page opens on the problem, lands on a
**main decision tree** (the hub), and every leaf of that tree **dives** into the deck's own
decision trees and diagrams, in deck order, each scene showing its deck slide number.

The page is assembled from a **fixed engine** (`assets/engine.css`, `assets/engine.js`,
`assets/shell.html`) and **one content file per deck** (`story.json`). The engine is never
edited per deck; the work of this skill is writing `story.json` from the deck, checking it and
building it. The format is in `references/story-format.md`; the full worked example is
`examples/latency-optimization/` (the approved first page: "Microsoft Foundry Latency
Optimization for Models and Agents", 18 scenes, built 2026-11-15).

| Mode | Trigger | Produces |
|------|---------|----------|
| **BUILD** (default) | "make the interactive story for this deck" | `<deck base name> - Interactive.html` in `output/` + `story.json` + check reports |
| **REFRESH** | "the deck has a new edition — update the interactive page" | updated `story.json` and page; slide map old → new |
| **KIT** | "add the interactive story to the kit" (only when asked) | the page and its `story.json` in the kit's `interactive-stories/` folder + `kit.yaml` and `README.md` patches |

## Quick Start

```
User: "Build the interactive story for the Model Router deck."

0. LOCATE   → the deck (attached, linked, or kit decks/ folder); read it fresh; kit.yaml if a kit is attached
1. EXTRACT  → python scripts/extract_deck.py deck.pptx working/story/deck.json --md working/story/deck.md
2. PLAN     → story map: scene · type · deck slide(s) · main-tree lens · what moves; show it if the user is present
3. WRITE    → working/story/story.json from examples/template/story.json (topic renderer only if no core type fits)
4. CHECK    → python scripts/story_check.py story.json --deck deck.json   (0 FAIL; read every WARN)
5. BUILD    → python scripts/build_story.py story.json "working/story/<deck base> - Interactive.html"
6. VALIDATE → html skill validator (0 errors) + node scripts/render_check.js <page> (pass) + view every screenshot
7. DELIVER  → CopyArtifact to output/ (ok: true); chat report; KIT mode only when asked
```

## When to Use

Both conditions hold: **a source deck exists** (named, linked, attached or in the kit's
`decks/` folder) **and the requested result is an interactive HTML story built from it**.
- "Make an interactive story from the <topic> deck", "turn this deck into an interactive HTML page"
- "An animated explainer like a motion-graphics video, but offline and built from the deck"
- "Refresh the interactive story, the deck has a new edition" (REFRESH mode)
- "Add the interactive story to the kit" (KIT mode)

## When NOT to Use

| Request | Use instead |
|---------|-------------|
| No source deck: an interactive page, explainer or decision tree written from scratch | `create` (page or app) or `html` |
| Build, edit or refresh the deck itself; animations or clickable links inside PowerPoint | `azure-ai-deep-dive-deck`, `foundry-whats-new-deck`, `azure-ai-architecture-decks`, `pptx` |
| A notebook derived from a deck | `deck-companion-notebook` |
| A hosted web app, live data, a sign-in or a backend | `create` (app) |
| An HTML report, landing page or static export of a deck | `create` or `html` |
| Video, GIF or image output | `image-operations` |
| A deck without decision content (a pitch deck, a photo deck) | none: say the story format does not fit and offer a static HTML export (`html`) |

---

## Section 1: The story structure (fixed)

| Order | Scene | Scene type | From the deck |
|-------|-------|------------|---------------|
| 1 | Title and chapter list | `title` | title and agenda slides |
| 2 | The problem: where the time, cost or risk goes | `turn` | the "sources of …" / problem slide |
| 3 | **Main decision tree** (the hub, amber in the progress bar) | `map` | editorial synthesis of the whole deck |
| 4 … n-2 | Deep dives, in deck order | `path`, `table`, `tree`, `spectrum`, `trace`, `compare`, `phases`, topic types | one scene per content slide |
| n-1 | Status and recent changes | `status` | status slide |
| n | References | `refs` | references slide |

**The main decision tree** is the only editorial element of the page:
- **3 to 5 questions**, each one **lens** of the topic (latency example: Avoid · Hide · Reduce ·
  Steady), asked in a defensible order — cheapest or most structural change first — with that
  order explained in `order`.
- Optional framing bands: `measure` (what to measure before changing anything) and `govern`
  (how to keep the gains) — use them when the deck has observability and governance slides.
- **Every leaf is an option named on a deck slide** and links (`go`) to the scene that explains
  it, with `focus` set to the row, panel or column to highlight there.
- `meta.editorial` states on the page that the grouping is an editorial aid and every option
  comes from the deck. Never present the grouping as Microsoft guidance.

**Mapping slides to scene types:**

| Slide content | Scene type |
|---------------|-----------|
| Request path, architecture flow of 3–6 components | `path` (isometric blocks, flowing particles; side `loop` for tool or agent calls) |
| Decision tree (question → Yes → recommendation, No → next) | `tree` (walk mode W) |
| Capacity, tier or option table | `table` (illustrative jitter sparklines where the slide contrasts variability) |
| Patterns from simple to complex | `spectrum` (animated mini diagrams) |
| Trace, waterfall, observability timeline | `trace` |
| Features × questions comparison | `compare` (column spotlight) |
| Adoption or optimization path | `phases` |
| Status and recent changes | `status` (preview filter) |
| References | `refs` |
| A topic-specific diagram no core type can show | a **topic renderer** (Section 4) — e.g. latency's `anatomy` (model-call timeline with streaming toggle and token slider) and `features` (four animated feature panels) |

One scene per deck slide is the default. Two slides may share a scene (`"slide": [7, 9]`) only
when the scene shows both; the agenda slide is covered by the title scene (`"slide": [1, 2]`).

## Section 2: Content rules (hard constraints — the user established these)

1. **The deck is the only source of facts.** Every option, feature, status, date and URL on the
   page comes from the paired deck edition (slides, speaker notes, footers). No new facts, no
   web research to "improve" the page; if the deck is wrong, say so in chat and offer to fix the
   deck through its skill. `meta.checked` is the deck's fact-check date, not today.
2. **Conceptual, not number-oriented.** No measured results, benchmark numbers or notebook
   outputs. Visual proportions (bar segments, sparklines, trace spans) are **labelled
   illustrative** on the scene ("ILLUSTRATIVE PROPORTIONS", "Illustrative trace").
3. **Never present an inferred mapping as documented.** The main-tree grouping is labelled
   editorial; anything else inferred is flagged in the text or left out.
4. **Preview items end with `*`** exactly as on the deck, and their scene has `"preview": true`
   so the footnote `* preview — no service level agreement.` shows.
5. **Speaker notes** are the deck's notes with every "Presenter note: verify …" sentence removed
   (`extract_deck.py` does this); those sentences are reported in chat, never shown.
6. **Wording** (same rules as the deck skills):
   - titles are short noun phrases (no sentences or clauses), taken from the deck slide titles;
   - plain, native English in the style of Microsoft Learn; no machine-like labels;
   - never "you/your" on the page — third person ("development team", "operators");
   - never "Learn says/lists" — "as per official documentation" or drop the attribution;
   - name actors precisely ("development team", never "agent team");
   - no pitch words (unlock, empower, seamless, game-changing, supercharge);
   - every row of a table answers the table's own question — descriptions go in captions;
   - expand acronyms on first use per scene where space allows (title, drawer detail).
7. **No customer names, data or internal material.** Sources are Microsoft Learn (`/en-us/`) and
   public GitHub only — the same links as the deck.
8. **Accessibility is part of done:** every interactive box has a label (the engine adds
   `role="button"`, keyboard Enter/Space); reduced motion is honoured; text contrast follows the
   engine palette — do not add colours outside `references/story-format.md`.

## Section 3: Workflow (BUILD)

### Step 0 — Locate the deck and read it fresh
- The deck the user linked or attached; otherwise the kit's `decks/` folder (kit: the attached
  folder holding `kit.yaml` — `GetTaskFolders`, else `SearchDrive` for `kit.yaml`). Read
  `kit.yaml` → `decks[]` for the file name, `edition` and `slides`. If `kit.yaml` →
  `interactive_stories` already lists a story for this deck, switch to REFRESH mode.
- Download a fresh copy into `working/story/`. A copy from an earlier session is never the
  source. **An encrypted sensitivity label** can block the download: use the live copy the
  user linked, or ask the owner to open it; never work around the protection.

### Step 1 — Extract
```bash
python scripts/extract_deck.py "<deck>.pptx" working/story/deck.json --md working/story/deck.md
```
Read `deck.md` end to end: titles, every text line, preview items, speaker notes, verify items.

### Step 2 — Plan the story
Write the **story map** and, if the user is present, show it before writing content:
```
| # | Scene id | Type | Deck slide(s) | Lens tags | What moves / what is interactive |
```
plus the **main tree**: the 3–5 lens questions in order, and per question the leaves with
their target scene. Every leaf target must exist; every content slide must be covered.

### Step 3 — Write `story.json`
Copy `examples/template/story.json` to `working/story/story.json` and fill it, scene by scene,
from `deck.json` (format: `references/story-format.md`; model answer:
`examples/latency-optimization/story.json`). Put every link in `sources` once and cite keys.
Keep within the layout limits — shorten wording rather than shrinking boxes. A topic renderer
is written only when no core type can show a slide (Section 4).

### Step 4 — Check the content
```bash
python scripts/story_check.py working/story/story.json --deck working/story/deck.json [--extra-js renderers.js]
```
Fix every FAIL. Read every WARN: shorten text that is over its design length, remove
measured-result wording, cover uncovered slides or say why not.

### Step 5 — Build
```bash
python scripts/build_story.py working/story/story.json "working/story/<deck base name> - Interactive.html" [--extra-js renderers.js]
```
`<deck base name>` is the deck file name without `.pptx` (spaces kept).

### Step 6 — Validate and look at every scene
```bash
python /opt/workspace-config/.github/skills/html/scripts/validate.py "<page>"      # 0 errors, 0 warnings
node scripts/render_check.js "<page>" --out working/story/render-check              # status pass
```
`render_check.js` opens every scene at its last beat in headless Chromium, screenshots it,
measures text overflow and out-of-stage boxes, and tests the drawer, notes, chapters, main-tree
dive, walk mode on every tree and deep links; it fails on any console error or external request.
Then **view every screenshot** (a montage of four per image is fine) and fix what the
measurements cannot see: overlapping labels, unreadable contrast, empty areas, a wire crossing
text. Iterate Steps 4–6 until both checks pass and the screenshots are clean (at most three
rounds; then report what is left).

If the render check reports `unavailable` (no Chromium), say so, keep the validator result and
ask the user to open the page and step through it once.

### Step 7 — Deliver
- Publish with `host-CopyArtifact(surface="output", source="working/story/<page>", destination="<page>")`
  (`overwrite=true` on a rebuild) and confirm `ok: true`. Also publish `story.json` (and
  `renderers.js` if any) to `output/<deck base name> - Interactive/` so the page can be rebuilt.
- Chat report (≤ 15 lines): file name; scene count and story order; the main-tree lenses;
  topic renderers added; check results (story check, validator, render check); presenter-verify
  items from the notes; browsers checked (headless Chromium only, unless the user tested more);
  how to open it (download or open from the synced folder — OneDrive serves HTML as a download,
  not as a web page); keys: → / ← steps, M main tree, C chapters, N notes, W walk a tree,
  P autoplay, F full screen.

## Section 4: Topic renderers

Write one only when a slide's diagram is specific to the topic and no core type can show it.
Put it in `working/story/renderers.js` and pass it with `--extra-js` to both `story_check.py`
and `build_story.py`. The contract and a minimal example are in `references/story-format.md`
→ "Topic renderers"; `examples/latency-optimization/renderers.js` shows two full ones.
Rules: core helpers only (`el`, `add`, `box`, `wire`, `curve`, `flow`, `spawn`, `clickable`,
`openDrawer`, `later`, `every`, `chip`, `COLORS`, `RM`); beats through `data-b`; text through
`textContent`, never content in `innerHTML`; reduced motion respected; stays inside the
1600 × 900 stage. **Never edit `assets/engine.*` for one deck** — a change every page needs is
an engine change: bump the engine version in `build_story.py` and `engine.js`, rebuild the
latency example, re-run its render check, and log it in `skills/CHANGELOG.md`.

## Section 5: REFRESH mode (new deck edition)

1. Start from the story's `story.json` in the kit (`interactive-stories/src/<topic-kebab>/`) or
   the one the user attaches, never from an earlier session's copy. Steps 0–1 on the new
   edition; compare its slide titles and numbers with `story.json`
   (`slide` fields) and write the slide map old → new.
2. Update `slide` numbers, changed content, status rows, preview stars, notes and sources;
   add scenes for new slides; remove scenes for removed slides (and their main-tree leaves).
3. Update `meta.edition` and `meta.checked` to the new edition's values.
4. Steps 4–7 unchanged. Report the slide map and every content change in chat.

## Section 6: KIT mode (only when the user asks)

The kit repository is the source of truth; re-read before every write. Stories live in the
folder named by `kit.yaml` → `paths.interactive_stories` (`interactive-stories/`; on first use
add that path entry and create the folder). This skill owns that folder, the
`interactive_stories:` list in `kit.yaml` and the *Interactive Stories* subsection of the
README, and writes nothing else in the kit.

1. **Files** (one story = one page + its sources):
   - `interactive-stories/<deck base name> - Interactive.html`: same base name as the deck in
     `decks/`;
   - `interactive-stories/src/<topic-kebab>/story.json`, plus `renderers.js` when the story has
     topic renderers. `<topic-kebab>` is the deck subject in kebab case, as for notebooks (e.g.
     `latency-optimization-for-models-and-agents`), so any contributor can rebuild the page.

   A refresh replaces both (git history is the rollback). Check reports go into the
   pull-request description, not into the repository. The skill's
   `examples/latency-optimization/` is a frozen model answer; the kit's `src/` copy is the one
   to refresh.
2. **`kit.yaml`** (re-check its eTag; patch, never rewrite): one entry per story in the
   top-level `interactive_stories:` list, placed after `decks:` (create the list if absent).
   Never write inside `decks[]`: deck entries belong to the deck skills. Show the diff in chat.
   ```yaml
   interactive_stories:
     - file: "<deck base name> - Interactive.html"
       source: src/<topic-kebab>/            # story.json, plus renderers.js when used
       deck: "<deck base name>.pptx"
       deck_edition: <yyyy-mm>
       scenes: <n>
       engine: <ENGINE_VERSION of build_story.py>
       built: <yyyy-mm-dd>
       checks: <story check, HTML validator and render check results; browsers not tested>
   ```
   Paths inside an entry are relative to `paths.interactive_stories`.
3. **`README.md`** (patch): an `### Interactive Stories` subsection at the end of the *Slide
   Decks* section, so the top-level section order stays as it is: one table row per story
   (`Story | Built from deck | Scenes`) and one paragraph on opening it (download it or open
   it from a synced clone in Edge or Chrome; no hosting or network needed). On first use, also
   add `interactive-stories/` to *Repository Guide*.
4. **Never write** `decks/CHANGELOG.md` (owned by `foundry-whats-new-deck`),
   `decks/DEEP-DIVE-DECKS.md` (owned by `azure-ai-deep-dive-deck`), `NOTEBOOKS-CHANGELOG.md`
   (owned by `deck-companion-notebook`) or a `decks[]` entry in `kit.yaml`.
5. Upload with `UploadFileContent` after a fresh eTag check; if a file changed since it was read,
   re-merge and show the new diff. **Cowork never pushes**: the contributor commits on a branch
   (`story/<topic-kebab>`) and opens a pull request with the check results (story check,
   validator, render check) in the description.

---

## Output

**Story map** (Step 2):
```
| # | Scene id | Type | Deck slide(s) | Lens tags | What moves / what is interactive |
```

**Files** (`output/`): `<deck base name> - Interactive.html` and
`<deck base name> - Interactive/` holding `story.json`, `renderers.js` (if any),
`story-check.txt` and `render-report.json`.

**Final chat report** (≤ 15 lines): see Step 7.

## Guardrails

- **Facts only from the paired deck edition**; never invent options, statuses, dates or URLs.
- **The main-tree grouping is labelled editorial** on the page; never presented as Microsoft guidance.
- **No measured results or benchmark numbers**; illustrative visuals are labelled illustrative.
- **No presenter-verify sentences, customer names or internal material** on the page.
- **One self-contained file**: no external scripts, fonts, images, trackers or network calls;
  no inline `on…` attributes; `lang` set; works from `file://`.
- **The engine is shared**: never edit it for one deck; topic renderers go in `--extra-js`.
- **Never claim a browser test you did not run**: headless Chromium is what the render check
  covers; Safari, Firefox and physical screens are "not tested" unless the user tested them.
- **Kit writes only on request**, after an eTag re-check, as patches; never into files owned by
  other skills; never push.
- **Never work around a sensitivity label or encryption** on a deck.

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `render_check` reports overflow on tree rows | question or recommendation too long | shorten to the design length in `references/story-format.md`; keep the full sentence in `detail` |
| Main-tree question boxes clip | two-line question plus long hint, or 5 questions | ≤ 55 characters per question, ≤ 60 per hint; with 5 questions keep each question on one line |
| A leaf opens the wrong place | `focus` index or `go` id wrong | `story_check.py` catches unknown ids; check `focus` against the target's row order |
| Page opens as a download from OneDrive | OneDrive serves HTML as a file, not a page | open it from the synced folder or download it, then open it in Edge or Chrome |
| Text small on a 1366-pixel laptop | the 1600 × 900 stage is scaled to fit | full screen (F) hides the bars and gives the stage the whole screen |
| Full screen (F) does nothing in one browser but works in another | the page is open inside a preview pane or embedded frame, or a browser policy blocks full screen | engine 1.0.1 and later hide the toolbars instead and show a notice; open the downloaded file directly, or press F11 for browser full screen; rebuild pages made with engine 1.0.0 |
| `render_check` status `unavailable` | no Chromium or playwright-core in the environment | set `CHROME_PATH` / `PLAYWRIGHT_CORE`, or report the validator result and ask for a manual walk-through |
| Deck download blocked | encrypted sensitivity label | use the live copy the user linked or ask the owner; never bypass |
