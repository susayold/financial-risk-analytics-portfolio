# D2 Loss & Recovery Evidence — Stop Report

## Status

`BLOCKED_PENDING_FULL_ACCEPTED_SOURCE`

The available accepted-source fallback was inspected at field level. It contains 27 origination/pricing fields, including `loan_amnt`, `term`, `int_rate`, `installment`, `issue_d`, `id` and `loan_status`, but it does not contain the required retrospective recovery/loss fields.

Missing required evidence fields:

```text
funded_amnt
funded_amnt_inv
total_rec_prncp
total_rec_int
total_rec_late_fee
recoveries
collection_recovery_fee
total_pymnt
last_pymnt_d
last_pymnt_amnt
out_prncp
```

Because the full-source bridge and post-outcome semantics cannot be verified from the available input, D2 does not construct a retrospective LGD proxy and does not impute or invent recovery values.

## Consequence for downstream stages

- Empirical D4 LGD challenger: stopped.
- Fallback permitted by the plan: scenario LGD only, subject to explicit assumptions and approval.
- D5 Expected Loss cannot be frozen until a scenario LGD method is formally registered and approved.
- The inspected 27-field source remains a temporary D-runtime input and is not committed to GitHub or uploaded as raw data.
