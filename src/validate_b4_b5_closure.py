"""Static closure validator; does not require raw data or a DuckDB runtime."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1]); ap.add_argument('--output', type=Path, required=True); args = ap.parse_args()
    root = args.repo_root
    build = (root/'src'/'build_marts.py').read_text(encoding='utf-8')
    b4sql = (root/'sql'/'marts'/'05_mart_credit_application_core.sql').read_text(encoding='utf-8')
    reject_sql = (root/'sql'/'staging'/'03_stg_lc_rejected.sql').read_text(encoding='utf-8')
    ingest = (root/'src'/'ingest_supplemental.py').read_text(encoding='utf-8')
    runner = (root/'src'/'run_b5_tests.py').read_text(encoding='utf-8')
    contract = yaml.safe_load((root/'config'/'b5_contract.yaml').read_text(encoding='utf-8'))
    checks = []
    def check(name, passed, detail=''):
        checks.append({'check': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail})
    check('expected staging contains title', "'addr_state', 'zip_code', 'title', 'desc', 'actual_default'" in build)
    check('expected staging contains desc', "'title', 'desc', 'actual_default'" in build)
    check('B4 mart excludes title/desc', 'title' not in b4sql and 'desc' not in b4sql)
    check('B4 uses STRUCTURAL_PASS', "'STRUCTURAL_PASS' AS dq_status" in b4sql and "'PASS' AS dq_status" not in b4sql)
    check('B4 dq_flag_count is NULL', 'CAST(NULL AS INTEGER) AS dq_flag_count' in b4sql and '0 AS dq_flag_count' not in b4sql)
    check('RejectStats DTI removes percent', "REPLACE(TRIM(debt_to_income_ratio), '%', '')" in reject_sql)
    check('technical key uses materialized rowid', 'rowid + 1' in ingest)
    check('unordered row_number key removed', 'row_number() OVER ()' not in ingest)
    expected_roles = {'sub_grade': 'BENCHMARK_ONLY', 'grade_derived': 'BENCHMARK_ONLY', 'int_rate': 'ECONOMICS_ONLY', 'installment': 'ECONOMICS_ONLY', 'term': 'ECONOMICS_ONLY'}
    check('YAML pricing roles exact', contract.get('pricing_fields') == expected_roles)
    check('test runner enforces YAML roles', 'yaml.safe_load' in runner and 'actual_roles == EXPECTED_PRICING_ROLES' in runner)
    check('B5T13 exists', "'B5T13'" in runner and 'REJECTED_PARSE_QUALITY' in runner)
    stale = ['Constant `PASS`', 'Constant `0`', 'No account-level exceptions existed upstream', 'propagated account-level DQ flag count']
    stale_hits = [s for s in stale if s in (root/'docs'/'B4_DATA_DICTIONARY.md').read_text(encoding='utf-8') or s in (root/'docs'/'B4_ASSUMPTIONS_AND_LIMITS.md').read_text(encoding='utf-8') or s in (root/'docs'/'B4_RUN_REPORT.md').read_text(encoding='utf-8')]
    check('stale account-level-DQ wording absent', not stale_hits, str(stale_hits))
    payload = {'block': 'B4_B5_CLOSURE', 'status': 'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL', 'checks': checks}
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': payload['status'], 'pass_count': sum(c['status']=='PASS' for c in checks), 'check_count': len(checks)}, indent=2))
    return 0 if payload['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
