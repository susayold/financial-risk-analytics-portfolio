"""Validate the structured Block D owner-decision register.

The register is intentionally allowed to remain pending. This validator
separates a structurally valid pending register from a register that is ready
to unlock D9, and never invents an approval.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER = ROOT / "block-d" / "D9_CLOSURE" / "D9_APPROVAL_REGISTER.json"
DEFAULT_OUTPUT = ROOT / "block-d" / "D9_CLOSURE" / "D9_APPROVAL_VALIDATION.json"

DECISION_KEYS = (
    "D4_main_case_lgd",
    "D4_timing_boundary",
    "D5_analytical_proxy",
    "D6_action_policy",
    "D7_pricing_scope",
    "D8_stress_policy",
)
DECISION_STATUSES = {"PENDING", "APPROVED"}
SIGNOFF_ROLES = ("data_owner", "model_owner", "risk_owner")
LGD_OPTIONS = {"Q25", "Q50", "Q75", "Q90"}
PRICING_OPTIONS = {
    "DESCRIPTIVE_ONLY",
    "PROVIDE_APPROVED_COST_FEE_TIMING_INPUTS_FOR_ADEQUACY_ANALYSIS",
}


def validate_register(register: dict) -> dict:
    errors: list[str] = []
    pending: list[str] = []

    # The final portfolio closure is intentionally separate from an
    # institutional approval workflow.  A portfolio project may record the
    # analytical decisions and the role that owns them without fabricating a
    # bank data/model/risk owner or a production approval.
    governance_mode = register.get("governance_mode")
    if governance_mode is not None:
        if governance_mode not in {"PORTFOLIO_PROJECT_REVIEW", "INSTITUTIONAL_PRODUCTION"}:
            return {
                "run_name": "block_d_owner_decision_validation",
                "run_date": date.today().isoformat(),
                "scope": "D9 governance-mode validation; no approval is inferred",
                "validation_status": "INVALID",
                "schema_valid": False,
                "ready_for_d9_rerun": False,
                "governance_mode": governance_mode,
                "errors": ["governance_mode must be PORTFOLIO_PROJECT_REVIEW or INSTITUTIONAL_PRODUCTION"],
            }
        if governance_mode == "PORTFOLIO_PROJECT_REVIEW":
            return _validate_portfolio_register(register)
        return _validate_institutional_register(register)

    if register.get("stage") != "D9":
        errors.append("stage must be D9")
    if register.get("status") not in {"PENDING_OWNER_INPUT", "READY_FOR_D9_RERUN"}:
        errors.append("status must be PENDING_OWNER_INPUT or READY_FOR_D9_RERUN")
    if not isinstance(register.get("decisions"), dict):
        errors.append("decisions must be an object")
        decisions: dict = {}
    else:
        decisions = register["decisions"]

    if set(decisions) != set(DECISION_KEYS):
        errors.append("decisions must contain exactly the six required D4-D8 decision keys")

    def decision_status(key: str) -> str | None:
        item = decisions.get(key)
        if not isinstance(item, dict):
            errors.append(f"{key} must be an object")
            return None
        for field in ("decision_owner", "decision_date", "decision_reference", "conditions"):
            if field not in item:
                errors.append(f"{key}.{field} is required; use null while pending")
        status = item.get("status")
        if status not in DECISION_STATUSES:
            errors.append(f"{key}.status must be PENDING or APPROVED")
            return status
        if status == "PENDING":
            pending.append(key)
        if status == "APPROVED" and not all(
            item.get(field) for field in ("decision_owner", "decision_date", "decision_reference")
        ):
            errors.append(f"approved {key} requires decision_owner, decision_date and decision_reference")
        return status

    statuses = {key: decision_status(key) for key in DECISION_KEYS}

    d4_lgd = decisions.get("D4_main_case_lgd", {})
    selected_lgd = d4_lgd.get("selected_option") if isinstance(d4_lgd, dict) else None
    if selected_lgd is not None and selected_lgd not in LGD_OPTIONS:
        errors.append("D4_main_case_lgd.selected_option must be Q25, Q50, Q75 or Q90")
    if statuses.get("D4_main_case_lgd") == "APPROVED" and selected_lgd not in LGD_OPTIONS:
        errors.append("approved D4_main_case_lgd requires selected_option")

    d4_timing = decisions.get("D4_timing_boundary", {})
    if isinstance(d4_timing, dict):
        approved = d4_timing.get("approved")
        if approved is not None and not isinstance(approved, bool):
            errors.append("D4_timing_boundary.approved must be boolean or null")
        if statuses.get("D4_timing_boundary") == "APPROVED" and approved is not True:
            errors.append("approved D4_timing_boundary requires approved=true")

    d5 = decisions.get("D5_analytical_proxy", {})
    if isinstance(d5, dict):
        approved = d5.get("approved")
        if approved is not None and not isinstance(approved, bool):
            errors.append("D5_analytical_proxy.approved must be boolean or null")
        if statuses.get("D5_analytical_proxy") == "APPROVED" and approved is not True:
            errors.append("approved D5_analytical_proxy requires approved=true")

    d6 = decisions.get("D6_action_policy", {})
    if isinstance(d6, dict):
        for field in ("thresholds_approved", "overrides_approved"):
            value = d6.get(field)
            if value is not None and not isinstance(value, bool):
                errors.append(f"D6_action_policy.{field} must be boolean or null")
        if statuses.get("D6_action_policy") == "APPROVED" and not all(
            d6.get(field) is True for field in ("thresholds_approved", "overrides_approved")
        ):
            errors.append("approved D6_action_policy requires thresholds_approved=true and overrides_approved=true")

    d7 = decisions.get("D7_pricing_scope", {})
    selected_pricing = d7.get("selected_option") if isinstance(d7, dict) else None
    if selected_pricing is not None and selected_pricing not in PRICING_OPTIONS:
        errors.append("D7_pricing_scope.selected_option is not an allowed option")
    if statuses.get("D7_pricing_scope") == "APPROVED" and selected_pricing not in PRICING_OPTIONS:
        errors.append("approved D7_pricing_scope requires selected_option")

    d8 = decisions.get("D8_stress_policy", {})
    if isinstance(d8, dict):
        approved = d8.get("approved")
        if approved is not None and not isinstance(approved, bool):
            errors.append("D8_stress_policy.approved must be boolean or null")
        if statuses.get("D8_stress_policy") == "APPROVED" and approved is not True:
            errors.append("approved D8_stress_policy requires approved=true")

    signoffs = register.get("owner_signoff")
    if not isinstance(signoffs, dict) or set(signoffs) != set(SIGNOFF_ROLES):
        errors.append("owner_signoff must contain data_owner, model_owner and risk_owner")
        signoffs = {}

    signoff_statuses: dict[str, str | None] = {}
    for role in SIGNOFF_ROLES:
        item = signoffs.get(role)
        if not isinstance(item, dict):
            errors.append(f"{role} sign-off must be an object")
            signoff_statuses[role] = None
            continue
        status = item.get("status")
        signoff_statuses[role] = status
        if status not in DECISION_STATUSES:
            errors.append(f"{role}.status must be PENDING or APPROVED")
        if status == "PENDING":
            pending.append(role)
        if status == "APPROVED" and not all(item.get(field) for field in ("name", "date", "reference")):
            errors.append(f"approved {role} requires name, date and reference")

    all_decisions_approved = all(statuses.get(key) == "APPROVED" for key in DECISION_KEYS)
    all_signoffs_approved = all(signoff_statuses.get(role) == "APPROVED" for role in SIGNOFF_ROLES)
    ready = not errors and all_decisions_approved and all_signoffs_approved
    if ready and register.get("status") != "READY_FOR_D9_RERUN":
        errors.append("fully approved register must set status=READY_FOR_D9_RERUN")
        ready = False

    schema_valid = not errors
    if schema_valid and not ready and not pending:
        pending.append("approval status transition")

    return {
        "run_name": "block_d_owner_decision_validation",
        "run_date": date.today().isoformat(),
        "scope": "D9 owner-input validation; no approval is inferred",
        "validation_status": "INVALID" if not schema_valid else ("READY_FOR_D9_RERUN" if ready else "VALID_PENDING"),
        "schema_valid": schema_valid,
        "ready_for_d9_rerun": ready,
        "decision_statuses": statuses,
        "owner_signoff_statuses": signoff_statuses,
        "pending_items": pending,
        "errors": errors,
        "unlock_rule": "All six decisions and all three owner sign-offs must be APPROVED before D9 rerun.",
    }


def _validate_portfolio_register(register: dict) -> dict:
    errors: list[str] = []
    decisions = register.get("decisions")
    if register.get("stage") != "D9":
        errors.append("stage must be D9")
    if register.get("production_authorized") is not False:
        errors.append("portfolio mode requires production_authorized=false")
    if register.get("regulatory_compliance_claimed") is not False:
        errors.append("portfolio mode requires regulatory_compliance_claimed=false")
    if not isinstance(decisions, dict) or set(decisions) != set(DECISION_KEYS):
        errors.append("portfolio decisions must contain exactly the six required D4-D8 decision keys")
        decisions = {}
    decision_statuses = {}
    for key in DECISION_KEYS:
        item = decisions.get(key)
        if not isinstance(item, dict):
            errors.append(f"{key} must be an object")
            continue
        decision_statuses[key] = item.get("status")
        if item.get("status") not in {"COMPLETED_BY_PORTFOLIO_PROJECT_REVIEW", "FORMALLY_STOPPED_BY_PREDECLARED_STOP_CONDITION"}:
            errors.append(f"{key}.status must be a portfolio completion or declared stop status")
        if item.get("decision_owner") != "PORTFOLIO_PROJECT_OWNER":
            errors.append(f"{key}.decision_owner must be PORTFOLIO_PROJECT_OWNER")
        if not item.get("decision_reference"):
            errors.append(f"{key}.decision_reference is required")
        if "conditions" not in item:
            errors.append(f"{key}.conditions is required")
        if item.get("production_authorization") is not False:
            errors.append(f"{key}.production_authorization must be false")
        if item.get("regulatory_claim") not in {False, "NONE", "NOT_CLAIMED"}:
            errors.append(f"{key}.regulatory_claim must be false/none")
    signoffs = register.get("owner_signoff")
    signoff_statuses = {}
    if not isinstance(signoffs, dict) or set(signoffs) != set(SIGNOFF_ROLES):
        errors.append("owner_signoff must contain data_owner, model_owner and risk_owner")
        signoffs = {}
    for role in SIGNOFF_ROLES:
        item = signoffs.get(role)
        if not isinstance(item, dict) or item.get("status") != "NOT_APPLICABLE_PORTFOLIO_PROJECT":
            errors.append(f"{role} must be NOT_APPLICABLE_PORTFOLIO_PROJECT in portfolio mode")
            signoff_statuses[role] = None
        else:
            signoff_statuses[role] = item.get("status")
    valid = not errors
    return {
        "run_name": "block_d_owner_decision_validation",
        "run_date": date.today().isoformat(),
        "scope": "D9 portfolio project review; institutional production authorization is out of scope",
        "governance_mode": "PORTFOLIO_PROJECT_REVIEW",
        "validation_status": "PORTFOLIO_VALID" if valid else "INVALID",
        "schema_valid": valid,
        "ready_for_d9_rerun": valid,
        "decision_statuses": decision_statuses,
        "owner_signoff_statuses": signoff_statuses,
        "pending_items": [],
        "errors": errors,
        "production_authorized": False,
        "regulatory_compliance_claimed": False,
        "unlock_rule": "Six portfolio project-owner analytical decisions complete; institutional signoffs are not applicable; no production authorization is inferred.",
    }


def _validate_institutional_register(register: dict) -> dict:
    """Validate the explicit institutional-mode shape without auto-approving it."""
    errors: list[str] = []
    owners = register.get("institutional_owners")
    if not isinstance(owners, dict):
        errors.append("institutional_owners is required in INSTITUTIONAL_PRODUCTION mode")
        owners = {}
    for role in SIGNOFF_ROLES:
        item = owners.get(role)
        if not isinstance(item, dict) or not all(item.get(x) for x in ("name", "date", "reference")):
            errors.append(f"institutional_owners.{role} requires name, date and reference")
    return {
        "run_name": "block_d_owner_decision_validation",
        "run_date": date.today().isoformat(),
        "scope": "D9 institutional production validation; no approval is inferred",
        "governance_mode": "INSTITUTIONAL_PRODUCTION",
        "validation_status": "INSTITUTIONAL_VALID" if not errors else "INVALID",
        "schema_valid": not errors,
        "ready_for_d9_rerun": False,
        "errors": errors,
        "production_authorized": register.get("production_authorized"),
        "regulatory_compliance_claimed": register.get("regulatory_compliance_claimed"),
    }


def run_validator_self_tests(register: dict | None = None) -> dict:
    """Exercise pending, malformed and fully-approved register paths."""

    if register is None:
        register = json.loads(DEFAULT_REGISTER.read_text(encoding="utf-8"))
    if register.get("governance_mode") == "PORTFOLIO_PROJECT_REVIEW":
        from test_block_d_portfolio_governance import run as run_portfolio_tests
        portfolio_results = run_portfolio_tests()
        passed = sum(1 for result in portfolio_results if result["pass"])
        return {"tests_run": len(portfolio_results), "tests_passed": passed, "tests_failed": len(portfolio_results) - passed, "tests": portfolio_results}
    results: list[dict] = []

    pending = validate_register(register)
    results.append(
        {
            "name": "pending_register_is_valid_but_not_ready",
            "pass": pending["validation_status"] == "VALID_PENDING"
            and pending["schema_valid"] is True
            and pending["ready_for_d9_rerun"] is False,
        }
    )

    malformed_register = deepcopy(register)
    malformed_register["decisions"]["D4_main_case_lgd"]["status"] = "APPROVED"
    malformed = validate_register(malformed_register)
    results.append(
        {
            "name": "approved_lgd_without_selection_is_rejected",
            "pass": malformed["validation_status"] == "INVALID"
            and malformed["schema_valid"] is False,
        }
    )

    ready_register = deepcopy(register)
    ready_register["status"] = "READY_FOR_D9_RERUN"
    for key in DECISION_KEYS:
        ready_register["decisions"][key].update(
            decision_owner="Test owner", decision_date="2026-09-03", decision_reference=f"TEST-{key}", conditions=None
        )
    ready_register["decisions"]["D4_main_case_lgd"].update(status="APPROVED", selected_option="Q50")
    ready_register["decisions"]["D4_timing_boundary"].update(status="APPROVED", approved=True)
    ready_register["decisions"]["D5_analytical_proxy"].update(status="APPROVED", approved=True)
    ready_register["decisions"]["D6_action_policy"].update(
        status="APPROVED", thresholds_approved=True, overrides_approved=True
    )
    ready_register["decisions"]["D7_pricing_scope"].update(status="APPROVED", selected_option="DESCRIPTIVE_ONLY")
    ready_register["decisions"]["D8_stress_policy"].update(status="APPROVED", approved=True)
    for role, item in ready_register["owner_signoff"].items():
        item.update(status="APPROVED", name=f"Test {role}", date="2026-09-03", reference=f"TEST-{role}")
    ready = validate_register(ready_register)
    results.append(
        {
            "name": "complete_register_is_ready_for_d9_rerun",
            "pass": ready["validation_status"] == "READY_FOR_D9_RERUN"
            and ready["schema_valid"] is True
            and ready["ready_for_d9_rerun"] is True,
        }
    )

    passed = sum(1 for result in results if result["pass"])
    return {"tests_run": len(results), "tests_passed": passed, "tests_failed": len(results) - passed, "tests": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = run_validator_self_tests()
        print(f"OWNER DECISION VALIDATOR SELF-TEST {result['tests_passed']}/{result['tests_run']} pass")
        for test in result["tests"]:
            print(f"{'PASS' if test['pass'] else 'FAIL'}: {test['name']}")
        return 0 if result["tests_failed"] == 0 else 1

    register = json.loads(args.register.read_text(encoding="utf-8"))
    result = validate_register(register)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"OWNER DECISION VALIDATION {result['validation_status']} — "
        f"schema_valid={result['schema_valid']} ready_for_d9_rerun={result['ready_for_d9_rerun']}"
    )
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}")
    if args.require_ready and not result["ready_for_d9_rerun"]:
        return 1
    return 0 if result["schema_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
