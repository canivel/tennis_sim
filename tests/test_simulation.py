# tests/test_simulation.py

import pytest
from simulation.engine import SimulationEngine
from simulation.player import create_player, ShotType
from simulation.match_formats import create_match_format
from models.ml_model import MLModel
from models.odds_calculator import OddsCalculator

@pytest.fixture
def simulation_engine():
    player1 = create_player(
        name="Player1",
        stats={
            'serve_accuracy': 0.65,
            'groundstroke_accuracy': 0.75,
            'volley_accuracy': 0.70,
            'speed': 85,
            'stamina': 90,
            'mental_strength': 95
        },
        preferences={
            ShotType.FOREHAND: 0.4,
            ShotType.BACKHAND: 0.3,
            ShotType.SLICE_FOREHAND: 0.1,
            ShotType.SLICE_BACKHAND: 0.1,
            ShotType.VOLLEY_FOREHAND: 0.05,
            ShotType.VOLLEY_BACKHAND: 0.03,
            ShotType.SMASH: 0.02
        }
    )
    player2 = create_player(
        name="Player2",
        stats={
            'serve_accuracy': 0.62,
            'groundstroke_accuracy': 0.78,
            'volley_accuracy': 0.68,
            'speed': 90,
            'stamina': 95,
            'mental_strength': 98
        },
        preferences={
            ShotType.FOREHAND: 0.35,
            ShotType.BACKHAND: 0.35,
            ShotType.SLICE_FOREHAND: 0.08,
            ShotType.SLICE_BACKHAND: 0.12,
            ShotType.VOLLEY_FOREHAND: 0.04,
            ShotType.VOLLEY_BACKHAND: 0.04,
            ShotType.SMASH: 0.02
        }
    )
    match_format = create_match_format('grand_slam')
    ml_model = MLModel('path/to/test/model.joblib')  # You might need to create a test model
    odds_calculator = OddsCalculator()
    return SimulationEngine(player1, player2, match_format, ml_model, odds_calculator)

def test_process_event(simulation_engine):
    initial_odds = simulation_engine.current_odds.copy()
    event = simulation_engine.generate_next_event()
    simulation_engine.process_event(event)
    assert simulation_engine.recent_events[-1] == event
    assert simulation_engine.current_odds != initial_odds  # Odds should have changed

def test_run_simulation(simulation_engine):
    results = simulation_engine.run_simulation()
    assert 'winner' in results
    assert 'score' in results
    assert 'stats' in results
    assert 'final_odds' in results
    assert simulation_engine.match.is_match_over()

def test_generate_next_event(simulation_engine):
    event = simulation_engine.generate_next_event()
    assert event.player in [0, 1]
    assert event.shot_type in ShotType
    assert event.shot_outcome in ShotOutcome
    assert 60 <= event.ball_speed <= 160
    assert 1000 <= event.ball_spin <= 4000

def test_update_player_stats(simulation_engine):
    initial_confidence = simulation_engine.match.players[0].confidence
    initial_fatigue = simulation_engine.match.players[0].fatigue
    event = simulation_engine.generate_next_event()
    simulation_engine.update_player_stats(event)
    assert simulation_engine.match.players[0].confidence != initial_confidence
    assert simulation_engine.match.players[0].fatigue > initial_fatigue