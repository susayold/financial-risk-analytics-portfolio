import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_seven_page_registry_and_upstream_boundary():
    page = load("page-07-architecture.json")
    assert page["meta"]["status"] == "IN_PROGRESS"
    assert len(page["pages"]) == 7
    assert len({item["route"] for item in page["pages"]}) == 7
    assert page["upstream"]["block_d_release"] == "block-d-v1.0-final"
    assert page["upstream"]["block_e_release"] == "block-e-v1.0.2-final"
    assert page["upstream"]["scored_population"] == 310066
    assert page["upstream"]["feature_count"] == 79
    assert page["upstream"]["snapshot_sha256"] == "fe2ae600c9913ccfe827509f439c2f14108260e0e237f3fa78715b145123cd42"
    assert page["upstream"]["upstream_analytics_changed_in_block_f"] is False


def test_delivery_and_qa_are_separate_from_block_e():
    page = load("page-07-architecture.json")
    assert page["delivery"] == {"mode": "STATIC_PUBLIC_SITE", "hosting": "GITHUB_PAGES", "browser_row_level_data": False, "live_scoring_api": False, "production_database": False, "automatic_retraining": False}
    assert set(page["block_f_qa"].values()) == {"PENDING"}
    assert page["meta"]["production_authorized"] is False
    assert page["meta"]["regulatory_compliance_claimed"] is False
    assert page["public_private_boundary"]["flow"] == ["SANITIZE", "RECONCILE", "SCAN", "PUBLISH"]


def test_cross_page_metrics_reconcile():
    page = load("page-07-architecture.json")
    checks = page["cross_page_checks"]
    assert checks["overview_oot_roc_auc"] == checks["model_oot_roc_auc"]
    assert checks["overview_expected_loss_rate"] == checks["loss_expected_loss_rate"]
    assert checks["current_kri"] == "AMBER"
    assert checks["release"] == "block-e-v1.0.2-final"


def test_html_claim_boundary_and_required_sections():
    html = (ROOT / "architecture" / "index.html").read_text(encoding="utf-8").lower()
    for phrase in ("architecture &amp; delivery", "turn governed evidence", "7-page", "public-safe", "static", "block f", "in progress", "block-d-v1.0-final", "block-e-v1.0.2-final", "sanitize", "reconcile", "scan", "publish", "target delivery stack", "not claimed", "back to overview"):
        assert phrase in html, phrase
    for forbidden in ("block f delivered", "production architecture", "live scoring api", "real-time model monitoring", "regulatory compliant", "enterprise security certified", "github actions deployed", "astro migration complete"):
        assert forbidden not in html, forbidden
    assert "not bank deployment" in html
