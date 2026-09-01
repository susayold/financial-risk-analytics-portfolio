# D3 EAD Framework Contract

## Status

`PASS_WITH_LIMITATIONS — P2_PRICING_MATCHED_PUBLIC_SOURCE`

## Main method

```text
ead_origination_proxy = loan_amnt
```

This is an origination exposure proxy, not an observed balance at default and not a regulatory EAD estimate.

## Contractual scenarios

For each pricing-matched account:

```text
P   = loan_amnt
r   = int_rate / 100 / 12
PMT = installment

balance_k = P × (1+r)^k - PMT × (((1+r)^k - 1) / r)
```

If `r = 0`, use `max(P - PMT × k, 0)`. Balances are floored at zero and no scenario is emitted beyond contractual term. Required scenario points are 0, 6, 12, 18, 24, 36 and 48 months, with 48 months active only for 60-month contracts.

## Scope limitation

The current run uses the 331,865-row accepted/pricing source fallback. It is not silently presented as C8E/C9 full-population model coverage. `p_bad_final` is not inserted because score-to-source materialization is still incomplete.
