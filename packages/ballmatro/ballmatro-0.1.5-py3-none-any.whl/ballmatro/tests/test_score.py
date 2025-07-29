from ballmatro.card import Card
from ballmatro.hands import InvalidPlay
from ballmatro.score import Score, _score_card, ScoreDataset
from datasets import Dataset

def test_score_invalid_hand():
    available = [Card(txt="2♥"), Card(txt="3♦"), Card(txt="A♠")]
    played = [Card(txt="2♥"), Card(txt="A♠")]
    assert Score(available, played).score == 0

def test_score_unavailable_card():
    available = [Card(txt="2♥"), Card(txt="3♦"), Card(txt="A♠")]
    played = [Card(txt="2♥"), Card(txt="K♠")]
    assert Score(available, played).score == 0  # Card not available

def test_score_high_card():
    available = [Card(txt="2♥"), Card(txt="3♦"), Card(txt="A♠")]
    played = [Card(txt="3♦")]
    assert Score(available, played).score == 8

def test_score_pair():
    available = [Card(txt="3♥"), Card(txt="3♦"), Card(txt="A♠")]
    played = [Card(txt="3♥"), Card(txt="3♦")]
    assert Score(available, played).score == 32

def test_score_two_pair():
    available = played = [Card(txt="3♥"), Card(txt="3♦"), Card(txt="A♠"), Card(txt="A♦")]
    assert Score(available, played).score == 96

def test_score_three_of_a_kind():
    available = [Card(txt="3♥"), Card(txt="3♦"), Card(txt="3♠"), Card(txt="A♦")]
    played = [Card(txt="3♥"), Card(txt="3♦"), Card(txt="3♠")]
    assert Score(available, played).score == 117

def test_score_straight():
    available = played = [Card(txt="2♥"), Card(txt="3♦"), Card(txt="4♠"), Card(txt="5♦"), Card(txt="6♠")]
    assert Score(available, played).score == 200

def test_score_flush():
    available = played = [Card(txt="2♥"), Card(txt="3♥"), Card(txt="5♥"), Card(txt="8♥"), Card(txt="J♥")]
    assert Score(available, played).score == 252

def test_score_full_house():
    available = played = [Card(txt="3♥"), Card(txt="3♦"), Card(txt="3♠"), Card(txt="A♦"), Card(txt="A♠")]
    assert Score(available, played).score == 284

def test_score_four_of_a_kind():
    available = played = [Card(txt="3♥"), Card(txt="3♦"), Card(txt="3♠"), Card(txt="3♣")]
    assert Score(available, played).score == 504

def test_score_straight_flush():
    available = played = [Card(txt="2♥"), Card(txt="3♥"), Card(txt="4♥"), Card(txt="5♥"), Card(txt="6♥")]
    assert Score(available, played).score == 960

def test_score_card_two_hearts():
    card = Card(txt="2♥")
    chips, multiplier = _score_card(card, 0, 1)
    assert (chips, multiplier) == (2, 1)

def test_score_card_bonus():
    card = Card(txt="A♠+")
    chips, multiplier = _score_card(card, 0, 1)
    assert (chips, multiplier) == (41, 1)

def test_score_card_mult():
    card = Card(txt="K♠x")
    chips, multiplier = _score_card(card, 0, 1)
    assert (chips, multiplier) == (10, 5)

def test_score_string_input():
    """Test Score with string inputs for available and played cards."""
    available = "[2♥,3♦,A♠]"
    played = "[3♦]"
    score = Score(available, played)
    assert score.score == 8
    assert score.hand.__name__ == "HighCard"
    assert score.remaining == [Card(txt="2♥"), Card(txt="A♠")]

def test_scoredataset_all_valid():
    data = {
        "input": ["[3♥,3♦]", "[2♥,3♦]"],
        "score": [32, 8],
    }
    ds = Dataset.from_dict(data)
    plays = [
        [Card("3♥"), Card("3♦")],  # valid pair
        [Card("3♦")],              # high card
    ]
    score_dataset = ScoreDataset(dataset=ds, plays=plays)
    assert score_dataset.total_score == 32 + 8
    assert score_dataset.normalized_score == 1.0
    assert score_dataset.invalid_hands == 0
    assert score_dataset.normalized_invalid_hands == 0.0

def test_scoredataset_with_invalid_play():
    data = {
        "input": ["[3♥,3♦]"],
        "score": [32],
    }
    ds = Dataset.from_dict(data)
    plays = [
        [Card("A♠")],  # not available, should be invalid
    ]
    score_dataset = ScoreDataset(dataset=ds, plays=plays)
    assert score_dataset.total_score == 0
    assert score_dataset.normalized_score == 0.0
    assert score_dataset.invalid_hands == 1
    assert score_dataset.normalized_invalid_hands == 1.0
    assert score_dataset.scores[0].hand == InvalidPlay

def test_scoredataset_mixed_valid_invalid():
    data = {
        "input": ["[3♥,3♦]", "[2♥,3♦]"],
        "score": [32, 8],
    }
    ds = Dataset.from_dict(data)
    plays = [
        [Card("3♥"), Card("3♦")],  # valid
        [Card("A♠")],              # invalid
    ]
    score_dataset = ScoreDataset(dataset=ds, plays=plays)
    assert score_dataset.total_score == 32
    assert score_dataset.invalid_hands == 1
    assert score_dataset.normalized_invalid_hands == 0.5
    assert score_dataset.normalized_score == 32/40
    assert score_dataset.scores[1].hand == InvalidPlay

def test_scoredataset_strings():
    """Test ScoreDataset with string inputs for plays."""
    data = {
        "input": ["[3♥,3♦]", "[2♥,3♦]"],
        "score": [32, 8],
    }
    ds = Dataset.from_dict(data)
    plays = [
        "[3♥,3♦]",  # valid pair
        "[3♦]"      # high card
    ]
    score_dataset = ScoreDataset(dataset=ds, plays=plays)
    assert score_dataset.total_score == 32 + 8
    assert score_dataset.normalized_score == 1.0
    assert score_dataset.invalid_hands == 0
    assert score_dataset.normalized_invalid_hands == 0.0
