# Nth Letter Concatenation

## Problem Statement

Given a list of words, build a new string by taking the **nth** letter from each word,  
where `n` is the index of the word in the list (starting from 0).

For example:
```python
>>> build_word(["yoda", "best", "has"])
"yes"
```
Explanation:
- Word 0 (`"yoda"`) → index 0 → `'y'`
- Word 1 (`"best"`) → index 1 → `'e'`
- Word 2 (`"has"`)  → index 2 → `'s'`
Result: `"yes"`

## Constraints

- The input is always valid: every word has at least (index + 1) letters.
- An empty list returns an empty string `""`.

## Function Signature

```python
def build_word(words: list[str]) -> str:
    ...
```

## Examples

```python
>>> build_word(["hello", "world"])
"ho"   # index 0: 'h', index 1: 'o'

>>> build_word([])
""
```

## Task

Implement `build_word` in the starter code.

