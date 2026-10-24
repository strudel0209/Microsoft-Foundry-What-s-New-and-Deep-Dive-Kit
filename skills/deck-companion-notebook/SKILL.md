---
name: deck-companion-notebook
description: |
  Derives a companion Python Jupyter notebook from an Azure AI deep-dive or Foundry
  what's-new deck (one step per slide concept, code from Microsoft Learn and Microsoft
  GitHub samples) and adds it to the Foundry demo kit, enriching shared requirements.txt
  and .env.example after a dependency and breaking-change check.
  Use when asked to "build the companion notebook for this deck", "derive a notebook
  from the deck", "add a demo notebook for <topic> to the kit", "update the notebook for the
  new deck edition", "check the kit's dependencies", or "refresh requirements for the demo kit".
  Do NOT use for topic decks (use azure-ai-deep-dive-deck), the what's-new deck (use
  foundry-whats-new-deck), other slides (use pptx), app templates, non-Python notebooks.
metadata:
  category: custom
  domain: "development / Azure AI"
  icon: Notebook
---

# Deck Companion Notebook

> Version 1.1.0 · 2026-10-22 · part of the Microsoft Foundry What's New and Deep-Dive Kit — history in
> `skills/CHANGELOG.md` of the kit repository.

## Overview

Turns a technical deck into a **runnable Python Jupyter notebook** that demonstrates the
concepts on its slides — **one numbered step per demonstrable concept, slide numbers matching
the paired deck edition** — and adds it to the **existing** demo kit (the repository folder holding `kit.yaml`). The kit grows
cumulatively: the shared `requirements.txt`, `.env.example` and `README.md` are **enriched by
patch, never replaced or duplicated**, and every SDK or library change is checked for dependency
conflicts and breaking changes **against all notebooks already in the kit** before anything is
written, so a new demo never breaks one that already works.

Three modes, one skill:

| Mode | Trigger | Produces |
|------|---------|----------|
| **BUILD** (default) | "build the companion notebook for this deck", "add a demo notebook for <topic> to the kit" | new `foundry-demo-<n>-<topic>.ipynb` + patched shared files + `NOTEBOOKS-CHANGELOG.md` entry |
| **DECK REFRESH** | "update the notebook for the new deck edition" (offered by `foundry-whats-new-deck` after APPLY) | updated slide references + new steps in the paired notebook, as an approval-gated proposal |
| **DEPENDENCY AUDIT** | "check the kit's dependencies", "refresh requirements for the demo kit" | no notebook; audit table, proposed safe bumps and caps, **Last dependency audit** date |

Contributors refine notebooks in VS Code after generation, so **the attached kit folder (a
OneDrive-synced clone of the kit repository) is the source of truth** — never a copy from an
earlier session, never this skill's own previous output. Several people contribute to the same
kit: re-read before every write, never renumber or rename another contributor's notebook, and
claim the next free notebook number from `kit.yaml` (`next_notebook_number`) in the same change
that adds the notebook.

## Quick Start

```
User: "Build the companion notebook for the Model Router deep-dive deck."

0. LOCATE    → kit folder holding kit.yaml (GetTaskFolders, else SearchDrive "kit.yaml");
               read kit.yaml; download README.md, requirements.txt, .env.example, devcontainer.json,
               agent/azure.yaml, agent/src/*/requirements.txt, every *.ipynb — fresh.
1. READ DECK → slide titles + numbers, asterisks (preview), notes, "Presenter note: verify", URLs.
2. MAP       → step map: step · concept · slide(s) · GA/preview · demo or explain-only; one
               business scenario through all steps. Show it if the user is present.
3. SOURCE    → Learn how-to (/en-us/) → SDK samples + CHANGELOG → foundry-samples / Azure-Samples
               → PyPI. URL + package version per API; unconfirmed → `# verify`.
4. DEPS      → impact analysis vs ALL notebooks (scripts/kit_check.py API inventory +
               CHANGELOG breaking changes), resolver dry run if the index is reachable
               → DEPENDENCY CHANGE LOG. Breaking an existing notebook = stop and ask.
5. ENV       → reuse a variable only with identical meaning, else a prefixed new name
               → ENV CHANGE LOG.
