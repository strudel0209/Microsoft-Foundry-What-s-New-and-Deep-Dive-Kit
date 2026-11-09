"""Render ontology/ontology-design.md from the ontology specification.

Run after changing ontology_spec.py so the design document and the specification stay in step:
    python render_design.py --out ../ontology/ontology-design.md
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ontology_spec as o  # noqa: E402
from reference import CROWD_DENSITY_LIMIT, VENUES  # noqa: E402
from schema import EVENTHOUSE_TABLES, LAKEHOUSE_TABLES  # noqa: E402

INTRO = """# Games operations ontology: design

Design of the Fabric IQ ontology, its data sources and the semantic model for the synthetic
**Valmont Winter Games** sample. The ontology is the semantic layer that Foundry agents, Copilot Studio agents
and Microsoft 365 Copilot use to answer Games-time operations questions over structured data, real-time
telemetry and facts extracted from documents.

> All data is synthetic. National committee codes and country names are public; venues, athletes, assets,
> suppliers, people, thresholds and findings are fictional.

This document is generated from `generator/ontology_spec.py` by `generator/render_design.py`. Change the
specification, not this file, then regenerate.

## 1. Scenario

Games-time operations for a winter multi-sport event with 10 venues in three clusters, 40 medal events,
about 1,300 athletes from 40 national committees, 41 spectator gates and about 220 venue assets.
By default the Games open on **16 November 2026** and the data cut-off is **24 November 2026, 11:00 UTC**
(competition day 9), so the workshop day is "today" in the data.

The ontology must answer questions such as:

| Question | Sources it needs |
|---|---|
| Which venues host sessions tomorrow, and which Critical assets serve them? | Lakehouse through the ontology |
| Which NOCs lead the medal table? What is the attendance rate at a venue? | Semantic model metrics |
| Which gate exceeded the crowd density limit, and for how long? | Eventhouse time series |
| Which sessions are at risk from open High findings, and what did the inspector recommend? | Ontology plus documents |
| What is the wind limit for a venue? (a superseded manual says otherwise) | Documents plus the governed document register |
"""

SOURCES = """## 2. Sources and how each reaches the ontology

| Source | Fabric item | Content | Role in the ontology |
|---|---|---|---|
| Lakehouse | `{lakehouse}` | {n_lh} Delta tables: master data, schedule, results, assets, document register, extracted findings, row-level security mapping | Static entity and relationship bindings |
| Eventhouse | `{eventhouse}` / `{kql}` | {n_eh} tables: venue conditions, gate flow, asset telemetry, live timing | Time series bindings on Venue, Gate, Asset and Athlete |
| Semantic model | `{sm}` (Direct Lake) | All lakehouse tables with keys and relationships; medal, ticketing and attendance measures; row-level security by NOC | Source for **Generate ontology**: entity types, bindings, relationship types and metrics |
| Documents | Lakehouse **Files** | {n_docs} PDF manuals, inspection reports, transport plans and policies | Path A: AI functions extract findings into the `finding` table. Path B: full text indexed for Foundry IQ |

**Why this split.** As per official documentation, ontology binding reads data that is already in Fabric
(eventhouse, KQL database, lakehouse, mirrored database, semantic model, SQL database, warehouse). The ontology is
generated from a Direct Lake semantic model over the lakehouse: generation creates the entity types with data
bindings to the backing lakehouse tables, relationship types (bound when the key of the "one" side is marked), and
metrics from the DAX measures. The semantic model stays the owner of the business calculations and the row-level
security. The eventhouse adds live state as time series bindings, added after generation.

