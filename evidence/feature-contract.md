# Feature contract

## Champion whitelist

The default-deny champion boundary contains:

`revenue`, `dti_n`, `loan_amnt`, `fico_n`, `experience_c`, `emp_length`, `purpose`, `home_ownership_n`.

`dti_n` has a Development-only outlier rule. `loan_amnt` is also an EAD proxy for later economics work.

## Controlled or excluded fields

- `id`: key only; not a model feature.
- `issue_d`: split/vintage authority only.
- `Default`: target only.
- `addr_state` / `zip_code`: analysis/economics/benchmark; excluded from champion.
- `title` / `desc`: text context; excluded from champion.
- `sub_grade` / derived grade: benchmark/economics; excluded from champion.
- `int_rate` / `installment` / `term`: economics only; excluded from champion.

The whitelist is the approval boundary for later modeling work; it is not a claim that a Block C model has already been built.
