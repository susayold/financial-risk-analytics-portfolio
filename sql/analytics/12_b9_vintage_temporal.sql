-- B9: Vintage and temporal observed-risk analysis.
-- Temporal authority is issue_d only. This is descriptive cohort analysis.

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE TABLE analytics.vintage_monthly AS
SELECT
    issue_cohort AS cohort,
    MIN(issue_d)::DATE AS cohort_start,
    COUNT(*)::BIGINT AS accounts,
    COUNT(*) FILTER (WHERE actual_default=0)::BIGINT AS good_accounts,
    COUNT(*) FILTER (WHERE actual_default=1)::BIGINT AS bad_accounts,
    AVG(actual_default)::DOUBLE AS bad_rate,
    SUM(loan_amnt)::DOUBLE AS loan_amount,
    SUM(loan_amnt) FILTER (WHERE actual_default=1)::DOUBLE AS bad_associated_loan_amount,
    AVG(fico_n)::DOUBLE AS avg_fico,
    AVG(dti_n)::DOUBLE AS avg_dti,
    AVG(revenue)::DOUBLE AS avg_revenue,
    AVG(loan_amnt)::DOUBLE AS avg_loan_amount,
    MEDIAN(fico_n)::DOUBLE AS median_fico,
    MEDIAN(dti_n)::DOUBLE AS median_dti,
    MEDIAN(revenue)::DOUBLE AS median_revenue,
    MEDIAN(loan_amnt)::DOUBLE AS median_loan_amount
FROM mart.mart_credit_application_core
GROUP BY issue_cohort
ORDER BY cohort;

CREATE OR REPLACE TABLE analytics.vintage_annual AS
SELECT
    issue_year,
    COUNT(*)::BIGINT AS accounts,
    COUNT(*) FILTER (WHERE actual_default=0)::BIGINT AS good_accounts,
    COUNT(*) FILTER (WHERE actual_default=1)::BIGINT AS bad_accounts,
    AVG(actual_default)::DOUBLE AS bad_rate,
    SUM(loan_amnt)::DOUBLE AS loan_amount,
    SUM(loan_amnt) FILTER (WHERE actual_default=1)::DOUBLE AS bad_associated_loan_amount,
    MEDIAN(fico_n)::DOUBLE AS median_fico,
    MEDIAN(dti_n)::DOUBLE AS median_dti,
    MEDIAN(revenue)::DOUBLE AS median_revenue,
    MEDIAN(loan_amnt)::DOUBLE AS median_loan_amount
FROM mart.mart_credit_application_core
GROUP BY issue_year
ORDER BY issue_year;

CREATE OR REPLACE TABLE analytics.vintage_split AS
SELECT
    split_name,
    COUNT(*)::BIGINT AS accounts,
    COUNT(*) FILTER (WHERE actual_default=0)::BIGINT AS good_accounts,
    COUNT(*) FILTER (WHERE actual_default=1)::BIGINT AS bad_accounts,
    AVG(actual_default)::DOUBLE AS bad_rate,
    MIN(issue_d)::DATE AS min_issue_d,
    MAX(issue_d)::DATE AS max_issue_d,
    COUNT(DISTINCT issue_cohort)::INTEGER AS issue_cohorts,
    SUM(loan_amnt)::DOUBLE AS loan_amount,
    SUM(loan_amnt) FILTER (WHERE actual_default=1)::DOUBLE AS bad_associated_loan_amount
FROM mart.mart_credit_application_core
GROUP BY split_name
ORDER BY CASE split_name WHEN 'Development' THEN 1 WHEN 'Validation' THEN 2 WHEN 'OOT' THEN 3 WHEN 'Historical Shadow' THEN 4 ELSE 5 END;
