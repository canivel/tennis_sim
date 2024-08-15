# simulation/engine.py

from typing import List
from .events import TennisEvent, ShotType, ShotOutcome
from .match import Match, Surface, Weather
from .player import PlayerStats
from .match_formats import MatchFormat
from models.ml_model import MLModel
from models.odds_calculator import OddsCalculator

class SimulationEngine:
    def __init__(self, player1: PlayerStats, player2: PlayerStats, match_format: MatchFormat, 
                 surface: Surface, is_indoor: bool, weather: Weather, event_country: str,
                 ml_model: MLModel, odds_calculator: OddsCalculator):
        self.match = Match(player1, player2, match_format, surface, is_indoor, weather, event_country)
        self.ml_model = ml_model
        self.odds_calculator = odds_calculator
        self.current_odds = {
            'match_winner': [2.0, 2.0],  # Initial even odds
            'set_winner': [2.0, 2.0],
            'game_winner': [2.0, 2.0]
        }
        self.recent_events = []
        
    def process_event(self, event: TennisEvent):
        # Update match state based on the event
        self.match.update_state(event)
        
        # Update recent events
        self.recent_events.append(event)
        if len(self.recent_events) > 10:  # Keep only the last 10 events
            self.recent_events.pop(0)
        
        # Update player statistics based on the event
        self.update_player_stats(event)
        
        # Recalculate odds
        self.update_odds()
        
        # Check if the point, game, set, or match has ended
        self.check_match_progress()
    
    def update_player_stats(self, event: TennisEvent):
        player = self.match.players[event.player]
        
        # Update relevant player statistics based on the event
        if event.shot_outcome == ShotOutcome.WINNER:
            player.confidence += 0.05
        elif event.shot_outcome in [ShotOutcome.UNFORCED_ERROR, ShotOutcome.NET, ShotOutcome.OUT]:
            player.confidence -= 0.05
        
        # Limit confidence to a range of 0-1
        player.confidence = max(0, min(1, player.confidence))
        
        # Update fatigue
        player.fatigue += 0.01
        if event.shot_type in [ShotType.SMASH, ShotType.SERVE]:
            player.fatigue += 0.01
        
        # Limit fatigue to a range of 0-1
        player.fatigue = min(1, player.fatigue)
    
    def update_odds(self):
        features = self.match.get_current_state()
        
        # Add any additional features that the ML model might need
        features.update({
            'recent_events': [event.shot_outcome.value for event in self.recent_events[-5:]]  # Last 5 events
        })
        
        # Ensure all required features are present
        required_features = [
            'set_score_1', 'set_score_2', 'game_score_1', 'game_score_2',
            'player1_serve', 'player2_serve', 'player1_ground', 'player2_ground',
            'fatigue_1', 'fatigue_2', 'average_winning_odd', 'average_losing_odd'
        ]
        
        for feature in required_features:
            if feature not in features:
                raise ValueError(f"Missing required feature: {feature}")
        
        prediction = self.ml_model.predict(features)
        self.current_odds = self.odds_calculator.calculate(prediction, features, self.recent_events)

    
    def prepare_features(self):
        features = self.match.get_current_state()
        features.update({
            'player1_confidence': self.match.players[0].confidence,
            'player2_confidence': self.match.players[1].confidence,
            'player1_fatigue': self.match.players[0].fatigue,
            'player2_fatigue': self.match.players[1].fatigue,
            'recent_events': [event.shot_outcome.value for event in self.recent_events],
        })
        return features
    
    def check_match_progress(self):
        if self.match.is_point_over():  # Assume these methods exist in Match class
            self.match.end_point()
        if self.match.is_game_over():
            self.match.end_game()
        if self.match.is_set_over():
            self.match.end_set()
        if self.match.is_match_over():  # Changed from is_match_ended to is_match_over
            self.match.end_match()
    
    def run_simulation(self):
        while not self.match.is_match_over():  # Changed from is_match_ended to is_match_over
            event = self.generate_next_event()
            self.process_event(event)
        return self.get_match_results()
    
    def generate_next_event(self):
        # This method should generate the next event based on the current match state
        # It can use probabilities influenced by player stats, match situation, etc.
        # For now, we'll use a placeholder implementation
        import random
        player = random.choice([0, 1])
        shot_type = random.choice(list(ShotType))
        shot_outcome = random.choice(list(ShotOutcome))
        ball_speed = random.uniform(60, 160)
        ball_spin = random.uniform(1000, 4000)
        return TennisEvent(player, shot_type, shot_outcome, ball_speed, ball_spin)
    
    def get_match_results(self):
        return {
            'winner': self.match.get_winner(),
            'score': self.match.get_score(),
            'stats': self.match.get_stats(),
            'final_odds': self.current_odds
        }