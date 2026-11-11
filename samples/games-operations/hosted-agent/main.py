"""Games operations hosted agent — Microsoft Agent Framework, Responses protocol.

Notebook 9 step 5c imports this module and runs `agent` in the notebook process, as the signed-in user.
Deployed as a hosted agent, the same code runs as the agent's own identity; the ontology endpoint doesn't
accept service principals, so read README.md (production identity options) before deploying.

The code owns what each tool returns: the ontology answer as the caller sees it, and document passages
from Current documents only, each with its document ID. The model decides when to call each tool.
"""
import json
import os
from datetime import timedelta
from typing import Annotated

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# FOUNDRY_PROJECT_ENDPOINT is injected by the hosted runtime; the notebook sets the other values from .env.
project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME") or os.environ["FOUNDRY_MODEL_NAME"]
ONTOLOGY_MCP_URL = (f"https://api.fabric.microsoft.com/v1/mcp/dataPlane/workspaces/{os.environ['FABRIC_WORKSPACE_ID']}"
                    f"/items/{os.environ['FABRIC_ONTOLOGY_ID']}/ontologyEndpoint")
DOCS_KS = os.environ.get("GAMES_DOCS_KS", "games-docs-ks")
CURRENT_ONLY = "document_status eq 'Current'"
TOOL_TIMEOUT_SECONDS = 90

credential = DefaultAzureCredential()
kb_client = KnowledgeBaseRetrievalClient(endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
                                         knowledge_base_name=os.environ.get("GAMES_AGENT_KB", "games-agent-kb"),
                                         credential=credential, api_version="2026-08-01-preview",
                                         retry_total=0, connection_timeout=10, read_timeout=TOOL_TIMEOUT_SECONDS)


async def ask_ontology(
    question: Annotated[str, "Question in business terms, for example 'Which Critical assets are overdue for service?'"],
) -> str:
    """Ask the Games Operations ontology about venues, sessions, athletes, assets, findings, business rules and live readings."""
    token = await credential.get_token("https://api.fabric.microsoft.com/.default")
    headers = {"Authorization": f"Bearer {token.token}",
               "x-ms-fabric-skill": "fabriciq-ontology-cli"}
    async with streamablehttp_client(
        ONTOLOGY_MCP_URL, headers=headers, sse_read_timeout=TOOL_TIMEOUT_SECONDS,
    ) as (read, write, _):
        async with ClientSession(
            read, write, read_timeout_seconds=timedelta(seconds=TOOL_TIMEOUT_SECONDS),
        ) as session:
            await session.initialize()
            result = await session.call_tool("ask_ontology", {"request": question})
    text = "\n".join(content.text for content in result.content if content.type == "text")
    if result.isError:
        raise RuntimeError(f"Ontology tool failed: {text}")
    return text


async def search_current_documents(
    query: Annotated[str, "What to look up in venue manuals, inspection reports, transport plans and policies"],
) -> str:
    """Search the operating documents. Only documents with status Current are searched; every passage comes with its document ID."""
    result = (await kb_client.retrieve(retrieval_request={
        "intents": [{"type": "semantic", "search": query}],
        "knowledgeSourceParams": [{"knowledgeSourceName": DOCS_KS, "kind": "searchIndex", "filterAddOn": CURRENT_ONLY,
                                   "includeReferences": True, "includeReferenceSourceData": True}],
        "retrievalReasoningEffort": {"kind": "minimal"},
        "outputMode": "extractiveData",
    })).as_dict()
    passages = " ".join(content.get("text", "") for message in result.get("response", [])
                        for content in message.get("content", []))
    sources = [ref.get("sourceData") or ref.get("source_data") or {} for ref in result.get("references", [])]
    return json.dumps({"passages": passages[:8000], "sources": sources}, ensure_ascii=False)


chat_client = FoundryChatClient(project_endpoint=project_endpoint, model=model, credential=credential)
chat_client.client.max_retries = 0
chat_client.client.timeout = TOOL_TIMEOUT_SECONDS

agent = Agent(
    client=chat_client,
    name="games-ops-hosted",
    instructions=(
        "You are the operations assistant of the Valmont Winter Games operations centre. "
        "Call ask_ontology for venues, sessions, athletes, assets, findings, business rules and live readings. "
        "Call search_current_documents for procedures, operating limits and inspector wording; when a question needs "
        "both, rewrite an ontology-only question for operational facts and session, asset, finding and report IDs. "
        "Explicitly exclude document retrieval and inspector recommendations from that ontology question. "
        "Then search the documents with the identifiers it returned and combine the evidence. "
        "Cite every document by the document_id in the sources list (for example DOC-MAN-V07-21). "
        "Answer in at most six sentences. If the tools don't return the answer, say you don't know."
    ),
    tools=[ask_ontology, search_current_documents],
)

if __name__ == "__main__":
    from agent_framework_foundry_hosting import ResponsesHostServer   # provided by agent-framework-foundry-hosting

    ResponsesHostServer(agent).run()      # serves the Responses protocol on port 8088
