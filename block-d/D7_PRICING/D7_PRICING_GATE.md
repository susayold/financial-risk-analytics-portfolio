# D7 — Pricing Adequacy Gate

## Status

`HOLD_UPSTREAM_EVIDENCE` — pricing bridge and adequacy contract defined; no
price, margin or profitability result is claimed.

## Required pricing bridge

The same account-level key must carry the frozen score and the governed pricing
fields:

```text
account_id, term, int_rate, installment, sub_grade, grade_derived,
loan_amnt, p_bad_final, LGD, EAD
```

The Block B → C re-contract for `term`, `int_rate` and `installment` is an
explicit exception and must remain visible in the lineage.

## Required acceptance tests

1. One-to-one score-to-pricing join at the declared grain.
2. No post-outcome fields used in pricing inputs.
3. Cash-flow and EAD definitions reconcile to the declared source scope.
4. Adequacy is evaluated by split, risk band and scenario, with uncertainty
   shown.
5. No realized profitability claim unless costs, fees, recoveries and timing
   are actually evidenced.

## Current decision

D7 remains closed because the validated score-to-pricing bridge and D5
economics output are not materialized.

