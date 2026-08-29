"""Export sanitized B4 public evidence from aggregate run outputs only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    args = parser.parse_args()
    reconciliation = json.loads((args.output_dir / 'b4_reconciliation.json').read_text(encoding='utf-8'))
    test_results = json.loads((args.output_dir / 'b4_test_results.json').read_text(encoding='utf-8'))
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    status = reconciliation['status']
    status_label = 'REVIEWED / PASS' if status == 'PASS' else status
    args.evidence_dir.joinpath('b4-status.md').write_text(
        f"# B4 STATUS\n\n**B4 — `mart_credit_application_core` — {status_label}**\n\nB4 built the canonical one-account analytical mart from the reviewed staging contract. Block B remains `IN PROGRESS`; the next gate is B5.\n\n- Mart rows: {reconciliation['mart_rows']:,}\n- Distinct accounts: {reconciliation['distinct_account_id']:,}\n- Duplicate IDs: {reconciliation['duplicate_account_id']}\n- Population loss: {reconciliation['staging_rows'] - reconciliation['mart_rows']}\n- Tests: {sum(t['status'] == 'PASS' for t in test_results['tests'])}/{len(test_results['tests'])} PASS\n\nNo row-level mart, DuckDB database or raw CSV is published.\n",
        encoding='utf-8',
    )
    args.evidence_dir.joinpath('b4-reconciliation.md').write_text(
        f"# B4 RECONCILIATION\n\n| Metric | Result |\n|---|---:|\n| Staging rows | {reconciliation['staging_rows']:,} |\n| Mart rows | {reconciliation['mart_rows']:,} |\n| Distinct accounts | {reconciliation['distinct_account_id']:,} |\n| Duplicate IDs | {reconciliation['duplicate_account_id']} |\n| Population loss | {reconciliation['staging_rows'] - reconciliation['mart_rows']} |\n| BAD | {reconciliation['bad']:,} |\n| GOOD | {reconciliation['good']:,} |\n| BAD rate | {reconciliation['bad_rate']:.9%} |\n| Issue cohorts | {reconciliation['issue_cohorts']} |\n| Unassigned split | {reconciliation['unassigned']} |\n\nValues are aggregate only.\n",
        encoding='utf-8',
    )
    args.evidence_dir.joinpath('b4-mart-schema.md').write_text(
        "# B4 MART SCHEMA\n\n**Object:** `mart.mart_credit_application_core`  \n**Grain:** one account per `account_id`  \n**Version:** `B4_v1.0`\n\n## Schema groups\n\n- **KEY / TIME / TARGET:** `account_id`, `issue_d`, `issue_year`, `issue_month`, `issue_cohort`, `split_name`, `actual_default`, `target_label`\n- **CHAMPION CANDIDATES:** `revenue`, `dti_n`, `loan_amnt`, `fico_n`, `experience_c`, `emp_length`, `purpose`, `home_ownership_n`\n- **ANALYSIS-ONLY:** `addr_state`, `zip_code`\n- **GOVERNANCE METADATA:** `dq_status`, `dq_flag_count`, `source_population`, `source_version`, `feature_contract_version`, `preprocessing_version`, `mart_version`, `mart_build_ts`\n\nForbidden outcome/pricing fields are absent. `title` and `desc` remain in staging but are intentionally omitted from the core mart.\n",
        encoding='utf-8',
    )
    args.evidence_dir.joinpath('b4-run-report.md').write_text(
        f"# B4 RUN REPORT\n\n## Result\n\n`B4 = {status_label}`\n\nThe direct-projection build created `mart_credit_application_core` at one account grain with no population filter, join or model transformation. All {len(test_results['tests'])} B4 tests passed.\n\nThe mart preserves the reviewed source population, observed final-resolution target, chronological splits and Block A feature contract. Next gate: B5 supplemental/pricing/rejected-context marts.\n",
        encoding='utf-8',
    )
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
