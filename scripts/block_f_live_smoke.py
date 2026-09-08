"""Live GitHub Pages smoke test for CRD.PI Block F.

Validates the deployed static surface, not the local checkout. All seven primary
routes and every public JSON contract are fetched concurrently with bounded
retries. In addition to availability, the smoke test enforces the post-release
website reconciliation contract so stale status text, date ambiguity, pricing
unit errors, PSI divergence, and KRI-count drift cannot silently reappear.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import json
import math
import os
import re
import time
import urllib.request

BASE_URL = os.environ.get(
    "BLOCK_F_LIVE_BASE_URL",
    "https://susayold.github.io/financial-risk-analytics-portfolio/",
).rstrip("/")
TIMEOUT = float(os.environ.get("BLOCK_F_SMOKE_REQUEST_TIMEOUT", "8"))
EXPECTED_STATUS = os.environ.get("BLOCK_F_EXPECTED_DELIVERY_STATUS", "").strip().upper()

ROUTES = {
    "/": "Credit Risk Intelligence & Portfolio Analytics",
    "/portfolio-risk/": "Portfolio Risk Intelligence",
    "/model-decisioning/": "Risk Model & Decisioning",
    "/loss-policy-stress/": "Loss, Policy & Stress",
    "/monitoring/": "Monitoring & Early Warning",
    "/governance/": "Governance & Audit",
    "/architecture/": "Architecture & Delivery",
}
PUBLIC_JSON = [
    "/public/data/governance-evidence-index.json",
    "/public/data/governance-taxonomy.json",
    "/public/data/model-feature-contract-79f.json",
    "/public/data/monitoring-alerts.json",
    "/public/data/monitoring-thresholds.json",
    "/public/data/page-01-overview.json",
    "/public/data/page-02-portfolio-risk.json",
    "/public/data/page-03-model-decisioning.json",
    "/public/data/page-04-loss-policy-stress.json",
    "/public/data/page-05-monitoring.json",
    "/public/data/page-06-governance.json",
    "/public/data/page-07-architecture.json",
]


def get(path: str) -> tuple[str, int, bytes]:
    request = urllib.request.Request(
        BASE_URL + path,
        headers={"User-Agent": "CRD.PI-Block-F-Live-Smoke/1.3"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return path, response.status, response.read()


def _text(payloads: dict[str, tuple[int, bytes]], path: str) -> str:
    item = payloads.get(path)
    if not item:
        return ""
    return item[1].decode("utf-8", errors="replace")


def _json(parsed_json: dict[str, object], path: str) -> dict:
    value = parsed_json.get(path)
    return value if isinstance(value, dict) else {}


def audit_once() -> list[str]:
    failures: list[str] = []
    payloads: dict[str, tuple[int, bytes]] = {}
    parsed_json: dict[str, object] = {}
    paths = list(ROUTES) + PUBLIC_JSON
    with ThreadPoolExecutor(max_workers=min(12, len(paths))) as pool:
        futures = {pool.submit(get, path): path for path in paths}
        for future in as_completed(futures):
            path = futures[future]
            try:
                _, status, payload = future.result()
                payloads[path] = (status, payload)
            except Exception as exc:
                failures.append(f"{path}: {type(exc).__name__}: {exc}")

    for path, expected_title in ROUTES.items():
        if path not in payloads:
            continue
        status, payload = payloads[path]
        text = payload.decode("utf-8", errors="replace")
        title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        actual_title = html.unescape(re.sub(r"\s+", " ", title.group(1)).strip()) if title else ""
        if status != 200:
            failures.append(f"{path}: HTTP {status}")
        if expected_title.lower() not in actual_title.lower():
            failures.append(f"{path}: unexpected title {actual_title!r}")
        if "viewport" not in text.lower():
            failures.append(f"{path}: missing viewport metadata")
        if "noindex" in text.lower():
            failures.append(f"{path}: noindex present")

    for path in PUBLIC_JSON:
        if path not in payloads:
            continue
        status, payload = payloads[path]
        if status != 200:
            failures.append(f"{path}: HTTP {status}")
            continue
        try:
            parsed = json.loads(payload)
            parsed_json[path] = parsed
        except Exception as exc:
            failures.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(parsed, (dict, list)):
            failures.append(f"{path}: JSON root is not object/list")

    # Final delivery wording must be correct even before JavaScript runs.
    overview_html = _text(payloads, "/")
    if "Block F · Delivered" not in overview_html:
        failures.append("overview: final Block F DELIVERED status missing")
    if "Delivery in progress" in overview_html:
        failures.append("overview: stale Block F in-progress wording present")
    if "Higher quality approvals" in overview_html:
        failures.append("overview: unsupported approval-improvement wording present")
    if "Historical policy simulation" not in overview_html:
        failures.append("overview: bounded historical-policy wording missing")

    portfolio_html = _text(payloads, "/portfolio-risk/")
    if "block-f-v1.0-final" not in portfolio_html:
        failures.append("portfolio: final Block F release label missing")
    if "As of Block F (v1.0.2-final)" in portfolio_html or "Latest data:" in portfolio_html:
        failures.append("portfolio: stale release/date wording present")

    architecture_html = _text(payloads, "/architecture/")
    if "BLOCK F · IN PROGRESS" in architecture_html or "Current state: IN PROGRESS" in architecture_html:
        failures.append("architecture: stale raw-HTML delivery status present")

    # Page 02: full resolved portfolio extends through 2018-12; OOT remains 2017-12.
    page02 = _json(parsed_json, "/public/data/page-02-portfolio-risk.json")
    p02_meta = page02.get("meta", {}) if isinstance(page02.get("meta"), dict) else {}
    p02_portfolio = page02.get("portfolio", {}) if isinstance(page02.get("portfolio"), dict) else {}
    if p02_meta.get("as_of") != "2018-12-01" or p02_portfolio.get("max_issue_d") != "2018-12-01":
        failures.append("page-02: full-core latest date is not 2018-12-01")
    if p02_meta.get("oot_cutoff") != "2017-12-01":
        failures.append("page-02: OOT cutoff is not 2017-12-01")

    # Page 03 and Page 05 must use one canonical annual score PSI.
    page03 = _json(parsed_json, "/public/data/page-03-model-decisioning.json")
    page05 = _json(parsed_json, "/public/data/page-05-monitoring.json")
    ranking = page03.get("ranking", {}) if isinstance(page03.get("ranking"), dict) else {}
    score_drift = page05.get("score_drift", {}) if isinstance(page05.get("score_drift"), dict) else {}
    p03_psi = ranking.get("prediction_psi")
    p05_psi = score_drift.get("annual_psi")
    if not isinstance(p03_psi, (int, float)) or not isinstance(p05_psi, (int, float)) or not math.isclose(float(p03_psi), float(p05_psi), rel_tol=0.0, abs_tol=1e-15):
        failures.append(f"page-03/page-05: annual score PSI mismatch {p03_psi!r} vs {p05_psi!r}")

    # Page 04: browser-facing interest rate must be a decimal fraction and
    # diagnostic spread must reconcile to rate minus analytical EL rate.
    page04 = _json(parsed_json, "/public/data/page-04-loss-policy-stress.json")
    pricing = page04.get("pricing", {}) if isinstance(page04.get("pricing"), dict) else {}
    diagnostics = pricing.get("diagnostics", []) if isinstance(pricing.get("diagnostics"), list) else []
    if not diagnostics:
        failures.append("page-04: pricing diagnostics missing")
    for row in diagnostics:
        if not isinstance(row, dict):
            failures.append("page-04: malformed pricing diagnostic row")
            continue
        rate = row.get("mean_rate")
        el_rate = row.get("mean_el_rate")
        spread = row.get("diagnostic_spread")
        if not all(isinstance(value, (int, float)) for value in (rate, el_rate, spread)):
            failures.append(f"page-04: non-numeric pricing diagnostic {row!r}")
            continue
        if not 0.0 <= float(rate) <= 1.0:
            failures.append(f"page-04: mean_rate is not a decimal fraction: {rate!r}")
        if not math.isclose(float(rate) - float(el_rate), float(spread), rel_tol=0.0, abs_tol=1e-12):
            failures.append(f"page-04: pricing spread does not reconcile for {row.get('label')!r}")

    # Page 05: canonical E8 registry is exactly 92 KRIs across E3-E7.
    expected_domain_counts = {
        "feature_drift": 3,
        "score_risk_mix": 17,
        "performance_calibration": 68,
        "loss_severity": 1,
        "policy_capacity_concentration": 3,
        "total": 92,
    }
    actual_domain_counts = page05.get("kri_domain_counts")
    if actual_domain_counts != expected_domain_counts:
        failures.append(f"page-05: KRI domain counts mismatch {actual_domain_counts!r}")
    governance_counts = page05.get("governance_counts", {}) if isinstance(page05.get("governance_counts"), dict) else {}
    if governance_counts.get("kri_count") != 92:
        failures.append("page-05: canonical KRI total is not 92")
    dq = page05.get("data_quality_control", {}) if isinstance(page05.get("data_quality_control"), dict) else {}
    if dq.get("registry") != "E2" or dq.get("kri_count") != 0:
        failures.append("page-05: E2 data-quality control boundary is not explicit")

    page07 = _json(parsed_json, "/public/data/page-07-architecture.json")
    if page07:
        meta = page07.get("meta", {}) if isinstance(page07.get("meta"), dict) else {}
        if meta.get("project") != "CRD.PI":
            failures.append("page-07: project marker mismatch")
        actual_status = str(meta.get("status", "")).upper()
        if actual_status not in {"IN_PROGRESS", "DELIVERED"}:
            failures.append(f"page-07: invalid delivery status {meta.get('status')!r}")
        if EXPECTED_STATUS and actual_status != EXPECTED_STATUS:
            failures.append(
                f"page-07: expected deployed status {EXPECTED_STATUS!r}, got {actual_status!r}"
            )
        upstream = page07.get("upstream", {}) if isinstance(page07.get("upstream"), dict) else {}
        if upstream.get("upstream_analytics_changed_in_block_f") is not False:
            failures.append("page-07: upstream analytics mutation boundary violated")
    return failures


def main() -> None:
    attempts = int(os.environ.get("BLOCK_F_SMOKE_ATTEMPTS", "12"))
    delay = int(os.environ.get("BLOCK_F_SMOKE_DELAY_SECONDS", "5"))
    last: list[str] = []
    for attempt in range(1, attempts + 1):
        last = audit_once()
        if not last:
            print(json.dumps({
                "status": "PASS",
                "base_url": BASE_URL + "/",
                "primary_routes": len(ROUTES),
                "public_json_contracts": len(PUBLIC_JSON),
                "deployment_smoke": "PASS",
                "website_reconciliation": "PASS",
                "expected_delivery_status": EXPECTED_STATUS or None,
            }, indent=2))
            return
        print(f"Live smoke attempt {attempt}/{attempts} failed with {len(last)} finding(s):", flush=True)
        for item in sorted(last):
            print(f"- {item}", flush=True)
        if attempt < attempts:
            time.sleep(delay)
    print(json.dumps({"status": "FAIL", "findings": last}, indent=2))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
