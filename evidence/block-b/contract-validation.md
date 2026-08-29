# Feature contract validation

## Champion whitelist

The exact Block A v1.0 candidate set is:

`revenue`, `dti_n`, `loan_amnt`, `fico_n`, `experience_c`, `emp_length`, `purpose`, `home_ownership_n`

## Reviewed assertions

| Assertion | Result |
|---|---:|
| Missing champion fields | 0 |
| Unexpected champion fields | 0 |
| Forbidden fields in champion | 0 |
| Supplemental fields in primary staging | 0 |

The contract test is executable and capable of producing `FAIL`; it is not a declarative PASS label.

## Controlled fields

- `account_id`, `issue_d`, `split_name`, `actual_default`: identifier/time/target roles only.
- `addr_state`, `zip_code`, `title`, `desc`: analysis/review only.
- `grade`, `sub_grade`, `int_rate`, `installment`, `term`: supplemental-only and excluded from primary staging.