6. BUILD     → foundry-demo-9-model-router.ipynb (next free number, nbformat 4, empty outputs).
7. ENRICH    → patch requirements.txt / .env.example / README.md; diff each.
8. GATE      → kit_check.py across ALL notebooks; honest pass/fail per notebook.
9. LOG       → NOTEBOOKS-CHANGELOG.md entry (never the deck changelog) + kit.yaml diff.
10. DELIVER  → output/ + diffs in chat; upload into the kit only when asked, after an eTag re-check.
```

## When to Use

- "Build the companion notebook for this deck" / "derive a notebook from the deck"
- "Add a demo notebook for Foundry IQ to the kit"
- "Update the notebook for the new deck edition" — DECK REFRESH mode
- "Check the kit's dependencies" / "refresh requirements for the demo kit" — DEPENDENCY AUDIT
- The handoff offer at the end of `azure-ai-deep-dive-deck` or the APPLY step of
  `foundry-whats-new-deck`

## When NOT to Use

- **Building or patching a deck → `azure-ai-deep-dive-deck` (new topic deck) or
  `foundry-whats-new-deck` (the recurring what's-new deck).** This skill reads decks; it never
  edits one.
- **Any other slide work → `pptx`.**
- **Production application templates, accelerators or reference implementations** — a kit
  notebook is a presenter demo, not deployable code. Point to the Azure-Samples template instead.
- **Non-Python notebooks** (C#/.NET Interactive, TypeScript, R) — out of scope.
- **Generic data-science or machine-learning notebooks** unrelated to a deck — answer directly.
- **Standalone `.http` REST Client files** are only produced as a companion to a notebook step
  (as notebook 5 has); a REST-only demo is out of scope.

---

## Section 1: The kit (`kit.yaml` is authoritative)

**Location:** the folder that contains `kit.yaml` — a clone of the kit repository, synced to the
contributor's OneDrive and attached to the task. Find it with `GetTaskFolders`; if several
attached folders qualify, ask which one. Never assume a fixed OneDrive path.

**Read `kit.yaml` first, on every run.** It lists the notebooks (number, file, paired deck and
slides, environment variables), the decks, the shared environment variables with their meaning,
the next free notebook number, the paths of the changelogs and the known issues. The tables below
describe the kit **at skill version 1.0.1** and are orientation only — when they disagree with
`kit.yaml` or the files, the files win; propose a `kit.yaml` fix as a diff.

**Kit-specific notes** (personal environment details) live in an optional git-ignored
`kit.local.yaml` next to `kit.yaml` — for example a private package index. Read it if present;
never copy its content into a shared file.

| Path | What it is | Who owns it |
|------|-----------|-------------|
| `.devcontainer/devcontainer.json` | image `mcr.microsoft.com/devcontainers/python:3.12`; Azure CLI + azd features; `postCreateCommand` = `pip install -r requirements.txt` + azd extensions `azure.ai.agents`, `microsoft.foundry`; `PIP_INDEX_URL` **unset** in the public kit (PyPI) — a private index belongs in the
contributor's `kit.local.yaml` or local environment, never in the shared file; remoteEnv `AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true`, `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=false`; forwarded ports 8088 (hosted agent), 18888 (Aspire dashboard), 4317 (OpenTelemetry Protocol, OTLP) | this skill — patch only when a new CLI tool, extension or port is required |
| `agent/` | Azure Developer CLI (azd) project with two hosted agents; `agent/src/<agent>/requirements.txt` pulled into the root file with `-r`; `agent/azure.yaml` sets the hosted runtime (Python 3.13) | user — read-only for this skill |
| `private-agent/`, `docs/` | supporting material | user — read-only |
| `README.md` | single kit README (sections below) | this skill — patch only |
| `decks/CHANGELOG.md` (`paths.deck_changelog`) | **deck changelog owned by `foundry-whats-new-deck`**, parsed by that skill | **never write to it** |
| `decks/DEEP-DIVE-DECKS.md` (`paths.deep_dive_register`) | deep-dive deck register owned by `azure-ai-deep-dive-deck` | read-only |
| `kit.yaml` | kit manifest | this skill — patch its `notebooks`, `env` and `next_notebook_number` entries only, as a diff on approval |
| `NOTEBOOKS-CHANGELOG.md` | notebook changelog (create if absent) | this skill |
| `.env.example`, `requirements.txt`, `.gitignore` | shared kit files | this skill — patch only |
| `decks/` | paired decks, referenced from the README and `kit.yaml` | read-only |

**Existing notebooks at version 1.0.0** — names are kept exactly as they are, including the typos;
never rename or renumber:

| # | File | Note |
|---|------|------|
| 1 | `foundry-demo-1-what-is-new.ipynb` | pairs with the what's-new deck |
| 2 | `foundry-demo-2-hosted-agents.ipynb` | |
| 3 | `foundry-demo-3-hosted-agent-private-nework.ipynb` | (sic) |
| 4 | `foundry-demo-4-promp-caching.ipynb` | (sic) |
| 5 | `foundry-demo-5-a2a.ipynb` + companion `.http` REST Client file | installs its own `%pip` pin — known defect |
| 6 | `foundry-demo-6-content-understanding.ipynb` | |
| 7 | `foundry-demo-7-voice-live.ipynb` | |
| 8 | `foundry-demo-8-ai-gateway-governance.ipynb` | rewritten from raw ARM REST to `azure-mgmt-apimanagement` |

**README sections (order fixed):** Choose a Notebook (table `Notebook | Focus | What you
demonstrate`) · Slide Decks (table `Deck | Pairs with`) · one section per notebook ·
Prerequisites · Local Setup (env table `Variable | Used for`) · Recommended Demo Flow · Costs,
Validation, and Cleanup · Repository Guide.

**Python versions:** notebook kernel **3.12** (devcontainer); hosted-agent runtime **3.13**
(`agent/azure.yaml`); azure-ai-projects 2.x needs **≥3.10**. Keep kernel and hosted-runtime
requirements separate — never raise the kernel to satisfy an agent dependency or vice versa.

---

## Section 2: Notebook conventions (hard constraints — the user established these)

### 2.1 Title cell (first markdown cell)
`# <Topic> — companion notebook` (or `· demo notebook`), then:
- the companion deck: file name + edition date;
- **Before you start (Azure side)** — prerequisites list (resources, roles, model deployments,
  regions where a feature is region-limited);
