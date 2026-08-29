# DQ01–DQ07 reviewed results

| Control | Result | Reviewed evidence |
|---|---|---|
| DQ01 Key integrity | PASS | 0 null IDs; 0 duplicates |
| DQ02 Target integrity | PASS | BAD 269,249; GOOD 1,078,432; unknown 0 |
| DQ03 Temporal integrity | PASS | 139 cohorts; 0 unassigned |
| DQ04 Numeric integrity | PASS | NULL-safe checks; invalid values 0 |
| DQ05 Feature governance | PASS | Exact set; no contamination |
| DQ06 Text sparsity | PASS + `REVIEW_ONLY` | `desc` sparse 1,228,580; `title` sparse 16,656 |
| DQ07 Block A reconciliation | PASS | Locked totals match exactly |

## Reconciliation

- Rows: `1,347,681`
- BAD: `269,249`
- GOOD: `1,078,432`
- Observed BAD rate: `19.9786893%`
- Issue range: Jun-2007 to Dec-2018

No capping, imputation, outlier treatment or model preprocessing is fitted in B0–B3.
