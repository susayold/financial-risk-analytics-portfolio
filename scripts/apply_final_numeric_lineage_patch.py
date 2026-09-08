"""One-time remediation for final public numeric lineage audit.

This script is intentionally idempotent. It restores the distinct Block C and
Block E PSI definitions, records a sanitized public Block C evidence bridge,
and strengthens regression/live-smoke checks so the two metrics cannot be
silently collapsed again.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected source fragment not found in {path.relative_to(ROOT)}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    evidence_path = ROOT / "evidence" / "block-c" / "C9_PUBLIC_CLOSURE_SUMMARY.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema": "crd.pi.block-c.c9-public-closure-summary.v1",
        "project": "CRD.PI",
        "block": "C",
        "stage": "C9_FINAL_OOT_AND_BLOCK_C_CLOSURE",
        "status": "PASS_WITH_MONITORING",
        "model_id": "C8E_RICH_BUREAU_CATBOOST_79F",
        "feature_count": 79,
        "prediction_psi": 0.003663365071810081,
        "prediction_psi_basis": "Validation-2016_to_OOT-2017",
        "source": "Block C C9 BLOCK_C_CLOSURE.md canonical evidence; sanitized public bridge",
        "block_e_monitoring_annual_psi_is_separate": True,
        "production_authorized": False,
        "regulatory_compliance_claimed": False,
    }
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    builder = ROOT / "scripts" / "build_page03_public_data.py"
    replace_once(
        builder,
        '    score_psi = read_csv(ROOT / "block-e" / "E4_SCORE_RISK_MIX" / "score_psi.csv")\n',
        '    block_c_public = read_json(ROOT / "evidence" / "block-c" / "C9_PUBLIC_CLOSURE_SUMMARY.json")\n',
    )
    replace_once(
        builder,
        '    annual_score_psi = row_for(score_psi, "window_id", "OOT")\n',
        '    if block_c_public["model_id"] != "C8E_RICH_BUREAU_CATBOOST_79F":\n'
        '        raise ValueError("Block C public evidence bridge model ID mismatch")\n'
        '    if block_c_public["prediction_psi_basis"] != "Validation-2016_to_OOT-2017":\n'
        '        raise ValueError("Block C prediction PSI basis mismatch")\n',
    )
    replace_once(
        builder,
        '            "prediction_psi": number(annual_score_psi, "psi"),\n'
        '            "interpretation": "Risk ordering remains clean while aggregate score-distribution shift is low.",\n',
        '            "prediction_psi": block_c_public["prediction_psi"],\n'
        '            "prediction_psi_basis": block_c_public["prediction_psi_basis"],\n'
        '            "prediction_psi_source": block_c_public["source"],\n'
        '            "interpretation": "Block C C9 prediction PSI measures Validation-2016 to OOT-2017 shift under the frozen-model validation contract; Block E annual monitoring PSI is a separate downstream calculation.",\n',
    )

    test_recon = ROOT / "tests" / "test_website_reconciliation.py"
    replace_once(test_recon, "import json\n", "import json\nimport math\n")
    replace_once(
        test_recon,
        'def test_model_prediction_psi_uses_monitoring_canonical_value():\n'
        '    model = load("page-03-model-decisioning.json")\n'
        '    monitoring = load("page-05-monitoring.json")\n'
        '    assert model["ranking"]["prediction_psi"] == monitoring["score_drift"]["annual_psi"]\n',
        'def test_model_and_monitoring_psi_keep_distinct_canonical_lineage():\n'
        '    model = load("page-03-model-decisioning.json")\n'
        '    monitoring = load("page-05-monitoring.json")\n'
        '    model_psi = model["ranking"]["prediction_psi"]\n'
        '    monitoring_psi = monitoring["score_drift"]["annual_psi"]\n'
        '    assert math.isclose(model_psi, 0.003663365071810081, rel_tol=0.0, abs_tol=1e-15)\n'
        '    assert math.isclose(monitoring_psi, 0.0036352563867260096, rel_tol=0.0, abs_tol=1e-15)\n'
        '    assert model["ranking"]["prediction_psi_basis"] == "Validation-2016_to_OOT-2017"\n'
        '    assert not math.isclose(model_psi, monitoring_psi, rel_tol=0.0, abs_tol=1e-15)\n',
    )

    test_page03 = ROOT / "tests" / "test_page03_model_decisioning.py"
    replace_once(
        test_page03,
        '    assert page["ranking"]["decile_spearman"] == 1.0\n',
        '    assert page["ranking"]["decile_spearman"] == 1.0\n'
        '    assert abs(page["ranking"]["prediction_psi"] - 0.003663365071810081) < 1e-15\n'
        '    assert page["ranking"]["prediction_psi_basis"] == "Validation-2016_to_OOT-2017"\n',
    )

    live_smoke = ROOT / "scripts" / "block_f_live_smoke.py"
    replace_once(
        live_smoke,
        'unit errors, PSI divergence, and KRI-count drift cannot silently reappear.\n',
        'unit errors, PSI lineage collapse, and KRI-count drift cannot silently reappear.\n',
    )
    replace_once(
        live_smoke,
        '    # Page 03 and Page 05 must use one canonical annual score PSI.\n'
        '    page03 = _json(parsed_json, "/public/data/page-03-model-decisioning.json")\n'
        '    page05 = _json(parsed_json, "/public/data/page-05-monitoring.json")\n'
        '    ranking = page03.get("ranking", {}) if isinstance(page03.get("ranking"), dict) else {}\n'
        '    score_drift = page05.get("score_drift", {}) if isinstance(page05.get("score_drift"), dict) else {}\n'
        '    p03_psi = ranking.get("prediction_psi")\n'
        '    p05_psi = score_drift.get("annual_psi")\n'
        '    if not isinstance(p03_psi, (int, float)) or not isinstance(p05_psi, (int, float)) or not math.isclose(float(p03_psi), float(p05_psi), rel_tol=0.0, abs_tol=1e-15):\n'
        '        failures.append(f"page-03/page-05: annual score PSI mismatch {p03_psi!r} vs {p05_psi!r}")\n',
        '    # Page 03 and Page 05 intentionally preserve distinct canonical PSI definitions.\n'
        '    # Block C: frozen-model Validation-2016 -> OOT-2017 prediction PSI.\n'
        '    # Block E: downstream annual score-monitoring PSI under the monitoring contract.\n'
        '    page03 = _json(parsed_json, "/public/data/page-03-model-decisioning.json")\n'
        '    page05 = _json(parsed_json, "/public/data/page-05-monitoring.json")\n'
        '    ranking = page03.get("ranking", {}) if isinstance(page03.get("ranking"), dict) else {}\n'
        '    score_drift = page05.get("score_drift", {}) if isinstance(page05.get("score_drift"), dict) else {}\n'
        '    p03_psi = ranking.get("prediction_psi")\n'
        '    p05_psi = score_drift.get("annual_psi")\n'
        '    expected_p03_psi = 0.003663365071810081\n'
        '    expected_p05_psi = 0.0036352563867260096\n'
        '    if not isinstance(p03_psi, (int, float)) or not math.isclose(float(p03_psi), expected_p03_psi, rel_tol=0.0, abs_tol=1e-15):\n'
        '        failures.append(f"page-03: Block C prediction PSI lineage mismatch {p03_psi!r}")\n'
        '    if ranking.get("prediction_psi_basis") != "Validation-2016_to_OOT-2017":\n'
        '        failures.append(f"page-03: Block C prediction PSI basis mismatch {ranking.get(\'prediction_psi_basis\')!r}")\n'
        '    if not isinstance(p05_psi, (int, float)) or not math.isclose(float(p05_psi), expected_p05_psi, rel_tol=0.0, abs_tol=1e-15):\n'
        '        failures.append(f"page-05: Block E annual monitoring PSI lineage mismatch {p05_psi!r}")\n'
        '    if isinstance(p03_psi, (int, float)) and isinstance(p05_psi, (int, float)) and math.isclose(float(p03_psi), float(p05_psi), rel_tol=0.0, abs_tol=1e-15):\n'
        '        failures.append("page-03/page-05: distinct PSI definitions were incorrectly collapsed")\n',
    )

    model_html = ROOT / "model-decisioning" / "index.html"
    replace_once(model_html, '<small>Prediction PSI</small>', '<small>Block C Prediction PSI</small>')
    replace_once(
        model_html,
        '<p>Risk ordering remains clean while aggregate score-distribution shift is low.</p>',
        '<p>Block C C9 measures Validation-2016 → OOT-2017 prediction shift; Block E monitoring recomputes annual score PSI under a separate downstream monitoring contract.</p>',
    )

    print("Final numeric-lineage patch applied")


if __name__ == "__main__":
    main()
