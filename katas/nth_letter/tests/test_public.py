import importlib.util
from pathlib import Path

def load_function():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_word

def test_example():
    build_word = load_function()
    assert build_word(["yoda", "best", "has"]) == "yes"

def test_two_words():
    build_word = load_function()
    assert build_word(["hello", "world"]) == "ho"

def test_empty_list():
    build_word = load_function()
    assert build_word([]) == ""

