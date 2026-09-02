# CRD.PI Block D — Artifact Index

Updated: 2026-09-02  
Git branch: `main` (latest pushed revision)

## Overall state

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 PASS_WITH_LIMITATIONS` · `D3 PASS_WITH_LIMITATIONS` · `D4 BRIDGE_RECONCILED_APPROVAL_PENDING` · `D5–D9 CONTROLLED_HOLD`

Block D is not closed. D1 and D2 evidence bridges are now reconciled; D4 and
D5–D9 remain bounded by scenario approval and owner-controlled policy gates.

## Drive locations

- [Block D main folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-)
- [D2 Loss & Recovery Evidence](https://drive.google.com/drive/folders/1c5pGHEDN5x7RgAChIVglTU9FFT2B_cFg)
- [D3 EAD Framework](https://drive.google.com/drive/folders/1Z0raNYjNOxYUUOoUqnTEuM7lMPh4-8oE)
- [D4 LGD Framework](https://drive.google.com/drive/folders/1LCwVt8AtdG8uBRS56FfgbQtAUIeUo4zk)

## Stage index

| Stage | Current result | Key evidence | Claim boundary |
|---|---|---|---|
| D0 | PASS, 10/10 gates | Governance contract, population contract, role matrix, assumptions and run audit | Frozen upstream model and roles only |
| D1 | PASS_WITH_LIMITATIONS | Frozen C8E Development replay, Validation/OOT score audit, 310,066-row mart, pricing bridge and 10/10 QA | C8E matched scored subset only; no full-governed score coverage claim |
| D2 | PASS_WITH_LIMITATIONS | Full-source audit, exact governed-core bridge, target/loan amount reconciliation, governed BAD-only evidence and anomaly treatment | Retrospective BAD-only loss evidence; not regulatory LGD and no GOOD-row loss recovery claim |
| D3 | PASS_WITH_LIMITATIONS | EAD contract, account EAD proxy, sensitivity, term view, anomaly audit and tests | 331,865-row pricing-source scope; `loan_amnt` origination proxy only |
| D4 | BRIDGE_RECONCILED_APPROVAL_PENDING | Governed BAD-only Q25/Q50/Q75/Q90 anchors and 2018 monitor-only diagnostic | Scenario assumptions remain unapproved main-case LGD |
| D5 | GATED_HOLD | `D5_EXPECTED_LOSS/D5_EXPECTED_LOSS_GATE.md`, `D5_GATE_RESULTS.json` | No EL number until D1/D2 bridges and approved D4 input pass |
| D6 | GATED_HOLD | `D6_DECISION_POLICY/D6_POLICY_GATE.md`, `D6_GATE_RESULTS.json` | No production policy until D1/D5 and owner thresholds pass |
| D7 | GATED_HOLD | `D7_PRICING/D7_PRICING_GATE.md`, `D7_GATE_RESULTS.json` | No pricing adequacy or profitability claim |
| D8 | GATED_HOLD | `D8_STRESS/D8_STRESS_GATE.md`, `D8_GATE_RESULTS.json` | No stress result until passed D5 baseline exists |
| D9 | GATED_HOLD | `D9_CLOSURE/D9_CLOSURE_GATE.md`, `D9_GATE_RESULTS.json` | Closure remains `NOT_LOCKED` until all upstream gates pass |

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

## Latest private Drive packs

- [D1 full evidence ZIP](https://drive.google.com/file/d/1A2laFU3d9e5UHAegKfIzKaAegLNpBlRy/view?usp=drivesdk)
- [D2 governed bridge ZIP](https://drive.google.com/file/d/1503zJkDmksZwx7AkIEg3-OHdCxk6TYq8/view?usp=drivesdk)
- [D5 scenario pack ZIP](https://drive.google.com/file/d/1i4TjiREQAzutHrEU3iYBK3sOk5woMpDm/view?usp=drivesdk)
- [D6 policy pack ZIP](https://drive.google.com/file/d/1G5OLPz-NAvO1KLUynJc1DEJxnJrdYU2T/view?usp=drivesdk)
- [D7 pricing pack ZIP](https://drive.google.com/file/d/1umRSK8tUFUscH4bLZi8hyhIOKhfqwvPl/view?usp=drivesdk)

Run the deterministic downstream control check:

```text
python src/run_block_d_downstream_gate_qa.py
```
