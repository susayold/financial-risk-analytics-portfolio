"""Build B7 single-variable segment risk tables and locked band definitions."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import duckdb

def clean(v): return v.isoformat() if hasattr(v, "isoformat") else v

def export(con, query, path):
    cur = con.execute(query); cols = [d[0] for d in cur.description]; rows = cur.fetchall()
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(cols); [w.writerow([clean(x) for x in row]) for row in rows]
    return cols, rows

def main():
    p=argparse.ArgumentParser(); p.add_argument('--db-path',type=Path,required=True); p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    c=duckdb.connect(str(a.db_path))
    try:
        c.execute((a.repo_root/'sql'/'analytics'/'10_b7_segment_risk.sql').read_text(encoding='utf-8'))
        cols, rows = export(c, 'SELECT * FROM analytics.segment_risk', a.output_dir/'segment_risk.csv')
        cuts = c.execute('SELECT * FROM analytics.b7_band_cuts').fetchone()
        defs={'fico_band':['<600','600–639','640–679','680–719','720–759','760–799','800+'],'dti_band':['<10','10–19.99','20–29.99','30–39.99','40–59.99','60–99.99','100+'],'revenue_band':['Q1 (≤25th percentile)','Q2 (>25th–50th percentile)','Q3 (>50th–75th percentile)','Q4 (>75th percentile)'],'loan_amount_band':['Q1 (≤25th percentile)','Q2 (>25th–50th percentile)','Q3 (>50th–75th percentile)','Q4 (>75th percentile)'],'quantile_cut_points':{'revenue_q25':cuts[0],'revenue_q50':cuts[1],'revenue_q75':cuts[2],'loan_amnt_q25':cuts[3],'loan_amnt_q50':cuts[4],'loan_amnt_q75':cuts[5]},'missing_label':'UNKNOWN / MISSING','primary_segment_rule':'accounts >= 1,000 AND account_share >= 0.001'}
        (a.output_dir/'b7_band_definitions.json').write_text(json.dumps(defs,indent=2,ensure_ascii=False,default=clean)+'\n',encoding='utf-8')
        (a.output_dir/'b7_run_manifest.json').write_text(json.dumps({'stage':'B7','status':'BUILT','source_table':'mart.mart_credit_application_core','input_table':'analytics.segment_risk','dimensions':sorted(set(r[0] for r in rows)),'row_count':len(rows),'primary_segment_rule':'accounts >= 1000 AND account_share >= 0.001','bad_amount_to_total_exposure_definition':'segment BAD-associated loan amount / total portfolio loan amount','bad_associated_share_definition':'segment BAD-associated loan amount / total BAD-associated loan amount','wilson_confidence_level':0.95,'no_combinatorial_fishing':True},indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'stage':'B7','status':'BUILT','segment_rows':len(rows)},indent=2))
    finally: c.close()
    return 0
if __name__=='__main__': raise SystemExit(main())
