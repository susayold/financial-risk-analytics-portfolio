"""Deterministic review-scope QA for the complete Block D evidence surface."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
OUT = BLOCK / "BLOCK_D_FULL_REVIEW_QA.json"


def load(rel: str) -> dict:
    return json.loads((BLOCK / rel).read_text(encoding="utf-8"))


checks: list[dict] = []


def check(check_id: str, observed, expected, passed: bool, evidence: str) -> None:
    checks.append(
        {
            "check_id": check_id,
            "observed": observed,
            "expected": expected,
            "pass": bool(passed),
            "evidence": evidence,
        }
    )


d0 = load("D0_GOVERNANCE_CONTRACT/D0_TEST_RESULTS.json")
d1 = load("D1_RISK_SCORE_MART/D1_RUN_AUDIT.json")
d1_tests = load("D1_RISK_SCORE_MART/D1_TEST_RESULTS.json")
d2 = load("D2_LOSS_RECOVERY_EVIDENCE/D2_GOVERNED_CORE_BRIDGE_AUDIT.json")
d2_tests = load("D2_LOSS_RECOVERY_EVIDENCE/D2_TEST_RESULTS.json")
d4 = load("D4_LGD_FRAMEWORK/D4_RUN_AUDIT.json")
d4_tests = load("D4_LGD_FRAMEWORK/D4_TEST_RESULTS.json")

check("D0_STATUS", d0.get("status"), "PASS", d0.get("status") == "PASS", "D0_TEST_RESULTS.json")
check("D0_TEST_COUNT", [d0.get("tests_passed"), d0.get("tests_failed")], [10, 0], d0.get("tests_passed") == 10 and d0.get("tests_failed") == 0, "D0_TEST_RESULTS.json")
check("D1_STATUS", d1.get("status"), "PASS_WITH_LIMITATIONS", d1.get("status") == "PASS_WITH_LIMITATIONS", "D1_RUN_AUDIT.json")
check("D1_SCORE_ROWS", d1.get("row_counts", {}).get("d1_mart"), 310066, d1.get("row_counts", {}).get("d1_mart") == 310066, "D1_RUN_AUDIT.json")
check("D1_TEST_COUNT", [d1_tests.get("tests_passed"), d1_tests.get("tests_failed"), d1_tests.get("tests_pending")], [10, 0, 0], d1_tests.get("tests_passed") == 10 and d1_tests.get("tests_failed") == 0 and d1_tests.get("tests_pending") == 0, "D1_TEST_RESULTS.json")
check("D2_STATUS", d2.get("status"), "PASS_WITH_LIMITATIONS", d2.get("status") == "PASS_WITH_LIMITATIONS", "D2_GOVERNED_CORE_BRIDGE_AUDIT.json")
check("D2_GOVERNED_ID_BRIDGE", d2.get("row_counts", {}).get("matched_governed_ids"), 1347681, d2.get("row_counts", {}).get("matched_governed_ids") == 1347681 and d2.get("row_counts", {}).get("governed_core_rows") == 1347681, "D2_GOVERNED_CORE_BRIDGE_AUDIT.json")
d2_checks = {item.get("check_id"): item for item in d2.get("checks", [])}
check("D2_TARGET_AMOUNT_CONCORDANCE", [d2_checks.get("D2-B04", {}).get("status"), d2_checks.get("D2-B05", {}).get("status")], ["PASS", "PASS"], d2_checks.get("D2-B04", {}).get("status") == "PASS" and d2_checks.get("D2-B05", {}).get("status") == "PASS", "D2_GOVERNED_CORE_BRIDGE_AUDIT.json")
check("D2_TEST_COUNT", [d2_tests.get("tests_passed"), d2_tests.get("tests_failed"), d2_tests.get("tests_pending")], [10, 0, 0], d2_tests.get("tests_passed") == 10 and d2_tests.get("tests_failed") == 0 and d2_tests.get("tests_pending") == 0, "D2_TEST_RESULTS.json")
check("D4_STATUS", d4.get("status"), "BRIDGE_RECONCILED_APPROVAL_PENDING", d4.get("status") == "BRIDGE_RECONCILED_APPROVAL_PENDING", "D4_RUN_AUDIT.json")
check("D4_COUNTS", [d4.get("row_counts", {}).get("usable_lgd_rows"), d4.get("tests_passed"), d4.get("tests_failed"), d4.get("tests_pending")], [269249, 10, 0, 0], d4.get("row_counts", {}).get("usable_lgd_rows") == 269249 and d4.get("tests_passed") == 10 and d4.get("tests_failed") == 0 and d4.get("tests_pending") == 0, "D4_RUN_AUDIT.json")
check("D4_TEST_COUNT", [d4_tests.get("tests_passed"), d4_tests.get("tests_failed"), d4_tests.get("tests_pending")], [10, 0, 0], d4_tests.get("tests_passed") == 10 and d4_tests.get("tests_failed") == 0 and d4_tests.get("tests_pending") == 0, "D4_TEST_RESULTS.json")
d4_g09 = next((item for item in d4_tests.get("tests", []) if item.get("test_id") == "D4-G09"), {})
check("D4_SCORE_LOSS_LINKAGE", d4_g09.get("observed"), "49,049/49,049 current scored-BAD rows matched", d4_g09.get("pass") is True and "49,049/49,049" in d4_g09.get("observed", ""), "D4_TEST_RESULTS.json")

downstream = {
    "D5": "D5_EXPECTED_LOSS/D5_GATE_RESULTS.json",
    "D6": "D6_DECISION_POLICY/D6_GATE_RESULTS.json",
    "D7": "D7_PRICING/D7_GATE_RESULTS.json",
    "D8": "D8_STRESS/D8_GATE_RESULTS.json",
    "D9": "D9_CLOSURE/D9_GATE_RESULTS.json",
}
audit_paths = {
    "D5": "D5_EXPECTED_LOSS/D5_ANALYTICAL_SCENARIO_AUDIT.json",
    "D6": "D6_DECISION_POLICY/D6_ANALYTICAL_PACK_AUDIT.json",
    "D7": "D7_PRICING/D7_DIAGNOSTIC_AUDIT.json",
    "D8": "D8_STRESS/D8_ILLUSTRATIVE_SENSITIVITY_AUDIT.json",
    "D9": "D9_CLOSURE/D9_CLOSURE_REVIEW_MANIFEST.json",
}
for stage, rel in downstream.items():
    item = load(rel)
    check(f"{stage}_GATE_STATUS", item.get("status"), "CONTROLLED_HOLD", item.get("status") == "CONTROLLED_HOLD", rel)
    check(f"{stage}_NO_NUMERIC_CLAIM", item.get("numeric_output_claimed"), False, item.get("numeric_output_claimed") is False, rel)
    audit = load(audit_paths[stage])
    check(f"{stage}_REVIEW_PACK_EXECUTED", audit.get("executed"), True, audit.get("executed") is True, audit_paths[stage])

d1_contract = (BLOCK / "D1_RISK_SCORE_MART/D1_MART_CONTRACT.md").read_text(encoding="utf-8")
d1_availability = (BLOCK / "D1_RISK_SCORE_MART/D1_INPUT_AVAILABILITY_AUDIT.md").read_text(encoding="utf-8")
check("D1_CONTRACT_NOT_STALE", "SCORE_ARTIFACT_NOT_MATERIALIZED" in d1_contract, False, "SCORE_ARTIFACT_NOT_MATERIALIZED" not in d1_contract, "D1_MART_CONTRACT.md")
check("D1_AVAILABILITY_UPDATED", "310,066-row matched scored mart" in d1_availability, True, "310,066-row matched scored mart" in d1_availability, "D1_INPUT_AVAILABILITY_AUDIT.md")

passed = sum(1 for item in checks if item["pass"])
failed = len(checks) - passed
result = {
    "run_name": "block_d_full_review_qa",
    "run_date": "2026-09-02",
    "scope": "controlled analytical review; no production or regulatory claim",
    "status": "PASS" if failed == 0 else "FAIL",
    "checks_passed": passed,
    "checks_failed": failed,
    "checks": checks,
    "overall_block_status": "NOT_LOCKED_REVIEW_REQUIRED",
    "open_inputs": [
        "D4 main-case LGD and timing approval",
        "D5 analytical proxy acceptance",
        "D6 thresholds and overrides approval",
        "D7 cost/fee assumptions if profitability is required",
        "D8 baseline and shock policy",
        "data/model/risk owner sign-off",
    ],
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(f"BLOCK D FULL REVIEW QA {result['status']} — {passed}/{len(checks)} checks pass")
