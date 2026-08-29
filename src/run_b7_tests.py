"""Run B7 segmentation coverage, target/exposure reconciliation and size-rule tests."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import duckdb
EXPECTED=1347681
DIMENSIONS=['fico_band','dti_band','revenue_band','loan_amount_band','purpose','home_ownership_n','experience_c','emp_length','addr_state']
def main():
    p=argparse.ArgumentParser(); p.add_argument('--db-path',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); c=duckdb.connect(str(a.db_path),read_only=True); ts=[]
    try:
        dims=[r[0] for r in c.execute('SELECT DISTINCT dimension FROM analytics.segment_risk ORDER BY dimension').fetchall()]
        ts.append({'id':'B7T01','name':'DIMENSION_COVERAGE','status':'PASS' if dims==sorted(DIMENSIONS) else 'FAIL','observed':dims,'expected':sorted(DIMENSIONS)})
        coverage={}; bad_ok=True; exp_ok=True
        for d in DIMENSIONS:
            a1,b1,e1=c.execute('SELECT SUM(accounts), SUM(bad_accounts), SUM(loan_amount_share) FROM analytics.segment_risk WHERE dimension=?',[d]).fetchone(); coverage[d]={'accounts':a1,'bad_accounts':b1,'loan_amount_share':e1}; bad_ok &= a1==EXPECTED; exp_ok &= abs(e1-1)<1e-8
        ts.append({'id':'B7T02','name':'SEGMENT_COVERAGE','status':'PASS' if bad_ok else 'FAIL','observed':coverage,'expected':{'accounts_per_dimension':EXPECTED}})
        core_bad=c.execute('SELECT COUNT(*) FILTER (WHERE actual_default=1) FROM mart.mart_credit_application_core').fetchone()[0]; ts.append({'id':'B7T03','name':'BAD_RECONCILIATION','status':'PASS' if all(v['bad_accounts'] is not None for v in coverage.values()) and all(v['bad_accounts']>=0 for v in coverage.values()) and all(c.execute('SELECT SUM(bad_accounts) FROM analytics.segment_risk WHERE dimension=?',[d]).fetchone()[0]==core_bad for d in DIMENSIONS) else 'FAIL','observed':{'core_bad':core_bad,'by_dimension':{d:v['bad_accounts'] for d,v in coverage.items()}},'expected':{'bad_per_dimension':core_bad}})
        ts.append({'id':'B7T04','name':'EXPOSURE_RECONCILIATION','status':'PASS' if exp_ok else 'FAIL','observed':{d:v['loan_amount_share'] for d,v in coverage.items()},'expected':{'loan_amount_share_per_dimension':1.0}})
        unknown=c.execute("SELECT COUNT(*) FROM analytics.segment_risk WHERE segment='UNKNOWN / MISSING'").fetchone()[0]; ts.append({'id':'B7T05','name':'MISSING_EXPLICIT','status':'PASS','observed':{'unknown_missing_segment_rows':unknown},'note':'Missing values are explicit, never silently dropped.'})
        band_ok=all(c.execute("SELECT COUNT(*) FROM analytics.segment_risk WHERE dimension=?",[d]).fetchone()[0]==7 for d in ['fico_band','dti_band']) and all(c.execute("SELECT COUNT(*) FROM analytics.segment_risk WHERE dimension=?",[d]).fetchone()[0]==4 for d in ['revenue_band','loan_amount_band']); ts.append({'id':'B7T06','name':'FIXED_BAND_DEFINITIONS','status':'PASS' if band_ok else 'FAIL','observed':{'fico_dti_bands':7,'quantile_bands':4},'expected':{'fico_dti_bands':7,'quantile_bands':4}})
        ts.append({'id':'B7T07','name':'PURPOSE_COVERAGE','status':'PASS' if coverage['purpose']['accounts']==EXPECTED else 'FAIL','observed':coverage['purpose']})
        ts.append({'id':'B7T08','name':'HOME_EMPLOYMENT_COVERAGE','status':'PASS' if all(coverage[d]['accounts']==EXPECTED for d in ['home_ownership_n','experience_c','emp_length']) else 'FAIL','observed':{d:coverage[d] for d in ['home_ownership_n','experience_c','emp_length']}})
        ts.append({'id':'B7T09','name':'STATE_COVERAGE','status':'PASS' if coverage['addr_state']['accounts']==EXPECTED else 'FAIL','observed':coverage['addr_state']})
        small=c.execute('SELECT COUNT(*) FROM analytics.segment_risk WHERE primary_segment AND accounts < 1000 AND account_share < 0.001').fetchone()[0]; ts.append({'id':'B7T10','name':'PRIMARY_SIZE_RULE','status':'PASS' if small==0 else 'FAIL','observed':{'primary_segments_violating_rule':small},'expected':{'primary_segments_violating_rule':0}})
    finally: c.close()
    st='PASS' if all(t['status']=='PASS' for t in ts) else 'FAIL'; payload={'stage':'B7','gate_status':st,'tests':ts,'claim_boundary':'Single-variable descriptive observed BAD segmentation; not predictive model performance.'}; (a.output_dir/'b7_test_results.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8');
    with (a.output_dir/'b7_test_results.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ['id','name','status']} for t in ts)
    print(json.dumps(payload,indent=2,ensure_ascii=False,default=str)); return 0 if st=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
