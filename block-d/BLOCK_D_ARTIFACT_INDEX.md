# Block D Artifact Index

Current status: `CLOSED_WITH_LIMITATIONS_PORTFOLIO`.

| Area | Public artifacts | Boundary |
|---|---|---|
| D4 LGD | `D4_LGD_FRAMEWORK/D4_EMPIRICAL_LGD_*`; `D4_MAIN_CASE_DECISION.json`; `D4_TIMING_DECISION.json` | Analytical LGD only; Q50 main case |
| D5 EL | `D5_EXPECTED_LOSS/D5_*.csv`; `D5_*_RECONCILIATION.json` | Analytical expected-loss proxy only |
| D6 Policy | `D6_DECISION_POLICY/D6_*.csv`; `D6_*DECISION*.json` | Historical decision simulation only |
| D7 Pricing | `D7_PRICING/D7_*` | Descriptive-only diagnostics |
| D8 Stress | `D8_STRESS/D8_*` | Analytical sensitivity and reverse-stress breakpoint |
| D9 Closure | `D9_CLOSURE/D9_FINAL_*`; governance register; closure report | Portfolio project review; no institutional approval |

Raw LendingClub CSV, DuckDB databases, private model binaries, and row-level private marts are excluded from GitHub. The private account EL mart is retained only on the execution disk/approved private storage.
