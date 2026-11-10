# Demo notebooks · changelog

One entry per notebook change or dependency audit, newest first. Maintained by the
`deck-companion-notebook` skill (path in `kit.yaml` → `paths.notebooks_changelog`); entries are
appended, never rewritten. Deck editions are logged in `decks/CHANGELOG.md`, not here.

**Last dependency audit:** none yet — run *"check the kit's dependencies"* before the next customer session.

---

## 2026-11-09 · foundry-demo-9-fabric-iq-and-foundry-iq-agents.ipynb — added (steps 0–4)

**Paired deck:** Microsoft Foundry Fabric IQ and Foundry IQ Agents.pptx (in preparation, not yet in decks/) · slide map: step headings name deck sections until the slides exist — step 1 → section 2, step 2 → section 2, step 3 → section 4, step 4 → section 3. Run DECK REFRESH MODE once the deck is built
**Change:** new notebook over the `samples/games-operations` sample (fictional Valmont Winter Games). Step 0 settings and the sample's register and questions; step 1 ontology MCP endpoint (preview): tool list and Q12; step 2 Fabric IQ MCP (GA): tool list and a discovery call; step 3 OneLake indexer → Content Understanding skill (fixed-size chunks with page numbers) → Azure OpenAI embedding skill → index projections → `games-docs` index, with a fallback to built-in PDF extraction plus Text Split when no chunks are produced, then register fields (type, venue, version, status, sensitivity) merged into every chunk; step 4 search index, indexed OneLake and Fabric ontology knowledge sources in one knowledge base, compared per source (Q09, Q13, Q10, Q17; Q05, Q12, Q11) and per reasoning effort (Q11 at low, medium, and minimal on documents only); cleanup cell off by default. Steps 5–11 (agents, evaluations, permissions, Work IQ, publishing, Copilot Studio, API Management) follow
**Dependency changes:** `azure-search-documents>=11.6.0` → `>=12.1.0b2,<12.2` (pre-release for REST API 2026-08-01-preview; untested — written against 12.1.0b2). Breaking changes reviewed 11.6.0 → 12.1.0b1: model `serialize`/`deserialize` removed, `EntityRecognitionSkill`/`SentimentSkill` removed, `SearchIndexerDataSourceType.ONE_LAKE` → `ONELAKE`, `SearchIndexerDataSourceConnection.connection_string` → `credentials` (12.1.0b1) — no existing notebook imports `azure.search` (the checker's `connection_string` keyword hit in NB1 cell 21 is `configure_azure_monitor`, not the search client). `mcp>=1.10.0` → `>=1.10.0,<2`: mcp 2.0 removed `streamablehttp_client`, which NB1, NB8 and NB9 use; the cap fixes a latent break of NB1 and NB8 on a fresh install. Added `-r samples/games-operations/requirements.txt` (closes the known issue; its `pandas>=2.0` overlaps the root `pandas>=2.2`, ranges intersect)
**Env changes:** added `AZURE_SEARCH_ENDPOINT`, `FABRIC_WORKSPACE_ID`, `FABRIC_LAKEHOUSE_ID`, `FABRIC_ONTOLOGY_ID`, `FABRIC_DOCS_FOLDER` (optional); reused `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL_NAME`, `FOUNDRY_EMBEDDING_NAME` with identical meaning; nothing renamed or removed
**Regression:** 9/9 notebooks compile; NB9 passes the static gate; findings otherwise unchanged from the pre-edit baseline (pre-existing: NB5 per-package installs in cells 2 and 23; the two agent `-r` includes not present in the checked copy) plus one new informational overlap warning (pandas) · resolver: resolved by reading, not executed · new notebook not executed against Azure
**Open verify items:** Fabric token scopes for the ontology MCP endpoint and Fabric IQ MCP; whether the OneLake indexer passes `file_data` to the Content Understanding skill; `project.deployments.get(...).model_name`; `api_version` keyword on `KnowledgeBaseRetrievalClient`; `fabricOntology` kind inside `knowledgeSourceParams` (documented on the preview class page)
**Last dependency audit:** none yet

## 2026-10-26 · foundry-demo-1-what-is-new.ipynb — updated (step 2b, Decisions API)

**Paired deck:** Microsoft-Foundry-Whats-New-2026-10-26.pptx · edition 2026-10-26 · slide map: step 2b → slide 11 (decision models). Other steps keep their edition 2026-10 slide numbers (see `kit.yaml` → `known_issues`)
**Change:** new optional step 2b after Priority Processing (one markdown and one code cell). One Decisions API request to a `gpt-6-luna` deployment asks a predicate, a choice and a score question about a support message and prints the typed answers, handling refusals. Calls the resource route `https://<account>.services.ai.azure.com/openai/v1/` with a Microsoft Entra ID token; the step is skipped when `FOUNDRY_DECISIONS_NAME` is empty. Microsoft-Decision-1 (preview) is mentioned only, not demonstrated. Added the optional deployment to the "Before you start" list.
**Dependency changes:** `openai>=3.0.0` → `openai>=3.26.0,<4` (the `decisions` resource needs 3.26.0 or later as per official documentation; major-version cap per the kit pin policy). Breaking changes reviewed between 3.0.0 and 3.37.0: the 3.37.0 Decisions type change keeps string instructions and user-message inputs (step 2b uses only those); the 3.1.0 MCP tool-call error change touches no notebook; the 3.0.0 HTTPX2 change was already absorbed (floor 3.0.0, `httpx` pinned). The long-running agent's own `openai>=3.0.0` stays compatible
**Env changes:** added `FOUNDRY_DECISIONS_NAME` (optional, notebook 1); no existing variable reused or renamed
**Regression:** 8/8 notebooks parse; static gate unchanged from the pre-edit baseline (2 FAIL, 30 WARN, 27 INFO, all pre-existing) except one informational overlap warning: `openai` is specified in both the root and the long-running agent requirements, and the two ranges intersect · pre-existing: notebook 5 per-package installs (cells 2 and 23) · resolver: resolved by reading, not executed · new step not executed against Azure
**Open verify items:** `decision.usage.total_tokens` attribute in the Python library; whether the Foundry User role covers the `/openai/v1/decisions` route (the v1 API documentation names Cognitive Services OpenAI User); Decisions API region rollout for the demo resource
**Last dependency audit:** none yet

## 2026-10-15 · notebook 8 — reuse notebook 5's Foundry A2A target through the gateway

**Paired deck:** Microsoft Foundry AI Gateway · step 8, slide 7
**Dependency changes:** none; tests use the Python standard library
**Env changes:** added `A2A_PROTOCOL_VERSION=1.0`; step 8a reuses `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_A2A_TARGET_AGENT`. Documented all-or-none gateway settings, authenticated card import, subscription requirements and the gateway identity's Foundry Agent Consumer role.
**Behavior:** version-matched 1.0 requests by default; explicit preview 0.3 compatibility without automatic downgrade. Checks native A2A API type, gateway URLs, rewritten card interfaces, completed JSON-RPC task state and the policy-linked glass artifact. Preserves original routing/inheritance with XML-based policy composition, applies per-subscription/API POST limits and Content Safety, and adds managed-identity backend authentication for `https://ai.azure.com`. Discovery does not consume the demo's POST budget. The optional 12-request burst is billable and requires a policy-specific retry header to confirm throttling. Documents manual concierge connection rewiring separately from model-call governance in 8b.
**Regression:** 16 offline unit tests pass against the notebook's actual cells, covering both protocol shapes, partial/unsafe settings, policy backup/reapplication, self-closing inbound sections, discovery bypass, HTTP/JSON-RPC failures, artifact checks, safety evidence and burst outcomes. Static gate findings are unchanged from the pre-edit baseline: 2 FAIL, 33 WARN, 27 INFO; no new findings.
**Open verify items:** live authenticated import, native APIM A2A 1.0 compatibility, RBAC, card rewriting and actual Content Safety/rate-limit enforcement must be rehearsed on the target non-production gateway. No Azure resources, connections or role assignments were changed during development.

## 2026-10-11 · notebooks 1 and 8 — environment and documentation consistency

**Paired decks:** Microsoft Foundry what's-new edition 2026-10 and Microsoft Foundry AI Gateway
**Dependency changes:** none; corrected the shared requirements header to notebooks 1–8
**Env changes:** notebook 8 now reads `APIM_RESOURCE_GROUP`; `AZURE_RESOURCE_GROUP` is Foundry-only. Both retain the shared `AZURE_SUBSCRIPTION_ID`, with all kit resources in one subscription. Consolidated `FOUNDRY_PROJECT_NAME` into one blank setting (notebook 1 derives its default from the endpoint; notebook 7 requires a value for Voice Live with an agent). Documented the optional, endpoint-derived `FOUNDRY_ACCOUNT_NAME` override.
**Resolved baseline findings:** the `FOUNDRY_ACCOUNT_NAME` example-file omission and the Foundry/APIM resource-group collision below are no longer open. The baseline entry is retained as history.
**Documentation:** corrected notebook 1's environment-derived ARM IDs and connection-name prerequisites; replaced notebook 2's obsolete gateway URL instructions with notebook 8's `INFERENCE_API_STYLE` contract; aligned kit branding and hosted Python 3.13 runtime references.
**Migration:** move the existing APIM resource-group value to `APIM_RESOURCE_GROUP`, set `AZURE_RESOURCE_GROUP` to the Foundry group, and keep one shared subscription and one project-name setting.
**Regression:** 8/8 notebooks pass the static syntax checks; focused runtime checks pass for separate resource groups in one subscription, blank/unset/explicit account and project names, missing APIM settings, and both gateway URL styles. YAML manifests and skill frontmatter parse and agree. The full static gate remains FAIL with the same two pre-existing per-package install findings in notebook 5 (cells 2 and 23), 29 WARN and 27 INFO; no new findings. Dependency resolver and live Azure calls were not run.

## 2026-10-11 · baseline — eight notebooks registered

**Paired decks:** see `kit.yaml` → `notebooks` (notebook 1 ↔ what's-new edition 2026-10; notebooks 2–8 ↔ deep-dive decks)
**Dependency changes:** none (baseline)
**Env changes:** none (baseline); collisions recorded in `kit.yaml` → `env`
**Regression:** static gate `scripts/kit_check.py` over 8/8 notebooks on the OneDrive kit copy — verdict FAIL (4 FAIL, 29 WARN, 27 INFO), all pre-existing. The owner then removed notebook 2's gateway section and cleared all outputs (repository commit of 2026-10-11), which resolves the notebook 2 findings below; re-run the gate on the repository to confirm · resolver: resolved by reading, not executed · notebooks not executed against Azure
**Pre-existing FAILs:**
- notebook 1, cell 2: `FOUNDRY_ACCOUNT_NAME` read but missing from `.env.example`
- notebook 5, cells 2 and 23: per-notebook `%pip install` (one floors `azure-ai-projects>=2.5.0` against the root `>=2.7.0,<3`)
**Notable WARNs:** env collision `AZURE_RESOURCE_GROUP` (notebooks 1 and 8); preview surfaces in notebook 1 without a minor cap on `azure-ai-projects`; requirements without notebook tags. Resolved by the owner's changes: `APIM_GATEWAY_URL` collision and `APIM_SUBSCRIPTION_KEY` (notebook 2 gateway removed), stored outputs (cleared)
**Open verify items:** `# verify` lines — notebook 1: 2, notebook 2: 3
**Next free notebook number:** 9

<!-- Template — copy, fill in, insert directly under the separator (newest first).

## <yyyy-mm-dd> · foundry-demo-<n>-<topic>.ipynb — added | updated
**Paired deck:** <file> · edition <yyyy-mm> · slide map: step 1 → slide <x>; step 2 → slides <y, z>; …
**Dependency changes:** <package old → new, or none>
**Env changes:** <variable added/reused, or none>
**Regression:** <n>/<n> notebooks pass static gate · pre-existing: <list or none> · resolver: executed | resolved by reading, not executed · new notebook not executed against Azure
**Open verify items:** <list or none>
**Last dependency audit:** <yyyy-mm-dd>
-->
