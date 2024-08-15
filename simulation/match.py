# simulation/match.py

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
from .player import PlayerStats
from .match_formats import MatchFormat
from .events import TennisEvent, ShotType, ShotOutcome
class PointOutcome(Enum):
    IN_PLAY = 0
    WINNER = 1
    FORCED_ERROR = 2
    UNFORCED_ERROR = 3
    NET = 4
    OUT = 5

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
        self.current_shot_type = ShotType.SERVE_1ST  # Initialize with SERVE
        self.current_ball_speed = 0.0  # Initialize with 0
        self.current_ball_spin = 0.0  # Initialize with 0
        self.previous_event: Optional[TennisEvent] = None
        self.current_point_events: List[TennisEvent] = []
    
    def set_current_shot_type(self, shot_type: ShotType):
        self.current_shot_type = shot_type
    
    def set_current_shot_info(self, shot_type: ShotType, ball_speed: float, ball_spin: float):
        self.current_shot_type = shot_type
        self.current_ball_speed = ball_speed
        self.current_ball_spin = ball_spin

    
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
            "point_score_1": self.state.point_score[0],
            "point_score_2": self.state.point_score[1],
            "current_set": self.state.current_set,
            "is_tiebreak": self.state.is_tiebreak,
            "is_match_tiebreak": self.state.is_match_tiebreak,
            "fatigue_1": self.players[0].fatigue,
            "fatigue_2": self.players[1].fatigue,
            "player1_serve_accuracy": self.players[0].serve_accuracy,
            "player2_serve_accuracy": self.players[1].serve_accuracy,
            "player1_ground_accuracy": self.players[0].groundstroke_accuracy,
            "player2_ground_accuracy": self.players[1].groundstroke_accuracy,
            "player1_volley_accuracy": self.players[0].volley_accuracy,
            "player2_volley_accuracy": self.players[1].volley_accuracy,
            "player1_atp_rank": self.players[0].atp_rank,
            "player2_atp_rank": self.players[1].atp_rank,
            "player1_previous_atp_rank": self.players[0].previous_atp_rank,
            "player2_previous_atp_rank": self.players[1].previous_atp_rank,
            "player1_weakness": ','.join([w.value for w in self.players[0].weaknesses]),
            "player2_weakness": ','.join([w.value for w in self.players[1].weaknesses]),
            "player1_strength": ','.join([s.value for s in self.players[0].strengths]),
            "player2_strength": ','.join([s.value for s in self.players[1].strengths]),
            "player1_previous_tournament_results": ','.join([r.value for r in self.players[0].previous_tournament_results]),
            "player2_previous_tournament_results": ','.join([r.value for r in self.players[1].previous_tournament_results]),
            "player1_country": self.players[0].country,
            "player2_country": self.players[1].country,
            "player1_current_injuries": ','.join([f"{k}:{v.value}" for k, v in self.players[0].current_injuries.items()]),
            "player2_current_injuries": ','.join([f"{k}:{v.value}" for k, v in self.players[1].current_injuries.items()]),
            "player1_previous_injuries": ','.join([f"{k}:{v.value}" for k, v in self.players[0].previous_injuries.items()]),
            "player2_previous_injuries": ','.join([f"{k}:{v.value}" for k, v in self.players[1].previous_injuries.items()]),
            "current_shot_type": self.current_shot_type.value,
            "current_ball_speed": self.current_ball_speed,
            "current_ball_spin": self.current_ball_spin,
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
            point_mapping = {"0": "15", "15": "30", "30": "40"}
            loser = 1 - winner
            
            if self.state.point_score[winner] == "40":
                if self.state.point_score[loser] == "40":
                    self.state.point_score[winner] = "Adv"
                else:
                    self.state.point_score[winner] = "Game"
            elif self.state.point_score[winner] == "Adv":
                self.state.point_score[winner] = "Game"
            elif self.state.point_score[loser] == "Adv":
                self.state.point_score[loser] = "40"
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

    def play_point(self, outcome: ShotOutcome, winner: int):
        if outcome != ShotOutcome.IN_PLAY:
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
            "sets": self.state.set_score,
            "games": self.state.game_score,
            "points": self.state.point_score
        }

    def get_stats(self) -> Dict[str, Dict[str, int]]:
        return {player.name: player.stats for player in self.players}

    def update_stats(self, event: TennisEvent):
        player = self.players[event.player]
        opponent = self.players[1 - event.player]
        
        if event.shot_type in [ShotType.SERVE_1ST, ShotType.SERVE_2ND]:
            if event.shot_outcome == ShotOutcome.ACE:
                player.stats['aces'] += 1
                player.stats['winners'] += 1
            elif event.shot_outcome == ShotOutcome.DOUBLE_FAULT:
                player.stats['double_faults'] += 1
                opponent.stats['winners'] += 1
        
        if event.shot_outcome == ShotOutcome.WINNER:
            player.stats['winners'] += 1
        elif event.shot_outcome == ShotOutcome.UNFORCED_ERROR:
            player.stats['unforced_errors'] += 1
        elif event.shot_outcome == ShotOutcome.FORCED_ERROR:
            opponent.stats['winners'] += 1

    def update_state(self, event: TennisEvent):
        self.current_point_events.append(event)
        
        if event.shot_outcome not in [ShotOutcome.IN_PLAY, ShotOutcome.OUT]:
            winner = event.player if event.shot_outcome in [ShotOutcome.ACE, ShotOutcome.WINNER, ShotOutcome.FORCED_ERROR] else 1 - event.player
            self.play_point(event.shot_outcome, winner)
            self.update_stats(event)
    
    def is_point_over(self) -> bool:
        return len(self.current_point_events) > 0 and self.current_point_events[-1].shot_outcome not in [ShotOutcome.IN_PLAY, ShotOutcome.OUT]

    def get_winner(self) -> str:
        return self.players[self.state.match_score.index(max(self.state.match_score))].name

    def get_score(self) -> Dict:
        return {
            "sets": self.state.set_score,
            "games": self.state.game_score,
            "points": self.state.point_score
        }

    def get_stats(self) -> Dict:
        return {player.name: player.stats for player in self.players}
    
    def end_point(self):
        if self.is_point_over():
            self.current_point_events = []
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