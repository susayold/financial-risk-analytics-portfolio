# B5 Data Dictionary

## `mart.mart_credit_pricing_enriched`

Grain: one matched `account_id` (325,255 rows). B4 columns `actual_default`, `target_label`, `issue_d`, `revenue`, `dti_n`, `loan_amnt`, `fico_n`, `purpose`, `home_ownership_n` and `addr_state` are selected from Zenodo/B4. Supplemental fields are `sub_grade`, `grade_derived`, `int_rate`, `installment` and `term`.

`sub_grade` / `grade_derived` = `BENCHMARK_ONLY`. `int_rate` / `installment` / `term` = `ECONOMICS_ONLY`. Bridge match flags and source/version metadata are audit fields.

## `mart.mart_rejected_context`

Grain: one rejected application record. `rejected_record_id` is `md5(source_file + source_row_number)` because the source does not provide a governed account_id. Verified context fields include application date, requested amount, loan title, risk score, DTI, zip/state, employment length and policy code. It carries `outcome_observed=false`, `model_target_eligible=false` and `champion_merge_eligible=false`.

