# Microsoft Foundry — What's New · deck changelog

One entry per dated edition, newest first. Each entry lists what changed since the previous edition, the source consulted for each change, the run date, and any items still to verify before presenting. Maintained by the `foundry-whats-new-deck` skill; entries are appended, never rewritten.

Location: `decks/` (path in `kit.yaml` → `paths.deck_changelog`). Deck file pattern: `Microsoft-Foundry-Whats-New-<yyyy>-<mm>[-<dd>].pptx` · 26 slides from edition 2026-10-22 (25 before) · 16:9 · speaker notes on every slide.

---

## Edition 2026-10-22

**File:** `Microsoft-Foundry-Whats-New-2026-10-22.pptx`
**Run date:** 2026-10-22 · **Baseline:** 2026-10-13 · **Last sweep:** 2026-09-16 · **Next detect run due:** 2026-11-05
**Structure:** CHANGED — one slide added at position 12 (section 03, after "Tools, Toolboxes and Skills"). Deck is now 26 slides; slides 12–25 of the previous edition become 13–26. Section 03 holds four slides (11–14). Base: the repository copy of edition 2026-10, which already carries the 2026-10-13 slide 7 changes and the hand-written speaker notes.

### Changes since edition 2026-10-13
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|
| 12 | NEW SLIDE — "Browser automation tool": agent → toolbox → Playwright Workspace → websites flow, human oversight (Live View, Take control, screenshot recording), setup paths, prerequisites, regions, governance, comparison with computer use | GA 19 Oct 2026 (private website browsing preview) | learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/browser-automation · devblogs.microsoft.com/foundry/browser-automation-tool-ga/ |
| 2 | Agenda ranges 11–14, 15–20, 21–24, 25–26; section 03 lists the browser automation tool | — | — |
| 3 | Voice agents* added to Agent Runtime; A2A and browser automation unmarked (GA); Insights* added to Observability | mixed | devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-september-2026/ |
| 4 | A2A and tool search unmarked (GA); second-person wording removed | GA | as above |
| 6 | azd extension azure.ai.agents beta.18, azd 1.34.2 or later; notes add Foundry Local 2.1 | preview | as above |
| 7 | claude-fable-5-1 status `available` → `Preview*`; "who bills you" wording removed | preview | learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models |
| 9 | Flex supported models: gpt-6.1-sol, GPT-6 and GPT-5.6 families (was gpt-5.6-sol only) | preview | learn.microsoft.com/en-us/azure/foundry/openai/how-to/flex-processing (updated 10/12/2026) |
| 10 | Routing pool adds gpt-6-astra, claude-fable-5-1, claude-opus-5, claude-sonnet-5, grok-4.6, Fireworks FW-GLM-5.3 / 5.3-Flash / FW-Kimi-K3; preview footnote added; notes rewritten | GA | learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router |
| 11 | Tool search, A2A and browser automation unmarked (GA); prompt-agent toolboxes marked preview | mixed | devblogs September roundup · learn…/agents/how-to/tools/tool-search |
| 15 | Prompt agent box adds "text or voice*"; second-person wording removed | preview | learn.microsoft.com/en-us/azure/foundry/agents/overview · agents/quickstarts/prompt-voice-agent |
| 18 | Agent Framework current releases python-1.22.0 and dotnet-1.25.0 | breaking change — open-source SDK | github.com/microsoft/agent-framework/releases |
| 21 | Insights* added to Monitoring; cross-references corrected to slides 24, 23, 22 | preview | learn.microsoft.com/en-us/azure/foundry/observability/how-to/agent-insights (updated 10/21/2026) |
| 24 | Notes only: Insights on top of stored traces | preview | as above |
| 25 | Title renamed "Changes since Build 2026"; timeline rewritten (3 Apr dropped, new dot 29 Sep – 19 Oct); still-preview band updated | mixed | devblogs September roundup · browser automation GA post |
| 26 | References add browser automation, voice agent configuration, Insights, September roundup and browser automation post; verify list in notes | — | — |
| 12–26 | Footer page numbers shifted by one | — | — |

