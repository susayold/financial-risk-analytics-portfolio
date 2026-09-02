# D4 LGD Scenario Contract

## Status

`REVIEW_REQUIRED_BRIDGE_PENDING`

## Scope

This D4 run is the plan-permitted fallback while the exact bridge from the full
accepted loss source to the governed core and C8E matched population is pending.
It creates source-level severity anchors from resolved BAD rows only. The
primary anchor reference ends at issue year 2017; the 2018 shadow cohort is
monitor-only because Block C documented truncation/final-resolution concerns.
It does not create an empirical LGD estimate for C8E and does not use
`p_bad_final`.

## Input and formula

The input is the D2 `retrospective_loss_proxy.csv` output. Before aggregation,
the run removes exact full-row duplicates and verifies that no non-exact
duplicate `account_id` rows remain. The resulting evidence is account-grain;
the deduplication audit records 271,353 input rows, 1,993 exact duplicates
removed and 269,360 retained rows. The model LGD value is
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

The numeric anchors are persisted in `lgd_scenario_anchors.csv`; they are not
approved main-case assumptions until the governed-core bridge passes review.

## Required boundary

- No C8E `p_bad_final` is joined in this run.
- No segment-level C8E LGD claim is made.
- No D5 Expected Loss or D6 policy output may use these anchors as approved
  main-case inputs.
- No regulatory, IFRS 9, Basel, realized-profit or realized-loss claim is made.
- The exact governed-core ID bridge and target concordance remain open gates.
