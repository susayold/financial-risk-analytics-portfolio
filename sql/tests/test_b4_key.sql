SELECT COUNT(*) AS row_count,
       COUNT(DISTINCT account_id) AS distinct_accounts,
       SUM(CASE WHEN account_id IS NULL THEN 1 ELSE 0 END) AS null_account_id,
       COUNT(*) - COUNT(DISTINCT account_id) AS duplicate_account_id
FROM mart.mart_credit_application_core;
