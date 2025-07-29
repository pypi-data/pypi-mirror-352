"""Class that represents a card, and associated functions"""
from dataclasses import dataclass
from typing import List
import re

SUITS = ["♣", "♦", "♠", "♥"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
MODIFIERS = [
    "+",  # Bonus card: +30 chips
    "x",  # Mult card: +4 multiplier
]
JOKER = "🂿"

@dataclass(frozen=True)
class Card:
    """Class that represents a card"""
    txt: str  # Text representation of the card

    def __post_init__(self):
        """Validate the card text representation"""
        if not isinstance(self.txt, str):
            raise TypeError("Card text must be a string")
        if self.suit is None and not self.is_joker:
            raise ValueError("Card must contain a suit or be a joker")
        if self.rank is None and not self.is_joker:
            raise ValueError("Card must contain a rank or be a joker")
        # For non-joker cards, check correct format with a regex
        if not self.is_joker:
            if not re.match(r"^(10|[2-9]|J|Q|K|A)[♣♦♠♥]([+x])?$", self.txt):
                raise ValueError(f"Invalid card format: {self.txt}")
        else:
            # For joker cards, check the format
            if not re.match(r"^🂿[^:]+:[^:]+$", self.txt):
                raise ValueError(f"Invalid joker format: {self.txt}")

    @property
    def suit(self) -> str:
        """Return the suit of the card, or None if the card has no suit"""
        for suit in SUITS:
            if suit in self.txt:
                return suit
        return None

    @property
    def rank(self) -> str:
        """Return the rank of the card, or None if the card has no rank"""
        match = re.match(r"([2-9]|10|J|Q|K|A)", self.txt)
        if match is not None:
            return match.group(0)
        return None
    
    @property
    def rank_numeric(self) -> int:
        """Return the numeric value of the rank of the card, or None if the card has no rank"""
        return RANKS.index(self.rank) if self.rank is not None else None

    @property
    def modifier(self) -> str:
        """Return the modifier of the card, or None if the card has no modifier"""
        for modifier in MODIFIERS:
            if modifier in self.txt[-1]:
                return modifier
        return None
    
    @property
    def is_joker(self) -> bool:
        """Return True if the card is a joker, False otherwise"""
        return self.txt[0] == JOKER
    
    @property
    def joker_name(self) -> str:
        """Return the name of the joker card, or None if the card is not a joker"""
        if self.is_joker:
            return self.txt[1:].split(":")[0].strip()
        return None

    @property
    def joker_rule(self) -> str:
        """Return the joker rule of the card, or None if the card is not a joker"""
        if self.is_joker:
            return self.txt[1:].split(":")[1].strip()
        return None

    def __repr__(self) -> str:
        """Return a string representation of the card"""
        return self.txt

def parse_card_list(txt: str) -> List[Card]:
    """Transforms a list of cards in text form into a list of Card objects.

    Example input: "[♣2, ♠3, ♥4]"
    Example output: [Card("♣2"), Card("♠3"), Card("♥4")]

    Raises a ValueError if the input is not a valid card list format, or if any card is invalid.
    """
    # Remove opening and closing brackets
    if not (txt.startswith("[") and txt.endswith("]")):
        raise ValueError("Input must start with '[' and end with ']'")
    txt = txt[1:-1]
    # Remove blanks
    txt = txt.replace(" ","")
    # No cards border case
    if len(txt) == 0:
        return []
    # Split by cards
    return [Card(cardtxt) for cardtxt in txt.split(",")]
