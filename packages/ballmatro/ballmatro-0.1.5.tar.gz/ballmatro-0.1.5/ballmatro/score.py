"""Functions to score ballmatro hands"""
from dataclasses import dataclass
from datasets import Dataset
from typing import List, Tuple, Union


from ballmatro.card import Card, parse_card_list
from ballmatro.hands import find_hand, NoPokerHand, InvalidPlay


CHIPS_PER_RANK = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11}


@dataclass
class Score:
    """Class that represents the score and details of a played hand"""
    input: Union[List[Card], str]  # Cards that were available for play
    played: Union[List[Card], str]  # Cards played in the hand

    def __post_init__(self):
        try:
            # Parse the input and played cards
            if isinstance(self.input, str):
                self.input = parse_card_list(self.input)
            if isinstance(self.played, str):
                self.played = parse_card_list(self.played)
            # Find cards that were not played
            self.remaining = self._remaining_cards(self.input, self.played)
            # Find the hand that was played
            self.hand = find_hand(self.played)
        except ValueError:
            self.remaining = None
            self.hand = InvalidPlay
        # Score the played cards
        self._score_played()

    def __repr__(self):
        """Return a string representation of the score info"""
        return f"Score(input={self.input}, played={self.played}, remaining={self.remaining}, hand={self.hand.__name__}, chips={self.chips}, multiplier={self.multiplier}, score={self.score})"
    
    def _remaining_cards(self, available: List[Card], played: List[Card]) -> List[Card]:
        """Returns the remaining (not played) cards after playing a hand"""
        remaining = available.copy()
        for card in played:
            # Check if the card is available
            if card not in remaining:
                raise ValueError(f"Impossible play: card {card} not in available cards")
            # Remove the card from the remaining cards
            remaining.remove(card)
        return remaining

    def _score_played(self):
        """Given a list of played cards, find their ballmatro score

        A score of 0 is attained when the hand is not recognized or the list of played cards contains cards that are not available.
        """
        # Check if the played cards were really available
        if self.remaining is None or self.hand in [NoPokerHand, InvalidPlay]:
            self.chips = 0
            self.multiplier = 0
            self.score = 0
            return

        # Start scoring using the chips and multiplier of the hand type
        self.chips, self.multiplier = self.hand.chips, self.hand.multiplier
        # Now iterate over the cards in the order played, and score each card individually
        for card in self.played:
            self.chips, self.multiplier = _score_card(card, self.chips, self.multiplier)

        self.score = self.chips * self.multiplier

def _score_card(card: Card, chips: int, multiplier: int) -> Tuple[int, int]:
    """Applies the scoring of a single card to the current chips and multiplier"""
    # Add the chips of the card rank to the current chips
    chips += CHIPS_PER_RANK.get(card.rank, 0)
    # Apply modifiers
    if card.modifier == "+":
        chips += 30
    elif card.modifier == "x":
        multiplier += 4
    return chips, multiplier

@dataclass
class ScoreDataset:
    """Class that represents the scores obtained over a whole Ballmatro dataset"""
    dataset: Dataset  # Dataset containing the hands and optimal plays
    plays: List[Union[str, List[Card]]]  # List of plays (hands) carried out for the dataset
    scores: List[Score] = None  # Detailed Score objects for each play
    total_score: int = 0  # Total score of the plays over the whole dataset
    normalized_score: float = 0.0  # Normalized score [0,1] of the plays over the whole dataset
    invalid_hands: int = 0  # Number of invalid hands played
    normalized_invalid_hands: float = 0.0  # Fraction of invalid hands played [0,1]

    def __post_init__(self):
        # Check inputs
        if len(self.dataset) != len(self.plays):
            raise ValueError("Dataset and plays must have the same length")
        # Score the plays
        self.scores = [Score(input, played) for input, played in zip(self.dataset["input"], self.plays)]
        # Compute statistics
        self.total_score = sum(score.score for score in self.scores)
        self.normalized_score = self.total_score / sum(self.dataset["score"])
        self.invalid_hands = sum(1 for score in self.scores if score.hand in [NoPokerHand, InvalidPlay])
        self.normalized_invalid_hands = self.invalid_hands / len(self.scores)

    def __repr__(self):
        """Return a string representation of the score info"""
        return f"ScoreDataset(total_score={self.total_score}, normalized_score={self.normalized_score}, invalid_hands={self.invalid_hands}, normalized_invalid_hands={self.normalized_invalid_hands})"
