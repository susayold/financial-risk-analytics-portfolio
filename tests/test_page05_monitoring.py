import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "public" / "data" / "page-05-monitoring.json"
ALERTS_PATH = ROOT / "public" / "data" / "monitoring-alerts.json"
THRESHOLDS_PATH = ROOT / "public" / "data" / "monitoring-thresholds.json"
HTML_PATH = ROOT / "monitoring" / "index.html"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def psi_severity(value):
    if value < 0.10:
        return "GREEN"
    if value < 0.25:
        return "AMBER"
    return "RED"


def slope_severity(value):
    if value < 0.65 or value > 1.35:
        return "RED"
    if value < 0.75 or value > 1.25:
        return "AMBER"
    return "GREEN"


def test_status_counts_and_population():
    page = load(PAGE_PATH)
    assert page["meta"]["block_e_status"] == "PASS_WITH_MONITORING"
    assert page["meta"]["canonical_release"] == "block-e-v1.0.2-final"
    assert page["population"]["rows"] == 310066
    assert page["population"]["feature_count"] == 79
    assert page["status"]["current_highest_kri"] == "AMBER"
    assert page["status"]["historical_highest_kri"] == "RED"
    assert page["governance_counts"] == {
        "kri_count": 92, "alert_count": 21, "amber_alert_count": 20,
        "red_alert_count": 1, "breach_count": 3, "investigation_count": 21,
        "action_count": 21, "green_alert_count": 0,
    }
    assert page["status"]["automatic_retraining"] is False
    assert page["status"]["recalibration_candidate"] is True
    assert page["status"]["redevelopment_candidate"] is False


def test_monitoring_metrics_and_thresholds():
    page = load(PAGE_PATH)
    thresholds = load(THRESHOLDS_PATH)
    drift = {row["feature"]: row for row in page["feature_drift"]}
    assert drift["int_rate"]["value"] == 0.100646
    assert drift["installment_to_loan"]["value"] == 0.136962
    assert drift["mths_since_last_delinq"]["value"] == 2.6635
    assert psi_severity(drift["int_rate"]["value"]) == "AMBER"
    assert psi_severity(drift["installment_to_loan"]["value"]) == "AMBER"
    assert page["score_drift"]["annual_psi"] == 0.0036352563867260096
    assert page["score_drift"]["annual_status"] == "GREEN"
    assert page["calibration"]["annual_slope"] == 1.2507071775766894
    assert slope_severity(page["calibration"]["annual_slope"]) == "AMBER"
    assert page["calibration"]["historical_red"]["slope"] == 1.3585283041585752
    assert slope_severity(page["calibration"]["historical_red"]["slope"]) == "RED"
    assert thresholds["version"] == "E0-1.0.1"
    assert "PSI" in thresholds["metrics"]
    assert "CALIBRATION_SLOPE" in thresholds["metrics"]


def test_alert_foreign_keys_and_claim_boundary():
    page = load(PAGE_PATH)
    alerts = load(ALERTS_PATH)["alerts"]
    alert_ids = {row["alert_id"] for row in alerts}
    assert len(alerts) == 21
    assert all(row["severity"] != "GREEN" for row in alerts)
    assert all(row["investigation_id"] and row["action_id"] for row in alerts)
    for breach in page["breaches"]:
        assert breach["alert_id"] in alert_ids
        assert breach["investigation_id"] and breach["action_id"]
    html = HTML_PATH.read_text(encoding="utf-8").lower()
    assert "pass with monitoring" in html
    assert "historical red" in html
    assert "red ≠ retrain" in html or "red != retrain" in html
    assert "not automatic retraining" in html
    assert "not production" in html
    assert "2018" in html and "disabled" in html
    assert "realized-loss backtesting" in html and "not claimed" in html
    assert "3 red breaches" not in html
    assert "real-time monitoring" not in html
    assert "production early-warning system" not in html


if __name__ == "__main__":
    test_status_counts_and_population()
    test_monitoring_metrics_and_thresholds()
    test_alert_foreign_keys_and_claim_boundary()
    print("page05 tests: PASS 3/3")
