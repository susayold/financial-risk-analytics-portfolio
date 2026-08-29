SELECT split_name,
       COUNT(*) AS row_count,
       MIN(issue_d) AS min_issue_d,
       MAX(issue_d) AS max_issue_d,
       COUNT(DISTINCT issue_cohort) AS issue_cohorts,
       SUM(CASE WHEN split_name IS NULL OR split_name NOT IN ('Development', 'Validation', 'OOT', 'Historical Shadow') THEN 1 ELSE 0 END) AS unassigned
FROM mart.mart_credit_application_core
GROUP BY split_name
ORDER BY CASE split_name WHEN 'Development' THEN 1 WHEN 'Validation' THEN 2 WHEN 'OOT' THEN 3 WHEN 'Historical Shadow' THEN 4 ELSE 5 END;
