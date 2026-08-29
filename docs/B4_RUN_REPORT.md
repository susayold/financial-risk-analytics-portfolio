# B4 RUN REPORT

## 1. Objective

Build `mart.mart_credit_application_core` as the stable one-account analytical mart for later portfolio analysis and Block C modeling, without changing the reviewed B0–B3 population, target, chronology or feature roles.

## 2. Input contract

- Input: `staging.stg_lc_granting_core`
- Governing source: Zenodo record `11295916`
- Grain: one granted loan/account per `account_id`
- Expected rows: `1,347,681`
- Temporal authority: `issue_d`
- Target: `actual_default` (`0 = GOOD`, `1 = BAD`)
- No supplemental Figshare, RejectStats or pricing join

## 3. Mart grain and build

The SQL build is a direct projection with no `WHERE` clause and no joins. It derives year/month/cohort labels, preserves the split and target, carries the approved Block A champion candidates, retains `addr_state`/`zip_code` as analysis-only fields, and adds lineage/governance metadata. No imputation, capping, scaling, encoding, WOE, IV or scorecard operation is applied.

## 4. Build result

`mart_credit_application_core` built successfully at `B4_v1.0` with `1,347,681` rows.

## 5. Reconciliation

| Check | Observed | Result |
|---|---:|---|
| Staging rows | 1,347,681 | PASS |
| Mart rows | 1,347,681 | PASS |
| Distinct `account_id` | 1,347,681 | PASS |
| Duplicate `account_id` | 0 | PASS |
| BAD | 269,249 | PASS |
| GOOD | 1,078,432 | PASS |
| BAD rate | 19.9786893% | PASS |
| Issue cohorts | 139 | PASS |
| Population loss | 0 | PASS |
| Unassigned split | 0 | PASS |

## 6. Temporal reconciliation

| Split | Rows | Date range |
|---|---:|---|
| Development | 829,347 | 2007-06-01 → 2015-12-01 |
| Validation | 293,057 | 2016-01-01 → 2016-12-01 |
| OOT | 169,117 | 2017-01-01 → 2017-12-01 |
| Historical Shadow | 56,160 | 2018-01-01 → 2018-12-01 |

## 7. Regression and boundary tests

| Test | Result |
|---|---|
| B4T01 key integrity | PASS |
| B4T02 population reconciliation | PASS |
| B4T03 target reconciliation | PASS |
| B4T04 temporal reconciliation | PASS |
| B4T05 schema contract | PASS |
| B4T06 feature boundary | PASS |
| B4T07 staging lineage + DQ semantics | PASS |
| B4T08 null profile | PASS (descriptive) |

Forbidden outcome/pricing fields are absent. All eight champion candidates are present. `preprocessing_version = NOT_APPLIED`. The staging layer retains `title` and `desc` for lineage/DQ traceability, while the lean core mart excludes both. Every core row has `dq_status = STRUCTURAL_PASS`; `dq_flag_count` is NULL by design because no row-level exception framework exists.

## 8. Null profile

The aggregate null profile covers the eight champion candidates plus `addr_state` and `zip_code`. It is descriptive only; no values are filled, capped or transformed.

## 9. Gate decision

`B4 = REVIEWED / PASS`.

## 10. Boundary and next step

This result does not claim portfolio findings, a production pipeline, predicted PD, calibration, LGD/EAD, ECL, pricing or decision cutoffs. B5 has now completed its controlled enrichment boundary; the next stage is B6 — Portfolio Overview.
