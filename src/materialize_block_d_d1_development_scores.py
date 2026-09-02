"""Materialize Development scores using the frozen Block C C8E model.

This is deliberately a replay of the persisted C9 C8E model on the matched
Development population.  It does not fit a model, use OOT data, or publish
the raw LendingClub source.  The raw source is read from a temporary D-drive
runtime and the output contains scores plus audit fields only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier


RICH_ALLOWLIST = [
    "inq_last_6mths", "acc_open_past_24mths", "bc_util", "bc_open_to_buy",
    "avg_cur_bal", "tot_cur_bal", "tot_hi_cred_lim", "total_bal_ex_mort",
    "total_bc_limit", "total_rev_hi_lim", "num_accts_ever_120_pd",
    "num_tl_90g_dpd_24m", "pct_tl_nvr_dlq", "percent_bc_gt_75",
    "mths_since_recent_inq", "mths_since_last_delinq",
    "mths_since_last_major_derog", "mo_sin_old_rev_tl_op",
    "mo_sin_rcnt_tl", "mo_sin_rcnt_rev_tl_op", "num_actv_bc_tl",
    "num_actv_rev_tl", "num_bc_tl", "num_il_tl", "num_rev_accts",
    "num_sats", "num_tl_op_past_12m", "delinq_2yrs",
    "collections_12_mths_ex_med", "chargeoff_within_12_mths", "tax_liens",
    "tot_coll_amt", "total_il_high_credit_limit", "title",
]

FORBIDDEN = {
    "loan_status", "recoveries", "collection_recovery_fee", "total_pymnt",
    "total_pymnt_inv", "total_rec_prncp", "total_rec_int", "last_pymnt_d",
    "last_pymnt_amnt", "out_prncp", "out_prncp_inv", "next_pymnt_d",
    "last_credit_pull_d", "settlement_status", "settlement_amount",
    "settlement_percentage", "settlement_term",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def key_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()


def parse_percent_like(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    return pd.to_numeric(
        series.astype(str).str.replace("%", "", regex=False).str.strip(),
        errors="coerce",
    )


def engineer(df: pd.DataFrame, rich_cols: list[str]) -> pd.DataFrame:
    for col in [
        "total_acc", "open_acc", "pub_rec", "pub_rec_bankruptcies", "revol_bal",
        "mort_acc", "installment", "time_to_earliest_cr_line",
        "fico_range_low", "fico_range_high",
    ]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["revol_util", "int_rate", "bc_util", "pct_tl_nvr_dlq", "percent_bc_gt_75"]:
        if col in df:
            df[col] = parse_percent_like(df[col])

    for col in rich_cols:
        if col != "title" and col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    eps = 1.0
    df["loan_to_income"] = df["loan_amnt"] / df["revenue"].clip(lower=eps)
    df["log_revenue"] = np.log1p(df["revenue"].clip(lower=0))
    df["log_loan_amnt"] = np.log1p(df["loan_amnt"].clip(lower=0))
    df["fico_x_dti"] = df["fico_n"] * df["dti_n"]

    if "open_acc" in df and "total_acc" in df:
        df["open_to_total_acc"] = df["open_acc"] / df["total_acc"].replace(0, np.nan)
    if "revol_bal" in df:
        df["revol_bal_to_income"] = df["revol_bal"] / df["revenue"].clip(lower=eps)
    if "pub_rec" in df:
        df["has_public_record"] = (df["pub_rec"].fillna(0) > 0).astype(int)
    if "pub_rec_bankruptcies" in df:
        df["has_bankruptcy"] = (df["pub_rec_bankruptcies"].fillna(0) > 0).astype(int)
    if "installment" in df:
        df["installment_to_income"] = 12 * df["installment"] / df["revenue"].clip(lower=eps)
        df["installment_to_loan"] = df["installment"] / df["loan_amnt"].replace(0, np.nan)
    if "revol_util" in df:
        df["fico_x_revol_util"] = df["fico_n"] * df["revol_util"]
        df["dti_x_revol_util"] = df["dti_n"] * df["revol_util"]
    if "revol_bal" in df and "open_acc" in df:
        df["revol_bal_per_open_acc"] = df["revol_bal"] / df["open_acc"].replace(0, np.nan)
    if "mort_acc" in df:
        df["has_mortgage_account"] = (df["mort_acc"].fillna(0) > 0).astype(int)
    if "time_to_earliest_cr_line" in df:
        df["credit_history_log"] = np.log1p(df["time_to_earliest_cr_line"].clip(lower=0))
    if "fico_range_low" in df and "fico_range_high" in df:
        df["fico_source_midpoint"] = (df["fico_range_low"] + df["fico_range_high"]) / 2
        df["fico_source_width"] = df["fico_range_high"] - df["fico_range_low"]

    if "bc_open_to_buy" in df and "total_bc_limit" in df:
        df["bc_available_ratio"] = df["bc_open_to_buy"] / df["total_bc_limit"].replace(0, np.nan)
    if "total_bal_ex_mort" in df:
        df["nonmort_balance_to_income"] = df["total_bal_ex_mort"] / df["revenue"].clip(lower=eps)
    if "tot_cur_bal" in df:
        df["total_balance_to_income"] = df["tot_cur_bal"] / df["revenue"].clip(lower=eps)
    if "acc_open_past_24mths" in df and "open_acc" in df:
        df["recent_open_share"] = df["acc_open_past_24mths"] / df["open_acc"].replace(0, np.nan)
    if "num_tl_op_past_12m" in df and "open_acc" in df:
        df["very_recent_open_share"] = df["num_tl_op_past_12m"] / df["open_acc"].replace(0, np.nan)
    if "inq_last_6mths" in df:
        df["inquiry_pressure"] = np.log1p(df["inq_last_6mths"].clip(lower=0))
    if "num_tl_90g_dpd_24m" in df:
        df["has_recent_90dpd"] = (df["num_tl_90g_dpd_24m"].fillna(0) > 0).astype(int)
    if "num_accts_ever_120_pd" in df:
        df["has_ever_120pd"] = (df["num_accts_ever_120_pd"].fillna(0) > 0).astype(int)
    return df


def prepare_x(df: pd.DataFrame, features: list[str], cat_indices: list[int]) -> pd.DataFrame:
    out = df[features].copy()
    categorical = {features[i] for i in cat_indices}
    for col in features:
        if col in categorical:
            out[col] = out[col].astype("string").fillna("UNKNOWN").astype(str)
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def read_core(dev_path: Path) -> pd.DataFrame:
    columns = [
        "account_id", "issue_d", "issue_year", "actual_default", "revenue", "dti_n",
        "loan_amnt", "fico_n", "experience_c", "emp_length", "purpose",
        "home_ownership_n",
    ]
    dev = pd.read_parquet(dev_path, columns=columns)
    dev["split_name"] = "Development"
    dev["account_id_key"] = key_series(dev["account_id"])
    if not dev["account_id"].is_unique:
        raise ValueError("Governed Development account_id is not unique")
    return dev


def read_reduced(train_path: Path, test_path: Path) -> pd.DataFrame:
    train = pd.read_csv(train_path, low_memory=False)
    test = pd.read_csv(test_path, low_memory=False)
    reduced = pd.concat([train, test], ignore_index=True)
    reduced.columns = [str(col).strip().lower() for col in reduced.columns]
    reduced["account_id_key"] = key_series(reduced["id"])
    return reduced.drop_duplicates("account_id_key")


def read_rich(full_path: Path, wanted_ids: pd.Series) -> tuple[pd.DataFrame, list[str]]:
    if set(RICH_ALLOWLIST) & FORBIDDEN:
        raise ValueError("Forbidden feature entered rich allowlist")
    con = duckdb.connect(database=":memory:")
    sql_path = str(full_path).replace("'", "''")
    schema = con.execute(
        f"DESCRIBE SELECT * FROM read_csv_auto('{sql_path}', header=true, "
        "all_varchar=true, sample_size=20000, ignore_errors=true)"
    ).df()
    available = set(schema["column_name"].astype(str))
    rich_cols = [col for col in RICH_ALLOWLIST if col in available]
    if "id" not in available:
        raise ValueError("Full accepted source has no id column")
    wanted = pd.DataFrame({"account_id_key": wanted_ids.astype(str).unique()})
    con.register("wanted_ids", wanted)
    select = ["regexp_replace(CAST(f.id AS VARCHAR), '\\.0$', '') AS account_id_key"]
    select += [f'f."{col}" AS "{col}"' for col in rich_cols]
    projection = ",\n".join(select)
    rich = con.execute(
        f"SELECT {projection} FROM read_csv_auto('{sql_path}', header=true, "
        "all_varchar=true, sample_size=20000, ignore_errors=true) AS f "
        "INNER JOIN wanted_ids w ON regexp_replace(CAST(f.id AS VARCHAR), '\\.0$', '') "
        "= w.account_id_key"
    ).df()
    con.close()
    return rich.drop_duplicates("account_id_key"), rich_cols


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-parquet", type=Path, required=True)
    parser.add_argument("--train-csv", type=Path, required=True)
    parser.add_argument("--test-csv", type=Path, required=True)
    parser.add_argument("--full-csv", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--loss-proxy", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-json", type=Path, required=True)
    args = parser.parse_args()

    dev = read_core(args.dev_parquet)
    reduced = read_reduced(args.train_csv, args.test_csv)
    merged = dev.merge(reduced, on="account_id_key", how="inner", validate="one_to_one")
    authority = [
        "issue_d", "issue_year", "actual_default", "revenue", "dti_n", "loan_amnt",
        "fico_n", "experience_c", "emp_length", "purpose", "home_ownership_n",
    ]
    for col in authority:
        if f"{col}_x" in merged:
            merged[col] = merged[f"{col}_x"]
    merged["issue_d"] = pd.to_datetime(merged["issue_d"])

    rich, rich_cols = read_rich(args.full_csv, merged["account_id_key"])
    df = merged.merge(rich, on="account_id_key", how="left", validate="one_to_one")
    df = engineer(df, rich_cols)

    model = CatBoostClassifier()
    model.load_model(str(args.model))
    features = list(model.feature_names_)
    cat_indices = list(model.get_cat_feature_indices())
    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Frozen model features missing after replay: {missing}")
    X = prepare_x(df, features, cat_indices)
    prediction = model.predict_proba(X)[:, 1]

    pricing_required = ["term", "installment", "int_rate"]
    pricing_match = df[pricing_required].notna().all(axis=1)
    grade_derived = (
        df["sub_grade"].astype("string").str.strip().str[0]
        if "sub_grade" in df
        else pd.Series(pd.NA, index=df.index, dtype="string")
    )
    loss_ids: set[str] = set()
    if args.loss_proxy and args.loss_proxy.exists():
        loss = pd.read_csv(args.loss_proxy, usecols=["account_id", "actual_default"])
        loss_ids = set(key_series(loss.loc[loss["actual_default"].eq(1), "account_id"]))

    out = pd.DataFrame({
        "account_id": df["account_id"].astype(str),
        "issue_d": df["issue_d"].dt.strftime("%Y-%m-%d"),
        "issue_year": pd.to_numeric(df["issue_year"], errors="coerce").astype("Int64"),
        "split_name": "Development",
        "actual_default": pd.to_numeric(df["actual_default"], errors="coerce").astype(int),
        "p_bad_final": prediction,
        "model_version": "C8E_RICH_BUREAU_CATBOOST_79F",
        "model_feature_count": len(features),
        "population_scope": "P1_C8E_ENRICHED_MATCHED_DEVELOPMENT",
        "term": df["term"].astype("string") if "term" in df else pd.NA,
        "int_rate": pd.to_numeric(df["int_rate"], errors="coerce") if "int_rate" in df else pd.NA,
        "installment": pd.to_numeric(df["installment"], errors="coerce") if "installment" in df else pd.NA,
        "sub_grade": df["sub_grade"].astype("string") if "sub_grade" in df else pd.NA,
        "grade_derived": grade_derived,
        "application_type": df["application_type"].astype("string") if "application_type" in df else pd.NA,
        "pricing_match_flag": np.where(pricing_match, "MATCHED", "MISSING_REQUIRED_PRICING"),
        "loss_evidence_match_flag": np.where(
            df["actual_default"].eq(1),
            np.where(key_series(df["account_id"]).isin(loss_ids), "BAD_MATCHED", "BAD_NOT_MATCHED"),
            "GOOD_NOT_APPLICABLE",
        ),
    })
    out = out.sort_values("account_id").reset_index(drop=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_json.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)

    audit = {
        "stage": "D1_DEVELOPMENT_SCORE_MATERIALIZATION",
        "status": "PASS_WITH_LIMITATIONS",
        "model": "C8E_RICH_BUREAU_CATBOOST_79F",
        "model_sha256": sha256(args.model),
        "model_feature_count": len(features),
        "model_features": features,
        "cat_feature_indices": cat_indices,
        "raw_source_path": str(args.full_csv),
        "raw_source_sha256": sha256(args.full_csv),
        "raw_source_published": False,
        "input_governed_dev_rows": int(len(dev)),
        "reduced_source_matched_dev_rows": int(len(merged)),
        "rich_source_matched_rows": int(len(rich)),
        "output_rows": int(len(out)),
        "output_sha256": sha256(args.output),
        "pricing_match_rows": int(pricing_match.sum()),
        "pricing_required_fields": pricing_required,
        "pricing_match_rate": float(pricing_match.mean()),
        "loss_bad_match_rows": int(((out["actual_default"] == 1) & (out["loss_evidence_match_flag"] == "BAD_MATCHED")).sum()),
        "loss_bad_rows": int((out["actual_default"] == 1).sum()),
        "claim_boundary": [
            "Development scores are replayed from the frozen C8E/C9 model; no fitting occurs in D1.",
            "Scores cover the enriched matched Development population, not all governed Development accounts.",
            "actual_default remains final-resolution observed BAD/GOOD, not verified fixed-horizon PD.",
            "Raw accepted LendingClub source is temporary D-drive runtime only and is not published.",
        ],
    }
    args.audit_json.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
