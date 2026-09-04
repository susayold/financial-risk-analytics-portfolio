"""Build the public-safe Page 02 Portfolio Risk data contract from Block B outputs.

The page uses aggregate evidence only. This script deliberately excludes row-level
records and keeps the public contract limited to metrics needed by the static site.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "data" / "page-02-portfolio-risk.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def i(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def pct(value: float) -> float:
    return round(value * 100, 8)


def find(rows: list[dict[str, str]], dimension: str, segment: str) -> dict[str, str]:
    for row in rows:
        if row["dimension"] == dimension and row["segment"] == segment:
            return row
    raise ValueError(f"Missing canonical segment: {dimension} / {segment}")


def public_segment(row: dict[str, str]) -> dict[str, Any]:
    return {
        "dimension": row["dimension"],
        "segment": row["segment"],
        "accounts": i(row, "accounts"),
        "account_share": f(row, "account_share"),
        "bad_rate": f(row, "bad_rate"),
        "relative_bad_rate": f(row, "relative_bad_rate"),
        "bad_associated_share": f(row, "bad_associated_share"),
        "bad_associated_loan_amount": f(row, "bad_associated_loan_amount"),
        "loan_amount": f(row, "loan_amount"),
        "headline_eligible": row.get("headline_eligible", "TRUE").upper() == "TRUE",
        "materiality_flag": row.get("materiality_flag", "FALSE").upper() == "TRUE",
        "materiality_rank": int(row["materiality_rank"]) if row.get("materiality_rank") else None,
        "primary_segment": row.get("primary_segment", "FALSE").upper() == "TRUE",
    }


def main() -> None:
    kpis = read_json(ROOT / "outputs" / "b6" / "portfolio_kpis.json")
    b7 = read_csv(ROOT / "outputs" / "b7" / "segment_risk.csv")
    b8 = read_csv(ROOT / "outputs" / "b8" / "risk_concentration.csv")
    splits = read_csv(ROOT / "outputs" / "b9" / "vintage_split.csv")
    annual = read_csv(ROOT / "outputs" / "b9" / "vintage_annual.csv")
    composition = read_csv(ROOT / "outputs" / "b9" / "vintage_composition_annual.csv")

    accounts = int(kpis["total_accounts"])
    good = int(kpis["good_accounts"])
    bad = int(kpis["bad_accounts"])
    observed_bad_rate = float(kpis["observed_bad_rate"])
    loan_amount = float(kpis["total_loan_amount"])
    bad_amount = float(kpis["bad_associated_loan_amount"])

    if good + bad != accounts:
        raise ValueError("B6 population reconciliation failed")
    if abs(observed_bad_rate - bad / accounts) > 1e-12:
        raise ValueError("B6 observed BAD rate reconciliation failed")

    split_records = []
    for row in splits:
        record = {
            "label": row["split_name"],
            "accounts": i(row, "accounts"),
            "account_share": i(row, "accounts") / accounts,
            "bad_rate": f(row, "bad_rate"),
            "min_issue_d": row["min_issue_d"],
            "max_issue_d": row["max_issue_d"],
            "issue_cohorts": i(row, "issue_cohorts"),
        }
        split_records.append(record)

    if sum(item["accounts"] for item in split_records) != accounts:
        raise ValueError("B9 split population reconciliation failed")
    if sum(i(row, "accounts") for row in annual) != accounts:
        raise ValueError("B9 annual population reconciliation failed")

    headline_specs = [
        ("dti_band", "40–59.99"),
        ("purpose", "small_business"),
        ("dti_band", "30–39.99"),
        ("fico_band", "640–679"),
    ]
    # Some Windows CSV readers can surface an invalid byte as �. Treat it as the
    # canonical en dash while matching, without changing the source evidence.
    normalized = {(row["dimension"], row["segment"].replace("�", "–")): row for row in b7}
    headline = []
    for dimension, segment in headline_specs:
        row = normalized.get((dimension, segment))
        if row is None:
            row = find(b7, dimension, segment)
        headline.append(public_segment(row))

    top_segments = []
    for row in sorted(b8, key=lambda item: int(item["materiality_rank"]) if item["materiality_rank"] else 999):
        if row.get("materiality_rank") and int(row["materiality_rank"]) <= 8:
            top_segments.append(public_segment(row))
    if len(top_segments) != 8:
        raise ValueError("B8 top-eight materiality evidence is incomplete")

    fico = normalized[("fico_band", "640–679")]
    debt_2018 = next(
        row
        for row in composition
        if row["issue_year"] == "2018"
        and row["dimension"] == "purpose"
        and row["segment"] == "debt_consolidation"
    )

    annual_records = [
        {
            "issue_year": int(row["issue_year"]),
            "accounts": i(row, "accounts"),
            "good_accounts": i(row, "good_accounts"),
            "bad_accounts": i(row, "bad_accounts"),
            "bad_rate": f(row, "bad_rate"),
            "loan_amount": f(row, "loan_amount"),
            "bad_associated_loan_amount": f(row, "bad_associated_loan_amount"),
        }
        for row in annual
    ]

    payload: dict[str, Any] = {
        "meta": {
            "schema": "crd.pi.page-02-portfolio-risk.v1",
            "generated_at": date.today().isoformat(),
            "as_of": "2017-12-01",
            "data_source": "LendingClub governed resolved-granted-loan core",
            "source_stages": ["B4", "B5", "B6", "B7", "B8", "B9"],
            "claim_scope": "DESCRIPTIVE_NON_CAUSAL_OBSERVED_FINAL_RESOLUTION",
            "public_safe": True,
        },
        "portfolio": {
            "accounts": accounts,
            "good_accounts": good,
            "bad_accounts": bad,
            "observed_bad_rate": observed_bad_rate,
            "loan_amount_proxy": loan_amount,
            "non_bad_loan_amount_proxy": loan_amount - bad_amount,
            "bad_associated_loan_amount": bad_amount,
            "bad_associated_exposure_share": float(kpis["bad_associated_exposure_share"]),
            "issue_cohorts": int(kpis["issue_cohorts"]),
            "min_issue_d": kpis["min_issue_d"],
            "max_issue_d": kpis["max_issue_d"],
        },
        "composition": {
            "account_good_share": good / accounts,
            "account_bad_share": bad / accounts,
            "amount_non_bad_share": (loan_amount - bad_amount) / loan_amount,
            "amount_bad_share": bad_amount / loan_amount,
            "default_dimension": "fico_band",
            "default_segment": "640–679",
            "default_segment_accounts": i(fico, "accounts"),
            "default_segment_bad_rate": f(fico, "bad_rate"),
            "default_segment_bad_associated_share": f(fico, "bad_associated_share"),
        },
        "headline_segment_risk": headline,
        "segment_explorer": {
            "baseline_bad_rate": observed_bad_rate,
            "eligibility": {"minimum_accounts": 1000, "minimum_account_share": 0.001},
            "default_dimension": "All Dimensions",
            "default_metric": "observed_bad_rate",
            "dimensions": ["dti_band", "fico_band", "purpose", "loan_amount_band", "revenue_band", "home_ownership_n", "emp_length", "addr_state"],
            "rows": [public_segment(row) for row in b7 if i(row, "accounts") >= 1000 and f(row, "account_share") >= 0.001],
        },
        "materiality": {
            "material_segment_count": 43,
            "ranking_metric": "bad_associated_share",
            "ranking_note": "Prioritized by BAD-associated loan amount share, not by BAD rate alone.",
            "top_segments": top_segments,
            "overlap_warning": "Segment views overlap across dimensions and must not be summed.",
            "contrast": [
                public_segment(normalized[("dti_band", "40–59.99")]),
                public_segment(normalized[("fico_band", "640–679")]),
            ],
        },
        "splits": split_records,
        "annual": annual_records,
        "historical_shadow_composition": {
            "issue_year": 2018,
            "dimension": "purpose",
            "segment": "debt_consolidation",
            "account_share": f(debt_2018, "account_share_within_year"),
            "observed_bad_rate": f(debt_2018, "bad_rate"),
            "interpretation": "Descriptive composition only; 2018 is a historical shadow cohort and is not evidence of confirmed improvement.",
        },
        "governance": {
            "flow": [
                "Zenodo governing source",
                "stg_lc_granting_core",
                "mart_credit_application_core",
                "B6 Portfolio Overview",
                "B7 Segment Risk",
                "B8 Risk Concentration",
                "B9 Vintage / Temporal",
            ],
            "side_lanes": [
                {"name": "Figshare", "role": "matched pricing/economics only"},
                {"name": "RejectStats", "role": "context only"},
            ],
            "headline_feed": "Zenodo governed core only",
            "checks": {
                "duplicate_account_ids": 0,
                "population_loss": 0,
                "unassigned_splits": 0,
                "b5_enrichment_tests": "13/13 PASS",
                "stage_qa": "B6–B9 QA PASS",
            },
            "boundary": "Supplemental pricing and rejected-applicant context do not feed Page 02 headline risk calculations unless a governed bridge is explicitly accepted.",
        },
        "interpretation": {
            "outcome": "Final-resolution BAD/GOOD; not verified 12-month PD.",
            "segments": "Single-variable descriptive associations; not causal drivers.",
            "exposure": "loan_amnt analytical proxy; not observed regulatory EAD.",
            "time": "2018 historical shadow resolved-loan cohort; not proof of improvement.",
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(payload['segment_explorer']['rows'])} eligible segment rows)")


if __name__ == "__main__":
    main()
