# D2 Loss Proxy Contract

## Current status

`BRIDGE_RECONCILED / PASS_WITH_LIMITATIONS`

The full accepted LendingClub source contains retrospective payment and recovery fields. D2 derives these fields only for retrospective loss evidence:

```text
gross_principal_loss_proxy = funded_amnt - total_rec_prncp
net_principal_loss_proxy = funded_amnt - total_rec_prncp - recoveries
net_economic_loss_proxy = funded_amnt - total_rec_prncp - recoveries + collection_recovery_fee
retrospective_lgd_proxy_raw = net_economic_loss_proxy / funded_amnt
```

The source status mapping is explicit: `Charged Off`/`Default` are BAD; `Fully Paid` is GOOD; current/late/grace and other unresolved statuses are not used as resolved loss outcomes.

Anomalies are not silently clipped. Rows are classified as `VALID`, `CLIPPED_FOR_MODELING`, `EXCLUDED_DATA_ERROR` or `MISSING`, with counts in `D2_TEST_RESULTS.json`.

## Claim boundary

This run is retrospective BAD-only evidence. The exact bridge to the 1,347,681-row
governed core now passes in `D2_GOVERNED_CORE_BRIDGE_AUDIT.json`: IDs, target
labels and loan amounts reconcile 100%. The output still must not be described
as regulatory LGD or score-conditional empirical LGD for C8E.
