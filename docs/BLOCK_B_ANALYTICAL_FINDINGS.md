# Block B — Analytical Findings (B6–B9)

## Executive answer

The resolved granted-loan portfolio contains **1,347,681 accounts**, with an observed final-resolution BAD rate of **19.98%**. BAD-associated `loan_amnt` totals **$4,186,020,700**, or **21.56%** of the loan amount proxy.

## Where observed risk is higher

- **dti_band = 40–59.99**: 31.26% observed BAD rate, 1.56x the portfolio baseline, 0.64% of total BAD-associated loan amount.
- **purpose = small_business**: 29.86% observed BAD rate, 1.49x the portfolio baseline, 1.89% of total BAD-associated loan amount.
- **dti_band = 30–39.99**: 29.12% observed BAD rate, 1.46x the portfolio baseline, 12.92% of total BAD-associated loan amount.
- **emp_length = NI**: 26.96% observed BAD rate, 1.35x the portfolio baseline, 6.00% of total BAD-associated loan amount.
- **addr_state = MS**: 26.12% observed BAD rate, 1.31x the portfolio baseline, 0.64% of total BAD-associated loan amount.

These are descriptive, single-variable comparisons. They are not causal explanations and are not an approval policy.

## Where higher risk overlaps with scale

The B8 materiality screen found **43** segments under the predefined rule `headline_eligible AND relative_bad_rate > 1.0 AND primary_segment AND accounts > 0`. The primary quantity is BAD-associated loan amount share: segment BAD-associated amount divided by total BAD-associated amount.

## How risk moves across cohorts

Development observed BAD rate is **18.46%**, Validation **23.28%**, OOT **23.13%**, and Historical Shadow 2018 **15.75%**. The 2018 decrease is not interpreted as confirmed quality improvement because of right truncation/resolution selection.

## Handoff

Block C may consume the frozen `mart_credit_application_core`. B6–B9 rankings and findings are evidence for analysis, not automatically admitted model features. Observed BAD is not verified 12-month PD.
