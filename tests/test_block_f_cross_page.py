import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_cross_page_metrics_and_release_are_consistent():
    p1 = load("page-01-overview.json")
    p3 = load("page-03-model-decisioning.json")
    p4 = load("page-04-loss-policy-stress.json")
    p5 = load("page-05-monitoring.json")
    p6 = load("page-06-governance.json")
    p7 = load("page-07-architecture.json")

    assert p1["model"]["oot_roc_auc"] == p3["oot"]["roc_auc"]
    assert p1["economics"]["expected_loss_rate"] == p4["central_case"]["el_rate"]
    assert p1["economics"]["scored_accounts"] == p3["population"]["scored_accounts"] == p4["central_case"]["accounts"] == p5["population"]["rows"] == p6["snapshot"]["rows"] == 310066
    assert p1["model"]["frozen_features"] == p3["contract"]["feature_count"] == p5["population"]["feature_count"] == p6["snapshot"]["feature_count"] == p7["upstream"]["feature_count"] == 79
    assert p1["monitoring"]["current_highest_kri"] == p5["status"]["current_highest_kri"] == p6["monitoring_state"]["current_highest_kri"] == "AMBER"
    assert p5["status"]["historical_highest_kri"] == p6["monitoring_state"]["historical_highest_kri"] == "RED"
    assert p5["governance_counts"]["breach_count"] == p6["monitoring_state"]["breach_count"] == 3
    assert p5["governance_counts"]["red_alert_count"] == p6["monitoring_state"]["red_alert_count"] == 1
    assert p5["meta"]["canonical_release"] == p6["meta"]["canonical_block_e_release"] == p7["upstream"]["block_e_release"] == "block-e-v1.0.2-final"
    assert p7["upstream"]["block_d_release"] == "block-d-v1.0-final"
    assert p7["upstream"]["upstream_analytics_changed_in_block_f"] is False
