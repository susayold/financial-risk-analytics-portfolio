# Block B — Analytical Findings (B6–B9)

## Executive answer

The resolved granted-loan portfolio contains **1,347,681 accounts**, with an observed final-resolution BAD rate of **19.98%**. BAD-associated `loan_amnt` totals **$4,186,020,700**, or **21.56%** of the loan amount proxy.

## Where observed risk is higher

- **dti_band = 40–59.99**: 31.26% observed BAD rate, 1.56x the portfolio baseline, 0.14% of total BAD-associated loan amount.
- **dti_band = 60–99.99**: 29.90% observed BAD rate, 1.50x the portfolio baseline, 0.04% of total BAD-associated loan amount.
- **purpose = small_business**: 29.86% observed BAD rate, 1.49x the portfolio baseline, 0.41% of total BAD-associated loan amount.
- **dti_band = 30–39.99**: 29.12% observed BAD rate, 1.46x the portfolio baseline, 2.79% of total BAD-associated loan amount.
- **emp_length = NI**: 26.96% observed BAD rate, 1.35x the portfolio baseline, 1.29% of total BAD-associated loan amount.

These are descriptive, single-variable comparisons. They are not causal explanations and are not an approval policy.

## Where higher risk overlaps with scale

The B8 materiality screen found **44** segments under the predefined rule `relative_bad_rate > 1.0 AND account_share >= 0.1%`. The primary prioritization quantity is BAD-associated exposure share; the separate concentration index is project-defined and descriptive.

## How risk moves across cohorts

Development observed BAD rate is **18.46%**, Validation **23.28%**, OOT **23.13%**, and Historical Shadow 2018 **15.75%**. The 2018 decrease is not interpreted as confirmed quality improvement because of right truncation/resolution selection.

## Handoff

Block C may consume the frozen `mart_credit_application_core`. B6–B9 rankings and findings are evidence for analysis, not automatically admitted model features.
