# D2 Loss & Recovery Evidence — Stop Report

## Status

`BRIDGE_RECONCILED / PASS_WITH_LIMITATIONS`

The full accepted-source file was recovered on the D runtime and audited in streaming mode. It contains the required retrospective recovery/loss fields. The audit covered 2,275,739 source rows, of which 1,356,914 have resolved outcomes: 271,353 BAD and 1,085,561 GOOD.

The exact bridge is now complete. All 1,347,681 governed account IDs match the
accepted source; source targets and loan amounts reconcile 100%, with no source
duplicate-ID groups or conflicts. The loss output remains retrospective
BAD-only evidence and is not a regulatory or empirical C8E LGD model.

A bounded score-to-loss sub-audit found 1,993 exact duplicate rows in the BAD-only loss proxy. After exact-row deduplication, all 20,082 scored-BAD accounts in the available Validation/OOT score mart matched loss evidence with zero target mismatches. This does not establish GOOD-row coverage or the governed-core bridge.

The deduplicated account-grain proxy is now persisted as
`retrospective_loss_proxy_account_grain.csv` with its own audit manifest. D4
uses this account-grain view for LGD scenario aggregation; the D4 bridge and
approval boundary remain open.

## Consequence for downstream stages

- D4 population compatibility: bridge reconciled; main-case LGD approval remains a separate governance decision.
- Source-level loss evidence is available for retrospective distribution and anomaly review.
- Fallback permitted by the plan: scenario LGD only, subject to explicit assumptions and approval.
- D5 Expected Loss cannot be frozen until D1 scores and the D4 LGD method are both approved.
- The 1.6 GB raw source was temporary D-runtime input and is not committed to GitHub or uploaded as raw data.
