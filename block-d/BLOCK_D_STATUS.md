# BLOCK D STATUS

Updated: 2026-09-03

## Current status

`D0 PASS` · `D1 PASS_WITH_LIMITATIONS` · `D2 PASS_WITH_LIMITATIONS` · `D3 PASS_WITH_LIMITATIONS` · `D4 BRIDGE_RECONCILED_APPROVAL_PENDING` · `D5–D9 CONTROLLED_HOLD`

Block D is not locked. The governance foundation and controlled analytical packs are implemented and reviewed; downstream outputs remain non-production until the declared assumptions and owner decisions are approved.

## Progress scorecard

- Planned stages with executed evidence: **10/10 = 100%**.
- Full-review technical QA: **53/53 PASS**.
- D9 manifest evidence checksums: **15/15 PASS**.
- Closure readiness toward a fully approved `LOCKED` state: **73.5%** under
  the documented conversion in `BLOCK_D_PLAN_COMPLETION_SCORECARD.md`.
- Final status: **`NOT_LOCKED_REVIEW_REQUIRED`**. The percentage does not imply
  owner approval, production readiness or a regulatory claim.

## Completed

### D0 — Economics Governance Contract

- Upstream status frozen: A `LOCKED`, B `LOCKED`, C `CLOSED_WITH_MONITORING`.
- Frozen model frozen as `C8E_RICH_BUREAU_CATBOOST_79F`, 79 features.
- `p_bad_final` and `actual_default` semantics preserved.
- Full-core and matched-enriched lanes separated.
- `loan_amnt` registered as `ead_origination_proxy`.
- LGD, pricing cost and stress assumptions explicitly left pending evidence.
- Block B → C pricing-variable re-contract retained as an auditable exception.
- Post-outcome fields marked evidence-only and forbidden as underwriting predictors.
- QA: **10/10 gates PASS**.

### D1 — Frozen Risk Score & Decision Mart

- Contract, risk bands, deterministic build script and QA schema created.
- Source packages inspected without retraining C8E or tuning OOT.
- Persisted C8E Validation and C9 OOT score files independently audited:
  required columns, account uniqueness, target/score validity, expected row
  counts and zero cross-split ID overlap all pass.
- Development scores were replayed from the frozen C8E 79-feature model without
  refitting, OOT tuning or recalibration: 182,181 matched Development rows.
- The scored decision mart contains **310,066** unique rows: 182,181
  Development, 83,664 Validation and 44,221 OOT; score coverage and pricing
  bridge are 100% within this matched scored subset.
- D1 QA: **10/10 executable gates PASS**. Status remains
  `PASS_WITH_LIMITATIONS` because this is the C8E matched scored subset, not a
  claim that every governed account has a score.

### D3 — EAD Framework

- Contractual amortization scenarios executed on the 331,865-row accepted/pricing source.
- 331,761 rows have valid non-increasing schedules.
- 104 schedule anomalies are retained as `EXCLUDED_DATA_ERROR`; their timing scenarios are not used.
- Origination EAD proxy reconciles exactly to `loan_amnt`.
- Public D3 contract audit: **8/8 checks PASS**; private schedule calculations
  remain bounded to the declared P2 scope.
- QA: **8/8 gates PASS** within the declared P2 scope. The resulting schedules are contractual scenarios, not approved regulatory EAD.

### D2 — Loss & Recovery Evidence

- The legacy source-level LendingClub loss audit covered **2,275,739 rows**;
  the separately checksummed accepted bridge artifact used for exact ID
  reconciliation contains **2,260,701 rows**. These artifacts are tracked
  separately and are not conflated.
- Resolved final outcomes: **1,356,914 rows** = **271,353 BAD** and **1,085,561 GOOD**.
- Required retrospective recovery fields are present and their timing/role is documented.
- Loss-quality treatment is explicit: **1,355,773 VALID** and **1,141 CLIPPED_FOR_MODELING**; no silent clipping is permitted.
- The current score-to-loss sub-audit covers **49,049/49,049 scored-BAD rows**
  from the 310,066-row D1 mart with zero target mismatches; the historical
  20,082-row score-only audit remains separately retained. The canonical
  account-grain proxy retains **269,360** rows after removing **1,993** exact
  duplicates from the legacy source-level proxy.
