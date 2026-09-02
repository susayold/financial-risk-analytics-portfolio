"""Build source-level LGD scenario anchors from the governed D2 loss evidence.

This is deliberately a scenario-only fallback. It does not join risk scores and
does not claim empirical LGD for the C8E matched population until the D2 bridge
to the governed core is available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--loss-evidence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    usecols = [
        "account_id", "issue_d", "loan_status", "funded_amnt",
        "retrospective_lgd_proxy_raw", "retrospective_lgd_proxy_model",
        "loss_data_quality_status",
    ]
    df_raw = pd.read_csv(args.loss_evidence, usecols=usecols, low_memory=False)
    # Remove only exact full-row duplicates so duplicated evidence cannot
    # overweight the severity distribution. Conflicting non-exact account rows
    # are not silently resolved.
    exact_duplicate_rows = int(df_raw.duplicated().sum())
    duplicate_account_id_groups = int(
        df_raw.loc[df_raw.duplicated("account_id", keep=False), "account_id"].nunique()
    )
    df = df_raw.drop_duplicates().copy()
    if df["account_id"].duplicated().any():
        raise ValueError("non-exact duplicate account_id rows remain after exact dedup")
    model_lgd = pd.to_numeric(df["retrospective_lgd_proxy_model"], errors="coerce")
    raw_lgd = pd.to_numeric(df["retrospective_lgd_proxy_raw"], errors="coerce")
    valid = model_lgd.notna() & model_lgd.between(0, 1, inclusive="both")
    if not bool(valid.all()):
        raise ValueError("D4 input contains missing/out-of-range model LGD values")

    x = df.loc[valid].copy()
    x["lgd_proxy"] = model_lgd.loc[valid].astype(float)
    x["issue_year"] = pd.to_datetime(x["issue_d"], format="%b-%Y", errors="coerce").dt.year
    if x["issue_year"].isna().any():
        raise ValueError("D4 input contains unparseable issue_d values")

    # Block C excludes the 2018 shadow cohort from primary claims because of
    # final-resolution/truncation concerns. Keep it monitor-only here too.
    reference = x.loc[x["issue_year"] <= 2017].copy()
    monitor_2018 = x.loc[x["issue_year"] == 2018].copy()
    if reference.empty:
        raise ValueError("D4 scenario reference population is empty")
    quantiles = {"q25": 0.25, "q50": 0.50, "q75": 0.75, "q90": 0.90}
    q = reference["lgd_proxy"].quantile(list(quantiles.values()))
    scenarios = pd.DataFrame([
        {
            "scenario_id": "LGD_LOW_SEVERITY_Q25",
            "scenario_role": "benign anchor",
            "quantile": 0.25,
            "lgd_assumption": float(q.loc[0.25]),
            "source_scope": "account-grain deduplicated BAD rows, issue_year <= 2017",
            "approval_status": "REVIEW_REQUIRED_BRIDGE_PENDING",
        },
        {
            "scenario_id": "LGD_CENTRAL_Q50",
            "scenario_role": "central anchor",
            "quantile": 0.50,
            "lgd_assumption": float(q.loc[0.50]),
            "source_scope": "account-grain deduplicated BAD rows, issue_year <= 2017",
            "approval_status": "REVIEW_REQUIRED_BRIDGE_PENDING",
        },
        {
            "scenario_id": "LGD_ADVERSE_Q75",
            "scenario_role": "adverse anchor",
            "quantile": 0.75,
            "lgd_assumption": float(q.loc[0.75]),
            "source_scope": "account-grain deduplicated BAD rows, issue_year <= 2017",
            "approval_status": "REVIEW_REQUIRED_BRIDGE_PENDING",
        },
        {
            "scenario_id": "LGD_SEVERE_Q90",
            "scenario_role": "severe anchor",
            "quantile": 0.90,
            "lgd_assumption": float(q.loc[0.90]),
            "source_scope": "account-grain deduplicated BAD rows, issue_year <= 2017",
            "approval_status": "REVIEW_REQUIRED_BRIDGE_PENDING",
        },
    ])
    scenarios.to_csv(out / "lgd_scenario_anchors.csv", index=False)

    summary = pd.DataFrame([{
        "scope": "SOURCE_LEVEL_BAD_EVIDENCE",
        "source_rows": int(len(df)),
        "source_rows_before_exact_dedup": int(len(df_raw)),
        "exact_duplicate_rows_removed": exact_duplicate_rows,
        "exact_duplicate_account_id_groups": duplicate_account_id_groups,
        "usable_lgd_rows": int(len(x)),
        "valid_rows": int((x["loss_data_quality_status"] == "VALID").sum()),
        "clipped_rows": int((x["loss_data_quality_status"] == "CLIPPED_FOR_MODELING").sum()),
        "scenario_reference_end_year": 2017,
        "scenario_reference_rows": int(len(reference)),
        "scenario_reference_valid_rows": int((reference["loss_data_quality_status"] == "VALID").sum()),
        "scenario_reference_clipped_rows": int((reference["loss_data_quality_status"] == "CLIPPED_FOR_MODELING").sum()),
        "monitor_only_2018_rows": int(len(monitor_2018)),
        "mean_lgd": float(reference["lgd_proxy"].mean()),
        "median_lgd": float(reference["lgd_proxy"].median()),
        "q25_lgd": float(q.loc[0.25]),
        "q75_lgd": float(q.loc[0.75]),
        "q90_lgd": float(q.loc[0.90]),
        "raw_lgd_below_zero_rows": int((raw_lgd.loc[valid] < 0).sum()),
        "governed_core_expected_rows": 1347681,
        "governed_core_bridge_rows": None,
        "bridge_status": "PENDING_GOVERNED_ID_LIST",
        "claim_status": "SCENARIO_ONLY_NOT_C8E_EMPIRICAL_LGD",
    }])
    summary.to_csv(out / "lgd_scenario_summary.csv", index=False)

    by_year = x.groupby("issue_year", as_index=False).agg(
        bad_rows=("account_id", "size"),
        mean_lgd=("lgd_proxy", "mean"),
        median_lgd=("lgd_proxy", "median"),
        q25_lgd=("lgd_proxy", lambda s: s.quantile(0.25)),
        q75_lgd=("lgd_proxy", lambda s: s.quantile(0.75)),
        q90_lgd=("lgd_proxy", lambda s: s.quantile(0.90)),
    )
    by_year["issue_year"] = by_year["issue_year"].astype(int)
    by_year.to_csv(out / "lgd_by_issue_year.csv", index=False)

    tests = {
        "stage": "D4",
        "status": "REVIEW_REQUIRED_BRIDGE_PENDING",
        "scope": "ACCOUNT_GRAIN_DEDUPLICATED_BAD_EVIDENCE_SCENARIO_ONLY",
        "tests_passed": 8,
        "tests_failed": 0,
        "tests_pending": 2,
        "row_counts": {
            "source_rows": int(len(df)),
            "source_rows_before_exact_dedup": int(len(df_raw)),
            "exact_duplicate_rows_removed": exact_duplicate_rows,
            "usable_lgd_rows": int(len(x)),
        },
        "tests": [
            {"test_id": "D4-G01", "description": "input schema present", "pass": True},
            {"test_id": "D4-G02", "description": "LGD values bounded to [0,1]", "observed": int(valid.sum()), "pass": True},
            {"test_id": "D4-G03", "description": "scenario quantile anchors generated", "observed": 4, "pass": True},
            {"test_id": "D4-G04", "description": "temporal source-level diagnostics generated", "observed": int(len(by_year)), "pass": True},
            {"test_id": "D4-G05", "description": "2018 truncation guard applied", "observed": f"anchors use issue_year <= 2017; {len(monitor_2018):,} 2018 rows monitor-only", "pass": True},
            {"test_id": "D4-G06", "description": "no p_bad_final used", "observed": "D4 input contains loss evidence only", "pass": True},
            {"test_id": "D4-G07", "description": "scenario approval is not implied", "observed": "all anchors REVIEW_REQUIRED_BRIDGE_PENDING", "pass": True},
            {"test_id": "D4-G10", "description": "exact duplicate evidence does not overweight anchors", "observed": f"removed {exact_duplicate_rows:,} exact duplicate rows; {duplicate_account_id_groups:,} duplicate account groups; no non-exact duplicates remain", "pass": True},
            {"test_id": "D4-G08", "description": "governed-core ID bridge", "observed": "not materialized", "pass": None},
            {"test_id": "D4-G09", "description": "C8E score-to-loss empirical linkage", "observed": "not materialized", "pass": None},
        ],
        "fallback_boundary": "Do not present these anchors as empirical LGD for C8E or combine with p_bad_final until D1/D2 bridges pass.",
    }
    (out / "D4_TEST_RESULTS.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")

    audit = {
        "stage": "D4",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "REVIEW_REQUIRED_BRIDGE_PENDING",
        "input_files": [args.loss_evidence.name],
        "input_checksums": {args.loss_evidence.name: sha256(args.loss_evidence)},
        "upstream_versions": {"block_a": "LOCKED", "block_b": "LOCKED", "block_c": "CLOSED_WITH_MONITORING"},
        "model_versions": {"frozen_risk_model": "C8E_RICH_BUREAU_CATBOOST_79F"},
        "assumption_version": "D4-SCENARIO-0.1",
        "random_seed": 42,
        "row_counts": {
            "source_rows": int(len(df)),
            "source_rows_before_exact_dedup": int(len(df_raw)),
            "exact_duplicate_rows_removed": exact_duplicate_rows,
            "usable_lgd_rows": int(len(x)),
        },
        "tests_passed": 8,
        "tests_failed": 0,
        "tests_pending": 2,
        "outputs": ["lgd_scenario_anchors.csv", "lgd_scenario_summary.csv", "lgd_by_issue_year.csv", "D4_TEST_RESULTS.json", "D4_RUN_AUDIT.json"],
        "claim_boundary": ["account-grain deduplicated source-level scenario anchors only", "not empirical C8E LGD", "no p_bad_final join", "governed-core bridge pending", "no regulatory LGD"],
    }
    (out / "D4_RUN_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"D4 generated {len(scenarios)} scenario anchors from {len(x):,} source-level BAD rows; bridge pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
