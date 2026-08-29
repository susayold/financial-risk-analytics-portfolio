# B4 STATUS

**Stage:** B4 — `mart_credit_application_core`  
**Status:** `REVIEWED / PASS`  
**Block B overall:** `IN PROGRESS`  
**Next:** B5 — supplemental / pricing / rejected-context marts

## What was completed

- Built a canonical one-account analytical mart from `staging.stg_lc_granting_core`.
- Preserved the reviewed source population, target and chronological split.
- Added explicit key/time/target, champion-candidate, analysis-only and governance metadata fields.
- Re-ran seven B4 tests, including the B0–B3 regression subset.
- Exported aggregate reconciliation, schema, null-profile and test-result evidence.

## Gate result

`B4 = REVIEWED / PASS`

All locked counts reconcile: 1,347,681 mart rows, 1,347,681 distinct accounts, 0 duplicate IDs, 0 population loss, BAD 269,249, GOOD 1,078,432, 139 issue cohorts and 0 unassigned splits.

This status does not claim a model, predicted PD, LGD/EAD, ECL, pricing policy or production deployment.
