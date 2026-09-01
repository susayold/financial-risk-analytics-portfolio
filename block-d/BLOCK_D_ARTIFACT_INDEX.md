# CRD.PI Block D — Artifact Index

Updated: 2026-09-02  
Git branch: `main` (latest pushed revision)

## Overall state

`D0 PASS` · `D1 REVIEW_REQUIRED` · `D2 REVIEW_REQUIRED_BRIDGE_PENDING` · `D3 PASS_WITH_LIMITATIONS` · `D4 SCENARIO_ONLY_REVIEW_REQUIRED` · `D5–D9 GATED_HOLD`

Block D is not closed. The current downstream outputs are deliberately bounded
by missing Development scores and the missing governed-core loss bridge.

## Drive locations

- [Block D main folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-)
- [D2 Loss & Recovery Evidence](https://drive.google.com/drive/folders/1c5pGHEDN5x7RgAChIVglTU9FFT2B_cFg)
- [D3 EAD Framework](https://drive.google.com/drive/folders/1Z0raNYjNOxYUUOoUqnTEuM7lMPh4-8oE)
- [D4 LGD Framework](https://drive.google.com/drive/folders/1LCwVt8AtdG8uBRS56FfgbQtAUIeUo4zk)

## Stage index

| Stage | Current result | Key evidence | Claim boundary |
|---|---|---|---|
| D0 | PASS, 10/10 gates | Governance contract, population contract, role matrix, assumptions and run audit | Frozen upstream model and roles only |
| D1 | REVIEW_REQUIRED | Risk-score mart contract, available-score artifact audit, input availability audit and risk-band contract | Persisted Validation/OOT files pass structural checks; no full account mart until Development score artifact and bridges are materialized |
| D2 | REVIEW_REQUIRED_BRIDGE_PENDING | Full-source audit, loss dictionary, retrospective loss proxy, score-to-loss sub-audit, bridge audit, tests | Source-level retrospective evidence; 1,993 exact proxy duplicates require account-grain deduplication; not C8E empirical LGD |
| D3 | PASS_WITH_LIMITATIONS | EAD contract, account EAD proxy, sensitivity, term view, anomaly audit and tests | 331,865-row pricing-source scope; `loan_amnt` origination proxy only |
| D4 | SCENARIO_ONLY_REVIEW_REQUIRED | LGD scenario contract, Q25/Q50/Q75/Q90 anchors, issue-year diagnostics, tests and run audit | No `p_bad_final` join; no approved C8E LGD or D5 input |
| D5 | GATED_HOLD | `D5_EXPECTED_LOSS/D5_EXPECTED_LOSS_GATE.md`, `D5_GATE_RESULTS.json` | No EL number until D1/D2 bridges and approved D4 input pass |
| D6 | GATED_HOLD | `D6_DECISION_POLICY/D6_POLICY_GATE.md`, `D6_GATE_RESULTS.json` | No production policy until D1/D5 and owner thresholds pass |
| D7 | GATED_HOLD | `D7_PRICING/D7_PRICING_GATE.md`, `D7_GATE_RESULTS.json` | No pricing adequacy or profitability claim |
| D8 | GATED_HOLD | `D8_STRESS/D8_STRESS_GATE.md`, `D8_GATE_RESULTS.json` | No stress result until passed D5 baseline exists |
| D9 | GATED_HOLD | `D9_CLOSURE/D9_CLOSURE_GATE.md`, `D9_GATE_RESULTS.json` | Closure remains `NOT_LOCKED` until all upstream gates pass |

## Current blockers

1. Persisted C8E Development predictions/scores joined to the governed
   Development population.
2. Exact C8E score-to-pricing bridge with the required pricing fields.
3. Governed-core ID bridge and target concordance between the 2,275,739-row
   full source and the 1,347,681-row governed core.
4. Owner decision on the approved LGD population and timing boundary.

## Storage rule

Raw source files and model binaries are not committed to GitHub. Derived D2–D4
outputs are private Drive evidence and are excluded from the public repository;
only contracts, sanitized manifests and reproducible code are public.

## D5–D9 gate register

- `D5_D9_DOWNSTREAM_GATE_REGISTER.md`
- `D5_D9_GATE_QA.json`

Run the deterministic downstream control check:

```text
python src/run_block_d_downstream_gate_qa.py
```
