import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_portfolio_dates_and_release_language_are_unambiguous():
    page = load("page-02-portfolio-risk.json")
    assert page["meta"]["as_of"] == page["portfolio"]["max_issue_d"] == "2018-12-01"
    assert page["meta"]["oot_cutoff"] == "2017-12-01"
    html = (ROOT / "portfolio-risk" / "index.html").read_text(encoding="utf-8")
    assert "block-f-v1.0-final" in html
    assert "Latest data:" not in html
    assert "As of Block F (v1.0.2-final)" not in html


def test_model_and_monitoring_psi_keep_distinct_canonical_lineage():
    model = load("page-03-model-decisioning.json")
    monitoring = load("page-05-monitoring.json")
    model_psi = model["ranking"]["prediction_psi"]
    monitoring_psi = monitoring["score_drift"]["annual_psi"]
    assert math.isclose(model_psi, 0.003663365071810081, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(monitoring_psi, 0.0036352563867260096, rel_tol=0.0, abs_tol=1e-15)
    assert model["ranking"]["prediction_psi_basis"] == "Validation-2016_to_OOT-2017"
    assert not math.isclose(model_psi, monitoring_psi, rel_tol=0.0, abs_tol=1e-15)


def test_pricing_contract_uses_decimal_rate_units_and_reconciles_spread():
    page = load("page-04-loss-policy-stress.json")
    for row in page["pricing"]["diagnostics"]:
        assert 0 <= row["mean_rate"] <= 1
        assert abs((row["mean_rate"] - row["mean_el_rate"]) - row["diagnostic_spread"]) < 1e-12
    assert abs(page["pricing"]["diagnostics"][0]["mean_rate"] - 0.06923217335266634) < 1e-15


def test_monitoring_kri_domain_counts_reconcile_to_92():
    page = load("page-05-monitoring.json")
    counts = page["kri_domain_counts"]
    assert counts == {
        "feature_drift": 3,
        "score_risk_mix": 17,
        "performance_calibration": 68,
        "loss_severity": 1,
        "policy_capacity_concentration": 3,
        "total": 92,
    }
    assert page["data_quality_control"]["kri_count"] == 0
    assert page["governance_counts"]["kri_count"] == counts["total"]


def test_final_delivery_status_is_not_stale_in_public_pages_or_docs():
    overview = (ROOT / "index.html").read_text(encoding="utf-8")
    architecture = (ROOT / "architecture" / "index.html").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    master = (ROOT / "PROJECT_MASTER_LINKS.md").read_text(encoding="utf-8")
    assert "Block F · Delivery in progress" not in overview
    assert "BLOCK F · IN PROGRESS" not in architecture
    assert "Current state: IN PROGRESS" not in architecture
    assert "final closure in progress" not in readme
    assert "Block F is being closed" not in master
    assert "block-f-v1.0-final" in readme
    assert "block-f-v1.0-final" in master


def test_overview_does_not_claim_proven_approval_improvement():
    overview = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "Higher quality approvals" not in overview
    assert "Historical policy simulation" in overview
