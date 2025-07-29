"""Tests for the card module."""
from ballmatro.card import Card, parse_card_list

def test_card_suit():
    card = Card("10♠")
    assert card.suit == "♠"
    card = Card("A♥")
    assert card.suit == "♥"
    card = Card("🂿 Double Double: Cards with rank 2 provide double chips")
    assert card.suit is None

def test_card_rank():
    card = Card("10♠")
    assert card.rank == "10"
    card = Card("A♥")
    assert card.rank == "A"
    card = Card("🂿 Double Double: Cards with rank 2 provide double chips")
    assert card.rank is None

def test_card_modifier():
    card = Card("10♠+")
    assert card.modifier == "+"
    card = Card("A♥x")
    assert card.modifier == "x"
    card = Card("Q♦")
    assert card.modifier is None

def test_card_is_joker():
    card = Card("🂿 Diamond Crack: Cards from the ♦ suit cannot be used in the hand")
    assert card.is_joker is True
    card = Card("10♠")
    assert card.is_joker is False

def test_card_joker_rule():
    card = Card("🂿 Oblique: Straights cannot be played")
    assert card.joker_rule == "Straights cannot be played"
    card = Card("10♠")
    assert card.joker_rule is None

def test_card_joker_name():
    card = Card("🂿 Double Double: Cards with rank 2 provide double chips")
    assert card.joker_name == "Double Double"
    card = Card("10♠")
    assert card.joker_name is None

def test_parse_card_list_basic():
    cards = parse_card_list("[2♣,3♠,4♥]")
    assert cards == [Card("2♣"), Card("3♠"), Card("4♥")]

def test_parse_card_list_with_spaces():
    cards = parse_card_list("[ 2♣ , 3♠ , 4♥ ]")
    assert cards == [Card("2♣"), Card("3♠"), Card("4♥")]

def test_parse_card_list_single_card():
    cards = parse_card_list("[A♦]")
    assert cards == [Card("A♦")]

def test_parse_card_list_empty():
    cards = parse_card_list("[]")
    assert cards == []
