-- B5T03: locked bridge populations.
SELECT match_status, COUNT(*) AS rows
FROM bridge.bridge_lc_core_figshare GROUP BY 1 ORDER BY 1;
