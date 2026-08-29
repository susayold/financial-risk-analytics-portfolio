-- B4T07: descriptive null profile only. No imputation or capping is applied.
WITH profile AS (
    SELECT 'revenue' AS field, COUNT(*) AS row_count, COUNT(*) FILTER (WHERE revenue IS NULL) AS null_count FROM mart.mart_credit_application_core
    UNION ALL SELECT 'dti_n', COUNT(*), COUNT(*) FILTER (WHERE dti_n IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'loan_amnt', COUNT(*), COUNT(*) FILTER (WHERE loan_amnt IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'fico_n', COUNT(*), COUNT(*) FILTER (WHERE fico_n IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'experience_c', COUNT(*), COUNT(*) FILTER (WHERE experience_c IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'emp_length', COUNT(*), COUNT(*) FILTER (WHERE emp_length IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'purpose', COUNT(*), COUNT(*) FILTER (WHERE purpose IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'home_ownership_n', COUNT(*), COUNT(*) FILTER (WHERE home_ownership_n IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'addr_state', COUNT(*), COUNT(*) FILTER (WHERE addr_state IS NULL) FROM mart.mart_credit_application_core
    UNION ALL SELECT 'zip_code', COUNT(*), COUNT(*) FILTER (WHERE zip_code IS NULL) FROM mart.mart_credit_application_core
)
SELECT field,
       row_count,
       null_count,
       null_count::DOUBLE / NULLIF(row_count, 0) AS null_rate
FROM profile
ORDER BY field;
