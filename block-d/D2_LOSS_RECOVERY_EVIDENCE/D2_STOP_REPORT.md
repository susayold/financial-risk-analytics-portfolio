# D2 Loss & Recovery Evidence — Stop Report

## Status

`BRIDGE_RECONCILED / PASS_WITH_LIMITATIONS`

The legacy source-level loss audit covered the artifact
`LendingClub_2007_to_2018Q4.csv` (2,275,739 rows; 1,356,914 resolved rows,
271,353 BAD and 1,085,561 GOOD). The exact governed bridge was then run against
the separately checksummed accepted bridge artifact
`accepted_2007_to_2018Q4.csv` (2,260,701 rows). These are distinct source
artifacts and are not combined into one row-count claim.

The exact bridge is now complete. All 1,347,681 governed account IDs match the
accepted bridge artifact; source targets and loan amounts reconcile 100%, with
no source duplicate-ID groups or conflicts. The loss output remains
retrospective BAD-only evidence and is not a regulatory or empirical C8E LGD
model.

A historical score-only sub-audit found 1,993 exact duplicate rows in the
BAD-only loss proxy. The current D1 decision mart now bridges all 49,049
scored-BAD accounts to governed loss evidence with zero target mismatches; the
historical 20,082-row result remains retained for provenance. This does not
establish GOOD-row coverage or full-governed score coverage.

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
