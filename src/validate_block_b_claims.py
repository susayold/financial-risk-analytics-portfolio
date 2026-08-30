"""Validate required public claim boundaries without inspecting row-level data."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--repo-root", type=Path, required=True); args = parser.parse_args()
    files = [args.repo_root / "block-b" / "index.html"] + [args.repo_root / "docs" / f"B{x}_RUN_REPORT.md" for x in (6, 7, 8, 9)]
    missing = [str(p) for p in files if not p.exists()]
    content = "\n".join(p.read_text(encoding="utf-8") for p in files if p.exists())
    required = {
        "not_12_month_pd": bool(re.search(r"not (?:verified |a )?12-month PD|not [^\.\n]{0,40}12-month PD", content, re.I)),
        "descriptive_not_causal": bool(re.search(r"not causal|not a causal|not predictive", content, re.I)),
        "issue_d_authority": "issue_d" in content,
        "pricing_boundary": bool(re.search(r"pricing.{0,100}(?:boundary|not mixed|absent|supplemental)", content, re.I | re.S)),
    }
    status = "PASS" if not missing and all(required.values()) else "FAIL"
    print(json.dumps({"status": status, "files_checked": [str(p) for p in files], "missing_files": missing, "required_boundary_checks": required}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__": raise SystemExit(main())
