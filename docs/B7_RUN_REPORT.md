# B7 Run Report — Segment Risk

## Work completed

B7 segmented the frozen core by the fixed FICO and DTI bands in the plan, exact Q1–Q4 cut points for revenue and loan amount, and the five categorical dimensions. Missing values are explicit as `UNKNOWN / MISSING`; no silent row drops were used. The exact quantile cut points are in `outputs/b7/b7_band_definitions.json`.

## Headline descriptive groups

| Dimension | Segment | Accounts | Observed BAD rate | Relative BAD rate | BAD-associated share |
|---|---|---:|---:|---:|---:|
| dti_band | 40–59.99 | 5,089 | 31.26% | 1.56x | 0.14% |
| dti_band | 60–99.99 | 1,184 | 29.90% | 1.50x | 0.04% |
| purpose | small_business | 15,575 | 29.86% | 1.49x | 0.41% |
| dti_band | 30–39.99 | 122,297 | 29.12% | 1.46x | 2.79% |
| emp_length | NI | 78,188 | 26.96% | 1.35x | 1.29% |
| addr_state | MS | 6,593 | 26.12% | 1.31x | 0.14% |
| fico_band | 640–679 | 460,588 | 25.30% | 1.27x | 8.65% |
| addr_state | NE | 3,591 | 25.20% | 1.26x | 0.07% |

These are screening findings, not causal effects, approval rules or automatically approved Block C features.

## QA

`PASS` across B7T01–B7T10. Every dimension reconciles to 1,347,681 accounts and 100% of the loan amount proxy.
