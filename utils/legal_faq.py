import json
import os
import re

FAQ_PATH = os.path.join(os.path.dirname(__file__), 'legal_faq.json')

# Load FAQ data once
with open(FAQ_PATH, encoding='utf-8') as f:
    FAQ_DATA = json.load(f)

def find_faq_answer(query):
    """
    Find the best-matching FAQ answer for the query.
    Returns the answer string or None if not found.
    """
    query_lower = query.lower()
    best_match = None
    best_score = 0
    for entry in FAQ_DATA:
        for kw in entry['keywords']:
            # Exact or substring match
            if kw in query_lower:
                if len(kw) > best_score:
                    best_score = len(kw)
                    best_match = entry['answer']
            # Fuzzy: allow for minor typos (Levenshtein distance <= 2)
            elif _levenshtein(kw, query_lower) <= 2:
                if len(kw) > best_score:
                    best_score = len(kw)
                    best_match = entry['answer']
    return best_match

def _levenshtein(a, b):
    """Compute Levenshtein distance between two strings (for fuzzy matching)."""
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    v0 = list(range(len(b) + 1))
    v1 = [0] * (len(b) + 1)
    for i in range(len(a)):
        v1[0] = i + 1
        for j in range(len(b)):
            cost = 0 if a[i] == b[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0, v1 = v1, v0
    return v0[len(b)] 