"""Ontology and semantic model design for the Games operations sample (single source of truth).

The design is expressed as data so it can be validated against the generated tables and
exported to JSON for the ontology build. Static entity bindings use the lakehouse, time
series use the eventhouse, and metrics come from DAX measures in the semantic model.
"""
from __future__ import annotations

from schema import EVENTHOUSE_TABLES, LAKEHOUSE_TABLES

TYPE_MAP = {"string": "string", "int": "integer", "long": "integer", "double": "double",
            "bool": "boolean", "date": "datetime", "timestamp": "datetime"}

ITEMS = {
    "lakehouse": "GamesLakehouse",
    "eventhouse": "GamesEventhouse",
    "kql_database": "GamesKQL",
    "semantic_model": "Games Operations Model",
    "ontology": "GamesOperationsOntology",
}


def _props(table, renames, skip=()):
    cols = {c: ty for c, ty, _ in LAKEHOUSE_TABLES[table]}
    out = []
    for col, name in renames.items():
        if col in skip:
            continue
        out.append(dict(name=name, column=col, type=TYPE_MAP[cols[col]]))
    return out


def _ts(table, key_col, props):
    cols = {c: ty for c, ty, _ in EVENTHOUSE_TABLES[table]}
    tmap = {"datetime": "datetime", "string": "string", "real": "double", "int": "integer"}
    return dict(source="eventhouse", item=ITEMS["kql_database"], table=table, key_column=key_col,
                timestamp_column="Timestamp",
                properties=[dict(name=p, column=p, type=tmap[cols[p]]) for p in props])


