-- B5.6/B5.7: RejectStats context-only staging. Never assign an outcome.
CREATE OR REPLACE TABLE staging.stg_lc_rejected AS
SELECT
    rejected_record_id,
    source_file,
    source_row_number,
    try_cast(application_date AS DATE) AS application_date,
    EXTRACT(YEAR FROM try_cast(application_date AS DATE))::INTEGER AS application_year,
    DATE_TRUNC('month', try_cast(application_date AS DATE))::DATE AS application_month,
    try_cast(amount_requested AS DECIMAL(18,2)) AS amount_requested,
    NULLIF(TRIM(loan_title), '') AS loan_title,
    try_cast(risk_score AS DECIMAL(10,2)) AS risk_score,
    try_cast(REPLACE(TRIM(debt_to_income_ratio), '%', '') AS DECIMAL(10,4)) AS dti_rejected,
    NULLIF(TRIM(zip_code), '') AS zip_code_rejected,
    NULLIF(UPPER(TRIM(state)), '') AS state_rejected,
    NULLIF(TRIM(employment_length), '') AS employment_length_rejected,
    try_cast(policy_code AS DECIMAL(18,2)) AS policy_code,
    'REJECTED_CONTEXT_ONLY' AS source_population,
    FALSE AS outcome_observed,
    FALSE AS model_target_eligible,
    FALSE AS champion_merge_eligible,
    'REJECTSTATS_KAGGLE_PUBLIC_V3' AS source_version,
    'B5_REJECTED_v1.0' AS rejected_mart_version,
    CURRENT_TIMESTAMP AS rejected_build_ts
FROM raw.rejectstats_union;
