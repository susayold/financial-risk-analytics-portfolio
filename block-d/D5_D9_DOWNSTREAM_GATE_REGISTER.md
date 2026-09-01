# Block D — D5–D9 Downstream Gate Register

Updated: 2026-09-02

## Purpose

This register records the downstream stages from the execution plan without
inventing results when upstream evidence is incomplete. A stage is marked
`HOLD_UPSTREAM_EVIDENCE` when its contract and acceptance criteria are ready,
but the stage must not produce a business number or approval claim.

## Gate register

| Stage | Purpose | Current status | Why it cannot open |
|---|---|---|---|
| D5 | Combine `p_bad_final`, LGD and EAD into analytical expected-loss proxy | HOLD | D1/D2 bridges pending; D4 LGD scenario-only |
| D6 | Map validated risk/economics evidence to decision actions | HOLD | D1 and D5 not passed; no owner-approved thresholds |
| D7 | Test pricing adequacy and score-to-pricing consistency | HOLD | Exact pricing bridge and D5 output unavailable |
| D8 | Run explicit stress and sensitivity scenarios | HOLD | No passed D5 baseline; D4 not approved as main-case LGD |
| D9 | Final closure, audit manifest and owner sign-off | HOLD | D1/D2/D4 and all downstream gates remain open |

## Evidence currently available

- D0 governance contract: PASS, 10/10 gates.
- D1: contract and QA schema exist; full Development score artifact is not
  materialized.
- D2: full accepted-source audit exists for 2,275,739 source rows; exact
  governed-core ID bridge remains pending.
- D3: EAD proxy evidence exists for the declared 331,865-row pricing-source
  scope, with limitations.
- D4: source-level LGD scenario anchors exist for the <=2017 reference cohort;
  2018 remains monitor-only; anchors are not approved empirical C8E LGD.

## Inputs needed to open the register

1. Persisted C8E Development predictions/scores joined to the governed
   Development population.
2. Validated C8E score-to-pricing bridge with `term`, `int_rate`,
   `installment`, `sub_grade` and `grade_derived`.
3. Exact governed-core ID and target bridge for the D2 full-source evidence.
4. Owner decision on the approved LGD population and timing boundary.

## Claim boundary

Until these inputs pass, the project may show governance contracts, source
audits, EAD mechanics and scenario-only LGD evidence. It may not show a frozen
expected loss, production decision policy, pricing adequacy, stress loss or
`BLOCK D = LOCKED` claim.

