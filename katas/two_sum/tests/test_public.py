import importlib.util, sys
from pathlib import Path


def load_solution():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_basic_case():
    sol = load_solution()
    assert sol.two_sum([2, 7, 11, 15], 9) == [0, 1]


def test_no_leading_zero():
    sol = load_solution()
    assert sol.two_sum([3, 2, 4], 6) == [1, 2]
