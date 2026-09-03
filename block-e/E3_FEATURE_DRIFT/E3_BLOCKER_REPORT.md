# E3 Feature Drift — Gate Stop Report

**Status:** `STOPPED_AT_E3_G04_REAL_GATE_FAILURE`  
**Baseline:** `E-BASELINE-2016-1.0`  
**Frozen model contract:** `C8E_RICH_BUREAU_CATBOOST_79F`

## Gate result

| Gate | Result |
|---|---:|
| E3-G01 bins reference-frozen | PASS |
| E3-G02 missing bin explicit | PASS |
| E3-G03 epsilon documented | PASS |
| E3-G04 79/79 features covered | **FAIL** |
| E3-G05 categorical logic correct | PASS |
| E3-G06 top-feature watchlist complete | PASS |
| E3-G07 feature importance version frozen | PASS |
| E3-G08 no model tuning | PASS |

## Evidence boundary

The frozen contract contains 79 features. The available row-level D1 decision-economics mart exposes values for 9 features and does not expose values for 70 features. The 70 unavailable fields are represented as `NOT_AVAILABLE_SOURCE_FEATURE_VALUES`. No synthetic values, imputation, or proxy substitution is used to force coverage.

The mandatory watchlist remains explicit: `installment_to_loan` and `int_rate`. `int_rate` is available in D1; `installment_to_loan` is contractually required but unavailable at row grain.

## Required unblock artifact

Provide a governed one-to-one snapshot of all 79 frozen C8E feature values for the scored population, with account linkage, privacy controls, source lineage, and a checksum. Rerun E3 only after that snapshot is accepted. E4–E9 must remain unexecuted until E3 reaches 8/8 PASS.
