from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_root_readme_positions_crdpi_as_flagship():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("# CRD.PI — Credit Risk Decisioning & Portfolio Intelligence")
    assert "flagship end-to-end project" in readme
    assert "The website presents five completed, independent financial risk projects." not in readme


def test_master_links_uses_proxy_safe_block_d_wording():
    text = (ROOT / "PROJECT_MASTER_LINKS.md").read_text(encoding="utf-8")
    assert "Model-score, LGD/EAD proxies, analytical expected loss" in text
    assert "PD/LGD/EAD/ECL, loss quantification and stress gates" not in text


def test_public_readme_has_no_labelled_phone_contact():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "phone:" not in text
