# Block B — B0–B9 reviewed and locked evidence index

## Status

`B0–B3 = REVIEWED / PASS`  
`B4 = REVIEWED / PASS`
`B5 = FINAL REVIEWED / PASS`
`B6–B9 = FINAL REVIEWED / PASS`
`Block B overall = FINAL REVIEWED / LOCKED`
`Next gate = Block C — Credit Risk Modeling`

This public evidence index contains sanitized aggregate and audit metadata only. It does not publish the raw LendingClub CSV, row-level Parquet, DuckDB database or private local paths.

## What the reviewed run proves

- Zenodo record 11295916 is the governing source authority.
- The reviewed inner CSV contains 1,347,681 rows and 15 source columns.
- `staging.stg_lc_granting_core` preserves one granted-loan/account grain.
- `issue_d` is the sole temporal authority.
- DQ01–DQ07 pass under `B0_B3_TEST_SUITE_v2`.
- The exact eight-feature Block A champion whitelist is enforced programmatically.
- Runtime source/CSV/database/row-level outputs were removed after evidence export; secure deletion is not claimed.

## B4 core mart

- `mart.mart_credit_application_core` is a reproducible one-account analytical mart with 1,347,681 rows.
- Population, key, target, temporal, schema, feature-boundary and descriptive null-profile tests pass 7/7.
- Public B4 evidence is available in [b4-status](b4-status.md), [b4-reconciliation](b4-reconciliation.md), [b4-mart-schema](b4-mart-schema.md) and [b4-run-report](b4-run-report.md).
- The B4 mart is not a model, a verified 12-month PD dataset, a pricing table or a production underwriting decision artifact.

## B5 controlled enrichment

- Figshare train/test source contract passes: 236,846 / 95,019 rows; 331,865 combined; zero train/test ID overlap.
- The exact bridge contains 325,255 MATCHED, 6,610 FIGSHARE_ONLY and 1,022,426 CORE_ONLY rows; no duplicate account_id.
- `mart_credit_pricing_enriched` contains 325,255 matched accounts and preserves Zenodo/B4 authority with 0 governed-field mismatches or target overwrites.
- Concordance reproduces the locked baseline: 100% for issue_d, loan_amnt, purpose, addr_state and FICO; 99.9769% home ownership; 97.9788% revenue; 99.5222% DTI.
- `mart_rejected_context` contains 27,648,741 deterministic-keyed context records with no observed outcome, GOOD/BAD label, PD, loss or champion merge eligibility.
- Independent B5 suite passes 12/12. B5 does not perform reject inference, causal approval analysis, model fitting or PD/LGD/EAD/ECL estimation.

## B6–B9 portfolio-risk analysis

- B6 covers 1,347,681 core accounts, 269,249 BAD, 1,078,432 GOOD, 19.9787% observed final-resolution BAD rate and $19.42B `loan_amnt` exposure proxy.
- B7 covers fixed FICO/DTI bands, persisted revenue/loan quantile cuts and categorical dimensions; each dimension reconciles to the full core.
- B8 uses the predefined rule `relative_bad_rate > 1.0 AND account_share >= 0.1%`; it reports 44 material single-variable segments with deterministic ranking.
- B9 uses `issue_d` and reconciles 139 monthly cohorts, annual cohorts and the four temporal splits. The 2018 historical shadow is right-truncated/resolution-selected and is not live monitoring.
- B6–B9 are descriptive findings only. They do not claim PD, model performance, expected loss, causal drivers, reject inference or production policy.

## Claim boundary

`actual_default` is the observed final-resolution default outcome in the resolved granted-loan population. It is not presented as a verified 12-month Probability of Default. B5 does not prove full-portfolio pricing conclusions, rejected-loan default performance, reject inference, causal approval effects, model performance, PD calibration, LGD/EAD, ECL, pricing/cutoff policy or production readiness.

## Artifacts

- [Run manifest](run-manifest.md)
- [Contract validation](contract-validation.md)
- [DQ results](dq-results.md)
- [Reviewed run report](reviewed-run-report.md)
- [Remediation summary](remediation-summary.md)
- [Cleanup verification](cleanup-verification.md)
- [B5 status](b5-status.md)
- [B5 bridge summary](b5-bridge-summary.md)
- [B5 field concordance](b5-field-concordance.md)
- [B5 pricing mart schema](b5-pricing-mart-schema.md)
- [B5 rejected-context boundary](b5-rejected-context-boundary.md)
- [B5 run report](b5-run-report.md)
- [B6 portfolio overview](b6-portfolio-overview.md)
- [B7 segment risk](b7-segment-risk.md)
- [B8 risk concentration](b8-risk-concentration.md)
- [B9 vintage analysis](b9-vintage-analysis.md)
- [Block B final lock](block-b-final-lock.md)
- [Zenodo source record](https://doi.org/10.5281/zenodo.11295916)
