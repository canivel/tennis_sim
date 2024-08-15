# tests/test_odds_calculator.py

import pytest
from models.odds_calculator import OddsCalculator
from simulation.events import TennisEvent, ShotType, ShotOutcome

@pytest.fixture
def odds_calculator():
    return OddsCalculator()

def test_convert_probability_to_odds(odds_calculator):
    assert odds_calculator.convert_probability_to_odds(0.5) == [2.0, 2.0]
    assert odds_calculator.convert_probability_to_odds(0.75) == [1.3333333333333333, 4.0]

def test_calculate_momentum_factor(odds_calculator):
    events = [
        TennisEvent(player=0, shot_type=ShotType.FOREHAND, shot_outcome=ShotOutcome.WINNER, ball_speed=100, ball_spin=2000, is_decisive_point=True),
        TennisEvent(player=0, shot_type=ShotType.BACKHAND, shot_outcome=ShotOutcome.UNFORCED_ERROR, ball_speed=90, ball_spin=1800),
    ]
    assert odds_calculator.calculate_momentum_factor(events) == 1.01  # 0.02 - 0.01

def test_calculate_set_odds(odds_calculator):
    match_odds = [1.5, 2.5]
    match_state = {
        'set_score': [1, 0],
        'game_score': [3, 2],
        'sets_to_win': 2
    }
    set_odds = odds_calculator.calculate_set_odds(match_odds, match_state)
    assert set_odds[0] < match_odds[0]  # Player 1 should be more likely to win the set

def test_calculate_game_odds(odds_calculator):
    match_odds = [1.5, 2.5]
    match_state = {
        'point_score': ['30', '15'],
        'server': 0
    }
    game_odds = odds_calculator.calculate_game_odds(match_odds, match_state)
    assert game_odds[0] < match_odds[0]  # Server (Player 1) should be more likely to win the game

def test_calculate(odds_calculator):
    prediction = 0.6
    match_state = {
        'set_score': [1, 1],
        'game_score': [2, 2],
        'point_score': ['0', '0'],
        'server': 1,
        'sets_to_win': 2
    }
    recent_events = [
        TennisEvent(player=0, shot_type=ShotType.FOREHAND, shot_outcome=ShotOutcome.WINNER, ball_speed=100, ball_spin=2000),
        TennisEvent(player=1, shot_type=ShotType.BACKHAND, shot_outcome=ShotOutcome.UNFORCED_ERROR, ball_speed=90, ball_spin=1800),
    ]
    odds = odds_calculator.calculate(prediction, match_state, recent_events)
    assert 'match_winner' in odds
    assert 'set_winner' in odds
    assert 'game_winner' in odds
    assert all(len(o) == 2 for o in odds.values())  # Each should have odds for both players