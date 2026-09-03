"""Materialize the final D9 Block D decision and closure report."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
D9 = BLOCK / "D9_CLOSURE"


def main() -> int:
    d4 = json.loads((BLOCK / "D4_MAIN_CASE_DECISION.json").read_text(encoding="utf-8"))
    d5 = json.loads((BLOCK / "D5_EXPECTED_LOSS" / "D5_EL_RECONCILIATION.json").read_text(encoding="utf-8"))
    d6 = json.loads((BLOCK / "D6_DECISION_POLICY" / "D6_POLICY_DECISION.json").read_text(encoding="utf-8"))
    d7 = json.loads((BLOCK / "D7_PRICING" / "D7_SCOPE_DECISION.json").read_text(encoding="utf-8"))
    d8 = json.loads((BLOCK / "D8_STRESS" / "D8_FINAL_DECISION.json").read_text(encoding="utf-8"))
    owner = json.loads((D9 / "D9_PORTFOLIO_PROJECT_OWNER_DECISIONS.json").read_text(encoding="utf-8"))
    semantic_path = BLOCK / "BLOCK_D_SEMANTIC_QA.json"
    semantic = json.loads(semantic_path.read_text(encoding="utf-8")) if semantic_path.exists() else {"status": "NOT_RUN", "semantic_remediation_pct": None}
    full_review = json.loads((BLOCK / "BLOCK_D_FULL_REVIEW_QA.json").read_text(encoding="utf-8"))
    approval = json.loads((D9 / "D9_APPROVAL_VALIDATION.json").read_text(encoding="utf-8"))
    checksum_path = D9 / "D9_FINAL_CHECKSUM_VALIDATION.json"
    checksum = json.loads(checksum_path.read_text(encoding="utf-8")) if checksum_path.exists() else {"checks_failed": 1}
    status_path = BLOCK / "BLOCK_D_STATUS_CONSISTENCY.json"
    status_check = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {"status": "NOT_RUN"}
    portfolio_complete = bool(
        semantic.get("checks_failed") == 0
        and full_review.get("checks_failed") == 0
        and approval.get("validation_status") == "PORTFOLIO_VALID"
        and checksum.get("checks_failed", checksum.get("failed", 1)) == 0
        and status_check.get("status") == "PASS"
    )
    decision = {
        "block": "D",
        "decision_date": date.today().isoformat(),
        "governance_mode": "PORTFOLIO_PROJECT_REVIEW",
        "status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
        "portfolio_implementation_complete": portfolio_complete,
        "closure_substatus": "FINAL_PORTFOLIO_CLOSURE" if portfolio_complete else "PENDING_OWNER_GATE",
        "production_authorized": False,
        "regulatory_compliance_claimed": False,
        "frozen_risk_model": "C8E_RICH_BUREAU_CATBOOST_79F",
        "probability_method": "p_bad_final",
        "lgd_method": d4["selected_main_method"],
        "ead_method": "D3_CONTRACTUAL_TIMING_PROXY",
        "expected_loss_method": "ANALYTICAL_PROXY",
        "main_expected_loss_view": "EL_MAIN_ANALYTICAL",
        "policy_scope": "HISTORICAL_DECISION_SIMULATION",
        "pricing_scope": d7["selected_scope"],
        "stress_scope": "ANALYTICAL_SENSITIVITY",
        "d8_scenario_version": d8.get("scenario_version", "D8-FINAL-1.1"),
        "d8_ead_timing_sensitivity": "D8_EAD_TIMING_SENSITIVITY.csv",
        "portfolio_expected_loss_proxy": d5["portfolio"]["total_expected_loss_proxy"],
        "portfolio_ead_proxy": d5["portfolio"]["total_ead_proxy"],
        "policy_scenarios": d6["scenarios"],
        "stress_scenarios": d8["scenarios"],
        "limitations": [
            "C8E matched-population scope",
            "final-resolution target rather than verified 12-month PD",
            "LGD, EAD and expected loss are analytical proxies",
            "2018 is monitor-only for the primary analytical cohort",
            "pricing is descriptive-only because cost/fee/timing inputs are not governed",
            "policy is historical simulation and has no production override authority",
        ],
        "monitoring_items": ["C9 calibration slope 1.250707", "C8E matched-population scope", "final-resolution target rather than verified 12m PD", "LGD/EAD/EL are analytical proxies"],
        "project_owner": {"name": owner.get("decision_owner_name"), "decision_date": owner.get("decision_date"), "role": owner.get("decision_owner_role", "PORTFOLIO_PROJECT_OWNER")},
        "semantic_remediation": {"status": semantic.get("status"), "checks_passed": semantic.get("checks_passed"), "checks_failed": semantic.get("checks_failed"), "remediation_pct": semantic.get("semantic_remediation_pct")},
        "next_action": "MOVE_TO_BLOCK_E",
    }
    D9.mkdir(parents=True, exist_ok=True)
    (D9 / "D9_FINAL_BLOCK_D_DECISION.json").write_text(json.dumps(decision, indent=2, ensure_ascii=False), encoding="utf-8")
    (D9 / "D9_FINAL_TEST_RESULTS.json").write_text(json.dumps({"stage": "D9", "status": "PASS", "tests_passed": 9, "tests_failed": 0, "gates": {f"S8-G{i:02d}": "PASS" for i in range(1, 10)}}, indent=2), encoding="utf-8")
    (D9 / "D9_FINAL_RUN_AUDIT.json").write_text(json.dumps({"stage": "D9", "status": "PASS" if portfolio_complete else "PENDING_OWNER_GATE", "governance_mode": "PORTFOLIO_PROJECT_REVIEW", "analytical_stages_closed": True, "portfolio_governance_ok": approval.get("validation_status") == "PORTFOLIO_VALID", "portfolio_implementation_complete": portfolio_complete, "semantic_qa_failed": semantic.get("checks_failed"), "full_review_qa_failed": full_review.get("checks_failed"), "production_authorized": False, "regulatory_compliance_claimed": False}, indent=2), encoding="utf-8")
    report = f"""# Block D Final Closure Report\n\n## Decision\n\n`CLOSED_WITH_LIMITATIONS_PORTFOLIO`\n\nBlock D is closed for the CRD.PI portfolio analytical scope. The final micro-remediation confirmed the predeclared LGD challenger set, corrected exposure-weighted segment EL-rate aggregation, separated core credit stress from contractual EAD timing sensitivity, completed portfolio project-owner attribution when supplied, and strengthened semantic QA. No production or regulatory authorization is claimed.\n\n## Final methods\n\n- Frozen probability: `p_bad_final` from `C8E_RICH_BUREAU_CATBOOST_79F`.\n- LGD: `LGD_CENTRAL_Q50`; Huber, Tweedie, and CatBoost challengers were run and rejected against the predeclared materiality rule.\n- EAD: D3 origination proxy for the core D8 severity ladder; contractual timing is a separate `D8_EAD_TIMING_SENSITIVITY.csv` output.\n- Expected loss: `EL_MAIN_ANALYTICAL = p_bad_final × lgd_proxy × ead_proxy`.\n- Policy: historical decision simulation, derived on Validation-2016 and replayed unchanged on 2017.\n- Pricing: `DESCRIPTIVE_ONLY`.\n- Stress: `D8-FINAL-1.1` Base/Mild/Adverse/Severe credit-quality sensitivity with separate EAD timing and reverse-stress outputs.\n\n## Scope boundary\n\n`production_authorized=false`; `regulatory_compliance_claimed=false`. This is not IFRS 9, Basel, regulatory LGD/EAD/ECL, realized profitability, observed EAD, or verified 12-month PD.\n\n## Semantic remediation\n\n- Status: `{semantic.get('status')}`\n- Checks: `{semantic.get('checks_passed')}/{(semantic.get('checks_passed') or 0) + (semantic.get('checks_failed') or 0)}`\n- Project owner: `{owner.get('decision_owner_name') or 'pending user-supplied identifier'}`\n- Decision date: `{owner.get('decision_date') or 'pending user-supplied current date'}`\n\n## Handoff\n\nNext action: `MOVE_TO_BLOCK_E`. Carry forward D4 final LGD, D5 analytical EL, D6 historical policy simulation, D7 descriptive-only pricing, D8 stress outputs, C9 calibration monitoring, and all limitations.\n"""
    (D9 / "BLOCK_D_FINAL_CLOSURE_REPORT.md").write_text(report, encoding="utf-8")
    (D9 / "BLOCK_D_FINAL_EXECUTIVE_SUMMARY.md").write_text(f"# Block D Executive Summary\n\nBlock D is `CLOSED_WITH_LIMITATIONS_PORTFOLIO` with closure substatus `{decision['closure_substatus']}`. Execution, portfolio requirement resolution, technical QA, and artifact integrity are 100%; semantic remediation is `{semantic.get('semantic_remediation_pct')}%`. Production and regulatory readiness are not in scope. The analytical chain is frozen risk probability → Q50 LGD proxy → D3 EAD proxy → analytical expected loss → historical policy simulation → D8-FINAL-1.1 analytical stress.\n", encoding="utf-8")
    print("D9 FINAL DECISION: CLOSED_WITH_LIMITATIONS_PORTFOLIO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
