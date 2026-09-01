# D5 — Expected Loss Gate

## Status

`HOLD_UPSTREAM_EVIDENCE` — gate definition complete; no approved expected-loss
number has been calculated.

## Purpose

D5 is the first stage allowed to combine the frozen Block C score with the
economics evidence:

```text
expected_loss_proxy = p_bad_final × LGD × EAD
```

This is an analytical proxy only. It is not a regulatory PD, LGD, EAD, ECL,
IFRS 9 or Basel calculation.

## Required upstream evidence

| Input | Required condition | Current state |
|---|---|---|
| D1 score mart | Full governed account grain with Development, Validation and OOT coverage | HOLD — Development scores not materialized |
| D2 loss bridge | Exact governed-core ID bridge, target concordance and recovery reconciliation | HOLD — source-level audit complete; core bridge pending |
| D3 EAD | Declared EAD scope and valid timing/schedule treatment | AVAILABLE with limitations — 331,865-row pricing-source scope |
| D4 LGD | Approved main-case LGD evidence linked to the same governed population | HOLD — current anchors are scenario-only |

## Gate checks before any D5 number

1. Reconcile D1 row counts to the governed population and split definitions.
2. Prove that `p_bad_final` is joined at account grain without duplicate keys.
3. Reconcile D2 BAD/GOOD labels to the governed core; retain exclusions and
   monitor-only rows explicitly.
4. Declare whether D5 is score-conditional, portfolio-average, or both.
5. Use only a D4 LGD input whose population, timing and approval status are
   compatible with D1/D2.
6. Reconcile `loan_amnt` to the declared origination EAD proxy before any EL
   aggregation.
7. Produce Development, Validation and OOT EL summaries with no leakage from
   post-outcome fields.

## Current decision

No baseline, segment, band or split-level expected loss is reported. D5 cannot
open until D1 and D2 bridges pass and D4 is promoted from scenario-only to an
approved input under the same population contract.

