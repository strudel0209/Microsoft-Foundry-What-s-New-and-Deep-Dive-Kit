# Games operations sample: synthetic data and ontology design

A synthetic, reusable dataset and Fabric IQ ontology design for an end-to-end demo: data in Microsoft Fabric
(lakehouse, eventhouse, semantic model), documents enriched for agentic retrieval, and agents in Microsoft
Foundry, Copilot Studio and Microsoft 365 Copilot. The scenario is Games-time operations for a fictional winter
multi-sport event, the **Valmont Winter Games**.

All content is synthetic. National committee codes and country names are public three-letter codes and names;
venues, athletes, people, assets, suppliers, thresholds and findings are fictional. Two naming themes produce
the same data model: `ioc` (Olympic wording, for the IOC workshop) and `neutral` (for the public kit).

## Contents

| Path | What it is |
|---|---|
| `generator/generate.py` | Command-line generator: tables, telemetry, PDFs, evaluation set, ontology specification |
| `generator/stream_simulator.py` | Streams a live biathlon race, venue weather and gate flow to an Eventstream custom endpoint |
| `generator/ontology_spec.py` | Ontology and semantic model design as data (single source of truth, validated against the schema) |
| `generator/render_design.py` | Regenerates `ontology/ontology-design.md` from the specification |
| `generator/schema.py` | Lakehouse and eventhouse table schemas |
| `fabric/01_load_lakehouse.ipynb` | Fabric notebook: loads the tables into the lakehouse as Delta tables |
| `fabric/02_eventhouse_setup.kql` | Eventhouse tables, column descriptions, CSV and JSON mappings, demo queries |
| `ontology/ontology-design.md` | Entity types, properties, bindings, relationships, metrics, rules, semantic model, build steps |

## Quick start

```bash
pip install -r requirements.txt
python generator/generate.py --out output --theme neutral
python generator/stream_simulator.py --dry-run --speed 20 --minutes 5
```

Output layout:

| Folder | Content | Default size |
|---|---|---|
| `output/lakehouse/` | 15 CSV tables (16 with `--include-findings-table`) | about 5,000 rows |
| `output/eventhouse/` | `VenueConditions`, `GateFlow`, `AssetTelemetry`, `TimingEvents` | about 316,000 rows |
| `output/documents/` | 51 PDFs: manuals, inspection reports, transport plans, policies | |
| `output/eval/` | `questions.jsonl` / `.csv` (18 questions with computed answers), `ground_truth_findings.csv` | |
| `output/ontology/ontology-spec.json` | Machine-readable ontology and semantic model specification | |
| `output/manifest.json` | Parameters, row counts and the identifiers of the scripted situations | |

## Parameters

| Option | Default | Purpose |
|---|---|---|
| `--theme` | `neutral` | `neutral` or `ioc` wording |
| `--start-date` | `2026-11-16` | Opening day (day 1). The default makes 24 November 2026 competition day 9 |
| `--as-of` | day 9, 11:00 UTC | Data cut-off: sessions before it are completed and have results and telemetry |
| `--seed` | `2026` | Random seed; output is deterministic for the same seed and dates |
| `--format` | `csv` | `csv`, `parquet` or `both` for the lakehouse tables |
| `--no-docs` | off | Skip PDF generation (the register is still written) |
| `--include-findings-table` | off | Load ground-truth findings instead of running AI functions extraction |

To reuse the sample on another date, set `--start-date` so the demo day falls mid-Games; every evaluation
answer is recomputed from the data.

## Build order in Fabric

1. Lakehouse `GamesLakehouse`: upload this folder to `Files/games_ops/`, run `fabric/01_load_lakehouse.ipynb`.
2. Eventhouse `GamesEventhouse` / KQL database `GamesKQL`: run `fabric/02_eventhouse_setup.kql`, ingest the
   CSV files; for live data, add an Eventstream custom endpoint and run `stream_simulator.py`.
3. Semantic model and ontology: follow sections 7 and 10 of `ontology/ontology-design.md`.

Prerequisites: paid Fabric capacity F2 or higher in a region that supports the full Fabric stack, and the tenant
settings that allow ontology and Fabric item creation.

## Fit with the kit

Proposed location in the Microsoft Foundry What's New and Deep-Dive Kit: `samples/games-operations/`, used by
notebook 9 and the end-to-end deck. Generated output stays out of source control (`.gitignore`); anyone can
recreate it with the same seed. Only public documentation was used for the design; no customer data is included.
