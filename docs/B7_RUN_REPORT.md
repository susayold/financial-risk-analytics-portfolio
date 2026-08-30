# B7 Run Report — Segment Risk

## Work completed

B7 segmented the frozen core by fixed FICO and DTI bands, exact Q1–Q4 cut points for revenue and loan amount, and five categorical dimensions. Missing values are explicit as `UNKNOWN / MISSING`; no silent row drops were used. The primary rule is `accounts >= 1,000 AND account_share >= 0.1%`.

## Headline descriptive groups

| Dimension | Segment | Accounts | Observed BAD rate | Relative BAD rate | BAD-associated share |
|---|---|---:|---:|---:|---:|
| dti_band | 40–59.99 | 5,089 | 31.26% | 1.56x | 0.64% |
| purpose | small_business | 15,575 | 29.86% | 1.49x | 1.89% |
| dti_band | 30–39.99 | 122,297 | 29.12% | 1.46x | 12.92% |
| emp_length | NI | 78,188 | 26.96% | 1.35x | 6.00% |
| addr_state | MS | 6,593 | 26.12% | 1.31x | 0.64% |
| fico_band | 640–679 | 460,588 | 25.30% | 1.27x | 40.12% |
| addr_state | NE | 3,591 | 25.20% | 1.26x | 0.31% |
| addr_state | AR | 10,058 | 24.11% | 1.21x | 0.85% |

`BAD-associated share` means segment BAD-associated `loan_amnt` divided by total portfolio BAD-associated `loan_amnt`. It is not the segment's share of total portfolio exposure; that separate ratio is `bad_amount_to_total_exposure`.

These are screening findings, not causal effects, approval rules or automatically approved Block C features. This is not predictive model performance.

## QA

`PASS` across B7T01–B7T12. Every dimension reconciles to 1,347,681 accounts, 100% of the loan amount proxy and 100% of total BAD-associated amount; Wilson 95% intervals are executable and bounded.
