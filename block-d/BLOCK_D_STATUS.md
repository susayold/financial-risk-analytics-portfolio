# BLOCK D STATUS

Updated: 2026-09-01

## Current status

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 BLOCKED_PENDING_SOURCE` · `D3 PASS_WITH_LIMITATIONS` · `D4–D9 NOT STARTED`

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

## Not claimed

- No full D1 account mart has been claimed until the Development score artifact is available.
- No LGD, EAD timing, Expected Loss, decision policy, pricing adequacy or stress result has been calculated.
- No regulatory PD/LGD/EAD/ECL or realized profit/loss claim is made.

## Blocking inputs

1. Persisted C8E Development predictions/scores joined to the governed Development population.
2. Validated C8E score-to-pricing bridge containing `term`, `int_rate`, `installment`, `sub_grade` and `grade_derived`.
3. Accepted full-source loss/recovery bridge for D2, with field definitions, timing, coverage, reconciliation and anomaly treatment.

The available private C9 closure package contains the frozen model, C9 OOT predictions and C8E Validation predictions, but does not by itself provide all three inputs above.

## Next valid action

Materialize the missing inputs into the D runtime on Drive/D storage, then rerun:

```text
python src/build_block_d_d1_mart.py --cumulative-c7 <path> --c8e <path> --c9 <path> --output-dir <D-runtime-output>
```

Only after D1 coverage and bridges reconcile should execution proceed to D2/D3 and then the strict D4–D9 sequence.
