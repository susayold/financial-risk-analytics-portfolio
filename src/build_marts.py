"""Build B4 from the reviewed staging contract, optionally bootstrapping staging from the public source on D:."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


REQUIRED_SOURCE_COLUMNS = {
    'id', 'issue_d', 'revenue', 'dti_n', 'loan_amnt', 'fico_n',
    'experience_c', 'emp_length', 'purpose', 'home_ownership_n',
    'addr_state', 'zip_code', 'Default',
}


def bootstrap_staging(con: duckdb.DuckDBPyConnection, csv_path: Path) -> None:
    """Create the reviewed B0–B3 staging shape from the public source for execution only."""
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE SCHEMA IF NOT EXISTS staging")
    con.execute("""
        CREATE OR REPLACE TABLE raw.lc_granting_source AS
        SELECT * FROM read_csv_auto(?, sample_size=-1, union_by_name=true)
    """, [str(csv_path)])
    names = {row[0] for row in con.execute("DESCRIBE raw.lc_granting_source").fetchall()}
    missing = REQUIRED_SOURCE_COLUMNS - names
    if missing:
        raise ValueError(f"Source is missing required columns: {sorted(missing)}")
    con.execute("""
        CREATE OR REPLACE TABLE staging.stg_lc_granting_core AS
        SELECT
            CAST(id AS VARCHAR) AS account_id,
            try_strptime(issue_d, '%b-%Y')::DATE AS issue_d,
            revenue,
            dti_n,
            loan_amnt,
            fico_n,
            experience_c,
            emp_length,
            purpose,
            home_ownership_n,
            addr_state,
            zip_code,
            CAST("Default" AS INTEGER) AS actual_default,
            CASE
                WHEN try_strptime(issue_d, '%b-%Y')::DATE < DATE '2016-01-01' THEN 'Development'
                WHEN try_strptime(issue_d, '%b-%Y')::DATE < DATE '2017-01-01' THEN 'Validation'
                WHEN try_strptime(issue_d, '%b-%Y')::DATE < DATE '2018-01-01' THEN 'OOT'
                WHEN try_strptime(issue_d, '%b-%Y')::DATE < DATE '2019-01-01' THEN 'Historical Shadow'
                ELSE NULL
            END AS split_name
        FROM raw.lc_granting_source;
    """)


def build_b4_mart(con: duckdb.DuckDBPyConnection, repo_root: Path) -> dict:
    con.execute("CREATE SCHEMA IF NOT EXISTS mart")
    sql = (repo_root / 'sql' / 'marts' / '05_mart_credit_application_core.sql').read_text(encoding='utf-8')
    con.execute(sql)
    rows = con.execute("SELECT COUNT(*) FROM mart.mart_credit_application_core").fetchone()[0]
    return {'mart': 'mart_credit_application_core', 'rows': rows, 'version': 'B4_v1.0'}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=Path, required=True)
    parser.add_argument('--csv-path', type=Path)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--metadata-out', type=Path)
    args = parser.parse_args()

    args.db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(args.db_path))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS staging")
        if args.csv_path:
            bootstrap_staging(con, args.csv_path)
        staging_exists = con.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = 'staging' AND table_name = 'stg_lc_granting_core'
        """).fetchone()[0]
        if not staging_exists:
            raise RuntimeError('staging.stg_lc_granting_core does not exist')
        result = build_b4_mart(con, args.repo_root)
        result['staging_rows'] = con.execute('SELECT COUNT(*) FROM staging.stg_lc_granting_core').fetchone()[0]
        result['source'] = 'ZENODO_11295916'
    finally:
        con.close()

    payload = json.dumps(result, indent=2)
    print(payload)
    if args.metadata_out:
        args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
        args.metadata_out.write_text(payload + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
