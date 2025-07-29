"""baLLMatro possible hands and functions to identify them"""
from collections import Counter
from dataclasses import dataclass
from typing import List

from ballmatro.card import Card

@dataclass
class PokerHand:
    """Abstract class with general methods for Poker Hands scoring"""
    ncards: int  # Number of cards that make up the hand
    chips: int  # Value in chips of the hand
    multiplier: int  # Multiplier for the chips value

    @classmethod
    def check_ncards(cls, hand: List[Card]) -> bool:
        return len(hand) == cls.ncards
    
    @classmethod
    def check(cls, hand: List[Card]) -> bool:
        """Check if the hand is of the specific type"""
        if not cls.check_ncards(hand): return False
        return cls.check_specific(hand)
    
    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a specific hand"""
        pass
    
class StraightFlush(PokerHand):
    """Straight Flush: Five cards in sequence, all of the same suit"""
    ncards = 5
    chips = 100
    multiplier = 8

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a Straight Flush"""
        return Straight.check_specific(hand) and Flush.check_specific(hand)
        
class FourOfAKind(PokerHand):
    """Four of a Kind: Four cards of the same rank"""
    ncards = 4
    chips = 60
    multiplier = 7

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for Four of a Kind"""
        return len(set([card.rank for card in hand])) == 1
    
class FullHouse(PokerHand):
    """Full House: Three cards of one rank and two cards of another rank"""
    ncards = 5
    chips = 40
    multiplier = 4

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a Full House"""
        return list(Counter([card.rank for card in hand]).values()) == [3, 2]

class Flush(PokerHand):
    """Flush: Five cards of the same suit"""
    ncards = 5
    chips = 35
    multiplier = 4

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a Flush"""
        return len(set([card.suit for card in hand])) == 1
    
class Straight(PokerHand):
    """Straight: Five cards in sequence"""
    ncards = 5
    chips = 30
    multiplier = 4

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a Straight"""
        srt = sorted([card.rank_numeric for card in hand])
        for c1, c2 in zip(srt[:-1], srt[1:]):
            if c2 - c1 != 1:
                return False
        return True
    
class ThreeOfAKind(PokerHand):
    """Three of a Kind: Three cards of the same rank"""
    ncards = 3
    chips = 30
    multiplier = 3

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for Three of a Kind"""
        return len(set([card.rank for card in hand])) == 1
    
class TwoPair(PokerHand):
    """Two Pair: Two cards of one rank and two cards of another rank"""
    ncards = 4
    chips = 20
    multiplier = 2

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for Two Pair"""
        return list(Counter([card.rank for card in hand]).values()) == [2, 2]

class Pair(PokerHand):
    """Pair: Two cards of the same rank"""
    ncards = 2
    chips = 10
    multiplier = 2

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a Pair"""
        return len(set([card.rank for card in hand])) == 1
    
class HighCard(PokerHand):
    """High Card: The highest card in the hand"""
    ncards = 1
    chips = 5
    multiplier = 1

    @classmethod
    def check_specific(cls, hand: List[Card]) -> bool:
        """Check the hand for a High Card"""
        # Just check that the card is not a joker
        return not hand[0].is_joker
    
class NoPokerHand(PokerHand):
    """Special PokerHand to represent the played cards form no poker hand"""
    ncards = 0
    chips = 0
    multiplier = 0

class InvalidPlay(PokerHand):
    """Special PokerHand to represent a played set of cards that are wrongly formatted or invalid"""
    ncards = 0
    chips = 0
    multiplier = 0

POKER_HANDS = [StraightFlush, FourOfAKind, FullHouse, Flush, Straight, ThreeOfAKind, TwoPair, Pair, HighCard]

def find_hand(hand: List[Card]) -> PokerHand:
    """Find which poker hand has been played. Returns the PokerHand object or None if no hand is found"""
    for poker_hand in POKER_HANDS:
        if poker_hand.check(hand):
            return poker_hand
    return NoPokerHand
