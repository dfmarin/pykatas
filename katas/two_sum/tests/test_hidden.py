import importlib.util
from pathlib import Path

def load_solution():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_example_1():
    sol = load_solution()
    assert sol.two_sum([2, 7, 11, 15], 9) == [0, 1]

def test_example_2():
    sol = load_solution()
    assert sol.two_sum([3, 2, 4], 6) == [1, 2]

def test_example_3():
    sol = load_solution()
    assert sol.two_sum([3, 3], 6) == [0, 1]

def test_negative_numbers():
    sol = load_solution()
    assert sol.two_sum([-1, -2, -3, -4, -5], -8) == [2, 4]  # -3 + -5 = -8

def test_large_numbers():
    sol = load_solution()
    assert sol.two_sum([10**9, 10**9, -10**9], 10**9) == [0, 2]

def test_duplicate_values():
    sol = load_solution()
    assert sol.two_sum([1, 2, 3, 1, 5], 2) == [0, 3]

def test_order_irrelevant():
    sol = load_solution()
    result = sol.two_sum([1, 4, 6, 8], 9)
    assert sorted(result) == [0, 2]  # 1 + 8 = 9

def test_many_elements():
    sol = load_solution()
    nums = list(range(10000))
    target = 9997  # 0 + 9997
    assert sol.two_sum(nums, target) == [0, 9997]

