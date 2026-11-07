"""Evaluation questions with expected answers computed from the generated data.

Each question names the source types it needs, so the same set can compare orchestration
patterns (knowledge base only, Fabric IQ tool plus knowledge base, multi-agent) and the
Copilot Studio agent. Answers are computed, not hand-written, so they stay correct when the
data is regenerated with another seed or date.
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd

from tables import GamesData


def _d(x):
    return x.strftime("%d %B %Y").lstrip("0")


def build_eval_set(gd: GamesData, telemetry: dict, register: pd.DataFrame, findings: pd.DataFrame):
    t = gd.tables
    venue = t["venue"].set_index("venue_id")
    asset = t["asset"]
    session = t["session"]
    se = t["session_event"]
    ev = t["event"].set_index("event_id")
    res = t["result"]
    noc = t["noc"].set_index("noc_code")
    today = gd.as_of.date()
    tomorrow = today + timedelta(days=1)
    q = []

    def add(qid, category, question, answer, sources, notes=""):
        q.append(dict(id=qid, category=category, question=question, expected_answer=answer,
                      required_sources=sources, notes=notes))

    # Q01 sessions tomorrow and critical assets
    s_tom = session[session.session_date == tomorrow]
    parts = []
    for vid, grp in s_tom.groupby("venue_id"):
        crit = asset[(asset.venue_id == vid) & (asset.criticality == "Critical")]
        parts.append(f"{venue.loc[vid].venue_name}: {len(grp)} session(s), {len(crit)} Critical assets "
                     f"({', '.join(sorted(crit.asset_type.unique()))})")
    add("Q01", "ontology-lakehouse",
        f"Which venues host competition sessions on {_d(tomorrow)}, and which Critical assets serve them?",
        "; ".join(parts), ["ontology"])

    # Q02 athletes of Norway in biathlon
    ath = t["athlete"]
    nb = ath[(ath.noc_code == "NOR") & (ath.discipline_code == "BTH")]
    add("Q02", "ontology-relationships", "Which athletes represent Norway in Biathlon?",
        ", ".join(sorted(nb.given_name + " " + nb.family_name)), ["ontology"])

    # Q03 medal table
    med = res[res.medal.notna()].groupby(["noc_code", "medal"]).size().unstack(fill_value=0)
    for c in ("Gold", "Silver", "Bronze"):
        if c not in med:
            med[c] = 0
    med = med.sort_values(["Gold", "Silver", "Bronze"], ascending=False).head(3)
    add("Q03", "metric-semantic-model", "Which three NOCs lead the medal table by gold medals?",
        "; ".join(f"{noc.loc[c].noc_name} ({c}): {r.Gold} gold, {r.Silver} silver, {r.Bronze} bronze"
                  for c, r in med.iterrows()), ["semantic model metric"])

    # Q04 attendance rate at Ice Arena
    tk = t["session_ticketing"].merge(session[["session_id", "venue_id", "session_status"]], on="session_id")
    ia = tk[(tk.venue_id == "V01") & (tk.session_status == "Completed")]
    rate = ia.scanned_entries.sum() / ia.tickets_sold.sum()
    add("Q04", "metric-semantic-model",
        "What is the attendance rate (scanned entries divided by tickets sold) for completed sessions at "
        "Valmont Ice Arena?", f"{rate:.1%} over {len(ia)} completed sessions", ["semantic model metric"])

    # Q05 postponement
    p = session[session.session_id == gd.scenario["postponed_session_id"]].iloc[0]
    r = session[session.session_id == gd.scenario["rescheduled_session_id"]].iloc[0]
    add("Q05", "ontology-lakehouse", "Which competition session was postponed, why, and when was it rescheduled?",
        f"{p.session_id} ({ev.loc[gd.scenario['wind_postponement_event']].event_name}, "
        f"{venue.loc[p.venue_id].venue_name}, {_d(p.session_date)}) was postponed because wind gusts exceeded "
        f"the venue operating limit; rescheduled as {r.session_id} on {_d(r.session_date)} at "
        f"{r.start_time_utc:%H:%M} UTC", ["ontology"])

    # Q06 wind exceedance
    vc = telemetry["VenueConditions"].merge(t["venue"][["venue_id", "wind_limit_ms"]],
                                            left_on="VenueId", right_on="venue_id")
    ex = vc[(vc.WindGustMs > vc.wind_limit_ms)]
    d6 = ex.Timestamp.dt.date.iloc[0]
    exd = ex[ex.Timestamp.dt.date == d6]
    add("Q06", "ontology-eventhouse",
        f"Which venue exceeded its wind gust limit on {_d(d6)}, for how many minutes, and what was the peak gust?",
        f"{venue.loc[exd.VenueId.iloc[0]].venue_name}: {len(exd)} minutes above "
        f"{exd.wind_limit_ms.iloc[0]} m/s between {exd.Timestamp.min():%H:%M} and "
        f"{exd.Timestamp.max():%H:%M} UTC; peak gust {exd.WindGustMs.max():.1f} m/s", ["ontology time series"])

    # Q07 crowd density
    gf = telemetry["GateFlow"]
    over = gf[gf.DensityPersonsPerM2 > 4.0]
    add("Q07", "ontology-eventhouse",
        f"Which gate exceeded the crowd density limit on {_d(over.Timestamp.iloc[0])}, for how long, and what "
        "was the peak density?",
        f"{over.GateId.iloc[0]}: {len(over)} minutes above 4.0 persons/m² from {over.Timestamp.min():%H:%M} to "
        f"{over.Timestamp.max():%H:%M} UTC; peak {over.DensityPersonsPerM2.max():.2f} persons/m²",
        ["ontology time series"])

    # Q08 alarm asset
    at = telemetry["AssetTelemetry"]
    last = at.sort_values("Timestamp").groupby("AssetId").tail(1)
    al = last[last.StatusCode == "ALARM"]
    al_names = asset.set_index("asset_id").loc[al.AssetId]
    add("Q08", "ontology-eventhouse", "Which monitored asset is currently in ALARM state, and what is its latest "
        "temperature reading?",
        "; ".join(f"{a} ({n.asset_type}, {venue.loc[n.venue_id].venue_name}): {tmp:.2f} °C"
                  for a, n, tmp in zip(al.AssetId, al_names.itertuples(), al.TemperatureC)) or "None",
        ["ontology time series"], "Depends on the as-of time used for generation.")

    # Q09 / Q13 current vs superseded manual
    for qid, vid in (("Q09", "V08"), ("Q13", "V07")):
        cur = register[(register.venue_id == vid) & (register.document_type == "Venue operations manual") &
                       (register.document_status == "Current")].iloc[0]
        add(qid, "documents-authoritative-source",
            f"What is the wind gust limit for {venue.loc[vid].venue_name}?",
            f"{venue.loc[vid].wind_limit_ms:.1f} m/s for three consecutive minutes, from the current manual "
            f"{cur.document_id} (version {cur.version}); the superseded version 1.0 must not be used",
            ["documents"], "Trap question: a superseded manual with a different limit is also indexed.")

    # Q10 crowd procedure
    add("Q10", "documents", "What must happen when a gate plaza exceeds the crowd density limit?",
        "Open the overflow lane at the gate; the transport hub holds arriving shuttles for 10 minutes; a public "
        "address announcement redirects spectators to a gate with spare capacity; report to the Main Operations "
        "Centre within 10 minutes", ["documents"])

    # Q11 sessions at risk
    crit_ids = set(asset[asset.criticality == "Critical"].asset_id)
    open_high = findings[(findings.severity == "High") & (findings.finding_status == "Open") &
                         (findings.asset_id.isin(crit_ids))]
    risk = []
    for f in open_high.itertuples():
        fut = session[(session.venue_id == f.venue_id) & (session.session_status == "Scheduled")]
        for s in fut.itertuples():
            evs = ", ".join(ev.loc[e].event_name for e in se[se.session_id == s.session_id].event_id)
            risk.append(f"{s.session_id} ({evs}, {_d(s.session_date)})")
        rec = f.recommendation
    add("Q11", "combined", "Which scheduled sessions are at risk from open High-severity findings on Critical "
        "assets, and what did the inspector recommend?",
        ("; ".join(risk) + f". Recommendation: {rec}") if risk else "None",
        ["ontology", "documents"])

    # Q12 overdue service
    od = asset[(asset.criticality == "Critical") &
               (asset.last_service_date < today - timedelta(days=30))]
    add("Q12", "ontology-rules", "Which Critical assets are overdue for service (more than 30 days since the last "
        "service)?", "; ".join(f"{a.asset_id} ({a.asset_type}, {venue.loc[a.venue_id].venue_name}, last service "
                               f"{a.last_service_date.isoformat()})" for a in od.itertuples()) or "None",
        ["ontology"])

    # Q14 row-level security
    add("Q14", "security-row-level", "Signed in as the Norway viewer test user: show the medal counts for every NOC.",
        "Only Norway (NOR) is returned; other NOCs are filtered out by row-level security",
        ["semantic model metric"], "Run as noc.nor.viewer test user mapped in security_noc_user.")

    # Q15 live
    add("Q15", "live-eventhouse", "Who leads the Women's 10 km Pursuit at the latest checkpoint?",
        "Computed at run time from TimingEvents streamed by the simulator", ["ontology time series"],
        f"Live session {gd.scenario['live_session_id']}; start the stream simulator first.")

    # Q16 suppliers of critical assets at venues with open findings
    open_v = set(findings[findings.finding_status == "Open"].venue_id)
    sup = t["supplier"].set_index("supplier_id")
    ca = asset[(asset.criticality == "Critical") & asset.venue_id.isin(open_v)]
    add("Q16", "ontology-relationships", "Which suppliers maintain Critical assets at venues that have open "
        "inspection findings?", ", ".join(sorted(sup.loc[ca.supplier_id.unique()].supplier_name)),
        ["ontology"])

    # Q17 inspector question
    f0 = open_high.iloc[0] if len(open_high) else findings.iloc[0]
    reg = register.set_index("document_id").loc[f0.document_id]
    add("Q17", "documents", f"What did the {_d(f0.inspection_date)} inspection of "
        f"{venue.loc[f0.venue_id].venue_name} find?",
        f"{f0.finding_id} ({f0.severity}, {f0.category}): {f0.description} Recommendation: {f0.recommendation}",
        ["documents"], f"Source document {reg.name}.")

    # Q18 optional work context
    add("Q18", "work-context-optional", "Summarise recent emails and meetings about Ice Arena gate operations.",
        "Depends on the tenant's Microsoft 365 content; check that only permitted content is cited",
        ["Work IQ"], "Optional; requires Work IQ setup and seeded mailbox content.")
    return pd.DataFrame(q)
