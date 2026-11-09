# Ontology agent prompts

Use prompts 1 and 2 after **Generate ontology** on `Games Operations Model` has created `GamesOperationsOntology`. Open the ontology,
select **Ontology agent**, attach `ontology-spec.json` from this folder, and send each prompt in **Plan** mode.
Open the preview the agent posts, check it, then switch to **Act** mode and send *Apply the plan*.
Run the check in `fabric/03_build_semantic_model.ipynb` afterwards.

This file is generated from `generator/ontology_spec.py` by `generator/render_design.py`.

## Prompt 1: structure

```text
The attached ontology-spec.json is the target design for this ontology, which was generated from the semantic
model "Games Operations Model". Change the ontology to match it. Keep property names as generated (source column names)
and keep all metrics.

1. Rename the entity types:
   - `noc` → **NOC**
   - `athlete` → **Athlete**
   - `discipline` → **Discipline**
   - `event` → **Event**
   - `session` → **Session**
   - `result` → **Result**
   - `entry` → **Entry**
   - `session_event` → **SessionEvent**
   - `venue` → **Venue**
   - `gate` → **Gate**
   - `asset` → **Asset**
   - `supplier` → **Supplier**
   - `finding` → **Finding**
   - `document_register` → **Document**
2. Delete the entity type `security_noc_user`.
3. Delete the entity type `session_ticketing` and instead add its columns as properties of Session, bound to the
   lakehouse table `session_ticketing` as a secondary binding joined on `session_id`.
4. Make sure each entity type uses this key:
   - NOC: `noc_code`
   - Athlete: `athlete_id`
   - Discipline: `discipline_code`
   - Event: `event_id`
   - Session: `session_id`
   - Result: `result_id`
   - Entry: `entry_id`
   - SessionEvent: `session_event_id`
   - Venue: `venue_id`
   - Gate: `gate_id`
   - Asset: `asset_id`
   - Supplier: `supplier_id`
   - Finding: `finding_id`
   - Document: `document_id`
5. Make sure exactly these relationship types exist, with these names and bindings; rename generated ones to
   match and remove any that are not listed. Skip the Finding items if Finding doesn't exist yet:
   - Athlete **represents** NOC, bound to lakehouse table `athlete`: Athlete.`noc_code` = NOC.`noc_code` (many-to-one)
   - Athlete **practises** Discipline, bound to lakehouse table `athlete`: Athlete.`discipline_code` = Discipline.`discipline_code` (many-to-one)
   - Athlete **hasEntry** Entry, bound to lakehouse table `entry`: Athlete.`athlete_id` = Entry.`athlete_id` (one-to-many)
   - Entry **entersEvent** Event, bound to lakehouse table `entry`: Entry.`event_id` = Event.`event_id` (many-to-one)
   - Event **belongsTo** Discipline, bound to lakehouse table `event`: Event.`discipline_code` = Discipline.`discipline_code` (many-to-one)
   - Session **schedules** SessionEvent, bound to lakehouse table `session_event`: Session.`session_id` = SessionEvent.`session_id` (one-to-many)
   - SessionEvent **concernsEvent** Event, bound to lakehouse table `session_event`: SessionEvent.`event_id` = Event.`event_id` (many-to-one)
   - Session **isHeldAt** Venue, bound to lakehouse table `session`: Session.`venue_id` = Venue.`venue_id` (many-to-one)
   - Venue **isHomeVenueOf** Discipline, bound to lakehouse table `discipline`: Venue.`venue_id` = Discipline.`venue_id` (one-to-many)
   - Result **isResultOf** Event, bound to lakehouse table `result`: Result.`event_id` = Event.`event_id` (many-to-one)
   - Result **isRecordedIn** Session, bound to lakehouse table `result`: Result.`session_id` = Session.`session_id` (many-to-one)
   - Result **isCreditedTo** NOC, bound to lakehouse table `result`: Result.`noc_code` = NOC.`noc_code` (many-to-one)
   - Result **isAchievedBy** Athlete, bound to lakehouse table `result`: Result.`athlete_id` = Athlete.`athlete_id` (many-to-one)
   - Gate **servesVenue** Venue, bound to lakehouse table `gate`: Gate.`venue_id` = Venue.`venue_id` (many-to-one)
   - Asset **isInstalledAt** Venue, bound to lakehouse table `asset`: Asset.`venue_id` = Venue.`venue_id` (many-to-one)
   - Asset **isMaintainedBy** Supplier, bound to lakehouse table `asset`: Asset.`supplier_id` = Supplier.`supplier_id` (many-to-one)
   - Finding **concernsVenue** Venue, bound to lakehouse table `finding`: Finding.`venue_id` = Venue.`venue_id` (many-to-one)
   - Finding **concernsAsset** Asset, bound to lakehouse table `finding`: Finding.`asset_id` = Asset.`asset_id` (many-to-one)
   - Finding **isRecordedInDocument** Document, bound to lakehouse table `finding`: Finding.`document_id` = Document.`document_id` (many-to-one)
   - Document **covers** Venue, bound to lakehouse table `document_register`: Document.`venue_id` = Venue.`venue_id` (many-to-one)
6. Add each entity type description from the spec as entity type metadata.
```

