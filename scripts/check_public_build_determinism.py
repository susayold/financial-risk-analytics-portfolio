"""Verify that two consecutive public-data builds are byte-for-byte deterministic."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "public" / "data"
BUILD = ROOT / "scripts" / "build_all_public_data.py"


def snapshot() -> dict[str, str]:
    files = sorted(path for path in DATA.rglob("*") if path.is_file())
    return {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in files
    }


def main() -> None:
    subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, check=True)
    first = snapshot()
    subprocess.run([sys.executable, str(BUILD)], cwd=ROOT, check=True)
    second = snapshot()

    changed = {
        name: (first.get(name), second.get(name))
        for name in sorted(set(first) | set(second))
        if first.get(name) != second.get(name)
    }
    if changed:
        details = "\n".join(f"- {name}: {before} -> {after}" for name, (before, after) in changed.items())
        raise AssertionError(f"Public build is not deterministic:\n{details}")

    print(f"Deterministic build PASS: {len(second)} public/data files stable across consecutive builds")


if __name__ == "__main__":
    main()
