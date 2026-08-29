-- B7: Single-variable observed BAD segmentation from the locked core mart.
-- Segment definitions are fixed before ranking; UNKNOWN / MISSING is retained.

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE TABLE analytics.b7_band_cuts AS
SELECT
    QUANTILE_CONT(revenue, 0.25)::DOUBLE AS revenue_q25,
    QUANTILE_CONT(revenue, 0.50)::DOUBLE AS revenue_q50,
    QUANTILE_CONT(revenue, 0.75)::DOUBLE AS revenue_q75,
    QUANTILE_CONT(loan_amnt, 0.25)::DOUBLE AS loan_amnt_q25,
    QUANTILE_CONT(loan_amnt, 0.50)::DOUBLE AS loan_amnt_q50,
    QUANTILE_CONT(loan_amnt, 0.75)::DOUBLE AS loan_amnt_q75
FROM mart.mart_credit_application_core;

CREATE OR REPLACE TABLE analytics.segment_risk AS
WITH base AS (
    SELECT *,
        CASE
            WHEN fico_n IS NULL THEN 'UNKNOWN / MISSING'
            WHEN fico_n < 600 THEN '<600'
            WHEN fico_n < 640 THEN '600–639'
            WHEN fico_n < 680 THEN '640–679'
            WHEN fico_n < 720 THEN '680–719'
            WHEN fico_n < 760 THEN '720–759'
            WHEN fico_n < 800 THEN '760–799'
            ELSE '800+'
        END AS fico_band,
        CASE
            WHEN dti_n IS NULL THEN 'UNKNOWN / MISSING'
            WHEN dti_n < 10 THEN '<10'
            WHEN dti_n < 20 THEN '10–19.99'
            WHEN dti_n < 30 THEN '20–29.99'
            WHEN dti_n < 40 THEN '30–39.99'
            WHEN dti_n < 60 THEN '40–59.99'
            WHEN dti_n < 100 THEN '60–99.99'
            ELSE '100+'
        END AS dti_band,
        CASE
            WHEN revenue IS NULL THEN 'UNKNOWN / MISSING'
            WHEN revenue <= c.revenue_q25 THEN 'Q1 (≤25th percentile)'
            WHEN revenue <= c.revenue_q50 THEN 'Q2 (>25th–50th percentile)'
            WHEN revenue <= c.revenue_q75 THEN 'Q3 (>50th–75th percentile)'
            ELSE 'Q4 (>75th percentile)'
        END AS revenue_band,
        CASE
            WHEN loan_amnt IS NULL THEN 'UNKNOWN / MISSING'
            WHEN loan_amnt <= c.loan_amnt_q25 THEN 'Q1 (≤25th percentile)'
            WHEN loan_amnt <= c.loan_amnt_q50 THEN 'Q2 (>25th–50th percentile)'
            WHEN loan_amnt <= c.loan_amnt_q75 THEN 'Q3 (>50th–75th percentile)'
            ELSE 'Q4 (>75th percentile)'
        END AS loan_amount_band
    FROM mart.mart_credit_application_core m CROSS JOIN analytics.b7_band_cuts c
), segments AS (
    SELECT 'fico_band' AS dimension, fico_band AS segment, loan_amnt, actual_default FROM base
    UNION ALL SELECT 'dti_band', dti_band, loan_amnt, actual_default FROM base
    UNION ALL SELECT 'revenue_band', revenue_band, loan_amnt, actual_default FROM base
    UNION ALL SELECT 'loan_amount_band', loan_amount_band, loan_amnt, actual_default FROM base
    UNION ALL SELECT 'purpose', COALESCE(NULLIF(TRIM(CAST(purpose AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM base
    UNION ALL SELECT 'home_ownership_n', COALESCE(NULLIF(TRIM(CAST(home_ownership_n AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM base
    UNION ALL SELECT 'experience_c', COALESCE(NULLIF(TRIM(CAST(experience_c AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM base
    UNION ALL SELECT 'emp_length', COALESCE(NULLIF(TRIM(CAST(emp_length AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM base
    UNION ALL SELECT 'addr_state', COALESCE(NULLIF(TRIM(CAST(addr_state AS VARCHAR)), ''), 'UNKNOWN / MISSING'), loan_amnt, actual_default FROM base
), totals AS (
    SELECT COUNT(*)::DOUBLE AS total_accounts, SUM(loan_amnt)::DOUBLE AS total_loan_amount FROM base
), scored AS (
    SELECT
        dimension, segment,
        COUNT(*)::BIGINT AS accounts,
        COUNT(*) FILTER (WHERE actual_default = 0)::BIGINT AS good_accounts,
        COUNT(*) FILTER (WHERE actual_default = 1)::BIGINT AS bad_accounts,
        COUNT(*) FILTER (WHERE actual_default = 1) / NULLIF(COUNT(*), 0)::DOUBLE AS bad_rate,
        SUM(loan_amnt)::DOUBLE AS loan_amount,
        SUM(loan_amnt) / NULLIF(totals.total_loan_amount, 0)::DOUBLE AS loan_amount_share,
        SUM(loan_amnt) FILTER (WHERE actual_default = 1)::DOUBLE AS bad_associated_loan_amount,
        SUM(loan_amnt) FILTER (WHERE actual_default = 1) / NULLIF(totals.total_loan_amount, 0)::DOUBLE AS bad_associated_share,
        COUNT(*) / totals.total_accounts AS account_share
    FROM segments CROSS JOIN totals
    GROUP BY dimension, segment, totals.total_accounts, totals.total_loan_amount
)
SELECT
    *,
    bad_rate / NULLIF((SELECT AVG(actual_default) FROM base), 0)::DOUBLE AS relative_bad_rate,
    accounts >= 1000 OR account_share >= 0.001 AS primary_segment,
    CASE WHEN bad_rate >= 0 THEN NULL ELSE NULL END::DOUBLE AS wilson_lower_95,
    CASE WHEN bad_rate >= 0 THEN NULL ELSE NULL END::DOUBLE AS wilson_upper_95
FROM scored
ORDER BY dimension, accounts DESC, segment;

-- Preserve every fixed bucket even when the source has zero observations.
INSERT INTO analytics.segment_risk
    (dimension, segment, accounts, good_accounts, bad_accounts, bad_rate,
     loan_amount, loan_amount_share, bad_associated_loan_amount,
     bad_associated_share, account_share, relative_bad_rate, primary_segment,
     wilson_lower_95, wilson_upper_95)
SELECT 'fico_band', x.segment, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, FALSE, NULL, NULL
FROM (VALUES ('<600'),('600–639'),('640–679'),('680–719'),('720–759'),('760–799'),('800+')) x(segment)
WHERE NOT EXISTS (SELECT 1 FROM analytics.segment_risk s WHERE s.dimension='fico_band' AND s.segment=x.segment);

INSERT INTO analytics.segment_risk
    (dimension, segment, accounts, good_accounts, bad_accounts, bad_rate,
     loan_amount, loan_amount_share, bad_associated_loan_amount,
     bad_associated_share, account_share, relative_bad_rate, primary_segment,
     wilson_lower_95, wilson_upper_95)
SELECT 'dti_band', x.segment, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, FALSE, NULL, NULL
FROM (VALUES ('<10'),('10–19.99'),('20–29.99'),('30–39.99'),('40–59.99'),('60–99.99'),('100+')) x(segment)
WHERE NOT EXISTS (SELECT 1 FROM analytics.segment_risk s WHERE s.dimension='dti_band' AND s.segment=x.segment);
