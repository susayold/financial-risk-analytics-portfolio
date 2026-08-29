-- B5T09/B5T10: outcome boundary is structural and flag-based.
SELECT COUNT(*) AS rows, COUNT(DISTINCT rejected_record_id) AS distinct_keys,
       COUNT(*) FILTER (WHERE outcome_observed) AS outcome_true,
       COUNT(*) FILTER (WHERE model_target_eligible) AS target_true,
       COUNT(*) FILTER (WHERE champion_merge_eligible) AS champion_true
FROM mart.mart_rejected_context;
