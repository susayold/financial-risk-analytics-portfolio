# CRD.PI — Block D

## Decision & Risk Economics

Block D is `CLOSED_WITH_LIMITATIONS_PORTFOLIO` for the CRD.PI analytical scope, with closure substatus `PENDING_OWNER_GATE`. The D0–D8 analytical chain is complete; the canonical D9 release remains pending the explicit portfolio project-owner identifier and decision date.

| Stage | Final state | Scope boundary |
|---|---|---|
| D0 | PASS | Governance and claim contract |
| D1 | CLOSED | C8E matched scored population |
| D2 | CLOSED | Retrospective BAD loss evidence |
| D3 | CLOSED | Contractual EAD timing proxy |
| D4 | CLOSED | Q50 analytical LGD; challenger rejected by predeclared materiality rule |
| D5 | CLOSED | Analytical expected-loss proxy |
| D6 | CLOSED | Historical decision simulation |
| D7 | CLOSED | Descriptive-only pricing scope |
| D8 | CLOSED | Analytical stress sensitivity and reverse stress |
| D9 | CLOSED | Portfolio project governance |

Execution coverage, portfolio requirement resolution, technical QA, and artifact checksum integrity are each 100%. Production authorization and regulatory compliance are not in scope.

The post-closure micro-remediation checkpoint is `7/8` semantic checks: CatBoost coverage, exposure-weighted D5 segment rates, D8-FINAL-1.1 stress/timing separation, fold semantics, and superseded-evidence labels pass. R8-G06 remains pending only because the portfolio project-owner identifier and decision date must be supplied explicitly by the project owner. No final release tag is created before that gate passes.

## Final links

- `D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json` — final decision and limitations.
- `BLOCK_D_FINAL_SCORECARD.md` / `.json` — separate completion and readiness axes.
- `D9_CLOSURE/BLOCK_D_FINAL_CLOSURE_REPORT.md` — durable methodology and handoff.
- `BLOCK_D_FULL_REVIEW_QA.json` — final deterministic QA.
- `D9_CLOSURE/D9_FINAL_CLOSURE_MANIFEST.json` — final checksums.

Raw CSV, DuckDB, private model binaries, and row-level private marts remain outside GitHub.
