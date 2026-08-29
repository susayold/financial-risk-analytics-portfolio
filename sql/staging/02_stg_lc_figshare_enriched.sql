-- B5.2: Figshare is supplemental only. No target, imputation or core overwrite.
CREATE OR REPLACE TABLE staging.stg_lc_figshare_enriched AS
SELECT
    CAST(id AS VARCHAR) AS account_id,
    figshare_source_split,
    figshare_source_file,
    COALESCE(TRY_CAST(issue_d AS DATE), TRY_STRPTIME(CAST(issue_d AS VARCHAR), '%b-%Y')::DATE) AS issue_d_supp,
    TRY_CAST(loan_amnt AS DECIMAL(18,2)) AS loan_amnt_supp,
    TRY_CAST(annual_inc AS DECIMAL(18,2)) AS revenue_supp,
    TRY_CAST(dti AS DECIMAL(18,6)) AS dti_supp,
    (TRY_CAST(fico_range_low AS DECIMAL(10,2)) + TRY_CAST(fico_range_high AS DECIMAL(10,2))) / 2 AS fico_supp,
    NULLIF(LOWER(TRIM(purpose)), '') AS purpose_supp,
    NULLIF(UPPER(TRIM(home_ownership)), '') AS home_ownership_supp,
    NULLIF(UPPER(TRIM(addr_state)), '') AS addr_state_supp,
    NULLIF(TRIM(sub_grade), '') AS sub_grade,
    CASE WHEN NULLIF(TRIM(sub_grade), '') IS NOT NULL THEN SUBSTR(TRIM(sub_grade), 1, 1) END AS grade_derived,
    TRY_CAST(REPLACE(CAST(int_rate AS VARCHAR), '%', '') AS DECIMAL(10,4)) AS int_rate,
    TRY_CAST(installment AS DECIMAL(18,2)) AS installment,
    NULLIF(TRIM(term), '') AS term,
    'VALID' AS figshare_row_status,
    'FIGSHARE_22121477_V4' AS supplemental_version
FROM raw.figshare_union;
