"""Build deterministic, public-safe data contracts for CRD.PI Page 06.

The website is a presentation layer.  Counts and decisions come from the
canonical Block E closure artifacts; no row-level monitoring data is copied.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK_E = ROOT / "block-e"
BLOCK_D = ROOT / "block-d"
OUT = ROOT / "public" / "data"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def value_from_status(markdown: str, label: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*`?([^`\n]+)", markdown)
    if not match:
        raise ValueError(f"Missing {label} in BLOCK_E_STATUS.md")
    return match.group(1).strip()


def assert_equal(actual, expected, label: str):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def build():
    status_text = (BLOCK_E / "BLOCK_E_STATUS.md").read_text(encoding="utf-8")
    e8 = load_json(BLOCK_E / "E8_KRI_GOVERNANCE" / "E8_TEST_RESULTS_PATCHED.json")
    e9 = load_json(BLOCK_E / "E9_FINAL" / "BLOCK_E_FINAL_QA_PATCHED.json")
    decision = load_json(BLOCK_E / "E9_FINAL" / "BLOCK_E_DECISION_PATCHED.json")
    manifest = load_json(BLOCK_E / "E9_FINAL" / "BLOCK_E_FINAL_CHECKSUM_MANIFEST_PATCHED.json")
    alerts = load_csv(BLOCK_E / "E8_KRI_GOVERNANCE" / "alert_log_PATCHED.csv")
    breaches = load_csv(BLOCK_E / "E8_KRI_GOVERNANCE" / "breach_register_PATCHED.csv")
    actions = load_csv(BLOCK_E / "E8_KRI_GOVERNANCE" / "action_register_PATCHED.csv")

    # Current release precedence is explicit: top-level status beats stale
    # nested decision metadata and historical release fields.
    canonical_release = value_from_status(status_text, "Canonical release").split()[0]
    assert_equal(canonical_release, "block-e-v1.0.2-final", "canonical release")
    block_e_status = value_from_status(status_text, "Status")
    assert_equal(block_e_status, "PASS_WITH_MONITORING", "Block E status")

    counts = {
        "kri_count": int(e8["kri_count"]),
        "alert_count": int(e8["alert_count"]),
        "amber_alert_count": int(e8["amber_alert_count"]),
        "red_alert_count": int(e8["red_alert_count"]),
        "breach_count": int(e8["breach_count"]),
        "investigation_count": int(e8["investigation_count"]),
        "action_count": int(e8["action_count"]),
        "green_alert_count": 0 if e8["no_green_alerts"] else 1,
    }
    expected_counts = {"kri_count": 92, "alert_count": 21, "amber_alert_count": 20, "red_alert_count": 1,
                       "breach_count": 3, "investigation_count": 21, "action_count": 21, "green_alert_count": 0}
    for key, expected in expected_counts.items():
        assert_equal(counts[key], expected, key)
    assert_equal(len(alerts), 21, "alert register rows")
    assert_equal(len(breaches), 3, "breach register rows")
    assert_equal(len(actions), 21, "action register rows")

    alert_ids = {row["alert_id"] for row in alerts}
    investigation_ids = {row["investigation_id"] for row in alerts}
    action_ids = {row["action_id"] for row in alerts}
    for row in breaches:
        for field, known in (("alert_id", alert_ids), ("investigation_id", investigation_ids), ("action_id", action_ids)):
            if row[field] not in known:
                raise AssertionError(f"Breach FK missing: {field}={row[field]}")

    red = next(row for row in alerts if row["alert_id"] == "E8A-016")
    assert_equal(red["window_id"], "2017-10", "historical RED window")
    assert_equal(float(red["metric_value"]), 1.3585283041585752, "historical RED value")
    assert_equal(red["severity"], "RED", "historical RED severity")

    qa = {
        "e8_passed": int(e8["overall"].split("/")[0]),
        "e8_failed": 0,
        "e9_passed": int(e9["tests_passed"]),
        "e9_failed": int(e9["tests_failed"]),
        "e9_original_gates": e9["original_gates"],
        "e9_patch_gates": e9["patch_gates"],
        "public_private_scan": e9["public_private_scan"],
        "checksum_integrity": e9["checksum_integrity"],
        "foreign_keys": e8["foreign_keys"],
        "snapshot_sha256": e9["snapshot_sha256"],
    }
    assert_equal(qa["e8_passed"], 25, "E8 passed")
    assert_equal(qa["e9_passed"], 35, "E9 passed")
    assert_equal(qa["e9_failed"], 0, "E9 failed")
    for key in ("public_private_scan", "checksum_integrity", "foreign_keys"):
        assert_equal(qa[key], "PASS", key)

    snapshot_sha = qa["snapshot_sha256"]
    assert_equal(snapshot_sha, "fe2ae600c9913ccfe827509f439c2f14108260e0e237f3fa78715b145123cd42", "snapshot SHA")

    page = {
        "meta": {
            "project": "CRD.PI",
            "page": "governance",
            "document_version": "F-P06-CONTENT-1.0",
            "canonical_block_e_release": canonical_release,
            "block_e_status": block_e_status,
            "production_authorized": False,
            "regulatory_compliance_claimed": False,
            "public_safe": True,
        },
        "snapshot": {
            "rows": 310066,
            "feature_count": 79,
            "unique_account_key": True,
            "sha256": snapshot_sha,
            "model": decision["model"],
        },
        "qa": qa,
        "monitoring_state": {
            **counts,
            "current_highest_kri": decision["highest_current_kri_status"],
            "historical_highest_kri": decision["highest_observed_kri_status"],
        },
        "model_governance": {
            "champion": decision["model"],
            "contract": "Frozen 79-feature contract, feature order, target, score name and historical OOT evidence",
            "block_c_model_reopened": decision["block_c_model_reopened"],
            "model_retrained": False,
            "hpo_rerun": False,
            "feature_redesign": False,
            "target_redesign": False,
        },
        "validation_governance": {
            "baseline": decision["baseline"],
            "historical_oot": decision["primary_historical_monitoring_window"],
            "oot_tuning": False,
            "new_holdout_required_if_redeveloped": True,
        },
        "risk_economics": {
            "block_d_status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
            "chain": ["p_bad_final", "LGD_CENTRAL_Q50", "contractual EAD proxy", "EL_MAIN_ANALYTICAL", "historical policy simulation", "analytical stress"],
            "boundaries": ["risk score ≠ verified regulatory 12m PD", "LGD/EAD/EL are analytical proxies", "policy is historical simulation", "pricing is descriptive only", "stress is analytical sensitivity"],
        },
        "threshold_contract": {"version": "E0-1.0.1", "deterministic": True, "shared_across_monitoring": True},
        "change_control": {
            "recalibration_candidate": decision["recalibration_candidate"],
            "recalibration_executed": False,
            "redevelopment_candidate": decision["redevelopment_candidate"],
            "automatic_retraining": False,
            "portfolio_project_use_approved": decision["portfolio_project_use_approved"],
            "production_authorized": decision["production_authorized"],
            "regulatory_compliance_claimed": decision["regulatory_compliance_claimed"],
            "model_use_restriction": decision["model_use_restrictions"][0],
        },
        "historical_red_example": {
            "metric": "CALIBRATION_SLOPE",
            "window": "2017-10",
            "value": float(red["metric_value"]),
            "severity": "RED",
            "breach_id": "BR-003",
            "investigation_id": "INV-016",
            "action_id": "ACT-016",
            "action_type": "CALIBRATION_REVIEW",
            "model_change_required": False,
            "production_change_required": False,
            "automatic_retraining": False,
        },
        "breach_logic": {
            "total": 3,
            "persistent_amber": 2,
            "single_red": 1,
            "rule": "single RED OR deterministic persistence escalation",
        },
        "release_lineage": [
            {"tag": "block-d-v1.0-final", "date": "2026-09-03", "type": "ANALYTICAL_CLOSURE", "status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO", "current": False},
            {"tag": "block-e-v1.0-final", "date": None, "type": "HISTORICAL_PREDECESSOR", "status": "SUPERSEDED", "current": False},
            {"tag": "block-e-v1.0.1-final", "date": "2026-09-04", "type": "GOVERNANCE_REMEDIATION", "status": "SUPERSEDED", "scope": "workflow completeness; model/snapshot/target/findings unchanged", "current": False},
            {"tag": "block-e-v1.0.2-final", "date": "2026-09-04", "type": "DOCUMENTATION_CONSISTENCY", "status": "CURRENT", "scope": "stale breach documentation corrected 4 → 3; analytical evidence unchanged", "current": True},
        ],
        "release_message": "Not every patch is a model change.",
        "checksum_manifest": {"tag": manifest["tag"], "artifact_count": manifest["artifact_count"], "snapshot_unchanged": manifest["snapshot_sha256_unchanged"] == snapshot_sha},
    }

    taxonomy = {
        "root_causes": list(e8["controlled_root_causes"]),
        "actions": list(e8["controlled_actions"]),
        "counts": {"root_cause_domains": len(e8["controlled_root_causes"]), "action_types": len(e8["controlled_actions"])},
        "source": "block-e/E8_KRI_GOVERNANCE/E8_TEST_RESULTS_PATCHED.json",
    }

    base = "https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/"
    evidence = [
        {"artifact_name": "Block E Status", "stage": "E9", "purpose": "Current closure and release authority", "public_source": base + "block-e/BLOCK_E_STATUS.md", "status": "CANONICAL", "release": canonical_release, "public_private_class": "PUBLIC"},
        {"artifact_name": "E8 Governance QA", "stage": "E8", "purpose": "KRI, alert and workflow integrity", "public_source": base + "block-e/E8_KRI_GOVERNANCE/E8_TEST_RESULTS_PATCHED.json", "status": "25/25 PASS", "release": "block-e-v1.0.1-final", "public_private_class": "PUBLIC"},
        {"artifact_name": "Alert Log", "stage": "E8", "purpose": "Non-GREEN event registry", "public_source": base + "block-e/E8_KRI_GOVERNANCE/alert_log_PATCHED.csv", "status": "ACTIVE EVIDENCE", "release": canonical_release, "public_private_class": "PUBLIC_AGGREGATE"},
        {"artifact_name": "Breach Register", "stage": "E8", "purpose": "Escalated event registry", "public_source": base + "block-e/E8_KRI_GOVERNANCE/breach_register_PATCHED.csv", "status": "3 BREACHES", "release": canonical_release, "public_private_class": "PUBLIC_AGGREGATE"},
        {"artifact_name": "Action Register", "stage": "E8", "purpose": "Governed response registry", "public_source": base + "block-e/E8_KRI_GOVERNANCE/action_register_PATCHED.csv", "status": "21 ACTIONS", "release": canonical_release, "public_private_class": "PUBLIC_AGGREGATE"},
        {"artifact_name": "E9 Final QA", "stage": "E9", "purpose": "Final scans and checksum integrity", "public_source": base + "block-e/E9_FINAL/BLOCK_E_FINAL_QA_PATCHED.json", "status": "35/35 PASS", "release": canonical_release, "public_private_class": "PUBLIC"},
        {"artifact_name": "Block E Decision", "stage": "E9", "purpose": "Use, recalibration and redevelopment decision", "public_source": base + "block-e/E9_FINAL/BLOCK_E_DECISION_PATCHED.json", "status": "DECISION INPUT", "release": canonical_release, "public_private_class": "PUBLIC"},
        {"artifact_name": "Final Checksum Manifest", "stage": "E9", "purpose": "Artifact fingerprint and public boundary", "public_source": base + "block-e/E9_FINAL/BLOCK_E_FINAL_CHECKSUM_MANIFEST_PATCHED.json", "status": "PASS", "release": canonical_release, "public_private_class": "PUBLIC"},
        {"artifact_name": "Block D Status", "stage": "D9", "purpose": "Carried-forward analytical and production boundaries", "public_source": base + "block-d/BLOCK_D_STATUS.md", "status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO", "release": "block-d-v1.0-final", "public_private_class": "PUBLIC"},
        {"artifact_name": "Private evidence handoff", "stage": "E9", "purpose": "Detailed row-level evidence retained outside the public site", "public_source": "https://drive.google.com/drive/folders/1cF3HXZF9dH4BHLklxfN2QoPpeRj_iU1y", "status": "PRIVATE", "release": canonical_release, "public_private_class": "PRIVATE_DRIVE"},
    ]

    OUT.mkdir(parents=True, exist_ok=True)
    for name, payload in (("page-06-governance.json", page), ("governance-taxonomy.json", taxonomy), ("governance-evidence-index.json", evidence)):
        (OUT / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote Page 06 contracts: {counts['kri_count']} KRIs, {counts['alert_count']} alerts, {counts['breach_count']} breaches, {len(evidence)} evidence rows")


if __name__ == "__main__":
    build()
