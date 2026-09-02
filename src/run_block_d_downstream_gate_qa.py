"""Validate that D5-D9 remain safely gated while upstream evidence is pending."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGES = ["D5", "D6", "D7", "D8", "D9"]


def main() -> int:
    register = ROOT / "block-d" / "D5_D9_GATE_QA.json"
    payload = json.loads(register.read_text(encoding="utf-8"))
    errors: list[str] = []
    if payload.get("status") != "CONTROLLED_HOLD":
        errors.append("register status is not CONTROLLED_HOLD")
    if payload.get("numeric_outputs_claimed") is not False:
        errors.append("numeric_outputs_claimed must be false")
    for stage in STAGES:
        status = payload.get("stages", {}).get(stage)
        if status != "CONTROLLED_HOLD":
            errors.append(f"{stage} status is {status!r}")
        stage_file = ROOT / "block-d" / {
            "D5": "D5_EXPECTED_LOSS",
            "D6": "D6_DECISION_POLICY",
            "D7": "D7_PRICING",
            "D8": "D8_STRESS",
            "D9": "D9_CLOSURE",
        }[stage] / f"{stage}_GATE_RESULTS.json"
        stage_payload = json.loads(stage_file.read_text(encoding="utf-8"))
        if stage_payload.get("executed") is not False:
            errors.append(f"{stage} executed flag must be false")
        if stage_payload.get("numeric_output_claimed") is not False:
            errors.append(f"{stage} numeric_output_claimed must be false")
    for key, value in payload.get("control_checks", {}).items():
        if value != "PASS":
            errors.append(f"control check {key} is {value!r}")
    if errors:
        print("D5-D9 DOWNSTREAM GATE QA FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("D5-D9 DOWNSTREAM GATE QA PASS — 5 stages controlled as HOLD")
    print("No downstream numeric or production claim is present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
