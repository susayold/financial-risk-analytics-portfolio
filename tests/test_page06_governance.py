import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_release_precedence_and_snapshot():
    page = load("page-06-governance.json")
    assert page["meta"]["canonical_block_e_release"] == "block-e-v1.0.2-final"
    assert page["meta"]["block_e_status"] == "PASS_WITH_MONITORING"
    assert page["snapshot"] == {
        "rows": 310066,
        "feature_count": 79,
        "unique_account_key": True,
        "sha256": "fe2ae600c9913ccfe827509f439c2f14108260e0e237f3fa78715b145123cd42",
        "model": "C8E_RICH_BUREAU_CATBOOST_79F",
    }


def test_governance_counts_and_qa():
    page = load("page-06-governance.json")
    assert page["monitoring_state"] == {
        "kri_count": 92, "alert_count": 21, "amber_alert_count": 20,
        "red_alert_count": 1, "breach_count": 3, "investigation_count": 21,
        "action_count": 21, "green_alert_count": 0, "current_highest_kri": "AMBER",
        "historical_highest_kri": "RED",
    }
    assert page["qa"]["e8_passed"] == 25
    assert page["qa"]["e8_failed"] == 0
    assert page["qa"]["e9_passed"] == 35
    assert page["qa"]["e9_failed"] == 0
    assert page["qa"]["public_private_scan"] == "PASS"
    assert page["qa"]["checksum_integrity"] == "PASS"
    assert page["qa"]["foreign_keys"] == "PASS"


def test_change_control_and_red_trace():
    page = load("page-06-governance.json")
    change = page["change_control"]
    assert change["recalibration_candidate"] is True
    assert change["recalibration_executed"] is False
    assert change["redevelopment_candidate"] is False
    assert change["automatic_retraining"] is False
    assert change["production_authorized"] is False
    assert change["regulatory_compliance_claimed"] is False
    assert page["model_governance"]["block_c_model_reopened"] is False
    red = page["historical_red_example"]
    assert red["window"] == "2017-10"
    assert abs(red["value"] - 1.3585283041585752) < 1e-12
    assert red["breach_id"] == "BR-003"
    assert red["investigation_id"] == "INV-016"
    assert red["action_id"] == "ACT-016"
    assert red["action_type"] == "CALIBRATION_REVIEW"


def test_taxonomy_and_public_private_boundary():
    taxonomy = load("governance-taxonomy.json")
    assert taxonomy["counts"] == {"root_cause_domains": 13, "action_types": 12}
    evidence = load("governance-evidence-index.json")
    assert len(evidence) == 10
    assert all("C:\\" not in json.dumps(row) and "D:\\" not in json.dumps(row) for row in evidence)
    assert any(row["public_private_class"] == "PRIVATE_DRIVE" for row in evidence)


def test_html_claim_boundary_and_required_controls():
    html = (ROOT / "governance" / "index.html").read_text(encoding="utf-8").lower()
    for phrase in ("governance &amp; audit", "pass_with_monitoring", "35 / 35", "25 / 25", "checksum", "current amber", "historical red", "red ≠ retrain", "block-e-v1.0.2-final", "2017-10", "copy full hash", "not production"):
        assert phrase in html, phrase
    for forbidden in ("3 red breaches", "production approved", "regulatory compliant", "externally validated", "independently validated by a separate team", "model risk = low", "100% documentation coverage", "production-ready", "real-time governance", "red automatically triggers retraining", "v1.0.1 is current"):
        assert forbidden not in html, forbidden
    assert "not every patch is a model change" in html
    assert "../monitoring/" in html
    assert "../architecture/" in html
