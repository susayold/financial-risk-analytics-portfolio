# B4 HANDOFF

## Handoff state

`B0–B3 = REVIEWED / PASS`  
`B4 = REVIEWED / PASS`  
`Block B = IN PROGRESS`

## Downstream contract

The canonical input for later work is `mart.mart_credit_application_core`: one row per granted account, exact population reconciliation, `actual_default` as the observed target, `issue_d` as temporal authority and Block A v1.0 feature governance preserved.

## What downstream users may do

- Reproduce account, target and vintage counts.
- Build portfolio KPI tables from the governed account grain.
- Use champion candidates as untransformed inputs to a later governed modeling stage.
- Use `addr_state` and `zip_code` for analysis only.

## What downstream users may not infer

The mart is not a verified 12-month PD dataset, not a production model-ready claim, and not an observed LGD/EAD/ECL dataset. `loan_amnt` is an exposure proxy only.

## Next gate

`B5 — Supplemental / Pricing / Rejected Context Marts`

Required B5 boundaries: `bridge_lc_core_figshare`, `mart_credit_pricing_enriched`, and `mart_rejected_context`. Do not start B6 portfolio-risk analysis before those populations are explicit.
