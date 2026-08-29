# B5 Run Report

The run validated B4 pre-flight, ingested verified Figshare train/test files and public RejectStats, built staging, bridge and marts, then re-ran the B4 regression. The build fails closed before pricing construction if bridge counts or concordance do not match the locked baseline.

`B5 = FINAL REVIEWED / PASS` — 13/13 gates passed: source counts and key uniqueness, exact bridge counts, bridge grain, concordance, core authority, pricing mart grain, executable pricing role contract, rejected schema, rejected outcome boundary, B4 non-mutation, lineage metadata and rejected parse quality.

RejectStats `Debt-To-Income Ratio` is parsed by trimming and removing `%`, then casting to decimal percentage-point units. `risk_score` is retained under a generic name; no universal FICO interpretation is claimed. `rejected_record_id` is a technical source-row key based on the materialized source row position.

Execution-only raw inputs are referenced by source/version metadata. No raw Figshare, RejectStats, DuckDB database, row-level bridge or row-level mart is committed or published.

