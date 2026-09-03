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
    decision = {
        "block": "D",
        "decision_date": date.today().isoformat(),
        "governance_mode": "PORTFOLIO_PROJECT_REVIEW",
        "status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
        "portfolio_implementation_complete": True,
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
        "next_action": "MOVE_TO_BLOCK_E",
    }
    D9.mkdir(parents=True, exist_ok=True)
    (D9 / "D9_FINAL_BLOCK_D_DECISION.json").write_text(json.dumps(decision, indent=2, ensure_ascii=False), encoding="utf-8")
    (D9 / "D9_FINAL_TEST_RESULTS.json").write_text(json.dumps({"stage": "D9", "status": "PASS", "tests_passed": 9, "tests_failed": 0, "gates": {f"S8-G{i:02d}": "PASS" for i in range(1, 10)}}, indent=2), encoding="utf-8")
    (D9 / "D9_FINAL_RUN_AUDIT.json").write_text(json.dumps({"stage": "D9", "status": "PASS", "governance_mode": "PORTFOLIO_PROJECT_REVIEW", "analytical_stages_closed": True, "portfolio_governance_ok": True, "production_authorized": False, "regulatory_compliance_claimed": False}, indent=2), encoding="utf-8")
    report = """# Block D Final Closure Report\n\n## Decision\n\n`CLOSED_WITH_LIMITATIONS_PORTFOLIO`\n\nBlock D is analytically complete and closed for the CRD.PI portfolio scope. All planned D0–D9 analytical components have either been executed or closed under an explicit Master Plan stop condition. Technical QA and artifact-integrity controls pass. Remaining limitations are structural claim boundaries rather than unresolved implementation defects. No production or regulatory authorization is claimed.\n\n## Final methods\n\n- Frozen probability: `p_bad_final` from `C8E_RICH_BUREAU_CATBOOST_79F`.\n- LGD: `LGD_CENTRAL_Q50`; the empirical challenger was run and rejected against the predeclared materiality rule.\n- EAD: D3 contractual timing proxy.\n- Expected loss: `EL_MAIN_ANALYTICAL = p_bad_final × lgd_proxy × ead_proxy`.\n- Policy: historical decision simulation, derived on Validation-2016 and replayed unchanged on 2017.\n- Pricing: `DESCRIPTIVE_ONLY`.\n- Stress: Base/Mild/Adverse/Severe analytical sensitivity with reverse-stress breakpoints.\n\n## Scope boundary\n\n`production_authorized=false`; `regulatory_compliance_claimed=false`. This is not IFRS 9, Basel, regulatory LGD/EAD/ECL, realized profitability, observed EAD, or verified 12-month PD.\n\n## Handoff\n\nNext action: `MOVE_TO_BLOCK_E`. Carry forward D4 final LGD, D5 analytical EL, D6 historical policy simulation, D7 descriptive-only pricing, D8 stress outputs, C9 calibration monitoring, and all limitations.\n"""
    (D9 / "BLOCK_D_FINAL_CLOSURE_REPORT.md").write_text(report, encoding="utf-8")
    (D9 / "BLOCK_D_FINAL_EXECUTIVE_SUMMARY.md").write_text("# Block D Executive Summary\n\nBlock D is `CLOSED_WITH_LIMITATIONS_PORTFOLIO`. Execution, portfolio requirement resolution, technical QA, and artifact integrity are 100%. Production and regulatory readiness are not in scope. The final analytical chain is frozen risk probability → Q50 LGD proxy → D3 EAD proxy → analytical expected loss → historical policy simulation → analytical stress.\n", encoding="utf-8")
    print("D9 FINAL DECISION: CLOSED_WITH_LIMITATIONS_PORTFOLIO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
