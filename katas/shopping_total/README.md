# Shopping Total

## Problem Statement

You have a dictionary that maps item names to their prices (as numbers).  
You also have a list of items that were purchased (some may not be in the dictionary).  
You need to calculate the **subtotal** (sum of prices of items that exist in the dictionary) and then apply a **tax rate** (given as a decimal, e.g., `0.09` for 9% tax).  
Finally, round the total to **two decimal places** and return it.

If no valid items are bought, the subtotal is `0`.

## Function Signature

```python
def get_total(costs: dict, items: list, tax: float) -> float:
    ...
```

## Examples

```python
>>> costs = {'socks': 5, 'shoes': 60, 'sweater': 30}
>>> get_total(costs, ['socks', 'shoes'], 0.09)
70.85
```
Explanation:  
Subtotal = 5 + 60 = 65  
Tax = 65 * 0.09 = 5.85  
Total = 65 + 5.85 = 70.85 → rounded to 70.85

## Edge Cases

- If `items` is empty → return `0.00`
- If tax is `0` → return subtotal rounded to two decimals
- Items not found in `costs` are ignored
- Prices may be integers or floats (but you can treat them as numbers)

## Constraints

- `costs` dictionary contains up to 1000 entries
- `items` list length up to 10^4
- Prices are non‑negative
- Tax rate: 0.0 ≤ tax ≤ 1.0

## Task

Implement `get_total` in the starter code.

