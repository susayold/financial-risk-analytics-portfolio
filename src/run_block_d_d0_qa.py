"""Deterministic D0 governance QA; no raw data or private paths required."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
D0 = ROOT / "block-d" / "D0_GOVERNANCE_CONTRACT"


def load_json(name: str):
    return json.loads((D0 / name).read_text(encoding="utf-8"))


def main() -> int:
    snapshot = load_json("D0_UPSTREAM_SNAPSHOT.json")
    populations = load_json("D0_POPULATION_CONTRACT.json")
    tests = load_json("D0_TEST_RESULTS.json")
    with (D0 / "D0_DATA_ROLE_MATRIX.csv").open(encoding="utf-8", newline="") as f:
        roles = list(csv.DictReader(f))
    with (D0 / "D0_ASSUMPTION_REGISTER.csv").open(encoding="utf-8", newline="") as f:
        assumptions = list(csv.DictReader(f))

    assert snapshot["frozen_model"]["model_id"] == "C8E_RICH_BUREAU_CATBOOST_79F"
    assert snapshot["target"]["score_name"] == "p_bad_final"
    assert snapshot["target"]["fixed_horizon_12m_verified"] is False
    assert snapshot["population"]["full_core_accounts"] == 1347681
    assert snapshot["population"]["c8e_matched_validation"] == 83664
    assert snapshot["population"]["c8e_matched_oot_2017"] == 44221
    assert len(populations["populations"]) == 5
    assert {p["population_id"] for p in populations["populations"]} == {
        "P0_FULL_CORE", "P1_C8E_MATCHED", "P2_PRICING_MATCHED",
        "P3_LOSS_EVIDENCE_MATCHED", "P4_DEFAULTED_LOSS_SAMPLE",
    }
    required = {
        "account_id", "issue_d", "actual_default", "p_bad_final", "loan_amnt",
        "term", "int_rate", "installment", "sub_grade", "grade_derived",
        "recoveries", "collection_recovery_fee", "total_rec_prncp", "total_pymnt",
        "last_pymnt_d", "last_fico_range_high", "last_fico_range_low",
    }
    assert required <= {r["field_name"] for r in roles}
    forbidden = {
        "recoveries", "collection_recovery_fee", "total_rec_prncp", "total_pymnt",
        "last_pymnt_d", "last_fico_range_high", "last_fico_range_low",
    }
    by_name = {r["field_name"]: r for r in roles}
    assert all(by_name[name]["model_input_allowed"].lower() == "false" for name in forbidden)
    assert all(r["source_reference"] and r["rationale"] for r in assumptions)
    assert tests["status"] == "PASS" and tests["tests_passed"] == 10 and tests["tests_failed"] == 0
    print("D0 QA PASS — 10/10 governance gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
