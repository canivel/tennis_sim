# models/odds_calculator.py

from typing import List, Dict
from simulation.events import TennisEvent, ShotOutcome
import math

class OddsCalculator:
    def calculate(self, prediction: float, match_state: Dict, recent_events: List[TennisEvent]) -> Dict[str, List[float]]:
        # Base odds from the ML model prediction
        base_odds = self.convert_probability_to_odds(prediction)
        
        # Adjust odds based on recent events
        momentum_factor = self.calculate_momentum_factor(recent_events)
        adjusted_odds = self.adjust_odds(base_odds, momentum_factor)
        
        return {
            'match_winner': adjusted_odds,
            'set_winner': self.calculate_set_odds(adjusted_odds, match_state),
            'game_winner': self.calculate_game_odds(adjusted_odds, match_state)
        }
    
    def convert_probability_to_odds(self, probability: float) -> List[float]:
        odds_player1 = 1 / probability if probability > 0 else 100
        odds_player2 = 1 / (1 - probability) if probability < 1 else 100
        return [odds_player1, odds_player2]
    
    def calculate_momentum_factor(self, recent_events: List[TennisEvent]) -> float:
        momentum = 0
        for event in recent_events:
            if event.shot_outcome == ShotOutcome.WINNER:
                momentum += 0.02 if event.is_decisive_point else 0.01
            elif event.shot_outcome in [ShotOutcome.UNFORCED_ERROR, ShotOutcome.NET, ShotOutcome.OUT]:
                momentum -= 0.02 if event.is_decisive_point else 0.01
        return 1 + momentum
    
    def adjust_odds(self, odds: List[float], factor: float) -> List[float]:
        return [odds[0] * factor, odds[1] / factor]
    
    def calculate_set_odds(self, match_odds: List[float], match_state: Dict) -> List[float]:
        set_score = match_state['set_score']
        game_score = match_state['game_score']
        sets_to_win = match_state['sets_to_win']
        
        # Convert match odds to set win probability
        set_win_prob = self.odds_to_probability(match_odds[0])
        
        # Adjust for current set score
        set_difference = set_score[0] - set_score[1]
        if set_difference > 0:
            set_win_prob = set_win_prob + (1 - set_win_prob) * (set_difference / sets_to_win)
        elif set_difference < 0:
            set_win_prob = set_win_prob * (1 + set_difference / sets_to_win)
        
        # Adjust for current game score in the ongoing set
        game_difference = game_score[0] - game_score[1]
        set_win_prob = set_win_prob + (1 - set_win_prob) * (game_difference / 12)  # Assuming 6 games to win a set
        
        # Ensure probability is between 0 and 1
        set_win_prob = max(0, min(1, set_win_prob))
        
        return self.convert_probability_to_odds(set_win_prob)
    
    def calculate_game_odds(self, match_odds: List[float], match_state: Dict) -> List[float]:
        point_score = match_state['point_score']
        serving_player = match_state['server']
        
        # Convert match odds to game win probability
        game_win_prob = self.odds_to_probability(match_odds[0])
        
        # Adjust for serving player
        if serving_player == 1:  # If player 2 is serving
            game_win_prob = 1 - game_win_prob
        
        # Adjust for current point score
        point_values = {'0': 0, '15': 1, '30': 2, '40': 3, 'Ad': 4}
        point_difference = point_values[point_score[0]] - point_values[point_score[1]]
        
        # Use logistic function to adjust game win probability based on point difference
        game_win_prob = 1 / (1 + math.exp(-point_difference))
        
        # Ensure probability is between 0 and 1
        game_win_prob = max(0, min(1, game_win_prob))
        
        game_odds = self.convert_probability_to_odds(game_win_prob)
        
        # If player 2 is serving, swap the odds
        return game_odds if serving_player == 0 else game_odds[::-1]
    
    def odds_to_probability(self, odds: float) -> float:
        return 1 / odds if odds > 0 else 0