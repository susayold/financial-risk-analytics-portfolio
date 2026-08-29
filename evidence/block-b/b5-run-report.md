# B5 Run Report

The run validated B4 pre-flight, ingested verified Figshare train/test files and public RejectStats, built staging, bridge and marts, then re-ran the B4 regression. The build fails closed before pricing construction if bridge counts or concordance do not match the locked baseline.

`B5 = PASS` — 12/12 gates passed: source counts and key uniqueness, exact bridge counts, bridge grain, concordance, core authority, pricing mart grain, pricing feature boundary, rejected schema, rejected outcome boundary, B4 non-mutation and lineage metadata.

Execution-only raw inputs are referenced by source/version metadata. No raw Figshare, RejectStats, DuckDB database, row-level bridge or row-level mart is committed or published.

