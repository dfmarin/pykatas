import importlib.util
from pathlib import Path


def load_dictionary_class():
    """Loads the Dictionary class from the user's solution."""
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Dictionary


def test_newentry_and_look():
    DictClass = load_dictionary_class()
    d = DictClass()
    d.newentry("Apple", "A fruit that grows on trees")
    assert d.look("Apple") == "A fruit that grows on trees"


def test_missing_word():
    DictClass = load_dictionary_class()
    d = DictClass()
    assert d.look("Banana") == "Can't find entry for Banana"
