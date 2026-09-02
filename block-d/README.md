# CRD.PI — Block D

## Decision & Risk Economics

Block D converts the frozen Block C signal into a governed economics and decision-analytics layer.

Execution is strictly sequenced:

`D0 → D1 → D2 → D3 → D4 → D5 → D6 → D7 → D8 → D9`

Current state: **D0 PASS / D1 PASS_WITH_LIMITATIONS / D2 PASS_WITH_LIMITATIONS / D3 PASS_WITH_LIMITATIONS / D4 BRIDGE_RECONCILED_APPROVAL_PENDING / D5–D9 CONTROLLED_HOLD**.

The D0 contract freezes:

- Block A `LOCKED`, Block B `LOCKED`, Block C `CLOSED WITH MONITORING`.
- Frozen model `C8E_RICH_BUREAU_CATBOOST_79F`.
- Primary score name `p_bad_final`.
- Target boundary: `actual_default` is an observed final-resolution BAD/GOOD outcome, not a verified 12-month PD.
- Population lanes: full governed core versus C8E matched enriched population.
- Expected-loss boundary: analytical proxy only, never regulatory IFRS 9/Basel.
- Post-outcome recovery fields as evidence-only; never underwriting predictors.

Raw CSV, DuckDB, model binaries and private source data are intentionally excluded from the public repository.

## Current review checkpoint

- Execution coverage: **100% (10/10 planned stages)**.
- Full-review technical QA: **55/55 PASS**.
- D9 manifest integrity: **16/16 checksums PASS**.
- Closure readiness: **73.5%** under the documented management conversion.
- Final state: **`NOT_LOCKED_REVIEW_REQUIRED`**; owner approvals are not inferred.

Review files:

- `BLOCK_D_PLAN_TRACEABILITY.md` — requirement-to-evidence matrix.
- `BLOCK_D_PLAN_COMPLETION_SCORECARD.md` — stage score and remaining conditions.
- `BLOCK_D_VALIDATION_REPORT.md` — methodology, calculation spot-checks and claim boundary.
- `BLOCK_D_FULL_REVIEW_QA.json` — deterministic full-review QA output.
- `D9_CLOSURE/D9_APPROVAL_REGISTER.json` — structured owner decision intake.
- `D9_CLOSURE/D9_DECISION_GAP_REGISTER.md` — nine open inputs and acceptance criteria.
- `D9_CLOSURE/D9_CLOSURE_REVIEW_MANIFEST.json` — closure evidence and checksums.

The D5–D9 downstream gate register is present. Controlled analytical packs are
materialized for review, but all five production gates remain held because D4
main-case approval and owner policy decisions are not available. No production
claim is made.

## D0 artifacts

- `D0_GOVERNANCE_CONTRACT/D0_UPSTREAM_SNAPSHOT.json`
- `D0_GOVERNANCE_CONTRACT/D0_DATA_ROLE_MATRIX.csv`
- `D0_GOVERNANCE_CONTRACT/D0_ASSUMPTION_REGISTER.csv`
- `D0_GOVERNANCE_CONTRACT/D0_POPULATION_CONTRACT.json`
- `D0_GOVERNANCE_CONTRACT/D0_CLAIM_BOUNDARY.md`
- `D0_GOVERNANCE_CONTRACT/D0_TEST_RESULTS.json`
- `D0_GOVERNANCE_CONTRACT/D0_RUN_AUDIT.json`

## D3 contract audit

- `D3_EAD_FRAMEWORK/D3_EAD_CONTRACT.md`
- `D3_EAD_FRAMEWORK/D3_CONTRACT_AUDIT.json`

Run the deterministic public D3 contract check from the repository root:

```text
python src/audit_block_d_d3_contract.py
```

Run the deterministic D0 check from the repository root:

```text
python src/run_block_d_d0_qa.py
```
