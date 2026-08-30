-- B8: Risk concentration with target-independent dimension informativeness.
-- Materiality is fixed before ranking: headline_eligible AND relative BAD > 1
-- AND primary_segment. Dimensions dominated by >99.5% of accounts are audit-only.

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE TABLE analytics.b8_dimension_profile AS
WITH ranked AS (
    SELECT dimension, segment, accounts, account_share,
           ROW_NUMBER() OVER (PARTITION BY dimension ORDER BY accounts DESC, segment) AS segment_rank
    FROM analytics.segment_risk
), summary AS (
    SELECT dimension, COUNT(*)::INTEGER AS segment_count,
           MAX(segment) FILTER (WHERE segment_rank = 1) AS dominant_segment,
           MAX(accounts) FILTER (WHERE segment_rank = 1)::BIGINT AS dominant_segment_accounts,
           MAX(account_share) FILTER (WHERE segment_rank = 1)::DOUBLE AS dominant_segment_account_share
    FROM ranked GROUP BY dimension
)
SELECT *,
       CASE WHEN dominant_segment_account_share > 0.995 THEN 'QUASI_CONSTANT' ELSE 'INFORMATIVE' END AS dimension_status,
       dominant_segment_account_share <= 0.995 AS headline_eligible
FROM summary ORDER BY dimension;

CREATE OR REPLACE TABLE analytics.risk_concentration AS
WITH scored AS (
    SELECT s.dimension, s.segment, s.accounts, s.good_accounts, s.bad_accounts,
           s.bad_rate, s.loan_amount, s.loan_amount_share,
           s.bad_associated_loan_amount, s.bad_amount_to_total_exposure,
           s.bad_associated_share, s.account_share, s.relative_bad_rate,
           s.primary_segment, p.dimension_status, p.headline_eligible,
           (p.headline_eligible AND s.relative_bad_rate > 1.0 AND s.primary_segment AND s.accounts > 0) AS materiality_flag,
           'headline_eligible AND relative_bad_rate > 1.0 AND primary_segment = TRUE' AS materiality_rule,
           s.relative_bad_rate * s.loan_amount_share AS descriptive_concentration_index,
           s.wilson_lower_95, s.wilson_upper_95
    FROM analytics.segment_risk s JOIN analytics.b8_dimension_profile p USING (dimension)
), ranked AS (
    SELECT *, CASE WHEN materiality_flag THEN ROW_NUMBER() OVER (ORDER BY materiality_flag DESC, bad_associated_share DESC, dimension, segment) ELSE NULL END::INTEGER AS materiality_rank
    FROM scored
)
SELECT dimension, segment, accounts, good_accounts, bad_accounts, bad_rate,
       loan_amount, loan_amount_share, bad_associated_loan_amount,
       bad_amount_to_total_exposure, bad_associated_share, account_share,
       relative_bad_rate, primary_segment, dimension_status, headline_eligible,
       materiality_flag, materiality_rule, descriptive_concentration_index,
       materiality_rank, wilson_lower_95, wilson_upper_95
FROM ranked
ORDER BY materiality_flag DESC, materiality_rank NULLS LAST, bad_associated_share DESC, dimension, segment;
