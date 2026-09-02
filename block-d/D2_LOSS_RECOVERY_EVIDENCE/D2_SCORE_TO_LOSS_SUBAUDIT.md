# D2 Score-to-Loss Evidence Sub-audit

Updated: 2026-09-02

## Result

`PASS_WITH_LIMITATIONS` for the current D1 scored-BAD to retrospective-loss
proxy bridge. The exact governed-core bridge is now separately reconciled and
referenced below; neither result creates an approved or regulatory LGD.

The current check joins the private 310,066-row D1 decision mart to the
governed BAD evidence at account grain. The earlier score-only audit remains
retained as historical evidence, but must not be confused with the current D1
mart.

| Check | Result |
|---|---:|
| Current D1 decision mart rows | 310,066 |
| Current scored BAD rows | 49,049 |
| Current scored BAD rows matched to loss evidence | 49,049 |
| Scored-BAD loss-evidence coverage | 100.0000% |
| Target mismatches among matched rows | 0 |
| Matched loss quality: VALID / CLIPPED_FOR_MODELING | 48,917 / 132 |
| Governed BAD evidence rows | 269,249 |

The historical score-only audit covered 127,885 rows and 20,082 scored BAD
rows. Its 1,993 exact duplicate loss-proxy rows were removed for that legacy
account-grain join; the current governed BAD evidence used by D4 is already
account-grain reconciled and has no remaining exact duplicate rows.

The loss proxy has 271,353 rows before exact deduplication and 269,360 rows
after deduplication. The duplicate rows are exact duplicates across the
persisted proxy fields, so they must not be counted twice in any account-grain
bridge or LGD aggregation.

## Boundary

- This proves that current D1 scored BAD accounts in the matched scored subset
  have corresponding retrospective loss evidence.
- The proxy contains resolved BAD rows only; it cannot prove loss coverage for
  GOOD rows or full-population D1 coverage.
- The governed-core ID and target/loan amount bridge pass in the companion
  audit; this sub-audit itself remains limited to scored BAD rows and does not
  imply full-governed score coverage.
- No empirical C8E LGD, Expected Loss, pricing, stress, or production claim is
  authorized from this sub-audit.
