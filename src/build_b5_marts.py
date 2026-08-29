"""Fail-closed B5 build: supplemental bridge, pricing mart and rejected context mart."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_marts import bootstrap_staging, build_b4_mart, validate_staging_contract  # noqa: E402
from ingest_supplemental import ingest_figshare, ingest_rejectstats  # noqa: E402

EXPECTED_BRIDGE = {'MATCHED': 325255, 'FIGSHARE_ONLY': 6610, 'CORE_ONLY': 1022426}
EXPECTED_CONCORDANCE = {
    'issue_d': (325255, 0, 0), 'loan_amnt': (325255, 0, 0), 'purpose': (325255, 0, 0), 'addr_state': (325255, 0, 0), 'fico': (325255, 0, 0),
    'home_ownership': (324391, 75, 789), 'revenue': (318681, 6574, 0), 'dti': (323701, 1554, 0),
}


def exec_sql(con: duckdb.DuckDBPyConnection, relative: str) -> None:
    con.execute((REPO / relative).read_text(encoding='utf-8'))


def validate_bridge(con: duckdb.DuckDBPyConnection) -> dict:
    rows = dict(con.execute('SELECT match_status, COUNT(*) FROM bridge.bridge_lc_core_figshare GROUP BY match_status').fetchall())
    total = con.execute('SELECT COUNT(*) FROM bridge.bridge_lc_core_figshare').fetchone()[0]
    dup = con.execute('SELECT COUNT(*) - COUNT(DISTINCT account_id) FROM bridge.bridge_lc_core_figshare').fetchone()[0]
    observed = {'counts': rows, 'full_bridge_rows': total, 'duplicate_account_id': dup}
    if rows != EXPECTED_BRIDGE or total != 1354291 or dup != 0:
        raise RuntimeError(f'B5 bridge reconciliation failed; pricing mart build blocked: {observed}')
    return observed


def field_concordance(con: duckdb.DuckDBPyConnection, output_dir: Path) -> list[dict]:
    checks = [
        ('issue_d', 'issue_d_match', 'exact date equality'), ('loan_amnt', 'loan_amnt_match', 'absolute tolerance <= 0.01'),
        ('purpose', 'purpose_match', 'trim + lower equality'), ('addr_state', 'addr_state_match', 'trim + upper equality'),
        ('fico', 'fico_match', 'FICO midpoint, absolute tolerance <= 0.01'), ('home_ownership', 'home_ownership_match', 'trim + upper equality'),
        ('revenue', 'revenue_match', 'absolute tolerance <= 0.01'), ('dti', 'dti_match', 'absolute tolerance <= 0.0001'),
    ]
    output = []
    for field, flag, rule in checks:
        matched, equal, conflicts, nulls = con.execute(f"""
            SELECT COUNT(*) FILTER (WHERE match_status='MATCHED'),
                   COUNT(*) FILTER (WHERE match_status='MATCHED' AND {flag}),
                   COUNT(*) FILTER (WHERE match_status='MATCHED' AND {flag}=FALSE),
                   COUNT(*) FILTER (WHERE match_status='MATCHED' AND {flag} IS NULL)
            FROM bridge.bridge_lc_core_figshare
        """).fetchone()
        expected_equal, expected_conflicts, expected_nulls = EXPECTED_CONCORDANCE[field]
        comparable = equal + conflicts
        row = {'field': field, 'matched_accounts': int(matched), 'comparable_accounts': int(comparable), 'equal_count': int(equal), 'conflict_count': int(conflicts), 'null_comparison_count': int(nulls), 'concordance_rate': round(equal / comparable, 10), 'comparison_rule': rule, 'authority': 'ZENODO_CORE', 'action': 'CORE_WINS'}
        output.append(row)
        if (equal, conflicts, nulls) != (expected_equal, expected_conflicts, expected_nulls):
            raise RuntimeError(f'B5 concordance baseline failed for {field}: {row}')
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / 'b5_field_concordance.csv').open('w', newline='', encoding='utf-8') as handle:
        import csv
        writer = csv.DictWriter(handle, fieldnames=output[0].keys())
        writer.writeheader(); writer.writerows(output)
    return output


def validate_pricing(con: duckdb.DuckDBPyConnection) -> dict:
    rows, ids, dup = con.execute('SELECT COUNT(*), COUNT(DISTINCT account_id), COUNT(*) - COUNT(DISTINCT account_id) FROM mart.mart_credit_pricing_enriched').fetchone()
    target_mismatch = con.execute("""
        SELECT COUNT(*) FROM mart.mart_credit_pricing_enriched p
        JOIN mart.mart_credit_application_core c USING (account_id)
        WHERE p.actual_default IS DISTINCT FROM c.actual_default OR p.revenue IS DISTINCT FROM c.revenue
           OR p.dti_n IS DISTINCT FROM c.dti_n OR p.loan_amnt IS DISTINCT FROM c.loan_amnt
           OR p.fico_n IS DISTINCT FROM c.fico_n OR p.purpose IS DISTINCT FROM c.purpose
           OR p.home_ownership_n IS DISTINCT FROM c.home_ownership_n OR p.addr_state IS DISTINCT FROM c.addr_state
    """).fetchone()[0]
    forbidden = {'sub_grade', 'grade_derived', 'int_rate', 'installment', 'term'} & {r[0] for r in con.execute('DESCRIBE mart.mart_credit_application_core').fetchall()}
    result = {'rows': int(rows), 'distinct_account_id': int(ids), 'duplicates': int(dup), 'core_authority_mismatches': int(target_mismatch), 'core_forbidden_pricing_fields': sorted(forbidden)}
    if result != {'rows': 325255, 'distinct_account_id': 325255, 'duplicates': 0, 'core_authority_mismatches': 0, 'core_forbidden_pricing_fields': []}:
        raise RuntimeError(f'B5 pricing mart contract failed: {result}')
    return result


def validate_rejected(con: duckdb.DuckDBPyConnection) -> dict:
    columns = {r[0] for r in con.execute('DESCRIBE mart.mart_rejected_context').fetchall()}
    forbidden = {'actual_default', 'target_label', 'GOOD', 'BAD', 'predicted_pd', 'observed_loss'} & columns
    result = {
        'rows': con.execute('SELECT COUNT(*) FROM mart.mart_rejected_context').fetchone()[0],
        'distinct_rejected_record_id': con.execute('SELECT COUNT(DISTINCT rejected_record_id) FROM mart.mart_rejected_context').fetchone()[0],
        'outcome_observed_true': con.execute('SELECT COUNT(*) FROM mart.mart_rejected_context WHERE outcome_observed').fetchone()[0],
        'model_target_eligible_true': con.execute('SELECT COUNT(*) FROM mart.mart_rejected_context WHERE model_target_eligible').fetchone()[0],
        'champion_merge_eligible_true': con.execute('SELECT COUNT(*) FROM mart.mart_rejected_context WHERE champion_merge_eligible').fetchone()[0],
        'forbidden_outcome_columns': sorted(forbidden),
    }
    if result['rows'] != result['distinct_rejected_record_id'] or any(result[k] != 0 for k in ('outcome_observed_true', 'model_target_eligible_true', 'champion_merge_eligible_true')) or forbidden:
        raise RuntimeError(f'Rejected context boundary failed: {result}')
    return {k: int(v) if isinstance(v, int) else v for k, v in result.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-path', type=Path, required=True)
    parser.add_argument('--core-csv', type=Path, required=True)
    parser.add_argument('--train-path', type=Path, required=True)
    parser.add_argument('--test-path', type=Path, required=True)
    parser.add_argument('--reject-path', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(args.db_path))
    try:
        con.execute('CREATE SCHEMA IF NOT EXISTS mart; CREATE SCHEMA IF NOT EXISTS bridge; CREATE SCHEMA IF NOT EXISTS staging;')
        bootstrap_staging(con, args.core_csv)
        preflight = validate_staging_contract(con)
        build_b4_mart(con, REPO)
        figshare = ingest_figshare(con, args.train_path, args.test_path, args.output_dir)
        rejectstats = ingest_rejectstats(con, args.reject_path, args.output_dir)
        exec_sql(con, 'sql/staging/02_stg_lc_figshare_enriched.sql')
        exec_sql(con, 'sql/bridges/04_bridge_lc_core_figshare.sql')
        bridge = validate_bridge(con)
        concordance = field_concordance(con, args.output_dir)
        exec_sql(con, 'sql/marts/06_mart_credit_pricing_enriched.sql')
        pricing = validate_pricing(con)
        exec_sql(con, 'sql/staging/03_stg_lc_rejected.sql')
        exec_sql(con, 'sql/marts/07_mart_rejected_context.sql')
        rejected = validate_rejected(con)
        b4_after = validate_staging_contract(con)
        core_rows, core_ids, bad, good, cohorts = con.execute("SELECT COUNT(*), COUNT(DISTINCT account_id), SUM(actual_default), COUNT(*)-SUM(actual_default), COUNT(DISTINCT issue_cohort) FROM mart.mart_credit_application_core").fetchone()
        core_regression = {'rows': core_rows, 'distinct_account_id': core_ids, 'bad': bad, 'good': good, 'issue_cohorts': cohorts}
        if core_regression != {'rows': 1347681, 'distinct_account_id': 1347681, 'bad': 269249, 'good': 1078432, 'issue_cohorts': 139}:
            raise RuntimeError(f'B4 non-mutation regression failed: {core_regression}')
        reconciliation = {'block': 'B5', 'status': 'PASS', 'figshare': figshare, 'bridge': bridge, 'pricing': pricing, 'rejected': rejected, 'core_regression': core_regression, 'concordance': concordance}
        (args.output_dir / 'b5_reconciliation.json').write_text(json.dumps(reconciliation, indent=2, default=str) + '\n', encoding='utf-8')
        manifest = {'block': 'B5', 'status': 'PASS', 'core_version': 'B4_v1.0', 'supplemental_version': 'FIGSHARE_22121477_V4', 'bridge_version': 'B5_BRIDGE_v1.0', 'pricing_mart_version': 'B5_PRICING_v1.0', 'rejected_mart_version': 'B5_REJECTED_v1.0', 'matched': 325255, 'figshare_only': 6610, 'core_only': 1022426, 'rejected_context_rows': rejected['rows'], 'next_gate': 'B6_PORTFOLIO_OVERVIEW'}
        (args.output_dir / 'b5_run_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        for table, filename in [('bridge.bridge_lc_core_figshare', 'b5_bridge_summary.csv')]:
            with (args.output_dir / filename).open('w', newline='', encoding='utf-8') as handle:
                import csv
                writer = csv.writer(handle); writer.writerow(['match_status', 'rows']); writer.writerows(con.execute(f'SELECT match_status, COUNT(*) FROM {table} GROUP BY match_status ORDER BY match_status').fetchall())
        (args.output_dir / 'b5_pricing_schema.json').write_text(json.dumps({'table': 'mart.mart_credit_pricing_enriched', 'version': 'B5_PRICING_v1.0', 'columns': [{'name': r[0], 'type': r[1]} for r in con.execute('DESCRIBE mart.mart_credit_pricing_enriched').fetchall()]}, indent=2) + '\n', encoding='utf-8')
        (args.output_dir / 'b5_rejected_schema.json').write_text(json.dumps({'table': 'mart.mart_rejected_context', 'version': 'B5_REJECTED_v1.0', 'role': 'context_only', 'columns': [{'name': r[0], 'type': r[1]} for r in con.execute('DESCRIBE mart.mart_rejected_context').fetchall()]}, indent=2) + '\n', encoding='utf-8')
    finally:
        con.close()
    print(json.dumps({'block': 'B5', 'status': 'PASS', 'manifest': str(args.output_dir / 'b5_run_manifest.json')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
