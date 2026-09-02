"""Run a deterministic audit of the public D3 EAD contract."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "block-d" / "D3_EAD_FRAMEWORK" / "D3_EAD_CONTRACT.md"
OUTPUT = ROOT / "block-d" / "D3_EAD_FRAMEWORK" / "D3_CONTRACT_AUDIT.json"


def main() -> int:
    text = CONTRACT.read_text(encoding="utf-8")
    checks = [
        ("D3-C01", "declared status is pass with limitations", "PASS_WITH_LIMITATIONS" in text),
        ("D3-C02", "origination proxy is loan_amnt", "ead_origination_proxy = loan_amnt" in text),
        ("D3-C03", "proxy is explicitly non-regulatory", "not a regulatory EAD estimate" in text),
        ("D3-C04", "contract formula defines P, r, PMT and balance_k", all(token in text for token in ["P   =", "r   =", "PMT =", "balance_k ="])),
        ("D3-C05", "zero-rate branch is specified", "If `r = 0`" in text),
        ("D3-C06", "balances are floored and bounded by term", "Balances are floored at zero" in text and "beyond contractual term" in text),
        ("D3-C07", "required scenario points and 60-month rule are specified", all(token in text for token in ["0, 6, 12, 18, 24, 36 and 48 months", "60-month contracts"])),
        ("D3-C08", "declared source scope and no score insertion are explicit", "331,865-row accepted/pricing source fallback" in text and "`p_bad_final` is not inserted" in text),
    ]
    test_rows = [{"test_id": test_id, "description": description, "pass": passed} for test_id, description, passed in checks]
    passed = sum(1 for row in test_rows if row["pass"])
    result = {
        "stage": "D3",
        "audit_type": "contract_control_review",
        "run_date": date.today().isoformat(),
        "status": "PASS_WITH_LIMITATIONS" if passed == len(test_rows) else "FAIL",
        "executed": True,
        "numeric_output_claimed": False,
        "tests_passed": passed,
        "tests_failed": len(test_rows) - passed,
        "tests": test_rows,
        "scope": "public contract and declared-run metadata; not a recalculation of private EAD schedules",
        "claim_boundary": "loan_amnt is an origination exposure proxy; not regulatory EAD",
        "source_file": "D3_EAD_CONTRACT.md",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"D3 CONTRACT AUDIT {result['status']} — {passed}/{len(test_rows)} checks pass")
    return 0 if result["status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
