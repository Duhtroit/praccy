"""Tests for the strict comparison rules.

These assert the *rejections*, not just the acceptances. A strictness layer
that only proves it can pass correct answers is worthless; the value is in
catching the subtle near-misses that Coderbyte marks wrong.

Run with: python3 -m cbp.strictness_test
"""

from __future__ import annotations

from .strictness import BOOL, INT, STRING, judge, python_type_name

CASES = []


def check(name, got, expected_pass, *args, **kwargs):
    CASES.append((name, got, expected_pass, args, kwargs))


# --- the headline case: boolean where a string is required -------------------
check("string 'true' passes a string contract",
      judge("true", {"expected": "true", "expectedType": STRING}), True)
check("boolean True is REJECTED by a string contract",
      judge(True, {"expected": "true", "expectedType": STRING}), False)
check("boolean False is REJECTED by a string contract",
      judge(False, {"expected": "false", "expectedType": STRING}), False)

# --- the reverse -------------------------------------------------------------
check("boolean True passes a bool contract",
      judge(True, {"expected": True, "expectedType": BOOL}), True)
check("string 'true' is REJECTED by a bool contract",
      judge("true", {"expected": True, "expectedType": BOOL}), False)

# --- bool/int confusion, the Python subclass trap ----------------------------
check("int 1 is REJECTED by a bool contract",
      judge(1, {"expected": True, "expectedType": BOOL}), False)
check("bool True is REJECTED by an int contract",
      judge(True, {"expected": 1, "expectedType": INT}), False)
check("int 1 passes an int contract",
      judge(1, {"expected": 1, "expectedType": INT}), True)

# --- type naming -------------------------------------------------------------
check("python_type_name(True) is bool, not int",
      python_type_name(True) == BOOL, True)
check("python_type_name(1) is int",
      python_type_name(1) == INT, True)
check("python_type_name('1') is string",
      python_type_name("1") == STRING, True)

# --- value mismatch is distinguished from type mismatch ----------------------
check("wrong value reports the value, not the type",
      "wrong value" in judge("abc", {"expected": "xyz", "expectedType": STRING})[1], True)
check("wrong type reports the type mismatch",
      "wrong type" in judge(1, {"expected": "1", "expectedType": STRING})[1], True)

# --- case sensitivity, a real Coderbyte trap ---------------------------------
check("'True' is rejected where 'true' is expected",
      judge("True", {"expected": "true", "expectedType": STRING}), False)
check("'Arithmetic' is rejected where 'arithmetic' is expected",
      judge("Arithmetic", {"expected": "arithmetic", "expectedType": STRING}), False)

# --- int vs float ------------------------------------------------------------
check("float 1.0 is rejected where int 1 is expected",
      judge(1.0, {"expected": 1, "expectedType": INT}), False)
check("int 1 is rejected where float 1.0 is expected",
      judge(1, {"expected": 1.0, "expectedType": "float"}), False)


def run() -> int:
    failures = 0
    print("Strictness tests")
    print("=" * 62)
    for name, got, expected_pass, args, kwargs in CASES:
        if isinstance(got, tuple) and len(got) == 2 and isinstance(got[0], bool):
            ok = got[0] == expected_pass
            detail = f"passed={got[0]}"
        else:
            ok = bool(got) == expected_pass
            detail = f"value={got!r}"
        status = "ok  " if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  {status}  {name:52s} {detail}")

    print("=" * 62)
    total = len(CASES)
    print(f"{total - failures}/{total} passed")
    if failures:
        print(f"\n{failures} FAILURE(S) -- the strictness layer is unsound.")
        return 1
    print("Strictness verified: near-miss answers are rejected correctly.")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(run())