- a step table `| Step | What it shows | Status | Deck slide |` with Status `GA` or `preview`;
- the verify convention, verbatim: *"Lines marked `# verify` use a shape that was documented at
  the time of writing but not executed here — check them against the Learn page linked in the
  cell before you present."*

### 2.2 Step headings
`## <n> · <Short title>  *(slide x, y)*` — slide numbers **MUST** match the paired deck edition.
Preview steps carry "(preview)" in the heading, e.g. `## 4 · Routing subset (preview)  *(slide 9)*`.
Each step: one markdown cell (what it shows, why, source URL) + the minimum code cells.

### 2.3 Step 0 · Setup (template — adapt names, keep the shape)
```python
%pip install -q -r requirements.txt   # kit-level install only; never per-package %pip lines
```
```python
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv(override=True)
env = lambda k, d="": os.getenv(k, d).strip()

FOUNDRY_PROJECT_ENDPOINT = env("FOUNDRY_PROJECT_ENDPOINT", "<your-project-endpoint>")
FOUNDRY_MODEL_NAME       = env("FOUNDRY_MODEL_NAME", "<your-model-deployment>")
# notebook-specific settings use prefixed names — see Section 4, defect 1

required = {"FOUNDRY_PROJECT_ENDPOINT": FOUNDRY_PROJECT_ENDPOINT, "FOUNDRY_MODEL_NAME": FOUNDRY_MODEL_NAME}
missing = [k for k, v in required.items() if not v or v.startswith("<")]
print("required settings missing:", ", ".join(missing) if missing else "none")

credential = DefaultAzureCredential()            # Entra ID by default — no keys
project = AIProjectClient(endpoint=FOUNDRY_PROJECT_ENDPOINT, credential=credential)
openai_client = project.get_openai_client()      # where Foundry is involved
```
Reuse the existing notebooks' `LIVE` flag definition (read it in Step 0); if none exists, define
`LIVE = False` in Step 0 with a comment that chargeable steps run only when it is `True`.

### 2.4 Code rules
- **Official SDK clients over raw REST.** The user rewrote notebook 8 from raw ARM REST to
  `azure-mgmt-apimanagement` (`ApiManagementClient`, `PolicyContract`, …). REST is allowed only
  for calls the SDK cannot model, behind an env-var api-version (pattern: `APIM_ARM_API_VERSION`),
  with a comment saying why.
- **Optional steps are gated:** `if LIVE:` or a printed `"<SETTING> not set — step <n> skipped"`.
- **Destructive or chargeable cells are flagged** in their markdown cell and with a first-line
  comment (`# CHARGEABLE: …` / `# DESTRUCTIVE: …`).
- **Back up before changing shared Azure resources** — e.g. save the original API Management
  policy to a file and restore it in cleanup.
- **Final cleanup step** states explicitly what it does **NOT** delete, above all billable
  resources (Azure Cache for Redis, API Management, provisioned deployments).
- **No stored outputs** (empty `outputs`, `execution_count: null`); never fabricate an output,
  not even as a markdown "expected output".
- `# verify <URL>` on every line whose shape was not confirmed in a fetched source.

### 2.5 Closing markdown cells
1. **What you built** — table `| Step | Built / shown | Azure resource touched |`.
2. **Sources and tested versions** — each package version the code was written against, plus
   every source URL used.
3. **Before you build on this: re-check …** — the preview surfaces, `# verify` lines and
   versions most likely to drift.

### 2.6 Wording in markdown cells (user rules)
Same rules as the deck skills' Slide wording rules 4–6, applied to markdown cells:
- Never "Learn says" / "Learn lists" — write "as per official documentation" or drop the phrase
  when the fact stands on its own; the URL goes in the step's source line.
- Name the actor: "development team", "platform team", "operators" — never an ambiguous label such
  as "agent team".
- Every row of a markdown table answers the table's own question, with the same type of entry in
  every row — descriptions go in the text above the table.
