"""Final deterministic QA for the Block D portfolio closure plan."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from validate_block_d_owner_decisions import validate_register, run_validator_self_tests


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
OUT = BLOCK / "BLOCK_D_FULL_REVIEW_QA.json"
checks: list[dict] = []


def add(cid: str, passed: bool, observed, expected, evidence: str) -> None:
    checks.append({"check_id": cid, "pass": bool(passed), "observed": observed, "expected": expected, "evidence": evidence})


def load(path: str):
    return json.loads((BLOCK / path).read_text(encoding="utf-8"))


def main() -> int:
    d0 = load("D0_GOVERNANCE_CONTRACT/D0_TEST_RESULTS.json")
    add("D0-G01", d0.get("status") == "PASS", d0.get("status"), "PASS", "D0_TEST_RESULTS.json")
    add("D0-G02", d0.get("tests_failed") == 0, d0.get("tests_failed"), 0, "D0_TEST_RESULTS.json")
    for stage, rel, expected in [("D1", "D1_RISK_SCORE_MART/D1_RUN_AUDIT.json", "PASS_WITH_LIMITATIONS"), ("D2", "D2_LOSS_RECOVERY_EVIDENCE/D2_GOVERNED_CORE_BRIDGE_AUDIT.json", "PASS_WITH_LIMITATIONS"), ("D3", "D3_EAD_FRAMEWORK/D3_CONTRACT_AUDIT.json", "PASS_WITH_LIMITATIONS")]:
        payload = load(rel); add(f"{stage}-STATUS", payload.get("status") == expected, payload.get("status"), expected, rel)
    d4 = load("D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_DECISION.json")
    d4_final = load("D4_FINAL_TEST_RESULTS.json")
    add("D4-G01", d4.get("status") == "PASS_WITH_LIMITATIONS", d4.get("status"), "PASS_WITH_LIMITATIONS", "D4_EMPIRICAL_LGD_DECISION.json")
    add("D4-G02", d4.get("decision") in {"REJECT_ML_CHALLENGER_KEEP_SCENARIO_LGD", "PROMOTE_EMPIRICAL_LGD_CHALLENGER"}, d4.get("decision"), "declared challenger decision", "D4_EMPIRICAL_LGD_DECISION.json")
    add("D4-G03", d4_final.get("tests_failed") == 0 and d4_final.get("tests_passed") == 10, [d4_final.get("tests_passed"), d4_final.get("tests_failed")], [10, 0], "D4_FINAL_TEST_RESULTS.json")
    add("D4-G04", load("D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_LEAKAGE_AUDIT.json").get("matches_in_X") == [], load("D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_LEAKAGE_AUDIT.json").get("matches_in_X"), [], "D4_EMPIRICAL_LGD_LEAKAGE_AUDIT.json")
    d5 = load("D5_EXPECTED_LOSS/D5_EL_RECONCILIATION.json"); d5t = load("D5_EXPECTED_LOSS/D5_FINAL_TEST_RESULTS.json")
    add("D5-G01", d5.get("status") == "PASS_WITH_LIMITATIONS", d5.get("status"), "PASS_WITH_LIMITATIONS", "D5_EL_RECONCILIATION.json")
    add("D5-G02", d5.get("tests_failed") == 0 and all(x.get("pass") for x in d5.get("checks", [])), [d5.get("tests_failed"), len(d5.get("checks", []))], "0 failures and all reconciliations pass", "D5_EL_RECONCILIATION.json")
    add("D5-G03", d5t.get("tests_passed") == 10 and d5t.get("tests_failed") == 0, [d5t.get("tests_passed"), d5t.get("tests_failed")], [10, 0], "D5_FINAL_TEST_RESULTS.json")
    d6 = load("D6_DECISION_POLICY/D6_POLICY_DECISION.json"); d6t = load("D6_DECISION_POLICY/D6_FINAL_TEST_RESULTS.json")
    add("D6-G01", d6.get("status") == "PASS_WITH_LIMITATIONS", d6.get("status"), "PASS_WITH_LIMITATIONS", "D6_POLICY_DECISION.json")
    add("D6-G02", d6.get("thresholds_retuned_after_replay") is False, d6.get("thresholds_retuned_after_replay"), False, "D6_POLICY_DECISION.json")
    add("D6-G03", d6t.get("tests_passed") == 12 and d6t.get("tests_failed") == 0, [d6t.get("tests_passed"), d6t.get("tests_failed")], [12, 0], "D6_FINAL_TEST_RESULTS.json")
    d7 = load("D7_PRICING/D7_SCOPE_DECISION.json"); d7t = load("D7_PRICING/D7_FINAL_TEST_RESULTS.json")
    add("D7-G01", d7.get("selected_scope") == "DESCRIPTIVE_ONLY", d7.get("selected_scope"), "DESCRIPTIVE_ONLY", "D7_SCOPE_DECISION.json")
    add("D7-G02", d7t.get("tests_passed") == 8 and d7t.get("tests_failed") == 0, [d7t.get("tests_passed"), d7t.get("tests_failed")], [8, 0], "D7_FINAL_TEST_RESULTS.json")
    d8 = load("D8_STRESS/D8_FINAL_DECISION.json"); d8t = load("D8_STRESS/D8_FINAL_TEST_RESULTS.json")
    add("D8-G01", d8.get("status") == "PASS_WITH_LIMITATIONS", d8.get("status"), "PASS_WITH_LIMITATIONS", "D8_FINAL_DECISION.json")
    add("D8-G02", d8.get("policy_thresholds_unchanged") is True, d8.get("policy_thresholds_unchanged"), True, "D8_FINAL_DECISION.json")
    add("D8-G03", d8t.get("tests_passed") == 12 and d8t.get("tests_failed") == 0, [d8t.get("tests_passed"), d8t.get("tests_failed")], [12, 0], "D8_FINAL_TEST_RESULTS.json")
    reg = load("D9_CLOSURE/D9_APPROVAL_REGISTER.json"); validation = validate_register(reg)
    add("S7-G01", reg.get("governance_mode") == "PORTFOLIO_PROJECT_REVIEW", reg.get("governance_mode"), "PORTFOLIO_PROJECT_REVIEW", "D9_APPROVAL_REGISTER.json")
    add("S7-G02", validation.get("validation_status") == "PORTFOLIO_VALID", validation.get("validation_status"), "PORTFOLIO_VALID", "D9_APPROVAL_VALIDATION.json")
    add("S7-G03", reg.get("production_authorized") is False, reg.get("production_authorized"), False, "D9_APPROVAL_REGISTER.json")
    add("S7-G04", reg.get("regulatory_compliance_claimed") is False, reg.get("regulatory_compliance_claimed"), False, "D9_APPROVAL_REGISTER.json")
    add("S7-G05", all(x.get("status") == "NOT_APPLICABLE_PORTFOLIO_PROJECT" for x in reg.get("owner_signoff", {}).values()), reg.get("owner_signoff"), "institutional signoffs N/A", "D9_APPROVAL_REGISTER.json")
    tests = run_validator_self_tests(reg)
    add("S7-G06", tests.get("tests_failed") == 0, [tests.get("tests_passed"), tests.get("tests_failed")], "legacy validator regression pass", "test_block_d_owner_decisions.py")
    governance_tests = ROOT / "src/test_block_d_portfolio_governance.py"
    add("S7-G07", governance_tests.exists(), governance_tests.exists(), True, "test_block_d_portfolio_governance.py")
    final = load("D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json")
    final_manifest = load("D9_CLOSURE/D9_FINAL_CLOSURE_MANIFEST.json")
    add("S8-G01", final.get("status") == "CLOSED_WITH_LIMITATIONS_PORTFOLIO", final.get("status"), "CLOSED_WITH_LIMITATIONS_PORTFOLIO", "D9_FINAL_BLOCK_D_DECISION.json")
    add("S8-G02", final.get("portfolio_implementation_complete") is True, final.get("portfolio_implementation_complete"), True, "D9_FINAL_BLOCK_D_DECISION.json")
    add("S8-G03", final.get("production_authorized") is False and final.get("regulatory_compliance_claimed") is False, [final.get("production_authorized"), final.get("regulatory_compliance_claimed")], [False, False], "D9_FINAL_BLOCK_D_DECISION.json")
    add("S8-G04", final_manifest.get("status") == "CLOSED_WITH_LIMITATIONS_PORTFOLIO" and final_manifest.get("missing_required_entries") == [], [final_manifest.get("status"), final_manifest.get("missing_required_entries")], ["CLOSED_WITH_LIMITATIONS_PORTFOLIO", []], "D9_FINAL_CLOSURE_MANIFEST.json")
    add("S8-G05", load("D9_CLOSURE/D9_FINAL_TEST_RESULTS.json").get("tests_failed") == 0, load("D9_CLOSURE/D9_FINAL_TEST_RESULTS.json").get("tests_failed"), 0, "D9_FINAL_TEST_RESULTS.json")
    score = load("BLOCK_D_FINAL_SCORECARD.json")
    add("S9-G01", score.get("axes", {}).get("execution_coverage_pct") == 100.0, score.get("axes", {}).get("execution_coverage_pct"), 100.0, "BLOCK_D_FINAL_SCORECARD.json")
    add("S9-G02", score.get("axes", {}).get("portfolio_requirement_resolution_pct") == 100.0, score.get("axes", {}).get("portfolio_requirement_resolution_pct"), 100.0, "BLOCK_D_FINAL_SCORECARD.json")
    add("S9-G03", score.get("axes", {}).get("production_regulatory_readiness") == "NOT_IN_SCOPE", score.get("axes", {}).get("production_regulatory_readiness"), "NOT_IN_SCOPE", "BLOCK_D_FINAL_SCORECARD.json")
    add("S10-G01", load("D9_CLOSURE/D9_FINAL_CHECKSUM_VALIDATION.json").get("checks_failed") == 0, load("D9_CLOSURE/D9_FINAL_CHECKSUM_VALIDATION.json").get("checks_failed"), 0, "D9_FINAL_CHECKSUM_VALIDATION.json")
    passed = sum(x["pass"] for x in checks); failed = len(checks) - passed
    payload = {"run_name": "block_d_full_review_qa", "run_date": date.today().isoformat(), "scope": "final portfolio closure; no production or regulatory claim", "status": "PASS" if failed == 0 else "FAIL", "checks_passed": passed, "checks_failed": failed, "checks": checks, "overall_block_status": final.get("status"), "production_authorized": False, "regulatory_compliance_claimed": False}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"BLOCK D FULL REVIEW QA {payload['status']} — {passed}/{len(checks)} checks pass")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
