# B8 Run Report — Risk Concentration

## Work completed

B8 joined elevated observed BAD rates to scale using only B7 single-variable outputs. The materiality rule was fixed before ranking and was not tuned to the observed result. No combinatorial segment search was performed.

## First material rows by BAD-associated loan amount share

| Rank | Dimension | Segment | Accounts | Observed BAD rate | BAD-associated share |
|---:|---|---|---:|---:|---:|
| 1 | purpose | debt_consolidation | 781,206 | 21.15% | 64.00% |
| 2 | loan_amount_band | Q4 (>75th percentile) | 291,928 | 23.38% | 45.50% |
| 3 | home_ownership_n | RENT | 535,585 | 23.23% | 41.58% |
| 4 | fico_band | 640–679 | 460,588 | 25.30% | 40.12% |
| 5 | dti_band | 20–29.99 | 410,172 | 23.07% | 35.39% |
| 6 | loan_amount_band | Q3 (>50th–75th percentile) | 369,729 | 21.96% | 32.03% |
| 7 | revenue_band | Q2 (>25th–50th percentile) | 348,634 | 21.16% | 25.26% |
| 8 | revenue_band | Q1 (≤25th percentile) | 337,001 | 23.07% | 17.91% |

`BAD-associated share` is segment BAD-associated loan amount divided by total BAD-associated loan amount. The `experience_c` dimension is quasi-constant (dominant share >99.5%), so it remains audit-visible but is excluded from headline/materiality ranking.

The table is a prioritization view for descriptive investigation. It does not represent realized loss, expected loss, a causal driver ranking or a production policy.

## QA

`PASS` across B8T01–B8T09. Account, exposure and BAD-associated shares reconcile independently within every dimension; quasi-constant dimensions are excluded from headline ranking and ranks are deterministic.
