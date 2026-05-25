from typing import List


def two_sum(nums: List[int], target: int) -> List[int]:
    """
    Efficient O(n) solution using a hash map.
    """
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    # According to problem constraints, a solution always exists.
    return []
