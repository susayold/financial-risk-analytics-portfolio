"""Run B4 reconciliation, schema, boundary and descriptive null-profile tests."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path

import duckdb


EXPECTED_COLUMNS = [
    'account_id', 'issue_d', 'issue_year', 'issue_month', 'issue_cohort', 'split_name',
    'actual_default', 'target_label', 'revenue', 'dti_n', 'loan_amnt', 'fico_n',
    'experience_c', 'emp_length', 'purpose', 'home_ownership_n', 'addr_state', 'zip_code',
    'dq_status', 'dq_flag_count', 'source_population', 'source_version',
    'feature_contract_version', 'preprocessing_version', 'mart_version', 'mart_build_ts',
]
CHAMPION = {'revenue', 'dti_n', 'loan_amnt', 'fico_n', 'experience_c', 'emp_length', 'purpose', 'home_ownership_n'}
FORBIDDEN = {'grade', 'sub_grade', 'int_rate', 'installment', 'term', 'loan_status', 'recoveries', 'total_pymnt', 'out_prncp', 'collection_recovery_fee'}
NULL_PROFILE_FIELDS = sorted(CHAMPION | {'addr_state', 'zip_code'})


def clean(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def one(con, query, params=None):
    row = con.execute(query, params or []).fetchone()
    return [clean(value) for value in row]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=Path, required=True)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(args.db_path), read_only=True)
    results = []
    schema_columns = []
    try:
        key = one(con, """
            SELECT COUNT(*), COUNT(DISTINCT account_id),
                   SUM(CASE WHEN account_id IS NULL THEN 1 ELSE 0 END),
                   COUNT(*) - COUNT(DISTINCT account_id)
            FROM mart.mart_credit_application_core
        """)
        key_pass = key == [1347681, 1347681, 0, 0]
        results.append({'id': 'B4T01', 'name': 'KEY', 'status': 'PASS' if key_pass else 'FAIL', 'observed': {'row_count': key[0], 'distinct_account_id': key[1], 'null_account_id': key[2], 'duplicate_account_id': key[3]}, 'expected': {'row_count': 1347681, 'distinct_account_id': 1347681, 'null_account_id': 0, 'duplicate_account_id': 0}})

        population = one(con, """
            SELECT (SELECT COUNT(*) FROM staging.stg_lc_granting_core),
                   (SELECT COUNT(*) FROM mart.mart_credit_application_core)
        """)
        pop_pass = population == [1347681, 1347681]
        results.append({'id': 'B4T02', 'name': 'POPULATION', 'status': 'PASS' if pop_pass else 'FAIL', 'observed': {'staging_rows': population[0], 'mart_rows': population[1], 'population_loss': population[0] - population[1]}, 'expected': {'staging_rows': 1347681, 'mart_rows': 1347681, 'population_loss': 0}})

        target = one(con, """
            SELECT SUM(CASE WHEN actual_default=1 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN actual_default=0 THEN 1 ELSE 0 END), AVG(actual_default),
                   SUM(CASE WHEN actual_default IS NULL OR actual_default NOT IN (0,1) THEN 1 ELSE 0 END)
            FROM mart.mart_credit_application_core
        """)
        target_pass = target[0] == 269249 and target[1] == 1078432 and abs(target[2] - 0.199786893) < 1e-9 and target[3] == 0
        results.append({'id': 'B4T03', 'name': 'TARGET', 'status': 'PASS' if target_pass else 'FAIL', 'observed': {'bad': target[0], 'good': target[1], 'bad_rate': target[2], 'unknown_target': target[3]}, 'expected': {'bad': 269249, 'good': 1078432, 'bad_rate': 0.199786893, 'unknown_target': 0}})

        temporal_rows = con.execute("""
            SELECT split_name, COUNT(*), MIN(issue_d), MAX(issue_d), COUNT(DISTINCT issue_cohort)
            FROM mart.mart_credit_application_core GROUP BY split_name
            ORDER BY CASE split_name WHEN 'Development' THEN 1 WHEN 'Validation' THEN 2 WHEN 'OOT' THEN 3 WHEN 'Historical Shadow' THEN 4 ELSE 5 END
        """).fetchall()
        temporal = {row[0]: {'row_count': row[1], 'min_issue_d': clean(row[2]), 'max_issue_d': clean(row[3]), 'issue_cohorts': row[4]} for row in temporal_rows}
        temporal_pass = {key: temporal.get(key, {}).get('row_count') for key in ['Development', 'Validation', 'OOT', 'Historical Shadow']} == {'Development': 829347, 'Validation': 293057, 'OOT': 169117, 'Historical Shadow': 56160} and sum(v['issue_cohorts'] for v in temporal.values()) == 139 and temporal.get(None, {}).get('row_count', 0) == 0
        results.append({'id': 'B4T04', 'name': 'TEMPORAL', 'status': 'PASS' if temporal_pass else 'FAIL', 'observed': temporal, 'expected': {'Development': 829347, 'Validation': 293057, 'OOT': 169117, 'Historical Shadow': 56160, 'issue_cohorts': 139, 'unassigned': 0, 'date_range': ['2007-06-01', '2018-12-01']}})

        schema_info = con.execute("DESCRIBE mart.mart_credit_application_core").fetchall()
        schema_columns = [{'name': row[0], 'type': row[1]} for row in schema_info]
        actual_columns = [row['name'] for row in schema_columns]
        schema_pass = actual_columns == EXPECTED_COLUMNS
        results.append({'id': 'B4T05', 'name': 'SCHEMA', 'status': 'PASS' if schema_pass else 'FAIL', 'observed': {'columns': actual_columns}, 'expected': {'columns': EXPECTED_COLUMNS}})

        forbidden_present = sorted(set(actual_columns) & FORBIDDEN)
        champion_missing = sorted(CHAMPION - set(actual_columns))
        boundary_pass = not forbidden_present and not champion_missing
        results.append({'id': 'B4T06', 'name': 'FEATURE_BOUNDARY', 'status': 'PASS' if boundary_pass else 'FAIL', 'observed': {'forbidden_present': forbidden_present, 'champion_missing': champion_missing}, 'expected': {'forbidden_present': [], 'champion_missing': []}})

        staging_columns = {row[0] for row in con.execute('DESCRIBE staging.stg_lc_granting_core').fetchall()}
        mart_columns = set(actual_columns)
        dq_status_values, dq_flag_non_null = con.execute("SELECT STRING_AGG(DISTINCT dq_status, ',' ORDER BY dq_status), COUNT(*) FILTER (WHERE dq_flag_count IS NOT NULL) FROM mart.mart_credit_application_core").fetchone()
        lineage_pass = {'title', 'desc'}.issubset(staging_columns) and 'title' not in mart_columns and 'desc' not in mart_columns and dq_status_values == 'STRUCTURAL_PASS' and dq_flag_non_null == 0
        results.append({'id': 'B4T07', 'name': 'LINEAGE_DQ_SEMANTICS', 'status': 'PASS' if lineage_pass else 'FAIL', 'observed': {'staging_has_title': 'title' in staging_columns, 'staging_has_desc': 'desc' in staging_columns, 'mart_has_title': 'title' in mart_columns, 'mart_has_desc': 'desc' in mart_columns, 'dq_status_values': dq_status_values, 'dq_flag_non_null_rows': dq_flag_non_null}, 'expected': {'staging_has_title': True, 'staging_has_desc': True, 'mart_has_title': False, 'mart_has_desc': False, 'dq_status_values': 'STRUCTURAL_PASS', 'dq_flag_non_null_rows': 0}})

        null_rows = []
        for field in NULL_PROFILE_FIELDS:
            row_count, null_count = one(con, f"SELECT COUNT(*), SUM(CASE WHEN \"{field}\" IS NULL THEN 1 ELSE 0 END) FROM mart.mart_credit_application_core")
            null_rows.append({'field': field, 'row_count': row_count, 'null_count': null_count, 'null_rate': null_count / row_count if row_count else None})
        results.append({'id': 'B4T08', 'name': 'NULL_PROFILE', 'status': 'PASS', 'observed': {'fields': len(null_rows)}, 'note': 'Descriptive only; no imputation or capping applied.'})
    finally:
        con.close()

    reconciliation = {'stage': 'B4', 'status': 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL', 'staging_rows': results[1]['observed']['staging_rows'], 'mart_rows': results[1]['observed']['mart_rows'], 'distinct_account_id': results[0]['observed']['distinct_account_id'], 'duplicate_account_id': results[0]['observed']['duplicate_account_id'], 'bad': results[2]['observed']['bad'], 'good': results[2]['observed']['good'], 'bad_rate': results[2]['observed']['bad_rate'], 'issue_cohorts': 139, 'development': 829347, 'validation': 293057, 'oot': 169117, 'historical_shadow': 56160, 'unassigned': 0, 'mart_version': 'B4_v1.0'}
    (args.output_dir / 'b4_reconciliation.json').write_text(json.dumps(reconciliation, indent=2) + '\n', encoding='utf-8')
    (args.output_dir / 'b4_schema.json').write_text(json.dumps({'stage': 'B4', 'mart': 'mart.mart_credit_application_core', 'mart_version': 'B4_v1.0', 'columns': schema_columns}, indent=2) + '\n', encoding='utf-8')
    (args.output_dir / 'b4_test_results.json').write_text(json.dumps({'stage': 'B4', 'gate_status': reconciliation['status'], 'tests': results}, indent=2) + '\n', encoding='utf-8')
    with (args.output_dir / 'b4_test_results.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['id', 'name', 'status'])
        writer.writeheader()
        writer.writerows({key: row[key] for key in ['id', 'name', 'status']} for row in results)
    with (args.output_dir / 'b4_null_profile.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['field', 'row_count', 'null_count', 'null_rate'])
        writer.writeheader()
        writer.writerows(null_rows)
    print(json.dumps({'stage': 'B4', 'gate_status': reconciliation['status'], 'tests': results}, indent=2))
    return 0 if reconciliation['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
