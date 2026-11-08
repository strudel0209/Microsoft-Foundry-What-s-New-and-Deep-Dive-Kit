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
| `fabric/03_build_semantic_model.ipynb` | Fabric notebook: builds the semantic model (keys, relationships, measures, roles) and checks the ontology |
| `fabric/04_extract_findings.ipynb` | Fabric notebook: AI functions extract inspection findings from the PDFs, score them against the answer key and write the `finding` table |
| `ontology/ontology-design.md` | Entity types, properties, bindings, relationships, metrics, rules, semantic model, build steps |
| `ontology/ontology-agent-prompts.md` | The ontology agent prompts that finish the generated ontology (prompt 3 adds findings) |
| `ontology/ontology-spec.json` | Machine-readable design; attach it to the ontology agent |

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

## Send live data to a Fabric Eventstream

1. In a Fabric-capacity or trial workspace, create an Eventstream and add a **Custom endpoint source**,
   then **Publish**. Contributor or higher permissions are required.
2. Select the source in **Live view**, then **Details > Event Hub > SAS Key Authentication**.
   Copy the full **Connection string-primary key**, not just the key or the AMQP URI.
3. Add the connection settings to the **repository-root `.env`**, next to the root
   [`.env.example`](../../.env.example). If `.env` does not exist, copy that template first; do not
   overwrite an existing `.env`. Fill in the Games operations section locally:

   ```dotenv
   EVENTSTREAM_CONNECTION_STRING="Endpoint=sb://<endpoint>/;SharedAccessKeyName=<key-name>;SharedAccessKey=<key>;EntityPath=<event-hub-name>"
   EVENTSTREAM_EVENTHUB_NAME=
   ```

   Replace the placeholders with the full connection string copied from Fabric. If it has no
   `EntityPath`, set `EVENTSTREAM_EVENTHUB_NAME` to the **Event hub name** on that same Fabric pane
   (not the Eventstream display name). Leave the name blank when `EntityPath` is present.
   Keep the entire connection string on **one physical line**, even inside quotes. Visual word wrapping
   in the editor is fine, but pressing Enter inserts characters that can corrupt the endpoint or SAS
   key and cause `CBS Token authentication failed`. The simulator rejects embedded line breaks before
   connecting.
   The `.env` file is Git-ignored; never put real credentials in `.env.example`.
4. Install dependencies and run from the **repository root**, using the same Python interpreter
   for both commands:

   ```bash
   python -m pip install -r samples/games-operations/requirements.txt
   python samples/games-operations/generator/stream_simulator.py --speed 20 --minutes 45
   ```

   The simulator locates the root `.env` relative to its own file, so it also works when launched
   from this sample directory with `python generator/stream_simulator.py --speed 20 --minutes 45`.
   It does not search for other `.env` files. Precedence is **command-line option > exported
   environment variable > root `.env`**. If an old or empty exported value masks `.env`, remove it
   in Bash with `unset EVENTSTREAM_CONNECTION_STRING EVENTSTREAM_EVENTHUB_NAME` before rerunning.
   `--connection-string` is optional when configured in `.env`; if supplied, it requires a value.
5. Confirm the terminal reports **First event accepted by the Eventstream endpoint**, then select the
   default stream node in Fabric and use **Data preview > JSON > Refresh**. **Data insights >
   IncomingMessages** should increase for the time range covering the run. At speed 20, the 45-minute
   replay takes roughly 2 minutes 15 seconds.

`--dry-run` prints locally and `--output` writes a local file; neither sends to Fabric, even when a
connection string is configured. Without either local-output option, a missing connection string is
an error. Older versions silently printed messages while reporting "Sent"; this did not prove delivery.
The simulator now reports its output mode and only reports "Sent" after successful SDK sends.
Endpoint acceptance does not confirm downstream Eventhouse ingestion. No destination is required to
preview events, but persistence to KQL tables requires destinations and routing by `EventType`.

The SDK uses AMQP over outbound TCP 5671 by default; HTTPS 443 should also be allowed. If the script
stays at "Connecting" without the first-event confirmation, check connectivity and authentication
rather than relying on an empty preview.

See [Fabric custom endpoint setup](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-custom-app).

## Optional: persist live events in Eventhouse tables

Choose the scope you need:

| Goal | Fabric configuration |
|---|---|
| Send and preview events only | Custom endpoint source connected to the default stream; no destination |
| Store and query live events | Add Eventhouse destinations that ingest into KQL database tables |
| Store historical generated data only | Ingest the CSV files using the existing CSV mappings; no Eventstream needed |

**Sending to Eventhouse means ingesting into tables in a KQL database within that Eventhouse.**
It is not a separate forwarding step followed by an optional "save" switch. Eventstream preview and
its finite event retention are not a replacement for table storage. The entire Eventhouse path below
is optional for the simulator, but the full ontology demo needs the Eventhouse tables.

### 1. Prepare the database and tables

