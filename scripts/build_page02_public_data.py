"""Validate and canonicalize the frozen Page 02 public portfolio-risk contract.

Page 02 already contains the sanitized Block B aggregate snapshot. This builder
is deliberately non-row-level: it validates the frozen public contract and
rewrites it deterministically without reconstructing borrower data.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "data" / "page-02-portfolio-risk.json"


def check(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def build():
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    portfolio = payload["portfolio"]

    check(portfolio["accounts"] == 1_347_681, "Unexpected governed portfolio population")
    check(portfolio["good_accounts"] + portfolio["bad_accounts"] == portfolio["accounts"], "GOOD + BAD != portfolio total")
    check(abs(portfolio["observed_bad_rate"] - portfolio["bad_accounts"] / portfolio["accounts"]) < 1e-12, "Observed BAD rate does not reconcile")
    check(sum(row["accounts"] for row in payload["splits"]) == portfolio["accounts"], "Split population mismatch")
    check(sum(row["accounts"] for row in payload["annual"]) == portfolio["accounts"], "Annual population mismatch")
    check(payload["governance"]["checks"]["duplicate_account_ids"] == 0, "Duplicate account IDs detected in frozen contract")
    check(payload["governance"]["checks"]["population_loss"] == 0, "Population loss detected")
    check(payload["governance"]["checks"]["unassigned_splits"] == 0, "Unassigned split detected")
    check(payload["meta"]["claim_scope"] == "DESCRIPTIVE_NON_CAUSAL_OBSERVED_FINAL_RESOLUTION", "Page 02 claim scope changed")
    check(payload["meta"]["public_safe"] is True, "Page 02 must remain public-safe")
    check("not verified 12-month PD" in payload["interpretation"]["outcome"], "PD claim boundary missing")
    check("not observed regulatory EAD" in payload["interpretation"]["exposure"], "EAD claim boundary missing")

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Validated and canonicalized {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
