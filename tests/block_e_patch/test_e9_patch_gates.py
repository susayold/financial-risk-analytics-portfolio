from ._helpers import E9, js

def test_e9_patch_gates():
    q = js(E9 / "BLOCK_E_FINAL_QA_PATCHED.json")
    assert q["tests_passed"] == 35 and q["tests_failed"] == 0
    assert all(v == "PASS" for v in q["gates"].values())
