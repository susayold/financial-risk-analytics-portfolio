"""Build the exact Block C governed-population to source/loss bridge for D2.

The accepted source is scanned in chunks and is never copied into the
repository or the published artifact set.  Only account-level bridge evidence
and a compact audit manifest are written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_GOVERNED_ROWS = 1_347_681


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_core(zip_path: Path) -> pd.DataFrame:
    members = [
        "data/development.parquet",
        "data/validation.parquet",
        "data/oot_SEALED_until_C9.parquet",
        "data/historical_shadow_SEALED_until_C9.parquet",
    ]
    parts = []
    with zipfile.ZipFile(zip_path) as archive:
        for member in members:
            with archive.open(member) as handle:
                parts.append(pd.read_parquet(handle, columns=["account_id", "issue_d", "issue_year", "split_name", "actual_default", "loan_amnt"]))
    core = pd.concat(parts, ignore_index=True)
    core["account_id"] = core["account_id"].astype("string").str.strip()
    if core["account_id"].isna().any() or core["account_id"].duplicated().any():
        raise ValueError("Governed core IDs are not unique and non-null")
    return core


def normalize_id(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    return numeric.astype("Int64").astype("string").str.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cumulative-c7", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--loss-proxy", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    core = read_core(args.cumulative_c7)
    core_by_id = core.set_index("account_id", drop=False)
    governed_ids = set(core["account_id"].tolist())

    source_rows = 0
    matched_source_rows = 0
    source_records: list[pd.DataFrame] = []
    source_usecols = ["id", "loan_amnt", "loan_status", "issue_d"]
    for chunk in pd.read_csv(args.source, usecols=source_usecols, chunksize=100_000, low_memory=False):
        source_rows += len(chunk)
        chunk["account_id"] = normalize_id(chunk["id"])
        hit = chunk["account_id"].isin(governed_ids)
        if not hit.any():
            continue
        x = chunk.loc[hit, ["account_id", "loan_amnt", "loan_status", "issue_d"]].copy()
        matched_source_rows += len(x)
        x["source_target"] = np.select(
            [x["loan_status"].fillna("").astype(str).str.contains("Charged Off", regex=False) | x["loan_status"].fillna("").astype(str).eq("Default"),
             x["loan_status"].fillna("").astype(str).str.contains("Fully Paid", regex=False)],
            [1, 0],
            default=pd.NA,
        )
        source_records.append(x)

    if not source_records:
        raise ValueError("No governed IDs matched the accepted source")
    source = pd.concat(source_records, ignore_index=True)
    source["source_target"] = pd.to_numeric(source["source_target"], errors="coerce").astype("Int8")

    grouped = source.groupby("account_id", dropna=False)
    source_summary = grouped.agg(
        source_row_count=("account_id", "size"),
        source_loan_amnt_nunique=("loan_amnt", "nunique"),
        source_target_nunique=("source_target", "nunique"),
        source_resolved_rows=("source_target", lambda s: int(s.notna().sum())),
    ).reset_index()
    first_source = source.sort_values(["account_id", "issue_d"], na_position="last").drop_duplicates("account_id", keep="first")
    source_summary = source_summary.merge(
        first_source[["account_id", "loan_amnt", "loan_status", "issue_d", "source_target"]],
        on="account_id", how="left", validate="one_to_one",
    ).rename(columns={"loan_amnt": "source_loan_amnt", "loan_status": "source_loan_status", "issue_d": "source_issue_d", "source_target": "source_target_first"})
    bridge = core[["account_id", "issue_d", "issue_year", "split_name", "actual_default", "loan_amnt"]].merge(
        source_summary, on="account_id", how="left", validate="one_to_one",
    ).rename(columns={"loan_amnt": "core_loan_amnt"})
    bridge["id_match_flag"] = np.where(bridge["source_row_count"].notna(), "MATCHED", "NOT_MATCHED")
    bridge["target_concordance_flag"] = np.select(
        [bridge["source_target_nunique"].isna(), bridge["source_target_nunique"].gt(1), bridge["source_target_first"].isna()],
        ["UNRESOLVED_SOURCE_STATUS", "CONFLICTING_SOURCE_TARGET", "UNRESOLVED_SOURCE_STATUS"],
        default=np.where(bridge["actual_default"].eq(bridge["source_target_first"]), "MATCHED", "TARGET_MISMATCH"),
    )
    bridge["loan_amount_concordance_flag"] = np.select(
        [bridge["source_loan_amnt_nunique"].isna(), bridge["source_loan_amnt_nunique"].gt(1), bridge["source_loan_amnt"].isna(), bridge["core_loan_amnt"].isna()],
        ["NOT_MATCHED", "CONFLICTING_SOURCE_LOAN_AMOUNT", "SOURCE_LOAN_AMOUNT_MISSING", "CORE_LOAN_AMOUNT_MISSING"],
        default=np.where(np.isclose(bridge["core_loan_amnt"].astype(float), bridge["source_loan_amnt"].astype(float), equal_nan=False), "MATCHED", "LOAN_AMOUNT_MISMATCH"),
    )

    loss = pd.read_csv(args.loss_proxy, dtype={"account_id": "string"}, low_memory=False)
    loss["account_id"] = loss["account_id"].astype("string").str.strip()
    loss_bad = set(loss.loc[loss["actual_default"].eq(1), "account_id"].tolist())
    bridge["loss_evidence_flag"] = np.where(
        bridge["actual_default"].eq(1),
        np.where(bridge["account_id"].isin(loss_bad), "BAD_MATCHED", "BAD_NOT_MATCHED"),
        "GOOD_NOT_APPLICABLE",
    )

    # Keep D4 on the exact governed BAD population. The full accepted source
    # has a small number of resolved BAD records outside the Block C governed
    # population; those are valid source evidence but must not enter the D4
    # bridge for this project.
    bad_loss_bridge = loss.loc[loss["actual_default"].eq(1)].merge(
        core[["account_id", "issue_year", "split_name", "loan_amnt"]].rename(columns={"loan_amnt": "core_loan_amnt"}),
        on="account_id", how="inner", validate="one_to_one",
    )
    bad_loss_bridge.to_csv(out / "D2_GOVERNED_BAD_LOSS_EVIDENCE.csv", index=False)

    bridge_output = bridge[[
        "account_id", "issue_d", "issue_year", "split_name", "actual_default", "core_loan_amnt",
        "source_row_count", "source_loan_amnt", "source_loan_status", "source_issue_d", "source_target_first",
        "id_match_flag", "target_concordance_flag", "loan_amount_concordance_flag", "loss_evidence_flag",
    ]].sort_values("account_id")
    bridge_output.to_csv(out / "D2_GOVERNED_CORE_BRIDGE.csv", index=False)

    source_duplicate_ids = int(source_summary["source_row_count"].gt(1).sum())
    matched_ids = int(bridge["id_match_flag"].eq("MATCHED").sum())
    resolved_ids = int(bridge["source_target_first"].notna().sum())
    target_matched = int(bridge["target_concordance_flag"].eq("MATCHED").sum())
    target_conflicts = int(bridge["target_concordance_flag"].eq("CONFLICTING_SOURCE_TARGET").sum())
    target_mismatch = int(bridge["target_concordance_flag"].eq("TARGET_MISMATCH").sum())
    loan_matched = int(bridge["loan_amount_concordance_flag"].eq("MATCHED").sum())
    bad_core = bridge["actual_default"].eq(1)
    bad_loss_matched = int((bad_core & bridge["loss_evidence_flag"].eq("BAD_MATCHED")).sum())
    checks = [
        {"check_id": "D2-B01", "check": "full governed population row count", "expected": EXPECTED_GOVERNED_ROWS, "observed": int(len(core)), "status": "PASS" if len(core) == EXPECTED_GOVERNED_ROWS else "REVIEW_REQUIRED"},
        {"check_id": "D2-B02", "check": "governed IDs matched in accepted source", "expected": EXPECTED_GOVERNED_ROWS, "observed": matched_ids, "status": "PASS" if matched_ids == EXPECTED_GOVERNED_ROWS else "REVIEW_REQUIRED"},
        {"check_id": "D2-B03", "check": "source duplicate ID groups", "expected": 0, "observed": source_duplicate_ids, "status": "PASS" if source_duplicate_ids == 0 else "REVIEW_REQUIRED"},
        {"check_id": "D2-B04", "check": "resolved source target concordance", "expected": resolved_ids, "observed": target_matched, "status": "PASS" if target_matched == resolved_ids and target_conflicts == 0 and target_mismatch == 0 else "REVIEW_REQUIRED"},
        {"check_id": "D2-B05", "check": "core/source loan amount concordance", "expected": matched_ids, "observed": loan_matched, "status": "PASS" if loan_matched == matched_ids else "REVIEW_REQUIRED"},
        {"check_id": "D2-B06", "check": "BAD core to loss evidence coverage", "expected": int(bad_core.sum()), "observed": bad_loss_matched, "status": "PASS" if bad_loss_matched == int(bad_core.sum()) else "REVIEW_REQUIRED"},
    ]
    audit = {
        "stage": "D2_GOVERNED_CORE_BRIDGE",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_WITH_LIMITATIONS" if all(x["status"] == "PASS" for x in checks) else "REVIEW_REQUIRED",
        "input_files": [args.cumulative_c7.name, args.source.name, args.loss_proxy.name],
        "input_checksums": {p.name: sha256(p) for p in [args.cumulative_c7, args.source, args.loss_proxy]},
        "row_counts": {"governed_core_rows": int(len(core)), "source_rows_scanned": source_rows, "matched_source_rows": matched_source_rows, "matched_governed_ids": matched_ids, "resolved_source_ids": resolved_ids, "core_bad_rows": int(bad_core.sum()), "bad_loss_matched": bad_loss_matched},
        "duplicate_and_conflict_counts": {"source_duplicate_id_groups": source_duplicate_ids, "conflicting_source_target_ids": target_conflicts, "target_mismatch_ids": target_mismatch, "source_duplicate_loan_amount_ids": int(source_summary["source_loan_amnt_nunique"].gt(1).sum())},
        "checks": checks,
        "outputs": ["D2_GOVERNED_CORE_BRIDGE.csv", "D2_GOVERNED_CORE_BRIDGE_AUDIT.json", "D2_GOVERNED_BAD_LOSS_EVIDENCE.csv"],
        "claim_boundary": ["exact ID bridge is at governed account grain", "Historical Shadow is included for population reconciliation but is monitor-only", "retrospective loss evidence is BAD-only", "this bridge does not create a verified 12-month PD or regulatory LGD"],
    }
    (out / "D2_GOVERNED_CORE_BRIDGE_AUDIT.json").write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    print(f"D2 governed bridge: {matched_ids:,}/{len(core):,} IDs matched; target {target_matched:,}/{resolved_ids:,}; loan amount {loan_matched:,}/{matched_ids:,}; status {audit['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
