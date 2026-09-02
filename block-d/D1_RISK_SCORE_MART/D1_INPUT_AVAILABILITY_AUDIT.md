# D1 Input Availability Audit

Updated: 2026-09-02

## Finding

The initial availability gap has been resolved at controlled review scope.
Drive contains the upstream Block C packages, and the runtime has now
materialized a D1 Development replay and combined it with the persisted
Validation/OOT artifacts into a 310,066-row matched scored mart. D1 remains
`PASS_WITH_LIMITATIONS` because the scored lane is not the full governed
population.

The available persisted score files were independently audited on 2026-09-02.
Validation 2016 contains 83,664 unique scored accounts with 14,190 BAD cases;
OOT 2017 contains 44,221 unique scored accounts with 5,892 BAD cases. The
recomputed AUCs are 0.8219379569 and 0.8557777505 respectively, with zero
cross-split account-ID overlap. See
`D1_AVAILABLE_SCORE_ARTIFACT_AUDIT.md`. These checks validate the files, not
their coverage of the governed core.

## Evidence inventory

| Object | Drive evidence | What it proves | What it does not prove |
|---|---|---|---|
| C8 self-run package | [C8 package](https://drive.google.com/file/d/1NhAA-gqwjuvzjTcprYft6g4L1g4EpZ57/view?usp=drivesdk) | A runnable package references C7 Development/Validation extraction and a C7 cumulative input | It does not provide a persisted C8E Development prediction file already joined to the governed population |
| C8 README | [C8 README](https://drive.google.com/file/d/1hwD3xsSpGbsg0tY2LvZoZE5JpYcYiQju/view?usp=drivesdk) | The notebook is designed to extract C7 Development/Validation and evaluate candidates | It is not account-level D1 score evidence by itself |
| C8E result package | [C8E results](https://drive.google.com/file/d/1v0KmPsCkRAKGVfubn2u27T9QRDrg5laa/view?usp=drivesdk) | Validation 2016 result files, including validation predictions and feature contract, are available | It does not contain the required full Development score mart |
| C9 closure folder | [C9 folder](https://drive.google.com/drive/folders/1Z_ORctxmgWkDTMXfw-1SDPMC1IcMg70x) | Frozen model, feature contract and OOT 2017 predictions are available | OOT evidence cannot substitute for Development coverage or pricing bridge |

## D1 opening decision and completion evidence

The C8 self-run package was used only as a candidate input for a controlled
materialization run. The following opening requirements are now complete and
are recorded in the D1 run audit:

```text
1. Governed Development IDs were joined to a frozen C8E replay.
2. `model_version = C8E_RICH_BUREAU_CATBOOST_79F` was preserved.
3. The required pricing bridge (`term`, `int_rate`, `installment`,
   `sub_grade`, `grade_derived`) is complete for all 310,066 scored rows.
4. Account-grain uniqueness, score/target validity, expected split counts,
   cross-split ID overlap and population reconciliation passed.
```

The resulting D1 status is `PASS_WITH_LIMITATIONS`: account-level metrics and
cutpoints exist for the matched scored subset, while no full governed
Development/OOT score-coverage claim is made.
