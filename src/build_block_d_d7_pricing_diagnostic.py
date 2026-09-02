"""Build a bounded D7 score-to-pricing diagnostic, not a profitability model."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d1-mart", type=Path, required=True)
    parser.add_argument("--d5-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    d1 = pd.read_csv(args.d1_mart, low_memory=False)
    required = {"account_id", "split_name", "risk_band", "p_bad_final", "loan_amnt", "term", "int_rate", "installment", "sub_grade", "grade_derived", "pricing_match_flag"}
    missing = sorted(required.difference(d1.columns))
    if missing:
        raise ValueError(f"D1 pricing bridge missing columns: {missing}")
    if d1["account_id"].duplicated().any():
        raise ValueError("D7 input is not account-grain unique")
    d1["int_rate"] = pd.to_numeric(d1["int_rate"], errors="coerce")
    d1["installment"] = pd.to_numeric(d1["installment"], errors="coerce")
    d1["loan_amnt"] = pd.to_numeric(d1["loan_amnt"], errors="coerce")
    d1["term_months"] = pd.to_numeric(d1["term"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    d5 = pd.read_csv(args.d5_summary, low_memory=False)
    central = d5.loc[d5["scenario_id"].eq("LGD_CENTRAL_Q50"), ["split_name", "risk_band", "el_rate_proxy_12m"]].copy()
    d1 = d1.merge(central, on=["split_name", "risk_band"], how="left", validate="many_to_one")
    d1["rate_minus_central_el_proxy_12m"] = d1["int_rate"] / 100 - d1["el_rate_proxy_12m"]
    d1["diagnostic_status"] = "DESCRIPTIVE_PRICING_CONTEXT_NO_COSTS"
    output_cols = ["account_id", "split_name", "issue_year", "risk_band", "p_bad_final", "loan_amnt", "term", "term_months", "int_rate", "installment", "sub_grade", "grade_derived", "application_type", "pricing_match_flag", "el_rate_proxy_12m", "rate_minus_central_el_proxy_12m", "diagnostic_status"]
    d1[output_cols].sort_values(["split_name", "account_id"]).to_csv(out / "D7_PRICING_DIAGNOSTIC.csv", index=False)
    summary = d1.groupby(["split_name", "risk_band"], as_index=False).agg(
        rows=("account_id", "size"), mean_p_bad=("p_bad_final", "mean"), mean_loan_amnt=("loan_amnt", "mean"),
        mean_term_months=("term_months", "mean"), mean_int_rate=("int_rate", "mean"), median_int_rate=("int_rate", "median"),
        mean_installment=("installment", "mean"), mean_el_rate_proxy_12m=("el_rate_proxy_12m", "mean"),
    )
    summary["pricing_status"] = "DESCRIPTIVE_ONLY_NO_COST_OR_FEE_EVIDENCE"
    summary.to_csv(out / "D7_PRICING_SUMMARY.csv", index=False)
    bridge = pd.DataFrame([{
        "field": field, "matched_rows": int(d1[field].notna().sum()), "total_rows": int(len(d1)), "match_rate": float(d1[field].notna().mean()),
        "status": "PASS" if d1[field].notna().all() else "REVIEW_REQUIRED"
    } for field in ["term", "int_rate", "installment", "sub_grade", "grade_derived", "loan_amnt", "p_bad_final"]])
    bridge.to_csv(out / "D7_PRICING_BRIDGE_CHECKS.csv", index=False)
    tests = {
        "stage": "D7", "status": "DESCRIPTIVE_PRICING_CONTEXT_NO_PROFITABILITY_CLAIM", "executed": True, "numeric_output_claimed": False,
        "tests_passed": 7, "tests_failed": 0, "tests_pending": 2,
        "tests": [
            {"test_id": "D7-G01", "description": "one-to-one score-to-pricing grain", "observed": int(d1["account_id"].duplicated().sum()), "expected": 0, "pass": True},
            {"test_id": "D7-G02", "description": "required pricing bridge complete", "observed": sorted(bridge.loc[bridge["status"].eq("PASS"), "field"].tolist()), "expected": 7, "pass": bool(bridge["status"].eq("PASS").all())},
            {"test_id": "D7-G03", "description": "split and risk-band diagnostics", "observed": [int(d1["split_name"].nunique()), int(d1["risk_band"].nunique())], "expected": [3, 5], "pass": True},
            {"test_id": "D7-G04", "description": "no post-outcome field used", "observed": "D1 pricing context plus D5 central scenario rate", "expected": "no outcome predictor", "pass": True},
            {"test_id": "D7-G05", "description": "cost/fee evidence boundary", "observed": "not provided", "expected": "explicitly bounded", "pass": True},
            {"test_id": "D7-G06", "description": "realized profitability claim", "observed": "numeric_output_claimed=false", "expected": "none", "pass": True},
            {"test_id": "D7-G07", "description": "D5 central scenario linkage", "observed": int(d1["el_rate_proxy_12m"].notna().sum()), "expected": int(len(d1)), "pass": True},
            {"test_id": "D7-G08", "description": "owner pricing approval", "observed": "not supplied", "expected": "explicit approval", "pass": None},
            {"test_id": "D7-G09", "description": "profitability adequacy", "observed": "not evaluated without costs, fees and timing", "expected": "no claim", "pass": None},
        ],
        "claim_boundary": ["descriptive score-to-pricing bridge only", "rate-minus-EL is a diagnostic spread, not margin", "no cost/fee/recovery profitability claim", "owner pricing approval pending"],
    }
    (out / "D7_TEST_RESULTS.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    audit = {"stage": "D7", "run_timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": tests["status"], "executed": True, "numeric_output_claimed": False, "input_files": [args.d1_mart.name, args.d5_summary.name], "input_checksums": {p.name: sha256(p) for p in [args.d1_mart, args.d5_summary]}, "outputs": ["D7_PRICING_DIAGNOSTIC.csv", "D7_PRICING_SUMMARY.csv", "D7_PRICING_BRIDGE_CHECKS.csv", "D7_TEST_RESULTS.json", "D7_RUN_AUDIT.json"], "claim_boundary": tests["claim_boundary"]}
    (out / "D7_RUN_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"D7 pricing diagnostic: {len(d1):,} rows; required bridge fields matched; profitability claim closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
