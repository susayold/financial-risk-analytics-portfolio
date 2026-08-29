# B5 Bridge Report

## Sources and join

- Core authority: `ZENODO_11295916`, B4 object `B4_v1.0`.
- Supplemental source: Figshare article `22121477`, DOI `10.6084/m9.figshare.22121477.v4`.
- Join key: exact string equality on `account_id`.
- Grain: exactly one bridge row per account_id; FULL OUTER join makes all population statuses auditable.

## Reconciliation

| match_status | rows |
|---|---:|
| MATCHED | 325,255 |
| FIGSHARE_ONLY | 6,610 |
| CORE_ONLY | 1,022,426 |
| Full bridge | 1,354,291 |

Match rate is `325,255 / 331,865 = 98.00822624%`. Core enrichment coverage is `325,255 / 1,347,681 = 24.13442053%`.

## Field concordance

| Field | Equal | Conflicts | Null comparisons | Concordance |
|---|---:|---:|---:|---:|
| issue_d | 325,255 | 0 | 0 | 100.00% |
| loan_amnt | 325,255 | 0 | 0 | 100.00% |
| purpose | 325,255 | 0 | 0 | 100.00% |
| addr_state | 325,255 | 0 | 0 | 100.00% |
| FICO midpoint | 325,255 | 0 | 0 | 100.00% |
| home ownership | 324,391 | 75 | 789 | 99.9769% |
| revenue / annual_inc | 318,681 | 6,574 | 0 | 97.9788% |
| DTI | 323,701 | 1,554 | 0 | 99.5222% |

Null comparisons are excluded from the concordance denominator. Conflicts are retained and the Zenodo/B4 core wins; supplemental values remain explicit and separate.