- Headings are short noun phrases; no pitch words ("unlock", "empower", "seamless",
  "game-changing", "supercharge"); expand every acronym on first use.

---

## Section 3: Shared-file conventions (preserve exactly)

### requirements.txt
- Header: `# Microsoft Foundry demo — notebooks … — Python 3.12 recommended`.
- **Grouped sections** with comment headers: `# --- Core … (NB1 …, NB2 all) ---`,
  `# --- Voice Live (NB7; …) ---`.
- **Every line carries an inline comment** naming the notebooks/steps that use it and why an
  unusual pin exists, e.g.
  `azure-ai-contentunderstanding>=1.2.0b3   # pre-release pin: 1.1.0 lacks ContentAnalyzerWorkflow …`,
  `a2a-sdk[http-server]>=1.1.4  # … caps protobuf<7`,
  `uvicorn>=0.30  # not a dependency of a2a-sdk — install explicitly`.
- **Pin policy** (applied in Step 4):

| Package kind | Spec | Comment must say |
|---|---|---|
| GA | `>=floor,<next-major` — e.g. `azure-ai-projects[voice]>=2.7.0,<3`, `azure-mgmt-apimanagement>=5.0.0,<6` | notebooks using it |
| Pre-release | `>=x.y.zbN`, or `==x.y.zbN` when later betas are known to break | the reason for the pre-release |
| Any notebook uses a **preview surface** of it (`.beta.`, `allow_preview=True`, `*PreviewTool`, `Foundry-Features` header) | cap at the **next minor** of the highest tested version, e.g. `>=2.8.0,<2.9` | `preview surfaces used in NB<x>` |
| Agent services | `-r agent/src/<agent>/requirements.txt` | which hosted agent |

- **No tested version yet** (a new package, or a preview surface used for the first time): the
  "highest tested version" is the version the code was written against in Step 3, meaning the
  release whose CHANGELOG, samples or API reference was read. Set the floor to that version and
  the cap to its next minor (preview surfaces) or next major (GA). Write
  `untested — written against <version>` in the inline comment until the user confirms a live
  run, then replace it with `tested <yyyy-mm-dd>`.
- Extras where needed (`[voice]`, `[http-server]`). **Never lower or remove an existing pin
  without explicit user approval.**

### .env.example
- Shared names first, following official sample naming: `FOUNDRY_PROJECT_ENDPOINT`,
  `FOUNDRY_MODEL_NAME` (azure-ai-projects 2.1.0 renamed the samples' `AZURE_AI_PROJECT_ENDPOINT`
  → `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME` → `FOUNDRY_MODEL_NAME`,
  `AZURE_AI_MODEL_AGENT_NAME` → `FOUNDRY_AGENT_NAME`), then the tracing flags.
- Then per-notebook blocks headed `# Notebook <n> only: <topic>.` with an inline comment per
  variable.
- Secrets under a `# Keys below are secrets` line, **always empty**. Optional values left blank
  with a comment saying they are optional.

---

## Section 4: Defects already in the kit (worked examples — prevent, never repeat)

1. **Semantic env-var collision.** `AZURE_RESOURCE_GROUP` meant the Foundry resource group in
   notebook 1 but the API Management resource group in notebook 8. Resolved on 2026-10-11:
   notebook 8 now uses `APIM_RESOURCE_GROUP`; both share `AZURE_SUBSCRIPTION_ID` because all kit
   resources use one subscription. `APIM_GATEWAY_URL`
   meant "URL including the API suffix" in notebook 2 but "base URL" in notebook 8 until notebook
   2's gateway section was removed (2026-10-11) — the README had to tell readers to set it per
   notebook.
   **Rule:** a new notebook **reuses** an existing variable **only with the identical meaning**.
   Otherwise it introduces a **new, prefixed name** — feature prefix (`APIM_RESOURCE_GROUP`) or
   `NB<n>_…` — and never redefines an existing one.
2. **Per-notebook `%pip` drift.** Notebook 5 installs `azure-ai-projects>=2.5.0` while the root
   pins `>=2.7.0,<3`. Never emit a per-package `%pip install`; flag every existing one.
3. **Preview-API breakage inside minor versions.** The azure-ai-projects CHANGELOG
   (`https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/CHANGELOG.md`)
   records breaking changes to preview/beta surfaces in 2.2.0, 2.3.0, 2.4.0, 2.5.0, 2.7.0 and
   2.8.0 (2026-10-02): `.beta.toolboxes` → `.toolboxes` (2.3.0); `agent_session_id` → `session_id`;
   renamed `Optimization*` / `DataGeneration*` classes; `create_generation_job` →
   `begin_create_generation_job` long-running operation; `extra_body={"agent": …}` →
   `{"agent_reference": …}` (2.0.0b4). 2.5.0 moved to `openai>=3.0.0` (which uses `httpx2`
   instead of `httpx`) and dropped Python 3.9; 2.3.0 states hosted-agent code upload no longer
   supports `python_3_12`. **A floor-only pin does not protect a notebook that uses a preview
   surface** — hence the minor cap in Section 3.