```mermaid
flowchart LR
  subgraph Sources[Synthetic sources]
    G[generate.py] --> CSV[CSV tables]
    G --> PDF[PDF documents]
    SIM[stream_simulator.py] --> ES[Eventstream]
  end
  CSV --> LH[(GamesLakehouse)]
  CSV --> EH[(GamesKQL)]
  ES --> EH
  PDF --> FILES[Lakehouse Files]
  FILES -- AI functions --> LH
  LH --> SM[Games Operations Model]
  SM -- generate: entity types, bindings, metrics --> ONT{{GamesOperationsOntology}}
  LH -. bound tables .-> ONT
  EH -- time series --> ONT
  FILES -- indexed OneLake knowledge source --> KB[Foundry IQ knowledge base]
  ONT -- Fabric Ontology knowledge source --> KB
```
"""


def match_text(n, src, tgt, tb, sk, tk):
    """Origin property and target property that an ontology relationship type matches on."""
    tables = {e["name"]: (e["table"], e["key"]) for e in o.ENTITY_TYPES}
    (st, skey), (tt, tkey) = tables[src], tables[tgt]
    if tb == st:
        return f"{src}.`{tk}` = {tgt}.`{tkey}`"
    if tb == tt:
        return f"{src}.`{skey}` = {tgt}.`{sk}`"
    return f"via `{tb}`: {src}.`{sk}`, {tgt}.`{tk}`"


def entity_section():
    out = ["## 3. Entity types", "",
           "| Entity type | Key | Static binding (lakehouse table) | Time series (eventhouse table) | Description |",
           "|---|---|---|---|---|"]
    for e in o.ENTITY_TYPES:
        ts = ", ".join(f"`{t['table']}` on `{t['key_column']}`" for t in e.get("time_series", [])) or "-"
        extra = ""
        if e.get("secondary_bindings"):
            extra = " + `" + "`, `".join(b["table"] for b in e["secondary_bindings"]) + "` (secondary)"
        out.append(f"| **{e['name']}** | `{e['key']}` (string) | `{e['table']}`{extra} | {ts} | {e['description']} |")
    out += ["", "Entity keys are strings, which the ontology supports as key types (string or integer). "
            "Generation names properties after the source columns; the business names below are aliases used in "
            "this document and in agent instructions. Entry and SessionEvent are their own entity types because "
            "an ontology relationship links two entity types through matching properties.", ""]
    for e in o.ENTITY_TYPES:
        out += [f"### {e['name']}", "", "| Property | Type | Bound column | Description |", "|---|---|---|---|"]
        desc = {c: d for c, _, d in LAKEHOUSE_TABLES[e["table"]]}
        for p in e["properties"]:
            out.append(f"| {p['name']} | {p['type']} | `{e['table']}.{p['column']}` | {desc[p['column']]} |")
        for b in e.get("secondary_bindings", []):
            d2 = {c: d for c, _, d in LAKEHOUSE_TABLES[b["table"]]}
            for p in b["properties"]:
                out.append(f"| {p['name']} | {p['type']} | `{b['table']}.{p['column']}` (joined on "
                           f"`{b['join_column']}`) | {d2[p['column']]} |")
        for t in e.get("time_series", []):
            d3 = {c: d for c, _, d in EVENTHOUSE_TABLES[t["table"]]}
            for p in t["properties"]:
                out.append(f"| {p['name']} | {p['type']} (time series) | `{t['table']}.{p['column']}` | "
                           f"{d3[p['column']]} |")
        out.append("")
    return "\n".join(out)


def relationship_section():
    out = ["## 4. Relationship types", "",
           "Each relationship is bound to the lakehouse table that holds both keys.", "",
           "| Relationship | Source → target | Binding table | Matching properties | Cardinality |",
           "|---|---|---|---|---|"]
    for n, s, t, tb, sk, tk, c in o.RELATIONSHIP_TYPES:
        out.append(f"| {s} **{n}** {t} | {s} → {t} | `{tb}` | {match_text(n, s, t, tb, sk, tk)} | {c} |")
    out += ["", "```mermaid", "erDiagram"]
    for n, s, t, tb, sk, tk, c in o.RELATIONSHIP_TYPES:
        card = {"many-to-one": "}o--||", "one-to-many": "||--o{", "many-to-many": "}o--o{"}[c]
        out.append(f"  {s} {card} {t} : {n}")
    out += ["```", ""]
    return "\n".join(out)


def metrics_section():
    out = ["## 5. Metrics (semantic model measures)", "",
           f"Defined once in **{o.SEMANTIC_MODEL['name']}** and referenced by the ontology as metrics; the "
           "semantic model keeps ownership of the DAX expression.", "",
           "A measure appears as a metric on the entity type of the table it lives on, so medal measures live on "
           "`noc`, ticketing measures on `session` and session counts on `venue`.", "",
           "| Metric | Home table (entity type) | DAX | Format |", "|---|---|---|---|"]
    for n, tb, dax, f, u in o.SEMANTIC_MODEL["measures"]:
        out.append(f"| {n} | `{tb}` ({u}) | `{dax}` | `{f}` |")
    return "\n".join(out) + "\n"


def rules_section():
    out = ["## 6. Rules", "", "Plain-language business rules linked to ontology concepts. The thresholds come from "
           "bound data (for example `Venue.WindLimitMs`), so a rule never hard-codes a value that the documents or "
           "tables own.", "", "| Rule | Statement | References |", "|---|---|---|"]
    for r in o.RULES:
        out.append(f"| **{r['name']}** | {r['statement']} | {', '.join(r['references'])} |")
    return "\n".join(out) + "\n"


def semantic_model_section():
    sm = o.SEMANTIC_MODEL
    out = ["## 7. Semantic model", "",
           f"**{sm['name']}**, Direct Lake on OneLake over `{o.ITEMS['lakehouse']}`, built by "
           "`fabric/03_build_semantic_model.ipynb`. Tables: " + ", ".join(f"`{t}`" for t in sm["tables"])
           + f" (`finding` only when it exists). Hidden: {', '.join(f'`{t}`' for t in sm['hidden_tables'])}.", "",
           "**Key columns** (marked so generation binds relationship types and sets entity type keys): "
           + ", ".join(f"`{t}[{c}]`" for t, c in sm["keys"].items()) + ".", "",
           "| From | To | State |", "|---|---|---|"]
    for a, b, c, d, e in sm["relationships"]:
        out.append(f"| `{a}[{b}]` | `{c}[{d}]` | {e} |")
    out += ["", "Relationships are many-to-one and single direction unless noted. Inactive relationships avoid two "
            "filter paths between the same tables.", "",
            "**Roles (row-level security)**", "", "| Role | Table | Filter | Purpose |", "|---|---|---|---|"]
    for r in sm["roles"]:
        out.append(f"| {r['name']} | {('`' + r['table'] + '`') if r['table'] else '-'} | "
                   f"{('`' + r['filter'] + '`') if r['filter'] else '-'} | {r['note']} |")
    out += ["", "Set the test users in the `TEST_USERS` parameter of the build notebook before the permission test "
            "(evaluation question Q14). Row-level security applies only to users with Viewer-level access.", ""]
    return "\n".join(out)


DOCS = """## 8. Documents and enrichment

