from ballmatro.card import Card, RANKS, SUITS, MODIFIERS
from ballmatro.generators import exhaustive_generator, random_generator, to_hf_dataset, generator_to_dict, int2cards
from ballmatro.score import Score
from ballmatro.hands import NoPokerHand

def test_exhaustive_generator_size1():
    # Use a small hand size for tractable test
    results = list(exhaustive_generator(1))
    # Each result is a tuple: (hand, Score)
    assert all(isinstance(hand, list) for hand, _ in results)
    assert all(isinstance(score_info, Score) for _, score_info in results)
    # Check that the number of generated hands matches the expected count
    # There are 4 suits, 13 ranks, 2 modifiers, so 4*13*3 = 156 possible cards
    assert len(results) == 156
    # Check no repetitions in the generated hands
    assert len({tuple(hand) for hand, _ in results}) == len(results)
    # Check no invalid hands
    assert all(result.hand != NoPokerHand for _, result in results)

def test_exhaustive_generator_size2():
    # Use a small hand size for tractable test
    results = list(exhaustive_generator(2))
    # Check that the number of generated hands matches the expected count
    # There are 4 suits, 13 ranks, 2 modifiers, so 4*13*3 = 156 possible cards
    # The number of combinations with replacement is (n + r - 1)
    # where n is the number of items to choose from and r is the number of items to choose
    # In this case, n = 156 and r = 2 so the number of combinations is (156 + 2 - 1) choose 2 = 156 * 157 / 2 = 12246
    assert len(results) == 12246
    # Check no repetitions in the generated hands
    assert len({tuple(hand) for hand, _ in results}) == len(results)
    # Check no invalid hands
    assert all(result.hand != NoPokerHand for _, result in results)

def test_random_generator_size4():
    results = list(random_generator(max_hand_size=4, n=100))
    assert len(results) == 100
    assert all(len(result[0]) <= 4 for result in results)

def test_random_generator_size8():
    results = list(random_generator(max_hand_size=8, n=123))
    assert len(results) == 123
    assert all(len(result[0]) <= 8 for result in results)

def test_random_generator_random_seed():
    results = list(random_generator(max_hand_size=5, n=150, seed=12345))
    results2 = list(random_generator(max_hand_size=5, n=150, seed=12345))
    assert results == results2  # Ensure reproducibility with the same seed

def test_random_generator_modifiers():
    # Test with modifiers
    results = list(random_generator(max_hand_size=1, n=100, modifiers=["+"]))
    assert len(results) == 100
    # Check that the cards have the expected modifiers
    for hand, _ in results:
        for card in hand:
            assert card.modifier in [None, "+"]

def test_generator_to_dict():
    # Generate a small dataset with a small generator
    dict_generator = generator_to_dict(exhaustive_generator(1))
    # Check that the dictionary has the expected keys
    assert "input" in dict_generator
    assert "output" in dict_generator
    assert "score" in dict_generator
    assert "hand" in dict_generator
    assert "chips" in dict_generator
    assert "multiplier" in dict_generator
    assert "remaining" in dict_generator

def test_hf_dataset():
    # Generate a Hugging Face dataset with a small generator
    dataset = to_hf_dataset(exhaustive_generator(1))
    # Check that the dataset has the expected columns
    assert "input" in dataset.column_names
    assert "output" in dataset.column_names
    assert "score" in dataset.column_names
    assert "hand" in dataset.column_names
    assert "chips" in dataset.column_names
    assert "multiplier" in dataset.column_names
    assert "remaining" in dataset.column_names

def test_int2cards():
    # Test conversion of integer to cards
    ncards = len(SUITS) * len(RANKS) * (len(MODIFIERS) + 1)

    cards = int2cards(0)
    assert len(cards) == 0

    cards = int2cards(1)
    assert len(cards) == 1
    assert cards[0] == Card("2♣")

    cards = int2cards(2)
    assert len(cards) == 1
    assert cards[0] == Card("2♦")

    cards = int2cards(5)
    assert len(cards) == 1
    assert cards[0] == Card("3♣")

    cards = int2cards(52)
    assert len(cards) == 1
    assert cards[0] == Card("A♥")

    cards = int2cards(53)
    assert len(cards) == 1
    assert cards[0] == Card("2♣+")

    cards = int2cards(ncards)
    assert len(cards) == 1
    assert cards[0] == Card("A♥x")

    cards = int2cards(ncards+1)
    assert len(cards) == 2
    assert cards[0] == Card("2♣")
    assert cards[1] == Card("2♣")

    cards = int2cards(ncards+2)
    assert len(cards) == 2
    assert cards[0] == Card("2♣")
    assert cards[1] == Card("2♦")

    cards = int2cards(2*ncards)
    assert len(cards) == 2
    assert cards[0] == Card("2♣")
    assert cards[1] == Card("A♥x")

    cards = int2cards(ncards+ncards**2)
    assert len(cards) == 2
    assert cards[0] == Card("A♥x")
    assert cards[1] == Card("A♥x")

    cards = int2cards(1+ncards+ncards**2)
    assert len(cards) == 3
    assert cards[0] == Card("2♣")
    assert cards[1] == Card("2♣")
    assert cards[2] == Card("2♣")

    # Now test with modifiers

    ncards = len(SUITS) * len(RANKS) * 2

    cards = int2cards(1, modifiers=["+"])
    assert len(cards) == 1
    assert cards[0] == Card("2♣")

    cards = int2cards(ncards)
    assert len(cards) == 1
    assert cards[0] == Card("A♥+")
