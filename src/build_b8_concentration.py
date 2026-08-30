"""Build B8 risk concentration output from the locked B7 table."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import duckdb
def clean(v): return v.isoformat() if hasattr(v,'isoformat') else v
def main():
    p=argparse.ArgumentParser(); p.add_argument('--db-path',type=Path,required=True); p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); c=duckdb.connect(str(a.db_path))
    try:
        c.execute((a.repo_root/'sql'/'analytics'/'11_b8_risk_concentration.sql').read_text(encoding='utf-8'))
        q='SELECT * FROM analytics.risk_concentration'; cur=c.execute(q); cols=[d[0] for d in cur.description]; rows=cur.fetchall()
        with (a.output_dir/'risk_concentration.csv').open('w',newline='',encoding='utf-8') as f: w=csv.writer(f); w.writerow(cols); [w.writerow([clean(x) for x in row]) for row in rows]
        pcur=c.execute('SELECT * FROM analytics.b8_dimension_profile'); pcols=[d[0] for d in pcur.description]; prows=pcur.fetchall()
        with (a.output_dir/'b8_dimension_profile.csv').open('w',newline='',encoding='utf-8') as f: w=csv.writer(f); w.writerow(pcols); [w.writerow([clean(x) for x in row]) for row in prows]
        summary=c.execute("SELECT COUNT(*) FILTER (WHERE materiality_flag), SUM(bad_associated_share) FILTER (WHERE materiality_flag), MAX(materiality_rank), COUNT(*) FILTER (WHERE dimension_status='QUASI_CONSTANT') FROM analytics.risk_concentration").fetchone()
        (a.output_dir/'b8_summary.json').write_text(json.dumps({'stage':'B8','status':'BUILT','material_segments':summary[0],'material_bad_associated_share_sum':summary[1],'max_materiality_rank':summary[2],'quasi_constant_dimensions':summary[3],'materiality_rule':'headline_eligible AND relative_bad_rate > 1.0 AND primary_segment = TRUE','dimension_rule':'dominant_segment_account_share > 0.995 => QUASI_CONSTANT','concentration_index_definition':'relative_bad_rate × loan_amount_share; descriptive only','primary_ranking_metric':'bad_associated_share = segment BAD-associated amount / total BAD-associated amount'},indent=2)+'\n',encoding='utf-8')
        (a.output_dir/'b8_run_manifest.json').write_text(json.dumps({'stage':'B8','status':'BUILT','source_table':'analytics.segment_risk','dimension_profile':'analytics.b8_dimension_profile','ranking_key':'bad_associated_share DESC','single_variable_only':True,'no_combinatorial_fishing':True},indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'stage':'B8','status':'BUILT','rows':len(rows),'material_segments':summary[0]},indent=2))
    finally: c.close()
    return 0
if __name__=='__main__': raise SystemExit(main())
