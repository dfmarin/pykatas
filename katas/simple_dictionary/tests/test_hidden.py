import importlib.util
from pathlib import Path

def load_dictionary_class():
    spec = importlib.util.spec_from_file_location("solution", Path("/sandbox/solution.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Dictionary

def test_overwrite_existing():
    DictClass = load_dictionary_class()
    d = DictClass()
    d.newentry("Python", "A snake")
    d.newentry("Python", "A programming language")
    assert d.look("Python") == "A programming language"

def test_empty_definition():
    DictClass = load_dictionary_class()
    d = DictClass()
    d.newentry("Empty", "")
    assert d.look("Empty") == ""

def test_case_sensitivity():
    DictClass = load_dictionary_class()
    d = DictClass()
    d.newentry("Hello", "Greeting")
    assert d.look("hello") == "Can't find entry for hello"
    assert d.look("HELLO") == "Can't find entry for HELLO"
    assert d.look("Hello") == "Greeting"

def test_multiple_entries():
    DictClass = load_dictionary_class()
    d = DictClass()
    entries = {
        "one": "first",
        "two": "second",
        "three": "third"
    }
    for w, defn in entries.items():
        d.newentry(w, defn)
    for w, defn in entries.items():
        assert d.look(w) == defn

def test_large_number_of_entries():
    DictClass = load_dictionary_class()
    d = DictClass()
    for i in range(10000):
        d.newentry(f"word{i}", f"definition{i}")
    assert d.look("word5000") == "definition5000"
    assert d.look("missing") == "Can't find entry for missing"