ENTITY_TYPES = [
    dict(name="NOC", description="A national committee and its delegation at the Games.",
         table="noc", key="noc_code", display="noc_name",
         properties=_props("noc", {"noc_code": "NocCode", "noc_name": "Name", "region": "Region",
                                   "delegation_size": "DelegationSize"})),
    dict(name="Athlete", description="A competitor entered by a national committee.",
         table="athlete", key="athlete_id", display="family_name",
         properties=_props("athlete", {"athlete_id": "AthleteId", "given_name": "GivenName",
                                       "family_name": "FamilyName", "gender_category": "Category",
                                       "birth_year": "BirthYear", "noc_code": "NocCode",
                                       "discipline_code": "DisciplineCode"}),
         time_series=[_ts("TimingEvents", "AthleteId",
                          ["SessionId", "EventId", "Checkpoint", "LapNumber", "SplitTimeS",
                           "ShootingMisses", "RankAtCheckpoint"])]),
    dict(name="Discipline", description="A discipline within a sport, played at one home venue.",
         table="discipline", key="discipline_code", display="discipline_name",
         properties=_props("discipline", {"discipline_code": "DisciplineCode", "discipline_name": "Name",
                                          "sport_name": "Sport", "venue_id": "VenueId",
                                          "scoring_type": "ScoringType"})),
    dict(name="Event", description="A medal event, for example Women's 10 km Pursuit.",
         table="event", key="event_id", display="event_name",
         properties=_props("event", {"event_id": "EventId", "event_name": "Name",
                                     "discipline_code": "DisciplineCode", "gender_category": "Category",
                                     "is_team_event": "IsTeamEvent", "medal_date": "MedalDate",
                                     "has_qualification": "HasQualification"})),
    dict(name="Session", description="A ticketed competition session at a venue.",
         table="session", key="session_id", display="session_id",
         properties=_props("session", {"session_id": "SessionId", "venue_id": "VenueId",
                                       "competition_day": "CompetitionDay", "session_date": "SessionDate",
                                       "start_time_utc": "StartTimeUtc", "end_time_utc": "EndTimeUtc",
                                       "session_type": "SessionType", "session_status": "Status",
                                       "status_reason": "StatusReason"}),
         secondary_bindings=[dict(table="session_ticketing", join_column="session_id",
                                  properties=_props("session_ticketing", {
                                      "seats_available": "SeatsAvailable", "tickets_sold": "TicketsSold",
                                      "scanned_entries": "ScannedEntries"}))]),
    dict(name="Result", description="A ranked result recorded in a session; team results have no athlete.",
         table="result", key="result_id", display="result_id",
         properties=_props("result", {"result_id": "ResultId", "event_id": "EventId",
                                      "session_id": "SessionId", "noc_code": "NocCode",
                                      "athlete_id": "AthleteId", "result_rank": "Rank", "mark": "Mark",
                                      "mark_unit": "MarkUnit", "medal": "Medal"})),
    dict(name="Venue", description="A competition venue with its operating limits.",
         table="venue", key="venue_id", display="venue_name",
         properties=_props("venue", {"venue_id": "VenueId", "venue_name": "Name", "cluster_name": "Cluster",
                                     "environment": "Environment", "seating_capacity": "SeatingCapacity",
                                     "gate_count": "GateCount", "wind_limit_ms": "WindLimitMs",
                                     "crowd_density_limit": "CrowdDensityLimit", "latitude": "Latitude",
                                     "longitude": "Longitude"}),
         time_series=[_ts("VenueConditions", "VenueId",
                          ["WindSpeedMs", "WindGustMs", "AirTempC", "SnowTempC", "HumidityPct", "VisibilityM"])]),
    dict(name="Gate", description="A spectator gate and its queueing plaza.",
         table="gate", key="gate_id", display="gate_name",
         properties=_props("gate", {"gate_id": "GateId", "venue_id": "VenueId", "gate_name": "Name",
                                    "plaza_area_m2": "PlazaAreaM2", "max_entries_per_min": "MaxEntriesPerMin"}),
         time_series=[_ts("GateFlow", "GateId", ["EntriesPerMin", "QueueingPersons", "DensityPersonsPerM2"])]),
    dict(name="Asset", description="Venue equipment, with criticality and service history.",
         table="asset", key="asset_id", display="asset_name",
         properties=_props("asset", {"asset_id": "AssetId", "venue_id": "VenueId", "asset_name": "Name",
                                     "asset_type": "AssetType", "criticality": "Criticality",
                                     "operational_status": "OperationalStatus", "is_monitored": "IsMonitored",
                                     "supplier_id": "SupplierId", "install_date": "InstallDate",
                                     "last_service_date": "LastServiceDate"}),
         time_series=[_ts("AssetTelemetry", "AssetId", ["TemperatureC", "PowerKw", "StatusCode"])]),
    dict(name="Supplier", description="A contractor that maintains venue assets.",
         table="supplier", key="supplier_id", display="supplier_name",
         properties=_props("supplier", {"supplier_id": "SupplierId", "supplier_name": "Name",
                                        "service_category": "ServiceCategory"})),
    dict(name="Finding", description="An inspection finding extracted from an inspection report (AI functions).",
         table="finding", key="finding_id", display="finding_id",
         properties=_props("finding", {"finding_id": "FindingId", "document_id": "DocumentId",
                                       "venue_id": "VenueId", "asset_id": "AssetId",
                                       "inspection_date": "InspectionDate", "severity": "Severity",
                                       "category": "Category", "description": "Description",
                                       "recommendation": "Recommendation", "finding_status": "Status",
                                       "due_date": "DueDate"})),
    dict(name="Document", description="A controlled document: manual, inspection report, plan or policy.",
         table="document_register", key="document_id", display="title",
         properties=_props("document_register", {
             "document_id": "DocumentId", "title": "Title", "document_type": "DocumentType",
             "venue_id": "VenueId", "version": "Version", "document_status": "Status",
             "effective_date": "EffectiveDate", "sensitivity": "Sensitivity", "onelake_path": "OneLakePath"})),
]