| Document type | Count | Ontology use (path A) | Retrieval use (path B) |
|---|---|---|---|
| Venue operations manual | 12 (10 current, 2 superseded) | Document entity; operating limits already bound from `venue` | Wind and crowd procedures, cited |
| Inspection report | about 34 | Findings extracted with AI functions into `finding` → Finding entity | Inspector wording, cited |
| Transport plan | 2 | Document entity | Shuttle and crowd interface procedures |
| Games-wide policy | 3 (one Confidential) | Document entity | Crowd standard, weather procedure, accreditation |

**Authoritative source.** Two venues have a superseded manual (version 1.0) with a looser wind limit than the
current manual (version 2.1). The PDFs both say "Approved", as stale copies in file shares usually do; only
`document_register.document_status` says which one is current. Path B should carry `document_status` and
`sensitivity` from the register into the index as filterable fields, and the agent instructions should prefer
Current documents. Evaluation questions Q09 and Q13 test this.

**Extraction ground truth.** `eval/ground_truth_findings.csv` holds every finding as written into the PDFs. Use
it to score AI functions extraction before binding the `finding` table, or load it directly with
`--include-findings-table` when extraction is not part of the demo.

**Sensitivity.** `document_register.sensitivity` marks which files should receive a Confidential Microsoft
Purview label after upload, so the permission-trimming demo has labelled content to work with.
"""


def scenario_section():
    v = {x[0]: x for x in VENUES}
    return f"""## 9. Scripted situations

