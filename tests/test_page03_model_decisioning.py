import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data" / "page-03-model-decisioning.json"
FEATURES = ROOT / "public" / "data" / "model-feature-contract-79f.json"
HTML = ROOT / "model-decisioning" / "index.html"
JS = ROOT / "assets" / "crdpi-model.js"


def test_page03_model_and_population_contract():
    page = json.loads(DATA.read_text(encoding="utf-8"))
    contract = page["contract"]
    population = page["population"]
    assert contract["model_id"] if "model_id" in contract else page["meta"]["model_id"]
    assert contract["feature_count"] == 79
    assert contract["score"] == "p_bad_final"
    assert contract["target_semantics"] == "final_resolution_bad_good"
    assert contract["development_only_fit"] is True
    assert contract["oot_early_stopping"] is False
    assert contract["post_oot_specification_changes"] == 0
    assert population["scored_accounts"] == 310066
    assert sum(split["rows"] for split in population["splits"]) == 310066
    assert population["cross_split_id_overlap"] == 0
    assert population["splits"][0]["rows"] == 182181
    assert population["splits"][1]["rows"] == 83664
    assert population["splits"][2]["rows"] == 44221


def test_page03_metrics_and_frozen_decisioning():
    page = json.loads(DATA.read_text(encoding="utf-8"))
    oot = page["oot"]
    assert abs(oot["roc_auc"] - 0.8557777504539299) < 1e-12
    assert abs(oot["ks"] - 0.5625094217238796) < 1e-12
    assert abs(oot["pr_auc"] - 0.5489091154627448) < 1e-12
    assert abs(oot["brier"] - 0.08362492875360526) < 1e-12
    assert abs(oot["log_loss"] - 0.2843152586611653) < 1e-12
    assert oot["bootstrap_reps"] == 300
    assert page["calibration"]["status"] == "AMBER_WATCH"
    assert abs(page["calibration"]["slope"] - 1.2507071775766894) < 1e-12
    assert page["ranking"]["decile_monotonic_violations"] == 0
    assert page["ranking"]["decile_spearman"] == 1.0
    assert page["decisioning"]["split_level_qcut_allowed"] is False
    assert page["decisioning"]["risk_bands"] == ["R1 VERY_LOW", "R2 LOW", "R3 MEDIUM", "R4 HIGH", "R5 VERY_HIGH"]


def test_page03_feature_contract_and_public_boundary():
    page = json.loads(DATA.read_text(encoding="utf-8"))
    feature_data = json.loads(FEATURES.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    assert feature_data["feature_count"] == 79
    assert len(feature_data["canonical_order"]) == 79
    assert len(set(feature_data["canonical_order"])) == 79
    assert sum(group["count"] for group in page["feature_groups"]) == 79
    assert page["red_team"]["used_as_champion"] is False
    assert page["reproducibility"]["oot_replay_rows"] == 44221
    assert page["reproducibility"]["oot_replay_max_abs_diff"] == 0.0
    assert "Not verified regulatory PD" in html
    assert "not production readiness" in html
    assert "not automatic approval or decline rules" in html
    assert "Higher accuracy is not useful" in html
    assert "../public/data/page-03-model-decisioning.json" in js
    assert "../public/data/model-feature-contract-79f.json" in js
    assert "Page queued in Block F" not in html
    assert "qcut(" not in html + js
    for forbidden in ["The model predicts 12-month PD.", "The model is production ready.", "All 1.35M loans were scored by C8E."]:
        assert forbidden not in html
