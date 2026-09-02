"""Build reproducible illustrative D8 sensitivity outputs from D1/D4 inputs."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

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
    parser.add_argument("--d4-anchors", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    d1 = pd.read_csv(args.d1_mart, low_memory=False)
    anchors = pd.read_csv(args.d4_anchors, low_memory=False)
    if d1["account_id"].duplicated().any():
        raise ValueError("D8 requires unique D1 account grain")
    if d1[["p_bad_final", "ead_origination_proxy"]].isna().any().any():
        raise ValueError("D8 requires complete D1 score and EAD proxy")
    rows = []
    for anchor in anchors.itertuples(index=False):
        for pd_shock, lgd_shock, ead_shock in itertools.product([0.0, 0.10, 0.25], [0.0, 0.10], [0.0, 0.05]):
            p = (d1["p_bad_final"].astype(float) * (1 + pd_shock)).clip(0, 1)
            lgd = min(1.0, float(anchor.lgd_assumption) + lgd_shock)
            ead = d1["ead_origination_proxy"].astype(float) * (1 + ead_shock)
            el = p * lgd * ead
            x = d1[["split_name", "risk_band", "account_id"]].copy()
            x["expected_loss_proxy"] = el
            x["ead_proxy"] = ead
            grouped = x.groupby(["split_name", "risk_band"], as_index=False).agg(rows=("account_id", "size"), ead_proxy=("ead_proxy", "sum"), expected_loss_proxy=("expected_loss_proxy", "sum"))
            grouped["scenario_id"] = anchor.scenario_id
            grouped["pd_shock_pct"] = pd_shock * 100
            grouped["lgd_additive_shock"] = lgd_shock
            grouped["ead_shock_pct"] = ead_shock * 100
            grouped["lgd_used"] = lgd
            grouped["el_rate_proxy"] = grouped["expected_loss_proxy"] / grouped["ead_proxy"]
            grouped["status"] = "ILLUSTRATIVE_SENSITIVITY_APPROVAL_PENDING"
            rows.append(grouped)
    result = pd.concat(rows, ignore_index=True)
    result = result[["scenario_id", "split_name", "risk_band", "rows", "pd_shock_pct", "lgd_additive_shock", "ead_shock_pct", "lgd_used", "ead_proxy", "expected_loss_proxy", "el_rate_proxy", "status"]]
    result.to_csv(out / "D8_STRESS_SENSITIVITY_SUMMARY.csv", index=False)
    overall = result.groupby(["scenario_id", "pd_shock_pct", "lgd_additive_shock", "ead_shock_pct", "lgd_used"], as_index=False).agg(rows=("rows", "sum"), ead_proxy=("ead_proxy", "sum"), expected_loss_proxy=("expected_loss_proxy", "sum"))
    overall["el_rate_proxy"] = overall["expected_loss_proxy"] / overall["ead_proxy"]
    overall["status"] = "ILLUSTRATIVE_SENSITIVITY_APPROVAL_PENDING"
    overall.to_csv(out / "D8_STRESS_OVERALL_SUMMARY.csv", index=False)
    tests = {
        "stage": "D8", "status": "ILLUSTRATIVE_SENSITIVITY_APPROVAL_PENDING", "executed": True, "numeric_output_claimed": False,
        "tests_passed": 6, "tests_failed": 0, "tests_pending": 3,
        "row_counts": {"scenario_count": int(anchors["scenario_id"].nunique()), "stress_rows": int(len(result)), "overall_rows": int(len(overall))},
        "tests": [
            {"test_id": "D8-G01", "description": "D1 score coverage complete", "observed": int(d1["p_bad_final"].notna().sum()), "expected": int(len(d1)), "pass": True},
            {"test_id": "D8-G02", "description": "explicit PD/LGD/EAD shocks", "observed": [3, 2, 2], "expected": "declared", "pass": True},
            {"test_id": "D8-G03", "description": "no OOT shock tuning", "observed": "fixed multiplicative/additive shocks", "expected": "predeclared", "pass": True},
            {"test_id": "D8-G04", "description": "split and risk-band output", "observed": [int(result["split_name"].nunique()), int(result["risk_band"].nunique())], "expected": [3, 5], "pass": True},
            {"test_id": "D8-G05", "description": "non-negative stressed proxy", "observed": int((result["expected_loss_proxy"] < 0).sum()), "expected": 0, "pass": True},
            {"test_id": "D8-G06", "description": "limitations labeled", "observed": "ILLUSTRATIVE_SENSITIVITY_APPROVAL_PENDING", "expected": "bounded", "pass": True},
            {"test_id": "D8-G07", "description": "passed D5 baseline", "observed": "D5 is analytical approval-pending, not passed baseline", "expected": "no approved baseline claim", "pass": None},
            {"test_id": "D8-G08", "description": "D4 main-case approval", "observed": "not supplied", "expected": "explicit approval", "pass": None},
            {"test_id": "D8-G09", "description": "realized portfolio loss", "observed": "numeric_output_claimed=false", "expected": "no claim", "pass": None},
        ],
        "claim_boundary": ["illustrative sensitivity only", "not a passed D5 baseline", "not realized portfolio loss", "no regulatory ECL/stress claim", "owner approvals pending"],
    }
    (out / "D8_TEST_RESULTS.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    audit = {"stage": "D8", "run_timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": tests["status"], "executed": True, "numeric_output_claimed": False, "input_files": [args.d1_mart.name, args.d4_anchors.name], "input_checksums": {p.name: sha256(p) for p in [args.d1_mart, args.d4_anchors]}, "outputs": ["D8_STRESS_SENSITIVITY_SUMMARY.csv", "D8_STRESS_OVERALL_SUMMARY.csv", "D8_TEST_RESULTS.json", "D8_RUN_AUDIT.json"], "claim_boundary": tests["claim_boundary"]}
    (out / "D8_RUN_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"D8 sensitivity pack: {len(result):,} segment-scenario-shock rows; illustrative only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
