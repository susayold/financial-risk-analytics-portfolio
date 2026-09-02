"""Verify every evidence checksum recorded by the Block D9 manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "block-d" / "D9_CLOSURE" / "D9_CLOSURE_REVIEW_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    block_dir = args.manifest.parent.parent
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    failures: list[str] = []
    checked = 0
    for key, item in manifest.get("evidence_checksums", {}).items():
        checked += 1
        relative = Path(item["file"])
        evidence = block_dir / relative
        if not evidence.is_file():
            failures.append(f"{key}: missing {item['file']}")
            continue
        actual = sha256(evidence)
        if actual != item.get("sha256"):
            failures.append(f"{key}: checksum mismatch for {item['file']}")

    print(f"D9 checksum entries: {checked}")
    print(f"D9 checksum failures: {len(failures)}")
    for failure in failures:
        print(f"ERROR: {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
