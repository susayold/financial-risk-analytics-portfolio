SELECT SUM(CASE WHEN actual_default = 1 THEN 1 ELSE 0 END) AS bad,
       SUM(CASE WHEN actual_default = 0 THEN 1 ELSE 0 END) AS good,
       AVG(actual_default) AS bad_rate,
       SUM(CASE WHEN actual_default IS NULL OR actual_default NOT IN (0, 1) THEN 1 ELSE 0 END) AS unknown_target
FROM mart.mart_credit_application_core;
