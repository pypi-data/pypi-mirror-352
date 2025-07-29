from ballmatro.card import Card
from ballmatro.hands import StraightFlush, FourOfAKind, FullHouse, Flush, Straight, ThreeOfAKind, TwoPair, Pair, HighCard, NoPokerHand, find_hand

def test_straight_flush():
    cards = [Card('10♥'), Card('J♥'), Card('Q♥'), Card('K♥'), Card('A♥')]
    assert StraightFlush.check(cards)

def test_four_of_a_kind():
    cards = [Card('10♥'), Card('10♦'), Card('10♠'), Card('10♣')]
    assert FourOfAKind.check(cards)

def test_full_house():
    cards = [Card('10♥'), Card('10♦'), Card('10♠'), Card('K♣'), Card('K♦')]
    assert FullHouse.check(cards)

def test_flush():
    cards = [Card('2♥'), Card('4♥'), Card('6♥'), Card('8♥'), Card('10♥')]
    assert Flush.check(cards)

def test_straight():
    cards = [Card('10♥'), Card('J♦'), Card('Q♠'), Card('K♣'), Card('A♦')]
    assert Straight.check(cards)

def test_three_of_a_kind():
    cards = [Card('10♥'), Card('10♦'), Card('10♠')]
    assert ThreeOfAKind.check(cards)

def test_two_pair():
    cards = [Card('10♥'), Card('10♦'), Card('K♠'), Card('K♣')]
    assert TwoPair.check(cards)

def test_pair():
    cards = [Card('10♥'), Card('10♦')]
    assert Pair.check(cards)

def test_high_card():
    cards = [Card('A♥')]
    assert HighCard.check(cards)

def test_find_hand():
    assert find_hand([Card('10♥'), Card('J♥'), Card('Q♥'), Card('K♥'), Card('A♥')]) == StraightFlush
    assert find_hand([Card('10♥'), Card('10♦'), Card('10♠'), Card('10♣')]) == FourOfAKind
    assert find_hand([Card('10♥'), Card('10♦'), Card('10♠'), Card('K♣'), Card('K♦')]) == FullHouse
    assert find_hand([Card('2♥'), Card('4♥'), Card('6♥'), Card('8♥'), Card('10♥')]) == Flush
    assert find_hand([Card('10♥'), Card('J♦'), Card('Q♠'), Card('K♣'), Card('A♦')]) == Straight
    assert find_hand([Card('10♥'), Card('10♦'), Card('10♠')]) == ThreeOfAKind
    assert find_hand([Card('10♥'), Card('10♦'), Card('K♠'), Card('K♣')]) == TwoPair
    assert find_hand([Card('10♥'), Card('10♦')]) == Pair
    assert find_hand([Card('A♥')]) == HighCard
    assert find_hand([]) == NoPokerHand
    assert find_hand([Card("🂿 Double Double: Cards with rank 2 provide double chips")]) == NoPokerHand