# (name, source entity, target entity, binding table, source key column, target key column, cardinality)
RELATIONSHIP_TYPES = [
    ("represents", "Athlete", "NOC", "athlete", "athlete_id", "noc_code", "many-to-one"),
    ("practises", "Athlete", "Discipline", "athlete", "athlete_id", "discipline_code", "many-to-one"),
    ("isEnteredIn", "Athlete", "Event", "entry", "athlete_id", "event_id", "many-to-many"),
    ("belongsTo", "Event", "Discipline", "event", "event_id", "discipline_code", "many-to-one"),
    ("isContestedIn", "Event", "Session", "session_event", "event_id", "session_id", "many-to-many"),
    ("isHeldAt", "Session", "Venue", "session", "session_id", "venue_id", "many-to-one"),
    ("isHomeVenueOf", "Venue", "Discipline", "discipline", "venue_id", "discipline_code", "one-to-many"),
    ("isResultOf", "Result", "Event", "result", "result_id", "event_id", "many-to-one"),
    ("isRecordedIn", "Result", "Session", "result", "result_id", "session_id", "many-to-one"),
    ("isCreditedTo", "Result", "NOC", "result", "result_id", "noc_code", "many-to-one"),
    ("isAchievedBy", "Result", "Athlete", "result", "result_id", "athlete_id", "many-to-one"),
    ("servesVenue", "Gate", "Venue", "gate", "gate_id", "venue_id", "many-to-one"),
    ("isInstalledAt", "Asset", "Venue", "asset", "asset_id", "venue_id", "many-to-one"),
    ("isMaintainedBy", "Asset", "Supplier", "asset", "asset_id", "supplier_id", "many-to-one"),
    ("concernsVenue", "Finding", "Venue", "finding", "finding_id", "venue_id", "many-to-one"),
    ("concernsAsset", "Finding", "Asset", "finding", "finding_id", "asset_id", "many-to-one"),
    ("isRecordedInDocument", "Finding", "Document", "finding", "finding_id", "document_id", "many-to-one"),
    ("covers", "Document", "Venue", "document_register", "document_id", "venue_id", "many-to-one"),
]

# Semantic model: Direct Lake over the lakehouse tables
SEMANTIC_MODEL = dict(
    name=ITEMS["semantic_model"],
    tables=["noc", "athlete", "discipline", "event", "venue", "session", "session_event",
            "session_ticketing", "result", "security_noc_user"],
    relationships=[
        ("athlete", "noc_code", "noc", "noc_code", "active"),
        ("result", "noc_code", "noc", "noc_code", "active"),
        ("result", "athlete_id", "athlete", "athlete_id", "inactive (avoids an ambiguous path NOC→Result)"),
        ("result", "event_id", "event", "event_id", "active"),
        ("result", "session_id", "session", "session_id", "active"),
        ("event", "discipline_code", "discipline", "discipline_code", "active"),
        ("session", "venue_id", "venue", "venue_id", "active"),
        ("session_ticketing", "session_id", "session", "session_id", "active (one-to-one)"),
        ("session_event", "session_id", "session", "session_id", "active"),
        ("session_event", "event_id", "event", "event_id", "inactive (bridge; use in DAX when needed)"),
    ],
    measures=[
        ("Gold Medals", "result", "CALCULATE ( COUNTROWS ( 'result' ), 'result'[medal] = \"Gold\" )", "NOC"),
        ("Silver Medals", "result", "CALCULATE ( COUNTROWS ( 'result' ), 'result'[medal] = \"Silver\" )", "NOC"),
        ("Bronze Medals", "result", "CALCULATE ( COUNTROWS ( 'result' ), 'result'[medal] = \"Bronze\" )", "NOC"),
        ("Total Medals", "result", "[Gold Medals] + [Silver Medals] + [Bronze Medals]", "NOC"),
        ("Tickets Sold", "session_ticketing", "SUM ( 'session_ticketing'[tickets_sold] )", "Session, Venue"),
        ("Seats Available", "session_ticketing", "SUM ( 'session_ticketing'[seats_available] )", "Session, Venue"),
        ("Sell-Through Rate", "session_ticketing", "DIVIDE ( [Tickets Sold], [Seats Available] )", "Session, Venue"),
        ("Attendance Rate", "session_ticketing",
         "DIVIDE ( SUM ( 'session_ticketing'[scanned_entries] ), "
         "CALCULATE ( [Tickets Sold], NOT ISBLANK ( 'session_ticketing'[scanned_entries] ) ) )", "Session, Venue"),
        ("Completed Sessions", "session",
         "CALCULATE ( COUNTROWS ( 'session' ), 'session'[session_status] = \"Completed\" )", "Venue"),
    ],
    roles=[
        dict(name="NOC delegation viewer", table="noc",
             filter="'noc'[noc_code] IN CALCULATETABLE ( VALUES ( 'security_noc_user'[noc_code] ), "
                    "'security_noc_user'[user_principal_name] = USERPRINCIPALNAME () )",
             note="Filters NOC, and through relationships athletes and results, to the user's delegation."),
        dict(name="Games-wide viewer", table=None, filter=None, note="No filter."),
    ],
)

