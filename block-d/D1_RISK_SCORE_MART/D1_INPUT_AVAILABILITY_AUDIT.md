# D1 Input Availability Audit

Updated: 2026-09-02

## Finding

Drive contains upstream Block C packages, but the available objects are not
equivalent to a complete D1 Development score mart. D1 remains
`REVIEW_REQUIRED`.

## Evidence inventory

| Object | Drive evidence | What it proves | What it does not prove |
|---|---|---|---|
| C8 self-run package | [C8 package](https://drive.google.com/file/d/1NhAA-gqwjuvzjTcprYft6g4L1g4EpZ57/view?usp=drivesdk) | A runnable package references C7 Development/Validation extraction and a C7 cumulative input | It does not provide a persisted C8E Development prediction file already joined to the governed population |
| C8 README | [C8 README](https://drive.google.com/file/d/1hwD3xsSpGbsg0tY2LvZoZE5JpYcYiQju/view?usp=drivesdk) | The notebook is designed to extract C7 Development/Validation and evaluate candidates | It is not account-level D1 score evidence by itself |
| C8E result package | [C8E results](https://drive.google.com/file/d/1v0KmPsCkRAKGVfubn2u27T9QRDrg5laa/view?usp=drivesdk) | Validation 2016 result files, including validation predictions and feature contract, are available | It does not contain the required full Development score mart |
| C9 closure folder | [C9 folder](https://drive.google.com/drive/folders/1Z_ORctxmgWkDTMXfw-1SDPMC1IcMg70x) | Frozen model, feature contract and OOT 2017 predictions are available | OOT evidence cannot substitute for Development coverage or pricing bridge |

## D1 opening decision

The C8 self-run package is a valid candidate input for a controlled
materialization run. It is not treated as proof that D1 has passed. Before
opening D1, the runtime must materialize and checksum:

```text
governed Development IDs
C8E Development predictions/scores
model_version = C8E_RICH_BUREAU_CATBOOST_79F
pricing bridge: term, int_rate, installment, sub_grade, grade_derived
```

The materialized output must then pass account-grain uniqueness, row-count,
coverage, target-concordance and no-leakage checks. Until that occurs, D1 has
no account-level metrics, decile cutpoints or full Development/OOT mart claim.

