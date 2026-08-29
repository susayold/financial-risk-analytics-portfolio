-- B4: canonical one-account analytical mart.
-- Input contract: staging.stg_lc_granting_core, one row per granted account.
-- No WHERE clause, joins, imputation, capping, encoding or model transformation.
CREATE OR REPLACE TABLE mart.mart_credit_application_core AS
SELECT
    CAST(account_id AS VARCHAR) AS account_id,
    issue_d,
    EXTRACT(YEAR FROM issue_d)::INTEGER AS issue_year,
    DATE_TRUNC('month', issue_d) AS issue_month,
    STRFTIME(issue_d, '%Y-%m') AS issue_cohort,
    split_name,
    actual_default,
    CASE
        WHEN actual_default = 1 THEN 'BAD'
        WHEN actual_default = 0 THEN 'GOOD'
        ELSE NULL
    END AS target_label,
    revenue,
    dti_n,
    loan_amnt,
    fico_n,
    experience_c,
    emp_length,
    purpose,
    home_ownership_n,
    addr_state,
    zip_code,
    'PASS' AS dq_status,
    0 AS dq_flag_count,
    'ZENODO_GRANTED_RESOLVED' AS source_population,
    'ZENODO_11295916' AS source_version,
    'BLOCK_A_v1.0' AS feature_contract_version,
    'NOT_APPLIED' AS preprocessing_version,
    'B4_v1.0' AS mart_version,
    CURRENT_TIMESTAMP AS mart_build_ts
FROM staging.stg_lc_granting_core;
