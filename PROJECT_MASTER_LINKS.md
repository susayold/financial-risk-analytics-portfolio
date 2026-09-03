# CRD.PI Block A–F Project Links

Updated: 2026-09-03

| Block / scope | Data or project | Google Drive | GitHub |
|---|---|---|---|
| A–F umbrella | CRD.PI project root | [Drive root folder](https://drive.google.com/drive/folders/1Y9X6hEcoa7PVpg-o827vY3w0lUQIWYM0) | [Portfolio repository](https://github.com/susayold/financial-risk-analytics-portfolio) |
| A | Foundation data core / Project 0 | [Drive folder](https://drive.google.com/drive/folders/148qly8JYPGS3nV9FNklo9ZOBflHdSkl8) | [Block A in portfolio repo](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-a) |
| B | Data engineering, DQ and portfolio-risk evidence | [Drive folder](https://drive.google.com/drive/folders/1GSjqsDdS6qNCBeQDEMxx1JC-U4F3yPyd) | [Block B in portfolio repo](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-b) |
| C | C1–C7 credit-risk modeling checkpoints | [Block C folder](https://drive.google.com/drive/folders/15T6gKbJVk3Y93eorRhTSC1yjdzn7p3W_) | [Portfolio repository](https://github.com/susayold/financial-risk-analytics-portfolio) |
| D | PD/LGD/EAD/ECL, loss quantification and stress gates | [Block D folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-) | [Block D in portfolio repo](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-d) |
| E | Monitoring governance and feature-drift monitoring | [Block E private evidence folder](https://drive.google.com/drive/folders/1cF3HXZF9dH4BHLklxfN2QoPpeRj_iU1y) | [Block E checkpoint in portfolio repo](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-e) |
| C–D supporting | Project 3 — Credit Risk Decision Engine | [Drive folder](https://drive.google.com/drive/folders/1-3YYoGzKVEGH9Tie_43sSslUnybDubbP) | [GitHub repository](https://github.com/susayold/credit-risk-decision-engine) |
| D supporting | Project 4 — IFRS 9 ECL & Stress Testing | [Drive folder](https://drive.google.com/drive/folders/1B2BwBho0pBN_Y6-JXymvwzuKE1AiB_pQ) | [GitHub repository](https://github.com/susayold/ifrs9-ecl-stress-testing) |
| E supporting | Project 2 — Credit Portfolio Monitoring | [Drive folder](https://drive.google.com/drive/folders/1EEwuTxoVZAAv8ruTHpL_4zIZexuKMmke) | [GitHub repository](https://github.com/susayold/credit-portfolio-monitoring) |
| F supporting | Project 6 — Risk System Rule Implementation | [Drive folder](https://drive.google.com/drive/folders/1sd3mTkFutoaprwcZB84iyC6egHJMgHw8) | [GitHub repository](https://github.com/susayold/risk-system-rule-implementation) |
| Outside A–F / legacy | Project 5 and C06 fraud checkpoint | [Legacy fraud folder](https://drive.google.com/drive/folders/1NS64ojSQm0ZE8o1zCeFxy0yVy5HkIHwK) | [GitHub repository](https://github.com/susayold/fraud-operational-risk) |

This file only indexes links. The Drive root is the single storage location; GitHub holds public code and website files.

## Current Block D checkpoint

- Status: **`CLOSED_WITH_LIMITATIONS_PORTFOLIO`**; closure substatus: **`FINAL_PORTFOLIO_CLOSURE`**.
- Execution coverage: **100% (10/10 stages)**.
- Portfolio requirement resolution: **100%**.
- Technical QA: **N/N PASS**; final artifact checksum integrity: **100%**.
- Production authorization: **NOT IN SCOPE**; regulatory claim: **NONE**.
- Semantic remediation: **100% (8/8)**; full review QA: **37/37 PASS**; public scan: **122 files / 0 findings**; D9 checksum validation: **25 entries / 0 failures**.
- Portfolio owner: **`susayold`**; decision date: **`2026-09-03`**; canonical tag: **`block-d-v1.0-final`**.
- [Block D status](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_STATUS.md)
- [Block D final scorecard](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_FINAL_SCORECARD.md)
- [Block D machine-readable final scorecard](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_FINAL_SCORECARD.json)
- [Block D full review QA](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_FULL_REVIEW_QA.json)
- [Block D final decision](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json)

## Current Block E checkpoint

- Status: **`STOPPED_AT_E3_G04_REAL_GATE_FAILURE`**; E0 `12/12 PASS`, E1 `10/10 PASS`, E2 `8/8 PASS`, E3 `7/8`.
- E3 blocker: the frozen 79-feature contract has row-level values for only 9 features in the available D1 mart; 70 remain unavailable and are not fabricated.
- R0–R3 remediation passed; R4B is blocked because no exact 79F matrix or complete frozen reconstruction logic was found. E4–E9 were not run because the plan requires stopping at the first unresolved 79F evidence gate. No `block-e-v1.0-final` tag exists.
- [Block E 79F recovery evidence](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-e/RECOVERY_79F)
- [Block E status](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-e/BLOCK_E_STATUS.md)
- [Block E execution tracker](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-e/BLOCK_E_EXECUTION_TRACKER.md)
- [E3 blocker report](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-e/E3_FEATURE_DRIFT/E3_BLOCKER_REPORT.md)
- [Block E private monitoring mart on Drive](https://drive.google.com/file/d/1XS6TfIi7pPzDHQFjxfC1MS_IX1VIvCpD/view?usp=drivesdk)
- [Block E canonical scored population key on private Drive](https://drive.google.com/file/d/1rczaozIFNWb-7VrYzhGimKgY9o6MBRX1/view?usp=drivesdk)

### Block D Drive checkpoint artifacts

- [Block D scorecard — JSON](https://drive.google.com/file/d/1iP6G5fN-HVPQTbOShz81KQOQReEtJ8_Z/view?usp=drivesdk)
- [Block D full-review QA](https://drive.google.com/file/d/13qXEdFccHbhzES8lVoHRD2Fs8GLN17J7/view?usp=drivesdk)
- [D3 contract audit](https://drive.google.com/file/d/1ff0WQq3YIxDgJQEYWsElXIIaYsSpW9EJ/view?usp=drivesdk)
- [D9 closure manifest](https://drive.google.com/file/d/1TdOVbCwPDEs2fJzu6qrYMsG8ZyKloGJD/view?usp=drivesdk)
- [D9 approval register](https://drive.google.com/file/d/1732Er0qo9IkhdkS2V37hsY9cZUvPsSFq/view?usp=drivesdk)
- [D9 owner decision intake](https://drive.google.com/file/d/1FlyvenJIKHSbhTHB896_yCRjSbTYxkcB/view?usp=drivesdk)
- [D9 decision gap register](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/D9_CLOSURE/D9_DECISION_GAP_REGISTER.md)
- [D9 decision gap register on Drive](https://drive.google.com/file/d/1sz6j7M5U1DxRT-VgdiFQfHqXf27QXCUj/view?usp=drivesdk)
- [Block D validation report](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_VALIDATION_REPORT.md)
- [Block D validation report on Drive](https://drive.google.com/file/d/1p_0-dhraDD2vIAFz2bRSaxtG9QK4BGbA/view?usp=drivesdk)
- [Block D README checkpoint on Drive](https://drive.google.com/file/d/1yNE2P3z2z1efOm9lJNolxiLpkenBfjVM/view?usp=drivesdk)
- [Block D previous final-10/10 checkpoint — historical/superseded](https://drive.google.com/file/d/19qBMgtxVoyHU6YHhZvL9PpLCiubVg2I8/view?usp=drivesdk)
- [Block D micro-remediation checkpoint package — pending owner gate](https://drive.google.com/file/d/1KtaOw_vG5kqj9SLKAM75kLDaCL5Pt4dR/view?usp=drivesdk)
- [Block D pre-owner-gate finalization package — checkpoint](https://drive.google.com/file/d/16UIDE_X4GJzM6NCrBeOTfebwKHE3_Ta_/view?usp=drivesdk)
- [Block D pre-final S0 sprint manifest on Drive](https://drive.google.com/file/d/1xopTFW55BG1cqefOHuSsgWynOcPwvhPg/view?usp=drivesdk)
- [Block D private account EL mart on Drive](https://drive.google.com/file/d/1xR9TSRArpCO03Tc_8Kc1QAGVMiOnwiKY/view?usp=drivesdk)
