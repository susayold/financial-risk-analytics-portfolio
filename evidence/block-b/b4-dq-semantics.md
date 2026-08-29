# B4 DQ Semantics

The B4 mart reports `dq_status = STRUCTURAL_PASS` for the reviewed aggregate/structural source-control state. `dq_flag_count` is NULL for every row by design because no account-level exception framework exists; NULL means not evaluated at account level, not measured zero.

The reviewed staging layer retains `title` and `desc` for lineage and DQ traceability. The lean B4 analytical mart intentionally excludes both sparse review-only fields.
