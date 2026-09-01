# D0 Claim Boundary

## Supported claims

- `p_bad_final` is the frozen C8E final-resolution BAD probability score.
- `expected_loss_proxy = p_bad_final × lgd_proxy × ead_proxy` is an analytical Expected Loss proxy.
- `ead_origination_proxy = loan_amnt` is an origination exposure proxy.
- LGD outputs are scenario or retrospective loss proxies, subject to D2/D4 evidence.
- Policy results are historical simulations on declared populations.
- Pricing results are observed contractual pricing adequacy analyses on the matched enriched subset.
- Stress results are scenario analyses, not macro forecasts.

## Prohibited claims

- `p_bad_final` must not be renamed `pd_12m`, regulatory PD, Basel PD or IFRS 9 PD.
- `lgd_proxy` must not be called observed regulatory LGD, Basel LGD or IFRS 9 LGD.
- `ead_origination_proxy` must not be called observed balance at default or regulatory EAD.
- Analytical EL must not be called a regulatory IFRS 9 ECL or Basel capital estimate.
- Historical policy simulation must not be described as realized approval uplift or realized loss savings.
- Observed contractual interest must not be described as realized interest or guaranteed profit.
- C8E/C9 matched-population metrics must not be generalized silently to the full 1,347,681-account core.

## Feature and timing boundary

Post-outcome fields (`recoveries`, `collection_recovery_fee`, `total_rec_prncp`, `total_pymnt`, `last_pymnt_d`, `last_pymnt_amnt`, `out_prncp`, and terminal FICO fields) are evidence-only for retrospective recovery/loss work. They are forbidden in underwriting predictors and projected probability models.

Block B classified `int_rate`, `installment` and `term` as `ECONOMICS_ONLY`. Block C's frozen C8E/C9 contract includes them under an explicit, versioned re-contract. Block D preserves both facts; the exception does not rewrite the Block B registry.

Historical Shadow 2018 is not a clean regulatory holdout. C9 OOT 2017 remains one-time evidence and must not be tuned on.
