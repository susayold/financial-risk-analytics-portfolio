"""Build B6 aggregate portfolio outputs from the locked B4 core mart."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import duckdb


def clean(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


def export_rows(con, query, path: Path):
    cur = con.execute(query)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for row in rows:
            w.writerow([clean(x) for x in row])
    return cols, rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", type=Path, required=True)
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(args.db_path))
    try:
        con.execute((args.repo_root / "sql" / "analytics" / "08_b6_portfolio_overview.sql").read_text(encoding="utf-8"))
        overview_cols, overview_rows = export_rows(con, "SELECT * FROM analytics.portfolio_overview", args.output_dir / "portfolio_kpis.csv")
        profile_cols, _ = export_rows(con, "SELECT * FROM analytics.numeric_profile ORDER BY field_name", args.output_dir / "numeric_profile.csv")
        mix_cols, _ = export_rows(con, "SELECT * FROM analytics.portfolio_mix", args.output_dir / "portfolio_mix.csv")
        overview = {k: clean(v) for k, v in zip(overview_cols, overview_rows[0])}
        (args.output_dir / "portfolio_kpis.json").write_text(json.dumps(overview, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "b6_run_manifest.json").write_text(json.dumps({
            "stage": "B6", "status": "BUILT", "source_mart": "mart.mart_credit_application_core",
            "grain": "one row per application", "preprocessing": "none",
            "tables": ["analytics.portfolio_overview", "analytics.numeric_profile", "analytics.portfolio_mix"],
            "exports": ["portfolio_kpis.json", "portfolio_kpis.csv", "numeric_profile.csv", "portfolio_mix.csv"],
        }, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "B6", "status": "BUILT", "total_accounts": overview["total_accounts"], "bad_accounts": overview["bad_accounts"]}, indent=2))
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
