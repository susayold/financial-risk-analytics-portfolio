"""Run CRD.PI Block F delivery QA and emit a machine-readable scorecard."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

try:
    from scripts.validate_public_bundle import scan as scan_public_bundle
except ModuleNotFoundError:  # direct execution: python scripts/run_block_f_qa.py
    from validate_public_bundle import scan as scan_public_bundle

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
OUT_DIR = ROOT / "block-f"
OUT = OUT_DIR / "BLOCK_F_FINAL_QA.json"
BROWSER_QA = ROOT / "outputs" / "block-f" / "BLOCK_F_BROWSER_QA.json"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def public_text():
    paths = [
        ROOT / "index.html",
        ROOT / "portfolio-risk" / "index.html",
        ROOT / "model-decisioning" / "index.html",
        ROOT / "loss-policy-stress" / "index.html",
        ROOT / "monitoring" / "index.html",
        ROOT / "governance" / "index.html",
        ROOT / "architecture" / "index.html",
    ]
    parts = []
    for path in paths:
        check(path.exists(), f"Missing primary page: {path.relative_to(ROOT)}")
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    for path in DATA.glob("page-*.json"):
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def check_claims(text: str):
    # Phrases are allowed only when explicitly negated in the immediate context.
    risky = [
        "production ready",
        "production approved",
        "regulatory compliant",
        "verified regulatory 12-month pd",
        "verified 12-month pd",
        "live production monitoring system",
        "real-time scoring api",
        "automatic retraining triggered",
        "bank deployment",
        "3 red breaches",
    ]
    lower = text.lower()
    violations = []
    for phrase in risky:
        for match in re.finditer(re.escape(phrase), lower):
            before = lower[max(0, match.start() - 64):match.start()]
            if any(token in before for token in ("not ", "not a ", "no ", "false", "without ", "≠", "isn't ", "is not ")):
                continue
            violations.append({"phrase": phrase, "context": lower[max(0, match.start()-48):match.end()+48]})
    check(not violations, f"Unsupported public claim(s): {violations}")


def existing_deployment_smoke() -> str:
    if not OUT.exists():
        return "PENDING"
    try:
        prior = json.loads(OUT.read_text(encoding="utf-8"))
        value = prior.get("gates", {}).get("deployment_smoke", "PENDING")
        return str(value).upper()
    except (json.JSONDecodeError, OSError, TypeError):
        return "PENDING"


def main():
    p1 = load("page-01-overview.json")
    p2 = load("page-02-portfolio-risk.json")
    p3 = load("page-03-model-decisioning.json")
    p4 = load("page-04-loss-policy-stress.json")
    p5 = load("page-05-monitoring.json")
    p6 = load("page-06-governance.json")
    p7 = load("page-07-architecture.json")

    # Data reconciliation and frozen analytical invariants.
    check(p2["portfolio"]["good_accounts"] + p2["portfolio"]["bad_accounts"] == p2["portfolio"]["accounts"], "Page 02 GOOD/BAD mismatch")
    check(p1["model"]["oot_roc_auc"] == p3["oot"]["roc_auc"], "Page 01/Page 03 OOT AUC mismatch")
    check(p1["economics"]["expected_loss_rate"] == p4["central_case"]["el_rate"], "Page 01/Page 04 EL rate mismatch")
    check(p1["economics"]["scored_accounts"] == p3["population"]["scored_accounts"] == p4["central_case"]["accounts"] == p5["population"]["rows"] == p6["snapshot"]["rows"] == 310066, "310,066 population mismatch")
    check(p1["model"]["frozen_features"] == p3["contract"]["feature_count"] == p5["population"]["feature_count"] == p6["snapshot"]["feature_count"] == p7["upstream"]["feature_count"] == 79, "79F mismatch")
    check(p1["monitoring"]["current_highest_kri"] == p5["status"]["current_highest_kri"] == p6["monitoring_state"]["current_highest_kri"] == "AMBER", "Current KRI mismatch")
    check(p5["status"]["historical_highest_kri"] == p6["monitoring_state"]["historical_highest_kri"] == "RED", "Historical KRI mismatch")
    check(p5["governance_counts"]["breach_count"] == p6["monitoring_state"]["breach_count"] == 3, "Breach count mismatch")
    check(p5["governance_counts"]["red_alert_count"] == p6["monitoring_state"]["red_alert_count"] == 1, "RED alert count mismatch")
    check(p5["meta"]["canonical_release"] == p6["meta"]["canonical_block_e_release"] == p7["upstream"]["block_e_release"] == "block-e-v1.0.2-final", "Canonical Block E release mismatch")
    check(p7["upstream"]["block_d_release"] == "block-d-v1.0-final", "Canonical Block D release mismatch")
    check(p7["upstream"]["upstream_analytics_changed_in_block_f"] is False, "Block F must not alter upstream analytics")
    check(p1["meta"]["production_authorized"] is False and p6["meta"]["production_authorized"] is False and p7["meta"]["production_authorized"] is False, "Production boundary changed")

    routes = p7["pages"]
    check(len(routes) == 7 and len({r["route"] for r in routes}) == 7, "Primary route registry must contain 7 unique routes")
    for row in routes:
        if row["route"] == "/":
            path = ROOT / "index.html"
        else:
            path = ROOT / row["route"].strip("/") / "index.html"
        check(path.exists(), f"Missing route file for {row['route']}")
        check((DATA / row["data_contract"]).exists(), f"Missing data contract {row['data_contract']}")

    check_claims(public_text())
    scanned_files = scan_public_bundle()

    browser = {
        "route_tests": "PENDING",
        "responsive_qa": "PENDING",
        "accessibility_qa": "PENDING",
        "visual_qa": "PENDING",
    }
    if BROWSER_QA.exists():
        browser.update(json.loads(BROWSER_QA.read_text(encoding="utf-8")))

    deployment = os.environ.get("BLOCK_F_DEPLOYMENT_SMOKE", existing_deployment_smoke()).upper()
    gates = {
        "data_reconciliation": "PASS",
        "cross_page_consistency": "PASS",
        "claim_tests": "PASS",
        "public_private_scan": "PASS",
        "route_tests": browser["route_tests"],
        "responsive_qa": browser["responsive_qa"],
        "accessibility_qa": browser["accessibility_qa"],
        "visual_qa": browser["visual_qa"],
        "deployment_smoke": deployment,
    }
    failed = [name for name, status in gates.items() if status == "FAIL"]
    pending = [name for name, status in gates.items() if status != "PASS"]
    if failed:
        status = "FAIL"
    elif pending == ["deployment_smoke"]:
        status = "READY_FOR_DEPLOYMENT"
    elif pending:
        status = "READY_FOR_REVIEW"
    else:
        status = "PASS"

    result = {
        "status": status,
        "primary_pages": 7,
        "upstream_analytics_changed": False,
        "block_d_release": "block-d-v1.0-final",
        "block_e_release": "block-e-v1.0.2-final",
        "production_authorized": False,
        "regulatory_compliance_claimed": False,
        "public_text_files_scanned": scanned_files,
        "gates": gates,
        "failed_gates": failed,
        "pending_gates": pending,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
