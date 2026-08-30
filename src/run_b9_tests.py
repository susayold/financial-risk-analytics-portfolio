"""Run executable B9 vintage, temporal and composition tests."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
import duckdb

EXPECTED_SPLITS = {
    'Development': (829347, 153062, 0.1845572480517805, '2007-06-01', '2015-12-01'),
    'Validation': (293057, 68229, 0.23281818895300233, '2016-01-01', '2016-12-01'),
    'OOT': (169117, 39112, 0.23127184138791487, '2017-01-01', '2017-12-01'),
    'Historical Shadow': (56160, 8846, 0.15751424501424502, '2018-01-01', '2018-12-01'),
}


def add(ts, test_id, name, ok, observed, expected):
    ts.append({'id': test_id, 'name': name, 'status': 'PASS' if ok else 'FAIL', 'observed': observed, 'expected': expected})


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument('--db-path', type=Path, required=True); p.add_argument('--output-dir', type=Path, required=True); p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    a = p.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True); c = duckdb.connect(str(a.db_path), read_only=True); ts = []
    try:
        row = c.execute('SELECT COUNT(*), COUNT(DISTINCT cohort), MIN(cohort_start), MAX(cohort_start) FROM analytics.vintage_monthly').fetchone()
        ok = row[0] == 139 and row[1] == 139 and str(row[2]) == '2007-06-01' and str(row[3]) == '2018-12-01'
        add(ts, 'B9T01', 'EXECUTABLE_COHORT_DATE_RANGE', ok, {'rows': row[0], 'distinct_cohorts': row[1], 'min': str(row[2]), 'max': str(row[3])}, {'cohorts': 139, 'min': '2007-06-01', 'max': '2018-12-01'})

        monthly = c.execute('SELECT SUM(accounts), SUM(bad_accounts), SUM(loan_amount), SUM(bad_associated_loan_amount) FROM analytics.vintage_monthly').fetchone()
        core = c.execute('SELECT COUNT(*), COUNT(*) FILTER (WHERE actual_default=1), SUM(loan_amnt), SUM(loan_amnt) FILTER (WHERE actual_default=1) FROM mart.mart_credit_application_core').fetchone()
        ok = all(abs(float(x)-float(y)) < 1e-6 for x, y in zip(monthly, core))
        add(ts, 'B9T02', 'MONTHLY_RECONCILIATION', ok, {'monthly': monthly, 'core': core}, {'equal': True})

        annual = c.execute('SELECT SUM(accounts), SUM(bad_accounts), SUM(loan_amount), SUM(bad_associated_loan_amount) FROM analytics.vintage_annual').fetchone()
        ok = all(abs(float(x)-float(y)) < 1e-6 for x, y in zip(annual, core))
        add(ts, 'B9T03', 'ANNUAL_RECONCILIATION', ok, {'annual': annual, 'core': core}, {'equal': True})

        rows = c.execute('SELECT split_name, accounts, bad_accounts, bad_rate, min_issue_d, max_issue_d FROM analytics.vintage_split ORDER BY CASE split_name WHEN \'Development\' THEN 1 WHEN \'Validation\' THEN 2 WHEN \'OOT\' THEN 3 WHEN \'Historical Shadow\' THEN 4 END').fetchall()
        observed = {r[0]: {'accounts': r[1], 'bad_accounts': r[2], 'bad_rate': r[3], 'min': str(r[4]), 'max': str(r[5])} for r in rows}
        ok = len(rows) == 4 and all(r[0] in EXPECTED_SPLITS and (r[1], r[2], str(r[4]), str(r[5])) == (EXPECTED_SPLITS[r[0]][0], EXPECTED_SPLITS[r[0]][1], EXPECTED_SPLITS[r[0]][3], EXPECTED_SPLITS[r[0]][4]) and abs(r[3]-EXPECTED_SPLITS[r[0]][2]) < 1e-12 for r in rows)
        add(ts, 'B9T04', 'EXACT_SPLIT_BAD_COUNTS_RATES_DATES', ok, observed, {k: {'accounts': v[0], 'bad_accounts': v[1], 'bad_rate': v[2], 'min': v[3], 'max': v[4]} for k, v in EXPECTED_SPLITS.items()})

        invalid = c.execute("SELECT COUNT(*) FROM mart.mart_credit_application_core WHERE issue_d IS NULL OR issue_d < DATE '2007-06-01' OR issue_d > DATE '2018-12-01'").fetchone()[0]
        add(ts, 'B9T05', 'ISSUE_DATE_VALIDITY', invalid == 0, {'invalid_issue_dates': invalid}, {'invalid_issue_dates': 0})

        sql = (a.repo_root / 'sql' / 'analytics' / '12_b9_vintage_temporal.sql').read_text(encoding='utf-8')
        source_ok = 'issue_d' in sql and 'issue_cohort' in sql and 'loan_status' not in sql and 'grade' not in sql
        add(ts, 'B9T06', 'TEMPORAL_AUTHORITY_SQL_SOURCE', source_ok, {'issue_d_present': 'issue_d' in sql, 'unsupported_authority_tokens': [x for x in ('loan_status', 'grade') if x in sql]}, {'authority': 'issue_d', 'unsupported_authority_tokens': []})

        docs = '\n'.join((a.repo_root / p).read_text(encoding='utf-8') for p in ('docs/B9_RUN_REPORT.md', 'outputs/b9/b9_summary.json', 'block-b/index.html') if (a.repo_root / p).exists())
        caveat_ok = bool(re.search(r'right truncation|right-truncated|resolution selection', docs, re.I)) and bool(re.search(r'2018', docs))
        add(ts, 'B9T07', 'RIGHT_TRUNCATION_CAVEAT_CONTENT', caveat_ok, {'caveat_found': caveat_ok}, {'2018_right_truncation_caveat': True})

        boundary_ok = bool(re.search(r'not causal|not a causal|descriptive', docs, re.I)) and not bool(re.search(r'\b(?:is|supports|provides|enables|claims)\s+(?:a )?(?:live monitoring|predictive PD|causal effect)\b', docs, re.I))
        add(ts, 'B9T08', 'CLAIM_BOUNDARY_CONTENT', boundary_ok, {'boundary_found': boundary_ok}, {'descriptive_and_non_live': True})

        comp = c.execute('SELECT issue_year, dimension, SUM(accounts), SUM(account_share_within_year), SUM(exposure_share_within_year), SUM(bad_accounts) FROM analytics.vintage_composition_annual GROUP BY issue_year, dimension ORDER BY issue_year, dimension').fetchall()
        ok = len(comp) > 0 and all(r[2] > 0 and abs(r[3]-1) < 1e-8 and abs(r[4]-1) < 1e-8 and r[5] >= 0 for r in comp) and {r[1] for r in comp} == {'purpose', 'home_ownership_n'}
        add(ts, 'B9T09', 'ANNUAL_COMPOSITION_RECONCILIATION', ok, {'year_dimension_rows': len(comp), 'dimensions': sorted({r[1] for r in comp}), 'all_shares_sum_one': ok}, {'dimensions': ['home_ownership_n', 'purpose'], 'shares_sum_one_per_year_dimension': True})
    finally: c.close()
    status = 'PASS' if all(t['status'] == 'PASS' for t in ts) else 'FAIL'
    payload = {'stage': 'B9', 'gate_status': status, 'tests': ts, 'claim_boundary': 'Vintage is descriptive and cohort-based. Temporal movement is associated/coincident/co-moving, not causal; this is not live monitoring.'}
    (a.output_dir/'b9_test_results.json').write_text(json.dumps(payload, indent=2, default=str)+'\n', encoding='utf-8')
    with (a.output_dir/'b9_test_results.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ['id','name','status']} for t in ts)
    print(json.dumps(payload, indent=2, default=str)); return 0 if status == 'PASS' else 1


if __name__ == '__main__': raise SystemExit(main())
