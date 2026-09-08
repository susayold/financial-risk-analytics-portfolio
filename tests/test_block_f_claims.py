from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_PAGES = [
    ROOT / "index.html",
    ROOT / "portfolio-risk" / "index.html",
    ROOT / "model-decisioning" / "index.html",
    ROOT / "loss-policy-stress" / "index.html",
    ROOT / "monitoring" / "index.html",
    ROOT / "governance" / "index.html",
    ROOT / "architecture" / "index.html",
]


def joined_text():
    return "\n".join(path.read_text(encoding="utf-8", errors="ignore").lower() for path in PUBLIC_PAGES)


def test_no_unqualified_production_or_regulatory_claims():
    text = joined_text()
    forbidden_positive = [
        "3 red breaches",
        "production-approved model",
        "production ready credit model",
        "regulatory compliant credit model",
        "live production monitoring system",
        "real-time scoring api",
        "automatic retraining triggered",
        "bank-deployed underwriting",
    ]
    for phrase in forbidden_positive:
        assert phrase not in text


def test_boundary_language_is_visible():
    text = joined_text()
    assert "no production underwriting claim" in text or "production authorization remains false" in text
    assert "not regulatory" in text or "regulatory compliance" in text
    assert "analytical expected-loss proxy" in text or "analytical expected loss" in text
