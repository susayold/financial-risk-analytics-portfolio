-- B5T11: exact B4 regression after B5.
SELECT COUNT(*) AS rows, COUNT(DISTINCT account_id) AS distinct_ids,
       SUM(actual_default) AS bad, COUNT(*)-SUM(actual_default) AS good,
       COUNT(DISTINCT issue_cohort) AS cohorts
FROM mart.mart_credit_application_core;