1. Create or open `GamesEventhouse` and its KQL database `GamesKQL`. You need Contributor or higher
   access to both the Eventstream workspace and destination workspace, on Fabric capacity or trial.
2. In `GamesKQL`, run the table commands in **section 1** of
   [`fabric/02_eventhouse_setup.kql`](fabric/02_eventhouse_setup.kql), then the JSON ingestion mappings
   in **section 4**. Run the management commands individually, or use the query editor's command-script
   execution option. Section 2 adds useful column descriptions; section 3 is only for historical CSVs.
3. The live simulator emits `TimingEvents`, `VenueConditions`, and `GateFlow`. It does **not** emit
   `AssetTelemetry`; that fourth table is populated from historical data in this sample.

Creating tables and mappings alone does not connect Eventstream to Eventhouse.

### 2. Route each event type separately

The custom endpoint receives **three different JSON shapes**, not one shared table schema.
`EventType` identifies the shape, but a Filter condition does **not** automatically select that
shape as its input schema. Selecting a timing schema for a weather branch can discard the weather
fields and produce null timing fields even though the original JSON is correct. A downstream mapper
cannot recover fields that were lost at the first operator.

1. Run a full 45-minute replay and refresh the default-stream preview so all three event types are
   available. The default race's first timing event occurs about six simulated minutes into the run
   (about 18 seconds at speed 20); a five-minute replay contains no timing events.
2. In the existing Eventstream experience, open **Settings > Schema** and enable **Multiple schema
   inferencing** if it is not already enabled. This setting cannot be disabled afterwards. In
   **Edit** mode, review **Inferred schema** and identify the three schemas by their fields, not just
   their automatically generated names. Associate each with the same custom endpoint source if asked.
   For a schema-aware Eventstream (Preview), use the **Classifier** workflow with `EventType` instead
   of the legacy multiple-schema setting.
3. From the default stream, add three **parallel Filter branches**. On the first operator of each
   branch, select its matching **Input schema**, then configure the `EventType` field with an
   **Equals** condition and the exact, case-sensitive value in the routing table below.
   You need both the correct input schema and the filter condition. Do not copy the timing input
   schema into the other branches, and do not chain the filters.
4. After each filter, add a **Derived stream** destination and name it as shown. Keep the original
   top-level fields unchanged so the existing JSON mappings still match. Use **View schema** and
   **Test result** on each branch to verify that the expected fields still exist and are populated
   before adding a destination.
5. **Publish**. For existing routes, recheck both the first filter and the destination input schema
   after editing; a previously saved destination can still refer to the old schema.

| Filter: `EventType` equals | Derived stream | Target table | Existing JSON mapping |
|---|---|---|---|
| `TimingEvents` | `TimingEventsStream` | `TimingEvents` | `TimingEvents_json` |
| `VenueConditions` | `VenueConditionsStream` | `VenueConditions` | `VenueConditions_json` |
| `GateFlow` | `GateFlowStream` | `GateFlow` | `GateFlow_json` |

Each input schema must include `EventType` (string) plus these columns:

| Branch | Fields besides `EventType` |
|---|---|
| `VenueConditions` | `Timestamp`, `VenueId`, `WindSpeedMs`, `WindGustMs`, `AirTempC`, `SnowTempC`, `HumidityPct`, `VisibilityM` |
| `GateFlow` | `Timestamp`, `GateId`, `VenueId`, `EntriesPerMin`, `QueueingPersons`, `DensityPersonsPerM2` |
| `TimingEvents` | `Timestamp`, `SessionId`, `EventId`, `AthleteId`, `Bib`, `Checkpoint`, `LapNumber`, `SplitTimeS`, `ShootingMisses`, `RankAtCheckpoint` |

Use the types in [the KQL setup](fabric/02_eventhouse_setup.kql). Eventstream may display these as
`DateTime` for KQL `datetime`, `Nvarchar(max)` for `string`, `Float` for `real`, and `BigInt` for `long`.
`ShootingMisses` is a nullable whole number: null at a non-shooting checkpoint is expected, not a missing
field. JSON timestamps are ISO 8601 strings and need datetime interpretation/conversion for ingestion.
Do not add all three event types' fields to every simulator message to compensate for a wrong branch schema.

### 3. Add Eventhouse destinations and configure ingestion

Repeat for each derived stream:

1. Add an **Eventhouse** destination connected to that derived stream. Select **Direct ingestion**
   (supported for derived streams), then the workspace and `GamesEventhouse`. Give each destination
   a distinct name, select **Save**, and **Publish**.
2. In **Live view**, select **Configure** on the Eventhouse destination. In the **Get data** wizard,
   select `GamesKQL` and the corresponding **existing table** from the routing table above.
3. Use a distinct data connection name for each destination, then select **Next**. If samples are
   unavailable, run the simulator while completing the wizard.
4. On **Inspect the data**, choose **JSON**. Under **Advanced**, select the corresponding existing
   JSON mapping. Verify column names and types, then select **Finish** and **Close**.

