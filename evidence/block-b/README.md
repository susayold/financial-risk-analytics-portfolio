# Block B — B0–B4 reviewed evidence index

## Status

`B0–B3 = REVIEWED / PASS`  
`B4 = REVIEWED / PASS`
`Block B overall = IN PROGRESS`  
`Next gate = B5 — supplemental / pricing / rejected-context marts`

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

## Claim boundary

`actual_default` is the observed final-resolution default outcome in the resolved granted-loan population. It is not presented as a verified 12-month Probability of Default. B0–B3 does not prove portfolio-risk findings, model performance, PD calibration, LGD/EAD, ECL, pricing/cutoff policy or production readiness.

## Artifacts

- [Run manifest](run-manifest.md)
- [Contract validation](contract-validation.md)
- [DQ results](dq-results.md)
- [Reviewed run report](reviewed-run-report.md)
- [Remediation summary](remediation-summary.md)
- [Cleanup verification](cleanup-verification.md)
- [Zenodo source record](https://doi.org/10.5281/zenodo.11295916)
