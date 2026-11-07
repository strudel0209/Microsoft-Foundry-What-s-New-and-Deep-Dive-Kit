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
| Semantic model | `{sm}` (Direct Lake) | Medal, ticketing and attendance measures; row-level security by NOC | Metrics (DAX measures referenced by the ontology) |
| Documents | Lakehouse **Files** | {n_docs} PDF manuals, inspection reports, transport plans and policies | Path A: AI functions extract findings into the `finding` table. Path B: full text indexed for Foundry IQ |

**Why this split.** As per official documentation, ontology binding reads data that is already in Fabric
(eventhouse, KQL database, lakehouse, mirrored database, semantic model, SQL database, warehouse). Static
bindings use the lakehouse so every entity type and relationship comes from one source type, which keeps the
pilot simple. The eventhouse adds live state as time series. The semantic model stays the owner of the
business calculations and the row-level security, and the ontology reuses its measures as metrics instead of
redefining them.

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
  LH --> ONT{{GamesOperationsOntology}}
  EH --> ONT
  SM -- metrics --> ONT
  FILES -- indexed OneLake knowledge source --> KB[Foundry IQ knowledge base]
  ONT -- Fabric Ontology knowledge source --> KB
```
"""


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
            "Property names are business names; the column each one binds to is shown below.", ""]
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
           "| Relationship | Source → target | Binding table | Source key → target key | Cardinality |",
           "|---|---|---|---|---|"]
    for n, s, t, tb, sk, tk, c in o.RELATIONSHIP_TYPES:
        out.append(f"| {s} **{n}** {t} | {s} → {t} | `{tb}` | `{sk}` → `{tk}` | {c} |")
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
           "| Metric | Home table | DAX | Used with |", "|---|---|---|---|"]
    for n, tb, dax, u in o.SEMANTIC_MODEL["measures"]:
        out.append(f"| {n} | `{tb}` | `{dax}` | {u} |")
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
           f"**{sm['name']}**, Direct Lake over `{o.ITEMS['lakehouse']}`. Tables: "
           + ", ".join(f"`{t}`" for t in sm["tables"]) + ". Hide `security_noc_user` from report view.", "",
           "| From | To | State |", "|---|---|---|"]
    for a, b, c, d, e in sm["relationships"]:
        out.append(f"| `{a}[{b}]` | `{c}[{d}]` | {e} |")
    out += ["", "**Roles (row-level security)**", "", "| Role | Table | Filter | Purpose |", "|---|---|---|---|"]
    for r in sm["roles"]:
        out.append(f"| {r['name']} | {('`' + r['table'] + '`') if r['table'] else '-'} | "
                   f"{('`' + r['filter'] + '`') if r['filter'] else '-'} | {r['note']} |")
    out += ["", "Replace the three placeholder sign-in names in `security_noc_user` with real test accounts "
            "before the permission test (evaluation question Q14).", ""]
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

1. **Generate** the data locally (`python generator/generate.py --out output --theme ioc`) or in Fabric with
   `fabric/01_load_lakehouse.ipynb` (option B).
2. **Lakehouse.** Create `GamesLakehouse`, upload the sample to `Files/games_ops/`, run
   `fabric/01_load_lakehouse.ipynb`.
3. **Eventhouse.** Create `GamesEventhouse` with the KQL database `GamesKQL`, run
   `fabric/02_eventhouse_setup.kql`, ingest the CSV files from `output/eventhouse/` with the `<Table>_csv`
   mappings. For live data, create an Eventstream with a custom endpoint, route by `EventType` to the four
   tables (JSON mappings `<Table>_json`), and run `generator/stream_simulator.py`.
4. **Findings (path A).** Run the AI functions extraction notebook (next deliverable) to write the `finding`
   table, or regenerate with `--include-findings-table`.
5. **Semantic model.** Create `Games Operations Model` (Direct Lake) over the lakehouse tables in section 7,
   add the relationships, measures and roles.
6. **Ontology.** Create `GamesOperationsOntology`. Add the entity types in section 3 and bind each to its
   lakehouse table; add the time series bindings from `GamesKQL`; add the relationship types in section 4;
   add the metrics from the semantic model; add the rules in section 6; refresh the ontology.
   Optional accelerator: generate the competition entity types from the semantic model, then rebind them to
   the lakehouse tables as in section 3.
7. **Publish and test.** Publish the ontology, try the questions in `eval/questions.csv` in the ontology agent,
   then connect the agents.
8. **Source control.** Export the finished definition with the Fabric REST API `getDefinition` (TMDL format) and
   commit it, so the ontology can be recreated with `updateDefinition` or a deployment pipeline in another
   workspace or tenant.
"""

VERIFY = """## 11. Design decisions and items to verify

**Decisions**
- One static source type (lakehouse) for all entity types and relationships; the semantic model provides
  metrics and row-level security; the eventhouse provides time series. Rejected: binding competition entities to
  the semantic model, because it mixes source types inside relationships during a preview.
- Keys are business codes stored as strings (`noc_code`, `session_id`, ...), readable in agent answers.
- Results carry `noc_code` directly, so team results (no athlete) still roll up to a national committee.
- Thresholds live in data (`venue.wind_limit_ms`, `venue.crowd_density_limit`) and in the current manuals,
  never only in prompts.

**To verify during the build** (not confirmed in public documentation at the time of writing)
- Whether an entity type bound to a semantic model table can also take an eventhouse time series binding
  (only relevant if the optional accelerator in step 6 is kept).
- Whether row-level security defined in the semantic model applies to answers that come through the ontology
  path; the permission demo (Q14) is designed for the semantic model path. For the ontology path, check
  OneLake security on the lakehouse tables.
- Exact TMDL syntax for relationships, metrics and rules: export with `getDefinition` after the portal build
  rather than writing TMDL by hand.
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
    print(f"Wrote {os.path.abspath(a.out)}")
