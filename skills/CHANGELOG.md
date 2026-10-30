# Kit skills · changelog

Versions of the three Cowork skills shipped in `skills/`. The version line at the top of each
`SKILL.md` must match the newest entry here. Semantic versioning: MAJOR = a change that breaks
existing decks, notebooks or `kit.yaml`; MINOR = new rule, mode or script; PATCH = wording fixes.
A change to the shared visual system or to the Slide wording rules updates **both** deck skills
(and `scripts/deck_lib.py`) in the same release.

## 1.2.0 · 2026-10-30 — deck file names, presenter line and sensitivity labels

**azure-ai-deep-dive-deck** (`SKILL.md` + `scripts/deck_lib.py` docstring)
- Deep-dive decks are named `Microsoft Foundry <Subject>.pptx`, matching the decks already in
  `decks/`: subject in Title Case, no "deep dive", no date. The edition date moves to the
  deep-dive register and `kit.yaml` → `decks[].edition`. Replaces
  `<topic-kebab-case>-deep-dive-<yyyy>-<mm>.pptx`.
- Delivery: a deep-dive deck whose name already exists in `decks/` is not uploaded again; the
  new edition stays in `output/` and the contributor replaces the kit file in the pull request.
  The what's-new deck keeps its dated names.
- Sensitivity labels: Cowork reports the label on every uploaded file and never changes,
  removes or works around one; an unsuitable label becomes a `kit.yaml` known issue until the
  owner changes it in PowerPoint.

- Presenter line (kit setup, rule 3, shared by both deck skills): the `output/` copy carries the
  running user's name from `kit.local.yaml` → `presenter` or the Microsoft 365 profile; the copy
  in the kit's `decks/` has the presenter line removed in place after upload; "put my name
  on <deck>" personalises a kit deck into `output/`.
- `deck_lib.py`: `title_slide` always creates a shape named `Presenter`; new `set_presenter()`
  fills it (adding it to decks that have none) or removes it.

**deck-companion-notebook**
- Step 1 reads a deep-dive deck's edition from `kit.yaml` / the register instead of the file
  name; the notebook topic is the deck subject in kebab case.

**foundry-whats-new-deck**
- Presenter line on slide 1 follows the shared kit rule: personal in `output/`, removed in `decks/`.

## 1.1.0 · 2026-10-22 — what's-new deck edition 2026-10-22

**foundry-whats-new-deck** (`SKILL.md` + `scripts/deck_qa.py`)
- Deck contract now 26 slides: new slide 12 "Browser automation tool" in section 03 (11–14);
  section 04 is 15–20, section 05 21–24, wrap-up 25–26. Slide map, Step 1 source mapping,
  promotion ladder, placement examples, Step 3 slide numbers and Step 4 provenance renumbered.
- Slide 25 renamed "Changes since Build 2026"; timeline rule: eight dots, drop the oldest,
  equal body heights. Slide 21 "→ slide n" links must be updated when slides move.
- Speaker-notes rule replaced by the presenter's style (about 230–500 words; opening line, "The
  core idea is that …", bold ordinal steps, questions folded into prose, verify items as
  sentences, closing takeaway). Hand-written notes are amended, not replaced. The
  `Presenter note:` / `Likely question:` labels are retired.
- New "Direct update request" mode (detect, propose and apply in one pass into a new dated
  edition) and "User-directed slide" rule (a new slide on the user's explicit direction when
  Gate 2 fails); worked examples from the 22 October run (browser automation, voice agents,
  Insights).
- DETECT also reads single-feature posts on the Foundry blog and handles a lagging Learn
  what's-new page.
- `deck_qa.py`: notes target 200–550 words; warns on "Likely question:" / "Presenter note:".

**azure-ai-deep-dive-deck, deck-companion-notebook**
- Version line only (shared kit version); no content change.

## 1.0.1 · 2026-10-11 — kit consistency corrections

**All three skills**
- Use the name **Microsoft Foundry What's New and Deep-Dive Kit** consistently.

**deck-companion-notebook**
- Correct hosted-agent runtime references to Python 3.13, separate from the Python 3.12 notebook kernel.
- Mark the resource-group collision resolved: notebook 8 uses `APIM_RESOURCE_GROUP`, while notebooks 1 and 8 share `AZURE_SUBSCRIPTION_ID` in one subscription.

## 1.0.0 · 2026-10-11 — first shared release

**All three skills**
- New "Kit and repository setup": the kit is the attached folder holding `kit.yaml`; every path
  is read from it; presenter from the running user's Microsoft 365 profile (or a git-ignored
  `kit.local.yaml`); deliver to `output/`, upload into the kit only on request; Cowork never pushes
  to GitHub — branch and pull request.
- Version line at the top of every `SKILL.md`.
- Hand-offs between the skills are conditional on the target skill being installed.
- References to the personal `azure-ai-architecture-decks` skill removed; from-scratch builds go
  to `azure-ai-deep-dive-deck`.
- No personal names, OneDrive paths or internal package feeds.

**azure-ai-deep-dive-deck** (`SKILL.md` + `scripts/deck_lib.py`, `scripts/deck_qa.py`)
- Slide wording rules 4–6 added (from presenter review): no "Learn says / Learn lists" on slides
  or in notes — "as per official documentation" or no attribution; named actors ("development
  team"), never "agent team"; every row of a slide table answers the table's own question.
- Rules 1–3 kept: noun-phrase titles, plain subtitles, no "you/your" on slides.
- Build step uses the bundled `deck_lib.py` (canonical visual system on python-pptx);
  QA step runs `deck_qa.py` before inspecting every rendered slide.
- Hand-off registers the deck in `decks/DEEP-DIVE-DECKS.md` and `kit.yaml` (diff, on approval).

**foundry-whats-new-deck** (`SKILL.md` + `scripts/deck_qa.py`)
- Slide wording rules 4–6 mirrored; QA checklist extended.
- Changelog path from `kit.yaml` (`decks/CHANGELOG.md`); current edition read from it instead of a
  hard-coded file name; slide 9 in the slide map is now "Priority and Flex processing".
- Multi-maintainer rule: re-read the changelog before APPLY and re-base on a newer edition.

**deck-companion-notebook** (`SKILL.md` + `scripts/kit_check.py`)
- Section 1 reads `kit.yaml` instead of a dated kit snapshot and a fixed OneDrive path.
- Private package index moved out of shared files (`kit.local.yaml` or the contributor's
  `PIP_INDEX_URL`); the shared devcontainer uses PyPI.
- Markdown wording rules aligned with deck rules 4–6 (the old guardrail line read as if
  "development team" were banned).
- Deck changelog path is `decks/CHANGELOG.md`; new `kit.yaml` diff (notebook entry, env entries,
  next notebook number) on every BUILD; pull-request flow with `kit-gate.md`.

## Pre-release history (single user, not shipped)
- 2026-10-10 · `deck-companion-notebook` created; kit_check.py false positives fixed; "No tested
  version yet" pin rule.
- early October 2026 · slide-wording rules 1–3 added to both deck skills.
- 2026-09 · `azure-ai-deep-dive-deck` and `foundry-whats-new-deck` created.
