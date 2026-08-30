# Block B Closure File Index

## Purpose

This index records what the closure sprint changed and where each reviewable result lives. All listed artifacts are aggregate, metadata or code artifacts; raw CSV and DuckDB runtime files are excluded.

## Closure decisions

| Area | Work completed | Result |
|---|---|---|
| B6 | Direct source exposure/null checks, count identity and claim-contract test | 8/8 PASS |
| B7 | Separate BAD/exposure denominators, AND primary rule, executable Wilson CI | 12/12 PASS |
| B8 | Dimension informativeness profile; quasi-constant exclusion from headline ranking | 9/9 PASS |
| B9 | Annual `purpose`/`home_ownership_n` composition and within-year reconciliation | 9/9 PASS |
| Final | Cross-gate, baseline, privacy, claim and website QA | 15/15 PASS |

## Review and evidence files

- `docs/BLOCK_B_FINAL_CLOSURE_REMEDIATION.md` — change-control scope, pre-closure commit and closure result.
- `docs/BLOCK_B_ANALYTICAL_FINDINGS.md` — corrected aggregate findings and denominator wording.
- `docs/BLOCK_B_ASSUMPTIONS_AND_LIMITS.md` — metric, temporal and claim boundaries.
- `docs/BLOCK_B_FINAL_LOCK.md` — final gate status and Block C handoff.
- `evidence/block-b/block-b-final-qa.md` — human-readable 15-test final QA evidence.
- `outputs/block_b_final/block_b_final_qa.json` — machine-readable final QA.
- `outputs/block_b_final/block_b_final_qa.csv` — one row per final QA test.
- `outputs/block_b_final/block_b_final_reconciliation.json` — baseline and gate reconciliation.

## Stage outputs

- B6: `outputs/b6/portfolio_kpis.json`, `numeric_profile.csv`, `portfolio_mix.csv`, `b6_test_results.json`.
- B7: `outputs/b7/segment_risk.csv`, `b7_band_definitions.json`, `b7_run_manifest.json`, `b7_test_results.json`.
- B8: `outputs/b8/risk_concentration.csv`, `b8_dimension_profile.csv`, `b8_summary.json`, `b8_run_manifest.json`, `b8_test_results.json`.
- B9: `outputs/b9/vintage_monthly.csv`, `vintage_annual.csv`, `vintage_split.csv`, `vintage_composition_annual.csv`, `b9_summary.json`, `b9_run_manifest.json`, `b9_test_results.json`.

## Reproducibility code

- `src/run_b6_tests.py`, `src/run_b7_tests.py`, `src/run_b8_tests.py`, `src/run_b9_tests.py` — stage gates.
- `src/validate_block_b_claims.py` — static public claim-contract validator.
- `src/run_block_b_final_qa.py` — final 15-test closure gate.
- `sql/analytics/10_b7_segment_risk.sql`, `11_b8_risk_concentration.sql`, `12_b9_vintage_temporal.sql` — executable analytical SQL.

## Storage boundary

The runtime source CSV and DuckDB database were used only temporarily on D and cleared after QA. They are not committed to GitHub or uploaded to Drive. The public package contains no row-level data.
