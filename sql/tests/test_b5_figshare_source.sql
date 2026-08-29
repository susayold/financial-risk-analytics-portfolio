-- B5T01/B5T02: source row and key checks; result is consumed by src/run_b5_tests.py.
SELECT figshare_source_split, COUNT(*) AS rows, COUNT(DISTINCT account_id) AS distinct_ids
FROM staging.stg_lc_figshare_enriched GROUP BY 1 ORDER BY 1;
