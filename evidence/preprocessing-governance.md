# Preprocessing governance

- Transformations are fit on Development only.
- Validation is used for model comparison and tuning, not for fitting the initial transformation boundary.
- Out-of-Time and Historical Shadow cohorts are never tuned.
- Geography and text are excluded from the champion whitelist.
- The final-resolution target is treated as an observed analytical target, not a verified 12-month PD.
- Expected Loss is defined as a downstream contract using predicted PD × LGD × EAD; the contract is not a completed loss simulation in Block A.