## Prompt 2: real-time data and rules

```text
Use the eventhouse KQL database in this workspace (GamesEventhouse) and the attached ontology-spec.json.

1. Add time series bindings (timestamp column `Timestamp`). Match each table's ID column to the entity type's
   existing key property. Don't add the ID column as a new property: a second property for the same ID (for
   example VenueId next to venue_id) blocks validation of later changes.
   - **Athlete** ← KQL table `TimingEvents`: match column `AthleteId` to the existing key property `athlete_id`, timestamp `Timestamp`, properties `SessionId`, `EventId`, `Checkpoint`, `LapNumber`, `SplitTimeS`, `ShootingMisses`, `RankAtCheckpoint`
   - **Venue** ← KQL table `VenueConditions`: match column `VenueId` to the existing key property `venue_id`, timestamp `Timestamp`, properties `WindSpeedMs`, `WindGustMs`, `AirTempC`, `SnowTempC`, `HumidityPct`, `VisibilityM`
   - **Gate** ← KQL table `GateFlow`: match column `GateId` to the existing key property `gate_id`, timestamp `Timestamp`, properties `EntriesPerMin`, `QueueingPersons`, `DensityPersonsPerM2`
   - **Asset** ← KQL table `AssetTelemetry`: match column `AssetId` to the existing key property `asset_id`, timestamp `Timestamp`, properties `TemperatureC`, `PowerKw`, `StatusCode`
2. Add these business rules and link them to the concepts named. Property names in the rules are the business
   aliases from the spec; link them to the matching generated properties (for example WindLimitMs is
   wind_limit_ms):
   - **WindHold**: An outdoor Session must not start, or must be interrupted, when its Venue's WindGustMs is above the Venue's WindLimitMs for three consecutive minutes. Linked concepts: Session, Venue.WindGustMs, Venue.WindLimitMs, Session isHeldAt Venue.
   - **GateOvercrowding**: A Gate is overcrowded when its DensityPersonsPerM2 stays above the Venue's CrowdDensityLimit for five minutes or more. Linked concepts: Gate.DensityPersonsPerM2, Venue.CrowdDensityLimit, Gate servesVenue Venue.
   - **ServiceOverdue**: An Asset with Criticality Critical is overdue for service when its LastServiceDate is more than 30 days before today. Linked concepts: Asset.Criticality, Asset.LastServiceDate.
   - **AuthoritativeManual**: Only a Document with Status Current is authoritative for operating limits; Superseded documents must not be used. Linked concepts: Document.Status, Document covers Venue.
```

## Prompt 3: findings (after `fabric/04_extract_findings.ipynb`)

Run this once the `finding` table exists and `fabric/03_build_semantic_model.ipynb` has run again.

```text
The lakehouse GamesLakehouse now has the table `finding`, extracted from the inspection reports with AI
functions. Use the attached ontology-spec.json.

1. Add the entity type **Finding** with the description from the spec, bound to the lakehouse table `finding`,
   key `finding_id`, display name `finding_id`, with these properties: `finding_id`, `document_id`, `venue_id`, `asset_id`, `inspection_date`, `severity`, `category`, `description`, `recommendation`, `finding_status`, `due_date`.
2. Add these relationship types:
   - Finding **concernsVenue** Venue, bound to lakehouse table `finding`: Finding.`venue_id` = Venue.`venue_id` (many-to-one)
   - Finding **concernsAsset** Asset, bound to lakehouse table `finding`: Finding.`asset_id` = Asset.`asset_id` (many-to-one)
   - Finding **isRecordedInDocument** Document, bound to lakehouse table `finding`: Finding.`document_id` = Document.`document_id` (many-to-one)
3. Add this business rule and link it to the concepts named. Keep the existing rules unchanged; ServiceOverdue
   also uses Asset criticality, and both rules are needed:
   - **SessionAtRisk**: A Scheduled Session is at operational risk when its Venue has an Open Finding of High severity that concerns an Asset with Criticality Critical. Linked concepts: Session, Finding.Severity, Finding.Status, Asset.Criticality, Finding concernsAsset Asset, Session isHeldAt Venue.
```

If the agent can't add rules, add them in **Overview** → **Rules** → **Create rule** with the same names and
definitions.
