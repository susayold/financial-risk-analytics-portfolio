# CRD.PI Block D — Final Validation Report

## Assessment

`CLOSED_WITH_LIMITATIONS_PORTFOLIO`

The final analytical chain is reproducible from the derived D1/D2/D3 inputs on the execution disk. D4–D8 final artifacts, governance-mode validation, status consistency, claim-boundary scanning, and checksum controls are required before publication. No production or regulatory authorization is claimed.

## Method and evidence

- D4 used 49,049 matched BAD rows, the frozen D2 retrospective LGD proxy, hard leakage exclusions, and rolling-origin temporal folds. The challenger decision is machine-readable; Q50 is selected because the predeclared challenger materiality rule was not met.
- D5 uses `p_bad_final × lgd_proxy × ead_proxy`, with account/segment/portfolio reconciliation and separate sensitivity views.
- D6 derives Growth/Balanced/Conservative scenarios on Validation-2016 and performs unchanged historical OOT replay on 2017.
- D7 is explicitly `DESCRIPTIVE_ONLY`.
- D8 contains rank-preserving PD stress, versioned LGD/EAD rules, sequential attribution, mix audit, reverse-stress breakpoints, and policy-under-stress with frozen thresholds.

## Claim boundary

Outputs are analytical portfolio evidence. They are not IFRS 9, Basel, regulatory LGD/EAD/ECL, production-approved lending policy, realized profitability, observed EAD, or verified 12-month PD.

## Closure axes

Execution 100%; portfolio requirement resolution 100%; technical QA 100%; artifact checksum integrity 100%; production/regulatory readiness `NOT_IN_SCOPE`.
