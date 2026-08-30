# Block B Final QA — Closure Evidence

## Gate result

`BLOCK_B_FINAL_QA = PASS` — 15/15 tests passed.

The final QA reads persisted B4/B5 evidence, executes direct checks against the frozen core mart, validates B6–B9 gate artifacts, checks metric semantics and dimension informativeness, scans public claim boundaries, and verifies the sanitized public package/site consistency.

## Test map

| Tests | Scope | Result |
|---|---|---|
| BBF01–BBF03 | B4/B5 prior gates and closure static validation | PASS |
| BBF04–BBF07 | B6, B7, B8 and B9 gates | PASS |
| BBF08–BBF10 | Core population, target, `issue_d` and temporal split locks | PASS |
| BBF11 | B5 matched/core-only/Figshare-only/rejected populations | PASS |
| BBF12 | B7 primary rule and BAD-associated share reconciliation | PASS |
| BBF13 | B8 quasi-constant/informativeness control | PASS |
| BBF14 | Public claim-boundary validator | PASS |
| BBF15 | Public evidence completeness, repository privacy and website consistency | PASS |

## Locked baseline

- Core: 1,347,681 accounts; 269,249 BAD; 1,078,432 GOOD.
- Issue cohorts: 139; temporal authority: `issue_d`.
- Total `loan_amnt`: $19,417,698,475.
- BAD-associated `loan_amnt`: $4,186,020,700.
- `baseline_change: false`.

## Sanitization

Raw CSV, DuckDB and row-level data are not tracked in the repository and are not included in this evidence package. The execution runtime is temporary and lives on D only.

## Machine-readable artifacts

- `outputs/block_b_final/block_b_final_qa.json`
- `outputs/block_b_final/block_b_final_qa.csv`
- `outputs/block_b_final/block_b_final_reconciliation.json`
