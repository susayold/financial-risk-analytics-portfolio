-- B5.3: FULL OUTER bridge, one row per account_id, core authority retained.
CREATE OR REPLACE TABLE bridge.bridge_lc_core_figshare AS
SELECT
    COALESCE(c.account_id, f.account_id) AS account_id,
    c.account_id IS NOT NULL AS core_present,
    f.account_id IS NOT NULL AS figshare_present,
    CASE WHEN c.account_id IS NOT NULL AND f.account_id IS NOT NULL THEN 'MATCHED'
         WHEN c.account_id IS NOT NULL THEN 'CORE_ONLY'
         ELSE 'FIGSHARE_ONLY' END AS match_status,
    c.issue_d AS core_issue_d,
    f.issue_d_supp AS figshare_issue_d,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE c.issue_d = f.issue_d_supp END AS issue_d_match,
    c.loan_amnt AS core_loan_amnt,
    f.loan_amnt_supp AS figshare_loan_amnt,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE abs(c.loan_amnt - f.loan_amnt_supp) <= 0.01 END AS loan_amnt_match,
    c.revenue AS core_revenue,
    f.revenue_supp AS figshare_revenue,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE abs(c.revenue - f.revenue_supp) <= 0.01 END AS revenue_match,
    c.dti_n AS core_dti,
    f.dti_supp AS figshare_dti,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE abs(c.dti_n - f.dti_supp) <= 0.0001 END AS dti_match,
    c.fico_n AS core_fico,
    f.fico_supp AS figshare_fico,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE abs(c.fico_n - f.fico_supp) <= 0.01 END AS fico_match,
    c.purpose AS core_purpose,
    f.purpose_supp AS figshare_purpose,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE lower(trim(c.purpose)) = lower(trim(f.purpose_supp)) END AS purpose_match,
    c.home_ownership_n AS core_home_ownership,
    f.home_ownership_supp AS figshare_home_ownership,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE upper(trim(c.home_ownership_n)) = upper(trim(f.home_ownership_supp)) END AS home_ownership_match,
    c.addr_state AS core_addr_state,
    f.addr_state_supp AS figshare_addr_state,
    CASE WHEN c.account_id IS NULL OR f.account_id IS NULL THEN NULL ELSE upper(trim(c.addr_state)) = upper(trim(f.addr_state_supp)) END AS addr_state_match,
    'B5_BRIDGE_v1.0' AS bridge_version,
    CURRENT_TIMESTAMP AS bridge_build_ts
FROM mart.mart_credit_application_core c
FULL OUTER JOIN staging.stg_lc_figshare_enriched f ON c.account_id = f.account_id;
