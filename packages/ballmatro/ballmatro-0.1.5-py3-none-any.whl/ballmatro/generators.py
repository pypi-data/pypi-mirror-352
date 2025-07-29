"""Functions to generate datasets for LLM training with ballmatro hands"""
import random
from datasets import Dataset
from itertools import combinations_with_replacement
from typing import List, Tuple, Generator, Dict, Any

from ballmatro.card import Card, SUITS, RANKS, MODIFIERS
from ballmatro.optimizer import brute_force_optimize
from ballmatro.score import Score

def exhaustive_generator(max_hand_size: int, seed: int = 42) -> Generator[Tuple[List[Card], Score], None, None]:
    """Generator functions for a dataset with all possible hands of a given size
    and their optimal plays using brute force optimization.
    Args:
        max_hand_size (int): The size of the hands to generate.
    Returns:
        List[Tuple[List[Card], Score]]: A list of tuples, each containing a hand and its optimal play in the form of a Score object.
    """
    # Generate all possible cards
    cards = [Card(f"{rank}{suit}{modifier}") for suit in SUITS for rank in RANKS for modifier in [""] + MODIFIERS]
    
    # Generate all combinations of the given size
    for input in combinations_with_replacement(cards, max_hand_size):
        # Find optimal play for this input
        optimal_play = brute_force_optimize(list(input))
        yield list(input), optimal_play

def random_generator(max_hand_size: int, n: int, modifiers: List[str] = None, seed: int = 42) -> Generator[Tuple[List[Card], Score], None, None]:
    """Generator function for a dataset with random hands and their optimal plays.

    Args:
        max_hand_size (int): The maximum size of the hands to generate.
        n (int): The number of random hands to generate.
        modifiers (List[str]): A list of modifiers to apply to the cards.

    Yields:
        Tuple[List[Card], Score]: A tuple containing a hand and its optimal play in the form of a Score object.
    """
    # Set the random seed for reproducibility
    random.seed(seed)
    # Ensure modifiers are set correctly
    modifiers = _get_modifiers(modifiers)
    # Find maximum ID for list of cards of size at most max_hand_size
    ncards = len(RANKS) * len(SUITS) * len(modifiers)
    max_id = sum([ncards**i for i in range(1, max_hand_size + 1)])
    for _ in range(n):
        # Generate a random hand
        input = int2cards(random.randint(1, max_id))
        # Find optimal play for this input
        optimal_play = brute_force_optimize(input)
        yield input, optimal_play

GENERATION_ALGORITHMS = {
    "exhaustive": exhaustive_generator,
    "random": random_generator,
}

def generator_to_dict(generator: Generator[Tuple[List[Card], Score], None, None]) -> Dict[str, List[Any]]:
    """Convert a generator of tuples to a generator of dictionaries.

    Args:
        generator (Generator[Tuple[List[Card], Score]]): A generator that yields tuples of input cards and their corresponding Score.

    Returns:
        Dict[str, List[Any]]: A dictionary where each key corresponds to a field in the Score object.
    """
    # Get all the data into memory
    data = list(generator)
    # Create a dictionary with the data
    dict_data = {
        "input": [str(cards) for cards, _ in data],
        "output": [str(score.played) for _, score in data],
        "score": [score.score for _, score in data],
        "hand": [score.hand.__name__ for _, score in data],
        "chips": [score.chips for _, score in data],
        "multiplier": [score.multiplier for _, score in data],
        "remaining": [str(score.remaining) for _, score in data],
    }
    return dict_data

def to_hf_dataset(generator: Generator[Tuple[List[Card], Score], None, None]) -> Dataset:
    """Convert a dataset generator to a Hugging Face dataset format.
    
    Args:
        generator (Generator[Tuple[List[Card], Score]]): A generator that yields tuples of input cards and their corresponding Score.
    
    Returns:
        Dataset: A Hugging Face dataset containing the generated data.
    """
    # Create a Hugging Face dataset from the generator
    return Dataset.from_dict(generator_to_dict(generator))

def int2cards(i: int, modifiers: List[str] = None) -> List[Card]:
    """Map from the space of integers to the space of all possible lists of cards.

    Useful for generating random datasets from a list of random integers.

    0: empty list of cards
    [1, ncards]: all possible single cards
    [1+ncards, ncards+ncards**2]: all possible pairs of cards
    [1+ncards+ncards**2, ncards+ncards**2+ncards**3]: all possible triplets of cards
    ... and so on.

    Args:
        i (int): non-negative integer to convert.
        modifiers (List[str], optional): A list of modifiers to apply to the cards. Defaults to None, which uses the global MODIFIERS.
            An empty modifier is always included.

    Returns:
        List[Card]: A list of Card objects representing the integer.
    """
    if i < 0:
        raise ValueError("Input integer must be non-negative")
    modifiers = _get_modifiers(modifiers)
    ncards = len(RANKS) * len(SUITS) * len(modifiers)

    # Find number of cards in the list to be generated
    lenlist = 0
    while i - ncards**lenlist >= 0:
        i -= ncards**lenlist
        lenlist += 1

    # Generate the list of cards
    cards = []
    for _ in range(lenlist):
        cards.append(_int2card(i % ncards, modifiers))
        i //= ncards
    return list(reversed(cards))

def _int2card(i: int, modifiers: List[str]) -> Card:
    """Map from the space of integers to the space of all possible cards.

    Useful for generating a random card from a random integer..

    Args:
        i (int): non-negative integer to convert from 0 to total number of possible cards (minus 1).

    Returns:
        Card: A Card object representing the integer.
    """
    if i < 0:
        raise ValueError("Input integer must be non-negative")
    ncards = len(RANKS) * len(SUITS) * len(modifiers)
    if i > ncards:
        raise ValueError(f"Input integer {i} exceeds maximum value {ncards-1}")

    suit = SUITS[i % len(SUITS)]
    rank = RANKS[(i // len(SUITS)) % len(RANKS)]
    modifier = modifiers[(i // (len(SUITS) * len(RANKS))) % len(modifiers)]

    return Card(f"{rank}{suit}{modifier}")

def _get_modifiers(modifiers: List[str] = None) -> List[str]:
    """Get the list of modifiers, ensuring the empty modifier is included."""
    if modifiers is None:
        return [""] + MODIFIERS  # Include empty modifier by default
    else:
        if "" not in modifiers:
            return [""] + modifiers
        return modifiers
