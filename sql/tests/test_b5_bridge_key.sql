-- B5T04: one bridge row per account_id.
SELECT COUNT(*) AS rows, COUNT(DISTINCT account_id) AS distinct_ids,
       COUNT(*) - COUNT(DISTINCT account_id) AS duplicates
FROM bridge.bridge_lc_core_figshare;
