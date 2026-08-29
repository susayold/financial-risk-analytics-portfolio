SELECT (SELECT COUNT(*) FROM staging.stg_lc_granting_core) AS staging_rows,
       (SELECT COUNT(*) FROM mart.mart_credit_application_core) AS mart_rows,
       (SELECT COUNT(*) FROM staging.stg_lc_granting_core)
       - (SELECT COUNT(*) FROM mart.mart_credit_application_core) AS population_loss;
