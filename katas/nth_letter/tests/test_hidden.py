import importlib.util
from pathlib import Path


def load_function():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build_word


def test_single_word():
    build_word = load_function()
    assert build_word(["abc"]) == "a"


def test_longer_words():
    build_word = load_function()
    words = ["python", "java", "swift", "cplusplus"]
    assert build_word(words) == "paiu"


def test_all_same_letter():
    build_word = load_function()
    words = ["aaaaa", "bbbbb", "ccccc"]
    assert build_word(words) == "abc"


def test_varying_lengths():
    build_word = load_function()
    words = ["a", "bc", "def", "ghij"]
    assert build_word(words) == "acfj"


def test_large_input():
    build_word = load_function()
    n = 1000
    words = ["a" * (i + 1) for i in range(n)]
    expected = "a" * n
    assert build_word(words) == expected
