from typing import Dict, List

def get_total(costs: Dict[str, float], items: List[str], tax: float) -> float:
    subtotal = 0.0
    for item in items:
        if item in costs:
            subtotal += costs[item]
    total = subtotal * (1 + tax)
    # Round to two decimal places
    return round(total, 2)

