# B6 Run Report — Portfolio Overview

## Work completed

B6 profiled the frozen core mart without caps, imputation, outlier treatment or feature transforms. It produced a portfolio KPI baseline, numeric percentile profile and composition tables for the governed core dimensions.

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

`FAIL` across B6T01–B6T08. Direct core-source exposure/null reconciliations, count identities, category shares and the public claim contract pass. Pricing fields are absent from the core mart; matched pricing remains under the B5 boundary. This observed BAD rate is not verified 12-month PD.

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
