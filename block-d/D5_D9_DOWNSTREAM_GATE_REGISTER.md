# Block D — D5–D9 Downstream Gate Register

Updated: 2026-09-02

## Purpose

This register records the downstream stages from the execution plan without
inventing results when upstream evidence is incomplete. A stage is marked
`CONTROLLED_HOLD` when an analytical pack exists for review but the stage must
not produce a business, production or approval claim.

## Gate register

| Stage | Purpose | Current status | Why it cannot open |
|---|---|---|---|
| D5 | Combine `p_bad_final`, LGD and EAD into analytical expected-loss proxy | CONTROLLED HOLD | Scenario pack executed for review; D4 main-case approval pending |
| D6 | Map validated risk/economics evidence to decision actions | CONTROLLED HOLD | Proposed mapping exists; no owner-approved thresholds |
| D7 | Test pricing adequacy and score-to-pricing consistency | CONTROLLED HOLD | Descriptive pricing bridge exists; costs/fees and profitability approval unavailable |
| D8 | Run explicit stress and sensitivity scenarios | CONTROLLED HOLD | Illustrative sensitivity exists; no passed/approved D5 baseline |
| D9 | Final closure, audit manifest and owner sign-off | CONTROLLED HOLD | Review manifest exists; D4/D6/D7/D8 approvals remain open |

## Evidence currently available

- D0 governance contract: PASS, 10/10 gates.
- D1: 310,066-row matched scored mart exists with Development replay,
  Validation/OOT evidence and pricing bridge; full-governed score coverage is
  not claimed.
- D2: full accepted-source audit and exact 1,347,681-row governed-core bridge
  pass; loss evidence remains retrospective BAD-only.
- D3: EAD proxy evidence exists for the declared 331,865-row pricing-source
  scope, with limitations.
- D4: governed BAD-only LGD scenario anchors exist for the <=2017 reference
  cohort; 2018 remains monitor-only; anchors are not approved main-case LGD.

## Inputs needed to open the register

1. Owner decision on the approved LGD population and timing boundary.
2. Approval of D5 analytical proxy use, D6 policy thresholds, D7 pricing
   assumptions and D8 shock policy.

## Claim boundary

Until these approvals pass, the project may show governance contracts, source
audits, EAD mechanics and explicitly bounded analytical scenario packs. It may
not show a frozen expected loss, production decision policy, pricing adequacy,
realized/stress loss or `BLOCK D = LOCKED` claim.
