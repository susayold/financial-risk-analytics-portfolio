"""Regression self-test for the Block D9 owner decision validator."""

from validate_block_d_owner_decisions import run_validator_self_tests


def main() -> int:
    result = run_validator_self_tests()
    print(f"OWNER DECISION VALIDATOR SELF-TEST {result['tests_passed']}/{result['tests_run']} pass")
    for test in result["tests"]:
        label = test.get("name", test.get("id", "unnamed_test"))
        print(f"{'PASS' if test['pass'] else 'FAIL'}: {label}")
    return 0 if result["tests_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
