# D1 Available Score Artifact Audit

Updated: 2026-09-02

## Result

`PASS_WITH_LIMITATIONS` for the persisted score files and the materialized
matched scored subset. This is not a claim that the full governed population
has C8E scores.

The initial audit was run with `src/audit_block_d_available_scores.py` against
the private C8E Validation artifact and the private C9 OOT artifact. A second
controlled build replayed the frozen C8E model on the matched Development
population; it did not refit, tune on OOT or recalibrate. It checked
required columns, non-null/non-blank account IDs, account-level uniqueness,
binary target values, finite scores in `[0, 1]`, expected row counts, and ID
overlap across splits.

The two files were also materialized into the private derived
`D1_AVAILABLE_SCORE_MART.csv` (127,885 rows). Its scope is explicitly
score-only; pricing and loss-evidence flags are `UNASSESSED`, not mismatches.

| Split | Artifact | Rows | BAD | BAD rate | Recomputed ROC-AUC | Result |
|---|---|---:|---:|---:|---:|---|
| Validation 2016 | `07_validation_2016_predictions.parquet` | 83,664 | 14,190 | 16.9557% | 0.8219379569 | PASS |
| OOT 2017 | `12_oot_2017_predictions.parquet` | 44,221 | 5,892 | 13.3240% | 0.8557777505 | PASS |
| Development | frozen C8E replay on matched governed rows | 182,181 | 28,967 | 15.9001% | score replay only | PASS |

Cross-split account-ID overlap is `0`. Score bounds are valid in both files;
the Validation `final_prediction` range is `0.0045953315`–`0.9380497573` and
the OOT `prediction` range is `0.0046268891`–`0.9223821735`.

## What this proves

- The two persisted score artifacts are structurally readable and internally
  consistent at account grain.
- The published OOT AUC can be reproduced from the persisted OOT artifact.
- Validation and OOT artifacts do not share account IDs.
- Development, Validation and OOT score inputs reconcile to **310,066** unique
  account rows; all rows carry complete score coverage and pricing fields.
- Risk decile cutpoints are referenced to Validation scores; OOT is not used to
  tune or recalibrate the frozen model.

## What this does not prove

- It does not prove that every one of the 1,347,681 governed accounts has a
  C8E score; the D1 scored lane is a matched enriched subset.
- It does not turn `p_bad_final` into a verified 12-month PD or a regulatory
  PD.
- It does not by itself approve D4 LGD, D5 Expected Loss, D6 policy, D7
  profitability, D8 stress or D9 closure.
