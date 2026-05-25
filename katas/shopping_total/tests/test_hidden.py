import importlib.util
from pathlib import Path

def load_function():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.get_total

def test_empty_items():
    get_total = load_function()
    costs = {'a': 10}
    assert get_total(costs, [], 0.05) == 0.0

def test_zero_tax():
    get_total = load_function()
    costs = {'x': 100, 'y': 200}
    assert get_total(costs, ['x', 'y'], 0.0) == 300.0

def test_tax_rounding():
    get_total = load_function()
    costs = {'item': 1}
    # 1 + 9% = 1.09 -> rounded to 1.09
    assert get_total(costs, ['item'], 0.09) == 1.09
    # test deeper rounding: 1.234 with tax? Actually let's test 0.3333 cent
    costs = {'pen': 0.99}
    # 0.99 * 1.07 = 1.0593 -> round to 1.06
    assert get_total(costs, ['pen'], 0.07) == 1.06

def test_all_items_missing():
    get_total = load_function()
    costs = {'real': 5}
    assert get_total(costs, ['fake1', 'fake2'], 0.1) == 0.0

def test_duplicate_items():
    get_total = load_function()
    costs = {'apple': 2}
    # Duplicate items count each occurrence
    assert get_total(costs, ['apple', 'apple'], 0.0) == 4.0

def test_large_numbers():
    get_total = load_function()
    costs = {'big': 1e9}
    total = get_total(costs, ['big'], 0.05)
    # 1e9 * 1.05 = 1,050,000,000.00
    assert total == 1050000000.0

def test_floating_precision():
    get_total = load_function()
    costs = {'c': 1.23, 'd': 4.56}
    # 1.23 + 4.56 = 5.79, tax 0.01 -> 5.79*1.01=5.8479 -> round 5.85
    assert get_total(costs, ['c', 'd'], 0.01) == 5.85

