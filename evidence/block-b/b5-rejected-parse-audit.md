# B5 RejectStats Parse Audit

RejectStats `Debt-To-Income Ratio` is parsed with `trim + remove_percent + decimal_cast` and stored in percentage-point units. The aggregate audit is available in `outputs/b5/rejectstats_dti_parse_audit.json`.

`risk_score` remains a generic field. The project does not assume one credit-score methodology across the full rejected-source period. `rejected_record_id` is a technical source-row key, not a borrower/account/business key.
