"""Ingest B5 supplemental sources into an execution-only DuckDB database.

The raw tables are temporary runtime objects. This module exports only sanitized
schemas and aggregate counts to the repository output directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


FIGSHARE_EXPECTED = {'train': 236846, 'test': 95019, 'combined': 331865}


def _schema(con: duckdb.DuckDBPyConnection, table: str, role: str) -> dict:
    columns = []
    for name, dtype, *_ in con.execute(f'DESCRIBE {table}').fetchall():
        quoted = '"' + name.replace('"', '""') + '"'
        non_null = con.execute(f'SELECT COUNT({quoted}) FROM {table}').fetchone()[0]
        columns.append({'raw_name': name, 'data_type': dtype, 'non_null_count': int(non_null), 'semantic_role': role})
    row_count = con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    return {'table': table, 'row_count': int(row_count), 'columns': columns}


def ingest_figshare(con: duckdb.DuckDBPyConnection, train_path: Path, test_path: Path, output_dir: Path) -> dict:
    con.execute('CREATE SCHEMA IF NOT EXISTS raw')
    con.execute("CREATE OR REPLACE TABLE raw.figshare_train AS SELECT * FROM read_csv_auto(?, sample_size=-1, union_by_name=true)", [str(train_path)])
    con.execute("CREATE OR REPLACE TABLE raw.figshare_test AS SELECT * FROM read_csv_auto(?, sample_size=-1, union_by_name=true)", [str(test_path)])
    con.execute("""
        CREATE OR REPLACE TABLE raw.figshare_union AS
        SELECT *, 'train' AS figshare_source_split, 'train_lending_club.csv' AS figshare_source_file FROM raw.figshare_train
        UNION ALL BY NAME
        SELECT *, 'test' AS figshare_source_split, 'test_lending_club.csv' AS figshare_source_file FROM raw.figshare_test
    """)
    counts = {
        'train': con.execute('SELECT COUNT(*) FROM raw.figshare_train').fetchone()[0],
        'test': con.execute('SELECT COUNT(*) FROM raw.figshare_test').fetchone()[0],
        'combined': con.execute('SELECT COUNT(*) FROM raw.figshare_union').fetchone()[0],
        'train_test_id_overlap': con.execute('SELECT COUNT(*) FROM raw.figshare_train t JOIN raw.figshare_test s ON CAST(t.id AS VARCHAR)=CAST(s.id AS VARCHAR)').fetchone()[0],
        'train_duplicate_ids': con.execute('SELECT COUNT(*) - COUNT(DISTINCT CAST(id AS VARCHAR)) FROM raw.figshare_train').fetchone()[0],
        'test_duplicate_ids': con.execute('SELECT COUNT(*) - COUNT(DISTINCT CAST(id AS VARCHAR)) FROM raw.figshare_test').fetchone()[0],
    }
    if counts != {'train': 236846, 'test': 95019, 'combined': 331865, 'train_test_id_overlap': 0, 'train_duplicate_ids': 0, 'test_duplicate_ids': 0}:
        raise ValueError(f'Figshare source contract failed: {counts}')
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'figshare_source_schema.json').write_text(json.dumps({
        'source': 'FIGSHARE_22121477_V4', 'role': 'supplemental_only', 'counts': counts,
        'train': _schema(con, 'raw.figshare_train', 'supplemental/raw audit'),
        'test': _schema(con, 'raw.figshare_test', 'supplemental/raw audit'),
        'planned_mappings': {
            'id': 'account_id join key', 'issue_d': 'issue_d_supp', 'loan_amnt': 'loan_amnt_supp',
            'annual_inc': 'revenue_supp', 'dti': 'dti_supp', 'fico_range_low/high': 'fico_supp midpoint',
            'purpose': 'purpose_supp', 'home_ownership': 'home_ownership_supp', 'addr_state': 'addr_state_supp',
            'sub_grade': 'benchmark_only', 'int_rate/installment/term': 'economics_only',
        },
    }, indent=2) + '\n', encoding='utf-8')
    return counts


def ingest_rejectstats(con: duckdb.DuckDBPyConnection, reject_path: Path, output_dir: Path) -> dict:
    con.execute('CREATE SCHEMA IF NOT EXISTS raw')
    con.execute("CREATE OR REPLACE TABLE raw.rejectstats_source AS SELECT * FROM read_csv_auto(?, sample_size=100000, union_by_name=true)", [str(reject_path)])
    required = {'Amount Requested', 'Application Date', 'Loan Title', 'Risk_Score', 'Debt-To-Income Ratio', 'Zip Code', 'State', 'Employment Length', 'Policy Code'}
    actual = {row[0] for row in con.execute('DESCRIBE raw.rejectstats_source').fetchall()}
    if not required.issubset(actual):
        raise ValueError(f'RejectStats schema missing required verified fields: {sorted(required - actual)}')
    con.execute("""
        CREATE OR REPLACE TABLE raw.rejectstats_union AS
        SELECT
            md5('rejected_2007_to_2018Q4.csv.gz:' || CAST(row_number() OVER () AS VARCHAR)) AS rejected_record_id,
            'rejected_2007_to_2018Q4.csv.gz' AS source_file,
            row_number() OVER () AS source_row_number,
            "Application Date" AS application_date,
            "Amount Requested" AS amount_requested,
            "Loan Title" AS loan_title,
            Risk_Score AS risk_score,
            "Debt-To-Income Ratio" AS debt_to_income_ratio,
            "Zip Code" AS zip_code,
            State AS state,
            "Employment Length" AS employment_length,
            "Policy Code" AS policy_code
        FROM raw.rejectstats_source
    """)
    row_count = con.execute('SELECT COUNT(*) FROM raw.rejectstats_union').fetchone()[0]
    duplicate_keys = con.execute('SELECT COUNT(*) - COUNT(DISTINCT rejected_record_id) FROM raw.rejectstats_union').fetchone()[0]
    null_keys = con.execute('SELECT COUNT(*) FILTER (WHERE rejected_record_id IS NULL) FROM raw.rejectstats_union').fetchone()[0]
    result = {'row_count': int(row_count), 'duplicate_rejected_record_id': int(duplicate_keys), 'null_rejected_record_id': int(null_keys)}
    if duplicate_keys != 0 or null_keys != 0:
        raise ValueError(f'RejectStats technical key contract failed: {result}')
    (output_dir / 'rejectstats_source_schema.json').write_text(json.dumps({
        'source': 'REJECTSTATS_KAGGLE_PUBLIC_V3', 'role': 'context_only', 'observed_outcome': False,
        'counts': result, 'raw_schema': _schema(con, 'raw.rejectstats_source', 'rejected applicant context'),
        'verified_mappings': {
            'Amount Requested': 'amount_requested', 'Application Date': 'application_date', 'Loan Title': 'loan_title',
            'Risk_Score': 'risk_score', 'Debt-To-Income Ratio': 'dti_rejected', 'Zip Code': 'zip_code_rejected',
            'State': 'state_rejected', 'Employment Length': 'employment_length_rejected', 'Policy Code': 'policy_code',
        }, 'technical_key': 'md5(source file + source row number)',
    }, indent=2) + '\n', encoding='utf-8')
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=Path, required=True)
    parser.add_argument('--train-path', type=Path, required=True)
    parser.add_argument('--test-path', type=Path, required=True)
    parser.add_argument('--reject-path', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    con = duckdb.connect(str(args.db_path))
    try:
        result = {'figshare': ingest_figshare(con, args.train_path, args.test_path, args.output_dir), 'rejectstats': ingest_rejectstats(con, args.reject_path, args.output_dir)}
    finally:
        con.close()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
