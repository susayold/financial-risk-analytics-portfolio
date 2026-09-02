"""Create an account-grain loss proxy after removing exact duplicate rows.

The D2 loss proxy is a BAD-only evidence table.  This utility removes only
byte-for-byte duplicate records, preserves the first occurrence, and emits a
small audit manifest.  It does not resolve conflicting account-level rows;
those remain an explicit review condition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input, low_memory=False)
    required = {"account_id", "actual_default"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"missing required columns: {missing}")

    duplicate_mask = df.duplicated(keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    duplicate_id_groups = int(
        df.loc[df.duplicated("account_id", keep=False), "account_id"].nunique()
    )
    conflicting_ids = int(
        df.groupby("account_id", dropna=False)["actual_default"].nunique(dropna=False).gt(1).sum()
    )

    dedup = df.loc[~duplicate_mask].copy()
    if dedup["account_id"].duplicated().any():
        raise ValueError(
            "non-exact duplicate account_id rows remain; account-grain output is unsafe"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    dedup.to_csv(args.output, index=False)
    audit = {
        "stage": "D2_LOSS_PROXY_EXACT_DEDUP",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_WITH_LIMITATIONS" if conflicting_ids == 0 else "REVIEW_REQUIRED",
        "input_file": args.input.name,
        "input_sha256": sha256(args.input),
        "output_file": args.output.name,
        "output_sha256": sha256(args.output),
        "deduplication_rule": "remove exact duplicate full rows; preserve first occurrence",
        "rows_before": int(len(df)),
        "rows_after": int(len(dedup)),
        "exact_duplicate_rows_removed": duplicate_rows,
        "exact_duplicate_account_id_groups": duplicate_id_groups,
        "non_exact_duplicate_account_ids": int(dedup["account_id"].duplicated().sum()),
        "conflicting_actual_default_ids": conflicting_ids,
        "scope": "BAD-only retrospective loss evidence; not full governed population",
        "claim_boundary": [
            "account-grain only after exact duplicate removal",
            "does not establish governed-core ID coverage",
            "does not add GOOD-row loss evidence",
            "does not create empirical C8E LGD",
        ],
    }
    args.audit_output.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(
        "D2 loss proxy dedup: "
        f"{len(df):,} -> {len(dedup):,} rows; "
        f"removed {duplicate_rows:,} exact duplicates; "
        f"conflicting IDs {conflicting_ids:,}; status {audit['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
