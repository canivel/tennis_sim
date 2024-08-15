# simulation/engine.py

from typing import List
from .events import TennisEvent, ShotType, ShotOutcome
from .match import Match
from models.ml_model import MLModel
from models.odds_calculator import OddsCalculator

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
            # Always start with a serve
            serve_event = self.generate_serve_event()
            self.process_event(serve_event)
            
            # Continue with rally until point is over
            while not self.match.is_point_over():
                rally_event = self.generate_rally_event()
                self.process_event(rally_event)
            
            # Point is over, update match state
            self.match.end_point()

        print("\nMatch ended.")
        self.print_final_results()
    
    def generate_serve_event(self) -> TennisEvent:
        import random
        
        player = self.match.state.server
        shot_type = ShotType.SERVE_1ST
        
        serve_in_prob = self.match.players[player].serve_accuracy
        if random.random() < serve_in_prob:
            shot_outcome = random.choices(
                [ShotOutcome.ACE, ShotOutcome.IN_PLAY],
                weights=[0.05, 0.95]
            )[0]
        else:
            shot_outcome = ShotOutcome.OUT
            
            # If first serve is out, generate second serve
            if shot_outcome == ShotOutcome.OUT:
                shot_type = ShotType.SERVE_2ND
                serve_in_prob = self.match.players[player].serve_accuracy * 1.1  # Slightly higher accuracy for second serve
                if random.random() < serve_in_prob:
                    shot_outcome = ShotOutcome.IN_PLAY
                else:
                    shot_outcome = ShotOutcome.DOUBLE_FAULT
        
        ball_speed = random.uniform(100, 140)  # Serve speeds are typically higher
        ball_spin = random.uniform(1000, 3000)
        
        return TennisEvent(player, shot_type, shot_outcome, ball_speed, ball_spin)

    def generate_rally_event(self) -> TennisEvent:
        import random
        
        player = random.choice([0, 1])
        shot_type = random.choice([st for st in ShotType if st not in [ShotType.SERVE_1ST, ShotType.SERVE_2ND]])
        shot_outcome = random.choices(
            [ShotOutcome.IN_PLAY, ShotOutcome.WINNER, ShotOutcome.FORCED_ERROR, ShotOutcome.UNFORCED_ERROR],
            weights=[0.7, 0.1, 0.1, 0.1]
        )[0]
        
        ball_speed = random.uniform(60, 120)
        ball_spin = random.uniform(1000, 4000)
        
        return TennisEvent(player, shot_type, shot_outcome, ball_speed, ball_spin)

    def process_event(self, event: TennisEvent):
        self.match.update_state(event)
        self.recent_events.append(event)
        if len(self.recent_events) > 10:
            self.recent_events.pop(0)

        self.update_odds()

        print(f"\nEvent: {self.format_event(event)}")
        print(f"Updated odds: {self.format_odds(self.current_odds)}")
        print(f"Current score: {self.match.get_score()}")

    def generate_next_event(self) -> TennisEvent:
        import random
        
        # Determine if this is a serve or a regular shot
        is_serve = self.match.state.point_score == ["0", "0"]
        
        player = self.match.state.server if is_serve else random.choice([0, 1])
        
        if is_serve:
            shot_type = ShotType.SERVE
            # Adjust probabilities for serve outcomes
            serve_in_prob = self.match.players[player].serve_accuracy
            if random.random() < serve_in_prob:
                shot_outcome = random.choices(
                    [ShotOutcome.IN_PLAY, ShotOutcome.WINNER],
                    weights=[0.9, 0.1]
                )[0]
            else:
                shot_outcome = ShotOutcome.OUT
        else:
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
        winner = self.match.get_winner()
        score = self.match.get_score()
        stats = self.match.get_stats()

        print(f"Winner: {winner}")
        print(f"Final score: {score}")
        print("Match statistics:")
        for player, player_stats in stats.items():
            print(f"  {player}:")
            for stat, value in player_stats.items():
                print(f"    {stat}: {value}")
        print(f"Final odds: {self.format_odds(self.current_odds)}")
        
    def get_match_results(self):
        winner = self.match.get_winner()
        score = self.match.get_score()
        stats = self.match.get_stats()
        
        return {
            'winner': winner,
            'score': score,
            'stats': stats,
            'final_odds': self.format_odds(self.current_odds)
        }