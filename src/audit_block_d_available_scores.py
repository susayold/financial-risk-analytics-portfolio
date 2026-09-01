"""Audit the persisted Block C score artifacts available for Block D.

This check is deliberately narrower than the D1 opening gate. It validates the
score files themselves, without implying that they are joined to the governed
core, Development population, pricing fields, or loss evidence.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED = {
    "Validation": {"rows": 83_664, "score": "final_prediction"},
    "OOT": {"rows": 44_221, "score": "prediction"},
}


def auc_rank(y: pd.Series, score: pd.Series) -> float:
    """Compute ROC-AUC from ranks, including average ranks for ties."""
    y_arr = y.astype(int).to_numpy()
    score_arr = score.astype(float).to_numpy()
    ranks = pd.Series(score_arr).rank(method="average").to_numpy()
    positives = y_arr == 1
    n_pos = int(positives.sum())
    n_neg = int((~positives).sum())
    if n_pos == 0 or n_neg == 0:
        raise ValueError("ROC-AUC is undefined with a single target class")
    return float((ranks[positives].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def inspect(path: Path, split: str) -> tuple[dict, set[str]]:
    df = pd.read_parquet(path)
    expected_score = EXPECTED[split]["score"]
    required = {"account_id", "actual_default", expected_score}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"{split}: missing required columns: {missing}")

    ids = df["account_id"].astype("string")
    target = pd.to_numeric(df["actual_default"], errors="coerce")
    score = pd.to_numeric(df[expected_score], errors="coerce")
    checks = {
        "account_id_non_null": bool(ids.notna().all()),
        "account_id_non_blank": bool((ids.str.strip().str.len() > 0).all()),
        "account_id_unique": bool(~ids.duplicated().any()),
        "target_non_null": bool(target.notna().all()),
        "target_binary": bool(set(target.dropna().astype(int).unique()).issubset({0, 1})),
        "score_non_null": bool(score.notna().all()),
        "score_finite": bool(np.isfinite(score.to_numpy(dtype=float)).all()),
        "score_in_unit_interval": bool(score.between(0.0, 1.0, inclusive="both").all()),
        "row_count_matches_expected": len(df) == EXPECTED[split]["rows"],
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"{split}: failed checks: {failed}")

    return {
        "path": path.name,
        "rows": int(len(df)),
        "bad_count": int(target.sum()),
        "bad_rate": float(target.mean()),
        "account_id_unique": True,
        "score_column": expected_score,
        "score_min": float(score.min()),
        "score_max": float(score.max()),
        "score_mean": float(score.mean()),
        "score_median": float(score.median()),
        "roc_auc_recomputed": auc_rank(target, score),
        "checks": checks,
    }, set(ids.dropna().tolist())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--oot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mart-output", type=Path, required=False)
    args = parser.parse_args()

    validation, validation_ids = inspect(args.validation, "Validation")
    oot, oot_ids = inspect(args.oot, "OOT")
    overlap = sorted(validation_ids.intersection(oot_ids))
    result = {
        "stage": "D1_SCORE_ARTIFACT_AUDIT",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_WITH_LIMITATIONS" if not overlap else "FAIL",
        "scope": "Persisted C8E Validation 2016 and C9 OOT 2017 score files only",
        "limitations": [
            "No Development score artifact is present in the audited inputs",
            "No governed-core join or full-population coverage is tested",
            "No pricing or loss/recovery bridge is tested",
        ],
        "splits": {"Validation": validation, "OOT": oot},
        "cross_split": {
            "account_id_overlap_count": len(overlap),
            "account_id_overlap_sample": overlap[:10],
            "target_class_total": validation["bad_count"] + oot["bad_count"],
            "row_total": validation["rows"] + oot["rows"],
        },
    }
    if args.mart_output:
        val_df = pd.read_parquet(args.validation)[
            ["account_id", "actual_default", "final_prediction"]
        ].rename(columns={"final_prediction": "p_bad_final"})
        val_df.insert(0, "split_name", "Validation")
        oot_df = pd.read_parquet(args.oot)[
            ["account_id", "actual_default", "prediction"]
        ].rename(columns={"prediction": "p_bad_final"})
        oot_df.insert(0, "split_name", "OOT")
        score_mart = pd.concat([val_df, oot_df], ignore_index=True)
        score_mart["model_version"] = "C8E_RICH_BUREAU_CATBOOST_79F"
        score_mart["economics_version"] = "D0.1"
        score_mart["population_scope"] = "P1_C8E_PERSISTED_SCORE_ARTIFACTS_ONLY"
        score_mart["pricing_match_flag"] = pd.NA
        score_mart["loss_evidence_match_flag"] = pd.NA
        score_mart = score_mart[
            [
                "account_id",
                "split_name",
                "actual_default",
                "p_bad_final",
                "model_version",
                "economics_version",
                "population_scope",
                "pricing_match_flag",
                "loss_evidence_match_flag",
            ]
        ].sort_values(["split_name", "account_id"])
        args.mart_output.parent.mkdir(parents=True, exist_ok=True)
        score_mart.to_csv(args.mart_output, index=False)
        result["materialized_score_only_mart"] = {
            "file": args.mart_output.name,
            "rows": int(len(score_mart)),
            "columns": score_mart.columns.tolist(),
            "pricing_match_flag": "UNASSESSED",
            "loss_evidence_match_flag": "UNASSESSED",
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        "D1 score artifact audit: "
        f"Validation {validation['rows']:,}, OOT {oot['rows']:,}, "
        f"overlap {len(overlap)}, status {result['status']}"
    )
    return 0 if result["status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
