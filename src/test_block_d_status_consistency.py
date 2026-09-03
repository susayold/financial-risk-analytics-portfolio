"""Check that current Block D status sources agree."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
FINAL = "CLOSED_WITH_LIMITATIONS_PORTFOLIO"


def main() -> int:
    final = json.loads((BLOCK / "D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json").read_text(encoding="utf-8"))
    score = json.loads((BLOCK / "BLOCK_D_PLAN_COMPLETION_SCORECARD.json").read_text(encoding="utf-8"))
    qa = json.loads((BLOCK / "BLOCK_D_FULL_REVIEW_QA.json").read_text(encoding="utf-8"))
    reg = json.loads((BLOCK / "D9_CLOSURE/D9_APPROVAL_REGISTER.json").read_text(encoding="utf-8"))
    sources = {"final_decision": final.get("status"), "scorecard": score.get("status"), "qa": qa.get("overall_block_status"), "register": reg.get("status")}
    errors = []
    if any(v != FINAL for v in sources.values()):
        errors.append(f"current statuses disagree: {sources}")
    if final.get("production_authorized") is not False or final.get("regulatory_compliance_claimed") is not False:
        errors.append("final decision has an unsafe authorization/claim flag")
    result = {"test": "block_d_status_consistency", "status": "PASS" if not errors else "FAIL", "sources": sources, "errors": errors}
    (BLOCK / "BLOCK_D_STATUS_CONSISTENCY.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"STATUS CONSISTENCY {result['status']}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
