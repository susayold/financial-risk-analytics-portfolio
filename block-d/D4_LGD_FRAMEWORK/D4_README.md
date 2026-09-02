# D4 — LGD Scenario Evidence

## What was done

- Read the D2 retrospective loss proxy output.
- Used the governed-core-only BAD evidence and generated account-grain
  Q25/Q50/Q75/Q90 severity anchors from 269,249 retained BAD evidence rows.
- Excluded the 2018 shadow cohort from primary anchors because of documented
  final-resolution/truncation concerns; retained it as monitor-only evidence.
- Produced an issue-year diagnostic table.
- Materialized a separate descriptive score-to-loss linkage for the current
  D1 matched scored subset: 49,049/49,049 scored-BAD rows matched across 31
  split/band/decile groups.
- Persisted test and run-audit manifests.
- Kept the C8E score and `p_bad_final` out of the calculation.

## What this means

This is a governed-population `SCENARIO_ONLY` analysis, not a finished
empirical LGD model. The separate score-to-loss table is descriptive linkage
evidence only; it cannot be used to claim score-conditional LGD for the C8E
matched population or to freeze D5 Expected Loss. Explicit main-case LGD/timing
approval remains required.
