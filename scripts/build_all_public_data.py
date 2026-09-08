"""Run all seven CRD.PI public-data builders in order."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

BUILDERS = [
    "build_page01_public_data.py",
    "build_page02_public_data.py",
    "build_page03_public_data.py",
    "build_page04_public_data.py",
    "build_page05_public_data.py",
    "build_page06_public_data.py",
    "build_page07_public_data.py",
]


def main():
    for name in BUILDERS:
        path = SCRIPTS / name
        if not path.exists():
            raise FileNotFoundError(path)
        print(f"[build] {name}")
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)
    print("[build] all seven public-data contracts completed")


if __name__ == "__main__":
    main()
