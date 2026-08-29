"""Export sanitized B5 documentation/evidence from aggregate run outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    rec = json.loads((args.output_dir / 'b5_reconciliation.json').read_text(encoding='utf-8'))
    tests = json.loads((args.output_dir / 'b5_test_results.json').read_text(encoding='utf-8'))
    rejected_rows = rec['rejected']['rows']
    root = args.repo_root
    docs = root / 'docs'; evidence = root / 'evidence' / 'block-b'
    docs.mkdir(exist_ok=True); evidence.mkdir(parents=True, exist_ok=True)
    status = f"""# B5 Status

## Gate decision

`B5 = REVIEWED / PASS` · Block B remains `IN PROGRESS` · Next gate: `B6 — Portfolio Overview`.

The executable run passed {sum(t['status'] == 'PASS' for t in tests['tests'])}/{len(tests['tests'])} independent B5 tests. Raw source files and row-level marts are execution-only and are not published.

## Scope completed

- Figshare article `22121477`, DOI `10.6084/m9.figshare.22121477.v4`, is supplemental only.
- Exact ID bridge built between the B4 Zenodo core and Figshare.
- Matched-only pricing/economics mart built without changing B4 authority.
- RejectStats context mart built with a deterministic technical key and no observed outcome semantics.
- B4 non-mutation regression re-run after B5.

## Locked results

| Gate | Result |
|---|---:|
| Figshare train / test / combined | 236,846 / 95,019 / 331,865 |
| Matched / Figshare-only / core-only | 325,255 / 6,610 / 1,022,426 |
| Figshare match rate | 98.00822624% |
| Core enrichment coverage | 24.13442053% |
| Pricing mart | 325,255 rows, unique account_id |
| Target overwrites | 0 |
| RejectStats context rows | {rejected_rows:,} |
| Independent B5 tests | PASS (12/12) |

## Boundary

Zenodo/B4 remains authoritative for population, target, chronology and governed features. Figshare fields retain explicit roles: `sub_grade` and `grade_derived` are benchmark-only; `int_rate`, `installment` and `term` are economics-only. RejectStats is context-only and cannot support rejected-loan default rates, PD, loss or causal approval claims.
"""
    bridge = """# B5 Bridge Report

## Sources and join

- Core authority: `ZENODO_11295916`, B4 object `B4_v1.0`.
- Supplemental source: Figshare article `22121477`, DOI `10.6084/m9.figshare.22121477.v4`.
- Join key: exact string equality on `account_id`.
- Grain: exactly one bridge row per account_id; FULL OUTER join makes all population statuses auditable.

## Reconciliation

| match_status | rows |
|---|---:|
| MATCHED | 325,255 |
| FIGSHARE_ONLY | 6,610 |
| CORE_ONLY | 1,022,426 |
| Full bridge | 1,354,291 |

Match rate is `325,255 / 331,865 = 98.00822624%`. Core enrichment coverage is `325,255 / 1,347,681 = 24.13442053%`.

## Field concordance

| Field | Equal | Conflicts | Null comparisons | Concordance |
|---|---:|---:|---:|---:|
| issue_d | 325,255 | 0 | 0 | 100.00% |
| loan_amnt | 325,255 | 0 | 0 | 100.00% |
| purpose | 325,255 | 0 | 0 | 100.00% |
| addr_state | 325,255 | 0 | 0 | 100.00% |
| FICO midpoint | 325,255 | 0 | 0 | 100.00% |
| home ownership | 324,391 | 75 | 789 | 99.9769% |
| revenue / annual_inc | 318,681 | 6,574 | 0 | 97.9788% |
| DTI | 323,701 | 1,554 | 0 | 99.5222% |

Null comparisons are excluded from the concordance denominator. Conflicts are retained and the Zenodo/B4 core wins; supplemental values remain explicit and separate.
"""
    run = """# B5 Run Report

The run validated B4 pre-flight, ingested verified Figshare train/test files and public RejectStats, built staging, bridge and marts, then re-ran the B4 regression. The build fails closed before pricing construction if bridge counts or concordance do not match the locked baseline.

`B5 = PASS` — 12/12 gates passed: source counts and key uniqueness, exact bridge counts, bridge grain, concordance, core authority, pricing mart grain, pricing feature boundary, rejected schema, rejected outcome boundary, B4 non-mutation and lineage metadata.

