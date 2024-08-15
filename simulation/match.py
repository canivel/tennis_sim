# simulation/match.py

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
from .player import PlayerStats
from .match_formats import MatchFormat

class PointOutcome(Enum):
    IN_PLAY = 0
    WINNER = 1
    FORCED_ERROR = 2
    UNFORCED_ERROR = 3
    NET = 4
    OUT = 5

class ShotType(Enum):
    SERVE = 0
    FOREHAND = 1
    BACKHAND = 2
    VOLLEY_FOREHAND = 3
    VOLLEY_BACKHAND = 4
    SMASH = 5
    SLICE_FOREHAND = 6
    SLICE_BACKHAND = 7
    DROPSHOT_FOREHAND = 8
    DROPSHOT_BACKHAND = 9

class Surface(Enum):
    HARD = 'hard'
    CLAY = 'clay'
    GRASS = 'grass'
    CARPET = 'carpet'
    
class Weather(Enum):
    SUNNY = 'sunny'
    CLOUDY = 'cloudy'
    WINDY = 'windy'
    RAINY = 'rainy'
    INDOOR = 'indoor'

@dataclass
class MatchState:
    server: int
    receiver: int
    point_score: List[str] = field(default_factory=lambda: ["0", "0"])
    game_score: List[int] = field(default_factory=lambda: [0, 0])
    set_score: List[int] = field(default_factory=lambda: [0, 0])
    match_score: List[int] = field(default_factory=lambda: [0, 0])
    current_set: int = 1
    is_tiebreak: bool = False
    is_match_tiebreak: bool = False
    player_fatigue: List[float] = field(default_factory=lambda: [0.0, 0.0])

