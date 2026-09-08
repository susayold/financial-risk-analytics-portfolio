"""Build Block F closure artifacts from the machine-readable QA scorecard.

The script is intentionally fail-closed: it will not create a release-ready
closure package unless every pre-deployment gate is PASS. Deployment smoke may
remain PENDING on the feature branch; in that case the package is explicitly
marked READY_FOR_DEPLOYMENT rather than DELIVERED.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCK_F = ROOT / "block-f"
QA_PATH = BLOCK_F / "BLOCK_F_FINAL_QA.json"
STATUS_PATH = BLOCK_F / "BLOCK_F_STATUS.md"
MANIFEST_PATH = BLOCK_F / "BLOCK_F_RELEASE_MANIFEST.json"
INDEX_PATH = BLOCK_F / "BLOCK_F_PUBLIC_ARTIFACT_INDEX.csv"
CLOSURE_PATH = BLOCK_F / "BLOCK_F_CLOSURE.md"

PUBLIC_ROOTS = [
    ROOT / "index.html",
    ROOT / "portfolio-risk",
    ROOT / "model-decisioning",
    ROOT / "loss-policy-stress",
    ROOT / "monitoring",
    ROOT / "governance",
    ROOT / "architecture",
    ROOT / "assets",
    ROOT / "public" / "data",
]
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".csv", ".md", ".txt"}
PRE_DEPLOYMENT_GATES = [
    "data_reconciliation",
    "cross_page_consistency",
    "claim_tests",
    "public_private_scan",
    "route_tests",
    "responsive_qa",
    "accessibility_qa",
    "visual_qa",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha() -> str:
    from_env = os.environ.get("GITHUB_SHA")
    if from_env:
        return from_env
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def iter_public_files():
    seen: set[Path] = set()
    for root in PUBLIC_ROOTS:
        if root.is_file():
            candidates = [root]
        elif root.exists():
            candidates = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES]
        else:
            candidates = []
        for path in sorted(candidates):
            if path in seen:
                continue
            seen.add(path)
            yield path


def artifact_type(path: Path) -> str:
    rel = str(path.relative_to(ROOT))
    if rel == "index.html" or rel.endswith("/index.html"):
        return "PAGE"
    if rel.startswith("public/data/"):
        return "PUBLIC_DATA_CONTRACT"
    if rel.startswith("assets/"):
        return "ASSET"
    return "PUBLIC_FILE"


def main() -> None:
    if not QA_PATH.exists():
        raise FileNotFoundError(f"Missing QA scorecard: {QA_PATH.relative_to(ROOT)}")

    qa = json.loads(QA_PATH.read_text(encoding="utf-8"))
    gates = qa["gates"]
    bad_pre = {name: gates.get(name) for name in PRE_DEPLOYMENT_GATES if gates.get(name) != "PASS"}
    if bad_pre:
        raise AssertionError(f"Cannot build closure package; pre-deployment gates not PASS: {bad_pre}")

    deployment = gates.get("deployment_smoke", "PENDING")
    if deployment == "PASS" and qa.get("status") == "PASS":
        closure_state = "DELIVERED"
    elif deployment == "PENDING" and qa.get("status") in {"READY_FOR_REVIEW", "READY_FOR_DEPLOYMENT"}:
        closure_state = "READY_FOR_DEPLOYMENT"
    else:
        raise AssertionError(
            f"Unsupported closure state: qa.status={qa.get('status')}, deployment_smoke={deployment}"
        )

    BLOCK_F.mkdir(parents=True, exist_ok=True)
    commit_sha = git_sha()

    rows = []
    for path in iter_public_files():
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "artifact_type": artifact_type(path),
            "public_safe": "true",
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    with INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "artifact_type", "public_safe", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "project": "CRD.PI",
        "block": "F",
        "state": closure_state,
        "commit_sha": commit_sha,
        "canonical_upstream": {
            "block_d_release": qa["block_d_release"],
            "block_e_release": qa["block_e_release"],
            "scored_population": 310066,
            "feature_contract": 79,
            "upstream_analytics_changed": qa["upstream_analytics_changed"],
        },
        "production_authorized": qa["production_authorized"],
        "regulatory_compliance_claimed": qa["regulatory_compliance_claimed"],
        "qa_status": qa["status"],
        "gates": gates,
        "public_artifact_count": len(rows),
        "artifact_index_sha256": sha256(INDEX_PATH),
        "target_release": "block-f-v1.0-final",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    gate_lines = "\n".join(f"- `{name}`: **{status}**" for name, status in gates.items())
    STATUS_PATH.write_text(
        f"""# CRD.PI Block F Status

**State:** `{closure_state}`  
**Commit:** `{commit_sha}`  
**Block D:** `block-d-v1.0-final`  
**Block E:** `block-e-v1.0.2-final`

## Delivery QA

{gate_lines}

## Frozen upstream controls

- Scored analytical population: **310,066**.
- Frozen feature contract: **79 features**.
- Block F did **not** retune the model, target, Block D economics/policy thresholds, or Block E monitoring findings.
- Production authorization remains **false**.
- Regulatory compliance is **not claimed**.

## Release rule

`DELIVERED` and `block-f-v1.0-final` are allowed only after `deployment_smoke = PASS` and every required QA gate is `PASS`.
""",
        encoding="utf-8",
    )

    CLOSURE_PATH.write_text(
        f"""# CRD.PI Block F Closure

Block F packages frozen analytical evidence into a seven-page recruiter-facing static delivery layer.

## Current closure state

`{closure_state}`

- Primary pages: **7**.
- Public artifact index entries: **{len(rows)}**.
- Block D canonical release: `block-d-v1.0-final`.
- Block E canonical release: `block-e-v1.0.2-final`.
- Upstream analytics changed in Block F: **false**.

## Interpretation boundary

This closure applies to **portfolio delivery only**. It does not authorize production underwriting, live loan-origination integration, real-time scoring, live production monitoring, regulatory reporting, automated retraining, or IFRS 9/Basel production use.

The project continues to describe the final-resolution target, LGD/EAD assumptions, analytical expected loss, historical policy simulation and historical monitoring within their documented analytical boundaries.

## Release decision

- If `deployment_smoke` is `PENDING`, this package is a **release candidate** and Block F remains `IN_PROGRESS` on the public site.
- Only after live GitHub Pages smoke testing passes may the project be marked `DELIVERED` and tagged `block-f-v1.0-final`.
""",
        encoding="utf-8",
    )

    print(f"Block F closure artifacts built: state={closure_state}, public_artifacts={len(rows)}")


if __name__ == "__main__":
    main()
