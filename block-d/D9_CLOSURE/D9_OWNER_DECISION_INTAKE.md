# D9 Owner Decision Intake

This is the controlled handoff for the remaining Block D decisions. The
structured input file is `D9_APPROVAL_REGISTER.json`; the validator is
`src/validate_block_d_owner_decisions.py`.

## Current state

The register is structurally valid but still `PENDING_OWNER_INPUT`. That is the
correct state until an authorized owner records an explicit decision. The
validator currently reports `VALID_PENDING`; it does not convert pending values
into approvals.

## What an owner must record

| Area | Required input |
|---|---|
| D4 main-case LGD | Select exactly one: Q25, Q50, Q75 or Q90 |
| D4 timing | Set `approved=true` for the accepted timing boundary |
| D5 analytical proxy | Set `approved=true` only for the stated analytical formula and claim boundary |
| D6 decision policy | Set both `thresholds_approved=true` and `overrides_approved=true` |
| D7 pricing | Select `DESCRIPTIVE_ONLY`, unless cost/fee/timing evidence is supplied and approved |
| D8 stress | Set `approved=true` for the documented baseline/shock policy |
| Owner sign-offs | Data, model and risk owner each need status, name, date and approval reference |

## Validation commands

From the repository root:

```text
python src/validate_block_d_owner_decisions.py
python src/validate_block_d_owner_decisions.py --require-ready
python src/validate_block_d_d9_checksums.py
```

The first command accepts a valid pending register and writes
`D9_APPROVAL_VALIDATION.json`. The second command intentionally fails until
all required decisions and sign-offs are present.

After an authorized owner completes the register:

1. Run the validator without `--require-ready` and inspect the errors.
2. Run it with `--require-ready`; it must report `READY_FOR_D9_RERUN`.
3. Run the full-review QA and regenerate the D9 closure manifest.
4. Run the checksum validator and only then review whether the closure status can be
   updated.

## Claim boundary

This intake does not authorize production decisions and does not turn the
analytical PD/LGD/EAD/EL or stress outputs into regulatory results. The D9
manifest must remain `NOT_LOCKED_REVIEW_REQUIRED` while any input is pending.