The generator plants situations so the demo questions have clear, checkable answers. Identifiers below are
for the default seed and dates; `manifest.json` records them for every run.

| Situation | Where it shows | Evaluation question |
|---|---|---|
| Ski jumping final postponed for wind (day 3) | `session` status, `VenueConditions` gusts above {v['V07'][6]} m/s for about 165 minutes | Q05, Q06 |
| Crowd density spike at gate V01-G2 before an afternoon session (day 8) | `GateFlow` above {CROWD_DENSITY_LIMIT} persons/m² for 14 minutes; follow-up finding in an inspection report | Q07, Q10 |
| Sliding Centre track refrigeration plant degrading (from day 7) | `AssetTelemetry` WARNING then ALARM; open High finding (day 8); asset status Degraded | Q08, Q11, Q17 |
| Alpine Centre safety netting overdue for service | `asset.last_service_date` 40 days before day 1; open Medium finding | Q12 |
| Superseded manuals with looser wind limits (V07, V08) | `document_register` only | Q09, Q13 |
| Live Women's 10 km Pursuit on the workshop day | `stream_simulator.py` → `TimingEvents` | Q15 |
| NOC-restricted test users | `security_noc_user` + semantic model role | Q14 |
"""


BUILD = """## 10. Build steps

1. **Generate** the data locally (`python generator/generate.py --out output`) or in Fabric with
   `fabric/01_load_lakehouse.ipynb` (option B).
2. **Lakehouse.** Create `GamesLakehouse`, upload the sample to `Files/games_ops/`, run
   `fabric/01_load_lakehouse.ipynb`.
