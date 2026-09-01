# D1 Available Score Artifact Audit

Updated: 2026-09-02

## Result

`PASS_WITH_LIMITATIONS` for the persisted score files themselves. This is a
pre-opening artifact audit, not a D1 population-coverage pass.

The audit was run with `src/audit_block_d_available_scores.py` against the
private C8E Validation artifact and the private C9 OOT artifact. It checked
required columns, non-null/non-blank account IDs, account-level uniqueness,
binary target values, finite scores in `[0, 1]`, expected row counts, and ID
overlap across splits.

| Split | Artifact | Rows | BAD | BAD rate | Recomputed ROC-AUC | Result |
|---|---|---:|---:|---:|---:|---|
| Validation 2016 | `07_validation_2016_predictions.parquet` | 83,664 | 14,190 | 16.9557% | 0.8219379569 | PASS |
| OOT 2017 | `12_oot_2017_predictions.parquet` | 44,221 | 5,892 | 13.3240% | 0.8557777505 | PASS |

Cross-split account-ID overlap is `0`. Score bounds are valid in both files;
the Validation `final_prediction` range is `0.0045953315`–`0.9380497573` and
the OOT `prediction` range is `0.0046268891`–`0.9223821735`.

## What this proves

- The two persisted score artifacts are structurally readable and internally
  consistent at account grain.
- The published OOT AUC can be reproduced from the persisted OOT artifact.
- Validation and OOT artifacts do not share account IDs.

## What this does not prove

- It does not prove Development score coverage; the Development prediction
  artifact is still missing from the available C8E package.
- It does not prove bridge coverage to the governed core, pricing fields, or
  loss/recovery evidence.
- It does not unlock the D1 full mart, empirical LGD, Expected Loss, policy,
  pricing, stress, or D9 closure gates.
