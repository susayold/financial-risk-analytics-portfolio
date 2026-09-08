"""Live GitHub Pages smoke test for CRD.PI Block F.

Validates the deployed static surface, not the local checkout. All seven primary
routes and every public JSON contract are fetched concurrently with bounded
retries so failures are fast, attributable and fail-closed.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import json
import os
import re
import time
import urllib.request

BASE_URL = os.environ.get(
    "BLOCK_F_LIVE_BASE_URL",
    "https://susayold.github.io/financial-risk-analytics-portfolio/",
).rstrip("/")
TIMEOUT = float(os.environ.get("BLOCK_F_SMOKE_REQUEST_TIMEOUT", "8"))

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
        headers={"User-Agent": "CRD.PI-Block-F-Live-Smoke/1.1"},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return path, response.status, response.read()


def audit_once() -> list[str]:
    failures: list[str] = []
    payloads: dict[str, tuple[int, bytes]] = {}
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

    page07 = None
    for path in PUBLIC_JSON:
        if path not in payloads:
            continue
        status, payload = payloads[path]
        if status != 200:
            failures.append(f"{path}: HTTP {status}")
            continue
        try:
            parsed = json.loads(payload)
        except Exception as exc:
            failures.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(parsed, (dict, list)):
            failures.append(f"{path}: JSON root is not object/list")
        if path.endswith("page-07-architecture.json"):
            page07 = parsed

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
