# CRD.PI — Block D

## Decision & Risk Economics

Block D converts the frozen Block C signal into a governed economics and decision-analytics layer.

Execution is strictly sequenced:

`D0 → D1 → D2 → D3 → D4 → D5 → D6 → D7 → D8 → D9`

Current state: **D0 PASS / D1 REVIEW_REQUIRED / D2 REVIEW_REQUIRED_BRIDGE_PENDING / D3 PASS_WITH_LIMITATIONS / D4 SCENARIO_ONLY_REVIEW_REQUIRED / D5–D9 GATED_HOLD**.

The D0 contract freezes:

- Block A `LOCKED`, Block B `LOCKED`, Block C `CLOSED WITH MONITORING`.
- Frozen model `C8E_RICH_BUREAU_CATBOOST_79F`.
- Primary score name `p_bad_final`.
- Target boundary: `actual_default` is an observed final-resolution BAD/GOOD outcome, not a verified 12-month PD.
- Population lanes: full governed core versus C8E matched enriched population.
- Expected-loss boundary: analytical proxy only, never regulatory IFRS 9/Basel.
- Post-outcome recovery fields as evidence-only; never underwriting predictors.

Raw CSV, DuckDB, model binaries and private source data are intentionally excluded from the public repository.

The D5–D9 downstream gate register is present, but all five stages remain
controlled holds because the D1/D2 bridges and approved D4 LGD input are not
available. No downstream numeric or production claim is made.

## D0 artifacts

- `D0_GOVERNANCE_CONTRACT/D0_UPSTREAM_SNAPSHOT.json`
- `D0_GOVERNANCE_CONTRACT/D0_DATA_ROLE_MATRIX.csv`
- `D0_GOVERNANCE_CONTRACT/D0_ASSUMPTION_REGISTER.csv`
- `D0_GOVERNANCE_CONTRACT/D0_POPULATION_CONTRACT.json`
- `D0_GOVERNANCE_CONTRACT/D0_CLAIM_BOUNDARY.md`
- `D0_GOVERNANCE_CONTRACT/D0_TEST_RESULTS.json`
- `D0_GOVERNANCE_CONTRACT/D0_RUN_AUDIT.json`

Run the deterministic D0 check from the repository root:

```text
python src/run_block_d_d0_qa.py
```
