import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data" / "page-02-portfolio-risk.json"
HTML = ROOT / "portfolio-risk" / "index.html"
JS = ROOT / "assets" / "crdpi-portfolio.js"


def test_page02_public_contract_reconciles():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    portfolio = payload["portfolio"]
    assert portfolio["accounts"] == 1_347_681
    assert portfolio["good_accounts"] + portfolio["bad_accounts"] == portfolio["accounts"]
    assert abs(portfolio["observed_bad_rate"] - portfolio["bad_accounts"] / portfolio["accounts"]) < 1e-12
    assert sum(row["accounts"] for row in payload["splits"]) == portfolio["accounts"]
    assert sum(row["accounts"] for row in payload["annual"]) == portfolio["accounts"]
    assert payload["governance"]["checks"]["duplicate_account_ids"] == 0
    assert payload["governance"]["checks"]["population_loss"] == 0
    assert payload["governance"]["checks"]["unassigned_splits"] == 0


def test_page02_has_required_evidence_and_boundaries():
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    assert payload["meta"]["public_safe"] is True
    assert payload["meta"]["claim_scope"] == "DESCRIPTIVE_NON_CAUSAL_OBSERVED_FINAL_RESOLUTION"
    assert payload["materiality"]["material_segment_count"] == 43
    assert len(payload["materiality"]["top_segments"]) == 8
    assert "not verified 12-month PD" in payload["interpretation"]["outcome"]
    assert "not causal" in payload["interpretation"]["segments"]
    assert "not observed regulatory EAD" in payload["interpretation"]["exposure"]
    assert "historical shadow" in payload["interpretation"]["time"]
    assert "Segment views overlap across dimensions and must not be summed." in html
    assert "Not predictive PD or approval policy" in html
    assert "../public/data/page-02-portfolio-risk.json" in js
    assert "../model-decisioning/" in html


def test_page02_route_is_real_page_not_placeholder():
    html = HTML.read_text(encoding="utf-8")
    assert "Page queued in Block F" not in html
    assert '<meta name="robots" content="noindex">' not in html
    assert '<section class="portfolio-hero">' in html
    assert 'id="concentration-rows"' in html
    assert 'id="annual-bars"' in html