class Match:
    def __init__(self, player1: PlayerStats, player2: PlayerStats, match_format: MatchFormat, 
                 surface: Surface, is_indoor: bool, weather: Weather, event_country: str):
        self.players = [player1, player2]
        self.match_format = match_format
        self.state = MatchState(server=0, receiver=1)
        self.point_history = []
        self.surface = surface
        self.is_indoor = is_indoor
        self.weather = weather if not is_indoor else Weather.INDOOR
        self.event_country = event_country
    
    def calculate_average_odds(self) -> Tuple[float, float]:
        # This is a simplified calculation and should be adjusted based on your specific requirements
        player1_strength = (self.players[0].serve_accuracy + self.players[0].groundstroke_accuracy) / 2
        player2_strength = (self.players[1].serve_accuracy + self.players[1].groundstroke_accuracy) / 2
        
        total_strength = player1_strength + player2_strength
        player1_win_probability = player1_strength / total_strength
        player2_win_probability = 1 - player1_win_probability
        
        # Convert probabilities to odds
        winning_odd = 1 / player1_win_probability if player1_win_probability > 0 else float('inf')
        losing_odd = 1 / player2_win_probability if player2_win_probability > 0 else float('inf')
        
        return winning_odd, losing_odd
        
    def get_current_state(self) -> Dict:
        winning_odd, losing_odd = self.calculate_average_odds()
        
        state = {
            "surface": self.surface.value,
            "is_indoor": self.is_indoor,
            "weather": self.weather.value,
            "event_country": self.event_country,
            "server": self.state.server,
            "receiver": self.state.receiver,
            "set_score_1": self.state.set_score[0],
            "set_score_2": self.state.set_score[1],
            "game_score_1": self.state.game_score[0],
            "game_score_2": self.state.game_score[1],
            "current_set": self.state.current_set,
            "is_tiebreak": self.state.is_tiebreak,
            "is_match_tiebreak": self.state.is_match_tiebreak,
            "fatigue_1": self.players[0].fatigue,
            "fatigue_2": self.players[1].fatigue,
            "player1_serve": self.players[0].serve_accuracy,
            "player2_serve": self.players[1].serve_accuracy,
            "player1_ground": self.players[0].groundstroke_accuracy,
            "player2_ground": self.players[1].groundstroke_accuracy,
            "average_winning_odd": winning_odd,
            "average_losing_odd": losing_odd,
            "player1_wins_vs_opponent": self.players[0].get_wins_vs_opponent(self.players[1].name),
            "player2_wins_vs_opponent": self.players[1].get_wins_vs_opponent(self.players[0].name)
        }
        
        # Add player stats
        for i, player in enumerate(self.players, 1):
            for stat, value in player.stats.items():
                state[f"player{i}_{stat}"] = value
        
        return state

    def update_point_score(self, winner: int):
        if self.state.is_tiebreak or self.state.is_match_tiebreak:
            self.state.point_score[winner] = str(int(self.state.point_score[winner]) + 1)
        else:
            point_mapping = {"0": "15", "15": "30", "30": "40", "40": "Game"}
            if self.state.point_score[winner] == "40" and self.state.point_score[1-winner] == "40":
                self.state.point_score[winner] = "Adv"
            elif self.state.point_score[1-winner] == "Adv":
                self.state.point_score[1-winner] = "40"
            else:
                self.state.point_score[winner] = point_mapping[self.state.point_score[winner]]

    def update_game_score(self):
        if self.state.is_tiebreak or self.state.is_match_tiebreak:
            winner = 0 if int(self.state.point_score[0]) > int(self.state.point_score[1]) else 1
        else:
            winner = self.state.point_score.index("Game")

        self.state.game_score[winner] += 1
        self.state.point_score = ["0", "0"]
        self.state.server, self.state.receiver = self.state.receiver, self.state.server
        
        if self.state.is_tiebreak:
            self.state.is_tiebreak = False
            self.state.server, self.state.receiver = self.state.receiver, self.state.server

    def is_game_over(self) -> bool:
        if self.state.is_tiebreak:
            return (int(self.state.point_score[0]) >= self.match_format.tiebreak_points and 
                    abs(int(self.state.point_score[0]) - int(self.state.point_score[1])) >= 2) or \
                   (int(self.state.point_score[1]) >= self.match_format.tiebreak_points and 
                    abs(int(self.state.point_score[0]) - int(self.state.point_score[1])) >= 2)
        elif self.state.is_match_tiebreak:
            return (int(self.state.point_score[0]) >= self.match_format.final_set_tiebreak_points and 
                    abs(int(self.state.point_score[0]) - int(self.state.point_score[1])) >= 2) or \
                   (int(self.state.point_score[1]) >= self.match_format.final_set_tiebreak_points and 
                    abs(int(self.state.point_score[0]) - int(self.state.point_score[1])) >= 2)
        else:
            return "Game" in self.state.point_score

    def is_set_over(self) -> bool:
        return (max(self.state.game_score) >= self.match_format.games_to_win_set and 
                abs(self.state.game_score[0] - self.state.game_score[1]) >= 2) or \
               (self.state.game_score[0] == self.state.game_score[1] == self.match_format.games_to_win_set - 1)

    def update_set_score(self):
        winner = 0 if self.state.game_score[0] > self.state.game_score[1] else 1
        self.state.set_score[winner] += 1
        self.state.current_set += 1
        self.state.game_score = [0, 0]
        
        if self.state.current_set == self.match_format.sets_to_win * 2 - 1 and self.match_format.final_set_tiebreak:
            self.state.is_match_tiebreak = True

    def is_match_over(self) -> bool:
        return max(self.state.set_score) >= self.match_format.sets_to_win

    def play_point(self, outcome: PointOutcome, winner: Optional[int] = None) -> None:
        if outcome != PointOutcome.IN_PLAY and winner is None:
            raise ValueError("Winner must be specified for non-IN_PLAY outcomes")

        self.point_history.append((outcome, winner))

        if outcome != PointOutcome.IN_PLAY:
            self.update_point_score(winner)

            if self.is_game_over():
                self.update_game_score()

                if self.is_set_over():
                    self.update_set_score()
                elif (self.state.game_score[0] == self.state.game_score[1] == self.match_format.games_to_win_set - 1 and
                      not self.state.is_match_tiebreak):
                    self.state.is_tiebreak = True

    def get_match_state(self) -> Dict:
        return {
            "server": self.state.server,
            "receiver": self.state.receiver,
            "point_score": self.state.point_score.copy(),
            "game_score": self.state.game_score.copy(),
            "set_score": self.state.set_score.copy(),
            "match_score": self.state.match_score.copy(),
            "current_set": self.state.current_set,
            "is_tiebreak": self.state.is_tiebreak,
            "is_match_tiebreak": self.state.is_match_tiebreak,
            "player_fatigue": self.state.player_fatigue.copy()
        }

    def get_winner(self) -> Optional[str]:
        if self.is_match_over():
            winner_index = 0 if self.state.set_score[0] > self.state.set_score[1] else 1
            return self.players[winner_index].name
        return None

    def get_score(self) -> Dict[str, List[int]]:
        return {
            "sets": self.state.set_score.copy(),
            "games": self.state.game_score.copy(),
            "points": [int(score) if score.isdigit() else 50 for score in self.state.point_score]
        }

    def get_stats(self) -> Dict[str, Dict[str, int]]:
        stats = {player.name: {"aces": 0, "double_faults": 0, "winners": 0, "unforced_errors": 0} 
                 for player in self.players}
        
        for outcome, winner in self.point_history:
            if outcome == PointOutcome.WINNER:
                stats[self.players[winner].name]["winners"] += 1
            elif outcome == PointOutcome.UNFORCED_ERROR:
                stats[self.players[1-winner].name]["unforced_errors"] += 1
        
        return stats

    def update_state(self, event):
        # Update match state based on the event
        if event.shot_outcome != PointOutcome.IN_PLAY:
            self.play_point(event.shot_outcome, event.player)
        
        # Update player fatigue and confidence
        fatigue_increase = 0.01
        confidence_change = 0.02
        if event.shot_type in [ShotType.SERVE, ShotType.SMASH]:
            fatigue_increase *= 2
        
        self.players[event.player].fatigue = min(1.0, self.players[event.player].fatigue + fatigue_increase)
        
        if event.shot_outcome in [PointOutcome.WINNER, PointOutcome.FORCED_ERROR]:
            self.players[event.player].confidence = min(1.0, self.players[event.player].confidence + confidence_change)
            self.players[1 - event.player].confidence = max(0.0, self.players[1 - event.player].confidence - confidence_change)
        elif event.shot_outcome in [PointOutcome.UNFORCED_ERROR, PointOutcome.NET, PointOutcome.OUT]:
            self.players[event.player].confidence = max(0.0, self.players[event.player].confidence - confidence_change)
            self.players[1 - event.player].confidence = min(1.0, self.players[1 - event.player].confidence + confidence_change)
        
        # Slightly reduce fatigue for the non-hitting player
        other_player = 1 - event.player
        self.players[other_player].fatigue = max(0.0, self.players[other_player].fatigue - 0.005)

    def is_point_over(self) -> bool:
        return len(self.point_history) > 0 and self.point_history[-1][0] != PointOutcome.IN_PLAY

    def end_point(self):
        # Update statistics
        last_point = self.point_history[-1]
        winner = last_point[1]
        outcome = last_point[0]
        
        if outcome == PointOutcome.WINNER:
            self.players[winner].stats['winners'] += 1
        elif outcome == PointOutcome.UNFORCED_ERROR:
            self.players[1-winner].stats['unforced_errors'] += 1
        elif outcome == PointOutcome.NET or outcome == PointOutcome.OUT:
            if self.state.server == 1-winner:  # If the server lost the point
                self.players[1-winner].stats['double_faults'] += 1
            else:
                self.players[1-winner].stats['unforced_errors'] += 1
        
        # Check if this point ended a game
        if self.is_game_over():
            self.end_game()

    def end_game(self):
        # Update game score
        self.update_game_score()
        
        # Check if this game ended a set
        if self.is_set_over():
            self.end_set()
        elif (self.state.game_score[0] == self.state.game_score[1] == self.match_format.games_to_win_set - 1 and
              not self.state.is_match_tiebreak):
            self.state.is_tiebreak = True

    def end_set(self):
        # Update set score
        self.update_set_score()
        
        # Reset game score
        self.state.game_score = [0, 0]
        
        # Check if this set ended the match
        if self.is_match_over():
            self.end_match()
        elif (self.state.current_set == self.match_format.sets_to_win * 2 - 1 and 
              self.match_format.final_set_tiebreak):
            self.state.is_match_tiebreak = True

    def end_match(self):
        winner = self.get_winner()
        print(f"Match ended. Winner: {winner}")
        print(f"Final score: {self.get_score()}")
        print(f"Match statistics: {self.get_stats()}")