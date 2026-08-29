# Block B — Assumptions and Limits

## Metric semantics

- `actual_default` is the observed final-resolution outcome in the governed granting dataset.
- Observed BAD rate is not verified 12-month PD, forecast PD or model score.
- `loan_amnt` is an exposure proxy; it is not observed EAD.
- BAD-associated loan amount is not realized loss, LGD, ECL or expected loss.
- Matched pricing fields remain B5 descriptive enrichment; they are not blended into the core baseline.
- Rejected applications remain context-only with no inferred GOOD/BAD outcome.

## Temporal assumptions

- `issue_d` is the only temporal authority.
- Temporal movement is descriptive and non-causal.
- The 2018 historical-shadow sample is resolution-selected and right-truncated; it is not live monitoring.

## Scope limits

This work does not claim ROC-AUC, KS, Gini, calibration, PD, LGD, EAD, ECL, optimized approval policy, reject inference or production monitoring. No caps, imputations, outlier treatments or model transformations were fitted in B6–B9.
