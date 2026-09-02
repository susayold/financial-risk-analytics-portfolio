"""Build the machine-readable Block D plan-completion scorecard."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
TRACEABILITY = BLOCK / "BLOCK_D_PLAN_TRACEABILITY.md"
QA = BLOCK / "BLOCK_D_FULL_REVIEW_QA.json"
MANIFEST = BLOCK / "D9_CLOSURE" / "D9_CLOSURE_REVIEW_MANIFEST.json"
OUTPUT = BLOCK / "BLOCK_D_PLAN_COMPLETION_SCORECARD.json"

STAGES = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"]
SCORE_BY_STATUS = {
    "PASS": 100.0,
    "PASS_WITH_LIMITATIONS": 90.0,
    "BRIDGE_RECONCILED_APPROVAL_PENDING": 75.0,
    "CONTROLLED_HOLD": 60.0,
    "NOT_LOCKED_REVIEW_REQUIRED": 50.0,
}


def traceability_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in TRACEABILITY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        for stage in STAGES:
            if cells[0].startswith(stage + " "):
                statuses[stage] = cells[3].split(";", 1)[0].strip()
    return statuses


def build_scorecard() -> dict:
    trace_status = traceability_statuses()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    qa = json.loads(QA.read_text(encoding="utf-8"))
    trace_status["D9"] = manifest.get("status", "")

    missing = [stage for stage in STAGES if stage not in trace_status]
    unknown = {stage: trace_status[stage] for stage in STAGES if trace_status.get(stage) not in SCORE_BY_STATUS and stage not in missing}
    if missing or unknown:
        raise ValueError(f"Cannot build scorecard; missing={missing} unknown={unknown}")

    rows = [
        {
            "stage": stage,
            "recorded_status": trace_status[stage],
            "execution_coverage_pct": 100.0,
            "closure_readiness_pct": SCORE_BY_STATUS[trace_status[stage]],
        }
        for stage in STAGES
    ]
    closure = round(sum(row["closure_readiness_pct"] for row in rows) / len(rows), 1)
    return {
        "scorecard_name": "block_d_plan_completion",
        "scorecard_version": "1.1",
        "run_date": date.today().isoformat(),
        "scope": "controlled analytical review; no production or regulatory claim",
        "execution_coverage_pct": 100.0 if manifest.get("executed") is True and len(rows) == 10 else 0.0,
        "closure_readiness_pct": closure,
        "technical_qa": {
            "status": qa.get("status"),
            "checks_passed": qa.get("checks_passed"),
            "checks_failed": qa.get("checks_failed"),
        },
        "d9": {
            "manifest_status": manifest.get("status"),
            "numeric_output_claimed": manifest.get("numeric_output_claimed"),
            "checksum_entries": len(manifest.get("evidence_checksums", {})),
        },
        "stages": rows,
        "conversion": SCORE_BY_STATUS,
        "formula": "simple average of the ten closure_readiness_pct values",
        "caveat": "This is a management readiness conversion, not a model metric or approval.",
    }


def main() -> int:
    result = build_scorecard()
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"BLOCK D SCORECARD: execution={result['execution_coverage_pct']:.1f}% "
        f"closure_readiness={result['closure_readiness_pct']:.1f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
