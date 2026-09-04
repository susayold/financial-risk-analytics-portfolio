"""Build the public-safe Block F Page 03 data contracts.

Only aggregate model evidence and feature names/order are published. The model
binary, account IDs, row-level predictions, and the private 79F matrix remain out
of the public site.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public" / "data"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str) -> float:
    return float(row[key])


def integer(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def row_for(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    for row in rows:
        if row[key] == value:
            return row
    raise ValueError(f"Missing canonical row: {key}={value}")


def main() -> None:
    overview = read_json(ROOT / "public" / "data" / "page-01-overview.json")
    manifest = read_json(ROOT / "block-e" / "E1_MART_79F" / "E1_MART_79F_RECONCILIATION.json")
    d1_bands = read_json(ROOT / "block-d" / "D1_RISK_SCORE_MART" / "risk_band_contract.json")
    replay = read_json(ROOT / "block-e" / "E3_FEATURE_DRIFT" / "C9_79F_SCORE_REPLAY_SUMMARY.json")
    discrimination = read_csv(ROOT / "block-e" / "E5_PERFORMANCE_CALIBRATION" / "discrimination_monitor.csv")
    calibration = read_csv(ROOT / "block-e" / "E5_PERFORMANCE_CALIBRATION" / "calibration_monitor.csv")
    quarterly = read_csv(ROOT / "block-e" / "E5_PERFORMANCE_CALIBRATION" / "quarterly_performance.csv")

    feature_order = manifest["feature_order"]
    if len(feature_order) != 79 or len(set(feature_order)) != 79:
        raise ValueError("Frozen feature contract is not exactly 79 unique features")
    if manifest["row_count"] != 310066 or manifest["unique_account_key_count"] != 310066:
        raise ValueError("E1 scored population reconciliation failed")
    if manifest["split_counts"] != {"Development": 182181, "Validation": 83664, "OOT": 44221}:
        raise ValueError("E1 split counts do not match the frozen population contract")

    validation = row_for(discrimination, "window_id", "Validation")
    oot = row_for(discrimination, "window_id", "OOT")
    oot_calibration = row_for(calibration, "window_id", "OOT")
    oot_quarters = [row for row in quarterly if row["window_id"].startswith("2017Q")]
    quarterly_auc_range = max(number(row, "roc_auc") for row in oot_quarters) - min(number(row, "roc_auc") for row in oot_quarters)

    group_specs = [
        ("A", "Core Borrower & Loan Signals", 8),
        ("B", "Basic Bureau & Account Structure", 8),
        ("C", "Derived Risk Ratios", 8),
        ("D", "Affordability, Loan Structure & Credit History", 14),
        ("E", "Rich Bureau Raw Signals", 33),
        ("F", "Rich Bureau Derived Signals", 8),
    ]
    feature_groups = []
    features = []
    cursor = 0
    for group_id, group_name, count in group_specs:
        names = feature_order[cursor : cursor + count]
        feature_groups.append({"id": group_id, "name": group_name, "count": count, "features": names[:4]})
        for offset, name in enumerate(names, start=1):
            features.append({
                "canonical_index": cursor + offset,
                "name": name,
                "group_id": group_id,
                "group_name": group_name,
                "role_exception": name in {"term", "installment", "int_rate"},
            })
        cursor += count
    if cursor != 79:
        raise ValueError("Feature family counts do not sum to 79")

    population_splits = [
        {"split": "Development", "rows": 182181, "bad": 28967, "bad_rate": 0.159001, "role": "model fitting / frozen replay"},
        {"split": "Validation 2016", "rows": 83664, "bad": 14190, "bad_rate": 0.169557, "roc_auc": number(validation, "roc_auc"), "role": "reference validation"},
        {"split": "OOT 2017", "rows": 44221, "bad": 5892, "bad_rate": number(oot, "bad_rate"), "roc_auc": number(oot, "roc_auc"), "role": "one-time untouched holdout"},
    ]

    page = {
        "meta": {
            "project": "CRD.PI",
            "page": "model-decisioning",
            "schema": "crd.pi.page-03-model-decisioning.v1",
            "model_id": "C8E_RICH_BUREAU_CATBOOST_79F",
            "block_c_status": "PASS_WITH_MONITORING",
            "analytical_handoff": "block-e-v1.0.2-final",
            "production_authorized": False,
            "regulatory_compliance_claimed": False,
            "public_safe": True,
        },
        "contract": {
            "champion": "C8E Rich Bureau CatBoost",
            "algorithm": "CatBoost",
            "feature_count": 79,
            "score": "p_bad_final",
            "target": "actual_default",
            "target_semantics": "final_resolution_bad_good",
            "development_only_fit": True,
            "oot_early_stopping": False,
            "oot_hyperparameter_tuning": False,
            "post_oot_specification_changes": 0,
            "historical_shadow_2018_used": False,
            "automatic_retraining": False,
            "feature_order_frozen": True,
        },
        "population": {
            "scored_accounts": manifest["row_count"],
            "cross_split_id_overlap": 0,
            "full_governed_core_accounts": overview["portfolio"]["resolved_loans"],
            "scope_note": "C8E performance applies to the matched enriched scored population, not all governed core accounts.",
            "splits": population_splits,
        },
        "validation": {
            "recorded_roc_auc": 0.821938,
            "reproduced_roc_auc": number(validation, "roc_auc"),
            "reproduction_difference": 0.000025,
            "rows": integer(validation, "account_count"),
            "bad": integer(validation, "bad_count"),
        },
        "oot": {
            "rows": integer(oot, "account_count"),
            "bad": integer(oot, "bad_count"),
            "observed_bad_rate": number(oot, "bad_rate"),
            "roc_auc": number(oot, "roc_auc"),
            "gini": number(oot, "gini"),
            "ks": number(oot, "ks"),
            "pr_auc": number(oot, "pr_auc"),
            "brier": number(oot, "brier"),
            "log_loss": number(oot, "logloss"),
            "bootstrap_reps": overview["model"]["bootstrap_reps"],
            "auc_ci_low": overview["model"]["bootstrap_auc_ci_low"],
            "auc_ci_high": overview["model"]["bootstrap_auc_ci_high"],
            "quarterly_auc_range": quarterly_auc_range,
        },
        "calibration": {
            "intercept": number(oot_calibration, "intercept"),
            "slope": number(oot_calibration, "slope"),
            "mean_prediction": number(oot_calibration, "mean_prediction"),
            "observed_bad_rate": number(oot_calibration, "observed_bad_rate"),
            "absolute_gap": number(oot_calibration, "calibration_gap"),
            "status": "AMBER_WATCH",
            "watch_reason": "The slope narrowly misses the project's 1.25 GREEN upper boundary.",
        },
        "ranking": {
            "decile_monotonic_violations": 0,
            "decile_spearman": 1.0,
            "prediction_psi": 0.003663365,
            "interpretation": "Risk ordering remains clean while aggregate score-distribution shift is low.",
        },
        "decisioning": {
            "score": "p_bad_final",
            "decile_low": "D01",
            "decile_high": "D10",
            "cutpoint_reference": d1_bands["cutpoint_reference_population"],
            "cutpoint_direction": d1_bands["cutpoint_direction"],
            "split_level_qcut_allowed": False,
            "risk_bands": [f"{band['band']} {band['label']}" for band in d1_bands["band_contract"]],
            "band_note": "Risk bands are reporting labels only, not automatic approval or decline rules.",
        },
        "feature_groups": feature_groups,
        "red_team": {
            "benchmark_auc_gt": 0.95,
            "classification": "LEAKAGE_RED_TEAM_BENCHMARK",
            "signals": ["post-origination information", "latest-FICO", "late-fee / post-outcome information"],
            "used_as_champion": False,
        },
        "reproducibility": {
            "feature_coverage": "79/79",
            "scored_rows": manifest["row_count"],
            "oot_replay_rows": integer(oot, "account_count"),
            "oot_replay_max_abs_diff": 0.0,
            "oot_replay_spearman": 1.0,
            "p_bad_replay_identity": manifest["p_bad_replay_identity"],
            "interpretation": "Exact historical score replay without retraining; this does not prove production readiness or future performance.",
        },
        "feature_role_exception": "term, installment and int_rate enter the frozen Block C model under a documented versioned re-contract; the exception remains audit-visible.",
        "monitoring_cross_link": "Block E later identifies a historical RED monthly calibration-slope event; the full alert workflow belongs on Monitoring.",
    }

    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "page-03-model-decisioning.json").write_text(json.dumps(page, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PUBLIC / "model-feature-contract-79f.json").write_text(json.dumps({
        "schema": "crd.pi.model-feature-contract-79f.v1",
        "model_id": page["meta"]["model_id"],
        "feature_count": len(features),
        "canonical_order": feature_order,
        "features": features,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote Page 03 public contracts: 79 features, 310066 scored rows")


if __name__ == "__main__":
    main()
