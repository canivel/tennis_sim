# simulation/engine.py

from typing import List, Dict
from .events import TennisEvent, ShotType, ShotOutcome
from .match import Match
from models.ml_model import MLModel
from models.odds_calculator import OddsCalculator
import random

class SimulationEngine:
    def __init__(self, player1, player2, match_format, surface, is_indoor, weather, event_country, ml_model: MLModel, odds_calculator: OddsCalculator):
        self.match = Match(player1, player2, match_format, surface, is_indoor, weather, event_country)
        self.ml_model = ml_model
        self.odds_calculator = odds_calculator
        self.current_odds = {
            'match_winner': [2.0, 2.0],
            'set_winner': [2.0, 2.0],
            'game_winner': [2.0, 2.0]
        }
        self.recent_events: List[TennisEvent] = []

    def run_simulation(self):
        print("Match starting...")
        print(f"Initial odds: {self.format_odds(self.current_odds)}")

        while not self.match.is_match_over():
            event = self.generate_next_event()
            self.process_event(event)

        print("\nMatch ended.")
        self.print_final_results()

    def process_event(self, event: TennisEvent):
        self.match.update_state(event)
        self.match.set_current_shot_info(event.shot_type, event.ball_speed, event.ball_spin)
        
        self.recent_events.append(event)
        if len(self.recent_events) > 10:
            self.recent_events.pop(0)

        self.update_odds()

        print(f"\nEvent: {self.format_event(event)}")
        print(f"Updated odds: {self.format_odds(self.current_odds)}")
        print(f"Current score: {self.match.get_score()}")

    def generate_next_event(self) -> TennisEvent:
        player = random.choice([0, 1])
        shot_type = random.choice(list(ShotType))
        shot_outcome = random.choice(list(ShotOutcome))
        ball_speed = random.uniform(60, 160)
        ball_spin = random.uniform(1000, 4000)
        return TennisEvent(player, shot_type, shot_outcome, ball_speed, ball_spin)

    def update_odds(self):
        match_state = self.match.get_current_state()
        prediction = self.ml_model.predict(match_state)
        self.current_odds = self.odds_calculator.calculate(prediction, match_state, self.recent_events)

    def format_event(self, event: TennisEvent) -> str:
        player_name = self.match.players[event.player].name
        return f"{player_name} - {event.shot_type.name}, {event.shot_outcome.name}, {event.ball_speed:.1f} mph, {event.ball_spin:.0f} rpm"

    def format_odds(self, odds: dict) -> str:
        return {k: [f"{v[0]:.2f}", f"{v[1]:.2f}"] for k, v in odds.items()}

    def print_final_results(self):
        results = self.get_match_results()
        print(f"Winner: {results['winner']}")
        print(f"Final score: {results['score']}")
        print("Match statistics:")
        for player, player_stats in results['stats'].items():
            print(f"  {player}:")
            for stat, value in player_stats.items():
                print(f"    {stat}: {value}")
        print(f"Final odds: {self.format_odds(results['final_odds'])}")

    def get_match_results(self) -> Dict:
        return {
            "winner": self.match.get_winner(),
            "score": self.match.get_score(),
            "stats": self.match.get_stats(),
            "final_odds": self.current_odds
        }