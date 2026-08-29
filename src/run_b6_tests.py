"""Run B6 contract, reconciliation, completeness and boundary tests."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import duckdb


EXPECTED_ACCOUNTS = 1_347_681
EXPECTED_BAD = 269_249
EXPECTED_GOOD = 1_078_432
EXPECTED_BAD_RATE = 0.199786893


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(args.db_path), read_only=True)
    tests = []
    try:
        row = con.execute("SELECT COUNT(*), COUNT(DISTINCT account_id), COUNT(*) FILTER (WHERE account_id IS NULL) FROM mart.mart_credit_application_core").fetchone()
        tests.append({"id":"B6T01","name":"CORE_RECONCILIATION","status":"PASS" if row == (EXPECTED_ACCOUNTS, EXPECTED_ACCOUNTS, 0) else "FAIL","observed":{"rows":row[0],"distinct_ids":row[1],"null_ids":row[2]},"expected":{"rows":EXPECTED_ACCOUNTS,"distinct_ids":EXPECTED_ACCOUNTS,"null_ids":0}})
        row = con.execute("SELECT COUNT(*) FILTER (WHERE actual_default=1), COUNT(*) FILTER (WHERE actual_default=0), AVG(actual_default), COUNT(*) FILTER (WHERE actual_default IS NULL OR actual_default NOT IN (0,1)) FROM mart.mart_credit_application_core").fetchone()
        ok = row[0] == EXPECTED_BAD and row[1] == EXPECTED_GOOD and abs(row[2]-EXPECTED_BAD_RATE) < 1e-9 and row[3] == 0
        tests.append({"id":"B6T02","name":"TARGET_RECONCILIATION","status":"PASS" if ok else "FAIL","observed":{"bad":row[0],"good":row[1],"bad_rate":row[2],"unknown":row[3]},"expected":{"bad":EXPECTED_BAD,"good":EXPECTED_GOOD,"bad_rate":EXPECTED_BAD_RATE,"unknown":0}})
        row = con.execute("SELECT total_loan_amount, bad_associated_loan_amount, bad_associated_exposure_share FROM analytics.portfolio_overview").fetchone()
        ok = row[0] > 0 and row[1] >= 0 and 0 <= row[2] <= 1
        tests.append({"id":"B6T03","name":"EXPOSURE_RECONCILIATION","status":"PASS" if ok else "FAIL","observed":{"total_loan_amount":row[0],"bad_associated_loan_amount":row[1],"bad_associated_exposure_share":row[2]},"expected":{"total_positive":True,"bad_nonnegative":True,"share_between_0_and_1":True}})
        null_count = con.execute("SELECT SUM(null_count) FROM analytics.numeric_profile").fetchone()[0]
        tests.append({"id":"B6T04","name":"NULL_PROFILE","status":"PASS","observed":{"numeric_field_null_cells":null_count},"note":"Descriptive only; no imputation or capping."})
        bad_ranges = con.execute("SELECT COUNT(*) FROM analytics.numeric_profile WHERE min IS NULL OR max IS NULL OR min > max OR p01 > p05 OR p05 > p25 OR p25 > p50 OR p50 > p75 OR p75 > p95 OR p95 > p99 OR p99 > max").fetchone()[0]
        tests.append({"id":"B6T05","name":"NUMERIC_SANITY","status":"PASS" if bad_ranges == 0 else "FAIL","observed":{"invalid_profile_rows":bad_ranges},"expected":{"invalid_profile_rows":0}})
        rows = con.execute("SELECT dimension, SUM(accounts), SUM(exposure_share) FROM analytics.portfolio_mix GROUP BY dimension").fetchall()
        ok = all(r[1] == EXPECTED_ACCOUNTS and abs(r[2]-1) < 1e-8 for r in rows)
        tests.append({"id":"B6T06","name":"CATEGORY_SHARE_SUM","status":"PASS" if ok else "FAIL","observed":{r[0]:{"accounts":r[1],"exposure_share":r[2]} for r in rows},"expected":{"accounts":EXPECTED_ACCOUNTS,"exposure_share":1.0}})
        forbidden = con.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='mart' AND table_name='mart_credit_application_core' AND column_name IN ('grade','sub_grade','int_rate','installment','term','loan_status')").fetchone()[0]
        tests.append({"id":"B6T07","name":"PRICING_SAMPLE_BOUNDARY","status":"PASS" if forbidden == 0 else "FAIL","observed":{"pricing_fields_in_core":forbidden},"expected":{"pricing_fields_in_core":0},"note":"Matched pricing sample remains B5-controlled and is not mixed into core baseline metrics."})
    finally:
        con.close()
    status = "PASS" if all(t["status"] == "PASS" for t in tests) else "FAIL"
    payload = {"stage":"B6","gate_status":status,"tests":tests,"claim_boundary":"Descriptive portfolio composition and observed final-resolution BAD baseline; not 12-month PD."}
    (args.output_dir / "b6_test_results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with (args.output_dir / "b6_test_results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","name","status"]); w.writeheader(); w.writerows({k:t[k] for k in ["id","name","status"]} for t in tests)
    print(json.dumps(payload, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
