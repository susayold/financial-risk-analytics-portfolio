# CRD.PI Block D — Artifact Index

Updated: 2026-09-02  
Git commit: `0cc6279`

## Overall state

`D0 PASS` · `D1 REVIEW_REQUIRED` · `D2 REVIEW_REQUIRED_BRIDGE_PENDING` · `D3 PASS_WITH_LIMITATIONS` · `D4 SCENARIO_ONLY_REVIEW_REQUIRED` · `D5–D9 NOT STARTED`

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
| D1 | REVIEW_REQUIRED | Risk-score mart contract and risk-band contract | No full account mart until Development score artifact is materialized |
| D2 | REVIEW_REQUIRED_BRIDGE_PENDING | Full-source audit, loss dictionary, retrospective loss proxy, bridge audit, tests | Source-level retrospective evidence; not C8E empirical LGD |
| D3 | PASS_WITH_LIMITATIONS | EAD contract, account EAD proxy, sensitivity, term view, anomaly audit and tests | 331,865-row pricing-source scope; `loan_amnt` origination proxy only |
| D4 | SCENARIO_ONLY_REVIEW_REQUIRED | LGD scenario contract, Q25/Q50/Q75/Q90 anchors, issue-year diagnostics, tests and run audit | No `p_bad_final` join; no approved C8E LGD or D5 input |
| D5–D9 | NOT STARTED | — | Cannot proceed to frozen expected loss, policy, pricing, stress or closure |

## Current blockers

1. Persisted C8E Development predictions/scores joined to the governed
   Development population.
2. Exact C8E score-to-pricing bridge with the required pricing fields.
3. Governed-core ID bridge and target concordance between the 2,275,739-row
   full source and the 1,347,681-row governed core.

## Storage rule

Raw source files and model binaries are not committed to GitHub. Derived D2–D4
outputs are private Drive evidence and are excluded from the public repository;
only contracts, sanitized manifests and reproducible code are public.