4. **Transitive conflicts to watch:** `httpx` (a2a-sdk needs `httpx>=0.28.1`) alongside `httpx2`
   (openai 3.x); protobuf caps from a2a-sdk; OpenTelemetry alignment across
   `azure-monitor-opentelemetry`, `opentelemetry-sdk` and `opentelemetry-instrumentation-openai-v2`
   (beta); `azure-core-tracing-opentelemetry` (beta); `azure-monitor-query` 2.0 (metrics moved to
   `azure-monitor-querymetrics`); `azure-search-documents` is now 12.0.0 while the kit floors at
   11.6.0 — a major bump arrives silently unless capped.
5. **Python versions:** kernel 3.12 vs hosted runtime 3.13 — see Section 1.

---

## Section 5: Workflow (BUILD mode)

### Step 0 — LOCATE THE KIT AND READ IT FRESH
1. Find the kit: `GetTaskFolders` (the attached folder holding `kit.yaml`) → else `SearchDrive`
   for `kit.yaml`. If the user names a path, use it. If no kit is found, stop and ask — never
   start a new kit silently. Read `kit.yaml` (and `kit.local.yaml` if present).
2. List it with `GetDriveChildren` and download with `ReadFileContent` into
   `working/kit/<run-date>/` (mirroring kit-relative paths): `README.md`, `requirements.txt`,
   `.env.example`, `.gitignore`, `.devcontainer/devcontainer.json`, `agent/azure.yaml`,
   `agent/src/*/requirements.txt`, every `*.ipynb` and `*.http`, and `NOTEBOOKS-CHANGELOG.md` if
   present. Record each file's **eTag / lastModifiedDateTime** (`GetDriveItem`) for Step 10.
3. **Never rely on copies from earlier sessions** or on this skill's earlier output — the user
   edits in VS Code.
4. Run the baseline check before any change:
   ```bash
   python /mnt/user-config/skills/deck-companion-notebook/scripts/kit_check.py working/kit/<run-date> \
     --json-output working/kit-baseline.json --md-output working/kit-baseline.md
   ```
   Pre-existing FAILs are reported as **pre-existing**, never attributed to the new notebook.

### Step 1 — READ THE DECK
Extract with `python-pptx` (or `python scripts/office/unpack.py`): slide numbers and titles,
status asterisks (`*` = preview in both deck skills), speaker notes, every
`Presenter note: verify …` item, and every source URL in footers and notes. For a
`foundry-whats-new-deck` deck, take the edition from the file name
(`Microsoft-Foundry-Whats-New-<yyyy>-<mm>[-<dd>].pptx`); for an `azure-ai-deep-dive-deck` deck,
from `<topic>-deep-dive-<yyyy>-<mm>.pptx`.

### Step 2 — MAP SLIDES TO STEPS
- One step per **demonstrable** concept, ordered simple → complex along the ladder:
  **read-only call → configuration → create resources → preview features → cleanup**.
- Concepts that cannot be shown in a notebook (portal-only, network topology, pricing) become
  **explain-only** markdown steps — never fake code.
- One realistic, simple **business scenario** runs through all steps (the kit already uses claims
  triage, IT service desk, accounts payable, procurement — pick one not yet used by a paired
  notebook unless it fits much better).
- Show the step map (`Step · Concept · Slide(s) · GA/preview · demo / explain-only · source`)
  and get it approved if the user is present; otherwise proceed and state it on delivery.

### Step 3 — SOURCE THE CODE (priority order; record URL + package version for every API used)
1. The Microsoft Learn how-to / quickstart for the feature — **`/en-us/` locale** (an unprefixed
   URL can return an empty page; retry with `/en-us/`).
2. The package's `samples/` folder and `CHANGELOG.md` in `Azure/azure-sdk-for-python` (or the
   relevant language repo).
3. `microsoft-foundry/foundry-samples`, other `microsoft-foundry/*` repos (e.g. voicelive-samples),
   `Azure-Samples/*` (e.g. the `AI-Gateway` labs, `foundry-citadel-platform`),
   `microsoft/agent-framework`.
4. PyPI release history (`https://pypi.org/project/<pkg>/#history`).
5. The Azure SDK latest-releases inventory: `https://azure.github.io/azure-sdk/releases/latest/python.html`.
6. The Foundry SDK overview: `https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/sdk-overview`
   (azure-ai-projects>=2.3.0 with openai>=3.0.0 and Python 3.10+).

Use `web_fetch` (and `web_search` only to locate a moved page). **Never invent a method, class,
parameter or endpoint.** Anything not confirmed in a source fetched **in this run** gets
`# verify <URL>`; a step that cannot be verified at all becomes explain-only.

