# Simple Dictionary

## Problem Statement

Create a class `Dictionary` that mimics a simple word‑definition dictionary.

The class must provide two methods:

1. `newentry(word, definition)`  
   Adds a new entry to the dictionary. If the word already exists, its definition is updated.

2. `look(word)`  
   Returns the definition of the given word. If the word is not found, it returns the string  
   `"Can't find entry for {word}"` (where `{word}` is the searched word).

## Examples

```python
>>> d = Dictionary()
>>> d.newentry('Apple', 'A fruit that grows on trees')
>>> print(d.look('Apple'))
A fruit that grows on trees

>>> print(d.look('Banana'))
Can't find entry for Banana
```

## Constraints

- Words are non‑empty strings (no leading/trailing spaces).
- Definitions are strings (can be empty).
- The dictionary may store up to 10^4 entries.
- All operations should be O(1) on average.

## Task

Implement the `Dictionary` class in the starter code.

