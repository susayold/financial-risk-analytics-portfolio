"""Run B7 executable segmentation coverage, semantics and CI tests."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import duckdb

EXPECTED = 1_347_681
EXPECTED_BAD = 269_249
EXPECTED_BAD_AMOUNT = 4_186_020_700.0
EXPECTED_TOTAL_AMOUNT = 19_417_698_475.0
EXPECTED_BAD_SHARE = EXPECTED_BAD_AMOUNT / EXPECTED_TOTAL_AMOUNT
DIMENSIONS = ['fico_band', 'dti_band', 'revenue_band', 'loan_amount_band', 'purpose', 'home_ownership_n', 'experience_c', 'emp_length', 'addr_state']
FICO = ['<600', '600–639', '640–679', '680–719', '720–759', '760–799', '800+']
DTI = ['<10', '10–19.99', '20–29.99', '30–39.99', '40–59.99', '60–99.99', '100+']
QUANTILE = ['Q1 (≤25th percentile)', 'Q2 (>25th–50th percentile)', 'Q3 (>50th–75th percentile)', 'Q4 (>75th percentile)']


def main() -> int:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(); p.add_argument('--db-path', type=Path, required=True); p.add_argument('--output-dir', type=Path, required=True); p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1]); a = p.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)
    c = duckdb.connect(str(a.db_path), read_only=True); tests = []
    try:
        dims = [r[0] for r in c.execute('SELECT DISTINCT dimension FROM analytics.segment_risk ORDER BY dimension').fetchall()]
        tests.append({'id':'B7T01','name':'DIMENSION_COVERAGE','status':'PASS' if dims == sorted(DIMENSIONS) else 'FAIL','observed':dims,'expected':sorted(DIMENSIONS)})
        coverage = {}; missing_checks = {}; semantic_sums = {}
        for d in DIMENSIONS:
            row = c.execute('SELECT SUM(accounts), SUM(bad_accounts), SUM(loan_amount_share), SUM(bad_amount_to_total_exposure), SUM(bad_associated_share) FROM analytics.segment_risk WHERE dimension=?', [d]).fetchone()
            coverage[d] = {'accounts':row[0], 'bad_accounts':row[1], 'loan_amount_share':row[2], 'bad_amount_to_total_exposure':row[3], 'bad_associated_share':row[4]}
            semantic_sums[d] = {'bad_share':row[4], 'exposure_ratio':row[3]}
        tests.append({'id':'B7T02','name':'SEGMENT_COVERAGE','status':'PASS' if all(x['accounts'] == EXPECTED for x in coverage.values()) else 'FAIL','observed':coverage,'expected':{'accounts_per_dimension':EXPECTED}})
        tests.append({'id':'B7T03','name':'BAD_RECONCILIATION','status':'PASS' if all(x['bad_accounts'] == EXPECTED_BAD for x in coverage.values()) else 'FAIL','observed':{'core_bad':EXPECTED_BAD,'by_dimension':{d:x['bad_accounts'] for d,x in coverage.items()}},'expected':{'bad_per_dimension':EXPECTED_BAD}})
        tests.append({'id':'B7T04','name':'EXPOSURE_RECONCILIATION','status':'PASS' if all(abs(x['loan_amount_share']-1) < 1e-8 for x in coverage.values()) else 'FAIL','observed':{d:x['loan_amount_share'] for d,x in coverage.items()},'expected':{'loan_amount_share_per_dimension':1.0}})
        categorical = {'purpose':'purpose','home_ownership_n':'home_ownership_n','experience_c':'experience_c','emp_length':'emp_length','addr_state':'addr_state'}
        for dim, field in categorical.items():
            source_missing = c.execute(f"SELECT COUNT(*) FROM mart.mart_credit_application_core WHERE {field} IS NULL OR TRIM(CAST({field} AS VARCHAR)) = ''").fetchone()[0]
            output_missing = c.execute("SELECT COALESCE(SUM(accounts),0) FROM analytics.segment_risk WHERE dimension=? AND segment='UNKNOWN / MISSING'", [dim]).fetchone()[0]
            missing_checks[dim] = {'source_missing':source_missing,'output_unknown_missing':output_missing}
        numeric_missing = {}
        for field, dim in [('fico_n','fico_band'),('dti_n','dti_band'),('revenue','revenue_band'),('loan_amnt','loan_amount_band')]:
            source_missing = c.execute(f'SELECT COUNT(*) FROM mart.mart_credit_application_core WHERE {field} IS NULL').fetchone()[0]
            output_missing = c.execute("SELECT COALESCE(SUM(accounts),0) FROM analytics.segment_risk WHERE dimension=? AND segment='UNKNOWN / MISSING'", [dim]).fetchone()[0]
            numeric_missing[dim] = {'source_missing':source_missing,'output_unknown_missing':output_missing}
        missing_ok = all(x['source_missing'] == x['output_unknown_missing'] for x in list(missing_checks.values()) + list(numeric_missing.values()))
        tests.append({'id':'B7T05','name':'MISSING_EXPLICIT','status':'PASS' if missing_ok else 'FAIL','observed':{'categorical':missing_checks,'numeric':numeric_missing},'expected':'source NULL/blank counts equal UNKNOWN / MISSING accounts'})
        band_rows = {d:[r[0] for r in c.execute('SELECT segment FROM analytics.segment_risk WHERE dimension=? ORDER BY segment', [d]).fetchall()] for d in ['fico_band','dti_band','revenue_band','loan_amount_band']}
        cuts = c.execute('SELECT * FROM analytics.b7_band_cuts').fetchone(); expected_cuts = [46600.0,65000.0,92000.0,7975.0,12000.0,20000.0]
        bands_ok = set(band_rows['fico_band']) == set(FICO) and set(band_rows['dti_band']) == set(DTI) and set(band_rows['revenue_band']) == set(QUANTILE) and set(band_rows['loan_amount_band']) == set(QUANTILE) and all(abs(float(x)-y) < 1e-9 for x,y in zip(cuts,expected_cuts))
        tests.append({'id':'B7T06','name':'EXACT_BAND_DEFINITIONS','status':'PASS' if bands_ok else 'FAIL','observed':{'labels':band_rows,'cuts':list(cuts)},'expected':{'fico':FICO,'dti':DTI,'quantile_cuts':expected_cuts}})
        tests.append({'id':'B7T07','name':'PURPOSE_COVERAGE','status':'PASS' if coverage['purpose']['accounts']==EXPECTED else 'FAIL','observed':coverage['purpose']})
        tests.append({'id':'B7T08','name':'HOME_EMPLOYMENT_COVERAGE','status':'PASS' if all(coverage[d]['accounts']==EXPECTED for d in ['home_ownership_n','experience_c','emp_length']) else 'FAIL','observed':{d:coverage[d] for d in ['home_ownership_n','experience_c','emp_length']}})
        tests.append({'id':'B7T09','name':'STATE_COVERAGE','status':'PASS' if coverage['addr_state']['accounts']==EXPECTED else 'FAIL','observed':coverage['addr_state']})
        rule_violations = c.execute('SELECT COUNT(*) FROM analytics.segment_risk WHERE primary_segment <> (accounts >= 1000 AND account_share >= 0.001)').fetchone()[0]
        tests.append({'id':'B7T10','name':'PRIMARY_SIZE_RULE','status':'PASS' if rule_violations==0 else 'FAIL','observed':{'rule_violations':rule_violations},'expected':'accounts >= 1000 AND account_share >= 0.001'})
        bad_rows = c.execute('SELECT SUM(bad_associated_loan_amount), SUM(bad_amount_to_total_exposure), SUM(bad_associated_share) FROM analytics.segment_risk GROUP BY dimension').fetchall()
        bad_share_ok = all(abs(float(r[0])-EXPECTED_BAD_AMOUNT)<1e-6 and abs(float(r[1])-EXPECTED_BAD_SHARE)<1e-10 and abs(float(r[2])-1)<1e-8 for r in bad_rows)
        tests.append({'id':'B7T11','name':'BAD_SHARE_RECONCILIATION','status':'PASS' if bad_share_ok else 'FAIL','observed':{'expected_bad_amount':EXPECTED_BAD_AMOUNT,'expected_exposure_ratio':EXPECTED_BAD_SHARE,'dimension_count':len(bad_rows)},'expected':{'bad_associated_share_per_dimension':1.0,'bad_amount_to_total_exposure_per_dimension':EXPECTED_BAD_SHARE}})
        ci_bad = c.execute('SELECT COUNT(*) FROM analytics.segment_risk WHERE accounts > 0 AND (wilson_lower_95 IS NULL OR wilson_upper_95 IS NULL OR wilson_lower_95 < 0 OR wilson_upper_95 > 1 OR wilson_lower_95 > bad_rate OR bad_rate > wilson_upper_95)').fetchone()[0]
        tests.append({'id':'B7T12','name':'WILSON_CI','status':'PASS' if ci_bad==0 else 'FAIL','observed':{'invalid_ci_rows':ci_bad},'expected':{'invalid_ci_rows':0}})
    finally: c.close()
    status = 'PASS' if all(t['status']=='PASS' for t in tests) else 'FAIL'; payload={'stage':'B7','gate_status':status,'tests':tests,'claim_boundary':'Single-variable descriptive observed BAD segmentation; not predictive model performance.'}; (a.output_dir/'b7_test_results.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8')
    with (a.output_dir/'b7_test_results.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ['id','name','status']} for t in tests)
    print(json.dumps(payload,indent=2,ensure_ascii=False,default=str)); return 0 if status=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
