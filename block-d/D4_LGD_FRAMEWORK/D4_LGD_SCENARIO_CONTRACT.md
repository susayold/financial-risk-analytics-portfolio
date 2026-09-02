# D4 LGD Scenario Contract

## Status

`BRIDGE_RECONCILED_APPROVAL_PENDING`

## Scope

This D4 run uses the exact governed-core BAD evidence bridge. It creates
source-level severity anchors from resolved BAD rows only. The
primary anchor reference ends at issue year 2017; the 2018 shadow cohort is
monitor-only because Block C documented truncation/final-resolution concerns.
The primary anchor calculation does not create an empirical LGD estimate for
C8E and does not use `p_bad_final`. A separate descriptive score-to-loss
linkage is materialized for review, but it is not an empirical LGD model or an
approved main-case input.

## Input and formula

The input is the D2 `retrospective_loss_proxy.csv` output. Before aggregation,
the run removes exact full-row duplicates and verifies that no non-exact
duplicate `account_id` rows remain. The resulting evidence is account-grain;
the deduplication audit records 271,353 input rows, 1,993 exact duplicates
removed before the governed-core filter; 269,249 governed BAD rows are retained
in the current run. The model LGD value is
the D2 governed proxy:

```text
retrospective_lgd_proxy_model
  = clip((funded_amnt - total_rec_prncp - recoveries
          + collection_recovery_fee) / funded_amnt, 0, 1)
```

Only rows with a bounded model value are used. The D2 quality status remains
visible; `CLIPPED_FOR_MODELING` rows are counted separately. Scenario quantiles
use issue years through 2017; 2018 is retained in the temporal diagnostic but
excluded from the primary anchors.

## Scenario anchors

| Scenario | Anchor | Role |
|---|---:|---|
| `LGD_LOW_SEVERITY_Q25` | Q25 | Benign source-level severity anchor |
| `LGD_CENTRAL_Q50` | Q50 | Central source-level severity anchor |
| `LGD_ADVERSE_Q75` | Q75 | Adverse source-level severity anchor |
| `LGD_SEVERE_Q90` | Q90 | Severe source-level severity anchor |

The numeric anchors are persisted in `lgd_scenario_anchors.csv`; the governed
bridge passes, but they remain unapproved main-case assumptions pending an
explicit owner decision on LGD/timing.

## Required boundary

- No C8E `p_bad_final` is joined in this run.
- No segment-level C8E LGD claim is made.
- No D5 Expected Loss or D6 policy output may use these anchors as approved
  main-case inputs.
- No regulatory, IFRS 9, Basel, realized-profit or realized-loss claim is made.
- The exact governed-core ID bridge and target concordance pass in D2. The
  descriptive score-conditional linkage does not replace owner approval,
  score-conditional LGD modeling or the main-case timing decision.
