# CRD.PI — Credit Risk Decisioning & Portfolio Intelligence

**CRD.PI** is an end-to-end credit-risk analytics portfolio connecting governed lending data, portfolio risk, a frozen out-of-time credit model, analytical loss economics, historical policy simulation, monitoring governance, and a public-safe recruiter-facing delivery layer.

[Open the live CRD.PI website](https://susayold.github.io/financial-risk-analytics-portfolio/)

## Project journey

| Page | Question | Live page |
|---|---|---|
| 01 — Executive Overview | What is CRD.PI and what does it demonstrate? | [Overview](https://susayold.github.io/financial-risk-analytics-portfolio/) |
| 02 — Portfolio Risk | Where is observed portfolio risk concentrated? | [Portfolio](https://susayold.github.io/financial-risk-analytics-portfolio/portfolio-risk/) |
| 03 — Risk Model & Decisioning | Can the frozen model rank historical OOT risk credibly? | [Model](https://susayold.github.io/financial-risk-analytics-portfolio/model-decisioning/) |
| 04 — Loss, Policy & Stress | What does the score mean for analytical loss, policy and stress? | [Loss & Policy](https://susayold.github.io/financial-risk-analytics-portfolio/loss-policy-stress/) |
| 05 — Monitoring & Early Warning | What changed and what requires attention? | [Monitoring](https://susayold.github.io/financial-risk-analytics-portfolio/monitoring/) |
| 06 — Governance & Audit | Can a reviewer trace a signal into an action and release? | [Governance](https://susayold.github.io/financial-risk-analytics-portfolio/governance/) |
| 07 — Architecture & Delivery | How is governed evidence delivered safely? | [Architecture](https://susayold.github.io/financial-risk-analytics-portfolio/architecture/) |

```text
Data
→ Portfolio Risk
→ Risk Model
→ Loss & Policy
→ Monitoring
→ Governance
→ Delivery
```

## Headline evidence

- **1,347,681** governed resolved granted loans in the core portfolio.
- Frozen champion: **C8E_RICH_BUREAU_CATBOOST_79F** with **79 features**.
- Historical one-time OOT 2017 **ROC-AUC 0.8558** on **44,221** scored accounts.
- Matched scored analytical population: **310,066** accounts.
- Origination exposure proxy: **$4.47B**.
- Central analytical expected-loss proxy: **$526.75M**, or **11.79% analytical EL rate**.
- Monitoring governance: **92 KRIs**, **21 alerts**, **3 breaches**, **21 investigations**, **21 actions**.
- Current highest KRI is **AMBER**; historical highest observed KRI is **RED**.

## What the project demonstrates

CRD.PI is designed to show a complete analytical risk workflow rather than a single model metric:

- governed source, target, chronology and analytical grain;
- descriptive portfolio-risk concentration and materiality;
- leakage-aware model development with frozen 79-feature contract;
- one-time historical out-of-time validation and exact score replay;
- analytical LGD/EAD/expected-loss proxies with explicit claim boundaries;
- historical policy-routing trade-offs and analytical stress testing;
- feature drift, score stability, discrimination, calibration and policy-capacity monitoring;
- KRI → alert → breach → investigation → action governance;
- deterministic public-data contracts, claim tests, privacy scanning and static delivery.

## Claim boundaries

This is a **historical analytical portfolio project**.

- The target is final-resolution BAD/GOOD; it is **not a verified regulatory 12-month PD**.
- LGD and EAD are analytical proxies/assumptions, not regulatory production parameters.
- Expected loss is an **analytical expected-loss proxy**, not IFRS 9 or Basel production ECL.
- Policy results are historical simulations, not deployed underwriting decisions.
- Pricing diagnostics are descriptive, not an optimal-pricing or profitability engine.
- Monitoring is historical portfolio-project monitoring, not live production monitoring.
- Production authorization remains **false** and regulatory compliance is **not claimed**.

## Canonical analytical releases

- Block D: [`block-d-v1.0-final`](https://github.com/susayold/financial-risk-analytics-portfolio/releases/tag/block-d-v1.0-final)
- Block E: [`block-e-v1.0.2-final`](https://github.com/susayold/financial-risk-analytics-portfolio/releases/tag/block-e-v1.0.2-final)
- Block F: **final closure in progress** on the recruiter-facing delivery layer.

Block F must not change the model, target, 79-feature contract, Block D economics, policy thresholds or Block E monitoring findings.

## Reproducibility & delivery QA

The delivery layer uses page-specific JSON contracts under `public/data/`, deterministic Python builders under `scripts/`, and repository tests under `tests/`.

Block F closure adds:

```text
build all public data
→ cross-page reconciliation
→ claim-boundary tests
→ full public-bundle privacy scan
→ browser route / responsive / accessibility QA
→ GitHub Actions enforcement
→ final release evidence
```

## Repository map

- `block-a/` — governed data foundation.
- `block-b/` — data-quality and portfolio-risk evidence.
- `block-d/` — analytical loss, policy and stress.
- `block-e/` — monitoring and governance.
- `portfolio-risk/`, `model-decisioning/`, `loss-policy-stress/`, `monitoring/`, `governance/`, `architecture/` — recruiter-facing pages.
- `public/data/` — sanitized aggregate page contracts.
- `scripts/` — deterministic data-build and QA scripts.
- `tests/` — page and cross-page validation.
- [`PROJECT_MASTER_LINKS.md`](PROJECT_MASTER_LINKS.md) — project / release navigation index.

## Related risk projects

These supporting repositories remain useful examples, but CRD.PI is the flagship end-to-end project.

| Project | Focus | GitHub |
|---|---|---|
| Credit Portfolio Monitoring & Early Warning | Portfolio monitoring and KRI actions | [Repository](https://github.com/susayold/credit-portfolio-monitoring) |
| Credit Risk Decision Engine | WOE/IV, scorecard and cutoff analysis | [Repository](https://github.com/susayold/credit-risk-decision-engine) |
| IFRS 9-Style ECL & Stress Testing | Analytical PD/LGD/EAD/ECL-style sensitivity and macro stress | [Repository](https://github.com/susayold/ifrs9-ecl-stress-testing) |
| Fraud Detection, Controls & Operational Risk | Fraud modeling, controls and root-cause analysis | [Repository](https://github.com/susayold/fraud-operational-risk) |
| Risk System Rule Implementation | Rule matrix, UAT/SIT, release and rollback controls | [Repository](https://github.com/susayold/risk-system-rule-implementation) |

## Contact

- **Nguyen Pham Khoi Nguyen**
- Email: `nguyen28052005@gmail.com`
- GitHub: [github.com/susayold](https://github.com/susayold)
