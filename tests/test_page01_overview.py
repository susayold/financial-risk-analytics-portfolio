import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data" / "page-01-overview.json"
HTML = ROOT / "index.html"


def test_page01_canonical_data_contract():
    overview = json.loads(DATA.read_text(encoding="utf-8"))
    assert overview["portfolio"]["resolved_loans"] == 1_347_681
    assert overview["model"]["frozen_features"] == 79
    assert overview["model"]["oot_scored_n"] == 44_221
    assert abs(overview["model"]["oot_roc_auc"] - 0.8557777504539299) < 1e-12
    assert overview["economics"]["scored_accounts"] == 310_066
    assert abs(overview["economics"]["ead_proxy"] - 4_469_158_350.0) < 1e-6
    assert abs(overview["economics"]["expected_loss_proxy"] - 526_752_273.6678772) < 1e-6
    assert overview["monitoring"]["kri_count"] == 92
    assert overview["monitoring"]["alert_count"] == 21
    assert overview["monitoring"]["breach_count"] == 3
    assert overview["monitoring"]["current_highest_kri"] == "AMBER"
    assert overview["monitoring"]["historical_highest_kri"] == "RED"


def test_page01_claim_boundary_and_scopes_are_present():
    html = HTML.read_text(encoding="utf-8")
    assert "Analytical EL Rate" in html
    assert "Not a verified 12-month regulatory PD." in html
    assert "Not IFRS 9 / Basel production estimates." in html
    assert "No production authorization is claimed." in html
    assert "data-bind=\"economics.scored_accounts\"" in html
    assert "data-bind=\"monitoring.current_highest_kri\"" in html
    assert "data-tooltip=" in html


def test_page01_deep_dive_routes_exist():
    routes = ["portfolio-risk", "model-decisioning", "loss-policy-stress", "monitoring", "governance", "architecture"]
    html = HTML.read_text(encoding="utf-8")
    for route in routes:
        assert f'href="{route}/"' in html
        assert (ROOT / route / "index.html").exists()
