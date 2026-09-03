"""Scan public Block D artifacts for private paths, secrets, and overclaims."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOCK = ROOT / "block-d"
FORBIDDEN = [
    r"[A-Za-z]:\\Users\\", r"/kaggle/input/", r"/mnt/data/", r"BEGIN (RSA|OPENSSH) PRIVATE KEY",
    r"(?i)(api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"][^'\"]+",
    r"(?i)IFRS\s*9\s*compliant", r"(?i)Basel\s*compliant", r"(?i)production\s+approved",
    r"(?i)realized\s+profitability", r"(?i)approved\s+lending\s+policy", r"(?i)regulatory\s+ECL",
]
EXCLUDE = {"PRE_FINAL_SPRINT_MANIFEST.json", "scan_block_d_public_artifacts.py", "BLOCK_D_PUBLIC_ARTIFACT_SCAN.json"}


def main() -> int:
    findings = []
    scanned = 0
    for path in BLOCK.rglob("*"):
        if not path.is_file() or path.name in EXCLUDE or path.suffix.lower() not in {".md", ".json", ".csv"}:
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN:
            for match in re.finditer(pattern, text):
                line = text[max(0, text.rfind("\n", 0, match.start()) + 1):text.find("\n", match.end()) if text.find("\n", match.end()) >= 0 else len(text)].lower()
                # Claim-boundary negation is intentional and is allowed by the plan.
                if any(token in line for token in ("not ", "no ", "without ", "never ", "forbidden", "not_claimed")) and not re.search(r"[A-Za-z]:\\Users\\|/kaggle/input/|/mnt/data/|PRIVATE KEY", match.group(0), re.I):
                    continue
                findings.append({"file": str(path.relative_to(ROOT)), "pattern": pattern, "line": line.strip()})
    result = {"scan": "block_d_public_artifacts", "status": "PASS" if not findings else "FAIL", "files_scanned": scanned, "findings": findings, "claim_boundary": "Explicit negation and analytical scope wording are required for limitations."}
    out = BLOCK / "BLOCK_D_PUBLIC_ARTIFACT_SCAN.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"PUBLIC ARTIFACT SCAN {result['status']} — {scanned} files, {len(findings)} findings")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