### Step 4 — DEPENDENCY IMPACT ANALYSIS (mandatory, before writing anything)
For every package the new notebook needs:
1. **Already in `requirements.txt` with a compatible range** → reuse; add the notebook tag
   (`NB<n>`) to its comment.
2. **Needs a higher floor, or is new** → read the CHANGELOG / release notes **between the current
   floor and the proposed version**: "Breaking Changes", removed or renamed APIs, dependency
   changes (new `Requires-Dist`, dropped Python versions).
3. **Build the API-usage inventory of ALL existing notebooks** (and the agent requirements) — the
   `api_chains` and `imported_names` per cell in `kit-baseline.json`. Write every breaking change
   found in item 2 as `{"package", "symbol", "change", "url"}` into `working/breaking.json` and run:
   ```bash
   python /mnt/user-config/skills/deck-companion-notebook/scripts/kit_check.py working/kit/<run-date> \
     --breaking working/breaking.json --json-output working/kit-impact.json --md-output working/kit-impact.md
   ```
   Report **every** collision with notebook + cell. (Keyword renames use `kw:<name>`, e.g.
   `kw:agent_session_id`.)
4. Apply the **pin policy** (Section 3). Record preview surfaces per notebook (`preview` in the
   report) — they drive the minor cap.
5. **A change that would break an existing notebook is NOT applied silently.** Present options and
   wait: **(a)** update the affected cells of the existing notebook — a proposed patch shown as a
   diff, applied only with approval; **(b)** keep the old version and adapt the new notebook;
   **(c)** last resort: a separate environment / requirements group, with the reason.
6. **Transitive conflicts** (Section 4, defect 4). Where the package index is reachable, resolve
   the **whole kit** in a throwaway virtual environment built on a copy of the kit:
   ```bash
   python3.12 -m venv /tmp/kitvenv
   /tmp/kitvenv/bin/pip install --dry-run --report /tmp/resolve.json -r requirements.txt   # or: uv pip compile requirements.txt --python-version 3.12
   /tmp/kitvenv/bin/pip install -r requirements.txt && /tmp/kitvenv/bin/pip check
   ```
   (run from the copied kit root so `-r agent/src/...` includes resolve; use the index named in
   `kit.local.yaml` or the contributor's `PIP_INDEX_URL` when set and reachable, otherwise PyPI;
   never write a private index into a shared file). **If resolution cannot be executed** (sandbox without index
   access), say so, fall back to the `Requires-Dist` metadata on PyPI pages plus the CHANGELOGs,
   and label the result **"resolved by reading, not executed"**.
7. Output the **DEPENDENCY CHANGE LOG** (format in Output).

### Step 5 — ENV IMPACT ANALYSIS
1. From `kit-baseline.json`: every variable each notebook reads (`os.getenv`, `env("…")`,
   `os.environ[...]`) and its meaning from `.env.example` comments and the README env table.
2. New variables: reuse a shared name **only with identical meaning**; otherwise a prefixed name.
   Append a `# Notebook <n> only: <topic>.` block; secrets flagged and left empty.
   **Never rename or delete an existing variable.**
3. Output the **ENV CHANGE LOG**.
4. Flag pre-existing collisions the checker reports (`env.collisions`; see the resolved
   `APIM_GATEWAY_URL` and `AZURE_RESOURCE_GROUP` examples in Section 4) and propose a fix as a **separate, approval-gated item** — typically a
   new prefixed name for one notebook, with the cell diff and the README change.

### Step 6 — BUILD THE NOTEBOOK
- File name: next free number from `next_free_notebook_number` →
  `foundry-demo-<n>-<topic-kebab>.ipynb`. **Never renumber** existing notebooks.
- nbformat 4, Python 3 kernel metadata, **empty outputs**, `execution_count: null`.
- Follow Section 2 exactly: title cell, Step 0 template, step headings with slide numbers,
  gating, flags, backups, cleanup, closing cells, `# verify` markers.
- Write it with `json` / `nbformat` into `working/kit-out/` (never hand-edit JSON strings).

### Step 7 — ENRICH THE SHARED FILES BY PATCH, NOT REWRITE
Copy each freshly read file to `working/kit-out/` and **patch** it; then produce a unified diff
(`diff -u`) against the Step 0 version:
- **`requirements.txt`** — add/adjust lines **inside the right section**, with tags; keep order,
  header and every existing comment.
- **`.env.example`** — append the new `# Notebook <n> only:` block.
- **`README.md`** — one row in *Choose a Notebook*; one row in *Slide Decks*; one notebook
  section; env-table rows in *Local Setup*; one item in *Recommended Demo Flow*; one paragraph in
  *Costs, Validation, and Cleanup*; one entry in *Repository Guide*.
