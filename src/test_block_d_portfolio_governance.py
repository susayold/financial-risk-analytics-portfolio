"""Nine explicit governance-mode regression tests required by the D closure plan."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from validate_block_d_owner_decisions import validate_register


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "block-d" / "D9_CLOSURE" / "D9_PORTFOLIO_PROJECT_OWNER_DECISIONS.json"


def portfolio_record() -> dict:
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def run() -> list[dict]:
    base = portfolio_record()
    results = []
    bad = copy.deepcopy(base); bad["governance_mode"] = "UNKNOWN"
    results.append({"id": "T1", "pass": validate_register(bad)["validation_status"] == "INVALID"})
    bad = copy.deepcopy(base); bad["production_authorized"] = True
    results.append({"id": "T2", "pass": validate_register(bad)["validation_status"] == "INVALID"})
    bad = copy.deepcopy(base); bad["owner_signoff"]["data_owner"]["status"] = "APPROVED"
    results.append({"id": "T3", "pass": validate_register(bad)["validation_status"] == "INVALID"})
    bad = copy.deepcopy(base); del bad["decisions"]["D4_main_case_lgd"]
    results.append({"id": "T4", "pass": validate_register(bad)["validation_status"] == "INVALID"})
    ready = copy.deepcopy(base)
    ready["decision_owner_name"] = "test-owner"
    ready["decision_date"] = "2026-09-03"
    for item in ready["decisions"].values():
        item["decision_owner"] = "test-owner"
        item["decision_date"] = "2026-09-03"
    results.append({"id": "T5", "pass": validate_register(ready)["validation_status"] == "PORTFOLIO_VALID"})
    inst = {"stage": "D9", "governance_mode": "INSTITUTIONAL_PRODUCTION", "production_authorized": True}
    for role in ("model_owner", "risk_owner"):
        inst.setdefault("institutional_owners", {})[role] = {"name": "x", "date": "2026-09-03", "reference": "x"}
    results.append({"id": "T6", "pass": "institutional_owners.data_owner" in " ".join(validate_register(inst)["errors"])})
    inst = {"stage": "D9", "governance_mode": "INSTITUTIONAL_PRODUCTION", "production_authorized": True, "institutional_owners": {"data_owner": {"name": "x", "date": "2026-09-03", "reference": "x"}, "risk_owner": {"name": "x", "date": "2026-09-03", "reference": "x"}}}
    results.append({"id": "T7", "pass": "institutional_owners.model_owner" in " ".join(validate_register(inst)["errors"])})
    inst = {"stage": "D9", "governance_mode": "INSTITUTIONAL_PRODUCTION", "production_authorized": True, "institutional_owners": {"data_owner": {"name": "x", "date": "2026-09-03", "reference": "x"}, "model_owner": {"name": "x", "date": "2026-09-03", "reference": "x"}}}
    results.append({"id": "T8", "pass": "institutional_owners.risk_owner" in " ".join(validate_register(inst)["errors"])})
    inst = {"stage": "D9", "governance_mode": "INSTITUTIONAL_PRODUCTION", "production_authorized": True, "institutional_owners": {role: {"name": role, "date": "2026-09-03", "reference": role} for role in ("data_owner", "model_owner", "risk_owner")}}
    results.append({"id": "T9", "pass": validate_register(inst)["validation_status"] == "INSTITUTIONAL_VALID"})
    return results


if __name__ == "__main__":
    results = run(); passed = sum(x["pass"] for x in results)
    print(f"PORTFOLIO GOVERNANCE TESTS {passed}/{len(results)} pass")
    for result in results:
        print(("PASS" if result["pass"] else "FAIL") + " " + result["id"])
    raise SystemExit(0 if passed == len(results) else 1)
