# Reviewed run report

The B0–B3 reviewed run converted Block A governance into a reproducible DuckDB + SQL + Python execution path:

`Zenodo → verified CSV → DuckDB runtime → canonical staging → DQ engine → sanitized evidence → cleanup`

Zenodo remains the governing source. Drive retains the operational archive pointer and provenance evidence. Because the Drive archive required an authenticated download session, the verified inner CSV was obtained directly from the public Zenodo record for this reviewed run.

The run reproduced the locked population, target and chronological split totals without changing their meaning. The reviewed staging key is currently physically represented as `BIGINT`; Block A specifies the key role and `cast_string` transformation but does not prescribe a DBMS-specific type. Aligning the physical representation to `VARCHAR` before supplemental joins is the next controlled consistency improvement.

The result is a controlled data foundation ready for B4, not a complete portfolio-risk or credit-model deliverable.