- **`.devcontainer/devcontainer.json`** — only if a new CLI tool, extension or port is required.
- **`.gitignore`** — only if the notebook generates new files (backups, audio, exports).

A diff that removes or rewrites existing lines it was not asked to change is a defect — redo it.

### Step 8 — REGRESSION GATE (across ALL notebooks, not just the new one)
Run the checker on the **patched** kit (`working/kit-out/` merged over the Step 0 copy):
```bash
python /mnt/user-config/skills/deck-companion-notebook/scripts/kit_check.py working/kit-merged \
  --new foundry-demo-<n>-<topic>.ipynb --breaking working/breaking.json \
  [--resolve-with /tmp/kitvenv/bin/python] \
  --json-output working/kit-gate.json --md-output working/kit-gate.md
```
It checks: every code cell compiles (`ast`, top-level await allowed, `%`/`!` magics stripped);
every import maps to a requirement — or, with `--resolve-with`, is importable in the resolved
venv; breaking-change collisions against the inventory; every env var read is in `.env.example`;
no per-package `%pip install`; no likely secrets; no stored outputs in the new notebook (FAIL)
or existing ones (WARN); preview packages without a minor cap; requirements without a comment.
Attribute chains not covered by `--breaking` are confirmed by introspection in the venv when it
exists (`hasattr` on the imported class — never by running notebook cells), otherwise by the
CHANGELOG reading; say which. Optionally mock-run the new notebook's **pure helper functions**
(no Azure calls).
Report **pass/fail per notebook honestly**, separating pre-existing findings from new ones. The
new notebook is **"not executed against Azure"** unless it was; recommend the user run it once in
VS Code against a **non-production** project.

### Step 9 — NOTEBOOK CHANGELOG
Add an entry to **`NOTEBOOKS-CHANGELOG.md`** in the kit (create it if absent). **Never write into
the deck changelog** (`decks/CHANGELOG.md`) — `foundry-whats-new-deck` owns and parses it.
Template in Output. Then prepare the **`kit.yaml` diff**: the new notebook entry (number, file,
paired deck, slides, environment variables), new `env` entries with their meaning, and
`next_notebook_number` + 1.

### Step 10 — DELIVER
1. Save to `output/` (generate in `working/kit-out/`; if a direct write to `output/` fails,
   publish with `CopyArtifact(surface="output", …)`): the new notebook, the patched shared files
   under their kit-relative names, `NOTEBOOKS-CHANGELOG.md`, the `kit.yaml` diff and `kit-gate.md`.
2. Summarise each diff in chat (lines added / changed per file, nothing removed).
3. **Upload into the kit folder only when** the user asks, or the kit folder was attached and the
   user requested an in-place update. Before uploading a shared file, re-read its current
   eTag/content (`GetDriveItem` / `ReadFileContent`); if it changed since Step 0, **re-merge** the
   patch onto the new content and show the new diff. Upload with `UploadFileContent`; if an upload
   fails, keep the `output/` copy and say it did not land in the kit.
4. **Cowork never pushes to GitHub.** Tell the contributor to commit on a branch and open a pull
   request; the gate result (`kit-gate.md`) goes into the pull-request description.
5. **Never overwrite the user's refined notebooks.** Changes to existing notebooks are proposals,
   applied one by one per approval.

---

## Section 6: DECK REFRESH MODE

When a deck gets a new dated edition (e.g. `foundry-whats-new-deck` edition 2026-10 added Flex
processing to slide 9):
1. Steps 0–1 on the kit and on **both** editions; diff slide titles and numbers to build an
   old → new slide map.
2. Update the paired notebook's slide references (title-cell table and every step heading).
3. Add steps for new concepts (Steps 2–3); mark removed or retired concepts in the step's
   markdown instead of deleting the step silently.
4. Run Steps 4, 5, 7 and 8 unchanged — same dependency and regression gates.
5. Present the notebook change as a **diff proposal** (the notebook is user-refined); apply only
   on approval. Log a NOTEBOOKS-CHANGELOG entry with the new edition and slide map.

## Section 7: DEPENDENCY AUDIT MODE

"Check the kit's dependencies" — **no new notebook**:
1. Step 0, then `kit_check.py` for the baseline inventory.
2. For every requirement (root and `-r` includes): current floor vs latest release (PyPI history,
   the Azure SDK latest-releases inventory).
3. List breaking changes between floor and latest from each CHANGELOG; write them to
   `breaking.json`; map them to notebook usages with `--breaking`.
4. Propose **safe bumps and caps** per the pin policy (e.g. cap `azure-search-documents` below 12
   until notebooks are checked against 12.0.0); resolver dry run where possible.
5. Output the DEPENDENCY CHANGE LOG as **proposals**; apply only on approval.
6. Record `**Last dependency audit:** <yyyy-mm-dd>` in NOTEBOOKS-CHANGELOG.md.
Recommend running it **monthly or before each customer session**.