3. **Eventhouse.** Create `GamesEventhouse`, run `fabric/02_eventhouse_setup.kql` in its KQL database, ingest the
   CSV files from `output/eventhouse/`. For optional live ingestion, follow the
   [Eventstream-to-Eventhouse walkthrough](../README.md#optional-persist-live-events-in-eventhouse-tables):
   load the simulator connection from the root `.env`, route by `EventType` to `TimingEvents`,
   `VenueConditions` and `GateFlow`, and configure an Eventhouse destination for each route.
   `AssetTelemetry` is historical only; no Eventhouse destination is needed for Eventstream preview.
4. **Findings (path A).** Run `fabric/04_extract_findings.ipynb`: AI functions read the inspection reports, the
   result is scored against `eval/ground_truth_findings.csv` and written to the `finding` table. Optional for the
   first build; without extraction, regenerate with `--include-findings-table`.
5. **Semantic model.** Run `fabric/03_build_semantic_model.ipynb`: tables, key columns, relationships, measures,
   roles and test users, refresh, and a check against evaluation questions Q03 and Q04.
6. **Ontology.** On the semantic model, select **Generate ontology** and name it `GamesOperationsOntology`. In the
   ontology, open the **Ontology agent**, attach `ontology/ontology-spec.json` and run the two prompts in
   `ontology/ontology-agent-prompts.md` (Plan mode, review the preview, then Act mode). Refresh the ontology.
   When the `finding` table was added after the ontology, run the semantic model notebook again and send prompt 3.
7. **Check.** Run the last section of `fabric/03_build_semantic_model.ipynb`: it reads the ontology definition and
   lists any entity type, relationship type, time series binding or rule that is missing or named differently.
8. **Test.** Ask the questions in `eval/questions.csv` in the ontology agent, then publish the ontology and connect
   the agents.
9. **Source control.** Export the definition with the Fabric REST API `getDefinition` (TMDL format) and commit it,
   so the ontology can be recreated with `updateDefinition` or a deployment pipeline.
"""

VERIFY = """## 11. Design decisions and items to verify

**Decisions**
- Generate the ontology from the Direct Lake semantic model, so bindings point at the lakehouse tables and
  measures become metrics; add time series and rules afterwards. Rejected: building every entity type by hand,
  which is slower and loses the metrics.
- Link tables (`entry`, `session_event`) become entity types, because an ontology relationship links two entity
  types through matching properties; `session_ticketing` is folded into Session as a secondary binding.
- Keys are business codes stored as strings (`noc_code`, `session_id`, ...), readable in agent answers.
- Results carry `noc_code` directly, so team results (no athlete) still roll up to a national committee.
- Thresholds live in data (`venue.wind_limit_ms`, `venue.crowd_density_limit`) and in the current manuals,
  never only in prompts.

**To verify during the build** (not confirmed in public documentation at the time of writing)
- Generation and the ontology agent are preview features; review the agent's preview before applying, and use the
  check in the build notebook rather than assuming every item was created.
- Whether row-level security defined in the semantic model applies to answers that come through the ontology
  path; the permission demo (Q14) is designed for the semantic model path. For the ontology path, check
  OneLake security on the lakehouse tables.
- There is no public API to generate an ontology from a semantic model; generation is a portal action. The
  TMDL definition can be exported with `getDefinition` and redeployed with `updateDefinition`.
- Ontology refresh is manual for new upstream rows; confirm how time series bindings behave for live
  eventhouse data during the demo.
- Service principals can't call the ontology MCP endpoint yet (known issue); plan for signed-in user access.

## 12. Sources

- Data binding in ontology (preview): https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-bind-data
- What is ontology (preview)?: https://learn.microsoft.com/en-us/fabric/iq/ontology/overview
- Consume ontology as an MCP server: https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-use-ontology-mcp-server
- Ontology item definition (TMDL): https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/ontology-definition
- Create Ontology REST API: https://learn.microsoft.com/en-us/rest/api/fabric/ontology/items/create-ontology
- Connect agents to Fabric IQ: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/fabric-iq
- Fabric Ontology knowledge source: https://learn.microsoft.com/en-us/azure/search/agentic-knowledge-source-how-to-fabric-ontology
- Knowledge source overview: https://learn.microsoft.com/en-us/azure/search/agentic-knowledge-source-overview
"""


def render_agent_prompts() -> str:
    sm = o.SEMANTIC_MODEL
    names = {e["table"]: e["name"] for e in o.ENTITY_TYPES}
    rename = "\n".join(f"   - `{t}` → **{n}**" for t, n in names.items())
    keys = "\n".join(f"   - {e['name']}: `{e['key']}`" for e in o.ENTITY_TYPES)
    rels = "\n".join(f"   - {s} **{n}** {t}, bound to lakehouse table `{tb}`: {match_text(n, s, t, tb, sk, tk)} ({c})"
                      for n, s, t, tb, sk, tk, c in o.RELATIONSHIP_TYPES)
    ts = "\n".join(f"   - **{e['name']}** ← KQL table `{t['table']}`: match column `{t['key_column']}` to the existing "
                    f"key property `{e['key']}`, timestamp `{t['timestamp_column']}`, properties "
                    + ", ".join(f"`{p['column']}`" for p in t["properties"])
                    for e in o.ENTITY_TYPES for t in e.get("time_series", []))
    def rule_line(r):
        return f"   - **{r['name']}**: {r['statement']} Linked concepts: {', '.join(r['references'])}."
    needs_finding = [r for r in o.RULES if any(x.startswith("Finding") for x in r["references"])]
    rules = "\n".join(rule_line(r) for r in o.RULES if r not in needs_finding)
    finding_rules = "\n".join(rule_line(r) for r in needs_finding)
    fe = next(e for e in o.ENTITY_TYPES if e["name"] == "Finding")
    f_props = ", ".join(f"`{p['column']}`" for p in fe["properties"])
    f_rels = "\n".join(f"   - {s} **{n}** {t}, bound to lakehouse table `{tb}`: {match_text(n, s, t, tb, sk, tk)} ({c})"
                        for n, s, t, tb, sk, tk, c in o.RELATIONSHIP_TYPES if "Finding" in (s, t))
    fold = o.GENERATION_CLEANUP["fold"][0]
    return f"""# Ontology agent prompts

Use prompts 1 and 2 after **Generate ontology** on `{sm['name']}` has created `{o.ITEMS['ontology']}`. Open the ontology,
select **Ontology agent**, attach `ontology-spec.json` from this folder, and send each prompt in **Plan** mode.
Open the preview the agent posts, check it, then switch to **Act** mode and send *Apply the plan*.
Run the check in `fabric/03_build_semantic_model.ipynb` afterwards.

This file is generated from `generator/ontology_spec.py` by `generator/render_design.py`.

## Prompt 1: structure

```text
The attached ontology-spec.json is the target design for this ontology, which was generated from the semantic
model "{sm['name']}". Change the ontology to match it. Keep property names as generated (source column names)
and keep all metrics.

1. Rename the entity types:
{rename}
2. Delete the entity type `{o.GENERATION_CLEANUP['delete'][0]}`.
3. Delete the entity type `{fold['table']}` and instead add its columns as properties of {fold['into']}, bound to the
   lakehouse table `{fold['table']}` as a secondary binding joined on `{fold['join_column']}`.
4. Make sure each entity type uses this key:
{keys}
5. Make sure exactly these relationship types exist, with these names and bindings; rename generated ones to
   match and remove any that are not listed. Skip the Finding items if Finding doesn't exist yet:
{rels}
6. Add each entity type description from the spec as entity type metadata.
```

## Prompt 2: real-time data and rules

```text
Use the eventhouse KQL database in this workspace (GamesEventhouse) and the attached ontology-spec.json.

1. Add time series bindings (timestamp column `Timestamp`). Match each table's ID column to the entity type's
   existing key property. Don't add the ID column as a new property: a second property for the same ID (for
   example VenueId next to venue_id) blocks validation of later changes.
{ts}
2. Add these business rules and link them to the concepts named. Property names in the rules are the business
   aliases from the spec; link them to the matching generated properties (for example WindLimitMs is
   wind_limit_ms):
{rules}
```

## Prompt 3: findings (after `fabric/04_extract_findings.ipynb`)

Run this once the `finding` table exists and `fabric/03_build_semantic_model.ipynb` has run again.

```text
The lakehouse {o.ITEMS['lakehouse']} now has the table `finding`, extracted from the inspection reports with AI
functions. Use the attached ontology-spec.json.

1. Add the entity type **Finding** with the description from the spec, bound to the lakehouse table `finding`,
   key `finding_id`, display name `finding_id`, with these properties: {f_props}.
2. Add these relationship types:
{f_rels}
3. Add this business rule and link it to the concepts named. Keep the existing rules unchanged; ServiceOverdue
   also uses Asset criticality, and both rules are needed:
{finding_rules}
```

If the agent can't add rules, add them in **Overview** → **Rules** → **Create rule** with the same names and
definitions.
"""


def render(n_docs: int = 51) -> str:
    sources = SOURCES.format(lakehouse=o.ITEMS["lakehouse"], eventhouse=o.ITEMS["eventhouse"],
                             kql=o.ITEMS["kql_database"], sm=o.ITEMS["semantic_model"],
                             n_lh=len(LAKEHOUSE_TABLES), n_eh=len(EVENTHOUSE_TABLES), n_docs=n_docs)
    return "\n".join([INTRO, sources, entity_section(), relationship_section(), metrics_section(),
                      rules_section(), semantic_model_section(), DOCS, scenario_section(), BUILD, VERIFY])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "ontology", "ontology-design.md"))
    a = ap.parse_args()
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(render())
    prompts = os.path.join(os.path.dirname(os.path.abspath(a.out)), "ontology-agent-prompts.md")
    with open(prompts, "w", encoding="utf-8") as f:
        f.write(render_agent_prompts())
    print(f"Wrote {os.path.abspath(a.out)} and {prompts}")
