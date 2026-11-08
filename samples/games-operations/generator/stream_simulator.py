"""Stream live Games telemetry to a Fabric Eventstream (custom endpoint) or to a local file.

Replays the live biathlon session (Women's 10 km Pursuit by default) with current timestamps,
together with weather readings for its venue and gate flow for its gates. Optional scripted
incidents: a crowd density spike at one gate, or a wind gust spike at an outdoor venue.

Every message carries an ``EventType`` field (TimingEvents, VenueConditions, GateFlow) so the
Eventstream can route messages to the matching eventhouse table.

Examples:
    python stream_simulator.py --dry-run --speed 20 --minutes 5            # print to the console
    python stream_simulator.py --output live.jsonl --speed 10              # write JSON Lines
    python stream_simulator.py --speed 5 --crowd-spike V05-G2              # uses EVENTSTREAM_CONNECTION_STRING

The connection string is the Event Hub-compatible connection string shown on the Eventstream
custom endpoint (SAS key authentication). Install ``azure-eventhub`` to send to it.
Set ``EVENTSTREAM_CONNECTION_STRING`` in the repository-root .env file or terminal environment,
or pass ``--connection-string``. Command-line options override exported variables, which override .env.
Without a connection string, explicitly select ``--dry-run`` or ``--output`` for local output.
Keep connection strings out of source control.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time as _time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tables import BASE_MARK, build_tables  # noqa: E402
from telemetry import timing_rows  # noqa: E402


def _iso(ts: datetime) -> str:
    if ts.tzinfo is not None:  # timestamps in this module are naive UTC
        ts = ts.astimezone(timezone.utc).replace(tzinfo=None)
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def plan_messages(event_id, start, seed, crowd_spike, wind_spike, minutes):
    gd = build_tables(date.fromisoformat("2026-11-16"), datetime(2026, 11, 24, 11, 0), seed)
    t = gd.tables
    rng = np.random.default_rng(seed + 99)
    se = t["session_event"]
    sid = se[se.event_id == event_id].session_id.iloc[0]
    session = t["session"].set_index("session_id").loc[sid]
    venue = t["venue"].set_index("venue_id").loc[session.venue_id]
    entries = t["entry"][t["entry"].event_id == event_id]
    noc_strength = {r.noc_code: r.delegation_size for r in t["noc"].itertuples()}
    ath = t["athlete"].set_index("athlete_id")
    ranked = sorted(entries.itertuples(), key=lambda r: -(noc_strength[ath.loc[r.athlete_id].noc_code] / 60
                                                         + rng.normal(0, 0.4)))
    base = BASE_MARK.get(event_id, 1800)
    finals = [(r.athlete_id, int(r.bib), round(base * (1 + 0.006 * i) + abs(rng.normal(0, 2)), 2))
              for i, r in enumerate(ranked)]
    msgs = []
    for row in timing_rows(start, sid, event_id, finals, rng, interval_s=0):
        row = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in row.items()}
        msgs.append((row["Timestamp"], dict(EventType="TimingEvents", **row)))
    end = start + timedelta(minutes=minutes)
    gates = t["gate"][t["gate"].venue_id == venue.name]
    m = 0
    while start + timedelta(minutes=m) < end:
        ts = start + timedelta(minutes=m)
        limit = venue.wind_limit_ms or 10.0
        wind = limit * 0.4 + rng.normal(0, limit * 0.05)
        gust = min(wind * 1.35, limit * 0.88)
        if wind_spike and wind_spike == venue.name and 10 <= m < 25:
            wind, gust = limit * 1.1, limit * 1.4
        msgs.append((ts, dict(EventType="VenueConditions", Timestamp=ts, VenueId=venue.name,
                              WindSpeedMs=round(wind, 2), WindGustMs=round(gust, 2),
                              AirTempC=round(-5 + rng.normal(0, 0.3), 2), SnowTempC=round(-7 + rng.normal(0, 0.3), 2),
                              HumidityPct=round(70 + rng.normal(0, 3), 1), VisibilityM=9000)))
        for g in gates.itertuples():
            dens = max(0.0, 1.2 + rng.normal(0, 0.15))
            if crowd_spike == g.gate_id and 5 <= m < 15:
                dens = rng.uniform(4.2, 4.9)
            msgs.append((ts, dict(EventType="GateFlow", Timestamp=ts, GateId=g.gate_id, VenueId=venue.name,
                                  EntriesPerMin=int(max(0, 40 + rng.normal(0, 6))),
                                  QueueingPersons=int(dens * g.plaza_area_m2),
                                  DensityPersonsPerM2=round(dens, 2))))
        m += 1
    msgs = [x for x in msgs if x[0] < end]
    msgs.sort(key=lambda x: x[0])
    return sid, msgs


def main(argv=None):
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--event", default="BTH-W10P", help="Event to replay (biathlon or cross-country)")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--speed", type=float, default=1.0, help="Replay speed factor (10 = ten times faster)")
    p.add_argument("--minutes", type=int, default=45, help="Minutes of race time to stream")
    p.add_argument("--crowd-spike", default=None, help="Gate ID that spikes above the density limit")
    p.add_argument("--wind-spike", default=None, help="Venue ID whose gusts exceed its limit")
    p.add_argument("--connection-string", default=os.environ.get("EVENTSTREAM_CONNECTION_STRING"),
                   help="Event Hub-compatible SAS connection string "
                        "(default: EVENTSTREAM_CONNECTION_STRING from environment or root .env)")
    p.add_argument("--eventhub-name", default=os.environ.get("EVENTSTREAM_EVENTHUB_NAME") or None,
                   help="Event hub name if EntityPath is absent "
                        "(default: EVENTSTREAM_EVENTHUB_NAME from environment or root .env)")
    p.add_argument("--output", default=None, help="Write JSON Lines to this file instead of sending")
    p.add_argument("--dry-run", action="store_true", help="Print messages to the console")
    a = p.parse_args(argv)

    if not (a.dry_run or a.output) and not (a.connection_string and a.connection_string.strip()):
        p.error("No Eventstream connection string configured. Set EVENTSTREAM_CONNECTION_STRING "
                "in the repository-root .env, export it in this terminal, or pass --connection-string. "
                "Use --dry-run or --output "
                "for local output; no events have been sent.")
    if not (a.dry_run or a.output) and any(c in a.connection_string for c in "\r\n"):
        p.error("The Eventstream connection string contains line breaks. Save "
                "EVENTSTREAM_CONNECTION_STRING on one physical line in .env or supply a single-line "
                "--connection-string value. Embedded line breaks can cause CBS authentication failures; "
                "no events have been sent.")

    start = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    sid, msgs = plan_messages(a.event, start, a.seed, a.crowd_spike, a.wind_spike, a.minutes)
    print(f"Replaying session {sid} ({a.event}): {len(msgs):,} messages over {a.minutes} race minutes "
          f"at x{a.speed}")
    producer = None
    if a.output:
        print("Mode: file output only; no events will be sent to Fabric.")
    elif a.dry_run:
        print("Mode: dry run only; no events will be sent to Fabric.")
    else:
        try:
            from azure.eventhub import EventData, EventHubProducerClient
        except ImportError:
            raise SystemExit("Install azure-eventhub to send to an Eventstream custom endpoint.")
        print("Mode: Eventstream. Connecting to the configured endpoint...", flush=True)
        producer = EventHubProducerClient.from_connection_string(a.connection_string,
                                                                 eventhub_name=a.eventhub_name)
    out = open(a.output, "w", encoding="utf-8") if a.output else None
    wall0 = _time.monotonic()
    sent = 0
    try:
        for ts, body in msgs:
            due = (ts - start).total_seconds() / a.speed
            delay = due - (_time.monotonic() - wall0)
            if delay > 0 and not a.output:
                _time.sleep(delay)
            body = {k: (_iso(v) if isinstance(v, datetime) else v) for k, v in body.items()}
            line = json.dumps(body, default=str)
            if out:
                out.write(line + "\n")
            elif producer:
                batch = producer.create_batch()
                batch.add(EventData(line))
                producer.send_batch(batch)
                if sent == 0:
                    print("First event accepted by the Eventstream endpoint.", flush=True)
            else:
                print(line)
            sent += 1
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        if out:
            out.close()
        if producer:
            producer.close()
    if a.output:
        print(f"Wrote {sent:,} messages to file; no events sent to Fabric.")
    elif a.dry_run:
        print(f"Printed {sent:,} messages; no events sent to Fabric.")
    else:
        print(f"Sent {sent:,} messages to Eventstream.")


if __name__ == "__main__":
    main()
