"""Create the final Block D review manifest without falsely locking the block."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--d1-audit", type=Path, required=True)
    parser.add_argument("--d2-audit", type=Path, required=True)
    parser.add_argument("--d4-audit", type=Path, required=True)
    parser.add_argument("--d5-audit", type=Path, required=True)
    parser.add_argument("--d6-audit", type=Path, required=True)
    parser.add_argument("--d7-audit", type=Path, required=True)
    parser.add_argument("--d8-audit", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    audits = {stage: json.loads(path.read_text(encoding="utf-8")) for stage, path in [("D1", args.d1_audit), ("D2", args.d2_audit), ("D4", args.d4_audit), ("D5", args.d5_audit), ("D6", args.d6_audit), ("D7", args.d7_audit), ("D8", args.d8_audit)]}
    block_dir = out.parent
    full_review_qa = block_dir / "BLOCK_D_FULL_REVIEW_QA.json"
    d1_band_contract = block_dir / "D1_RISK_SCORE_MART" / "risk_band_contract.json"
    approval_decision_pack = out / "BLOCK_D_APPROVAL_DECISION_PACK.md"
    approval_register = out / "D9_APPROVAL_REGISTER.json"
    approval_validation = out / "D9_APPROVAL_VALIDATION.json"
    manifest = {
        "stage": "D9", "status": "NOT_LOCKED_REVIEW_REQUIRED", "run_timestamp_utc": datetime.now(timezone.utc).isoformat(), "executed": True, "numeric_output_claimed": False,
        "upstream_status": {"D0": "PASS", "D1": audits["D1"].get("status"), "D2": audits["D2"].get("status"), "D3": "PASS_WITH_LIMITATIONS", "D4": audits["D4"].get("status"), "D5": audits["D5"].get("status"), "D6": audits["D6"].get("status"), "D7": audits["D7"].get("status"), "D8": audits["D8"].get("status")},
        "closure_checks": {
            "D0_governance": "PASS", "D1_score_mart": "PASS_WITH_LIMITATIONS", "D2_governed_bridge": "PASS_WITH_LIMITATIONS", "D3_ead": "PASS_WITH_LIMITATIONS", "D4_main_case_approval": "PENDING", "D5_expected_loss": "ANALYTICAL_ONLY_APPROVAL_PENDING", "D6_owner_policy": "PENDING", "D7_pricing_adequacy": "DESCRIPTIVE_ONLY", "D8_stress": "ILLUSTRATIVE_ONLY", "owner_signoff": "PENDING",
        },
        "required_follow_up": ["Record explicit D4 main-case LGD and timing approval", "Record D5 analytical proxy acceptance boundary", "Record D6 action thresholds and override owner approval", "Record D7 pricing cost/fee assumptions if profitability is required", "Record D8 approved baseline/shock policy", "Record data/model/risk owner sign-off", "Then rerun final gate QA and update D9 only after review"],
        "evidence_checksums": {
            **{stage: {"file": path.relative_to(block_dir).as_posix(), "sha256": sha256(path)} for stage, path in [("D1", args.d1_audit), ("D2", args.d2_audit), ("D4", args.d4_audit), ("D5", args.d5_audit), ("D6", args.d6_audit), ("D7", args.d7_audit), ("D8", args.d8_audit)]},
            "D1_BAND_CONTRACT": {"file": d1_band_contract.relative_to(block_dir).as_posix(), "sha256": sha256(d1_band_contract)},
            "FULL_REVIEW_QA": {"file": full_review_qa.name, "sha256": sha256(full_review_qa)},
            "APPROVAL_DECISION_PACK": {"file": str(approval_decision_pack.relative_to(block_dir)), "sha256": sha256(approval_decision_pack)},
            "APPROVAL_REGISTER": {"file": str(approval_register.relative_to(block_dir)).replace("\\", "/"), "sha256": sha256(approval_register)},
            "APPROVAL_VALIDATION": {"file": str(approval_validation.relative_to(block_dir)).replace("\\", "/"), "sha256": sha256(approval_validation)},
        },
        "claim_boundary": ["Block D is not locked", "D5/D8 values are analytical scenario outputs only", "no production decision policy", "no pricing profitability result", "no regulatory PD/LGD/EAD/ECL claim"],
    }
    (out / "D9_CLOSURE_REVIEW_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("D9 closure manifest: NOT_LOCKED_REVIEW_REQUIRED; owner approvals pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
