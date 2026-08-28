# Public audit run manifest

## Scope

This manifest describes the public website QA run for Block A `v1.0 / LOCKED`. It is a sanitized website/release manifest and contains no raw data.

## Checks

- Static HTML served successfully on GitHub Pages.
- Shared CSS and JavaScript assets served successfully.
- Social preview asset served as PNG at `1200 × 630`.
- Desktop and mobile layouts rendered without horizontal overflow in the QA run.
- Navigation rail contains 10 section anchors.
- Temporal GOOD shares use the displayed cohort counts: Development `81.54%`, Validation `76.72%`, OOT `76.87%`, Historical Shadow `84.25%`.
- Evidence cards use public GitHub/Zenodo destinations; private Drive artifacts are not required for the public review path.
- Forbidden showcase metrics were removed from the Block A page.

## Numeric reconciliations

- GOOD + BAD = `1,347,681`.
- Development + Validation + OOT + Historical Shadow = `1,347,681`.
- Figshare matched + unmatched = `331,865`.