---

## Output

**STEP MAP** (Step 2):
```
| Step | Concept | Slide(s) | Status | Demo / explain-only | Source |
```

**DEPENDENCY CHANGE LOG** (Step 4 / audit):
```
| Package | Old spec → new spec | Reason | Notebooks affected | Breaking changes reviewed (URL) | Verdict |
```
Verdict is one of: `reused` · `tag added` · `bump — safe` · `cap added` · `needs approval — breaks NB<x> cell <y>` · `rejected`.
Footer line: `Resolution: executed (pip/uv, index <url>) | resolved by reading, not executed`.

**ENV CHANGE LOG** (Step 5):
```
| Variable | Added / reused | Meaning | Notebooks |
```
plus `Pre-existing collisions: <variable — notebooks — proposed fix (approval needed)>`.

**`NOTEBOOKS-CHANGELOG.md` entry** (Step 9):
```
## <yyyy-mm-dd> · foundry-demo-<n>-<topic>.ipynb — added | updated
**Paired deck:** <file> · edition <yyyy-mm> · slide map: step 1 → slide <x>; step 2 → slides <y, z>; …
**Dependency changes:** <package old → new, or none>
**Env changes:** <variable added/reused, or none>
**Regression:** <n>/<n> notebooks pass static gate · pre-existing: <list or none> · resolver: executed | resolved by reading, not executed · new notebook not executed against Azure
**Open verify items:** <list or none>
**Last dependency audit:** <yyyy-mm-dd>
```

**Files** (`output/`): `foundry-demo-<n>-<topic>.ipynb`, patched `requirements.txt`,
`.env.example`, `README.md` (and `.devcontainer/devcontainer.json` / `.gitignore` only when
changed), `NOTEBOOKS-CHANGELOG.md`, `kit.yaml` diff, `kit-gate.md`.

**Final chat report** (≤20 lines): notebook file and step count; paired deck + edition; step map
summary; dependency and env change counts with any approval items; regression result per
notebook; resolver mode; open `# verify` items; upload status (uploaded / output-only).

---

## Guardrails

- **Never fabricate** SDK calls, classes, parameters, endpoints, outputs, versions or GA status.
  Unconfirmed → `# verify <URL>`; unverifiable → explain-only. If research tools are unavailable,
  say so and stop rather than producing unverified code.
- **Never put keys or secrets** in a notebook or `.env.example`. Entra ID
  (`DefaultAzureCredential`) by default; secret variables are left empty and flagged.
- **Never regenerate a shared file wholesale.** Patch by section; never delete or rename an
  existing variable, package, pin or notebook; never lower a pin without explicit approval.
- **Never apply a change that breaks an existing notebook without explicit approval** — present
  options (a)/(b)/(c) and wait.
- **Never write into the deck changelog** (`decks/CHANGELOG.md`) — it belongs to
  `foundry-whats-new-deck`.
- **Never put a personal path, tenant, subscription, resource name, private package index or
  person's name** into a shared kit file — placeholders only; personal values belong in `.env`
  (git-ignored) or `kit.local.yaml`.
- **Never overwrite a user-refined notebook**; changes to existing notebooks are diffs applied per
  approval.
- **Never upload into the kit without a fresh eTag/content re-check**; re-merge on change.
- **Never emit a per-package `%pip install`**; flag existing ones.
- **Destructive or chargeable cells are clearly marked**; cleanup states what remains billable.
- **Never claim a run you did not do** — "not executed against Azure" and "resolved by reading,
  not executed" are stated whenever they apply.
- **Public documentation and public repos only.** Internal Teams / Viva Engage / SharePoint
  material is never put into a notebook.
- **Preview features are labelled** in headings and the step table, and preview surfaces are
  recorded for pin capping.
- **Wording rules apply to markdown cells** (Section 2.6) — no "Learn says/lists", no ambiguous
  actor labels (write "development team"), no mixed-type table rows, no pitch words, acronyms
  expanded.
- `scripts/kit_check.py` is static: it never executes notebook code; `--resolve-with` only asks a
  throwaway venv whether modules can be found.

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Notebook works in the sandbox check but fails in VS Code | static gate only; Azure not called | run once in VS Code against a non-production project; record the result |
| `pip` dry run cannot reach an index | sandbox without network to PyPI / the Microsoft feed | fall back to `Requires-Dist` + CHANGELOG reading; label "resolved by reading, not executed" |
| kit_check reports collisions that pre-date this run | defects 1–2 in Section 4 | report as pre-existing; propose fixes as separate approval items |
| Slide numbers in the notebook no longer match the deck | new deck edition | DECK REFRESH MODE |
| Upload refused or eTag changed | user edited the file in VS Code meanwhile | re-read, re-merge, show the new diff |
