"""Run B6 source-backed reconciliation, completeness and claim-boundary tests."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import duckdb

EXPECTED = {"accounts": 1_347_681, "bad": 269_249, "good": 1_078_432,
            "bad_rate": 0.19978689318911522, "total_amount": 19_417_698_475.0,
            "bad_amount": 4_186_020_700.0}


def add(tests: list[dict], test_id: str, name: str, ok: bool, observed: dict, expected: dict | str) -> None:
    tests.append({"id": test_id, "name": name, "status": "PASS" if ok else "FAIL", "observed": observed, "expected": expected})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    tests: list[dict] = []
    con = duckdb.connect(str(args.db_path), read_only=True)
    try:
        row = con.execute("""
            SELECT COUNT(*), COUNT(DISTINCT account_id), COUNT(*) FILTER (WHERE account_id IS NULL),
                   COUNT(*) FILTER (WHERE actual_default IS NULL OR actual_default NOT IN (0, 1))
            FROM mart.mart_credit_application_core
        """).fetchone()
        add(tests, "B6T01", "CORE_RECONCILIATION", row == (EXPECTED["accounts"], EXPECTED["accounts"], 0, 0),
            {"rows": row[0], "distinct_ids": row[1], "null_ids": row[2], "invalid_targets": row[3]},
            {"rows": EXPECTED["accounts"], "distinct_ids": EXPECTED["accounts"], "null_ids": 0, "invalid_targets": 0})

        row = con.execute("""
            SELECT COUNT(*) FILTER (WHERE actual_default=1), COUNT(*) FILTER (WHERE actual_default=0),
                   AVG(actual_default), COUNT(*) FILTER (WHERE actual_default IS NULL OR actual_default NOT IN (0,1))
            FROM mart.mart_credit_application_core
        """).fetchone()
        ok = row[0] == EXPECTED["bad"] and row[1] == EXPECTED["good"] and abs(row[2] - EXPECTED["bad_rate"]) < 1e-12 and row[3] == 0
        add(tests, "B6T02", "TARGET_RECONCILIATION", ok,
            {"bad": row[0], "good": row[1], "bad_rate": row[2], "invalid_targets": row[3]},
            {"bad": EXPECTED["bad"], "good": EXPECTED["good"], "bad_rate": EXPECTED["bad_rate"], "invalid_targets": 0})

        direct = con.execute("""
            SELECT SUM(loan_amnt), SUM(loan_amnt) FILTER (WHERE actual_default=1),
                   SUM(loan_amnt) FILTER (WHERE actual_default=1) / NULLIF(SUM(loan_amnt), 0)
            FROM mart.mart_credit_application_core
        """).fetchone()
        overview = con.execute("SELECT total_loan_amount, bad_associated_loan_amount, bad_associated_exposure_share FROM analytics.portfolio_overview").fetchone()
        ok = all(abs(float(a) - float(b)) < 1e-6 for a, b in zip(direct, overview))
        add(tests, "B6T03", "DIRECT_SOURCE_EXPOSURE_EQUALITY", ok,
            {"direct_core": direct, "portfolio_overview": overview}, {"same_values": True})

        fields = ["fico_n", "dti_n", "revenue", "loan_amnt"]
        direct_nulls = {field: con.execute(f"SELECT COUNT(*) FROM mart.mart_credit_application_core WHERE {field} IS NULL").fetchone()[0] for field in fields}
        profile_nulls = {row[0]: row[1] for row in con.execute("SELECT field_name, null_count FROM analytics.numeric_profile").fetchall()}
        add(tests, "B6T04", "DIRECT_SOURCE_NULL_COUNTS", direct_nulls == profile_nulls,
            {"direct_core": direct_nulls, "numeric_profile": profile_nulls}, {"each_field_equal": True})

        bad_ranges = con.execute("""
            SELECT COUNT(*) FROM analytics.numeric_profile
            WHERE min IS NULL OR max IS NULL OR min > max OR p01 > p05 OR p05 > p25 OR p25 > p50
               OR p50 > p75 OR p75 > p95 OR p95 > p99 OR p99 > max
        """).fetchone()[0]
        add(tests, "B6T05", "NUMERIC_PROFILE_SANITY", bad_ranges == 0, {"invalid_profile_rows": bad_ranges}, {"invalid_profile_rows": 0})

        rows = con.execute("""
            SELECT dimension, SUM(accounts), SUM(account_share), SUM(exposure_share)
            FROM analytics.portfolio_mix GROUP BY dimension ORDER BY dimension
        """).fetchall()
        ok = all(r[1] == EXPECTED["accounts"] and abs(r[2] - 1) < 1e-8 and abs(r[3] - 1) < 1e-8 for r in rows)
        add(tests, "B6T06", "ACCOUNT_AND_EXPOSURE_SHARE_SUM", ok,
            {r[0]: {"accounts": r[1], "account_share": r[2], "exposure_share": r[3]} for r in rows},
            {"accounts_per_dimension": EXPECTED["accounts"], "account_share_per_dimension": 1.0, "exposure_share_per_dimension": 1.0})

        forbidden = con.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema='mart' AND table_name='mart_credit_application_core'
              AND column_name IN ('grade','sub_grade','int_rate','installment','term','loan_status')
        """).fetchone()[0]
        add(tests, "B6T07", "PRICING_SAMPLE_BOUNDARY", forbidden == 0, {"pricing_fields_in_core": forbidden}, {"pricing_fields_in_core": 0})

        validator = args.repo_root / "src" / "validate_block_b_claims.py"
        proc = subprocess.run([sys.executable, str(validator), "--repo-root", str(args.repo_root)], capture_output=True, text=True)
        try: validation = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError: validation = {"status": "FAIL", "stdout": proc.stdout[-1000:], "stderr": proc.stderr[-1000:]}
        add(tests, "B6T08", "CLAIM_CONTRACT_STATIC_SOURCE", proc.returncode == 0 and validation.get("status") == "PASS", validation, {"status": "PASS"})
    finally:
        con.close()

    status = "PASS" if all(t["status"] == "PASS" for t in tests) else "FAIL"
    payload = {"stage": "B6", "gate_status": status, "tests": tests,
               "claim_boundary": "Descriptive portfolio composition and observed final-resolution BAD baseline; not 12-month PD."}
    (args.output_dir / "b6_test_results.json").write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    with (args.output_dir / "b6_test_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "name", "status"]); writer.writeheader()
        writer.writerows({k: t[k] for k in ("id", "name", "status")} for t in tests)
    print(json.dumps(payload, indent=2, default=str)); return 0 if status == "PASS" else 1


if __name__ == "__main__": raise SystemExit(main())
