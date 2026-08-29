# B4 DATA DICTIONARY

**Object:** `mart.mart_credit_application_core`  
**Grain:** one granted-loan account per `account_id`  
**Version:** `B4_v1.0`

| Field | Type | Business meaning | Source | Role | Model eligible? | Transformation | Notes |
|---|---|---|---|---|---|---|---|
| `account_id` | VARCHAR | Granted-loan identifier | staging | key | No | Cast to VARCHAR | No arithmetic |
| `issue_d` | DATE | Origination cohort authority | staging | temporal | No | Parsed source month to first day | Sole temporal authority |
| `issue_year` | INTEGER | Origination year | issue_d | derived temporal | No | Extract year | Trend/vintage use |
| `issue_month` | DATE | Origination month | issue_d | derived temporal | No | Truncate to month | Trend/vintage use |
| `issue_cohort` | VARCHAR | `YYYY-MM` origination cohort | issue_d | derived temporal | No | `STRFTIME` | 139 cohorts |
| `split_name` | VARCHAR | Development/Validation/OOT/Historical Shadow | staging | split | No | Preserved from staging | No new split logic in mart |
| `actual_default` | INTEGER | Final-resolution observed outcome | staging | target | No | Preserved exactly | 0 GOOD, 1 BAD |
| `target_label` | VARCHAR | Human-readable target label | actual_default | presentation | No | CASE to GOOD/BAD | `actual_default` remains analytical target |
| `revenue` | DOUBLE | Applicant income/revenue | staging | champion candidate | Yes | None | No imputation/capping |
| `dti_n` | DOUBLE | Normalized debt-to-income measure | staging | champion candidate | Yes | None | No model preprocessing |
| `loan_amnt` | BIGINT | Granted loan amount | staging | champion candidate / exposure proxy | Yes | None | Not observed EAD |
| `fico_n` | DOUBLE | Normalized FICO measure | staging | champion candidate | Yes | None | No scaling |
| `experience_c` | BIGINT | Experience category/measure | staging | champion candidate | Yes | None | No encoding |
| `emp_length` | VARCHAR | Employment-length field | staging | champion candidate | Yes | None | No rare grouping |
| `purpose` | VARCHAR | Loan purpose | staging | champion candidate | Yes | None | No target encoding |
| `home_ownership_n` | VARCHAR | Home-ownership field | staging | champion candidate | Yes | None | No imputation |
| `addr_state` | VARCHAR | Applicant state | staging | analysis-only | No | None | Model excluded |
| `zip_code` | VARCHAR | Applicant ZIP context | staging | analysis-only | No | None | Model excluded |
| `dq_status` | VARCHAR | Reviewed structural/source control status | B4 build | governance | No | Constant `STRUCTURAL_PASS` | Aggregate/structural state, not account-level exception status |
| `dq_flag_count` | INTEGER | Reserved account-level DQ flag count | B4 build | governance | No | `NULL` by design | No row-level exception framework exists yet |
| `source_population` | VARCHAR | Governing population identifier | B4 build | lineage | No | Constant | `ZENODO_GRANTED_RESOLVED` |
| `source_version` | VARCHAR | Governing source version | B4 build | lineage | No | Constant | `ZENODO_11295916` |
| `feature_contract_version` | VARCHAR | Approved feature contract | B4 build | governance | No | Constant | `BLOCK_A_v1.0` |
| `preprocessing_version` | VARCHAR | Preprocessing state | B4 build | governance | No | Constant | `NOT_APPLIED` |
| `mart_version` | VARCHAR | Mart release identifier | B4 build | governance | No | Constant | `B4_v1.0` |
| `mart_build_ts` | TIMESTAMP | Build timestamp | B4 build | audit metadata | No | `CURRENT_TIMESTAMP` | Execution trace |

## Explicit exclusions

`title` and `desc` remain in staging but are intentionally omitted from the core mart because they are sparse, review-only and not needed for current portfolio KPIs. Pricing/supplemental fields, outcome-leakage fields and rejected-application fields are also absent by contract.

## Staging lineage note

The reviewed staging layer retains `title` and `desc` for lineage and DQ traceability. The lean B4 analytical core intentionally excludes both fields. B0–B3 established aggregate and structural Data Quality controls; B4 does not claim an account-level exception framework, so `dq_flag_count` is `NULL` by design.
