"""Functions to find the best hand in a given set of cards"""
from itertools import combinations
import math
from typing import List

from ballmatro.card import Card
from ballmatro.score import Score

def brute_force_optimize(cards: List[Card]) -> Score:
    """Find the best hand in a given set of cards using brute force"""
    best_score = -math.inf
    for i in range(1, len(cards) + 1):
        for hand in combinations(cards, i):
            score_info = Score(cards, list(hand))
            if score_info.score > best_score:
                best_score = score_info.score
                best_result = score_info
    return best_result
