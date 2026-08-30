"""Run the final 15-test Block B closure gate from persisted evidence and frozen marts."""
from __future__ import annotations
import argparse, csv, json, subprocess, sys
from pathlib import Path
import duckdb

CORE = {'accounts': 1_347_681, 'bad': 269_249, 'good': 1_078_432, 'cohorts': 139, 'total_amount': 19_417_698_475.0, 'bad_amount': 4_186_020_700.0}


def add(tests, test_id, name, ok, observed, expected):
    tests.append({'id': test_id, 'name': name, 'status': 'PASS' if ok else 'FAIL', 'observed': observed, 'expected': expected})


def read(root, rel): return json.loads((root / rel).read_text(encoding='utf-8'))


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument('--db-path', type=Path, required=True); p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1]); p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True); r = a.repo_root; tests = []
    b4, b5, closure = read(r, 'outputs/b4/b4_test_results.json'), read(r, 'outputs/b5/b5_test_results.json'), read(r, 'outputs/b5/closure_static_validation.json')
    b6, b7, b8, b9 = read(r, 'outputs/b6/b6_test_results.json'), read(r, 'outputs/b7/b7_test_results.json'), read(r, 'outputs/b8/b8_test_results.json'), read(r, 'outputs/b9/b9_test_results.json')
    add(tests, 'BBF01', 'B4_PRIOR_GATE', b4.get('gate_status') == 'PASS', {'gate_status': b4.get('gate_status')}, {'gate_status': 'PASS'})
    add(tests, 'BBF02', 'B5_PRIOR_GATE', b5.get('gate_status') == 'PASS', {'gate_status': b5.get('gate_status')}, {'gate_status': 'PASS'})
    add(tests, 'BBF03', 'B4_B5_CLOSURE_STATIC', closure.get('status') == 'PASS', {'status': closure.get('status')}, {'status': 'PASS'})
    add(tests, 'BBF04', 'B6_GATE', b6.get('gate_status') == 'PASS' and len(b6.get('tests', [])) == 8, {'gate_status': b6.get('gate_status'), 'test_count': len(b6.get('tests', []))}, {'gate_status': 'PASS', 'test_count': 8})
    add(tests, 'BBF05', 'B7_GATE', b7.get('gate_status') == 'PASS' and len(b7.get('tests', [])) == 12, {'gate_status': b7.get('gate_status'), 'test_count': len(b7.get('tests', []))}, {'gate_status': 'PASS', 'test_count': 12})
    add(tests, 'BBF06', 'B8_GATE', b8.get('gate_status') == 'PASS' and len(b8.get('tests', [])) == 9, {'gate_status': b8.get('gate_status'), 'test_count': len(b8.get('tests', []))}, {'gate_status': 'PASS', 'test_count': 9})
    add(tests, 'BBF07', 'B9_GATE', b9.get('gate_status') == 'PASS' and len(b9.get('tests', [])) == 9, {'gate_status': b9.get('gate_status'), 'test_count': len(b9.get('tests', []))}, {'gate_status': 'PASS', 'test_count': 9})

    c = duckdb.connect(str(a.db_path), read_only=True)
    try:
        row = c.execute('SELECT COUNT(*), COUNT(*) FILTER (WHERE actual_default=1), COUNT(*) FILTER (WHERE actual_default=0), COUNT(DISTINCT issue_cohort), SUM(loan_amnt), SUM(loan_amnt) FILTER (WHERE actual_default=1) FROM mart.mart_credit_application_core').fetchone()
        ok = row[:4] == (CORE['accounts'], CORE['bad'], CORE['good'], CORE['cohorts']) and abs(row[4]-CORE['total_amount']) < 1e-6 and abs(row[5]-CORE['bad_amount']) < 1e-6
        add(tests, 'BBF08', 'CORE_POPULATION_LOCK', ok, {'accounts': row[0], 'bad': row[1], 'good': row[2], 'cohorts': row[3], 'total_amount': row[4], 'bad_amount': row[5]}, CORE)
        row = c.execute('SELECT MIN(issue_d), MAX(issue_d), COUNT(*) FILTER (WHERE issue_d IS NULL) FROM mart.mart_credit_application_core').fetchone()
        add(tests, 'BBF09', 'TARGET_AND_TEMPORAL_AUTHORITY', row[2] == 0 and str(row[0]) == '2007-06-01' and str(row[1]) == '2018-12-01', {'min_issue_d': str(row[0]), 'max_issue_d': str(row[1]), 'null_issue_d': row[2]}, {'min_issue_d': '2007-06-01', 'max_issue_d': '2018-12-01', 'null_issue_d': 0})
        split = {r[0]: r[1] for r in c.execute('SELECT split_name, COUNT(*) FROM mart.mart_credit_application_core GROUP BY split_name').fetchall()}
        add(tests, 'BBF10', 'TEMPORAL_SPLIT_LOCK', split == {'Development': 829347, 'Validation': 293057, 'OOT': 169117, 'Historical Shadow': 56160}, {'split_counts': split}, {'split_counts': {'Development': 829347, 'Validation': 293057, 'OOT': 169117, 'Historical Shadow': 56160}})
        b5r = read(r, 'outputs/b5/b5_reconciliation.json'); b5core = b5r.get('core_regression', {}); b5bridge = b5r.get('bridge', {}).get('counts', {}); b5rej = b5r.get('rejected', {})
        ok = b5core.get('rows') == CORE['accounts'] and b5core.get('bad') == CORE['bad'] and b5bridge.get('MATCHED') == 325255 and b5bridge.get('FIGSHARE_ONLY') == 6610 and b5bridge.get('CORE_ONLY') == 1022426 and b5rej.get('rows') == 27648741
        add(tests, 'BBF11', 'B5_POPULATIONS_LOCK', ok, {'core': b5core, 'bridge_counts': b5bridge, 'rejected_rows': b5rej.get('rows')}, {'matched': 325255, 'figshare_only': 6610, 'core_only': 1022426, 'rejected_context': 27648741})
        semantic = c.execute('SELECT COUNT(*) FROM analytics.segment_risk WHERE primary_segment <> (accounts >= 1000 AND account_share >= 0.001)').fetchone()[0]
        badshare = c.execute('SELECT COUNT(*) FROM (SELECT dimension, SUM(bad_associated_share) s FROM analytics.segment_risk GROUP BY dimension HAVING ABS(s-1) >= 1e-8)').fetchone()[0]
        add(tests, 'BBF12', 'B7_SEMANTICS_LOCK', semantic == 0 and badshare == 0, {'primary_rule_violations': semantic, 'bad_share_sum_violations': badshare}, {'violations': 0})
        profile = c.execute("SELECT COUNT(*) FROM analytics.b8_dimension_profile WHERE dimension_status='QUASI_CONSTANT' AND headline_eligible=FALSE AND dominant_segment_account_share > 0.995").fetchone()[0]
        exp = c.execute("SELECT COUNT(*) FROM analytics.risk_concentration WHERE dimension='experience_c' AND materiality_flag=FALSE AND materiality_rank IS NULL").fetchone()[0]
        add(tests, 'BBF13', 'B8_INFORMATIVENESS_LOCK', profile >= 1 and exp >= 1, {'quasi_constant_profiles': profile, 'experience_audit_only_rows': exp}, {'experience_audit_only': True})
    finally: c.close()

    validator = subprocess.run([sys.executable, str(r/'src/validate_block_b_claims.py'), '--repo-root', str(r)], capture_output=True, text=True)
    add(tests, 'BBF14', 'CLAIM_BOUNDARY_LOCK', validator.returncode == 0, {'validator_returncode': validator.returncode}, {'validator_returncode': 0})
    required = ['docs/BLOCK_B_FINAL_LOCK.md','docs/BLOCK_B_FINAL_CLOSURE_REMEDIATION.md','docs/BLOCK_B_ANALYTICAL_FINDINGS.md','docs/BLOCK_B_ASSUMPTIONS_AND_LIMITS.md','evidence/block-b/block-b-final-lock.md','evidence/block-b/b6-portfolio-overview.md','evidence/block-b/b7-segment-risk.md','evidence/block-b/b8-risk-concentration.md','evidence/block-b/b9-vintage-analysis.md','outputs/b9/vintage_composition_annual.csv','block-b/index.html']
    tracked = subprocess.run(['git', 'ls-files'], cwd=r, capture_output=True, text=True).stdout.splitlines()
    privacy_bad = [x for x in tracked if x.lower().endswith(('.duckdb', '.parquet')) or x.lower().endswith('.csv') and ('raw' in x.lower() or 'source' in x.lower())]
    site = (r/'block-b/index.html').read_text(encoding='utf-8')
    site_ok = all(x in site for x in ('B0–B9 · FINAL REVIEWED / LOCKED', 'Next: Block C', '9/9 tests', '43 material rows')) and 'experience_c = 1</b>' not in site and 'Data Engineering &amp; Quality Control</title>' not in site
    release_ok = all((r/x).exists() for x in required) and not privacy_bad and site_ok
    add(tests, 'BBF15', 'PUBLIC_EVIDENCE_PRIVACY_WEBSITE', release_ok, {'missing_files': [x for x in required if not (r/x).exists()], 'privacy_bad_tracked_files': privacy_bad, 'website_consistent': site_ok}, {'all_required_files_present': True, 'no_raw_tracked': True, 'website_consistent': True})

    status = 'PASS' if all(t['status'] == 'PASS' for t in tests) else 'FAIL'
    payload = {'stage': 'BLOCK_B_FINAL_QA', 'gate_status': status, 'test_count': len(tests), 'tests': tests, 'pre_closure_commit': 'e325d7f', 'baseline_change': False, 'target_state': 'BLOCK B = FINAL REVIEWED / LOCKED'}
    (a.output_dir/'block_b_final_qa.json').write_text(json.dumps(payload, indent=2, default=str)+'\n', encoding='utf-8')
    with (a.output_dir/'block_b_final_qa.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ['id','name','status']} for t in tests)
    reconciliation = {'stage': 'BLOCK_B_FINAL_QA', 'status': status, 'pre_closure_commit': 'e325d7f', 'baseline_change': False, 'core_baseline': CORE, 'gates': {x: payload['tests'][i]['status'] for i, x in enumerate(['B4','B5','closure','B6','B7','B8','B9'])}}
    (a.output_dir/'block_b_final_reconciliation.json').write_text(json.dumps(reconciliation, indent=2, default=str)+'\n', encoding='utf-8')
    print(json.dumps(payload, indent=2, default=str)); return 0 if status == 'PASS' else 1


if __name__ == '__main__': raise SystemExit(main())