RULES = [
    dict(name="WindHold",
         statement="An outdoor Session must not start, or must be interrupted, when its Venue's WindGustMs "
                   "is above the Venue's WindLimitMs for three consecutive minutes.",
         references=["Session", "Venue.WindGustMs", "Venue.WindLimitMs", "Session isHeldAt Venue"]),
    dict(name="GateOvercrowding",
         statement="A Gate is overcrowded when its DensityPersonsPerM2 stays above the Venue's "
                   "CrowdDensityLimit for five minutes or more.",
         references=["Gate.DensityPersonsPerM2", "Venue.CrowdDensityLimit", "Gate servesVenue Venue"]),
    dict(name="SessionAtRisk",
         statement="A Scheduled Session is at operational risk when its Venue has an Open Finding of High "
                   "severity that concerns an Asset with Criticality Critical.",
         references=["Session", "Finding.Severity", "Finding.Status", "Asset.Criticality",
                     "Finding concernsAsset Asset", "Session isHeldAt Venue"]),
    dict(name="ServiceOverdue",
         statement="An Asset with Criticality Critical is overdue for service when its LastServiceDate is "
                   "more than 30 days before today.",
         references=["Asset.Criticality", "Asset.LastServiceDate"]),
    dict(name="AuthoritativeManual",
         statement="Only a Document with Status Current is authoritative for operating limits; Superseded "
                   "documents must not be used.",
         references=["Document.Status", "Document covers Venue"]),
]


def validate():
    """Check every bound column exists in the generated table schemas."""
    errors = []
    lh = {t: {c for c, *_ in cols} for t, cols in LAKEHOUSE_TABLES.items()}
    eh = {t: {c for c, *_ in cols} for t, cols in EVENTHOUSE_TABLES.items()}
    names = {e["name"] for e in ENTITY_TYPES}
    for e in ENTITY_TYPES:
        if e["key"] not in lh[e["table"]]:
            errors.append(f"{e['name']}: key {e['key']} missing")
        keytype = next(p["type"] for p in e["properties"] if p["column"] == e["key"])
        if keytype not in ("string", "integer"):
            errors.append(f"{e['name']}: key type {keytype} not allowed")
        for p in e["properties"]:
            if p["column"] not in lh[e["table"]]:
                errors.append(f"{e['name']}.{p['name']}: column {p['column']} missing")
        for ts in e.get("time_series", []):
            for p in ts["properties"] + [dict(column=ts["key_column"]), dict(column=ts["timestamp_column"])]:
                if p["column"] not in eh[ts["table"]]:
                    errors.append(f"{e['name']} time series: {p['column']} missing in {ts['table']}")
    for n, s, tgt, tbl, sk, tk, _ in RELATIONSHIP_TYPES:
        if s not in names or tgt not in names:
            errors.append(f"{n}: unknown entity")
        if sk not in lh[tbl] or tk not in lh[tbl]:
            errors.append(f"{n}: binding columns missing in {tbl}")
    return errors


def to_json_dict():
    return dict(
        name=ITEMS["ontology"], items=ITEMS,
        notes=["Static entity bindings use the lakehouse; time series use the eventhouse; metrics come from "
               "DAX measures in the semantic model.",
               "Property value types follow the supported ontology types: string, integer, double, boolean, "
               "datetime. Entity keys are string."],
        entity_types=ENTITY_TYPES,
        relationship_types=[dict(name=n, source=s, target=t, binding_table=tb, source_key_column=sk,
                                 target_key_column=tk, cardinality=c)
                            for n, s, t, tb, sk, tk, c in RELATIONSHIP_TYPES],
        metrics=[dict(name=n, semantic_model=ITEMS["semantic_model"], home_table=tb, dax=dax, used_by=u)
                 for n, tb, dax, u in SEMANTIC_MODEL["measures"]],
        rules=RULES,
        semantic_model=dict(name=SEMANTIC_MODEL["name"], storage_mode="Direct Lake on OneLake",
                            tables=SEMANTIC_MODEL["tables"],
                            relationships=[dict(from_table=a, from_column=b, to_table=c, to_column=d, state=e)
                                           for a, b, c, d, e in SEMANTIC_MODEL["relationships"]],
                            roles=SEMANTIC_MODEL["roles"]),
    )