The filters run before the derived streams; **Direct ingestion** here consumes the already-filtered
derived stream. Do not connect all three tables directly to the unfiltered default stream. JSON mappings
map fields; they do not filter by `EventType`. The mappings intentionally omit `EventType` from storage.

**Event processing before ingestion** is an alternative when attaching Eventhouse to an operator
output or derived stream. Select the destination workspace, Eventhouse, KQL database, matching table,
and JSON input format, then **Save**. Its configuration differs; do not mix that wizard with the
Direct-ingestion mapping steps above.

If this mode reports **Schema mismatch detected ... Add a mapper operator**:

1. First verify the destination targets the correct table: `VenueConditionsStream` must write to
   `VenueConditions`, not a `TimingEvents` table left selected when copying another destination.
   Also verify the first filter's **Input schema** contains the venue fields above. If it contains
   `AthleteId` and `Checkpoint` instead of `VenueId` and `WindSpeedMs`, fix the input schema first;
   inserting a mapper after that filter cannot restore the lost values.
2. Select **Insert a mapper** in the authoring error (or **Add** on the affected destination).
   The route becomes `Derived stream -> Mapper -> Eventhouse destination`.
3. Map each destination column to its identically named source field, using the table schema in
   [section 1 of the KQL setup](fabric/02_eventhouse_setup.kql). Do not carry `EventType` or fields
   belonging to other event types into the table. A Filter selects records; it does not project
   away extra columns or convert their types.
4. For `VenueConditions`, the destination columns are `Timestamp` (datetime), `VenueId` (string),
   `WindSpeedMs`, `WindGustMs`, `AirTempC`, `SnowTempC`, `HumidityPct` (real), and `VisibilityM` (long).
   If the mapper reports incompatible source types, use **Manage fields** before the mapper to
   convert the affected fields, then map them. Merely renaming a field does not convert its value.
5. Finish the mapping, verify the authoring error clears, then **Publish**. Repeat the same
   schema check for the other branches against their own destination tables.

If a previous ingestion wizard created columns such as `SnowTempC_2`, these are not fields produced
by the simulator. Map live `SnowTempC` to the canonical real-valued `SnowTempC` column, not the suffixed
string column. Review existing data and mappings before any cleanup; do not drop populated columns
just to make the destination schema match.

### 4. Verify stored rows

Wait until all branches and destinations are active, then run the simulator again. Events sent before
the routes became active might not be ingested; a new replay is the simplest verification.

In `GamesKQL`, compare table counts before and after the replay:

```kusto
union withsource=TableName TimingEvents, VenueConditions, GateFlow
| summarize Rows=count(), LatestEvent=max(Timestamp) by TableName
| order by TableName asc
```

Inspect stored events, for example:

```kusto
GateFlow
| top 10 by Timestamp desc
```

The simulator advances event timestamps at the requested replay speed, so accelerated runs can contain
future event timestamps relative to wall-clock time. Repeated runs append rows; they do not replace or
deduplicate previous data. Historical CSVs also contribute to table counts. A successful producer send
confirms endpoint acceptance, not table ingestion: verify rows in KQL and check destination status/errors
if Eventstream receives events but the tables remain empty.

For static history instead, use **Get data > Local file** in `GamesKQL`, choose each generated CSV from
`output/eventhouse/`, target its matching table, select **CSV**, skip the header row, and use that table's
`*_csv` mapping from section 3 of the setup script. This path does not require the simulator.

References: [Multiple schema inferencing and branch input schemas](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/process-events-with-multiple-schemas),
[Classifier for schema-aware Eventstreams](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/process-events-with-classifier),
[Derived streams](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-derived-stream),
[Eventhouse destinations and ingestion modes](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-destination-kql-database).

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
   CSV files; optionally [persist live events](#optional-persist-live-events-in-eventhouse-tables) from the
   simulator with three filtered Eventstream routes and Eventhouse destinations.
3. Semantic model: run `fabric/03_build_semantic_model.ipynb` (sections 1 to 4).
4. Ontology: on the semantic model select **Generate ontology**, then run the two prompts in
   `ontology/ontology-agent-prompts.md` in the ontology agent, and check the result with section 6 of the notebook.
5. Findings: run `fabric/04_extract_findings.ipynb`, run `fabric/03_build_semantic_model.ipynb` again, then send
   prompt 3 in the ontology agent and refresh the ontology.

Prerequisites: paid Fabric capacity F2 or higher in a region that supports the full Fabric stack, and the tenant
settings that allow ontology and Fabric item creation.

## Fit with the kit

Proposed location in the Microsoft Foundry What's New and Deep-Dive Kit: `samples/games-operations/`, used by
notebook 9 and the end-to-end deck. Generated output stays out of source control (`.gitignore`); anyone can
recreate it with the same seed. Only public documentation was used for the design; no customer data is included.
