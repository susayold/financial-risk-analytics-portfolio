# D2 Score-to-Loss Evidence Sub-audit

Updated: 2026-09-02

## Result

`PASS_WITH_LIMITATIONS` for the available scored-BAD to retrospective-loss
proxy bridge. This does not close the D2 governed-core bridge.

The check was run with `src/audit_block_d_score_loss_bridge.py`. It first
removed exact duplicate rows from the private D2 loss proxy for an
account-grain join, then compared the persisted D1 score-only mart against the
loss evidence.

| Check | Result |
|---|---:|
| D1 score-only mart rows | 127,885 |
| Scored BAD rows | 20,082 |
| Scored BAD rows matched to loss evidence | 20,082 |
| Scored-BAD loss-evidence coverage | 100.0000% |
| Target mismatches among matched rows | 0 |
| Exact duplicate loss-proxy rows | 1,993 |
| Exact duplicate account-ID groups | 1,993 |

The loss proxy has 271,353 rows before exact deduplication and 269,360 rows
after deduplication. The duplicate rows are exact duplicates across the
persisted proxy fields, so they must not be counted twice in any account-grain
bridge or LGD aggregation.

## Boundary

- This proves only that scored BAD accounts in the available Validation/OOT
  mart have corresponding retrospective loss evidence after exact-deduplication.
- The proxy contains resolved BAD rows only; it cannot prove loss coverage for
  GOOD rows or full-population D1 coverage.
- The governed-core ID list is still not materialized, so D2 remains
  `REVIEW_REQUIRED_BRIDGE_PENDING`.
- No empirical C8E LGD, Expected Loss, pricing, stress, or production claim is
  authorized from this sub-audit.
