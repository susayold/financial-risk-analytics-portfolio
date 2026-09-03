# Block D Status

## Current status

`CLOSED_WITH_LIMITATIONS_PORTFOLIO`

Block D is complete for the CRD.PI portfolio-project scope. It is not a production authorization and makes no regulatory compliance claim.

| Axis | Result |
|---|---:|
| Execution coverage | 100% |
| Portfolio requirement resolution | 100% |
| Technical QA | N/N PASS |
| Artifact checksum integrity | 100% |
| Production / regulatory readiness | NOT_IN_SCOPE |

## Frozen analytical chain

`C8E_RICH_BUREAU_CATBOOST_79F p_bad_final → D4 LGD_CENTRAL_Q50 → D3 contractual EAD proxy → EL_MAIN_ANALYTICAL → D6 historical policy simulation → D8 analytical stress`.

D4 empirical LGD challenger was run on 49,049 matched BAD rows and rejected by the predeclared materiality rule; Q50 remains the central analytical scenario. D7 is `DESCRIPTIVE_ONLY` because governed cost, fee, servicing, capital, and realized timing inputs are absent.

## Micro-remediation checkpoint

The final micro-remediation has executed CatBoostRegressor alongside Huber/Tweedie, corrected D5 segment EL rates to `sum(EL) / sum(EAD)`, and versioned D8 stress as `D8-FINAL-1.1` with a consistent origination-EAD severity basis plus separate contractual timing sensitivity. Semantic QA is currently `7/8 PASS`; the only remaining gate is user-supplied portfolio project-owner identifier and decision date. The final release tag is intentionally withheld until that manual field is supplied.

## Limitations carried forward

- C8E is a matched-population score mart, not full-core score coverage.
- The target is a final-resolution observed default flag, not verified 12-month PD.
- LGD, EAD, and expected loss are analytical proxies.
- 2018 is monitor-only for the primary cohort.
- Policy outputs are historical simulations; override authority is not in scope.
- Pricing outputs are descriptive diagnostics, not profitability.

See `D9_CLOSURE/BLOCK_D_FINAL_CLOSURE_REPORT.md` and `D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json`.
