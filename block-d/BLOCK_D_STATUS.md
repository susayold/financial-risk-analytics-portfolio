# BLOCK D STATUS

Updated: 2026-09-02

## Current status

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 REVIEW_REQUIRED_BRIDGE_PENDING` · `D3 PASS_WITH_LIMITATIONS` · `D4 SCENARIO_ONLY_REVIEW_REQUIRED` · `D5–D9 NOT STARTED`

Block D is not complete. The governance foundation is implemented and reviewed, but the downstream economics stages must not be fabricated from summary metrics.

## Completed

### D0 — Economics Governance Contract

- Upstream status frozen: A `LOCKED`, B `LOCKED`, C `CLOSED_WITH_MONITORING`.
- Frozen model frozen as `C8E_RICH_BUREAU_CATBOOST_79F`, 79 features.
- `p_bad_final` and `actual_default` semantics preserved.
- Full-core and matched-enriched lanes separated.
- `loan_amnt` registered as `ead_origination_proxy`.
- LGD, pricing cost and stress assumptions explicitly left pending evidence.
- Block B → C pricing-variable re-contract retained as an auditable exception.
- Post-outcome fields marked evidence-only and forbidden as underwriting predictors.
- QA: **10/10 gates PASS**.

### D1 — Frozen Risk Score & Decision Mart

- Contract, risk bands, deterministic build script and QA schema created.
- Source packages inspected without retraining C8E or tuning OOT.
- D1 build is ready for C8E Validation + C9 OOT persisted score outputs.
- The currently available score evidence covers 83,664 Validation and 44,221 OOT rows.
- Development score output and pricing fields are not present in the materialized input available to the runtime.

### D3 — EAD Framework

- Contractual amortization scenarios executed on the 331,865-row accepted/pricing source.
- 331,761 rows have valid non-increasing schedules.
- 104 schedule anomalies are retained as `EXCLUDED_DATA_ERROR`; their timing scenarios are not used.
- Origination EAD proxy reconciles exactly to `loan_amnt`.
- QA: **8/8 gates PASS** within the declared P2 scope.

### D2 — Loss & Recovery Evidence

- The full accepted LendingClub source was audited in streaming mode: **2,275,739 source rows**.
- Resolved final outcomes: **1,356,914 rows** = **271,353 BAD** and **1,085,561 GOOD**.
- Required retrospective recovery fields are present and their timing/role is documented.
- Loss-quality treatment is explicit: **1,355,773 VALID** and **1,141 CLIPPED_FOR_MODELING**; no silent clipping is permitted.
- The exact bridge to the governed **1,347,681-row core** is still pending because the governed-core ID list is not materialized in the D runtime.
- QA: **7 PASS / 2 FAIL / 1 PENDING**; status remains **REVIEW_REQUIRED_BRIDGE_PENDING**.

### D4 — LGD Scenario Evidence

- Source-level Q25/Q50/Q75/Q90 LGD anchors were generated from **262,479** resolved BAD rows with issue year through 2017.
- The 2018 shadow cohort (**8,874** rows) is retained as monitor-only and excluded from primary anchors because of documented final-resolution/truncation concerns.
- No `p_bad_final` or C8E score is used; this is not an empirical C8E LGD model.
- QA: **7 PASS / 0 FAIL / 2 PENDING**; status remains **SCENARIO_ONLY_REVIEW_REQUIRED** until D1/D2 bridges pass.

## Not claimed

- No full D1 account mart has been claimed until the Development score artifact is available.
- No LGD, EAD timing, Expected Loss, decision policy, pricing adequacy or stress result has been calculated.
- D4 scenario anchors are not approved main-case LGD inputs and must not be combined with `p_bad_final`.
- No regulatory PD/LGD/EAD/ECL or realized profit/loss claim is made.

## Blocking inputs

1. Persisted C8E Development predictions/scores joined to the governed Development population.
2. Validated C8E score-to-pricing bridge containing `term`, `int_rate`, `installment`, `sub_grade` and `grade_derived`.
3. Accepted full-source loss/recovery bridge for D2, with field definitions, timing, coverage, reconciliation and anomaly treatment. The source-level audit is complete; governed-core ID reconciliation remains pending.

The available private C9 closure package contains the frozen model, C9 OOT predictions and C8E Validation predictions, but does not by itself provide all three inputs above.

## Next valid action

Materialize the missing inputs into the D runtime on Drive/D storage, then rerun:

```text
python src/build_block_d_d1_mart.py --cumulative-c7 <path> --c8e <path> --c9 <path> --output-dir <D-runtime-output>
```

Only after D1 coverage and the governed-core D2 bridge reconcile should empirical D4 LGD work proceed. The current D4 output is scenario-only under the explicit fallback boundary in `D4_LGD_SCENARIO_CONTRACT.md`.
