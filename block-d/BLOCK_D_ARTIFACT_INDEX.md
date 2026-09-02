# CRD.PI Block D — Artifact Index

Updated: 2026-09-02  
Git branch: `main` (latest pushed revision)

## Overall state

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 PASS_WITH_LIMITATIONS` · `D3 PASS_WITH_LIMITATIONS` · `D4 BRIDGE_RECONCILED_APPROVAL_PENDING` · `D5–D9 CONTROLLED_HOLD`

Block D is not closed. D1 and D2 evidence bridges are now reconciled; D4 and
D5–D9 remain bounded by scenario approval and owner-controlled policy gates.

- [Plan traceability matrix on Drive](https://drive.google.com/file/d/1I5ldFx0L-YkU_iMG7e4a4Xz89NXgJpyT/view?usp=drivesdk)
- [Full review-scope QA audit on Drive](https://drive.google.com/file/d/13qXEdFccHbhzES8lVoHRD2Fs8GLN17J7/view?usp=drivesdk)
- [Plan completion scorecard](BLOCK_D_PLAN_COMPLETION_SCORECARD.md)
- [Machine-readable plan completion scorecard](BLOCK_D_PLAN_COMPLETION_SCORECARD.json)

## Drive locations

- [Block D main folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-)
- [D2 Loss & Recovery Evidence](https://drive.google.com/drive/folders/1c5pGHEDN5x7RgAChIVglTU9FFT2B_cFg)
- [D3 EAD Framework](https://drive.google.com/drive/folders/1Z0raNYjNOxYUUOoUqnTEuM7lMPh4-8oE)
- [D4 LGD Framework](https://drive.google.com/drive/folders/1LCwVt8AtdG8uBRS56FfgbQtAUIeUo4zk)

## Stage index

| Stage | Current result | Key evidence | Claim boundary |
|---|---|---|---|
| D0 | PASS, 10/10 gates | Governance contract, population contract, role matrix, assumptions and run audit | Frozen upstream model and roles only |
| D1 | PASS_WITH_LIMITATIONS | Frozen C8E Development replay, Validation/OOT score audit, 310,066-row mart, materialized Validation risk-band contract/cutpoints, pricing bridge and 10/10 QA | C8E matched scored subset only; no full-governed score coverage claim |
| D2 | PASS_WITH_LIMITATIONS | Full-source audit, exact governed-core bridge, target/loan amount reconciliation, governed BAD-only evidence and anomaly treatment | Retrospective BAD-only loss evidence; not regulatory LGD and no GOOD-row loss recovery claim |
| D3 | PASS_WITH_LIMITATIONS | EAD contract, `D3_CONTRACT_AUDIT.json`, account EAD proxy, sensitivity, term view, anomaly audit and tests | 331,865-row pricing-source scope; `loan_amnt` origination proxy only |
| D4 | BRIDGE_RECONCILED_APPROVAL_PENDING | Governed BAD-only Q25/Q50/Q75/Q90 anchors, descriptive score-to-loss linkage and 2018 monitor-only diagnostic | Scenario assumptions remain unapproved main-case LGD |
| D5 | CONTROLLED_HOLD | `D5_EXPECTED_LOSS/D5_ANALYTICAL_SCENARIO_AUDIT.json`, `D5_EXPECTED_LOSS/D5_EXPECTED_LOSS_GATE.md`, `D5_EXPECTED_LOSS/D5_GATE_RESULTS.json` | Analytical scenario pack executed; no approved EL claim until D4 main-case approval |
| D6 | CONTROLLED_HOLD | `D6_DECISION_POLICY/D6_ANALYTICAL_PACK_AUDIT.json`, `D6_DECISION_POLICY/D6_POLICY_GATE.md`, `D6_DECISION_POLICY/D6_GATE_RESULTS.json` | Proposed non-production policy only; owner thresholds and overrides remain pending |
| D7 | CONTROLLED_HOLD | `D7_PRICING/D7_DIAGNOSTIC_AUDIT.json`, `D7_PRICING/D7_PRICING_GATE.md`, `D7_PRICING/D7_GATE_RESULTS.json` | Diagnostic pricing context only; no pricing adequacy or profitability claim |
| D8 | CONTROLLED_HOLD | `D8_STRESS/D8_ILLUSTRATIVE_SENSITIVITY_AUDIT.json`, `D8_STRESS/D8_STRESS_GATE.md`, `D8_STRESS/D8_GATE_RESULTS.json` | Illustrative sensitivity pack only; no approved stress result |
| D9 | CONTROLLED_HOLD | `D9_CLOSURE/D9_CLOSURE_REVIEW_MANIFEST.json`, `D9_CLOSURE/D9_APPROVAL_REGISTER.md`, `D9_CLOSURE/D9_APPROVAL_REGISTER.json`, `D9_CLOSURE/D9_APPROVAL_VALIDATION.json`, `D9_CLOSURE/D9_OWNER_DECISION_INTAKE.md`, `D9_CLOSURE/BLOCK_D_APPROVAL_DECISION_PACK.md`, `D9_CLOSURE/D9_CLOSURE_GATE.md`, `D9_CLOSURE/D9_GATE_RESULTS.json` | Closure remains `NOT_LOCKED` until all upstream gates and owner sign-off pass |

## Current blockers

1. D4 main-case LGD/timing approval.
2. D5 analytical expected-loss proxy formula and timing output.
3. Owner decision on D6 action thresholds, D7 pricing assumptions and D8 shocks.

## Storage rule

Raw source files and model binaries are not committed to GitHub. Derived D2–D4
outputs are private Drive evidence and are excluded from the public repository;
only contracts, sanitized manifests and reproducible code are public.

## D5–D9 gate register

- `D5_D9_DOWNSTREAM_GATE_REGISTER.md`
- `D5_D9_GATE_QA.json`
- `BLOCK_D_EXECUTION_TRACKER.md`
- `src/validate_block_d_owner_decisions.py`
- `src/test_block_d_owner_decisions.py`
- `src/validate_block_d_d9_checksums.py`

## Latest private Drive packs

- [D1 full evidence ZIP](https://drive.google.com/file/d/1A2laFU3d9e5UHAegKfIzKaAegLNpBlRy/view?usp=drivesdk)
- [D2 governed bridge ZIP](https://drive.google.com/file/d/1503zJkDmksZwx7AkIEg3-OHdCxk6TYq8/view?usp=drivesdk)
- [D5 scenario pack ZIP](https://drive.google.com/file/d/1i4TjiREQAzutHrEU3iYBK3sOk5woMpDm/view?usp=drivesdk)
- [D6 policy pack ZIP](https://drive.google.com/file/d/1G5OLPz-NAvO1KLUynJc1DEJxnJrdYU2T/view?usp=drivesdk)
- [D7 pricing pack ZIP](https://drive.google.com/file/d/1umRSK8tUFUscH4bLZi8hyhIOKhfqwvPl/view?usp=drivesdk)

Reconciled follow-up evidence:

- [D2 reconciled run audit v2](https://drive.google.com/file/d/1Ztlr5790hp01uCE4pZ5-zd7TQJO-J2J0/view?usp=drivesdk)
- [D2 reconciled test results v2](https://drive.google.com/file/d/1noV377hFURVdJx76CUUzC5UzmCY3WSar/view?usp=drivesdk)
- [D4 reconciled run audit v2](https://drive.google.com/file/d/1OEG0OQELLVxKdXo5-_S9BBcYTCD_pb7j/view?usp=drivesdk)
- [D4 reconciled test results v2](https://drive.google.com/file/d/1cbUkD2vXsgQZf4kOh6nngkBd7iPqZ121/view?usp=drivesdk)
- [D4 descriptive score-to-loss linkage](https://drive.google.com/file/d/1DNksoMZTjHhIrIchGHjyxRO-UMwRTmZ3/view?usp=drivesdk)
- [D4 score-to-loss linkage audit](https://drive.google.com/file/d/1SxLMmVoGjUbyDVx4BXTRbqROhoGzDzFh/view?usp=drivesdk)

Run the deterministic downstream control check:

```text
python src/run_block_d_downstream_gate_qa.py
```
