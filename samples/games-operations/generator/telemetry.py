"""Historical telemetry for the eventhouse (real-time intelligence) tables.

Covers two days before the opening day up to the as-of time. Scripted anomalies:
- wind gusts above the Ski Jumping Hill limit before the day-3 final (postponement);
- a crowd density spike at one Ice Arena gate before an evening session on day 8;
- a rising brine temperature on the Sliding Centre track refrigeration plant from day 7.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from tables import GamesData

SHOOTING = {"BTH-M20I": 4, "BTH-W15I": 4, "BTH-M10S": 2, "BTH-W75S": 2, "BTH-M125P": 4, "BTH-W10P": 4}
CCS_CHECKPOINTS = 4


def _minutes(start: datetime, end: datetime, step: int):
    n = int((end - start).total_seconds() // (60 * step))
    return pd.date_range(start, periods=n, freq=f"{step}min")


def build_telemetry(gd: GamesData, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    t = gd.tables
    start = datetime.combine(gd.start_date, datetime.min.time()) - timedelta(days=2)
    end = gd.as_of
    venues = t["venue"]
    session = t["session"]

    # ---------------- VenueConditions (1 minute)
    idx = _minutes(start, end, 1)
    hours = np.asarray(idx.hour + idx.minute / 60.0, dtype=float)
    frames = []
    postponed = session[session.session_id == gd.scenario["postponed_session_id"]].iloc[0]
    wind_from = postponed.start_time_utc - timedelta(minutes=90)
    wind_to = postponed.start_time_utc + timedelta(minutes=75)
    gd.scenario["wind_anomaly"] = (wind_from, wind_to)
    for v in venues.itertuples():
        n = len(idx)
        if v.environment == "outdoor":
            limit = v.wind_limit_ms
            base = limit * 0.38 + 0.12 * limit * np.sin((hours - 14) / 24 * 2 * np.pi)
            wind = np.clip(base + rng.normal(0, limit * 0.06, n), 0.2, None)
            gust = np.minimum(wind * 1.35 + np.abs(rng.normal(0, limit * 0.05, n)), limit * 0.88)
            air = -6 + 5 * np.sin((hours - 9) / 24 * 2 * np.pi) + rng.normal(0, 0.4, n)
            snow = air - 2 + rng.normal(0, 0.3, n)
            hum = np.clip(70 + rng.normal(0, 6, n), 35, 99)
            vis = np.clip(9000 + rng.normal(0, 1500, n), 800, 10000).astype(int)
            if v.venue_id == "V07":
                m = (idx >= wind_from) & (idx < wind_to)
                k = int(m.sum())
                wind[m] = limit * rng.uniform(1.0, 1.3, k)
                gust[m] = limit * rng.uniform(1.15, 1.65, k)
                vis[m] = rng.integers(1500, 4000, k)
        else:
            wind = np.zeros(n)
            gust = np.zeros(n)
            air = 16 + rng.normal(0, 0.5, n)
            snow = np.full(n, np.nan)
            hum = np.clip(42 + rng.normal(0, 3, n), 30, 60)
            vis = np.full(n, 10000)
        frames.append(pd.DataFrame(dict(Timestamp=idx, VenueId=v.venue_id,
                                        WindSpeedMs=np.round(wind, 2), WindGustMs=np.round(gust, 2),
                                        AirTempC=np.round(air, 2), SnowTempC=np.round(snow, 2),
                                        HumidityPct=np.round(hum, 1), VisibilityM=vis)))
    venue_conditions = pd.concat(frames, ignore_index=True)

    # ---------------- GateFlow (1 minute around each session up to as-of)
    gates = t["gate"]
    tick = t["session_ticketing"].set_index("session_id")
    spike_gate = gd.scenario["crowd_spike_gate"]
    v01_day8 = session[(session.venue_id == "V01") & (session.competition_day == 8)]
    spike_session = v01_day8.sort_values("start_time_utc").iloc[-1]
    spike_from = spike_session.start_time_utc - timedelta(minutes=22)
    spike_to = spike_from + timedelta(minutes=14)
    gd.scenario["crowd_spike"] = (spike_session.session_id, spike_from, spike_to)
    gframes = []
    for s in session.itertuples():
        if s.start_time_utc - timedelta(minutes=90) >= end or s.session_status == "Postponed":
            continue
        w_start = s.start_time_utc - timedelta(minutes=90)
        w_end = min(s.start_time_utc + timedelta(minutes=30), end)
        if w_end <= w_start:
            continue
        widx = _minutes(w_start, w_end, 1)
        mins_to_start = np.array([(x - s.start_time_utc).total_seconds() / 60 for x in widx])
        curve = np.exp(-((mins_to_start + 25) ** 2) / (2 * 22 ** 2))
        vg = gates[gates.venue_id == s.venue_id]
        sold = tick.loc[s.session_id, "tickets_sold"]
        for g in vg.itertuples():
            peak_density = rng.uniform(1.4, 3.1)
            density = np.clip(peak_density * curve + rng.normal(0, 0.08, len(widx)), 0, None)
            if g.gate_id == spike_gate and s.session_id == spike_session.session_id:
                m = (widx >= spike_from) & (widx < spike_to)
                density[m] = rng.uniform(4.25, 4.95, int(m.sum()))
            entries = np.clip(sold / len(vg) / 60 * curve * 2.2 + rng.normal(0, 2, len(widx)), 0,
                              g.max_entries_per_min).astype(int)
            gframes.append(pd.DataFrame(dict(Timestamp=widx, GateId=g.gate_id, VenueId=s.venue_id,
                                             EntriesPerMin=entries,
                                             QueueingPersons=(density * g.plaza_area_m2).astype(int),
                                             DensityPersonsPerM2=np.round(density, 2))))
    gate_flow = pd.concat(gframes, ignore_index=True).sort_values(["Timestamp", "GateId"])

    # ---------------- AssetTelemetry (5 minutes, monitored assets)
    aidx = _minutes(start, end, 5)
    assets = t["asset"][t["asset"].is_monitored]
    ref_id = gd.scenario["refrigeration_asset_id"]
    drift_from = datetime.combine(gd.start_date, datetime.min.time()) + timedelta(days=6, hours=12)
    aframes = []
    for a in assets.itertuples():
        n = len(aidx)
        if "refrigeration" in a.asset_type:
            temp = -10 + rng.normal(0, 0.25, n)
            power = 180 + rng.normal(0, 8, n)
            if a.asset_id == ref_id:
                hrs = np.array([(x - drift_from).total_seconds() / 3600 for x in aidx])
                drift = np.clip(hrs, 0, None) * 0.07
                temp = temp + np.minimum(drift, 3.6)
                power = power + np.minimum(drift, 3.6) * 22
        elif a.asset_type == "HVAC and dehumidification unit":
            temp = 14 + rng.normal(0, 0.6, n)
            power = 60 + rng.normal(0, 5, n)
        elif a.asset_type == "Snowmaking unit":
            on = np.asarray((aidx.hour < 6) | (aidx.hour >= 22))
            temp = -4 + rng.normal(0, 0.8, n)
            power = np.where(on, 95 + rng.normal(0, 6, n), 2 + rng.normal(0, 0.5, n))
        elif a.asset_type == "Backup generator":
            temp = 21 + rng.normal(0, 0.8, n)
            power = np.zeros(n)
        else:  # weather station and others
            temp = 5 + rng.normal(0, 0.5, n)
            power = 0.4 + rng.normal(0, 0.02, n)
        status = np.where(temp > -8.0, "WARNING", "OK") if "refrigeration" in a.asset_type else np.full(n, "OK")
        if "refrigeration" in a.asset_type:
            status = np.where(temp > -6.8, "ALARM", status)
        aframes.append(pd.DataFrame(dict(Timestamp=aidx, AssetId=a.asset_id, VenueId=a.venue_id,
                                         TemperatureC=np.round(temp, 2), PowerKw=np.round(power, 1),
                                         StatusCode=status)))
    asset_telemetry = pd.concat(aframes, ignore_index=True).sort_values(["Timestamp", "AssetId"])

    # ---------------- TimingEvents (completed biathlon and cross-country medal sessions)
    timing = []
    sess = session.set_index("session_id")
    for sid, ev, finals in gd.scenario["timing_plan"]:
        timing.extend(timing_rows(sess.loc[sid].start_time_utc, sid, ev, finals, rng))
    timing_events = pd.DataFrame(timing).sort_values(["Timestamp", "Bib"]) if timing else pd.DataFrame()

    return dict(VenueConditions=venue_conditions, GateFlow=gate_flow,
                AssetTelemetry=asset_telemetry, TimingEvents=timing_events)


def checkpoint_plan(event_id: str):
    """Return [(checkpoint, lap, fraction_of_total, is_shooting)] for an event."""
    if event_id.startswith("BTH"):
        shots = SHOOTING.get(event_id, 2)
        laps = shots + 1
        plan = []
        for lap in range(1, laps + 1):
            frac = lap / laps
            plan.append((f"Lap {lap}", lap, frac * 0.97 if lap < laps else 1.0, False))
            if lap <= shots:
                plan.append((f"Shooting {lap}", lap, frac * 0.97 + 0.005, True))
        plan[-1] = ("Finish", laps, 1.0, False)
        return plan
    return [(f"Split {k}" if k < CCS_CHECKPOINTS else "Finish", k, k / CCS_CHECKPOINTS, False)
            for k in range(1, CCS_CHECKPOINTS + 1)]


def timing_rows(session_start, sid, ev, finals, rng, interval_s: int = 30):
    """Checkpoint rows that end exactly on each athlete's final mark."""
    plan = checkpoint_plan(ev)
    rows = []
    mass_start = ev.endswith("P")  # pursuit: near-simultaneous start
    for order, (aid, bib, mark) in enumerate(sorted(finals, key=lambda f: f[1])):
        offset = (order * 3 if mass_start else order * interval_s)
        for cp, lap, frac, shooting in plan:
            split = mark if cp == "Finish" else mark * frac * (1 + rng.normal(0, 0.004))
            rows.append(dict(Timestamp=session_start + timedelta(seconds=offset + split),
                             SessionId=sid, EventId=ev, AthleteId=aid, Bib=bib, Checkpoint=cp,
                             LapNumber=lap, SplitTimeS=round(float(split), 2),
                             ShootingMisses=int(rng.choice([0, 0, 0, 1, 1, 2])) if shooting else None,
                             RankAtCheckpoint=None))
    df = pd.DataFrame(rows)
    df["RankAtCheckpoint"] = df.groupby("Checkpoint")["SplitTimeS"].rank(method="first").astype(int)
    df["ShootingMisses"] = df["ShootingMisses"].astype("Int64")
    return df.to_dict("records")
