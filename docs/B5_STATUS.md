# B5 Status

## Gate decision

`B5 = REVIEWED / PASS` · Block B remains `IN PROGRESS` · Next gate: `B6 — Portfolio Overview`.

The executable run passed 12/12 independent B5 tests. Raw source files and row-level marts are execution-only and are not published.

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
| RejectStats context rows | 27,648,741 |
| Independent B5 tests | PASS (12/12) |

## Boundary

Zenodo/B4 remains authoritative for population, target, chronology and governed features. Figshare fields retain explicit roles: `sub_grade` and `grade_derived` are benchmark-only; `int_rate`, `installment` and `term` are economics-only. RejectStats is context-only and cannot support rejected-loan default rates, PD, loss or causal approval claims.

