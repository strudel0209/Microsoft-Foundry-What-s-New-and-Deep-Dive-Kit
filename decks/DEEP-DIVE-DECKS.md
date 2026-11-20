# Deep-dive decks · register

One entry per deep-dive deck edition, newest first. Since kit skills 1.2.0, deck files are named
`Microsoft Foundry <Subject>.pptx` without a date; older entries keep their original headings. Maintained by the `azure-ai-deep-dive-deck`
skill (path in `kit.yaml` → `paths.deep_dive_register`); entries are appended, never rewritten.
A new edition of a deck gets a new dated file and a new entry — the previous edition is the
rollback. `Conformance` states whether the deck meets the skill version named.

---

## Microsoft Foundry Microsoft IQ · edition 2026-11

**Kit file:** `Microsoft Foundry Microsoft IQ.pptx` · **Sources verified:** 2026-11-18 · **Slides:** 18
**Pairs with:** none yet (related: notebook 9 Foundry IQ knowledge base and Fabric IQ ontology, notebook 10 step 12 knowledge base retrieval)
**Sources:** learn.microsoft.com/microsoft-iq · azure/search/whats-new · search/agentic-retrieval-overview · search/agentic-retrieval-how-to-retrieve · search/agentic-knowledge-source-overview · azure/foundry/agents/how-to/foundry-iq-connect · microsoft-365/copilot/extensibility/work-iq · fabric/iq/overview · fabric/iq/connectors/fabric-iq-mcp · web-iq/resources/faq · web-iq/reference/auto · news.microsoft.com/events/ignite/2026/book-of-news · Microsoft Azure and Microsoft 365 blogs and Tech Community posts of November 2026 · github.com/microsoft/iq-series
**Conformance:** skill 1.4.0 — `deck_qa.py` 0 FAIL on the build (remaining warnings are notes-length and "Presenter note" checks tuned for the what's-new deck; deep-dive notes are 183–200 words with "Presenter note: verify …" lines by rule); one fix pass, every slide inspected as a rendered image. Covers Microsoft IQ (generally available at Ignite 2026) and its layered architecture; Foundry IQ in depth (Azure AI Search renamed Foundry IQ with the same resource provider, endpoints, APIs, roles and meters; knowledge sources; agentic retrieval and reasoning effort; Foundry Agent Service integration over the knowledge base MCP endpoint; permissions and network boundaries; November updates); Work IQ and Fabric IQ architectures; Web IQ APIs, crawling and index engine, data security and Zero Query Logging; a comparison of the four, Microsoft IQ in one Foundry agent and selection guidance. Named with "Microsoft IQ" in full so it is not mistaken for a Foundry IQ deck. Kit copy built without a presenter line. The kit copy carries a Microsoft sensitivity label with encryption applied in OneDrive (see `kit.yaml` → `known_issues`)
**Open verify items:**
- Foundry IQ Serverless tier status: the what's-new page says generally available, two November blogs say December 2026.
- Behaviour when the user token (`x-ms-query-source-authorization`) is missing: the connect page and the retrieve page describe it differently.
- Rollout date of the managed Foundry IQ option in every new Foundry project.
- Work IQ memory and content creation status: the Book of News says generally available, the Azure blog says preview.
- Name and status of the Foundry tool for Fabric IQ, as the Fabric data agent tool is being replaced.
- Current name of the Foundry web search tool, which some pages still call Grounding with Bing.
- Harrier retrieval model and DiskANN naming come from blogs only; check Learn before presenting.
- Preview items on the status slide (18), several of which are expected to change in December 2026.

## Microsoft Foundry Latency Optimization for Models and Agents · edition 2026-11

**Kit file:** `Microsoft Foundry Latency Optimization for Models and Agents.pptx` · **Sources verified:** 2026-11-14 · **Slides:** 18
**Pairs with:** none yet (related: notebook 1 priority processing, notebook 4 prompt caching, notebook 8 semantic caching)
**Sources:** learn.microsoft.com/azure/foundry/openai/how-to/latency · concepts/priority-processing · how-to/flex-processing · concepts/provisioned-throughput · how-to/spillover-traffic-management · how-to/prompt-caching · how-to/predicted-outputs · how-to/reasoning · concepts/model-router · how-to/responses · how-to/realtime-audio-webrtc · how-to/decisions · concepts/content-streaming · monitor-openai-reference · foundry-models/concepts/deployment-types · azure/foundry/agents/overview · agents/concepts/hosted-agents · agents/how-to/optimize-hosted-agent-latency · agents/how-to/debug-hosted-agent · agents/concepts/toolbox-overview · agents/how-to/tools/model-context-protocol · agents/how-to/tools/agent-to-agent · agents/concepts/tool-best-practice · observability/concepts/trace-agent-concept · observability/how-to/how-to-monitor-agents-dashboard · agent-framework/workflows/orchestrations · agent-framework/concepts/harness · agent-framework/agents/observability · azure/search/agentic-retrieval-overview · search/agentic-retrieval-how-to-set-retrieval-reasoning-effort · azure/api-management/genai-gateway-capabilities · api-management/llm-semantic-cache-lookup-policy · azure/architecture/ai-ml/guide/ai-agent-design-patterns · ai-ml/guide/generative-ai-gateway · ai-ml/architecture/baseline-microsoft-foundry-chat · azure/well-architected/ai/application-design · devblogs.microsoft.com/foundry · github.com/microsoft/agent-framework/releases
**Conformance:** skill 1.2.0 — `deck_qa.py` 0 FAIL, 0 WARN after two QA passes; every slide inspected as a rendered image. Generic deck built after a customer latency review; no customer name, data or measured results on slides or in speaker notes. Covers sources of latency, the request path of the baseline Microsoft Foundry chat architecture (Azure Architecture Center), model-call features, capacity options, five decision trees (model, capacity, orchestration pattern, agent runtime and framework, tools and protocols), observability and latency budgets, and an optimization path. Presenter line removed from the kit copy on 2026-11-14. The kit copy carries a Microsoft sensitivity label with encryption applied in OneDrive (see `kit.yaml` → `known_issues`)
**Open verify items:**
- Which deployment types show the Time to Response and time-between-tokens metrics in Azure Monitor (slide 5).
- Which small models accept reasoning effort "none" (slide 8).
- Priority processing model-version prerequisite against the gpt-4.1 rows of its latency-target table (slides 7, 17).
- Status of invocations over WebSocket for hosted agents and of the AI gateway in Foundry (slides 12, 17).
- Features with no explicit generally-available wording on Learn are shown without an asterisk; recheck before presenting.
- Workflows in the Foundry portal retire on 1 December 2026: remove that row (slides 12, 17) after that date.

## Microsoft Foundry Fabric IQ Ontologies for Agents · edition 2026-11

**Kit file:** `Microsoft Foundry Fabric IQ Ontologies for Agents.pptx` · **Sources verified:** 2026-11-04 · **Slides:** 17
**Pairs with:** none yet
**Sources:** learn.microsoft.com/fabric/iq/ontology/overview · resources-glossary · how-to-bind-data · concepts-agent-integration · how-to-create-agent-foundry-iq · how-to-create-agent-copilot-studio · how-to-use-ontology-mcp-server · how-to-use-ontology-graph · fabric/onelake/unify-data · fabric/data-science/ai-functions/overview · fabric/data-science/data-agent-microsoft-copilot-studio-tool · azure/foundry/agents/concepts/what-is-foundry-iq · azure/foundry/agents/how-to/tools/fabric-iq · azure/foundry/agents/how-to/tools/work-iq · azure/foundry/agents/how-to/publish-copilot · azure/search/agentic-knowledge-source-how-to-onelake · microsoft-iq · web-iq/overview · webiq.microsoft.ai documentation (Web IQ APIs)
**Conformance:** skill 1.2.0 — `deck_qa.py` 0 FAIL on the build; two review rounds with the presenter, applied in place on the live deck; every changed slide inspected as a rendered image. First built for a customer architecture session; the kit copy is customer-neutral (customer name removed from slides and speaker notes on 2026-11-05) and the demo storyline (slide 14) uses a synthetic venue-operations scenario. Covers whether ontologies can use unstructured or non-Fabric data: ontology binding reads seven Fabric source types only; data held elsewhere reaches OneLake through mirroring or shortcuts; documents reach agents through AI functions extraction (facts as tables) and a Foundry IQ knowledge base (full text), side by side with the ontology
**Open verify items:**
- Fabric data agent tool in Foundry Agent Service is deprecated on 6 November 2026; check that the Fabric IQ tool (slides 10, 16) has left preview or kept its status.
- Old ontology experience retires on 31 January 2027 (slide 16); recheck before presenting after that date.
- Document-level permissions on the indexed OneLake knowledge source exist only in REST 2026-08-01-preview (slides 12, 16); check for a generally available API version.
- Ontology MCP endpoint does not accept service principals (known issue on Learn, slide 12); recheck the known-issues page.
- Web IQ is limited access and needs a paid Azure subscription; the Auto API is beta (slide 4).
- Speaker notes on the agenda slide reference slide numbers of the 17-slide edition; recheck if slides are merged (slides 10–11 and 16 were offered for consolidation).

## Microsoft Foundry Copilot Harness Prompt Agents · edition 2026-10

**Kit file:** `Microsoft Foundry Copilot Harness Prompt Agents.pptx` (renamed on 2026-10-30, before its first commit, under kit skills 1.2.0) · **Sources verified:** 2026-10-29 · **Slides:** 7
**Pairs with:** none yet
**Sources:** learn.microsoft.com/azure/foundry/agents/how-to/use-tools-skills-copilot-harness · concepts/limits-quotas-regions · concepts/prompt-agents · concepts/hosted-agents · agents/overview · devblogs.microsoft.com/foundry/microsoft-copilot-harness-in-foundry · blogs.microsoft.com/blog/2026/10/28/introducing-the-microsoft-copilot-harness-unlocking-the-potential-of-truly-multi-model-agentic-work
**Conformance:** skill 1.1.0 — `deck_qa.py` 0 FAIL, 0 WARN; every slide inspected as a rendered image. Shortened 30-minute arc by request (6–7 slides): no agenda slide; overview, architecture, comparison, selection, limits and references. The architecture diagram follows the documented components, because no Azure Architecture Center pattern exists for the harness yet
**Open verify items:**
- Prompt-agent column on slide 4 ("tools such as Code Interpreter run in their own environment"): the prompt-agents concept page could not be fetched in full during the build.
- Harness regions, models and request constraints on slide 6: preview values, likely to change.
- Sandbox pricing from 2026-12-01 (Foundry Blog announcement) against the Foundry pricing page once published.

## guardrails-tuning-deep-dive-2026-10 · edition 2026-10

**Kit file:** `Microsoft Foundry Guardrails - Tuning Without Over-Blocking.pptx` (legacy name) · **Sources verified:** 2026-10-11 · **Slides:** 14
**Pairs with:** notebook 1 (guardrails section)
**Replaces:** the earlier build of the same kit file (10 slides, "-V4"), not made with the kit skills; same message and test data, restructured into the kit design, with speaker notes on every slide; the previous version stays in git history
**Sources:** learn.microsoft.com/azure/foundry/guardrails/guardrails-overview · guardrails/how-to-create-guardrails · openai/concepts/content-filter-severity-levels · openai/how-to/responses · concepts/evaluation-evaluators/risk-safety-evaluators · observability/how-to/cloud-evaluation · observability/how-to/evaluation-dataset-synthetic · learn.microsoft.com/azure/foundry-classic/openai/how-to/content-filters · github.com/strudel0209/foundry-content-safety-eval (test data: 266 question-and-model pairs, gpt-5.4-mini and gpt-5.6-sol, HighestBlocking / MediumBlocking / LowestBlocking)
**Conformance:** skill 1.0.1 — `deck_qa.py` 0 FAIL, 2 WARN (status headings on the status slide, allowed); every slide inspected as a rendered image
**Open verify items:**
- Portal blocking labels (Lowest / Medium / Highest blocking) against the API thresholds: read from the portal during the test; the documentation describes the direction inconsistently.
- Preview status of synthetic evaluation dataset generation: the page lost its preview label on 2026-10-08, while the evaluation data source type still carries a preview name.
- Intervention points per risk for agents (indirect attacks on tool responses; protected material on output only), which are still preview.

## hosted-agents-deep-dive-2026-10 · edition 2026-10

**Kit file:** `Microsoft Foundry Hosted Agents.pptx` (legacy name) · **Sources verified:** 2026-10-09 · **Slides:** 7
**Pairs with:** notebooks 2 and 3
**Sources:** learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents · how-to/deploy-hosted-agent · concepts/limits-quotas-regions · how-to/virtual-networks · add-hosted-agent-guardrails · agents/overview
**Conformance:** skill 1.0.0 — `deck_qa.py` 0 FAIL, 0 WARN
**Open verify items:**
- Which identity pulls the container image (project managed identity or agent identity — pages differ).
- Status of skills for hosted agents.
- Per-hour rates on the Foundry Agent Service pricing page (not published for the default region on 2026-10-09).
- Whether the agent endpoint is private when deployed with azd (pages differ).

## ai-gateway-deep-dive-2026-10 · edition 2026-10

**Kit file:** `Microsoft Foundry AI Gateway.pptx` (legacy name) · **Sources verified:** 2026-10-03 · **Slides:** 9
**Pairs with:** notebook 8
**Sources:** learn.microsoft.com/azure/api-management/genai-gateway-capabilities · llm-token-limit-policy · llm-emit-token-metric-policy · mcp-server-overview · agent-to-agent-api · azure/foundry/configuration/enable-ai-api-management-gateway-portal · agents/how-to/tools/governance · control-plane/register-custom-agent · guardrails/guardrails-overview · github.com/Azure-Samples/foundry-citadel-platform
**Conformance:** kept as published by owner decision (2026-10-11); speaker notes on slides 3 and 4 predate wording rule 4 — apply it in the next edition
**Open verify items:**
- AI Gateway in Foundry status (configuration page has no preview label; readiness table marks it preview).
- Whether semantic caching or content safety policies can be added to model traffic managed by the Foundry gateway.
- Whether Foundry agents' own model calls route through the gateway.
- `llm-token-limit` sample values against the policy reference.
- API Center MCP registry status; bring-your-own-model status; guardrail status for agents.
- Citadel repository and aka.ms/ai-hub-gateway links still current.

## voice-live-voice-agents-deep-dive-2026-10 · edition 2026-10

**Kit file:** `Microsoft Foundry Voice Live-Voice Agents.pptx` (legacy name) · **Sources verified:** 2026-10-02 · **Slides:** 9
**Pairs with:** notebook 7
**Sources:** learn.microsoft.com/azure/ai-services/speech-service/voice-live · voice-live-how-to · voice-live-api-reference-2026-07-15 · voice-live-faq · how-to-voice-agent-integration · speech-services-quotas-and-limits · regions · azure/foundry/agents/how-to/configure-voice-agent · voice-agent-telephony-channels
**Conformance:** skill 1.0.0 — `deck_qa.py` 0 FAIL (two status cells on the status slide, allowed)
**Open verify items:**
- Per-token prices on the Azure Speech pricing page.
- Voice agent property names (preview) against configure-voice-agent.
- SDK signature against the current azure-ai-voicelive release.
- Migration guide live on Learn (published on GitHub on 2026-09-30).
- Region and quota tables on the day.

## content-understanding-deep-dive-2026-09 · edition 2026-09-30

**Kit file:** `Microsoft Foundry Content-Understanding.pptx` (legacy name) · **Edition date:** 2026-09-30 · **Slides:** 12
**Pairs with:** notebook 6
**Sources:** learn.microsoft.com/azure/ai-services/content-understanding/overview · concepts/analyzer-reference · concepts/prebuilt-analyzers · concepts/agentic-mode · document/analyzer-improvement · choosing-right-ai-tool · pricing-explainer · service-limits · quickstart/use-rest-api
**Conformance:** kept as published by owner decision (2026-10-11); built before the slide-wording rules — apply skill 1.0.0 in the next edition

## a2a-deep-dive-2026-09 · edition 2026-09-18

**Kit file:** `Microsoft Foundry Agent2Agent-A2A.pptx` (legacy name) · **Edition date:** 2026-09-18 · **Slides:** 21
**Pairs with:** notebook 5
**Sources:** a2a-protocol.org/latest/specification · topics/what-is-a2a · life-of-a-task · agent-discovery · streaming-and-async · a2a-and-mcp · github.com/a2aproject/A2A · Microsoft Learn Foundry A2A pages
**Conformance:** kept as published by owner decision (2026-10-11); built before the slide-wording rules — apply skill 1.0.0 in the next edition

---

<!-- Template — copy, fill in, insert directly under the header (newest first).

## Microsoft Foundry <Subject> · edition <yyyy>-<mm>[-<dd>]

**Kit file:** `Microsoft Foundry <Subject>.pptx` · **Sources verified:** <yyyy-mm-dd> · **Slides:** <n>
**Pairs with:** notebook <n> | none yet
**Sources:** <Learn and GitHub paths fetched during the build>
**Conformance:** skill <version> — `deck_qa.py` <n> FAIL, <n> WARN
**Open verify items:**
- …
-->
