"""Semantic QA for the final Block D micro-remediation plan."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
OUT = BLOCK / "BLOCK_D_SEMANTIC_QA.json"


def load(rel: str) -> dict:
    return json.loads((BLOCK / rel).read_text(encoding="utf-8"))


def main() -> int:
    checks = []

    def add(check_id: str, passed: bool, observed, expected, evidence: str) -> None:
        checks.append({"check_id": check_id, "pass": bool(passed), "observed": observed, "expected": expected, "evidence": evidence})

    d4_comp = pd.read_csv(BLOCK / "D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_MODEL_COMPARISON.csv")
    required_models = {"HUBER_REGRESSOR", "TWEEDIE_REGRESSOR", "CATBOOST_REGRESSOR"}
    add("R8-G01", required_models.issubset(set(d4_comp["model"])), sorted(set(d4_comp["model"])), sorted(required_models), "D4_EMPIRICAL_LGD_MODEL_COMPARISON.csv")

    d4_audit = load("D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_RUN_AUDIT.json")
    skipped = d4_audit.get("skipped_folds", [])
    completed = d4_audit.get("completed_folds", [])
    fold_ok = len(skipped) == len(set(skipped)) and len(completed) == len(set(completed)) and not set(skipped).intersection(completed) and d4_audit.get("skipped_model_fold_rows") == len(skipped) * len(d4_comp["model"].unique())
    add("R8-G02", fold_ok, {"skipped_folds": skipped, "completed_folds": completed, "skipped_model_fold_rows": d4_audit.get("skipped_model_fold_rows")}, "unique folds, disjoint sets, explicit model-fold count", "D4_EMPIRICAL_LGD_RUN_AUDIT.json")

    d5_checks = []
    for name in ("D5_RISK_DECILE_EL.csv", "D5_SEGMENT_EL_SUMMARY.csv"):
        frame = pd.read_csv(BLOCK / "D5_EXPECTED_LOSS" / name)
        required = {"segment_el_rate", "total_ead_proxy", "total_expected_loss_proxy"}
        no_ambiguous_rate = "portfolio_el_rate" not in frame.columns
        for _, row in frame.iterrows():
            expected_rate = np.nan if row.total_ead_proxy == 0 else row.total_expected_loss_proxy / row.total_ead_proxy
            d5_checks.append(bool(np.isclose(row.segment_el_rate, expected_rate, rtol=1e-12, atol=1e-12, equal_nan=True)) and required.issubset(frame.columns) and no_ambiguous_rate)
    d5_recon = load("D5_EXPECTED_LOSS/D5_EL_RECONCILIATION.json")
    add("R8-G03", bool(d5_checks) and all(d5_checks) and d5_recon.get("tests_failed") == 0, {"rows_checked": len(d5_checks), "all_rates_valid": all(d5_checks) if d5_checks else False}, "all segment rates = sum(EL)/sum(EAD)", "D5_RISK_DECILE_EL.csv + D5_SEGMENT_EL_SUMMARY.csv")

    d8 = load("D8_STRESS/D8_FINAL_DECISION.json")
    severity_basis_ok = d8.get("scenario_version") == "D8-FINAL-1.1" and d8.get("ead_method") == "ead_origination_proxy" and d8.get("severity_ead_methods") == ["ead_origination_proxy"]
    add("R8-G04", severity_basis_ok, {"scenario_version": d8.get("scenario_version"), "ead_method": d8.get("ead_method"), "severity_ead_methods": d8.get("severity_ead_methods")}, "one consistent origination EAD basis", "D8_FINAL_DECISION.json")

    timing = pd.read_csv(BLOCK / "D8_STRESS/D8_EAD_TIMING_SENSITIVITY.csv")
    expected_timing = ["EAD_0M", "EAD_6M", "EAD_12M", "EAD_18M", "EAD_24M"]
    timing_ok = timing["timing_scenario"].tolist() == expected_timing and bool(np.all(np.diff(timing["total_ead_proxy"].to_numpy(float)) <= 1e-6))
    add("R8-G05", timing_ok, {"scenarios": timing["timing_scenario"].tolist(), "ead_non_increasing": bool(np.all(np.diff(timing["total_ead_proxy"].to_numpy(float)) <= 1e-6))}, {"scenarios": expected_timing, "ead_non_increasing": True}, "D8_EAD_TIMING_SENSITIVITY.csv")

    owner = load("D9_CLOSURE/D9_PORTFOLIO_PROJECT_OWNER_DECISIONS.json")
    owner_name = owner.get("decision_owner_name")
    owner_date = owner.get("decision_date")
    owner_ok = isinstance(owner_name, str) and bool(owner_name.strip()) and isinstance(owner_date, str) and bool(owner_date.strip())
    signoffs_ok = all(x.get("status") == "NOT_APPLICABLE_PORTFOLIO_PROJECT" for x in owner.get("owner_signoff", {}).values())
    decisions_ok = all(item.get("decision_owner") == owner_name and item.get("decision_date") == owner_date for item in owner.get("decisions", {}).values())
    add("R8-G06", owner_ok and signoffs_ok and decisions_ok, {"decision_owner_name": owner_name, "decision_date": owner_date, "institutional_signoffs_na": signoffs_ok}, "non-null project owner/date; institutional signoffs N/A", "D9_PORTFOLIO_PROJECT_OWNER_DECISIONS.json")

    status_files = ["README.md", "PROJECT_MASTER_LINKS.md", "block-d/README.md", "block-d/BLOCK_D_STATUS.md", "block-d/BLOCK_D_FINAL_SCORECARD.md", "block-d/BLOCK_D_VALIDATION_REPORT.md", "block-d/D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json"]
    status_ok = all("CLOSED_WITH_LIMITATIONS_PORTFOLIO" in (ROOT / rel).read_text(encoding="utf-8", errors="ignore") for rel in status_files)
    add("R8-G07", status_ok, {rel: "CLOSED_WITH_LIMITATIONS_PORTFOLIO" in (ROOT / rel).read_text(encoding="utf-8", errors="ignore") for rel in status_files}, "all current status sources agree", "status source set")

    old_audit = load("D8_STRESS/D8_FINAL_RUN_AUDIT.json")
    historical = load("D8_STRESS/D8_GATE_RESULTS.json")
    illustrated = load("D8_STRESS/D8_ILLUSTRATIVE_SENSITIVITY_AUDIT.json")
    superseded_ok = "superseded" in str(old_audit.get("old_version", "")).lower() and bool(historical.get("superseded_by")) and bool(illustrated.get("superseded_by"))
    add("R8-G08", superseded_ok, {"final_audit": old_audit.get("old_version"), "historical_gate": historical.get("superseded_by"), "illustrative": illustrated.get("superseded_by")}, "older methodology explicitly labelled superseded", "D8 historical evidence")

    passed = sum(x["pass"] for x in checks)
    failed = len(checks) - passed
    result = {"run_name": "block_d_semantic_qa", "run_date": date.today().isoformat(), "status": "PASS" if failed == 0 else "FAIL", "checks_passed": passed, "checks_failed": failed, "checks": checks, "semantic_remediation_pct": 100.0 if failed == 0 else round(passed / len(checks) * 100, 2)}
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"SEMANTIC QA {result['status']} — {passed}/{len(checks)} checks pass")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
