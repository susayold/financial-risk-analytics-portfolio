# CRD.PI Block A–F Project Links

Updated: 2026-09-08

This file is a navigation index. Analytical claims remain governed by the canonical stage artifacts and releases.

| Block / scope | Data or project | Google Drive | GitHub / Website |
|---|---|---|---|
| A–F umbrella | CRD.PI project root | [Drive root folder](https://drive.google.com/drive/folders/1Y9X6hEcoa7PVpg-o827vY3w0lUQIWYM0) | [Portfolio repository](https://github.com/susayold/financial-risk-analytics-portfolio) |
| A | Foundation data core / governed target and chronology | [Drive folder](https://drive.google.com/drive/folders/148qly8JYPGS3nV9FNklo9ZOBflHdSkl8) | [Block A](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-a) |
| B | Data engineering, DQ and descriptive portfolio-risk evidence | [Drive folder](https://drive.google.com/drive/folders/1GSjqsDdS6qNCBeQDEMxx1JC-U4F3yPyd) | [Block B](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-b) |
| C | Frozen credit-risk modeling and validation checkpoints | [Block C folder](https://drive.google.com/drive/folders/15T6gKbJVk3Y93eorRhTSC1yjdzn7p3W_) | [Portfolio repository](https://github.com/susayold/financial-risk-analytics-portfolio) |
| D | Model-score, LGD/EAD proxies, analytical expected loss, historical policy simulation and stress testing | [Block D folder](https://drive.google.com/drive/folders/1xutm72gqys_QruCtCx5Rd9xmQ0YVOud-) | [Block D](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-d) |
| E | Monitoring, KRIs, feature drift, calibration and governance | [Private evidence folder](https://drive.google.com/drive/folders/1cF3HXZF9dH4BHLklxfN2QoPpeRj_iU1y) | [Block E](https://github.com/susayold/financial-risk-analytics-portfolio/tree/main/block-e) |
| F | Recruiter-facing delivery — seven primary pages | [Drive root folder](https://drive.google.com/drive/folders/1Y9X6hEcoa7PVpg-o827vY3w0lUQIWYM0) | [01 Overview](https://susayold.github.io/financial-risk-analytics-portfolio/) · [02 Portfolio](https://susayold.github.io/financial-risk-analytics-portfolio/portfolio-risk/) · [03 Model](https://susayold.github.io/financial-risk-analytics-portfolio/model-decisioning/) · [04 Loss & Policy](https://susayold.github.io/financial-risk-analytics-portfolio/loss-policy-stress/) · [05 Monitoring](https://susayold.github.io/financial-risk-analytics-portfolio/monitoring/) · [06 Governance](https://susayold.github.io/financial-risk-analytics-portfolio/governance/) · [07 Architecture](https://susayold.github.io/financial-risk-analytics-portfolio/architecture/) |

## Canonical analytical releases

### Block D

- Status: **`CLOSED_WITH_LIMITATIONS_PORTFOLIO`**.
- Canonical tag: **`block-d-v1.0-final`**.
- Analytical chain: frozen model score → analytical LGD proxy → contractual EAD proxy → analytical expected-loss proxy → historical policy simulation → analytical stress.
- Production / regulatory readiness remains outside scope.
- [Block D status](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_STATUS.md)
- [Block D final scorecard](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/BLOCK_D_FINAL_SCORECARD.md)
- [Block D final decision](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-d/D9_CLOSURE/D9_FINAL_BLOCK_D_DECISION.json)
- [Block D release](https://github.com/susayold/financial-risk-analytics-portfolio/releases/tag/block-d-v1.0-final)

### Block E

- Status: **`PASS_WITH_MONITORING`**.
- Canonical tag: **`block-e-v1.0.2-final`**.
- Frozen monitoring snapshot: **310,066 rows / 79 features**.
- Governance: **92 KRIs / 21 alerts / 3 breaches / 21 investigations / 21 actions**.
- Current highest KRI: **AMBER**; historical highest: **RED**.
- Production authorization remains `false`; regulatory compliance is not claimed.
- [Block E status](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-e/BLOCK_E_STATUS.md)
- [Block E patched QA](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-e/E9_FINAL/BLOCK_E_FINAL_QA_PATCHED.json)
- [Block E patched decision](https://github.com/susayold/financial-risk-analytics-portfolio/blob/main/block-e/E9_FINAL/BLOCK_E_DECISION_PATCHED.json)
- [Block E canonical release](https://github.com/susayold/financial-risk-analytics-portfolio/releases/tag/block-e-v1.0.2-final)

## Block F delivery state

Block F is being closed through a dedicated delivery QA sprint. It must not change the frozen model, target, 79-feature contract, Block D economics, policy thresholds or Block E monitoring findings.

Target closure artifacts:

```text
block-f/BLOCK_F_STATUS.md
block-f/BLOCK_F_FINAL_QA.json
block-f/BLOCK_F_RELEASE_MANIFEST.json
block-f/BLOCK_F_PUBLIC_ARTIFACT_INDEX.csv
block-f/BLOCK_F_CLOSURE.md
```

Target final tag after all delivery gates pass:

```text
block-f-v1.0-final
```

## Supporting repositories

| Scope | Project | GitHub |
|---|---|---|
| C–D supporting | Credit Risk Decision Engine | [Repository](https://github.com/susayold/credit-risk-decision-engine) |
| D supporting | IFRS 9-Style ECL & Stress Testing | [Repository](https://github.com/susayold/ifrs9-ecl-stress-testing) |
| E supporting | Credit Portfolio Monitoring | [Repository](https://github.com/susayold/credit-portfolio-monitoring) |
| F supporting | Risk System Rule Implementation | [Repository](https://github.com/susayold/risk-system-rule-implementation) |
| Legacy / outside A–F | Fraud & Operational Risk | [Repository](https://github.com/susayold/fraud-operational-risk) |

## Claim boundary reminder

- Final-resolution BAD/GOOD is not a verified regulatory 12-month PD.
- LGD/EAD are analytical proxies/assumptions in this portfolio project.
- Analytical expected loss is not IFRS 9 / Basel production ECL.
- Historical policy simulation is not a deployed underwriting policy.
- Historical monitoring simulation is not live production monitoring.
