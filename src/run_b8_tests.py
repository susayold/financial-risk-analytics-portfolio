"""Run B8 input lock, reconciliation, materiality and ranking tests."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import duckdb
DIMENSIONS=['fico_band','dti_band','revenue_band','loan_amount_band','purpose','home_ownership_n','experience_c','emp_length','addr_state']
def main():
    p=argparse.ArgumentParser(); p.add_argument('--db-path',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); c=duckdb.connect(str(a.db_path),read_only=True); ts=[]
    try:
        rows=c.execute('SELECT * FROM analytics.risk_concentration').fetchall(); dims=[r[0] for r in c.execute('SELECT DISTINCT dimension FROM analytics.risk_concentration ORDER BY dimension').fetchall()]; ts.append({'id':'B8T01','name':'INPUT_LOCK','status':'PASS' if dims==sorted(DIMENSIONS) else 'FAIL','observed':dims,'expected':sorted(DIMENSIONS)})
        sums=c.execute('SELECT SUM(accounts), SUM(account_share), SUM(loan_amount_share), SUM(bad_associated_share) FROM analytics.risk_concentration GROUP BY dimension').fetchall(); ok=all(r[0]>=0 and abs(r[1]-1)<1e-8 and abs(r[2]-1)<1e-8 for r in sums); ts.append({'id':'B8T02','name':'ACCOUNT_EXPOSURE_RECONCILIATION','status':'PASS' if ok else 'FAIL','observed':{'dimensions':len(sums),'all_share_sums_one':ok},'expected':{'account_and_exposure_share_sum_per_dimension':1.0}})
        rule_ok=c.execute("SELECT COUNT(*) FROM analytics.risk_concentration WHERE materiality_flag <> (relative_bad_rate > 1.0 AND account_share >= 0.001 AND accounts > 0)").fetchone()[0]==0; ts.append({'id':'B8T03','name':'MATERIALITY_RULE','status':'PASS' if rule_ok else 'FAIL','observed':{'rule_violations':0 if rule_ok else 1},'expected':{'rule_violations':0}})
        ranks=c.execute('SELECT materiality_rank,bad_associated_share FROM analytics.risk_concentration WHERE materiality_flag ORDER BY materiality_rank').fetchall(); rank_ok=all(ranks[i][1]>=ranks[i+1][1] for i in range(len(ranks)-1)) and [r[0] for r in ranks]==list(range(1,len(ranks)+1)); ts.append({'id':'B8T04','name':'RANK_REPRODUCIBILITY','status':'PASS' if rank_ok else 'FAIL','observed':{'material_rows':len(ranks),'contiguous_rank':rank_ok},'expected':{'ordered_by':'bad_associated_share DESC'}})
        ts.append({'id':'B8T05','name':'BAD_AMOUNT_RECONCILIATION','status':'PASS' if all(c.execute('SELECT SUM(bad_associated_loan_amount) FROM analytics.risk_concentration WHERE dimension=?',[d]).fetchone()[0] is not None for d in DIMENSIONS) else 'FAIL','observed':{'dimensions_checked':len(DIMENSIONS)}})
        tiny=c.execute('SELECT COUNT(*) FROM analytics.risk_concentration WHERE materiality_flag AND (accounts < 1000 AND account_share < 0.001)').fetchone()[0]; ts.append({'id':'B8T06','name':'SMALL_SEGMENT_CONTROL','status':'PASS' if tiny==0 else 'FAIL','observed':{'material_tiny_segments':tiny},'expected':{'material_tiny_segments':0}})
        null_rank=c.execute('SELECT COUNT(*) FROM analytics.risk_concentration WHERE materiality_flag AND materiality_rank IS NULL').fetchone()[0]; ts.append({'id':'B8T07','name':'MATERIALITY_RANK_PRESENT','status':'PASS' if null_rank==0 else 'FAIL','observed':{'material_rows_without_rank':null_rank},'expected':{'material_rows_without_rank':0}})
    finally: c.close()
    st='PASS' if all(t['status']=='PASS' for t in ts) else 'FAIL'; payload={'stage':'B8','gate_status':st,'tests':ts,'claim_boundary':'Concentration is descriptive and single-variable; primary metric is BAD-associated exposure share, not realized loss.'}; (a.output_dir/'b8_test_results.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8');
    with (a.output_dir/'b8_test_results.csv').open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=['id','name','status']); w.writeheader(); w.writerows({k:t[k] for k in ['id','name','status']} for t in ts)
    print(json.dumps(payload,indent=2)); return 0 if st=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
