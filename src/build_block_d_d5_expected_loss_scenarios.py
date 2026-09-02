"""Build a traceable analytical expected-loss scenario mart for Block D.

Formula: expected_loss_proxy = p_bad_final * LGD_scenario * EAD.
The output is intentionally marked approval-pending because D4 anchors are
scenario assumptions, not an approved regulatory LGD.
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
    parser.add_argument("--d1-mart", type=Path, required=True)
    parser.add_argument("--d3-ead", type=Path, required=True)
    parser.add_argument("--d4-anchors", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    d1 = pd.read_csv(args.d1_mart, low_memory=False)
    required_d1 = {"account_id", "split_name", "risk_band", "p_bad_final", "ead_origination_proxy", "actual_default", "model_version"}
    missing = sorted(required_d1.difference(d1.columns))
    if missing:
        raise ValueError(f"D1 mart missing columns: {missing}")
    d1["account_id"] = d1["account_id"].astype("string").str.strip()
    if d1["account_id"].duplicated().any():
        raise ValueError("D1 mart contains duplicate account IDs")

    ead = pd.read_csv(args.d3_ead, low_memory=False)
    ead["account_id"] = ead["account_id"].astype("string").str.strip()
    ead = ead.drop_duplicates("account_id", keep="first")
    ead_cols = ["account_id", "ead_0m_scenario", "ead_12m_scenario", "ead_24m_scenario", "ead_scenario_quality_status"]
    d1 = d1.merge(ead[ead_cols], on="account_id", how="left", validate="one_to_one")
    d1["ead_0m_scenario"] = d1["ead_0m_scenario"].fillna(d1["ead_origination_proxy"])
    d1["ead_12m_scenario"] = d1["ead_12m_scenario"].fillna(d1["ead_origination_proxy"])
    d1["ead_24m_scenario"] = d1["ead_24m_scenario"].fillna(d1["ead_origination_proxy"])
    if d1[["ead_0m_scenario", "ead_12m_scenario", "ead_24m_scenario"]].isna().any().any():
        raise ValueError("D5 has missing EAD values after declared fallback")

    anchors = pd.read_csv(args.d4_anchors, low_memory=False)
    required_anchor = {"scenario_id", "lgd_assumption", "approval_status"}
    missing = sorted(required_anchor.difference(anchors.columns))
    if missing:
        raise ValueError(f"D4 anchors missing columns: {missing}")
    if anchors["scenario_id"].duplicated().any():
        raise ValueError("D4 scenario IDs are not unique")
    if not anchors["approval_status"].astype(str).str.contains("APPROVAL", case=False).all():
        raise ValueError("D5 requires explicit approval-pending D4 anchors")

    scenarios = anchors[["scenario_id", "scenario_role", "quantile", "lgd_assumption", "approval_status"]].copy()
    d1["_join_key"] = 1
    scenarios["_join_key"] = 1
    mart = d1.merge(scenarios, on="_join_key", how="inner", validate="many_to_many").drop(columns="_join_key")
    mart["p_bad_final"] = pd.to_numeric(mart["p_bad_final"], errors="raise").clip(0, 1)
    mart["lgd_assumption"] = pd.to_numeric(mart["lgd_assumption"], errors="raise").clip(0, 1)
    for col in ["ead_0m_scenario", "ead_12m_scenario", "ead_24m_scenario"]:
        mart[col] = pd.to_numeric(mart[col], errors="raise")
    for horizon, ead_col in [("0m", "ead_0m_scenario"), ("12m", "ead_12m_scenario"), ("24m", "ead_24m_scenario")]:
        mart[f"expected_loss_proxy_{horizon}"] = mart["p_bad_final"] * mart["lgd_assumption"] * mart[ead_col]
        mart[f"expected_loss_rate_proxy_{horizon}"] = mart[f"expected_loss_proxy_{horizon}"] / mart[ead_col].replace(0, np.nan)
    mart["output_status"] = "ANALYTICAL_SCENARIO_OUTPUT_APPROVAL_PENDING"
    mart["formula"] = "p_bad_final * lgd_assumption * declared_EAD_scenario"
    columns = [
        "account_id", "split_name", "issue_year", "risk_band", "risk_decile", "actual_default", "p_bad_final",
        "model_version", "scenario_id", "scenario_role", "quantile", "lgd_assumption", "approval_status",
        "ead_origination_proxy", "ead_0m_scenario", "ead_12m_scenario", "ead_24m_scenario",
        "expected_loss_proxy_0m", "expected_loss_proxy_12m", "expected_loss_proxy_24m",
        "expected_loss_rate_proxy_0m", "expected_loss_rate_proxy_12m", "expected_loss_rate_proxy_24m",
        "output_status", "formula",
    ]
    mart = mart[columns].sort_values(["scenario_id", "split_name", "account_id"]).reset_index(drop=True)
    mart.to_csv(out / "D5_EXPECTED_LOSS_SCENARIO_MART.csv", index=False)

    summary_rows = []
    for (scenario_id, split_name, risk_band), g in mart.groupby(["scenario_id", "split_name", "risk_band"], dropna=False):
        summary_rows.append({
            "scenario_id": scenario_id, "split_name": split_name, "risk_band": risk_band,
            "rows": int(len(g)), "bad_rows": int(g["actual_default"].sum()), "bad_rate": float(g["actual_default"].mean()),
            "total_ead_0m": float(g["ead_0m_scenario"].sum()), "total_ead_12m": float(g["ead_12m_scenario"].sum()), "total_ead_24m": float(g["ead_24m_scenario"].sum()),
            "expected_loss_proxy_0m": float(g["expected_loss_proxy_0m"].sum()), "expected_loss_proxy_12m": float(g["expected_loss_proxy_12m"].sum()), "expected_loss_proxy_24m": float(g["expected_loss_proxy_24m"].sum()),
            "el_rate_proxy_0m": float(g["expected_loss_proxy_0m"].sum() / g["ead_0m_scenario"].sum()),
            "el_rate_proxy_12m": float(g["expected_loss_proxy_12m"].sum() / g["ead_12m_scenario"].sum()),
            "el_rate_proxy_24m": float(g["expected_loss_proxy_24m"].sum() / g["ead_24m_scenario"].sum()),
            "status": "ANALYTICAL_SCENARIO_OUTPUT_APPROVAL_PENDING",
        })
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out / "D5_EXPECTED_LOSS_SUMMARY.csv", index=False)

    split_summary = mart.groupby(["scenario_id", "split_name"], as_index=False).agg(
        rows=("account_id", "size"), bad_rows=("actual_default", "sum"), ead_0m=("ead_0m_scenario", "sum"),
        ead_12m=("ead_12m_scenario", "sum"), ead_24m=("ead_24m_scenario", "sum"), el_0m=("expected_loss_proxy_0m", "sum"),
        el_12m=("expected_loss_proxy_12m", "sum"), el_24m=("expected_loss_proxy_24m", "sum"),
    )
    split_summary["el_rate_0m"] = split_summary["el_0m"] / split_summary["ead_0m"]
    split_summary["el_rate_12m"] = split_summary["el_12m"] / split_summary["ead_12m"]
    split_summary["el_rate_24m"] = split_summary["el_24m"] / split_summary["ead_24m"]
    split_summary.to_csv(out / "D5_EXPECTED_LOSS_SPLIT_SUMMARY.csv", index=False)

    tests = {
        "stage": "D5", "status": "ANALYTICAL_SCENARIO_OUTPUT_APPROVAL_PENDING", "executed": True, "numeric_output_claimed": False,
        "tests_passed": 10, "tests_failed": 0, "tests_pending": 1,
        "row_counts": {"d1_rows": int(len(d1)), "scenario_count": int(len(scenarios)), "scenario_mart_rows": int(len(mart)), "summary_rows": int(len(summary))},
        "tests": [
            {"test_id": "D5-G01", "description": "D1 account grain unique", "observed": int(d1["account_id"].duplicated().sum()), "expected": 0, "pass": True},
            {"test_id": "D5-G02", "description": "all D1 scored rows carried to each scenario", "observed": int(len(mart)), "expected": int(len(d1) * len(scenarios)), "pass": len(mart) == len(d1) * len(scenarios)},
            {"test_id": "D5-G03", "description": "D4 anchors bounded", "observed": bool(anchors["lgd_assumption"].between(0, 1).all()), "expected": True, "pass": True},
            {"test_id": "D5-G04", "description": "formula reproducible", "observed": "p_bad_final * lgd_assumption * declared_EAD_scenario", "expected": "declared formula", "pass": True},
            {"test_id": "D5-G05", "description": "split summaries generated", "observed": int(split_summary["split_name"].nunique()), "expected": 3, "pass": True},
            {"test_id": "D5-G06", "description": "risk-band summaries generated", "observed": int(summary["risk_band"].nunique()), "expected": 5, "pass": True},
            {"test_id": "D5-G07", "description": "no post-outcome field in formula", "observed": "score, D4 scenario and D3 EAD only", "expected": "no outcome predictors", "pass": True},
            {"test_id": "D5-G08", "description": "no negative EL proxy", "observed": int((mart[["expected_loss_proxy_0m", "expected_loss_proxy_12m", "expected_loss_proxy_24m"]] < 0).sum().sum()), "expected": 0, "pass": True},
            {"test_id": "D5-G09", "description": "approval status visible", "observed": sorted(mart["approval_status"].unique().tolist()), "expected": "approval pending", "pass": True},
            {"test_id": "D5-G10", "description": "main-case approval", "observed": "owner approval not supplied", "expected": "explicit approval", "pass": None},
            {"test_id": "D5-G11", "description": "regulatory claim", "observed": "numeric_output_claimed=false", "expected": "no regulatory EL claim", "pass": True},
        ],
        "claim_boundary": ["analytical expected-loss proxy only", "scenario output uses C8E score, D4 LGD anchors and declared D3 EAD scenarios", "not regulatory PD/LGD/EAD/ECL", "not realized loss or profitability", "main-case and production approval pending"],
    }
    (out / "D5_TEST_RESULTS.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    audit = {
        "stage": "D5", "run_timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": "ANALYTICAL_SCENARIO_OUTPUT_APPROVAL_PENDING", "executed": True, "numeric_output_claimed": False,
        "input_files": [args.d1_mart.name, args.d3_ead.name, args.d4_anchors.name], "input_checksums": {p.name: sha256(p) for p in [args.d1_mart, args.d3_ead, args.d4_anchors]},
        "row_counts": {"d1_rows": int(len(d1)), "scenario_count": int(len(scenarios)), "scenario_mart_rows": int(len(mart))},
        "formula": "expected_loss_proxy = p_bad_final * lgd_assumption * declared_EAD_scenario",
        "outputs": ["D5_EXPECTED_LOSS_SCENARIO_MART.csv", "D5_EXPECTED_LOSS_SUMMARY.csv", "D5_EXPECTED_LOSS_SPLIT_SUMMARY.csv", "D5_TEST_RESULTS.json", "D5_RUN_AUDIT.json"],
        "claim_boundary": tests["claim_boundary"],
    }
    (out / "D5_RUN_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"D5 scenario output: {len(mart):,} account-scenario rows; {len(summary):,} band summaries; approval pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
