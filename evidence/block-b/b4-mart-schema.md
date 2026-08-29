# B4 MART SCHEMA

**Object:** `mart.mart_credit_application_core`  
**Grain:** one account per `account_id`  
**Version:** `B4_v1.0`

## Schema groups

- **KEY / TIME / TARGET:** `account_id`, `issue_d`, `issue_year`, `issue_month`, `issue_cohort`, `split_name`, `actual_default`, `target_label`
- **CHAMPION CANDIDATES:** `revenue`, `dti_n`, `loan_amnt`, `fico_n`, `experience_c`, `emp_length`, `purpose`, `home_ownership_n`
- **ANALYSIS-ONLY:** `addr_state`, `zip_code`
- **GOVERNANCE METADATA:** `dq_status`, `dq_flag_count`, `source_population`, `source_version`, `feature_contract_version`, `preprocessing_version`, `mart_version`, `mart_build_ts`

Forbidden outcome/pricing fields are absent. `title` and `desc` remain in staging but are intentionally omitted from the core mart.
