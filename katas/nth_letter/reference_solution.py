from typing import List


def build_word(words: List[str]) -> str:
    result_chars = []
    for i, w in enumerate(words):
        result_chars.append(w[i])
    return "".join(result_chars)
