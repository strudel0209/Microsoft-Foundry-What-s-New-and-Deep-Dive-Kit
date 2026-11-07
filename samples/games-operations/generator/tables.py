"""Master and transactional tables for the synthetic Games operations sample.

All timestamps are UTC. Venue local time is UTC+1 (stated in the documents).
The generator is deterministic for a given seed, start date and as-of time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd

from reference import (ASSET_SUPPLIER, ASSET_TYPES, CROWD_DENSITY_LIMIT, DISCIPLINES, EVENTS,
                       FIRST_NAMES, LAST_NAMES, NOCS, SUPPLIERS, VENUES)

GAMES_DAYS = 14

# Session slots (UTC start hour, minute, duration minutes)
INDOOR_SLOTS = [(9, 0, 150), (13, 30, 150), (18, 30, 150), (21, 15, 105)]
OUTDOOR_SLOTS = [(9, 30, 120), (12, 30, 120), (16, 30, 120), (19, 0, 90)]

# Base winning marks for timed events, seconds (synthetic)
BASE_MARK = {
    "BTH-M20I": 2900, "BTH-W15I": 2500, "BTH-M10S": 1460, "BTH-W75S": 1230,
    "BTH-M125P": 1950, "BTH-W10P": 1790, "CCS-M10": 1500, "CCS-W10": 1700,
    "CCS-MSP": 175, "CCS-WSP": 200, "ALP-MDH": 104, "ALP-WDH": 98, "ALP-MGS": 135,
    "ALP-WGS": 130, "ALP-MSL": 98, "ALP-WSL": 96, "SSK-M500": 34.3, "SSK-W500": 37.1,
    "SSK-M1500": 103.5, "SSK-W1500": 113.0, "BOB-WMB": 238.0, "BOB-MLS": 211.0,
    "BOB-WLS": 211.5,
}
JUDGED_BASE = {"SJP": 280.0, "SBD": 92.0, "FSK": 270.0}

# Scripted scenario identifiers (documented in the README and used by the evaluation set)
SCENARIO = {
    "wind_postponement_event": "SJP-MNH",      # day 3 final postponed for wind at V07
    "crowd_spike_gate": "V01-G2",               # day 8 evening density spike at the Ice Arena
    "refrigeration_asset_venue": "V10",         # open High finding on the track refrigeration plant
    "overdue_netting_venue": "V08",             # safety netting overdue for service
    "live_session_event": "BTH-W10P",           # day 9 session streamed live by the simulator
}


@dataclass
class GamesData:
    start_date: date
    as_of: datetime
    tables: dict = field(default_factory=dict)
    scenario: dict = field(default_factory=dict)


def _day_date(start: date, day: int) -> date:
    return start + timedelta(days=day - 1)


def _ts(d: date, h: int, m: int) -> datetime:
    return datetime.combine(d, time(h, m))


def build_tables(start_date: date, as_of: datetime, seed: int = 2026) -> GamesData:
    rng = np.random.default_rng(seed)
    gd = GamesData(start_date=start_date, as_of=as_of)
    strength = {c: s for c, _, _, s in NOCS}
    venue_by_id = {v[0]: v for v in VENUES}
    disc_by_code = {d[0]: d for d in DISCIPLINES}

    # ---------------- venues and gates
    venue_rows, gate_rows = [], []
    for i, (vid, name, cluster, env, cap, gates, wind) in enumerate(VENUES):
        venue_rows.append(dict(
            venue_id=vid, venue_name=name, cluster_name=cluster, environment=env,
            seating_capacity=cap, gate_count=gates, wind_limit_ms=wind,
            crowd_density_limit=CROWD_DENSITY_LIMIT,
            latitude=round(46.10 + 0.012 * i + (0.08 if env == "outdoor" else 0), 5),
            longitude=round(7.20 + 0.017 * i, 5)))
        for g in range(1, gates + 1):
            gate_rows.append(dict(
                gate_id=f"{vid}-G{g}", venue_id=vid, gate_name=f"{name} Gate {g}",
                plaza_area_m2=int(rng.integers(450, 800)),
                max_entries_per_min=int(rng.integers(90, 160))))
    venue = pd.DataFrame(venue_rows)
    gate = pd.DataFrame(gate_rows)

    # ---------------- disciplines, events
    discipline = pd.DataFrame([dict(discipline_code=c, discipline_name=n, sport_name=s,
                                    venue_id=v, scoring_type=k) for c, n, s, v, k in DISCIPLINES])
    event = pd.DataFrame([dict(event_id=e, discipline_code=d, event_name=n, gender_category=g,
                               is_team_event=t, medal_date=_day_date(start_date, md),
                               has_qualification=q) for e, d, n, g, t, md, q in EVENTS])

    # ---------------- sessions
    plan = []  # (venue_id, day, event_id, session_type, phase)
    for e, d, n, g, team, md, q in EVENTS:
        vid = disc_by_code[d][3]
        if team and d in ("IHO", "CUR"):
            first = max(1, md - 8)
            for day in range(first, md):
                plan.append((vid, day, e, "Preliminary round", "Round robin"))
            plan.append((vid, md, e, "Medal game", "Medal game"))
        else:
            if q:
                plan.append((vid, md - 1 if d in ("SJP", "FSK", "CCS") else md, e,
                             "Qualification", "Qualification"))
            plan.append((vid, md, e, "Final", "Final"))
    # stable ordering: qualification before finals, preliminaries before medal games
    order = {"Qualification": 0, "Preliminary round": 1, "Final": 2, "Medal game": 3}
    plan.sort(key=lambda p: (p[0], p[1], order[p[3]], p[2]))

    session_rows, se_rows = [], []
    used = {}
    fixed = {("BTH-W10P", "Final"): 1, ("SJP-MNH", "Final"): 2}  # slot index overrides
    for vid, day, e, stype, phase in plan:
        env = venue_by_id[vid][3]
        slots = INDOOR_SLOTS if env == "indoor" else OUTDOOR_SLOTS
        taken = used.setdefault((vid, day), set())
        idx = fixed.get((e, stype))
        if idx is None or idx in taken:
            idx = next(i for i in range(len(slots)) if i not in taken)
        taken.add(idx)
        h, m, dur = slots[idx]
        d0 = _day_date(start_date, day)
        sid = f"S-{vid}-D{day:02d}-{idx + 1}"
        st = _ts(d0, h, m)
        session_rows.append(dict(session_id=sid, venue_id=vid, competition_day=day,
                                 session_date=d0, start_time_utc=st,
                                 end_time_utc=st + timedelta(minutes=dur),
                                 session_type=stype, session_status=None, status_reason=None))
        se_rows.append(dict(session_id=sid, event_id=e, phase=phase))

    # Scripted: wind postponement of the day-3 ski jumping final to day 4 evening
    sj_final = next(r for r, s in zip(session_rows, se_rows)
                    if s["event_id"] == SCENARIO["wind_postponement_event"] and s["phase"] == "Final")
    sj_final["status_reason"] = "Postponed: wind gusts above the venue operating limit"
    d4 = _day_date(start_date, sj_final["competition_day"] + 1)
    new_sid = f"S-V07-D{sj_final['competition_day'] + 1:02d}-R"
    session_rows.append(dict(session_id=new_sid, venue_id="V07",
                             competition_day=sj_final["competition_day"] + 1, session_date=d4,
                             start_time_utc=_ts(d4, 19, 0), end_time_utc=_ts(d4, 20, 45),
                             session_type="Final", session_status=None,
                             status_reason=f"Rescheduled from {sj_final['session_id']}"))
    se_rows.append(dict(session_id=new_sid, event_id=SCENARIO["wind_postponement_event"],
                        phase="Final (rescheduled)"))

    for r in session_rows:
        if r["status_reason"] and r["status_reason"].startswith("Postponed"):
            r["session_status"] = "Postponed"
        elif r["end_time_utc"] <= as_of:
            r["session_status"] = "Completed"
        elif r["start_time_utc"] <= as_of < r["end_time_utc"]:
            r["session_status"] = "In progress"
        else:
            r["session_status"] = "Scheduled"
    session = pd.DataFrame(session_rows).sort_values(["session_date", "start_time_utc", "venue_id"])
    session_event = pd.DataFrame(se_rows)

    # ---------------- athletes and entries
    athletes, entries = [], []
    pools = {}
    used_names = set()
    a_counter = [0]

    def new_athlete(noc, disc, gender):
        a_counter[0] += 1
        while True:
            gn, fn = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
            if (gn, fn, noc) not in used_names:
                used_names.add((gn, fn, noc))
                break
        aid = f"A{a_counter[0]:05d}"
        athletes.append(dict(athlete_id=aid, given_name=str(gn), family_name=str(fn),
                             gender_category=gender, birth_year=int(rng.integers(1994, 2008)),
                             noc_code=noc, discipline_code=disc))
        return aid

    codes = np.array([c for c, *_ in NOCS])
    weights = np.array([s for *_, s in NOCS])
    weights = weights / weights.sum()
    bib_counter = {}
    team_participants = {}
    for e, d, n, g, team, md, q in EVENTS:
        genders = ["M", "W"] if g == "X" else [g]
        if team:
            n_teams = {"IHO": 10, "CUR": 10}.get(d, 18)
            nocs = rng.choice(codes, size=n_teams, replace=False, p=weights)
            team_participants[e] = list(nocs)
            members = {"IHO": 18, "CUR": 4}.get(d, 2 if e != "BTH-XREL" else 4)
            if e == "CUR-XD":
                members = 2
            for noc in nocs:
                for k in range(members):
                    gen = genders[k % len(genders)]
                    key = (noc, d, gen, e if d in ("IHO", "CUR") else "pool")
                    pool = pools.setdefault(key, [])
                    if len(pool) < (members // len(genders) + 1):
                        pool.append(new_athlete(noc, d, gen))
                    aid = pool[k // len(genders) % len(pool)]
                    bib_counter[e] = bib_counter.get(e, 0) + 1
                    entries.append(dict(entry_id=f"EN-{e}-{bib_counter[e]:03d}", athlete_id=aid,
                                        event_id=e, bib=bib_counter[e]))
        else:
            n_nocs = int(rng.integers(18, 28))
            nocs = rng.choice(codes, size=n_nocs, replace=False, p=weights)
            for noc in nocs:
                per = 1 + int(strength[noc] > 0.6) + int(strength[noc] > 0.85)
                for gen in genders:
                    pool = pools.setdefault((noc, d, gen, "pool"), [])
                    while len(pool) < per:
                        pool.append(new_athlete(noc, d, gen))
                    for aid in pool[:per]:
                        bib_counter[e] = bib_counter.get(e, 0) + 1
                        entries.append(dict(entry_id=f"EN-{e}-{bib_counter[e]:03d}", athlete_id=aid,
                                            event_id=e, bib=bib_counter[e]))
    athlete = pd.DataFrame(athletes)
    entry = pd.DataFrame(entries)
    ath_noc = dict(zip(athlete.athlete_id, athlete.noc_code))
    skill = {a: strength[ath_noc[a]] + rng.normal(0, 0.18) for a in athlete.athlete_id}

    # ---------------- results (completed sessions only)
    results = []
    r_counter = [0]

    def add_result(e, sid, noc, aid, rank, mark, unit, medal):
        r_counter[0] += 1
        results.append(dict(result_id=f"R{r_counter[0]:06d}", event_id=e, session_id=sid,
                            noc_code=noc, athlete_id=aid, result_rank=int(rank),
                            mark=float(round(mark, 2)), mark_unit=unit, medal=medal))

    sess_idx = session.set_index("session_id")
    timing_plan = []  # (session_id, event_id, [(athlete_id, bib, final_mark)])
    medal_of = {1: "Gold", 2: "Silver", 3: "Bronze"}
    for _, se in session_event.iterrows():
        s = sess_idx.loc[se.session_id]
        if s.session_status != "Completed":
            continue
        e = se.event_id
        d = e.split("-")[0]
        kind = disc_by_code[d][4]
        is_medal = se.phase.startswith("Final") or se.phase == "Medal game"
        if kind == "team" or e in team_participants:
            nocs = team_participants[e]
            if se.phase == "Round robin":
                pair = rng.choice(nocs, size=2, replace=False)
                a, b = sorted(pair, key=lambda c: -(strength[c] + rng.normal(0, 0.25)))
                hi = int(rng.integers(2, 7)) if d == "IHO" else int(rng.integers(6, 10))
                lo = int(rng.integers(0, hi))
                add_result(e, se.session_id, a, None, 1, hi, "score", None)
                add_result(e, se.session_id, b, None, 2, lo, "score", None)
            else:
                ranked = sorted(nocs, key=lambda c: -(strength[c] + rng.normal(0, 0.2)))
                if d in ("IHO", "CUR"):
                    for rank, noc in enumerate(ranked[:3], start=1):
                        add_result(e, se.session_id, noc, None, rank, 4 - rank, "score", medal_of[rank])
                else:  # timed team events (relay, two-man bob)
                    base = 4350.0 if e == "BTH-XREL" else 232.0
                    for rank, noc in enumerate(ranked, start=1):
                        mark = base * (1 + 0.004 * (rank - 1) + abs(rng.normal(0, 0.001)))
                        add_result(e, se.session_id, noc, None, rank, mark, "seconds",
                                   medal_of.get(rank) if is_medal else None)
            continue
        ents = entry[entry.event_id == e]
        ranked = sorted(ents.itertuples(), key=lambda r: -(skill[r.athlete_id] + rng.normal(0, 0.12)))
        finals = []
        for rank, r in enumerate(ranked, start=1):
            if kind == "judged":
                base = JUDGED_BASE[d]
                mark, unit = base * (1 - 0.012 * (rank - 1)) + rng.normal(0, 0.4), "points"
            else:
                base = BASE_MARK[e]
                mark, unit = base * (1 + 0.006 * (rank - 1)) + abs(rng.normal(0, base * 0.0004)), "seconds"
            medal = medal_of.get(rank) if is_medal else None
            add_result(e, se.session_id, ath_noc[r.athlete_id], r.athlete_id, rank, mark, unit, medal)
            finals.append((r.athlete_id, int(r.bib), float(round(mark, 2))))
        if d in ("BTH", "CCS") and is_medal:
            timing_plan.append((se.session_id, e, finals))
    result = pd.DataFrame(results)
    if not result.empty:
        result["athlete_id"] = result["athlete_id"].astype("object")

    # ---------------- national committees
    sizes = athlete.groupby("noc_code").size()
    noc = pd.DataFrame([dict(noc_code=c, noc_name=n, region=r, delegation_size=int(sizes.get(c, 0)))
                        for c, n, r, _ in NOCS])

    # ---------------- ticketing
    tick = []
    for s in session.itertuples():
        cap = venue_by_id[s.venue_id][4]
        seats = int(cap * 0.95)
        fill = rng.uniform(0.86, 0.99) if s.session_type in ("Final", "Medal game") else rng.uniform(0.62, 0.9)
        sold = int(seats * fill)
        scanned = int(sold * rng.uniform(0.86, 0.97)) if s.session_status == "Completed" else None
        tick.append(dict(session_id=s.session_id, seats_available=seats, tickets_sold=sold,
                         scanned_entries=scanned))
    session_ticketing = pd.DataFrame(tick)
    session_ticketing["scanned_entries"] = session_ticketing["scanned_entries"].astype("Int64")

    # ---------------- suppliers and assets
    supplier = pd.DataFrame([dict(supplier_id=s, supplier_name=n, service_category=c)
                             for s, n, c in SUPPLIERS])
    assets = []
    for vid, name, cluster, env, cap, gates, wind in VENUES:
        discs = [d for d, *_rest in DISCIPLINES if _rest[2] == vid]
        n = 0
        for atype, crit, monitored, (lo, hi), applies in ASSET_TYPES:
            if applies == "indoor" and env != "indoor":
                continue
            if applies == "outdoor" and env != "outdoor":
                continue
            if isinstance(applies, list) and not set(applies) & set(discs):
                continue
            for k in range(int(rng.integers(lo, hi + 1))):
                n += 1
                install = start_date - timedelta(days=int(rng.integers(200, 900)))
                last = start_date + timedelta(days=int(rng.integers(-6, 7)))
                assets.append(dict(asset_id=f"{vid}-AS-{n:03d}", venue_id=vid,
                                   asset_name=f"{atype} {k + 1}" if hi > 1 else atype,
                                   asset_type=atype, criticality=crit,
                                   operational_status="Operational", is_monitored=monitored,
                                   supplier_id=ASSET_SUPPLIER[atype], install_date=install,
                                   last_service_date=last))
    asset = pd.DataFrame(assets)
    # Scripted asset states
    ref = asset[(asset.venue_id == SCENARIO["refrigeration_asset_venue"]) &
                (asset.asset_type == "Track refrigeration plant")].index[0]
    asset.loc[ref, "operational_status"] = "Degraded"
    net = asset[(asset.venue_id == SCENARIO["overdue_netting_venue"]) &
                (asset.asset_type == "Safety netting section")].index[0]
    asset.loc[net, "last_service_date"] = start_date - timedelta(days=40)

    # ---------------- RLS test users (placeholders)
    security = pd.DataFrame([
        dict(user_principal_name="noc.nor.viewer@contoso.example", noc_code="NOR"),
        dict(user_principal_name="noc.sui.viewer@contoso.example", noc_code="SUI"),
        dict(user_principal_name="noc.jpn.viewer@contoso.example", noc_code="JPN"),
    ])

    gd.tables.update(dict(noc=noc, discipline=discipline, event=event, venue=venue, gate=gate,
                          session=session.reset_index(drop=True), session_event=session_event,
                          session_ticketing=session_ticketing, athlete=athlete, entry=entry,
                          result=result, asset=asset, supplier=supplier,
                          security_noc_user=security))
    gd.scenario.update(dict(SCENARIO))
    gd.scenario["postponed_session_id"] = sj_final["session_id"]
    gd.scenario["rescheduled_session_id"] = new_sid
    gd.scenario["refrigeration_asset_id"] = asset.loc[ref, "asset_id"]
    gd.scenario["overdue_netting_asset_id"] = asset.loc[net, "asset_id"]
    gd.scenario["timing_plan"] = timing_plan
    gd.scenario["team_participants"] = team_participants
    live = session_event[(session_event.event_id == SCENARIO["live_session_event"])]
    gd.scenario["live_session_id"] = live.session_id.iloc[0]
    return gd
