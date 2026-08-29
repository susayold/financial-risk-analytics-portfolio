-- B5.7: rejected context only. Outcome semantics are intentionally absent.
CREATE OR REPLACE TABLE mart.mart_rejected_context AS
SELECT * FROM staging.stg_lc_rejected;
