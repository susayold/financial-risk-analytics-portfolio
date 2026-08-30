"""Build B9 monthly, annual and temporal split vintage aggregates."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import duckdb
def clean(v): return v.isoformat() if hasattr(v,'isoformat') else v
def export(c,q,path):
    cur=c.execute(q); cols=[d[0] for d in cur.description]; rows=cur.fetchall()
    with path.open('w',newline='',encoding='utf-8') as f: w=csv.writer(f); w.writerow(cols); [w.writerow([clean(x) for x in r]) for r in rows]
    return cols,rows
def main():
    p=argparse.ArgumentParser(); p.add_argument('--db-path',type=Path,required=True); p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); c=duckdb.connect(str(a.db_path))
    try:
        c.execute((a.repo_root/'sql'/'analytics'/'12_b9_vintage_temporal.sql').read_text(encoding='utf-8'))
        _,monthly=export(c,'SELECT * FROM analytics.vintage_monthly',a.output_dir/'vintage_monthly.csv'); _,annual=export(c,'SELECT * FROM analytics.vintage_annual',a.output_dir/'vintage_annual.csv'); _,splits=export(c,'SELECT * FROM analytics.vintage_split',a.output_dir/'vintage_split.csv'); _,composition=export(c,'SELECT * FROM analytics.vintage_composition_annual',a.output_dir/'vintage_composition_annual.csv')
        (a.output_dir/'b9_summary.json').write_text(json.dumps({'stage':'B9','status':'BUILT','cohorts':len(monthly),'years':len(annual),'splits':len(splits),'composition_rows':len(composition),'composition_dimensions':['purpose','home_ownership_n'],'temporal_authority':'issue_d','caveat':'2018 resolved-loan sample is subject to right truncation and resolution selection; lower observed BAD is not confirmed credit-quality improvement; this is not live monitoring.'},indent=2)+'\n',encoding='utf-8')
        (a.output_dir/'b9_run_manifest.json').write_text(json.dumps({'stage':'B9','status':'BUILT','source_table':'mart.mart_credit_application_core','temporal_authority':'issue_d','tables':['analytics.vintage_monthly','analytics.vintage_annual','analytics.vintage_split','analytics.vintage_composition_annual'],'composition_dimensions':['purpose','home_ownership_n'],'causal_claims':False,'live_monitoring_claims':False},indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'stage':'B9','status':'BUILT','cohorts':len(monthly),'years':len(annual),'splits':len(splits),'composition_rows':len(composition)},indent=2))
    finally: c.close()
    return 0
if __name__=='__main__': raise SystemExit(main())
