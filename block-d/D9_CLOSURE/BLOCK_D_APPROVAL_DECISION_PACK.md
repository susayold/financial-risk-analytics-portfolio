# Block D — Approval Decision Pack

Updated: 2026-09-03  
Purpose: provide a compact, evidence-backed comparison for the pending D4–D8 owner decisions.

## Review boundary

This pack is a decision aid built from the existing D4 LGD anchors, D5
12-month EAD scenarios and D8 illustrative sensitivity outputs. It is not an
approved main-case, forecast, regulatory PD/LGD/EAD/ECL result, profitability
analysis or production policy.

Common scope for the comparison:

- 310,066 matched scored accounts.
- 12-month declared EAD scenario.
- D4 reference cohort: `issue_year <= 2017`.
- 2018 Historical Shadow remains monitor-only.
- EL proxy formula: `p_bad_final × LGD assumption × declared EAD scenario`.

## D4 LGD choice comparison

| Option | LGD anchor | D5 12-month EL proxy rate | D8 illustrative adverse rate* | Interpretation |
|---|---:|---:|---:|---|
| Q25 / `LGD_LOW_SEVERITY_Q25` | 48.9670% | 9.2663% | 12.9971% | Lower-severity sensitivity anchor |
| Q50 / `LGD_CENTRAL_Q50` | 66.7385% | 12.6292% | 16.9141% | Median reference anchor |
| Q75 / `LGD_ADVERSE_Q75` | 79.0297% | 14.9552% | 19.6233% | Adverse sensitivity anchor |
| Q90 / `LGD_SEVERE_Q90` | 86.5786% | 16.3837% | 21.2871% | Severe sensitivity anchor |

\* Illustrative adverse rate uses the existing D8 cell with PD shock `+25%`,
LGD additive shock `+10 percentage points` and EAD shock `+5%`. It is not a
forecast or approved stress result.

The EL proxy rates are weighted over the declared 12-month EAD scenario for
the matched scored subset. They must not be presented as realized loss,
regulatory expected loss or a production risk appetite threshold.

## Decisions required

| Decision | Decision options | Current state |
|---|---|---|
| D4 main-case LGD | Select Q25, Q50, Q75 or Q90 | PENDING |
| D4 timing boundary | Approve `issue_year <= 2017` reference and 2018 monitor-only treatment, or document an alternative | PENDING |
| D5 EL usage | Accept the formula only as an analytical proxy with declared EAD | PENDING |
| D6 policy | Approve or revise the five-band reporting/action mapping, reason-coded overrides and monitoring limits | PENDING |
| D7 pricing | Retain descriptive-only scope, or provide approved cost/fee/timing evidence for adequacy analysis | PENDING |
| D8 stress | Approve the existing PD/LGD/EAD shocks, or document alternatives | PENDING |
| D9 ownership | Record data, model and risk owner sign-off | PENDING |

## Unlock condition

The decision pack does not unlock D9 by itself. The selected decisions must be
recorded in `D9_APPROVAL_REGISTER.md`, followed by a rerun of the final QA and
closure manifest. Until then, the valid status remains
`NOT_LOCKED_REVIEW_REQUIRED`.

## Source evidence

- D4: `D4_LGD_FRAMEWORK/D4_RUN_AUDIT.json` and governed LGD scenario anchors.
- D5: `D5_EXPECTED_LOSS/D5_ANALYTICAL_SCENARIO_AUDIT.json` and the private
  scenario mart.
- D8: `D8_STRESS/D8_ILLUSTRATIVE_SENSITIVITY_AUDIT.json` and the private
  sensitivity summary.