### Detected but not applied
| Item | Reason |
|---|---|
| Voice agents in Foundry Agent Service (preview) | Importance test Gate 2 not met (no own announcement, preview); the kit has a Voice Live deep-dive deck — covered as text patches on slides 3 and 15 |
| Insights in Foundry (preview) | Gate 2 not met (no capability-reference row, preview) — text patches on slides 3 and 21, notes on slide 24 |
| gpt-chat-latest 2026-10-07 snapshot (preview), sora-2, claude-opus-5-5-fast | No new rows added to the slide 7 table by earlier instruction; opus-5-5-fast mentioned in notes |
| MAI-Image-2.6 public preview (September roundup) | Conflicts with the 2026-10-13 run; listed as a verify item |
| Rubric evaluation, synthetic data, Agent Optimizer GA | Announced as targets only |
| Content Understanding toolkit and CLI, Speech LLM 2607 | Out of scope for this deck |

Open verify items:
- Date from which Flex processing applies to the GPT-6 models (Learn lists the models, not a date).
- GA of rubric evaluation, synthetic dataset generation and Agent Optimizer.
- Capability reference (updated 2026-08-27) still labels browser automation as preview.
- MAI-Image-2.6 status; claude-fable-5-1 lifecycle.
- **Carried over:** pre-existing second-person wording on slides 5, 8, 14, 16, 20, 22, 23 and 24; text at 6.5–7.0pt on slides 23 and 24.

---

## Edition 2026-10-13

**File:** `Microsoft-Foundry-Whats-New-2026-10-13.pptx`
**Run date:** 2026-10-13 · **Baseline:** 2026-10-07 · **Last sweep:** 2026-09-16 · **Next detect run due:** 2026-10-27
**Structure:** unchanged — 25 slides. Requested update: slide 7 table keeps only current new entries; models superseded since the table was set are replaced by their successors in the same rows (no rows added).

### Changes since edition 2026-10
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|
| 7 | Row `gpt-5.6 sol · terra · luna` → `gpt-6.1-sol` (GA · 29 Sep 2026; 1,050,000 tokens; multi-agent orchestration*) | GA | learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure |
| 7 | Row `gpt-6 astra · luna · sol` → `gpt-6 astra · luna` (gpt-6-sol carries no NEW flag; succeeded by gpt-6.1-sol) | GA | as above |
| 7 | Row `Claude Opus 5` → `Claude 5.5 family` (Opus · Sonnet · Haiku; GA · 22 Sep–7 Oct 2026; 1M / 128k) | GA | learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models (updated 09/22/2026) · anthropic.com/claude-opus-5-5 · support.claude.com release notes |
| 7 | MAI family list `Thinking-1 · Image-2.6 · Transcribe-2 · Voice-2` → `Thinking-1 · Transcribe-2 · Voice-2` (MAI-Image-2.6 not in Foundry) | preview | github.com/microsoft-foundry/model-releases (CHANGELOG, models/microsoft-ai) |
| 7 | Row `grok-4.6` (preview) → `grok-4.7` (GA · Oct 2026; 500,000 tokens; six-month minimum availability) | GA | learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-grok (updated 10/06/2026) · ai.azure.com/catalog/models/grok-4.7 |
| 7 | Footnote and source line name provider announcements alongside Microsoft Learn; speaker notes rewritten (195 words) | — | — |

### Items detected but not applied
| Item | Reason |
|---|---|
| Microsoft-Decision-1 (preview, text classification) | no room without adding a row; no Microsoft Learn page found to verify it |
| claude-fable-5-1 status "available" | Learn lists Hosted on Anthropic infrastructure: Preview — correction proposed, awaiting approval |
| slide 7 "who bills you" (subtitle, card labels) | pre-existing second-person wording; outside this request |
| gpt-5.6 references on slides 9, 10 and 24 | facts about Flex processing, Model Router and the timeline, not new-model lists |

### Verify before presenting
- grok-4.7 release date in Foundry (provider posts report 7 October 2026; Learn page updated 6 October).
- claude-fable-5-1 lifecycle (preview on Anthropic infrastructure).

---

## Edition 2026-10

**File:** `Microsoft-Foundry-Whats-New-2026-10.pptx`
**Run date:** 2026-10-07 · **Baseline:** 2026-09-29 · **Last sweep:** 2026-09-16 · **Next detect run due:** 2026-10-13
**Structure:** unchanged — 25 slides. Requested update (Flex processing), applied as a card, not a new slide.

