-- B6: Portfolio overview and descriptive baseline.
-- Grain: one row per application in mart.mart_credit_application_core.
-- No caps, imputation, transforms, or target-derived feature changes are applied.

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE TABLE analytics.portfolio_overview AS
SELECT
    COUNT(*)::BIGINT AS total_accounts,
    COUNT(*) FILTER (WHERE actual_default = 0)::BIGINT AS good_accounts,
    COUNT(*) FILTER (WHERE actual_default = 1)::BIGINT AS bad_accounts,
    AVG(actual_default)::DOUBLE AS observed_bad_rate,
    SUM(loan_amnt)::DOUBLE AS total_loan_amount,
    AVG(loan_amnt)::DOUBLE AS avg_loan_amount,
    MEDIAN(loan_amnt)::DOUBLE AS median_loan_amount,
    SUM(loan_amnt) FILTER (WHERE actual_default = 1)::DOUBLE AS bad_associated_loan_amount,
    SUM(loan_amnt) FILTER (WHERE actual_default = 1) / NULLIF(SUM(loan_amnt), 0)::DOUBLE AS bad_associated_exposure_share,
    AVG(fico_n)::DOUBLE AS avg_fico,
    MEDIAN(fico_n)::DOUBLE AS median_fico,
    AVG(dti_n)::DOUBLE AS avg_dti,
    MEDIAN(dti_n)::DOUBLE AS median_dti,
    AVG(revenue)::DOUBLE AS avg_revenue,
    MEDIAN(revenue)::DOUBLE AS median_revenue,
    COUNT(DISTINCT issue_cohort)::INTEGER AS issue_cohorts,
    MIN(issue_d)::DATE AS min_issue_d,
    MAX(issue_d)::DATE AS max_issue_d
FROM mart.mart_credit_application_core;

CREATE OR REPLACE TABLE analytics.numeric_profile AS
WITH fields AS (
    SELECT 'fico_n' AS field_name, fico_n::DOUBLE AS value FROM mart.mart_credit_application_core
    UNION ALL SELECT 'dti_n', dti_n::DOUBLE FROM mart.mart_credit_application_core
    UNION ALL SELECT 'revenue', revenue::DOUBLE FROM mart.mart_credit_application_core
    UNION ALL SELECT 'loan_amnt', loan_amnt::DOUBLE FROM mart.mart_credit_application_core
)
SELECT
    field_name,
    COUNT(value)::BIGINT AS non_null_count,
    COUNT(*)::BIGINT AS row_count,
    (COUNT(*) - COUNT(value))::BIGINT AS null_count,
    (COUNT(*) - COUNT(value)) / NULLIF(COUNT(*), 0)::DOUBLE AS null_rate,
    AVG(value)::DOUBLE AS mean,
    STDDEV_POP(value)::DOUBLE AS std,
    MIN(value)::DOUBLE AS min,
    QUANTILE_CONT(value, 0.01)::DOUBLE AS p01,
    QUANTILE_CONT(value, 0.05)::DOUBLE AS p05,
    QUANTILE_CONT(value, 0.25)::DOUBLE AS p25,
    QUANTILE_CONT(value, 0.50)::DOUBLE AS p50,
    QUANTILE_CONT(value, 0.75)::DOUBLE AS p75,
    QUANTILE_CONT(value, 0.95)::DOUBLE AS p95,
    QUANTILE_CONT(value, 0.99)::DOUBLE AS p99,
    MAX(value)::DOUBLE AS max
FROM fields
GROUP BY field_name;

CREATE OR REPLACE TABLE analytics.portfolio_mix AS
WITH segments AS (
    SELECT 'purpose' AS dimension, COALESCE(NULLIF(TRIM(CAST(purpose AS VARCHAR)), ''), 'UNKNOWN / MISSING') AS segment, loan_amnt, actual_default FROM mart.mart_credit_application_core
    UNION ALL SELECT 'home_ownership_n', COALESCE(NULLIF(TRIM(CAST(home_ownership_n AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM mart.mart_credit_application_core
    UNION ALL SELECT 'emp_length', COALESCE(NULLIF(TRIM(CAST(emp_length AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM mart.mart_credit_application_core
    UNION ALL SELECT 'experience_c', COALESCE(NULLIF(TRIM(CAST(experience_c AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM mart.mart_credit_application_core
    UNION ALL SELECT 'addr_state', COALESCE(NULLIF(TRIM(CAST(addr_state AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM mart.mart_credit_application_core
), totals AS (
    SELECT COUNT(*)::DOUBLE AS total_accounts, SUM(loan_amnt)::DOUBLE AS total_loan_amount FROM mart.mart_credit_application_core
)
SELECT
    s.dimension,
    s.segment,
    COUNT(*)::BIGINT AS accounts,
    COUNT(*) FILTER (WHERE actual_default = 0)::BIGINT AS good_accounts,
    COUNT(*) FILTER (WHERE actual_default = 1)::BIGINT AS bad_accounts,
    COUNT(*) / totals.total_accounts AS account_share,
    SUM(s.loan_amnt)::DOUBLE AS loan_amount,
    SUM(s.loan_amnt) / NULLIF(totals.total_loan_amount, 0) AS exposure_share
FROM segments s CROSS JOIN totals
GROUP BY s.dimension, s.segment, totals.total_accounts, totals.total_loan_amount
ORDER BY s.dimension, accounts DESC, s.segment;
