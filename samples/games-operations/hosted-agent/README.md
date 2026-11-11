# Games operations hosted agent

The hosted agent of notebook 9, step 5c: a Microsoft Agent Framework agent with two function tools.

| Tool | What the code controls |
|---|---|
| `ask_ontology` | Calls the `GamesOperationsOntology` Model Context Protocol (MCP) endpoint as the caller and returns its answer |
| `search_current_documents` | Retrieves passages from the `games-agent-kb` knowledge base with the filter `document_status eq 'Current'`, each with its document ID |

The model decides when to call each tool. The filter and the source list are fixed in code, which a prompt agent
can't do through the knowledge base MCP tool.

## Run it in the notebook

Notebook 9 imports `main.py` and calls `agent.run(...)` in its own Python process, with your `az login` identity.
No deployment is needed for the demo or for the evaluation in step 6.

The comparison gives each agent run a 180-second client deadline and saves each start/result to a unique
`output/eval/nb9-agent-comparison-*.jsonl` journal (relative to `samples/games-operations`).
Answers and explicit timeout/tool-error statuses appear immediately, rather than after all nine runs.
After a kernel restart, load the printed journal path with
`pd.read_json(path, lines=True).drop_duplicates(["question", "agent"], keep="last")`.
A remaining `running` row has no saved terminal result; it is not evidence that remote work is still active.

The function tools use async credentials and SDK calls so the comparison's deadline can cancel pending I/O.
Ontology MCP requests have a separate 90-second deadline, including initialization; model and Search SDK
request retries are disabled. The model or remote harness can still decide to make another tool call.
Client cancellation does not guarantee cancellation of work already running in Fabric or Foundry.
Minimal Search retrieval uses semantic `intents` (not `messages`), while preserving the code-enforced
Current-only filter. Tool failures are reported separately from answers and are rejected by the hosted evaluation cell.

## Deploy it (optional)

```bash
cd samples/games-operations/hosted-agent
azd env set FOUNDRY_PROJECT_ENDPOINT https://<account>.services.ai.azure.com/api/projects/<project>
azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME <chat-deployment>
azd env set AZURE_SEARCH_ENDPOINT https://<service>.search.windows.net
azd env set FABRIC_WORKSPACE_ID <workspace-id>
azd env set FABRIC_ONTOLOGY_ID <ontology-id>
azd up
```

After deployment, give the agent identity **Search Index Data Reader** on the search service.

Deployed, the agent runs as its own identity, a service principal. As per official documentation, the ontology
MCP endpoint doesn't accept service principals, so `ask_ontology` fails until one of these options is in place.

| Option | How the ontology call is authorised | Status | Trade-off |
|---|---|---|---|
| OAuth connection in a toolbox | Each user signs in once to a custom Microsoft Entra app with the Power BI delegated permissions `Item.Execute.All` and `Item.Read.All` (admin consent); the toolbox stores the user's token per connection; `ask_ontology` is replaced by the toolbox through `FoundryToolbox` | Works today for hosted agents | One-time app registration and tenant admin consent |
| Agent on behalf of user | The agent blueprint token represents the user and the agent; Conditional Access applies | Preview; direct runtime clients only | Not available through Teams or Microsoft 365 Copilot channels, or for direct toolbox access |
| Fabric data agent over the ontology | The data agent MCP endpoint accepts service principal tokens | Works today | Answers as the application, so per-user row-level security is lost |

Sources:
- https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/fabric-iq
- https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/use-toolbox-hosted-agent
- https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/tools/foundry-toolbox