### Changes since edition 2026-09-29
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|
| 9 | Title `Priority Processing (new)` → `Priority and Flex processing`; subtitle rewritten; the amber 25-September note is replaced by a full-width **Flex processing\*** card (selected per request; price and service level; behaviour when capacity is short; supported models) with the preview footnote; source line adds how-to/flex-processing; speaker notes rewritten (198 words) | preview | learn.microsoft.com/en-us/azure/foundry/openai/how-to/flex-processing (updated 09/28/2026) |
| 8 | Options card: `Option on a Standard deployment` → `Options on a Standard deployment`; Priority line shortened; **Flex processing\*** line added; notes now point to slide 9 and were trimmed to 198 words (were 235) | preview | as above |
| 24 | Timeline dot 8: `flex-to-standard fallback retired` → `Flex processing Preview (gpt-5.6-sol)`; "Still Preview" band gains Flex processing; notes reworded | preview | as above |
| 2 | Section 02 description: `Deployment types and Priority Processing` → `Deployment types, Priority and Flex processing` (ranges unchanged) | — | — |
| 25 | Learn list adds `how-to/flex-processing`; presenter checklist gains the Flex verify item | — | — |
| 1, 2–25 | Edition month: title slide and every footer `September 2026` → `October 2026` | — | — |

### Placement rationale
Flex processing sat at depth level 1 (named only, in the amber note on slide 9 and on the slide 24 timeline), so Gate 1 passed. Gate 2 failed on both mandatory signals: there is no Flex row in the capability reference (the "Deployment types" row names priority processing only), and Learn has a how-to page but no concept page. Signal 3 (own announcement) was not found, signal 4 holds (Learn's "Choose a processing option" table), and signal 5 fails (preview), giving 1/5. Outcome: a card on the slide that already owns service tiers. Learn itself groups Flex, Standard and Priority as "service-tier choices for online API requests", so slide 9 is the natural host and slide 8 points to it.

Open verify items:
- Flex processing launch date: Learn gives none (article dated 24 September 2026, updated 28 September). The timeline places it in the 22–25 September window alongside the fallback retirement.
- Flex supported models: gpt-5.6-sol (2026-07-09) only, at this run. Re-check before presenting.
- **Carried over:** slides 22 and 23 still hold text at 6.5–7.0pt. Slide 24's title "What changed since Build 2026 — timeline" breaks the noun-phrase title rule; it is a fixed slide-map title, left unchanged pending approval of a rename.

---

## Edition 2026-09-29

**File:** `Microsoft-Foundry-Whats-New-2026-09-29.pptx`
**Run date:** 2026-09-29 · **Baseline:** 2026-09-22 · **Last sweep:** 2026-09-16 · **Next detect run due:** 2026-10-13
**Structure:** CHANGED — one slide added at position 18 under the new importance override. Deck is now 25 slides; slides 18–24 of the previous edition become 19–25. Section 04 holds six slides (14–19), the documented exception.

### Changes since edition 2026-09-22
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|
| 18 | NEW SLIDE — "Routines: running an agent without a person". Three trigger types (timer, recurring cron, event), one-agent action with run history, Microsoft's routines-versus-workflows decision table, dispatch-identity / region / CMK limits, reminder tool. | GA 24 Sep 2026 | learn…/agents/concepts/routines · learn…/agents/how-to/use-routines · devblogs.microsoft.com/foundry routines GA post |
| 7 | Catalog row `gpt-6-astra` → `gpt-6 astra · luna · sol`; date `3 Sep 2026` → `3–22 Sep 2026` | new model | learn…/foundry-models/concepts/models-sold-directly-by-azure |
| 14 | `Python and C# · 34 regions` → `31 regions` — resolves the open verify item from edition 2026-09-22 | correction | learn…/agents/concepts/hosted-agents |
| 17 | `python-1.18.0 and dotnet-1.21.0` → `python-1.19.0 and dotnet-1.22.0` | breaking change — open-source SDK | github.com/microsoft/agent-framework/releases |
| 24 | Timeline dot 8: `25 Sep` → `22–25 Sep`; body now gpt-6 luna and sol, routines GA, network egress controls Preview, flex fallback retired | mixed | as above |
| 24 | "Still Preview" band gains network egress controls and reminder tool; source line and closing sentence refreshed to 24 September 2026 | preview | learn…/agents/how-to/add-hosted-agent-guardrails |
| 21 | Speaker notes rewritten to 200 words and given a presenter note on egress controls: same RAI policy, hosted agents only, ordered host rules, Audit then Enforce, 480-rule cap, fails closed | docs-only | as above |
| 2 | Agenda ranges: 04 `14–18` → `14–19`; 05 `19–22` → `20–23`; 06 `23–24` → `24–25`; section 04 description gains "Routines" | — | slide-map impact |
| 19–25 | Footer right renumbered (previously 18–24) | — | slide-map impact |

### Placement rationale — first use of the importance override
Routines sat at depth level 1 (a chip on slide 3) and the host slide had room for a card, so under the previous rules it would have been demoted. The skill was amended this run so that a Learn-evidenced importance test can outrank the slide budget. Routines scored **5/5** on the Gate 2 signals: its own capability-reference row; its own concept and how-to pages; its own GA announcement; an explicit "Routines and workflows" decision table published by Microsoft; and generally available status. Placed after slide 17 because the first audience question is how a routine differs from a workflow. Cost, accepted by the user: section 04 grows to six slides.

### Items detected but not applied
| Item | Reason |
|---|---|
| Network egress controls as a slide | Gate 1 failed — already at depth 2 on slide 21 with the preview asterisk. Notes enrichment only. |
| Reminder tool as a slide or card | Gate 1 passed at level 1 but Gate 2 failed signals 1, 2 and 5 (no capability-reference row, no own doc subtree, preview). Stays a chip on slide 11, now also named on slide 18. |
| gpt-chat-latest, sora-2, gpt-image-2.5 variants | Slide 7 table at capacity; not architecture-decision changing |
| Agent Framework vector-store connectors | Open-source SDK breadth, not a Foundry service capability |

Open verify items:
- **Pre-existing, not introduced this edition:** slides 22 (evaluations) and 23 (tracing) carry chip and key-value text at 6.5–7.0pt, below the 7.5pt floor in the visual rules. Left unchanged because correcting it is a layout change, not a patch. Worth a dedicated redesign pass.
- **Pre-existing:** speaker notes on 13 slides exceed the 120–200 word band, the longest being slide 25 at 299 words. Slides changed this edition (18 at 195, 21 at 200) are in band.
- Routines region exclusions (UK West, Switzerland West, Japan West, UAE North, Norway East) were correct on 2026-09-29; re-check before presenting.

---


## Edition 2026-09-22

**File:** `Microsoft-Foundry-Whats-New-2026-09-22.pptx`
**Run date:** 2026-09-22 · **Baseline:** 2026-09-16 · **Last sweep:** 2026-09-16 · **Next detect run due:** 2026-10-06
**Structure:** CHANGED — one slide added at position 16 on user request. Deck is now 24 slides; slides 16–23 of the previous edition become 17–24.

### Changes since edition 2026-09-16
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|
| 16 | NEW SLIDE — "Publishing a hosted agent to Teams and Microsoft 365". Left: hosted agent capability/status table (9 rows, 7 GA, 2 Preview). Right: shape-built flow for reaching Microsoft 365 from a project with public network access disabled, the `enable_m365_public_endpoint` property, and two caution cards. | mixed | learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents · learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot-virtual-network |
| 2 | Agenda ranges: section 04 "Slides 14–17" → "Slides 14–18"; section 05 "18–21" → "19–22"; section 06 "22–23" → "23–24" | — | slide-map impact of the insertion |
| 2 | Section 04 description gains "Publishing to Teams and Microsoft 365" | — | as above |
| 17–24 | Footer right renumbered (previous 16–23) | — | slide-map impact |

### Placement rationale
Section 04 (Agent Service and Agent Framework), inserted immediately after slide 15 "Protocols and APIs an agent speaks", which introduces the Activity protocol the new slide depends on. The 14→15 pair (Agent Service → the protocols it speaks) is not split. Section 04 now holds five slides, the maximum the skill permits before a merge is required.

### Sources consulted
| Source | Page date | Used for |
|---|---|---|
| learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents | updated 09/11/2026 | capability/status table, sandbox and session model, A2A v1.0 GA vs v0.3 preview, private networking, network-secured container registry |
| learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot-virtual-network | updated 08/28/2026 | `enable_m365_public_endpoint`, source-IP filtering, authorization schemes, inbound path, limitations |
| learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-copilot | updated 09/21/2026 | portal publishing unsupported when public network access is disabled |
| learn.microsoft.com/en-us/azure/foundry/agents/how-to/configure-agent | updated 09/21/2026 | protocol and authorization scheme requirements for Microsoft 365 publishing |
| github.com/sureshpaulraj/foundry-private-agent-teams | commit c67a691 | reference implementation — corroboration only; every fact on the slide traces to a Learn page |

Open verify items:
- Slide 14 states "34 regions" for hosted agents; the hosted-agents page list read on 2026-09-22 enumerates 31. Confirm the current count on the Learn page before presenting, then correct slide 14 in the next edition.
- Durable state store carries no explicit preview marker on the hosted-agents page and is shown as generally available. Re-confirm if a dedicated status page appears.

---


## Edition 2026-09-16

**File:** `Microsoft-Foundry-Whats-New-2026-09-16.pptx`
**Run date:** 2026-09-16 · **Baseline:** 2026-09-11 · **Last sweep:** 2026-09-16 · **Next detect run due:** 2026-09-30
**Structure:** unchanged — 23 slides, no slide added, removed or renumbered.

### Changes since edition 2026-09
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|
| 14 | "Other agents — A2A* · Invocations" and the protocol row lose the preview asterisk on A2A | GA | learn.microsoft.com/en-us/azure/foundry/agents/how-to/migrate |
| 15 | Tool-availability table: A2A under "New experience" Preview → GA; "A2A peers" card Preview → GA; inbound lane "a2a — Preview" → "a2a — GA" | GA | same |
| 16 | Orchestration row: "A2A (Preview)" → "A2A" | GA | same |
| 16 | Status row: "dotnet-1.20.0" → "dotnet-1.21.0" | breaking change — open-source SDK | github.com/microsoft/agent-framework/releases |
| 10 | Model subset caption gains session affinity* and per-request routing metadata* | preview | learn.microsoft.com/en-us/azure/foundry/foundry-models/whats-new-model-router |
| 10 | Governance card gains "Now in 32 regions, 23 of them with Data Zone Standard" | GA | same |
| 22 | Timeline dot 7: "3 Sep" → "3–16 Sep"; body now gpt-6-astra, A2A tool GA, Model Router 32 regions | mixed | as above |
| 22 | "Still Preview" band: A2A removed | GA | migrate page |
| 23 | Verify list: Model Router region count resolved and removed | — | whats-new-model-router |
| 10, 15, 16, 23 | Speaker notes updated: a2a_preview distinction, dotnet-1.21.0 breaking changes, September router additions, resolved region fact | — | as above |

### Items detected but not applied
| Item | Reason |
|---|---|
| Autopilots (depth 0) | Passes the new-slide test; deferred to a design conversation — needs section and position confirmed |
| Routines, Voice Live, fine-tuning (depth 1, GA) | Thin coverage; proposed as cards in a later edition |
| Reasoning models, model migration, multi-agent orchestration via Responses API | Material, card-sized; deferred with the above |
| sora-2, gpt-chat-latest, codex and image model families, Claude Mythos | Catalog gaps on slide 7; table is at capacity, needs a prune decision |
| Notification Center, diagnostic logging, cost management, HA/DR, Azure Government, healthcare models, CI/CD | Known, not included — failed the materiality test |

### Verify before presenting
Unchanged from edition 2026-09 except the Model Router region count, now resolved. Remaining: Foundry Agent Service SLA; Teams / Microsoft 365 Copilot publishing GA date; Assistants API retirement date; SLA percentages per deployment type; legacy ToolSet class; default guardrail severity; Control Plane announcement date; Logic Apps connector count.

### Preview features at edition date
Memory · agent guardrails (tool call / tool response points) · long-running agents · Work IQ · Fabric IQ · client-side tracing · agent monitoring dashboard · most Foundry IQ knowledge sources · AI gateway in Foundry · Skills · tool search · managed compute · instant access models · MAI model family · session affinity · per-request routing metadata · a2a_preview endpoint
*(A2A tool moved to GA this edition.)*

---

## Edition 2026-09 — initial edition

**File:** `Microsoft-Foundry-Whats-New-2026-09.pptx`
**Run date:** 2026-09-11 · **Baseline:** — (initial edition) · **Next detect run due:** 2026-09-25
**Sources checked on the run date:** Microsoft Learn, Foundry developer blog, GitHub

### Scope
Covers Microsoft Foundry releases and announcements through Build 2026 (2 June 2026) and the July–August 2026 roundup (published 9 September 2026). Ignite 2026 had not taken place at edition date.

### Structure
| Section | Slides |
|---|---|
| 01 Microsoft Foundry architecture | 3–6 |
| 02 Foundry Models | 7–10 |
| 03 Foundry Tools and Microsoft IQ | 11–13 |
| 04 Agent Service and Agent Framework | 14–17 |
| 05 Foundry Control Plane | 18–21 |
| Wrap-up | 22–23 |

### Sources consulted
- learn.microsoft.com/azure/foundry — what-is-foundry · concepts/architecture · concepts/capability-reference · how-to/develop/sdk-overview · whats-new-foundry
- learn.microsoft.com/azure/foundry/foundry-models/concepts — deployment-types · models-sold-directly-by-azure · models-from-partners
- learn.microsoft.com/azure/foundry/openai/concepts — model-router · priority-processing
- learn.microsoft.com/azure/foundry/agents — overview · concepts/hosted-agents · concepts/tool-catalog · concepts/toolbox-overview · how-to/use-your-own-resources · how-to/migrate · how-to/memory-usage · how-to/tools/work-iq · how-to/tools/fabric-iq · how-to/foundry-iq-connect · concepts/long-running-agent-resilience · how-to/manage-task-state
- learn.microsoft.com/azure/search — agentic-retrieval-overview · agentic-knowledge-source-overview
- learn.microsoft.com/agent-framework/overview · github.com/microsoft/agent-framework/releases
- learn.microsoft.com/azure/foundry/control-plane/overview · guardrails/guardrails-overview · ai-services/content-safety/overview
- learn.microsoft.com/azure/foundry/concepts — built-in-evaluators · observability · ai-red-teaming-agent
- learn.microsoft.com/azure/foundry/observability/how-to — cloud-evaluation-targets · evaluate-agent · trace-agent-client-side · how-to-monitor-agents-dashboard
- learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat
- learn.microsoft.com/azure/api-management/genai-gateway-capabilities
- devblogs.microsoft.com/foundry — What's new in Microsoft Foundry: Build 2026 · July–August 2026
- devblogs.microsoft.com/agent-framework — Microsoft Agent Framework version 1.0

### Verify before presenting
Items the documentation did not confirm at edition date. Also listed in the speaker notes of slide 23.
- Foundry Agent Service SLA — no SLA page found; do not quote a figure
- Publishing to Microsoft Teams and Microsoft 365 Copilot — GA planned for June 2026, not confirmed on Learn
- Assistants API retirement date — not published on Learn
- SLA percentages per deployment type — see the Azure OpenAI Service SLA document
- Model Router region count — blog states 28 Global Standard regions; the Learn table lists 33 *(resolved in edition 2026-09-16)*
- Legacy ToolSet class in the classic azure-ai-agents SDK — not confirmed
- Default guardrail severity — "medium" is not documented; default guardrail is Microsoft.DefaultV2
- Foundry Control Plane announcement date — do not attribute to Ignite 2025
- Logic Apps connector count (1,400+) — appears only on the product page, not on Learn

### Preview features at edition date
Memory · A2A · agent guardrails (tool call / tool response points) · long-running agents · Work IQ · Fabric IQ · client-side tracing · agent monitoring dashboard · most Foundry IQ knowledge sources · AI gateway in Foundry · Skills · tool search · managed compute · instant access models · MAI model family

---

<!-- Template for the next edition. Copy it, fill it in, and insert it directly under the header so the newest edition is first.

## Edition <yyyy>-<mm>

**File:** `Microsoft-Foundry-Whats-New-<yyyy>-<mm>.pptx`
**Run date:** <yyyy-mm-dd> · **Baseline:** <previous run date> · **Last sweep:** <yyyy-mm-dd> · **Next detect run due:** <run date + 14 days>

### Changes since edition <previous>
| Slide | Change | Status | Source (fetched this run) |
|---|---|---|---|

### Gaps versus the deck (present on the source page, absent from the deck)
| Item | Source page | Target slide | Note |
|---|---|---|---|

### Items detected but not applied
| Item | Reason |
|---|---|

### Verify before presenting
- …

### Preview features at edition date
…
-->
