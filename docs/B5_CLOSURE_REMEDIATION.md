# B4/B5 Closure Remediation

The prior B5 run at commit `55378b9` remains valid for the locked population counts, bridge reconciliation and authority boundaries. This closure patch strengthens staging lineage, DQ semantics, rejected-field parsing, technical-key reproducibility and role-test coverage without redefining the analytical baseline.

## Remediations applied

1. Restored `title` and `desc` to the reviewed B4 staging contract while keeping both out of the lean B4 mart.
2. Changed B4 `dq_status` to `STRUCTURAL_PASS` and reserved `dq_flag_count` as NULL because no row-level exception framework exists.
3. Corrected RejectStats DTI parsing to trim and remove `%`, storing percentage-point units.
4. Replaced unordered `row_number() over ()` with materialized DuckDB `rowid + 1` for the technical source-row key.
5. Added key range and first/last 100-key checksum evidence.
6. Made B5T08 enforce the exact YAML pricing-role map and exclude target-like supplemental fields.
7. Added B5T13 rejected parse-quality and technical-key validation.
8. Updated B4/B5 documentation, sanitized closure evidence and website status.

## Non-changes

Source authority, `actual_default`, `issue_d`, temporal splits, champion whitelist, bridge key, bridge baseline, pricing population and RejectStats context-only role were not changed. No preprocessing, model score, PD, LGD/EAD, ECL, reject inference or pricing optimization was added.

## Acceptance

The post-hotfix rerun must reproduce every locked count, pass static validation, pass B5T01–B5T13, and publish only aggregate evidence. B4 and B5 are frozen after this closure; the next stage is B6 — Portfolio Overview.
