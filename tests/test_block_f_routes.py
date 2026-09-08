import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = json.loads((ROOT / "config" / "routes.json").read_text(encoding="utf-8"))["primary_pages"]


def test_seven_routes_have_html_and_data_contracts():
    assert len(ROUTES) == 7
    assert len({row["route"] for row in ROUTES}) == 7
    for row in ROUTES:
        html = ROOT / "index.html" if row["route"] == "/" else ROOT / row["route"].strip("/") / "index.html"
        data = ROOT / "public" / "data" / row["data_contract"]
        assert html.exists(), row["route"]
        assert data.exists(), row["data_contract"]


def test_architecture_product_map_resolves_repository_relative_routes():
    js = (ROOT / "assets" / "crdpi-architecture.js").read_text(encoding="utf-8")
    assert "resolveProjectRoute" in js
    assert "link.href = page.route" not in js
    assert "new URL" in js


def test_architecture_uses_architecture_specific_og_image():
    html = (ROOT / "architecture" / "index.html").read_text(encoding="utf-8")
    assert '../assets/og/crdpi-architecture.svg' in html
    assert 'property="og:image" content="../assets/og/crdpi-governance.svg"' not in html


def test_no_primary_page_is_noindex_placeholder():
    for row in ROUTES:
        html_path = ROOT / "index.html" if row["route"] == "/" else ROOT / row["route"].strip("/") / "index.html"
        html = html_path.read_text(encoding="utf-8")
        assert "Page queued in Block F" not in html
        assert '<meta name="robots" content="noindex">' not in html
