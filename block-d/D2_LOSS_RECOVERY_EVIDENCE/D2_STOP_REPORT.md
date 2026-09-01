# D2 Loss & Recovery Evidence — Stop Report

## Status

`REVIEW_REQUIRED_BRIDGE_PENDING`

The full accepted-source file was recovered on the D runtime and audited in streaming mode. It contains the required retrospective recovery/loss fields. The audit covered 2,275,739 source rows, of which 1,356,914 have resolved outcomes: 271,353 BAD and 1,085,561 GOOD.

The exact bridge to the 1,347,681-row governed core is still pending because the governed-core ID list is not materialized in the current D runtime. Therefore the loss output is source-level retrospective evidence and is not yet an empirical LGD for the C8E population.

A bounded score-to-loss sub-audit found 1,993 exact duplicate rows in the BAD-only loss proxy. After exact-row deduplication, all 20,082 scored-BAD accounts in the available Validation/OOT score mart matched loss evidence with zero target mismatches. This does not establish GOOD-row coverage or the governed-core bridge.

## Consequence for downstream stages

- Empirical D4 LGD challenger: not yet opened for the C8E population; exact bridge remains a gate.
- Source-level loss evidence is available for retrospective distribution and anomaly review.
- Fallback permitted by the plan: scenario LGD only, subject to explicit assumptions and approval.
- D5 Expected Loss cannot be frozen until D1 scores and the D4 LGD method are both approved.
- The 1.6 GB raw source is temporary D-runtime input and is not committed to GitHub or uploaded as raw data.
