# B8 Run Report — Risk Concentration

## Work completed

B8 joined elevated observed BAD rates to scale using only B7 single-variable outputs. The materiality rule was fixed before ranking and was not tuned to the observed result. No combinatorial segment search was performed.

## First material rows by BAD-associated exposure share

| Rank | Dimension | Segment | Accounts | Observed BAD rate | BAD-associated share |
|---:|---|---|---:|---:|---:|
| 1 | experience_c | 1 | 1,347,656 | 19.98% | 21.56% |
| 2 | purpose | debt_consolidation | 781,206 | 21.15% | 13.80% |
| 3 | loan_amount_band | Q4 (>75th percentile) | 291,928 | 23.38% | 9.81% |
| 4 | home_ownership_n | RENT | 535,585 | 23.23% | 8.96% |
| 5 | fico_band | 640–679 | 460,588 | 25.30% | 8.65% |
| 6 | dti_band | 20–29.99 | 410,172 | 23.07% | 7.63% |
| 7 | loan_amount_band | Q3 (>50th–75th percentile) | 369,729 | 21.96% | 6.90% |
| 8 | revenue_band | Q2 (>25th–50th percentile) | 348,634 | 21.16% | 5.45% |

The table is a prioritization view for descriptive investigation. It does not represent realized loss, expected loss, a causal driver ranking or a production policy.

## QA

`PASS` across B8T01–B8T07. Account and exposure shares reconcile independently within every dimension, and ranks are deterministic.

## Evidence files

- `outputs/b8/risk_concentration.csv`
- `outputs/b8/b8_summary.json`
- `outputs/b8/b8_test_results.json`
