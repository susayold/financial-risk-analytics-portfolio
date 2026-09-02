# D4 — LGD Scenario Evidence

## What was done

- Read the D2 retrospective loss proxy output.
- Removed 1,993 exact duplicate rows and generated account-grain Q25/Q50/Q75/Q90
  severity anchors from 269,360 retained BAD evidence rows.
- Excluded the 2018 shadow cohort from primary anchors because of documented
  final-resolution/truncation concerns; retained it as monitor-only evidence.
- Produced an issue-year diagnostic table.
- Persisted test and run-audit manifests.
- Kept the C8E score and `p_bad_final` out of the calculation.

## What this means

This is a `SCENARIO_ONLY` fallback, not a finished empirical LGD model. The
governed-core bridge is still pending, so the output cannot be used to claim
LGD for the C8E matched population or to freeze D5 Expected Loss.