- The exact governed bridge is now materialized and audited: **1,347,681 / 1,347,681** IDs match the accepted source, target concordance is 100%, loan amount concordance is 100%, and there are no source duplicate-ID groups or target conflicts.
- All **269,249** governed BAD rows have account-grain retrospective loss
  evidence. A governed-core-only BAD evidence file is separated from the
  2,104 valid BAD source rows outside the core.
- QA: governed bridge checks **6/6 PASS**. Status remains
  `PASS_WITH_LIMITATIONS` because the evidence is retrospective BAD-only and
  does not become regulatory LGD or GOOD-row recovery evidence.

### D4 — LGD Scenario Evidence

- Account-grain Q25/Q50/Q75/Q90 LGD anchors were regenerated from **269,249** governed BAD rows; the 2018 shadow cohort remains monitor-only and excluded from primary anchors because of documented final-resolution/truncation concerns.
- The D2 population bridge now passes. D4 is therefore bridge-reconciled, but
  the anchors remain scenario assumptions pending explicit main-case approval;
  they are not an empirical C8E LGD model.
- No `p_bad_final` or C8E score is used; this is not an empirical C8E LGD model.
- QA: **10 PASS / 0 FAIL / 0 PENDING** in the D4 run audit. A separate
  descriptive score-to-loss linkage covers 49,049/49,049 current scored-BAD
  rows; main-case LGD/timing approval remains pending.

## Not claimed

- No full-governed-population score coverage is claimed; D1 is limited to the
  310,066-row C8E matched scored subset.
- D3 contractual EAD timing scenarios, D5 analytical expected-loss proxy
  scenarios, D6 proposed policy assignments, D7 descriptive pricing
  diagnostics and D8 sensitivity cells have been calculated for review scope;
  none is an approved production or regulatory result.
- D4 scenario anchors are not approved main-case LGD inputs and must not be combined with `p_bad_final`.
- No regulatory PD/LGD/EAD/ECL or realized profit/loss claim is made.

### D5–D9 downstream gates

The contracts and gate manifests for D5 Expected Loss, D6 Decision Policy, D7
Pricing Adequacy, D8 Stress/Sensitivity and D9 Closure are now recorded. Their
controlled status remains `CONTROLLED_HOLD` until the D4 main-case assumption
and owner thresholds are approved; no downstream production claim is made. See
`D5_D9_DOWNSTREAM_GATE_REGISTER.md` and `D5_D9_GATE_QA.json`.

### D9 — Closure controls

- The closure manifest remains `NOT_LOCKED_REVIEW_REQUIRED` and
  `numeric_output_claimed=false`.
- The structured owner register is `VALID_PENDING`; six decisions and three
  owner sign-offs remain blank/pending.
- The validator self-test is **3/3 PASS**, including rejection of an approved
  LGD row without a selected option and acceptance of a complete synthetic
  register for rerun readiness.
- The independent validation report is recorded and bounded to
  `SHARE WITH CAVEATS — NOT READY TO LOCK`.
- The current controls do not change the approval register and do not infer any
  owner decision.

## Blocking inputs

1. Explicit approval of the D4 main-case LGD scenario/timing boundary.
2. Acceptance boundary for the D5 analytical expected-loss proxy.
3. Owner decision on D6 action thresholds and overrides, D7 pricing cost/fee
   assumptions if profitability is required, and D8 baseline/shock policy.
4. Data/model/risk owner sign-off before final D9 closure.

The available private C9 closure package contains the frozen model, C9 OOT predictions and C8E Validation predictions, but does not by itself provide all three inputs above.

## Next valid action

Record the D4 main-case decision, confirm the D5 proxy acceptance boundary,
approve D6 thresholds/overrides and D8 shocks, and supply D7 cost/fee inputs if
profitability is required. Then obtain owner sign-off and rerun the final D9
closure gate. Validate the register with
`python src/validate_block_d_owner_decisions.py --require-ready` and verify
manifest checksums with `python src/validate_block_d_d9_checksums.py`. Until
that happens, the current controlled analytical outputs must remain
non-production.
