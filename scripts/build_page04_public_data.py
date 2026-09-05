"""Build the public, aggregate-only data contract for Block F Page 04.

The inputs are canonical Block D aggregates. No row-level data, private marts,
model binaries, or predictions are copied into the public contract.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK_D = ROOT / "block-d"
OUT = ROOT / "public" / "data" / "page-04-loss-policy-stress.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> float:
    return float(value)


def integer(value: str) -> int:
    return int(value)


def main() -> None:
    d4 = read_json(BLOCK_D / "D4_MAIN_CASE_DECISION.json")
    d5 = read_csv(BLOCK_D / "D5_EXPECTED_LOSS" / "D5_PORTFOLIO_EL_SUMMARY.csv")
    d6_validation = read_csv(BLOCK_D / "D6_DECISION_POLICY" / "D6_POLICY_SCENARIOS.csv")
    d6_oot = read_csv(BLOCK_D / "D6_DECISION_POLICY" / "D6_OOT_POLICY_REPLAY.csv")
    d7_scope = read_json(BLOCK_D / "D7_PRICING" / "D7_SCOPE_DECISION.json")
    d7_pricing = read_csv(BLOCK_D / "D7_PRICING" / "D7_DESCRIPTIVE_PRICING_SUMMARY.csv")
    d8_stress = read_csv(BLOCK_D / "D8_STRESS" / "D8_FINAL_STRESS_RESULTS.csv")
    d8_reverse = read_csv(BLOCK_D / "D8_STRESS" / "D8_REVERSE_STRESS_RESULTS.csv")
    d8_timing = read_csv(BLOCK_D / "D8_STRESS" / "D8_EAD_TIMING_SENSITIVITY.csv")

    expected_policies = {"GROWTH", "BALANCED", "CONSERVATIVE"}
    expected_stress = {"BASE", "MILD", "ADVERSE", "SEVERE"}
    if {row["scenario"] for row in d6_validation} != expected_policies:
        raise ValueError("D6 validation scenario set changed")
    if {row["scenario"] for row in d6_oot} != expected_policies:
        raise ValueError("D6 OOT scenario set changed")
    if {row["scenario"] for row in d8_stress} != expected_stress:
        raise ValueError("D8 stress scenario set changed")
    if len(d8_reverse) != 2:
        raise ValueError("D8 reverse-stress contract must contain A and B")

    central_rows = [
        row for row in d5
        if row["scenario_id"] == "LGD_CENTRAL_Q50" and row["ead_scenario"] == "EAD_0M"
    ]
    if len(central_rows) != 1:
        raise ValueError("Central D5 row is not unique")
    central_row = central_rows[0]
    central = {
        "accounts": integer(central_row["account_count"]),
        "mean_p_bad_final": number(central_row["mean_p_bad_final"]),
        "lgd_scenario": "LGD_CENTRAL_Q50",
        "lgd": number(central_row["lgd"]),
        "ead_scenario": "EAD_0M",
        "ead_proxy": number(central_row["total_ead_proxy"]),
        "expected_loss_proxy": number(central_row["total_expected_loss_proxy"]),
        "el_rate": number(central_row["portfolio_el_rate"]),
        "claim_boundary": "ANALYTICAL_EXPECTED_LOSS_PROXY",
    }
    assert central["accounts"] == 310_066
    assert abs(central["ead_proxy"] - 4_469_158_350.0) < 1e-6
    assert abs(central["expected_loss_proxy"] - 526_752_273.6678772) < 1e-6
    assert abs(central["el_rate"] - 0.11786386438240148) < 1e-12

    lgd_order = [
        ("LGD_LOW_SEVERITY_Q25", "Q25_LOW_SEVERITY"),
        ("LGD_CENTRAL_Q50", "Q50_CENTRAL"),
        ("LGD_ADVERSE_Q75", "Q75_ADVERSE"),
        ("LGD_SEVERE_Q90", "Q90_SEVERE"),
    ]
    lgd_sensitivity = []
    for source_id, public_id in lgd_order:
        row = next(row for row in d5 if row["scenario_id"] == source_id and row["ead_scenario"] == "EAD_0M")
        lgd_sensitivity.append({
            "scenario": public_id,
            "lgd": number(row["lgd"]),
            "el_proxy": number(row["total_expected_loss_proxy"]),
            "el_rate": number(row["portfolio_el_rate"]),
        })

    timing = []
    for row in d8_timing:
        timing.append({
            "timing": row["timing_scenario"].replace("EAD_", ""),
            "ead_proxy": number(row["total_ead_proxy"]),
            "el_proxy_q50": number(row["total_expected_loss_proxy"]),
            "el_rate_q50": number(row["el_rate"]),
        })
    timing.sort(key=lambda row: int(row["timing"].replace("M", "")))

    validation_by_name = {row["scenario"]: row for row in d6_validation}
    oot_by_name = {row["scenario"]: row for row in d6_oot}
    policies = []
    for name in ["GROWTH", "BALANCED", "CONSERVATIVE"]:
        validation = validation_by_name[name]
        oot = oot_by_name[name]
        route_sum = sum(number(oot[field]) for field in ("approval_rate", "review_rate", "decline_rate"))
        if abs(route_sum - 1.0) >= 1e-9:
            raise ValueError(f"OOT route shares do not reconcile for {name}")
        policies.append({
            "scenario": name,
            "validation": {
                "basis": validation["validation_basis"],
                "selection_rule": validation["selection_rule"],
                "approve_cutoff": number(validation["approve_cutoff"]),
                "decline_cutoff": number(validation["decline_cutoff"]),
                "approval_rate": number(validation["approval_rate"]),
                "review_rate": number(validation["review_rate"]),
                "decline_rate": number(validation["decline_rate"]),
                "approved_el_rate": number(validation["approved_el_rate"]),
                "bad_capture_rate": number(validation["historical_bad_capture_rate"]),
            },
            "oot": {
                "split": oot["split"],
                "approved_accounts": integer(oot["approved_accounts"]),
                "review_accounts": integer(oot["review_accounts"]),
                "declined_accounts": integer(oot["declined_accounts"]),
                "approval_rate": number(oot["approval_rate"]),
                "review_rate": number(oot["review_rate"]),
                "decline_rate": number(oot["decline_rate"]),
                "approved_bad_rate": number(oot["historical_approved_bad_rate"]),
                "review_bad_rate": number(oot["historical_review_bad_rate"]),
                "declined_bad_rate": number(oot["historical_declined_bad_rate"]),
                "bad_capture_rate": number(oot["historical_bad_capture_rate"]),
                "good_route_out_rate": number(oot["historical_good_route_out_rate"]),
                "approved_ead": number(oot["approved_ead"]),
                "review_ead": number(oot["review_ead"]),
                "declined_ead": number(oot["declined_ead"]),
                "approved_el_proxy": number(oot["approved_expected_loss_proxy"]),
                "review_el_proxy": number(oot["review_expected_loss_proxy"]),
                "declined_el_proxy": number(oot["declined_expected_loss_proxy"]),
                "approved_el_rate": number(oot["approved_el_rate"]),
                "review_el_rate": number(oot["review_el_rate"]),
                "declined_el_rate": number(oot["declined_el_rate"]),
            },
        })

    pricing_keys = {1: "D01 / R1", 5: "D05 / R3", 8: "D08 / R4", 10: "D10 / R5"}
    pricing = []
    for row in d7_pricing:
        decile = integer(row["risk_decile"])
        if decile in pricing_keys and not any(item["decile"] == decile for item in pricing):
            pricing.append({
                "decile": decile,
                "label": pricing_keys[decile],
                "accounts": integer(row["account_count"]),
                "mean_rate": number(row["mean_int_rate"]),
                "mean_el_rate": number(row["mean_expected_loss_rate"]),
                "diagnostic_spread": number(row["mean_diagnostic_spread"]),
            })
    pricing.sort(key=lambda item: item["decile"])

    stress = []
    for row in d8_stress:
        stress.append({
            "scenario": row["scenario"],
            "mean_p_bad": number(row["mean_p_bad"]),
            "lgd": number(row["lgd_used"]),
            "ead_proxy": number(row["total_ead_proxy"]),
            "el_proxy": number(row["total_expected_loss_proxy"]),
            "el_rate": number(row["el_rate"]),
        })
    stress.sort(key=lambda row: ["BASE", "MILD", "ADVERSE", "SEVERE"].index(row["scenario"]))
    if [row["el_rate"] for row in stress] != sorted(row["el_rate"] for row in stress):
        raise ValueError("Stress EL rates are not monotonic")
    base_rate = stress[0]["el_rate"]
    for row in stress:
        row["delta_vs_base_el_rate"] = row["el_rate"] - base_rate
        row["delta_vs_base_el_proxy"] = row["el_proxy"] - stress[0]["el_proxy"]

    reverse_stress = [{
        "id": row["reverse_stress"],
        "question": row["question"],
        "required_mean_p_bad": number(row["required_mean_p_bad"]),
        "relative_mean_p_increase": number(row["relative_mean_p_increase"]),
        "target_el_rate": number(row["target_el_rate"]),
        "scenario_version": row["scenario_version"],
    } for row in d8_reverse]

    payload = {
        "meta": {
            "project": "CRD.PI",
            "page": "loss-policy-stress",
            "version": "F-P04-CONTENT-1.0",
            "block_d_status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
            "population_scope": "matched_scored_310066",
            "production_authorized": False,
            "regulatory_compliance_claimed": False,
            "public_safe": True,
            "sources": [
                "block-d/D4_MAIN_CASE_DECISION.json",
                "block-d/D5_EXPECTED_LOSS/D5_PORTFOLIO_EL_SUMMARY.csv",
                "block-d/D6_DECISION_POLICY/D6_POLICY_SCENARIOS.csv",
                "block-d/D6_DECISION_POLICY/D6_OOT_POLICY_REPLAY.csv",
                "block-d/D7_PRICING/D7_SCOPE_DECISION.json",
                "block-d/D7_PRICING/D7_DESCRIPTIVE_PRICING_SUMMARY.csv",
                "block-d/D8_STRESS/D8_FINAL_STRESS_RESULTS.csv",
                "block-d/D8_STRESS/D8_REVERSE_STRESS_RESULTS.csv",
                "block-d/D8_STRESS/D8_EAD_TIMING_SENSITIVITY.csv",
            ],
        },
        "central_case": central,
        "lgd_sensitivity": lgd_sensitivity,
        "ead_timing": timing,
        "policies": policies,
        "pricing": {
            "scope": d7_scope["selected_scope"],
            "profitability_claim_allowed": False,
            "int_rate_recursion_caveat": bool(d7_scope["int_rate_recursion_caveat"]),
            "diagnostics": pricing,
        },
        "stress": stress,
        "reverse_stress": reverse_stress,
        "controls": {
            "policy_selection_basis": "Validation-2016",
            "policy_replay_split": "historical OOT 2017",
            "oot_threshold_tuning": False,
            "stress_version": "D8-FINAL-1.1",
            "claim_boundary": "ANALYTICAL STRESS SENSITIVITY; NOT FORECAST; NOT REGULATORY",
            "row_level_data_shipped": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote Page 04 public contract: {central['accounts']:,} accounts, {len(policies)} policies, {len(stress)} stress scenarios")


if __name__ == "__main__":
    main()
