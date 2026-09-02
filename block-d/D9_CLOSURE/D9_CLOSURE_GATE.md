# D9 — Block D Closure Gate

## Status

`CONTROLLED_HOLD` — closure review manifest prepared; Block D is not locked.

## Closure conditions

1. D0 governance QA remains PASS and upstream snapshot is frozen.
2. D1 full score mart and split diagnostics pass.
3. D2 governed-core loss/recovery bridge passes with reconciliation and
   anomaly treatment.
4. D3 limitations are accepted for its declared source scope.
5. D4 LGD is either approved for the governed population or explicitly
   retained as scenario-only with no downstream EL claim.
6. D5 expected-loss proxy passes with population, timing and formula audit.
7. D6 decision policy and D7 pricing controls have owner sign-off.
8. D8 stress/sensitivity evidence is reproducible and bounded.
9. Final artifact index, run manifests, claim boundary and owner sign-off are
   complete.

The decision fields are staged in `D9_APPROVAL_REGISTER.md`; blank or
`PENDING` fields are not treated as approval.

## Current decision

Conditions 2 and 3 are now evidenced by the D1/D2 bridge audits. D4 has
population compatibility but remains scenario-only pending main-case approval;
D5–D8 have controlled analytical packs but not approved production gates.
Therefore the only valid status is `NOT_LOCKED / REVIEW_REQUIRED`; this
document does not declare completion.
