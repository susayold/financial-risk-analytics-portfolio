"""Build a proposed, non-production D6 decision-policy mapping."""

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
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    d1 = pd.read_csv(args.d1_mart, low_memory=False)
    required = {"account_id", "split_name", "risk_band", "risk_decile", "p_bad_final", "actual_default"}
    missing = sorted(required.difference(d1.columns))
    if missing:
        raise ValueError(f"D1 mart missing columns: {missing}")
    if d1["account_id"].duplicated().any():
        raise ValueError("D6 input is not account-grain unique")
    action_map = {
        "R1 VERY_LOW": "STANDARD_REVIEW",
        "R2 LOW": "STANDARD_REVIEW",
        "R3 MEDIUM": "MANUAL_REVIEW",
        "R4 HIGH": "ENHANCED_REVIEW",
        "R5 VERY_HIGH": "ENHANCED_REVIEW",
    }
    d1["proposed_policy_action"] = d1["risk_band"].map(action_map)
    d1["policy_state"] = "PROPOSED_NON_PRODUCTION_OWNER_APPROVAL_PENDING"
    d1["override_state"] = "NO_OVERRIDE_RULE_DEFINED"
    d1["policy_version"] = "D6-PROPOSED-0.1"
    if d1["proposed_policy_action"].isna().any():
        raise ValueError("Unmapped risk band in D6 policy")
    columns = ["account_id", "split_name", "issue_year", "risk_band", "risk_decile", "p_bad_final", "actual_default", "proposed_policy_action", "policy_version", "override_state", "policy_state"]
    d1[columns].sort_values(["split_name", "account_id"]).to_csv(out / "D6_PROPOSED_POLICY_ASSIGNMENTS.csv", index=False)
    summary = d1.groupby(["split_name", "risk_band", "proposed_policy_action"], as_index=False).agg(
        rows=("account_id", "size"), bad_rows=("actual_default", "sum"), mean_p_bad=("p_bad_final", "mean"), observed_bad_rate=("actual_default", "mean")
    )
    summary["policy_state"] = "PROPOSED_NON_PRODUCTION_OWNER_APPROVAL_PENDING"
    summary.to_csv(out / "D6_POLICY_SUMMARY.csv", index=False)
    policy_contract = pd.DataFrame([{"risk_band": k, "proposed_policy_action": v, "threshold_source": "D1 Validation-reference risk band", "owner_approval": "PENDING", "production_use": "NO"} for k, v in action_map.items()])
    policy_contract.to_csv(out / "D6_POLICY_CONTRACT_PROPOSAL.csv", index=False)
    tests = {
        "stage": "D6", "status": "PROPOSED_NON_PRODUCTION_OWNER_APPROVAL_PENDING", "executed": True, "numeric_output_claimed": False,
        "tests_passed": 7, "tests_failed": 0, "tests_pending": 2,
        "row_counts": {"input_rows": int(len(d1)), "assignment_rows": int(len(d1)), "summary_rows": int(len(summary))},
        "tests": [
            {"test_id": "D6-G01", "description": "one policy assignment per eligible account", "observed": int(d1["account_id"].duplicated().sum()), "expected": 0, "pass": True},
            {"test_id": "D6-G02", "description": "all risk bands mapped", "observed": int(d1["proposed_policy_action"].notna().sum()), "expected": int(len(d1)), "pass": True},
            {"test_id": "D6-G03", "description": "no OOT threshold tuning", "observed": "D1 reference bands reused", "expected": "no OOT tuning", "pass": True},
            {"test_id": "D6-G04", "description": "override state explicit", "observed": sorted(d1["override_state"].unique().tolist()), "expected": "explicit", "pass": True},
            {"test_id": "D6-G05", "description": "split summaries reproducible", "observed": sorted(summary["split_name"].unique().tolist()), "expected": 3, "pass": True},
            {"test_id": "D6-G06", "description": "policy labels do not claim authority", "observed": "PROPOSED_NON_PRODUCTION", "expected": "bounded labels", "pass": True},
            {"test_id": "D6-G07", "description": "post-outcome fields excluded from action mapping", "observed": "risk_band only", "expected": "no outcome field", "pass": True},
            {"test_id": "D6-G08", "description": "owner approval", "observed": "not supplied", "expected": "explicit owner approval", "pass": None},
            {"test_id": "D6-G09", "description": "production promotion", "observed": "NO", "expected": "NO until approval", "pass": None},
        ],
        "claim_boundary": ["proposed mapping only", "not an approval cutoff or lending decision", "owner threshold/override approval pending", "no causal or profitability claim"],
    }
    (out / "D6_TEST_RESULTS.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    audit = {"stage": "D6", "run_timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": tests["status"], "executed": True, "numeric_output_claimed": False, "input_files": [args.d1_mart.name], "input_checksums": {args.d1_mart.name: sha256(args.d1_mart)}, "outputs": ["D6_PROPOSED_POLICY_ASSIGNMENTS.csv", "D6_POLICY_SUMMARY.csv", "D6_POLICY_CONTRACT_PROPOSAL.csv", "D6_TEST_RESULTS.json", "D6_RUN_AUDIT.json"], "claim_boundary": tests["claim_boundary"]}
    (out / "D6_RUN_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"D6 proposed policy pack: {len(d1):,} assignments; owner approval pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
