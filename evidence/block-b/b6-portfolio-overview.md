# B6 Run Report — Portfolio Overview

## Work completed

B6 profiled the frozen core mart without caps, imputation, outlier treatment, or feature transforms. It produced a portfolio KPI baseline, full numeric percentile profile for `fico_n`, `dti_n`, `revenue`, and `loan_amnt`, and composition tables for purpose, home ownership, employment length, experience and state.

## Results

| Metric | Result |
|---|---:|
| Total accounts | 1,347,681 |
| GOOD | 1,078,432 |
| BAD | 269,249 |
| Observed final-resolution BAD rate | 19.98% |
| Total `loan_amnt` proxy | $19,417,698,475 |
| BAD-associated amount | $4,186,020,700 |
| BAD-associated exposure share | 21.56% |
| Issue cohorts | 139 |

## QA

`PASS` across B6T01–B6T07. Category dimensions reconcile to the full core population and 100% of the loan amount proxy. Pricing fields are absent from the core mart; the matched pricing sample remains under the B5 boundary.

## Artifacts

- `outputs/b6/portfolio_kpis.json`
- `outputs/b6/numeric_profile.csv`
- `outputs/b6/portfolio_mix.csv`
- `outputs/b6/b6_test_results.json`

## Evidence files

- `outputs/b6/portfolio_kpis.json`
- `outputs/b6/numeric_profile.csv`
- `outputs/b6/portfolio_mix.csv`
- `outputs/b6/b6_test_results.json`
