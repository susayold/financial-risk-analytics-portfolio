-- B5T05: field flags are calculated in the bridge; null comparisons are explicit.
SELECT COUNT(*) FILTER (WHERE match_status='MATCHED' AND issue_d_match) AS issue_d_equal,
       COUNT(*) FILTER (WHERE match_status='MATCHED' AND revenue_match=FALSE) AS revenue_conflicts,
       COUNT(*) FILTER (WHERE match_status='MATCHED' AND dti_match=FALSE) AS dti_conflicts
FROM bridge.bridge_lc_core_figshare;
