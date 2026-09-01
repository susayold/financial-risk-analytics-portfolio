# D1 Risk Score & Decision Mart Contract

## Status

`REVIEW_REQUIRED — SCORE_ARTIFACT_NOT_MATERIALIZED`

D0 is PASS. D1 is contract-ready but the account-level C9 score artifact has not been materialized into the D runtime, so no account mart, decile cutpoints or coverage result is claimed yet. The available source is the private C9 Drive closure package; this D1 contract deliberately does not copy it into GitHub.

## Grain

`1 account_id × model_version × economics_version`

## Frozen score source

- Model: `C8E_RICH_BUREAU_CATBOOST_79F`
- Score: `p_bad_final`
- Preferred source: persisted C9 scores/predictions.
- Fallback: exact C8E `.cbm` plus exact 79-feature contract; rescoring is allowed only after source materialization and never retraining.
- C8F/C8G are excluded.

## Required output fields

```text
account_id, issue_d, issue_year, split_name, actual_default,
model_version, economics_version, population_scope,
p_bad_final, risk_percentile, risk_decile, risk_band,
loan_amnt, ead_origination_proxy,
pricing_match_flag, loss_evidence_match_flag,
term, int_rate, installment, sub_grade, grade_derived,
fico_n, dti_n, purpose, home_ownership_n, application_type
```

## Deciles and bands

Risk decile cutpoints must be fitted once on a declared reference population and reused across splits. `D01` is lowest risk and `D10` highest risk. Bands are reporting labels only:

`R1 VERY_LOW`, `R2 LOW`, `R3 MEDIUM`, `R4 HIGH`, `R5 VERY_HIGH`.

No independent split-level `qcut` is permitted. Cutpoints remain pending until the complete eligible score population is available.

## Required diagnostics

For each split: row count, score coverage, mean, median, standard deviation, BAD rate, AUC, Brier, and BAD rate by frozen risk band.

## Population and claim boundary

C8E/C9 performance is limited to the matched enriched population. Any full-core view is a separately-labelled governance benchmark. D1 must not imply C8E performance on all 1,347,681 core accounts.
