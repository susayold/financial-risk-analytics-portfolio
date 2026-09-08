"""Build CRD.PI Page 01 from frozen public-safe downstream contracts.

This builder intentionally consumes already-governed aggregate evidence from
Pages 03-06. It never reads row-level borrower data and never recalculates the
model, loss economics, policy thresholds, or monitoring severities.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
OUT = DATA / "page-01-overview.json"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def build():
    model = load("page-03-model-decisioning.json")
    economics = load("page-04-loss-policy-stress.json")
    monitoring = load("page-05-monitoring.json")
    governance = load("page-06-governance.json")

    check(model["contract"]["feature_count"] == 79, "Frozen feature count must remain 79")
    check(model["oot"]["roc_auc"] == monitoring["discrimination"]["oot_roc_auc"], "Model and monitoring AUC mismatch")
    check(economics["central_case"]["accounts"] == monitoring["population"]["rows"], "Scored population mismatch")
    check(monitoring["meta"]["canonical_release"] == governance["meta"]["canonical_block_e_release"], "Block E release mismatch")
    check(governance["meta"]["canonical_block_e_release"] == "block-e-v1.0.2-final", "Unexpected Block E release")

    payload = {
        "meta": {
            "project": "CRD.PI",
            "page": "executive-overview",
            "analytical_handoff": governance["meta"]["canonical_block_e_release"],
            "generated_from_canonical_artifacts": True,
            "production_authorized": False,
            "regulatory_compliance_claimed": False,
        },
        "portfolio": {
            "resolved_loans": model["population"]["full_governed_core_accounts"],
            "observed_bad": 269249,
            "observed_bad_rate": 0.1998,
            "scope": "full_core_resolved_granted_loans",
        },
        "model": {
            "model_id": model["meta"]["model_id"],
            "frozen_features": model["contract"]["feature_count"],
            "oot_year": 2017,
            "oot_scored_n": model["oot"]["rows"],
            "oot_roc_auc": model["oot"]["roc_auc"],
            "oot_gini": round(model["oot"]["gini"], 6),
            "oot_ks": round(model["oot"]["ks"], 6),
            "oot_pr_auc": round(model["oot"]["pr_auc"], 6),
            "oot_brier": round(model["oot"]["brier"], 6),
            "bootstrap_reps": model["oot"]["bootstrap_reps"],
            "bootstrap_auc_ci_low": model["oot"]["auc_ci_low"],
            "bootstrap_auc_ci_high": model["oot"]["auc_ci_high"],
        },
        "economics": {
            "scored_accounts": economics["central_case"]["accounts"],
            "ead_proxy": economics["central_case"]["ead_proxy"],
            "lgd_central_q50": economics["central_case"]["lgd"],
            "expected_loss_proxy": economics["central_case"]["expected_loss_proxy"],
            "expected_loss_rate": economics["central_case"]["el_rate"],
            "claim_boundary": "analytical_expected_loss_proxy_only",
        },
        "monitoring": {
            "kri_count": monitoring["governance_counts"]["kri_count"],
            "alert_count": monitoring["governance_counts"]["alert_count"],
            "amber_alert_count": monitoring["governance_counts"]["amber_alert_count"],
            "red_alert_count": monitoring["governance_counts"]["red_alert_count"],
            "breach_count": monitoring["governance_counts"]["breach_count"],
            "investigation_count": monitoring["governance_counts"]["investigation_count"],
            "action_count": monitoring["governance_counts"]["action_count"],
            "current_highest_kri": monitoring["status"]["current_highest_kri"],
            "historical_highest_kri": monitoring["status"]["historical_highest_kri"],
            "auto_retraining": monitoring["status"]["automatic_retraining"],
        },
    }

    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} from frozen aggregate contracts")


if __name__ == "__main__":
    build()
