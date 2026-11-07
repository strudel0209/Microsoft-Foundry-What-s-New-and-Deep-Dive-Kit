"""Generate the synthetic Games operations sample.

Usage (local or in a Fabric notebook):
    python generate.py --out ../output --theme ioc
    python generate.py --out ../output --theme neutral --start-date 2026-11-16 --seed 2026

Writes lakehouse and eventhouse tables (CSV, optionally Parquet), synthetic PDF documents,
an evaluation question set with computed answers, the ontology specification and a manifest.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, time, timedelta

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ontology_spec  # noqa: E402
from documents import HAVE_PDF, build_documents  # noqa: E402
from evalset import build_eval_set  # noqa: E402
from schema import EVENTHOUSE_TABLES, LAKEHOUSE_TABLES  # noqa: E402
from tables import build_tables  # noqa: E402
from telemetry import build_telemetry  # noqa: E402
from themes import get_theme  # noqa: E402

VERSION = "1.0.0"


def _write(df: pd.DataFrame, cols, path_no_ext: str, fmt: str, iso_z: bool):
    df = df[[c for c, *_ in cols]].copy()
    for c, ty, _ in cols:
        if ty in ("timestamp", "datetime"):
            df[c] = pd.to_datetime(df[c]).dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ" if iso_z else "%Y-%m-%d %H:%M:%S")
            if iso_z:
                df[c] = df[c].str.replace(r"\.(\d{3})\d{3}Z$", r".\1Z", regex=True)
        elif ty == "date":
            df[c] = pd.to_datetime(df[c]).dt.strftime("%Y-%m-%d")
        elif ty == "bool":
            df[c] = df[c].map({True: "true", False: "false"})
    if fmt in ("csv", "both"):
        df.to_csv(path_no_ext + ".csv", index=False)
    if fmt in ("parquet", "both"):
        try:
            df.to_parquet(path_no_ext + ".parquet", index=False)
        except ImportError:
            print("  Parquet skipped (pyarrow not installed)")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="output", help="Output folder")
    p.add_argument("--theme", default="ioc", choices=["ioc", "neutral"])
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--start-date", default="2026-11-16", help="Opening day (day 1), YYYY-MM-DD")
    p.add_argument("--as-of", default=None,
                   help="Data cut-off in UTC, YYYY-MM-DDTHH:MM (default: day 9 at 11:00 UTC)")
    p.add_argument("--format", default="csv", choices=["csv", "parquet", "both"])
    p.add_argument("--no-docs", action="store_true", help="Skip PDF generation (register still written)")
    p.add_argument("--include-findings-table", action="store_true",
                   help="Also write the ground-truth findings as the lakehouse 'finding' table "
                        "(use when AI functions extraction is not run)")
    a = p.parse_args(argv)

    start = date.fromisoformat(a.start_date)
    as_of = (datetime.fromisoformat(a.as_of) if a.as_of
             else datetime.combine(start + timedelta(days=8), time(11, 0)))
    theme = get_theme(a.theme)
    errs = ontology_spec.validate()
    if errs:
        raise SystemExit("Ontology specification does not match the schema: " + "; ".join(errs))

    print(f"Generating {theme['games_name']} | day 1 = {start} | as of {as_of:%Y-%m-%d %H:%M} UTC | seed {a.seed}")
    gd = build_tables(start, as_of, a.seed)
    tel = build_telemetry(gd, a.seed + 1)
    doc_dir = None if a.no_docs else os.path.join(a.out, "documents")
    register, findings = build_documents(gd, theme, doc_dir, a.seed + 2)
    gd.tables["document_register"] = register
    questions = build_eval_set(gd, tel, register, findings)

    lh_dir, eh_dir, ev_dir, on_dir = (os.path.join(a.out, d) for d in ("lakehouse", "eventhouse", "eval", "ontology"))
    for d in (lh_dir, eh_dir, ev_dir, on_dir):
        os.makedirs(d, exist_ok=True)
    counts = {}
    for name, cols in LAKEHOUSE_TABLES.items():
        if name == "finding":
            if not a.include_findings_table:
                continue
            df = findings
        else:
            df = gd.tables[name]
        _write(df, cols, os.path.join(lh_dir, name), a.format, iso_z=False)
        counts[f"lakehouse.{name}"] = len(df)
    for name, cols in EVENTHOUSE_TABLES.items():
        _write(tel[name], cols, os.path.join(eh_dir, name), "csv", iso_z=True)
        counts[f"eventhouse.{name}"] = len(tel[name])
    _write(findings, LAKEHOUSE_TABLES["finding"], os.path.join(ev_dir, "ground_truth_findings"), "csv", iso_z=False)
    questions.to_json(os.path.join(ev_dir, "questions.jsonl"), orient="records", lines=True, force_ascii=False)
    questions.to_csv(os.path.join(ev_dir, "questions.csv"), index=False)
    with open(os.path.join(on_dir, "ontology-spec.json"), "w", encoding="utf-8") as f:
        json.dump(ontology_spec.to_json_dict(), f, indent=2, ensure_ascii=False)

    scen = {k: (v.isoformat() if hasattr(v, "isoformat") else
                [x.isoformat() if hasattr(x, "isoformat") else x for x in v] if isinstance(v, tuple) else v)
            for k, v in gd.scenario.items() if k not in ("timing_plan", "team_participants")}
    manifest = dict(generator_version=VERSION, theme=a.theme, games_name=theme["games_name"], seed=a.seed,
                    start_date=start.isoformat(), as_of_utc=as_of.isoformat(), documents_written=not a.no_docs,
                    document_format="pdf" if HAVE_PDF else "markdown", row_counts=counts,
                    document_count=len(register), findings_ground_truth=len(findings),
                    evaluation_questions=len(questions), scenario=scen)
    with open(os.path.join(a.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)
    for k, v in counts.items():
        print(f"  {k:32s} {v:>8,}")
    print(f"  documents                        {len(register):>8,}")
    print(f"  evaluation questions             {len(questions):>8,}")
    print(f"Done. Output in {os.path.abspath(a.out)}")
    return manifest


if __name__ == "__main__":
    main()
