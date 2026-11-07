"""Synthetic unstructured documents (PDF) and their register.

Produces venue operations manuals (current and superseded versions), inspection reports
with findings, cluster transport plans and Games-wide policies. Inspection findings are
also returned as a ground-truth table, used to evaluate AI extraction (path A) and as an
optional pre-extracted ``finding`` table.
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

from reference import CROWD_DENSITY_LIMIT, DISCIPLINES, INSPECTORS
from tables import GamesData
from themes import DISCLAIMER

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    HAVE_PDF = True
except ImportError:  # pragma: no cover - Markdown fallback
    HAVE_PDF = False

FINDING_TEMPLATES = {
    "Safety": [("Barrier padding missing at two points along the spectator rail.",
                "Fit padding before the next session and record the check in the venue log.")],
    "Technical systems": [("Backup power changeover took longer than the specified 10 seconds during the test.",
                           "Repeat the changeover test with the supplier and adjust the transfer switch."),
                          ("Intermittent loss of signal between the timing system and the venue scoreboard.",
                           "Replace the fibre patch lead and run a full timing rehearsal.")],
    "Crowd management": [("Wayfinding signage at the gate plaza is obscured by temporary fencing.",
                          "Move the signage and add two volunteers at the plaza during ingress.")],
    "Accessibility": [("Accessible viewing platform ramp exceeds the planned gradient on the last section.",
                       "Install a temporary handrail and assign a steward until the ramp is regraded.")],
    "Field of play": [("Surface preparation log incomplete for the last two training sessions.",
                       "Complete the log and confirm sign-off by the field-of-play manager.")],
    "Environmental": [("Waste segregation bins missing in the concourse food area.",
                       "Add bins and brief the catering team on segregation.")],
}


def _pdf(path, title, meta_rows, sections, findings_table=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not HAVE_PDF:
        with open(path.replace(".pdf", ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            for k, v in meta_rows:
                f.write(f"- **{k}:** {v}\n")
            f.write(f"\n_{DISCLAIMER}_\n\n")
            for h, paras in sections:
                f.write(f"## {h}\n\n" + "\n\n".join(paras) + "\n\n")
            if findings_table:
                f.write("| " + " | ".join(findings_table[0]) + " |\n")
                f.write("|" + "---|" * len(findings_table[0]) + "\n")
                for r in findings_table[1:]:
                    f.write("| " + " | ".join(str(c) for c in r) + " |\n")
        return
    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    small = styles["BodyText"].clone("small", fontSize=8, leading=10)
    doc = SimpleDocTemplate(path, pagesize=A4, title=title, author="Synthetic data generator",
                            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    flow = [Paragraph(title, styles["Title"])]
    mt = Table([[Paragraph(f"<b>{k}</b>", small), Paragraph(str(v), small)] for k, v in meta_rows],
               colWidths=[4.5 * cm, 12 * cm])
    mt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke)]))
    flow += [mt, Spacer(1, 6), Paragraph(f"<i>{DISCLAIMER}</i>", small), Spacer(1, 8)]
    for h, paras in sections:
        flow.append(Paragraph(h, styles["Heading2"]))
        for p in paras:
            flow.append(Paragraph(p, body))
    if findings_table:
        flow.append(Paragraph("Findings", styles["Heading2"]))
        data = [[Paragraph(f"<b>{c}</b>", small) for c in findings_table[0]]]
        data += [[Paragraph(str(c), small) for c in r] for r in findings_table[1:]]
        ft = Table(data, colWidths=[2.2 * cm, 1.7 * cm, 2.4 * cm, 2.3 * cm, 4.2 * cm, 4.2 * cm], repeatRows=1)
        ft.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        flow.append(ft)
    doc.build(flow)


def build_documents(gd: GamesData, theme: dict, out_dir: str | None, seed: int = 11):
    """Write PDFs to ``out_dir`` (skip writing when None); return register and findings."""
    rng = np.random.default_rng(seed)
    t = gd.tables
    venues = t["venue"].set_index("venue_id")
    gates = t["gate"]
    assets = t["asset"]
    start = gd.start_date
    as_of_d = gd.as_of.date()
    register, findings = [], []
    discs_at = {v: [n for c, n, s, vv, k in DISCIPLINES if vv == v] for v in venues.index}

    def add_doc(doc_id, title, dtype, venue_id, version, status, eff, sens, sub, fname):
        register.append(dict(document_id=doc_id, title=title, document_type=dtype, venue_id=venue_id,
                             version=version, document_status=status, effective_date=eff,
                             sensitivity=sens, file_name=fname,
                             onelake_path=f"Files/documents/{sub}/{fname}"))
        return os.path.join(out_dir, sub, fname) if out_dir else None

    # ---------------- venue operations manuals
    superseded = {"V08": 18.0, "V07": 5.0}
    for vid, v in venues.iterrows():
        versions = [("2.1", "Current", start - timedelta(days=21), v.wind_limit_ms)]
        if vid in superseded:
            versions.insert(0, ("1.0", "Superseded", start - timedelta(days=160), superseded[vid]))
        for ver, status, eff, wind in versions:
            doc_id = f"DOC-MAN-{vid}-{ver.replace('.', '')}"
            fname = f"{doc_id}.pdf"
            title = f"{v.venue_name} Operations Manual"
            path = add_doc(doc_id, title, "Venue operations manual", vid, ver, status, eff,
                           "General", "manuals", fname)
            gl = gates[gates.venue_id == vid]
            gate_txt = "; ".join(f"{g.gate_id} (plaza {g.plaza_area_m2} m², design throughput "
                                 f"{g.max_entries_per_min} people per minute)" for g in gl.itertuples())
            crit = sorted(assets[(assets.venue_id == vid) & (assets.criticality == "Critical")].asset_type.unique())
            if v.environment == "outdoor":
                weather = [
                    f"Competition must not start, and must be interrupted, when the wind gust measured at the venue "
                    f"weather station exceeds <b>{wind:.1f} m/s</b> for three consecutive minutes.",
                    "The competition jury may hold the start for up to 30 minutes. If conditions do not improve, "
                    "the Venue Operations Centre requests a postponement from the Main Operations Centre and the "
                    "session is rescheduled under the Games-wide weather contingency procedure.",
                    "Visibility below 1 000 metres on the course is treated in the same way as an excess wind gust.",
                ]
            else:
                weather = [
                    "Indoor climate targets: air temperature 15–18 °C at spectator level and relative humidity below "
                    "55 percent, to protect the ice surface.",
                    "An alarm on the ice refrigeration plant must be acknowledged within 5 minutes and escalated to "
                    "the supplier on duty within 15 minutes.",
                ]
            sections = [
                ("1. Purpose and scope", [
                    f"This manual sets the operating rules for {v.venue_name} during the {theme['games_short']}. "
                    f"It applies to venue staff, contractors and volunteers. This is version {ver}."]),
                ("2. Venue profile", [
                    f"Cluster: {v.cluster_name}. Environment: {v.environment}. Seating capacity: "
                    f"{v.seating_capacity:,} spectators. Disciplines: {', '.join(discs_at[vid])}.",
                    f"Spectator gates: {gate_txt}."]),
                ("3. Weather and field-of-play limits", weather),
                ("4. Crowd management", [
                    f"Gate plaza density must not exceed <b>{CROWD_DENSITY_LIMIT:.1f} persons per square metre</b> "
                    "for five minutes or more. When the limit is reached the gate supervisor opens the overflow lane, "
                    "the transport hub holds arriving shuttles for 10 minutes, and a public address announcement "
                    "redirects spectators to the nearest gate with spare capacity.",
                    "Density readings come from the gate counting sensors and are shown on the venue operations "
                    "dashboard in real time."]),
                ("5. Critical assets and escalation", [
                    f"Critical assets at this venue: {', '.join(crit)}.",
                    "A High-severity inspection finding on a Critical asset must be resolved before the next "
                    "competition session. Otherwise the session needs written sign-off from the Venue General "
                    "Manager and the Main Operations Centre.",
                    "Critical assets are serviced at least every 30 days during the Games period."]),
                ("6. Contacts", ["Venue General Manager; Venue Operations Centre duty manager; competition "
                                 "manager; medical services lead. Contact details are held in the accreditation "
                                 "system and are not reproduced in this manual."]),
            ]
            if path:
                # The PDF shows the status as issued. Whether a version is Current or Superseded is held
                # only in the document register, as with outdated copies in real file shares.
                _pdf(path, title, [("Document ID", doc_id), ("Venue", f"{v.venue_name} ({vid})"),
                                   ("Version", ver), ("Status", "Approved"), ("Effective date", eff.isoformat()),
                                   ("Classification", "General"), ("Issued by", theme["organiser"])], sections)

    # ---------------- inspection reports and findings
    scripted = {
        ("V10", 8): [("High", "Technical systems", gd.scenario["refrigeration_asset_id"],
                      "Brine return temperature on the track refrigeration plant has risen steadily since the "
                      "previous day; compressor 2 shows vibration above its baseline.",
                      "Replace the compressor 2 bearing before the next sliding session and run the plant on the "
                      "redundant compressor until the repair is complete.", "Open", 1)],
        ("V08", 6): [("Medium", "Safety", gd.scenario["overdue_netting_asset_id"],
                      "Safety netting section B tension is below specification; the last recorded service was 45 "
                      "days before this inspection, beyond the 30-day interval.",
                      "Re-tension and service section B and update the service record before the next downhill "
                      "training run.", "Open", 4)],
        ("V01", 8): [("Medium", "Crowd management", None,
                      "Gate 2 plaza density stayed above 4.0 persons per square metre for about 14 minutes before "
                      "the afternoon session.",
                      "Open the Gate 3 overflow lane 45 minutes before start and stagger shuttle arrivals from the "
                      "transport hub.", "Open", 3)],
        ("V07", 3): [("Low", "Technical systems", None,
                      "Weather station anemometer reported a 20-second data gap during the wind hold.",
                      "Check the data logger power supply and confirm the backup anemometer feed.", "Closed", 1)],
    }
    plan = []
    for vid in venues.index:
        plan += [(vid, -12), (vid, -4)]
        day = int(rng.integers(2, 9))
        plan.append((vid, day))
    plan += [k for k in scripted if k not in plan]
    plan = sorted(set(plan), key=lambda p: (p[1], p[0]))
    n_rep = 0
    for vid, day in plan:
        n_rep += 1
        insp_date = start + timedelta(days=day - 1) if day > 0 else start + timedelta(days=day)
        if insp_date > as_of_d:
            continue
        v = venues.loc[vid]
        doc_id = f"DOC-IR-{n_rep:04d}"
        fname = f"{doc_id}.pdf"
        title = f"Venue Inspection Report: {v.venue_name}"
        sens = "Confidential" if n_rep % 7 == 0 else "General"
        path = add_doc(doc_id, title, "Inspection report", vid, "1.0", "Current", insp_date, sens,
                       "inspections", fname)
        inspector = INSPECTORS[int(rng.integers(0, len(INSPECTORS)))]
        rows = []
        if (vid, day) in scripted:
            items = scripted[(vid, day)]
        else:
            items = []
            for _ in range(int(rng.integers(1, 4))):
                cat = str(rng.choice(list(FINDING_TEMPLATES)))
                desc, rec = FINDING_TEMPLATES[cat][int(rng.integers(0, len(FINDING_TEMPLATES[cat])))]
                sev = str(rng.choice(["Low", "Medium", "High"], p=[0.5, 0.38, 0.12]))
                va = assets[assets.venue_id == vid]
                aid = va.asset_id.iloc[int(rng.integers(0, len(va)))] if cat == "Technical systems" else None
                due_days = int(rng.integers(1, 6))
                due = insp_date + timedelta(days=due_days)
                status = "Closed" if (sev == "High" or due < as_of_d and rng.random() < 0.8) else "Open"
                items.append((sev, cat, aid, desc, rec, status, due_days))
        for k, (sev, cat, aid, desc, rec, status, due_days) in enumerate(items, start=1):
            fid = f"F-{n_rep:04d}-{k}"
            due = insp_date + timedelta(days=due_days)
            findings.append(dict(finding_id=fid, document_id=doc_id, venue_id=vid, asset_id=aid,
                                 inspection_date=insp_date, severity=sev, category=cat, description=desc,
                                 recommendation=rec, finding_status=status, due_date=due))
            rows.append([fid, sev, cat, aid or "-", desc, f"{rec} (Status: {status}; due {due.isoformat()})"])
        if path:
            sections = [("Scope", [f"Routine inspection of {v.venue_name} carried out on {insp_date.isoformat()} "
                                   f"by {inspector}. The inspection covered spectator areas, field of play and "
                                   "technical systems."]),
                        ("Summary", [f"{len(rows)} finding(s) recorded. Severity follows the Games-wide "
                                     "inspection standard: High findings on Critical assets block the next "
                                     "session unless signed off by the Venue General Manager."])]
            _pdf(path, title, [("Document ID", doc_id), ("Venue", f"{v.venue_name} ({vid})"),
                               ("Inspection date", insp_date.isoformat()), ("Inspector", inspector),
                               ("Status", "Current"), ("Classification", sens)], sections,
                 [["Finding ID", "Severity", "Category", "Asset", "Observation", "Recommendation"]] + rows)

    # ---------------- transport plans
    for cluster, code in [("Valmont Ice Cluster", "ICE"), ("Ridge and Summit Mountain Clusters", "MTN")]:
        doc_id = f"DOC-TRN-{code}"
        fname = f"{doc_id}.pdf"
        title = f"Spectator Transport Plan: {cluster}"
        path = add_doc(doc_id, title, "Transport plan", None, "1.2", "Current", start - timedelta(days=14),
                       "General", "transport", fname)
        if path:
            freq = "every 4 minutes" if code == "ICE" else "every 8 minutes"
            _pdf(path, title, [("Document ID", doc_id), ("Version", "1.2"), ("Status", "Current"),
                               ("Classification", "General")],
                 [("Service pattern", [f"Shuttles run {freq} from 2 hours before the first session until 90 "
                                       "minutes after the last session. Peak arrivals are expected 30 to 45 minutes "
                                       "before session start."]),
                  ("Crowd interface", ["When a venue gate reports density above the crowd management limit, the "
                                       "transport hub holds arriving shuttles for 10 minutes and redirects "
                                       "passengers to the next gate with spare capacity."]),
                  ("Weather", ["Mountain shuttles switch to the snow-route timetable when snowfall exceeds "
                               "5 cm per hour; journey times increase by about 15 minutes."])])

    # ---------------- Games-wide policies
    policies = [
        ("DOC-POL-CROWD", "Games-wide Crowd Management Standard", "General",
         [("Density limit", [f"The Games-wide crowd density limit at gate plazas is {CROWD_DENSITY_LIMIT:.1f} "
                             "persons per square metre sustained for five minutes. Venues may set a lower limit "
                             "in their operations manual but never a higher one."]),
          ("Escalation", ["Breaches are reported to the Main Operations Centre within 10 minutes with the gate, "
                          "duration and actions taken."])]),
        ("DOC-POL-WEATHER", "Weather Contingency Procedure", "General",
         [("Holds and postponements", ["The competition jury may hold a start for up to 30 minutes. The Main "
                                       "Operations Centre approves a postponement and publishes the new session "
                                       "time within 60 minutes."]),
          ("Authoritative limits", ["The wind limit that applies is the one in the current version of the venue "
                                    "operations manual. Superseded versions must not be used."])]),
        ("DOC-POL-ACCRED", "Accreditation and Access Control Policy", "Confidential",
         [("Zones", ["Access to the field of play, technical rooms and the Venue Operations Centre requires the "
                     "matching zone code on the accreditation card."]),
          ("Lost cards", ["Lost cards are cancelled within 15 minutes and reissued only at the main "
                          "accreditation centre."])]),
    ]
    for doc_id, title, sens, sections in policies:
        fname = f"{doc_id}.pdf"
        path = add_doc(doc_id, title, "Games-wide policy", None, "3.0", "Current", start - timedelta(days=30),
                       sens, "policies", fname)
        if path:
            _pdf(path, title, [("Document ID", doc_id), ("Version", "3.0"), ("Status", "Current"),
                               ("Classification", sens), ("Issued by", theme["authority"])], sections)

    reg = pd.DataFrame(register)
    fnd = pd.DataFrame(findings)
    return reg, fnd
