# B5 Pricing Role Contract

The executable B5T08 gate loads `config/b5_contract.yaml` and requires this exact mapping:

```text
sub_grade     BENCHMARK_ONLY
grade_derived BENCHMARK_ONLY
int_rate      ECONOMICS_ONLY
installment   ECONOMICS_ONLY
term          ECONOMICS_ONLY
```

It also asserts that no supplemental target-like field is carried into the pricing mart. The sole analytical target remains `actual_default` from B4/Zenodo.
