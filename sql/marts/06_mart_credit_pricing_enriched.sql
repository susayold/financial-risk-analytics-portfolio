-- B5.5: matched-only pricing/economics mart. B4 core columns remain authoritative.
CREATE OR REPLACE TABLE mart.mart_credit_pricing_enriched AS
SELECT
    c.account_id,
    c.issue_d, c.issue_year, c.issue_month, c.issue_cohort, c.split_name,
    c.actual_default, c.target_label,
    c.revenue, c.dti_n, c.loan_amnt, c.fico_n, c.experience_c, c.emp_length,
    c.purpose, c.home_ownership_n, c.addr_state, c.zip_code,
    f.sub_grade, f.grade_derived, f.int_rate, f.installment, f.term,
    f.figshare_source_split, f.figshare_source_file,
    b.issue_d_match, b.loan_amnt_match, b.revenue_match, b.dti_match,
    b.fico_match, b.purpose_match, b.home_ownership_match, b.addr_state_match,
    'ZENODO_FIGSHARE_MATCHED_ENRICHED' AS source_population,
    'ZENODO_11295916' AS core_source_version,
    'FIGSHARE_22121477_V4' AS supplemental_version,
    'B5_BRIDGE_v1.0' AS bridge_version,
    'B5_PRICING_v1.0' AS pricing_mart_version,
    CURRENT_TIMESTAMP AS pricing_mart_build_ts
FROM mart.mart_credit_application_core c
JOIN bridge.bridge_lc_core_figshare b ON b.account_id = c.account_id AND b.match_status = 'MATCHED'
JOIN staging.stg_lc_figshare_enriched f ON f.account_id = c.account_id;
