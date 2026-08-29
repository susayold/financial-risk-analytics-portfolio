-- B5T07: matched-only pricing mart grain.
SELECT COUNT(*) AS rows, COUNT(DISTINCT account_id) AS distinct_ids,
       COUNT(*) - COUNT(DISTINCT account_id) AS duplicates
FROM mart.mart_credit_pricing_enriched;
