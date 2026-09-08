"""Scan the recruiter-facing public bundle for row-level or secret leakage."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".md", ".txt", ".svg", ".csv"}

# These target payload/key/path patterns rather than legitimate boundary prose.
FORBIDDEN = {
    "account_id_key": re.compile(r'["\']account_id["\']\s*:', re.I),
    "borrower_id_key": re.compile(r'["\']borrower_id["\']\s*:', re.I),
    "customer_id_key": re.compile(r'["\']customer_id["\']\s*:', re.I),
    "row_level_key": re.compile(r'["\']row_level(?:_data|_prediction|_score)?["\']\s*:', re.I),
    "kaggle_private_path": re.compile(r'/kaggle/input/', re.I),
    "windows_user_path": re.compile(r'[a-z]:[\\/]users[\\/][^\s"\']+', re.I),
    "authorization_bearer": re.compile(r'authorization\s*[:=]\s*["\']?bearer\s+[a-z0-9._-]+', re.I),
    "secret_assignment": re.compile(r'(?:api[_-]?key|secret[_-]?key|password)\s*[:=]\s*["\'][^"\']{8,}["\']', re.I),
}


def iter_public_files():
    for root in PUBLIC_ROOTS:
        if root.is_file():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                    yield path


def scan():
    findings = []
    scanned = 0
    for path in sorted(set(iter_public_files())):
        text = path.read_text(encoding="utf-8", errors="ignore")
        scanned += 1
        for name, pattern in FORBIDDEN.items():
            match = pattern.search(text)
            if match:
                findings.append({
                    "file": str(path.relative_to(ROOT)),
                    "rule": name,
                    "snippet": match.group(0)[:120],
                })
    if findings:
        details = "\n".join(f"- {x['file']} [{x['rule']}] {x['snippet']}" for x in findings)
        raise AssertionError(f"Public bundle scan failed:\n{details}")
    print(f"Public/private scan PASS: {scanned} public text files, 0 findings")
    return scanned


if __name__ == "__main__":
    scan()