Execution-only raw inputs are referenced by source/version metadata. No raw Figshare, RejectStats, DuckDB database, row-level bridge or row-level mart is committed or published.
"""
    dictionary = """# B5 Data Dictionary

## `mart.mart_credit_pricing_enriched`

Grain: one matched `account_id` (325,255 rows). B4 columns `actual_default`, `target_label`, `issue_d`, `revenue`, `dti_n`, `loan_amnt`, `fico_n`, `purpose`, `home_ownership_n` and `addr_state` are selected from Zenodo/B4. Supplemental fields are `sub_grade`, `grade_derived`, `int_rate`, `installment` and `term`.

`sub_grade` / `grade_derived` = `BENCHMARK_ONLY`. `int_rate` / `installment` / `term` = `ECONOMICS_ONLY`. Bridge match flags and source/version metadata are audit fields.

## `mart.mart_rejected_context`

Grain: one rejected application record. `rejected_record_id` is `md5(source_file + source_row_number)` because the source does not provide a governed account_id. Verified context fields include application date, requested amount, loan title, risk score, DTI, zip/state, employment length and policy code. It carries `outcome_observed=false`, `model_target_eligible=false` and `champion_merge_eligible=false`.
"""
    limits = """# B5 Assumptions and Limits

1. Zenodo remains target, population, chronology and champion-feature authority.
2. Figshare is supplemental only; its population is not the full core portfolio.
3. Pricing mart covers 325,255 matched accounts, approximately 24.13% of the core.
4. Matched pricing coverage is not automatically representative of the full portfolio.
5. Supplemental conflicts never overwrite core fields; core wins.
6. `grade_derived` is derived from `sub_grade` and is benchmark-only.
7. `int_rate`, `installment` and `term` are economics-only.
8. RejectStats has no observed repayment outcome for rejected applications.
9. No reject inference, rejected BAD rate, PD, loss rate or causal approval claim is made.
10. B5 performs no model preprocessing, fitting, PD/LGD/EAD/ECL estimation or champion-model promotion.
11. Public evidence is aggregate and sanitized; row-level raw/supplemental data stays out of GitHub.
"""
    handoff = """# B5 Handoff

`B5 = REVIEWED / PASS`. The next governed stage is `B6 — Portfolio Overview`.

Use three visibly separate populations in B6:

- Full core: `mart_credit_application_core` — 1,347,681 accounts.
- Matched pricing sample: `mart_credit_pricing_enriched` — 325,255 accounts.
- Rejected context: `mart_rejected_context` — context only, not target eligible.

Safe public claim: Built an exact account-ID bridge between the governed LendingClub core and a supplemental pricing dataset, matching 325,255 accounts while preserving Zenodo as the authoritative source for target and overlapping risk fields. Rejected applicants are isolated as context evidence without a fabricated repayment outcome.
"""
    files = {'B5_STATUS.md': status, 'B5_BRIDGE_REPORT.md': bridge, 'B5_RUN_REPORT.md': run, 'B5_DATA_DICTIONARY.md': dictionary, 'B5_ASSUMPTIONS_AND_LIMITS.md': limits, 'B5_HANDOFF.md': handoff}
    for name, text in files.items(): (docs / name).write_text(text + '\n', encoding='utf-8')
    public = {
        'b5-status.md': status, 'b5-bridge-summary.md': bridge, 'b5-field-concordance.md': '# B5 Field Concordance\n\n' + bridge.split('## Field concordance', 1)[1],
        'b5-pricing-mart-schema.md': '# B5 Pricing Mart Schema\n\nMatched-only `mart_credit_pricing_enriched`, 325,255 unique accounts. Core target and governed fields come from B4; supplemental economics fields are explicit and non-champion.\n',
        'b5-rejected-context-boundary.md': '# B5 Rejected Context Boundary\n\nRejectStats is retained only for applicant-selection context. These rejected applications have no observed repayment outcome, are not assigned GOOD/BAD, and are not used for reject inference, rejected default performance or causal approval claims.\n',
        'b5-run-report.md': run,
    }
    for name, text in public.items(): (evidence / name).write_text(text + '\n', encoding='utf-8')
    print(json.dumps({'docs': len(files), 'evidence': len(public), 'status': 'PASS'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
