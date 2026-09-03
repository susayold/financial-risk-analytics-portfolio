# Block D Final Closure Report

## Decision

`CLOSED_WITH_LIMITATIONS_PORTFOLIO`

Block D is closed for the CRD.PI portfolio analytical scope. The final micro-remediation confirmed the predeclared LGD challenger set, corrected exposure-weighted segment EL-rate aggregation, separated core credit stress from contractual EAD timing sensitivity, completed portfolio project-owner attribution when supplied, and strengthened semantic QA. No production or regulatory authorization is claimed.

## Final methods

- Frozen probability: `p_bad_final` from `C8E_RICH_BUREAU_CATBOOST_79F`.
- LGD: `LGD_CENTRAL_Q50`; Huber, Tweedie, and CatBoost challengers were run and rejected against the predeclared materiality rule.
- EAD: D3 origination proxy for the core D8 severity ladder; contractual timing is a separate `D8_EAD_TIMING_SENSITIVITY.csv` output.
- Expected loss: `EL_MAIN_ANALYTICAL = p_bad_final × lgd_proxy × ead_proxy`.
- Policy: historical decision simulation, derived on Validation-2016 and replayed unchanged on 2017.
- Pricing: `DESCRIPTIVE_ONLY`.
- Stress: `D8-FINAL-1.1` Base/Mild/Adverse/Severe credit-quality sensitivity with separate EAD timing and reverse-stress outputs.

## Scope boundary

`production_authorized=false`; `regulatory_compliance_claimed=false`. This is not IFRS 9, Basel, regulatory LGD/EAD/ECL, realized profitability, observed EAD, or verified 12-month PD.

## Semantic remediation

- Status: `PASS`
- Checks: `8/8`
- Project owner: `susayold`
- Decision date: `2026-09-03`

## Handoff

Next action: `MOVE_TO_BLOCK_E`. Carry forward D4 final LGD, D5 analytical EL, D6 historical policy simulation, D7 descriptive-only pricing, D8 stress outputs, C9 calibration monitoring, and all limitations.
