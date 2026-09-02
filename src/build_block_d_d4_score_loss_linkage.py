"""Build a bounded descriptive score-to-loss linkage for D4 review."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    weight = position - lower
    return values[lower] + (values[upper] - values[lower]) * weight


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score-mart", type=Path, required=True)
    parser.add_argument("--loss-evidence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    scores: dict[str, dict[str, str]] = {}
    score_rows = 0
    score_bad_rows = 0
    with args.score_mart.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            score_rows += 1
            if row["actual_default"] == "1":
                score_bad_rows += 1
                scores[row["account_id"]] = row

    groups: dict[tuple[str, str, str], list[dict[str, float]]] = defaultdict(list)
    matched = 0
    target_mismatches = 0
    quality_counts: dict[str, int] = defaultdict(int)
    with args.loss_evidence.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            score = scores.get(row["account_id"])
            if score is None:
                continue
            matched += 1
            target_mismatches += int(score["actual_default"] != "1" or row["actual_default"] != "1")
            quality_counts[row["loss_data_quality_status"]] += 1
            key = (score["split_name"], score["risk_band"], score["risk_decile"])
            groups[key].append(
                {
                    "p_bad_final": float(score["p_bad_final"]),
                    "lgd": float(row["retrospective_lgd_proxy_model"]),
                    "ead": float(score["ead_origination_proxy"]),
                }
            )

    output = args.output_dir / "D4_SCORE_CONDITIONAL_LOSS_LINKAGE.csv"
    fields = [
        "split_name", "risk_band", "risk_decile", "scored_bad_rows",
        "coverage_of_scored_bad", "mean_p_bad_final", "mean_lgd_proxy",
        "median_lgd_proxy", "lgd_q25", "lgd_q75", "mean_ead_origination_proxy",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for (split, band, decile), rows in sorted(groups.items()):
            lgd = [item["lgd"] for item in rows]
            writer.writerow(
                {
                    "split_name": split,
                    "risk_band": band,
                    "risk_decile": decile,
                    "scored_bad_rows": len(rows),
                    "coverage_of_scored_bad": f"{len(rows) / score_bad_rows:.12f}",
                    "mean_p_bad_final": f"{sum(item['p_bad_final'] for item in rows) / len(rows):.12f}",
                    "mean_lgd_proxy": f"{sum(lgd) / len(lgd):.12f}",
                    "median_lgd_proxy": f"{quantile(lgd, 0.50):.12f}",
                    "lgd_q25": f"{quantile(lgd, 0.25):.12f}",
                    "lgd_q75": f"{quantile(lgd, 0.75):.12f}",
                    "mean_ead_origination_proxy": f"{sum(item['ead'] for item in rows) / len(rows):.6f}",
                }
            )

    audit = {
        "stage": "D4_SCORE_CONDITIONAL_LINKAGE",
        "status": "PASS_WITH_LIMITATIONS",
        "scope": "descriptive current D1 scored-BAD rows joined to governed retrospective BAD loss evidence",
        "score_rows": score_rows,
        "score_bad_rows": score_bad_rows,
        "matched_scored_bad_rows": matched,
        "coverage": matched / score_bad_rows if score_bad_rows else 0.0,
        "target_mismatch_rows": target_mismatches,
        "group_rows": len(groups),
        "loss_quality_counts": dict(sorted(quality_counts.items())),
        "outputs": [output.name],
        "claim_boundary": [
            "descriptive score-to-loss linkage only",
            "not an empirical C8E LGD model",
            "not an approved main-case LGD input",
            "not a regulatory LGD or expected-loss claim",
        ],
    }
    (args.output_dir / "D4_SCORE_CONDITIONAL_LINKAGE_AUDIT.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"D4 score-to-loss linkage PASS_WITH_LIMITATIONS — "
        f"{matched}/{score_bad_rows} matched; {len(groups)} groups"
    )


if __name__ == "__main__":
    main()
