"""Build sanitized aggregate contracts for the Block F Monitoring page."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "block-e"
PUBLIC = ROOT / "public" / "data"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def f(value: str) -> float:
    return float(value)


def i(value: str) -> int:
    return int(value)


def main() -> None:
    thresholds = read_csv(E / "E0_MONITORING_CONTRACT" / "E0_THRESHOLD_REGISTER.csv")
    feature_alerts = read_csv(E / "E3_FEATURE_DRIFT" / "E3_ALERTS_FINAL_79F.csv")
    score_psi = read_csv(E / "E4_SCORE_RISK_MIX" / "score_psi.csv")
    calibration = read_csv(E / "E5_PERFORMANCE_CALIBRATION" / "calibration_monitor.csv")
    discrimination = read_csv(E / "E5_PERFORMANCE_CALIBRATION" / "discrimination_monitor.csv")
    e5_alerts = read_csv(E / "E5_PERFORMANCE_CALIBRATION" / "E5_ALERTS_PATCHED.csv")
    e6_alerts = read_csv(E / "E6_EXPECTED_LOSS_MONITORING" / "E6_ALERTS.csv")
    policy_alerts = read_csv(E / "E7_POLICY_CONCENTRATION" / "E7_ALERTS_PATCHED.csv")
    e8 = read_json(E / "E8_KRI_GOVERNANCE" / "E8_TEST_RESULTS_PATCHED.json")
    alert_log = read_csv(E / "E8_KRI_GOVERNANCE" / "alert_log_PATCHED.csv")
    breaches = read_csv(E / "E8_KRI_GOVERNANCE" / "breach_register_PATCHED.csv")
    actions = read_csv(E / "E8_KRI_GOVERNANCE" / "action_register_PATCHED.csv")
    decision = read_json(E / "E9_FINAL" / "BLOCK_E_DECISION_PATCHED.json")

    counts = {
        "kri_count": e8["kri_count"],
        "alert_count": e8["alert_count"],
        "amber_alert_count": e8["amber_alert_count"],
        "red_alert_count": e8["red_alert_count"],
        "breach_count": e8["breach_count"],
        "investigation_count": e8["investigation_count"],
        "action_count": e8["action_count"],
        "green_alert_count": 0,
    }
    assert counts == {
        "kri_count": 92, "alert_count": 21, "amber_alert_count": 20,
        "red_alert_count": 1, "breach_count": 3, "investigation_count": 21,
        "action_count": 21, "green_alert_count": 0,
    }

    threshold_payload = {"version": "E0-1.0.1", "metrics": {}}
    threshold_by_id = {row["threshold_id"]: row for row in thresholds}
    for row in thresholds:
        threshold_payload["metrics"][row["metric_id"]] = {
            "frequency_scope": row["frequency_scope"],
            "green": row["green_rule"],
            "amber": row["amber_rule"],
            "red": row["red_rule"],
            "insufficient_sample": row["insufficient_sample_rule"],
            "persistence": row["persistence_rule"],
        }

    headline_feature_drift = [{
        "kri_id": row["kri_id"],
        "feature": row["feature"],
        "window": row["window_id"],
        "metric": row["metric_id"],
        "value": f(row["observed_value"]),
        "severity": row["status"],
        "action": "WATCH",
    } for row in feature_alerts]
    assert len(headline_feature_drift) == 3

    score_monthly = [{
        "window": row["window_id"], "psi": f(row["psi"]), "severity": row["status"], "n": i(row["account_count"])
    } for row in score_psi if row["frequency"] == "monthly"]
    score_quarterly = [{
        "window": row["window_id"], "psi": f(row["psi"]), "severity": row["status"], "n": i(row["account_count"])
    } for row in score_psi if row["frequency"] == "quarterly"]
    annual_score = next(row for row in score_psi if row["window_id"] == "OOT")
    assert f(annual_score["psi"]) < 0.10

    oot_cal = next(row for row in calibration if row["window_id"] == "OOT")
    red_cal = next(row for row in calibration if row["window_id"] == "2017-10")
    cal_monthly = [{
        "window": row["window_id"], "slope": f(row["slope"]), "gap": f(row["calibration_gap"]),
        "mean_prediction": f(row["mean_prediction"]), "observed_bad_rate": f(row["observed_bad_rate"]),
        "n": i(row["account_count"]), "bad_count": i(row["bad_count"]),
    } for row in calibration if row["frequency"] == "monthly" and row["window_id"].startswith("2017-")]
    discrimination_oot = next(row for row in discrimination if row["window_id"] == "OOT")
    discrimination_quarterly = [{
        "window": row["window_id"], "roc_auc": f(row["roc_auc"]), "n": i(row["account_count"]),
        "bad_count": i(row["bad_count"]), "good_count": i(row["good_count"]),
    } for row in discrimination if row["frequency"] == "quarterly" and row["window_id"].startswith("2017Q")]

    policy_capacity = [{
        "policy": row["policy"], "over_capacity_pp": f(row["over_capacity_pp"]),
        "severity": row["severity"], "action": row["recommended_action"],
    } for row in policy_alerts]
    policy_capacity.append({"policy": "CONSERVATIVE", "severity": "GREEN", "alert_generated": False, "action": "NO_ACTION"})

    breach_by_alert = {row["alert_id"]: row for row in breaches}
    action_by_investigation = {row["investigation_id"]: row for row in actions}
    all_alerts = []
    for row in alert_log:
        if row["severity"] == "GREEN":
            raise ValueError("GREEN alert found in canonical alert log")
        breach = breach_by_alert.get(row["alert_id"], {})
        action = action_by_investigation.get(row["investigation_id"], {})
        all_alerts.append({
            "alert_id": row["alert_id"], "kri_id": row["kri_id"], "severity": row["severity"],
            "source_stage": row["source_stage"], "metric": row["metric_id"], "window": row["window_id"],
            "frequency": row["frequency"], "value": f(row["metric_value"]),
            "threshold_id": row["threshold_id"],
            "threshold": threshold_by_id[row["threshold_id"]]["red_rule"] if row["severity"] == "RED" else threshold_by_id[row["threshold_id"]]["amber_rule"],
            "population_scope": row["population_scope"], "investigation_id": row["investigation_id"],
            "action_id": row["action_id"], "action_type": action.get("action_type", "WATCH"),
            "breach_id": breach.get("breach_id"), "breach_type": breach.get("breach_type"),
            "persistence_count": i(breach["persistence_count"]) if breach else 0,
            "status": row["final_status"], "model_change_required": False,
            "production_change_required": False,
        })
    if len(all_alerts) != counts["alert_count"]:
        raise ValueError("Alert count mismatch")
    if not all(a["investigation_id"] and a["action_id"] for a in all_alerts):
        raise ValueError("Alert foreign keys are incomplete")
    if not all(row["alert_id"] and row["investigation_id"] and row["action_id"] for row in breaches):
        raise ValueError("Breach foreign keys are incomplete")

    breach_payload = [{
        "id": row["breach_id"], "kri_id": row["kri_id"], "alert_id": row["alert_id"],
        "type": row["breach_type"], "metric": row["kri_id"].split("-")[1] if "-" in row["kri_id"] else row["kri_id"],
        "window": row["window_id"], "severity": row["severity"],
        "persistence_count": i(row["persistence_count"]), "investigation_id": row["investigation_id"],
        "action_id": row["action_id"],
    } for row in breaches]

    payload = {
        "meta": {
            "project": "CRD.PI", "page": "monitoring", "version": "F-P05-CONTENT-1.0",
            "block_e_status": "PASS_WITH_MONITORING", "canonical_release": "block-e-v1.0.2-final",
            "baseline": "Validation-2016", "monitoring_window": "OOT-2017",
            "production_authorized": False, "regulatory_compliance_claimed": False,
            "public_safe": True,
        },
        "population": {
            "rows": 310066, "feature_count": 79, "unique_account_grain": True,
            "model_id": "C8E_RICH_BUREAU_CATBOOST_79F",
            "snapshot_sha256": "fe2ae600c9913ccfe827509f439c2f14108260e0e237f3fa78715b145123cd42",
        },
        "status": {
            "current_highest_kri": decision["highest_current_kri_status"],
            "historical_highest_kri": decision["highest_observed_kri_status"],
            "recalibration_candidate": decision["recalibration_candidate"],
            "redevelopment_candidate": decision["redevelopment_candidate"],
            "automatic_retraining": False,
            "model_use_restriction": decision["model_use_restrictions"][0],
            "portfolio_project_use_approved": decision["portfolio_project_use_approved"],
        },
        "governance_counts": counts,
        "feature_drift": headline_feature_drift,
        "score_drift": {
            "annual_psi": f(annual_score["psi"]), "annual_status": annual_score["status"],
            "monthly": score_monthly, "quarterly": score_quarterly,
        },
        "discrimination": {
            "oot_roc_auc": f(discrimination_oot["roc_auc"]), "oot_ks": f(discrimination_oot["ks"]),
            "quarterly_auc_range": max(row["roc_auc"] for row in discrimination_quarterly) - min(row["roc_auc"] for row in discrimination_quarterly),
            "quarterly": discrimination_quarterly,
        },
        "calibration": {
            "annual_slope": f(oot_cal["slope"]), "annual_severity": "AMBER",
            "annual_mean_prediction": f(oot_cal["mean_prediction"]), "annual_observed_bad_rate": f(oot_cal["observed_bad_rate"]),
            "historical_red": {
                "window": red_cal["window_id"], "slope": f(red_cal["slope"]), "sample_n": i(red_cal["account_count"]),
                "bad_count": i(red_cal["bad_count"]), "severity": "RED", "alert_id": "E8A-016",
                "breach_id": "BR-003", "investigation_id": "INV-016", "action_id": "ACT-016",
                "action": "CALIBRATION_REVIEW", "automatic_retraining": False,
            },
            "monthly": cal_monthly,
        },
        "policy_capacity": policy_capacity,
        "loss_monitoring": {"status": "GREEN", "non_green_alert_count": len(e6_alerts), "claim_boundary": "ANALYTICAL PROXY MONITORING ONLY"},
        "breaches": breach_payload,
        "change_control": {"model_recalibration_candidate": True, "model_redevelopment_candidate": False, "automatic_retraining": False, "model_change_required_for_red_event": False, "production_change_required": False},
        "controls": {"threshold_version": "E0-1.0.1", "block_c_reopened": False, "model_retrained": False, "feature_contract_changed": False, "outcome_2018_monitoring": "DISABLED / UNAVAILABLE", "realized_loss_backtesting": "DISABLED / NOT CLAIMED", "green_alerts_generated": False, "root_cause_highlights": ["CALIBRATION", "MISSINGNESS", "POLICY_CAPACITY", "POPULATION / FEATURE SHIFT"]},
    }
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "page-05-monitoring.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (PUBLIC / "monitoring-thresholds.json").write_text(json.dumps(threshold_payload, indent=2) + "\n", encoding="utf-8")
    (PUBLIC / "monitoring-alerts.json").write_text(json.dumps({"meta": {"public_safe": True, "row_level_data_shipped": False}, "alerts": all_alerts}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote Page 05 contracts: {counts['kri_count']} KRIs, {counts['alert_count']} alerts, {len(breach_payload)} breaches")


if __name__ == "__main__":
    main()
