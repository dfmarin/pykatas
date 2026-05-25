import importlib.util
from pathlib import Path

def load_function():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.get_total

def test_example():
    get_total = load_function()
    costs = {'socks': 5, 'shoes': 60, 'sweater': 30}
    result = get_total(costs, ['socks', 'shoes'], 0.09)
    assert result == 70.85

def test_missing_item():
    get_total = load_function()
    costs = {'apple': 1.0, 'banana': 1.5}
    result = get_total(costs, ['apple', 'orange', 'banana'], 0.0)
    assert result == 2.5  # orange ignored

