-- B8: Concentration of elevated observed BAD rates with portfolio scale.
-- Pre-declared materiality rule: relative BAD rate > 1.0 and account share >= 0.1%.

CREATE SCHEMA IF NOT EXISTS analytics;
CREATE OR REPLACE TABLE analytics.risk_concentration AS
WITH scored AS (
    SELECT
        dimension, segment, accounts, good_accounts, bad_accounts, bad_rate,
        account_share, loan_amount, loan_amount_share,
        bad_associated_loan_amount, bad_associated_share, relative_bad_rate,
        primary_segment,
        (relative_bad_rate > 1.0 AND account_share >= 0.001 AND accounts > 0) AS materiality_flag,
        'relative_bad_rate > 1.0 AND account_share >= 0.001 (0.1%)' AS materiality_rule
    FROM analytics.segment_risk
), ranked AS (
    SELECT *,
        CASE WHEN materiality_flag THEN ROW_NUMBER() OVER (ORDER BY materiality_flag DESC, bad_associated_share DESC, dimension, segment) ELSE NULL END::INTEGER AS materiality_rank,
        relative_bad_rate * loan_amount_share AS descriptive_concentration_index
    FROM scored
)
SELECT * FROM ranked
ORDER BY materiality_flag DESC, materiality_rank NULLS LAST, bad_associated_share DESC, dimension, segment;
