"""Build the public-safe architecture contract for CRD.PI Page 07.

Page 07 describes delivery of the frozen A–E analytical product. It never
recomputes upstream risk metrics. Delivery state is derived from the dedicated
Block F QA artifact rather than being hard-coded.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
OUT = DATA / "page-07-architecture.json"
QA_PATH = ROOT / "block-f" / "BLOCK_F_FINAL_QA.json"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def qa_state():
    if not QA_PATH.exists():
        gates = {
            "data_reconciliation": "PENDING",
            "cross_page_consistency": "PENDING",
            "claim_tests": "PENDING",
            "public_private_scan": "PENDING",
            "route_tests": "PENDING",
            "responsive_qa": "PENDING",
            "accessibility_qa": "PENDING",
            "visual_qa": "PENDING",
            "deployment_smoke": "PENDING",
        }
        return "IN_PROGRESS", gates
    qa = json.loads(QA_PATH.read_text(encoding="utf-8"))
    gates = qa["gates"]
    delivered = qa.get("status") == "PASS" and all(value == "PASS" for value in gates.values())
    return ("DELIVERED" if delivered else "IN_PROGRESS"), gates


def build():
    routes = json.loads((ROOT / "config" / "routes.json").read_text(encoding="utf-8"))["primary_pages"]
    check(len(routes) == 7, "Block F requires exactly 7 primary pages")
    check(len({item["route"] for item in routes}) == 7, "Primary routes must be unique")
    check(routes[-1]["route"] == "/architecture/", "Page 07 route mismatch")

    overview = load("page-01-overview.json")
    model = load("page-03-model-decisioning.json")
    economics = load("page-04-loss-policy-stress.json")
    monitoring = load("page-05-monitoring.json")
    governance = load("page-06-governance.json")

    check(overview["model"]["oot_roc_auc"] == model["oot"]["roc_auc"], "Overview AUC != Model AUC")
    check(overview["economics"]["expected_loss_rate"] == economics["central_case"]["el_rate"], "Overview EL rate != Loss page EL rate")
    check(overview["monitoring"]["current_highest_kri"] == monitoring["status"]["current_highest_kri"], "Overview KRI != Monitoring KRI")
    check(monitoring["status"]["current_highest_kri"] == governance["monitoring_state"]["current_highest_kri"], "Monitoring KRI != Governance KRI")
    check(monitoring["meta"]["canonical_release"] == governance["meta"]["canonical_block_e_release"] == "block-e-v1.0.2-final", "Canonical Block E release mismatch")

    status, gates = qa_state()
    page = {
        "meta": {
            "project": "CRD.PI",
            "page": "architecture",
            "block": "F",
            "status": status,
            "document_version": "F-P07-CONTENT-1.0",
            "production_authorized": False,
            "regulatory_compliance_claimed": False,
            "public_safe": True,
        },
        "upstream": {
            "block_d_release": "block-d-v1.0-final",
            "block_d_status": "CLOSED_WITH_LIMITATIONS_PORTFOLIO",
            "block_e_release": "block-e-v1.0.2-final",
            "block_e_status": "PASS_WITH_MONITORING",
            "scored_population": 310066,
            "feature_count": 79,
            "snapshot_sha256": governance["snapshot"]["sha256"],
            "upstream_analytics_changed_in_block_f": False,
        },
        "pages": routes,
        "delivery": {
            "mode": "STATIC_PUBLIC_SITE",
            "hosting": "GITHUB_PAGES",
            "browser_row_level_data": False,
            "live_scoring_api": False,
            "production_database": False,
            "automatic_retraining": False,
        },
        "block_f_qa": gates,
        "cross_page_checks": {
            "overview_oot_roc_auc": overview["model"]["oot_roc_auc"],
            "model_oot_roc_auc": model["oot"]["roc_auc"],
            "overview_expected_loss_rate": overview["economics"]["expected_loss_rate"],
            "loss_expected_loss_rate": economics["central_case"]["el_rate"],
            "current_kri": governance["monitoring_state"]["current_highest_kri"],
            "release": governance["meta"]["canonical_block_e_release"],
        },
        "architecture_flow": [
            "CANONICAL BLOCK ARTIFACT", "SOURCE SELECTION", "PUBLIC-SAFE AGGREGATION",
            "NORMALIZATION", "RECONCILIATION TESTS", "CLAIM-BOUNDARY TESTS",
            "VERSIONED PAGE JSON", "PAGE COMPONENTS", "STATIC BUILD",
        ],
        "shared_components": [
            "SiteHeader", "SiteFooter", "MetricCard", "StatusBadge", "SectionHeading",
            "BoundaryNote", "DataSourceTooltip", "EvidenceLink", "PageCTA",
        ],
        "technology_stack": [
            {"layer": "Application shell", "technology": "Static HTML", "status": "IMPLEMENTED", "purpose": "public static routing / SEO"},
            {"layer": "Types", "technology": "TypeScript", "status": "TARGET STACK", "purpose": "typed page-data contracts"},
            {"layer": "Selective interactivity", "technology": "Vanilla JavaScript", "status": "IMPLEMENTED", "purpose": "filters, tables and page interactions"},
            {"layer": "Analytical charts", "technology": "Browser-native SVG / CSS / JavaScript", "status": "IMPLEMENTED", "purpose": "lightweight analytical visualization"},
            {"layer": "Data build", "technology": "Python", "status": "IMPLEMENTED", "purpose": "deterministic aggregate JSON"},
            {"layer": "Hosting", "technology": "GitHub Pages", "status": "IMPLEMENTED", "purpose": "static public hosting"},
            {"layer": "Automation", "technology": "GitHub Actions", "status": "IMPLEMENTED", "purpose": "build / QA automation"},
        ],
        "public_private_boundary": {
            "private": ["raw source files", "row-level marts", "account keys", "79F row-level matrices", "row-level predictions", "private monitoring evidence", "private Drive handoff"],
            "public": ["source code", "documentation", "sanitized aggregate JSON", "aggregate QA", "release metadata", "charts", "website"],
            "flow": ["SANITIZE", "RECONCILE", "SCAN", "PUBLISH"],
        },
        "delivery_principles": [
            {"name": "Frozen Upstream", "detail": "No analytical retuning in Block F."},
            {"name": "Public-Safe by Design", "detail": "Browser consumes sanitized aggregates."},
            {"name": "Deterministic", "detail": "Page JSON comes from build scripts."},
            {"name": "Traceable", "detail": "Metrics link back to canonical artifacts."},
            {"name": "Fail Closed", "detail": "Reconciliation, privacy and claim errors block release."},
            {"name": "Static First", "detail": "No live borrower infrastructure is required."},
        ],
        "production_boundary": ["live LOS integration", "real-time scoring", "live model monitoring", "regulatory reporting", "automated retraining", "enterprise IAM", "SLA / uptime"],
        "traceability_example": {
            "metric": "$526.75M Expected-Loss Proxy",
            "page_contract": "page-04-loss-policy-stress.json → central_case.expected_loss_proxy",
            "source": "Block D D5",
            "release": "block-d-v1.0-final",
            "claim_boundary": "Analytical expected-loss proxy; not regulatory ECL",
        },
    }
    OUT.write_text(json.dumps(page, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote Page 07 contract: {len(routes)} pages, status={status}")


if __name__ == "__main__":
    build()
