"""Live GitHub Pages smoke test for CRD.PI Block F.

This validates the deployed static surface, not the local checkout. It checks all
seven primary routes plus every public JSON contract with bounded retries so a
Pages deployment can finish before the gate is evaluated.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get(
    "BLOCK_F_LIVE_BASE_URL",
    "https://susayold.github.io/financial-risk-analytics-portfolio/",
).rstrip("/")

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


def get(path: str) -> tuple[int, bytes]:
    request = urllib.request.Request(
        BASE_URL + path,
        headers={"User-Agent": "CRD.PI-Block-F-Live-Smoke/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.read()


def audit_once() -> list[str]:
    failures: list[str] = []
    for path, expected_title in ROUTES.items():
        try:
            status, payload = get(path)
            text = payload.decode("utf-8", errors="replace")
            title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
            actual_title = re.sub(r"\s+", " ", title.group(1)).strip() if title else ""
            if status != 200:
                failures.append(f"{path}: HTTP {status}")
            if expected_title.lower() not in actual_title.lower():
                failures.append(f"{path}: unexpected title {actual_title!r}")
            if "<meta" not in text.lower() or "viewport" not in text.lower():
                failures.append(f"{path}: missing viewport metadata")
            if "noindex" in text.lower():
                failures.append(f"{path}: noindex present")
        except Exception as exc:
            failures.append(f"{path}: {type(exc).__name__}: {exc}")

    page07 = None
    for path in PUBLIC_JSON:
        try:
            status, payload = get(path)
            if status != 200:
                failures.append(f"{path}: HTTP {status}")
                continue
            parsed = json.loads(payload)
            if not isinstance(parsed, (dict, list)):
                failures.append(f"{path}: JSON root is not object/list")
            if path.endswith("page-07-architecture.json"):
                page07 = parsed
        except Exception as exc:
            failures.append(f"{path}: {type(exc).__name__}: {exc}")

    if isinstance(page07, dict):
        meta = page07.get("meta", {})
        if meta.get("project") != "CRD.PI":
            failures.append("page-07: project marker mismatch")
        if meta.get("status") not in {"IN_PROGRESS", "DELIVERED"}:
            failures.append(f"page-07: invalid delivery status {meta.get('status')!r}")
        if page07.get("upstream", {}).get("upstream_analytics_changed_in_block_f") is not False:
            failures.append("page-07: upstream analytics mutation boundary violated")
    return failures


def main() -> None:
    attempts = int(os.environ.get("BLOCK_F_SMOKE_ATTEMPTS", "18"))
    delay = int(os.environ.get("BLOCK_F_SMOKE_DELAY_SECONDS", "5"))
    last: list[str] = []
    for attempt in range(1, attempts + 1):
        last = audit_once()
        if not last:
            result = {
                "status": "PASS",
                "base_url": BASE_URL + "/",
                "primary_routes": len(ROUTES),
                "public_json_contracts": len(PUBLIC_JSON),
                "deployment_smoke": "PASS",
            }
            print(json.dumps(result, indent=2))
            return
        print(f"Live smoke attempt {attempt}/{attempts} failed with {len(last)} finding(s):")
        for item in last:
            print(f"- {item}")
        if attempt < attempts:
            time.sleep(delay)

    print(json.dumps({"status": "FAIL", "findings": last}, indent=2))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
