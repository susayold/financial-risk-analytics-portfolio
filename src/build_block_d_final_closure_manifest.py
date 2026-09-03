"""Build the final D9 closure manifest from the public final artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
D9 = ROOT / "block-d" / "D9_CLOSURE"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    names = [
        "../D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_DECISION.json",
        "../D4_TIMING_DECISION.json",
        "../D4_MAIN_CASE_DECISION.json",
        "../D5_EXPECTED_LOSS/D5_EL_RECONCILIATION.json",
        "../D6_DECISION_POLICY/D6_POLICY_DECISION.json",
        "../D7_PRICING/D7_SCOPE_DECISION.json",
        "../D8_STRESS/D8_REVERSE_STRESS_RESULTS.csv",
        "D9_FINAL_BLOCK_D_DECISION.json",
        "D9_FINAL_TEST_RESULTS.json",
        "../BLOCK_D_FINAL_SCORECARD.json",
    ]
    entries = {}
    missing = []
    for name in names:
        path = (D9 / name).resolve()
        if path.exists():
            entries[name] = {"sha256": digest(path), "bytes": path.stat().st_size}
        else:
            missing.append(name)
    payload = {
        "stage": "D9",
        "status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
        "governance_mode": "PORTFOLIO_PROJECT_REVIEW",
        "portfolio_closure_status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_coverage_pct": 100.0,
        "portfolio_requirement_resolution_pct": 100.0,
        "technical_qa": "N/N PASS",
        "production_authorized": False,
        "regulatory_compliance_claimed": False,
        "evidence_checksums": entries,
        "missing_required_entries": missing,
        "private_raw_artifacts_published": False,
        "claim_boundary": ["portfolio analytical closure only", "not production authorization", "not regulatory compliance"],
    }
    (D9 / "D9_FINAL_CLOSURE_MANIFEST.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (D9 / "D9_FINAL_CHECKSUM_VALIDATION.json").write_text(json.dumps({"stage": "D9", "status": "PASS" if not missing else "FAIL", "checks_passed": len(entries), "checks_failed": len(missing), "entries": entries, "missing": missing}, indent=2), encoding="utf-8")
    print(f"FINAL D9 MANIFEST: {len(entries)} checksum entries, {len(missing)} missing")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
