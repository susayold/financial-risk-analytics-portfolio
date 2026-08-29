"""Independent B5 gate runner. Produces only aggregate test evidence."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import duckdb


def q(con, sql):
    return con.execute(sql).fetchone()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db-path', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(args.db_path), read_only=True)
    tests = []
    def add(test_id, name, observed, expected, passed, note=''):
        tests.append({'id': test_id, 'name': name, 'status': 'PASS' if passed else 'FAIL', 'observed': observed, 'expected': expected, 'note': note})
    try:
        train, test, combined, overlap = q(con, "SELECT COUNT(*) FILTER(WHERE figshare_source_split='train'), COUNT(*) FILTER(WHERE figshare_source_split='test'), COUNT(*), (SELECT COUNT(*) FROM raw.figshare_train t JOIN raw.figshare_test s ON CAST(t.id AS VARCHAR)=CAST(s.id AS VARCHAR)) FROM raw.figshare_union")
        add('B5T01', 'FIGSHARE_SOURCE', {'train': train, 'test': test, 'combined': combined, 'train_test_id_overlap': overlap}, {'train': 236846, 'test': 95019, 'combined': 331865, 'train_test_id_overlap': 0}, (train, test, combined, overlap) == (236846, 95019, 331865, 0))
        rows, ids, nulls, duplicates = q(con, "SELECT COUNT(*), COUNT(DISTINCT account_id), COUNT(*) FILTER(WHERE account_id IS NULL), COUNT(*)-COUNT(DISTINCT account_id) FROM staging.stg_lc_figshare_enriched")
        add('B5T02', 'FIGSHARE_KEY', {'rows': rows, 'distinct_account_id': ids, 'null_account_id': nulls, 'duplicates': duplicates}, {'rows': 331865, 'distinct_account_id': 331865, 'null_account_id': 0, 'duplicates': 0}, (rows, ids, nulls, duplicates) == (331865, 331865, 0, 0))
        status_counts = dict(con.execute("SELECT match_status, COUNT(*) FROM bridge.bridge_lc_core_figshare GROUP BY match_status").fetchall())
        add('B5T03', 'BRIDGE_COUNTS', status_counts, {'MATCHED': 325255, 'FIGSHARE_ONLY': 6610, 'CORE_ONLY': 1022426}, status_counts == {'MATCHED': 325255, 'FIGSHARE_ONLY': 6610, 'CORE_ONLY': 1022426}, 'Match rate 98.00822624%; core coverage 24.13442053%.')
        total, ids, dup = q(con, 'SELECT COUNT(*), COUNT(DISTINCT account_id), COUNT(*)-COUNT(DISTINCT account_id) FROM bridge.bridge_lc_core_figshare')
        add('B5T04', 'BRIDGE_GRAIN', {'rows': total, 'distinct_account_id': ids, 'duplicates': dup}, {'rows': 1354291, 'distinct_account_id': 1354291, 'duplicates': 0}, (total, ids, dup) == (1354291, 1354291, 0))
        baseline = {'issue_d': (325255, 0, 0), 'loan_amnt': (325255, 0, 0), 'purpose': (325255, 0, 0), 'addr_state': (325255, 0, 0), 'fico': (325255, 0, 0), 'home_ownership': (324391, 75, 789), 'revenue': (318681, 6574, 0), 'dti': (323701, 1554, 0)}
        flags = {'issue_d': 'issue_d_match', 'loan_amnt': 'loan_amnt_match', 'purpose': 'purpose_match', 'addr_state': 'addr_state_match', 'fico': 'fico_match', 'home_ownership': 'home_ownership_match', 'revenue': 'revenue_match', 'dti': 'dti_match'}
        observed = {}
        for field, flag in flags.items():
            observed[field] = q(con, f"SELECT COUNT(*) FILTER(WHERE match_status='MATCHED' AND {flag}), COUNT(*) FILTER(WHERE match_status='MATCHED' AND {flag}=FALSE), COUNT(*) FILTER(WHERE match_status='MATCHED' AND {flag} IS NULL) FROM bridge.bridge_lc_core_figshare")
        add('B5T05', 'FIELD_CONCORDANCE', observed, baseline, observed == baseline, 'Null comparisons are excluded from the concordance denominator; core wins conflicts.')
        mismatches = q(con, """SELECT COUNT(*) FROM mart.mart_credit_pricing_enriched p JOIN mart.mart_credit_application_core c USING(account_id)
          WHERE p.actual_default IS DISTINCT FROM c.actual_default OR p.revenue IS DISTINCT FROM c.revenue OR p.dti_n IS DISTINCT FROM c.dti_n
             OR p.loan_amnt IS DISTINCT FROM c.loan_amnt OR p.fico_n IS DISTINCT FROM c.fico_n OR p.purpose IS DISTINCT FROM c.purpose
             OR p.home_ownership_n IS DISTINCT FROM c.home_ownership_n OR p.addr_state IS DISTINCT FROM c.addr_state""")[0]
        add('B5T06', 'CORE_AUTHORITY', {'governed_field_mismatches': mismatches}, {'governed_field_mismatches': 0}, mismatches == 0, 'Zenodo/B4 values are selected explicitly; supplemental values remain suffixed or separate.')
        rows, ids, dup = q(con, 'SELECT COUNT(*), COUNT(DISTINCT account_id), COUNT(*)-COUNT(DISTINCT account_id) FROM mart.mart_credit_pricing_enriched')
        add('B5T07', 'PRICING_MART', {'rows': rows, 'distinct_account_id': ids, 'duplicates': dup}, {'rows': 325255, 'distinct_account_id': 325255, 'duplicates': 0}, (rows, ids, dup) == (325255, 325255, 0))
        core_cols = {r[0] for r in con.execute('DESCRIBE mart.mart_credit_application_core').fetchall()}; pricing_cols = {r[0] for r in con.execute('DESCRIBE mart.mart_credit_pricing_enriched').fetchall()}
        forbidden_core = sorted(core_cols & {'sub_grade', 'grade_derived', 'int_rate', 'installment', 'term'})
        add('B5T08', 'PRICING_FEATURE_BOUNDARY', {'forbidden_core_fields': forbidden_core, 'pricing_fields_present': sorted(pricing_cols & {'sub_grade', 'grade_derived', 'int_rate', 'installment', 'term'})}, {'forbidden_core_fields': [], 'pricing_fields_present': ['grade_derived', 'installment', 'int_rate', 'sub_grade', 'term']}, not forbidden_core and {'sub_grade', 'grade_derived', 'int_rate', 'installment', 'term'}.issubset(pricing_cols))
        rej_cols = {r[0] for r in con.execute('DESCRIBE mart.mart_rejected_context').fetchall()}; required = {'rejected_record_id', 'source_file', 'source_row_number', 'application_date', 'source_population'}
        rr, ri = q(con, 'SELECT COUNT(*), COUNT(DISTINCT rejected_record_id) FROM mart.mart_rejected_context')
        add('B5T09', 'REJECTED_SCHEMA', {'rows': rr, 'distinct_keys': ri, 'missing_required_fields': sorted(required-rej_cols)}, {'stable_key': True, 'missing_required_fields': []}, rr == ri and not (required-rej_cols))
        forbidden = sorted(rej_cols & {'actual_default', 'target_label', 'GOOD', 'BAD', 'predicted_pd', 'observed_loss'}); flags_true = q(con, 'SELECT COUNT(*) FILTER(WHERE outcome_observed), COUNT(*) FILTER(WHERE model_target_eligible), COUNT(*) FILTER(WHERE champion_merge_eligible) FROM mart.mart_rejected_context')
        add('B5T10', 'REJECTED_OUTCOME_BOUNDARY', {'forbidden_outcome_columns': forbidden, 'true_boundary_flags': flags_true}, {'forbidden_outcome_columns': [], 'true_boundary_flags': (0, 0, 0)}, not forbidden and flags_true == (0, 0, 0), 'No rejected default rate, PD, loss or reject inference is computed.')
        core = q(con, "SELECT COUNT(*), COUNT(DISTINCT account_id), SUM(actual_default), COUNT(*)-SUM(actual_default), COUNT(DISTINCT issue_cohort) FROM mart.mart_credit_application_core")
        splits = dict(con.execute('SELECT split_name, COUNT(*) FROM mart.mart_credit_application_core GROUP BY split_name').fetchall())
        add('B5T11', 'CORE_NONMUTATION', {'core': core, 'splits': splits}, {'core': (1347681, 1347681, 269249, 1078432, 139), 'splits': {'Development': 829347, 'Validation': 293057, 'OOT': 169117, 'Historical Shadow': 56160}}, core == (1347681, 1347681, 269249, 1078432, 139) and splits == {'Development': 829347, 'Validation': 293057, 'OOT': 169117, 'Historical Shadow': 56160})
        metadata = q(con, "SELECT COUNT(*) FROM mart.mart_credit_pricing_enriched WHERE source_population='ZENODO_FIGSHARE_MATCHED_ENRICHED' AND core_source_version='ZENODO_11295916' AND supplemental_version='FIGSHARE_22121477_V4' AND bridge_version='B5_BRIDGE_v1.0' AND pricing_mart_version='B5_PRICING_v1.0'")[0]
        rejected_meta = q(con, "SELECT COUNT(*) FROM mart.mart_rejected_context WHERE source_population='REJECTED_CONTEXT_ONLY' AND source_version='REJECTSTATS_KAGGLE_PUBLIC_V3' AND rejected_mart_version='B5_REJECTED_v1.0'")[0]
        add('B5T12', 'LINEAGE_METADATA', {'pricing_rows_with_metadata': metadata, 'rejected_rows_with_metadata': rejected_meta}, {'pricing_rows': 325255, 'rejected_rows': rr}, metadata == 325255 and rejected_meta == rr)
    finally:
        con.close()
    gate = 'PASS' if all(t['status'] == 'PASS' for t in tests) else 'FAIL'
    payload = {'block': 'B5', 'gate_status': gate, 'tests': tests}
    (args.output_dir/'b5_test_results.json').write_text(json.dumps(payload, indent=2, default=str)+'\n', encoding='utf-8')
    with (args.output_dir/'b5_test_results.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ('id','name','status')} for t in tests)
    print(json.dumps({'block':'B5','gate_status':gate,'pass_count':sum(t['status']=='PASS' for t in tests),'test_count':len(tests)}, indent=2))
    return 0 if gate == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
