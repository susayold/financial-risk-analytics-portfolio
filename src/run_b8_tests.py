"""Run B8 concentration, informativeness and ranking tests."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import duckdb

DIMENSIONS = ['fico_band','dti_band','revenue_band','loan_amount_band','purpose','home_ownership_n','experience_c','emp_length','addr_state']
EXPECTED_BAD_AMOUNT = 4_186_020_700.0
EXPECTED_TOTAL_AMOUNT = 19_417_698_475.0


def add(ts, test_id, name, ok, observed, expected):
    ts.append({'id': test_id, 'name': name, 'status': 'PASS' if ok else 'FAIL', 'observed': observed, 'expected': expected})


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument('--db-path', type=Path, required=True); p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True); c = duckdb.connect(str(a.db_path), read_only=True); ts = []
    try:
        dims = [r[0] for r in c.execute('SELECT DISTINCT dimension FROM analytics.risk_concentration ORDER BY dimension').fetchall()]
        profiles = [r[0] for r in c.execute('SELECT dimension FROM analytics.b8_dimension_profile ORDER BY dimension').fetchall()]
        add(ts, 'B8T01', 'INPUT_AND_PROFILE_LOCK', dims == sorted(DIMENSIONS) and profiles == sorted(DIMENSIONS), {'risk_dimensions': dims, 'profile_dimensions': profiles}, {'dimensions': sorted(DIMENSIONS), 'profile_present': True})

        sums = c.execute('SELECT dimension, SUM(accounts), SUM(account_share), SUM(loan_amount_share), SUM(bad_associated_share) FROM analytics.risk_concentration GROUP BY dimension ORDER BY dimension').fetchall()
        ok = all(r[1] == 1_347_681 and abs(r[2]-1) < 1e-8 and abs(r[3]-1) < 1e-8 and abs(r[4]-1) < 1e-8 for r in sums)
        add(ts, 'B8T02', 'ACCOUNT_EXPOSURE_BAD_SHARE_RECONCILIATION', ok, {r[0]: {'accounts': r[1], 'account_share': r[2], 'exposure_share': r[3], 'bad_associated_share': r[4]} for r in sums}, {'each_dimension_sums': {'accounts': 1_347_681, 'account_share': 1.0, 'exposure_share': 1.0, 'bad_associated_share': 1.0}})

        rule_bad = c.execute("""
            SELECT COUNT(*) FROM analytics.risk_concentration
            WHERE materiality_flag <> (headline_eligible AND relative_bad_rate > 1.0 AND primary_segment AND accounts > 0)
        """).fetchone()[0]
        add(ts, 'B8T03', 'MATERIALITY_RULE', rule_bad == 0, {'rule_violations': rule_bad}, {'rule': 'headline_eligible AND relative_bad_rate > 1.0 AND primary_segment AND accounts > 0'})

        ranks = c.execute('SELECT materiality_rank, bad_associated_share, dimension, segment FROM analytics.risk_concentration WHERE materiality_flag ORDER BY materiality_rank').fetchall()
        rank_ok = [r[0] for r in ranks] == list(range(1, len(ranks)+1)) and all(ranks[i][1] >= ranks[i+1][1] for i in range(len(ranks)-1))
        add(ts, 'B8T04', 'RANK_REPRODUCIBILITY', rank_ok, {'material_rows': len(ranks), 'first_rows': ranks[:5]}, {'contiguous_rank': True, 'ordered_by': 'bad_associated_share DESC'})

        recon = c.execute('''
            SELECT dimension, SUM(bad_associated_loan_amount), SUM(bad_amount_to_total_exposure), SUM(bad_associated_share)
            FROM analytics.risk_concentration GROUP BY dimension ORDER BY dimension
        ''').fetchall()
        ok = all(abs(float(r[1])-EXPECTED_BAD_AMOUNT) < 1e-6 and abs(float(r[2])-EXPECTED_BAD_AMOUNT/EXPECTED_TOTAL_AMOUNT) < 1e-10 and abs(float(r[3])-1) < 1e-8 for r in recon)
        add(ts, 'B8T05', 'BAD_AMOUNT_SHARE_RECONCILIATION', ok, {r[0]: {'bad_amount': r[1], 'exposure_ratio': r[2], 'bad_associated_share': r[3]} for r in recon}, {'bad_amount': EXPECTED_BAD_AMOUNT, 'exposure_ratio': EXPECTED_BAD_AMOUNT/EXPECTED_TOTAL_AMOUNT, 'bad_associated_share': 1.0})

        small = c.execute('SELECT COUNT(*) FROM analytics.risk_concentration WHERE materiality_flag AND (accounts < 1000 OR account_share < 0.001)').fetchone()[0]
        add(ts, 'B8T06', 'SMALL_SEGMENT_CONTROL', small == 0, {'material_small_segments': small}, {'material_small_segments': 0})

        null_rank = c.execute('SELECT COUNT(*) FROM analytics.risk_concentration WHERE materiality_flag AND materiality_rank IS NULL').fetchone()[0]
        add(ts, 'B8T07', 'MATERIALITY_RANK_PRESENT', null_rank == 0, {'material_rows_without_rank': null_rank}, {'material_rows_without_rank': 0})

        quasi = c.execute("SELECT dimension, dominant_segment_account_share, dimension_status, headline_eligible FROM analytics.b8_dimension_profile WHERE dominant_segment_account_share > 0.995").fetchall()
        quasi_ok = len(quasi) > 0 and all(r[2] == 'QUASI_CONSTANT' and r[3] is False for r in quasi)
        add(ts, 'B8T08', 'DIMENSION_INFORMATIVENESS', quasi_ok, {'quasi_constant_dimensions': quasi}, {'threshold': '> 0.995', 'status': 'QUASI_CONSTANT', 'headline_eligible': False})

        experience = c.execute("SELECT materiality_flag, materiality_rank, dimension_status, headline_eligible FROM analytics.risk_concentration WHERE dimension='experience_c' AND segment='1'").fetchone()
        top = c.execute('SELECT dimension, segment, materiality_rank, headline_eligible FROM analytics.risk_concentration WHERE materiality_rank=1').fetchone()
        ok = experience is not None and experience[0] is False and experience[1] is None and experience[2] == 'QUASI_CONSTANT' and experience[3] is False and top is not None and top[0] != 'experience_c' and top[3] is True
        add(ts, 'B8T09', 'TOP_RANK_SEMANTIC_ELIGIBILITY', ok, {'experience_c_1': experience, 'rank_1': top}, {'experience_not_ranked': True, 'rank_1_headline_eligible': True})
    finally: c.close()
    status = 'PASS' if all(t['status'] == 'PASS' for t in ts) else 'FAIL'
    payload = {'stage': 'B8', 'gate_status': status, 'tests': ts, 'claim_boundary': 'Concentration is descriptive and single-variable; primary metric is BAD-associated loan amount share, not realized loss.'}
    (a.output_dir/'b8_test_results.json').write_text(json.dumps(payload, indent=2, default=str)+'\n', encoding='utf-8')
    with (a.output_dir/'b8_test_results.csv').open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ['id','name','status']} for t in ts)
    print(json.dumps(payload, indent=2, default=str)); return 0 if status == 'PASS' else 1


if __name__ == '__main__': raise SystemExit(main())
