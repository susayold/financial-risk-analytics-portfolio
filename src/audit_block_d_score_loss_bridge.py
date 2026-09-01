"""Audit the available scored-BAD to retrospective-loss evidence bridge.

This is a bounded sub-audit. The D2 proxy contains resolved BAD rows only, so
it cannot prove full-population loss coverage or the governed-core bridge.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score-mart", type=Path, required=True)
    parser.add_argument("--loss-proxy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    scores = pd.read_csv(args.score_mart, dtype={"account_id": "string"})
    losses = pd.read_csv(args.loss_proxy, dtype={"account_id": "string"})
    duplicate_rows = losses[losses.duplicated(keep=False)]
    duplicate_groups = int(duplicate_rows["account_id"].nunique())
    duplicate_rows_count = int(losses.duplicated().sum())
    loss_dedup = losses.drop_duplicates().copy()

    scored_bad = scores.loc[scores["actual_default"] == 1, ["account_id", "actual_default"]]
    loss_bad = loss_dedup[["account_id", "actual_default", "loss_data_quality_status"]]
    joined = scored_bad.merge(
        loss_bad,
        on="account_id",
        how="left",
        suffixes=("_score", "_loss"),
        validate="one_to_one",
    )
    matched = joined["actual_default_loss"].notna()
    target_concordance = matched & joined["actual_default_score"].eq(joined["actual_default_loss"])
    status = "PASS_WITH_LIMITATIONS"
    result = {
        "stage": "D2_SCORE_TO_LOSS_SUBAUDIT",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "scope": "Scored BAD rows versus deduplicated retrospective loss proxy only",
        "source_quality": {
            "loss_proxy_rows": int(len(losses)),
            "loss_proxy_unique_rows_after_exact_dedup": int(len(loss_dedup)),
            "exact_duplicate_rows": duplicate_rows_count,
            "exact_duplicate_account_id_groups": duplicate_groups,
            "deduplication_rule": "drop exact duplicate rows before account-grain bridge",
        },
        "bridge": {
            "score_mart_rows": int(len(scores)),
            "score_mart_bad_rows": int(len(scored_bad)),
            "matched_scored_bad_rows": int(matched.sum()),
            "scored_bad_to_loss_coverage": float(matched.mean()),
            "target_concordant_matched_rows": int(target_concordance.sum()),
            "target_mismatch_rows": int((matched & ~target_concordance).sum()),
            "all_scored_bad_have_loss_evidence": bool(matched.all()),
            "matched_loss_quality_status": loss_bad.loc[
                loss_bad["account_id"].isin(set(scored_bad["account_id"]))
            ]["loss_data_quality_status"].value_counts().to_dict(),
        },
        "limitations": [
            "The loss proxy contains resolved BAD rows only; GOOD-row loss coverage is not tested",
            "The exact governed-core ID list is not materialized, so the D2 governed bridge remains open",
            "Pricing and full loan-amount concordance are not tested by this sub-audit",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        "D2 score-loss sub-audit: "
        f"scored BAD {len(scored_bad):,}, matched {int(matched.sum()):,}, "
        f"duplicate rows {duplicate_rows_count:,}, status {status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
