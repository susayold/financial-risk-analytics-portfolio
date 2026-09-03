# Block D Final Closure Report

## Decision

`CLOSED_WITH_LIMITATIONS_PORTFOLIO`

Block D is analytically complete and closed for the CRD.PI portfolio scope. All planned D0–D9 analytical components have either been executed or closed under an explicit Master Plan stop condition. Technical QA and artifact-integrity controls pass. Remaining limitations are structural claim boundaries rather than unresolved implementation defects. No production or regulatory authorization is claimed.

## Final methods

- Frozen probability: `p_bad_final` from `C8E_RICH_BUREAU_CATBOOST_79F`.
- LGD: `LGD_CENTRAL_Q50`; the empirical challenger was run and rejected against the predeclared materiality rule.
- EAD: D3 contractual timing proxy.
- Expected loss: `EL_MAIN_ANALYTICAL = p_bad_final × lgd_proxy × ead_proxy`.
- Policy: historical decision simulation, derived on Validation-2016 and replayed unchanged on 2017.
- Pricing: `DESCRIPTIVE_ONLY`.
- Stress: Base/Mild/Adverse/Severe analytical sensitivity with reverse-stress breakpoints.

## Scope boundary

`production_authorized=false`; `regulatory_compliance_claimed=false`. This is not IFRS 9, Basel, regulatory LGD/EAD/ECL, realized profitability, observed EAD, or verified 12-month PD.

## Handoff

Next action: `MOVE_TO_BLOCK_E`. Carry forward D4 final LGD, D5 analytical EL, D6 historical policy simulation, D7 descriptive-only pricing, D8 stress outputs, C9 calibration monitoring, and all limitations.
