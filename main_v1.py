import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

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

class CourtLocation(Enum):
    LEFT_NEAR = 0
    CENTER_NEAR = 1
    RIGHT_NEAR = 2
    LEFT_MIDDLE = 3
    CENTER_MIDDLE = 4
    RIGHT_MIDDLE = 5
    LEFT_FAR = 6
    CENTER_FAR = 7
    RIGHT_FAR = 8

class PointOutcome(Enum):
    IN_PLAY = 0
    WINNER = 1
    FORCED_ERROR = 2
    UNFORCED_ERROR = 3
    NET = 4
    OUT = 5

@dataclass
class Ball:
    speed: float  # in km/h
    spin: float  # in rpm
    location: CourtLocation

@dataclass
class Shot:
    shot_type: ShotType
    ball: Ball

@dataclass
class PlayerStats:
    name: str
    serve_accuracy: float
    groundstroke_accuracy: float
    volley_accuracy: float
    speed: float
    stamina: float
    mental_strength: float
    shot_preferences: dict = field(default_factory=lambda: {
        ShotType.SERVE: 0,  # This should always be 0 as serves are handled separately
        ShotType.FOREHAND: 0.3,
        ShotType.BACKHAND: 0.3,
        ShotType.VOLLEY_FOREHAND: 0.05,
        ShotType.VOLLEY_BACKHAND: 0.05,
        ShotType.SMASH: 0.05,
        ShotType.SLICE_FOREHAND: 0.1,
        ShotType.SLICE_BACKHAND: 0.1,
        ShotType.DROPSHOT_FOREHAND: 0.025,
        ShotType.DROPSHOT_BACKHAND: 0.025
    })

    def __post_init__(self):
        # Ensure all shot types are in the preferences
        for shot_type in ShotType:
            if shot_type not in self.shot_preferences:
                self.shot_preferences[shot_type] = 0.0
        
        # Normalize preferences to ensure they sum to 1
        total = sum(self.shot_preferences.values())
        if total > 0:
            for key in self.shot_preferences:
                self.shot_preferences[key] /= total

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
    last_n_shots: List[Shot] = field(default_factory=list)
    player_fatigue: List[float] = field(default_factory=lambda: [0.0, 0.0])

@dataclass
class MatchFormat:
    sets_to_win: int
    games_to_win_set: int
    tiebreak_points: int
    final_set_tiebreak: bool

@dataclass
class PointRecord:
    set_number: int
    server: int
    receiver: int
    shots: List[Shot]
    outcome: PointOutcome
    winner: Optional[int]

@dataclass
class MatchRecord:
    points: List[PointRecord] = field(default_factory=list)
    games: List[Tuple[int, int, int]] = field(default_factory=list)
    sets: List[Tuple[int, int, int]] = field(default_factory=list)
    winner: Optional[int] = None

class MLModel:
    def __init__(self, n_estimators=100, max_depth=10):
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.X_train = []
        self.y_train = []

    def prepare_features(self, match_state: MatchState, player_stats: List[PlayerStats]) -> np.array:
        features = []
        for i in range(2):
            features.extend([
                player_stats[i].serve_accuracy,
                player_stats[i].groundstroke_accuracy,
                player_stats[i].volley_accuracy,
                player_stats[i].speed,
                player_stats[i].stamina,
                player_stats[i].mental_strength,
                match_state.player_fatigue[i]
            ])
        features.extend([
            match_state.current_set, 
            match_state.set_score[0], match_state.set_score[1],
            match_state.game_score[0], match_state.game_score[1]
        ])
        
        # Pad or truncate last_n_shots to always have 5 shots
        shots = match_state.last_n_shots + [None] * (5 - len(match_state.last_n_shots))
        for shot in shots[:5]:
            if shot:
                features.extend([shot.shot_type.value, shot.ball.speed, shot.ball.spin, shot.ball.location.value])
            else:
                features.extend([0, 0, 0, 0])  # Padding for missing shots
        
        return np.array(features).reshape(1, -1)

    def train(self, X, y):
        self.X_train = X
        self.y_train = y
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict(self, X):
        if not self.is_trained:
            return None
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def update(self, X, y):
        self.X_train = np.vstack((self.X_train, X))
        self.y_train = np.append(self.y_train, y)
        self.scaler.fit(self.X_train)
        X_scaled = self.scaler.transform(self.X_train)
        self.model.fit(X_scaled, self.y_train)
        
class OddsCalculator:
    @staticmethod
    def calculate_odds(probabilities: List[float]) -> List[float]:
        return [1 / p for p in probabilities]

    @staticmethod
    def adjust_odds(current_odds: List[float], prediction: np.array, adjustment_factor: float = 0.1) -> List[float]:
        current_probs = [1 / odd for odd in current_odds]
        adjusted_probs = [(1 - adjustment_factor) * curr + adjustment_factor * pred 
                          for curr, pred in zip(current_probs, prediction[0])]
        return OddsCalculator.calculate_odds(adjusted_probs)

class TennisMatch:
    def __init__(self, player1: PlayerStats, player2: PlayerStats, match_format: MatchFormat):
        self.players = [player1, player2]
        self.match_format = match_format
        self.state = MatchState(server=0, receiver=1)
        self.record = MatchRecord()
        self.ml_model = MLModel()
        self.current_odds = {
            'match_winner': [2.0, 2.0],  # Initial even odds
            'set_winner': [2.0, 2.0],
            'game_winner': [2.0, 2.0]
        }
        self.initialize_ml_model()

    def initialize_ml_model(self):
        # Create some basic training data
        X = []
        y = []
        for _ in range(100):  # Generate 100 random data points
            match_state = MatchState(server=random.randint(0, 1), receiver=1-random.randint(0, 1))
            match_state.set_score = [random.randint(0, 2), random.randint(0, 2)]
            match_state.game_score = [random.randint(0, 5), random.randint(0, 5)]
            match_state.player_fatigue = [random.random(), random.random()]
            X.append(self.ml_model.prepare_features(match_state, self.players)[0])
            y.append(random.randint(0, 1))  # Random winner
        
        self.ml_model.train(np.array(X), np.array(y))

    def play_shot(self, player: int, prev_shot: Optional[Shot]) -> Tuple[Shot, PointOutcome]:
        player_stats = self.players[player]
        
        # Determine shot type based on player preferences and previous shot
        if prev_shot is None:
            shot_type = ShotType.SERVE
        else:
            shot_types = list(ShotType)
            weights = [player_stats.shot_preferences[st] for st in shot_types]
            shot_type = random.choices(shot_types, weights=weights)[0]
        
        # Determine ball parameters
        speed = random.gauss(player_stats.speed * 0.7, 10)  # Adjust as needed
        spin = random.gauss(2000, 500)  # Adjust as needed
        location = random.choice(list(CourtLocation))
        
        ball = Ball(speed, spin, location)
        shot = Shot(shot_type, ball)
        
        # Determine shot outcome
        accuracy = self.get_shot_accuracy(player, shot_type)
        outcome_roll = random.random()
        
        if outcome_roll < accuracy * 0.8:
            outcome = PointOutcome.IN_PLAY
        elif outcome_roll < accuracy * 0.9:
            outcome = PointOutcome.WINNER
        elif outcome_roll < accuracy * 0.95:
            outcome = PointOutcome.FORCED_ERROR
        elif outcome_roll < accuracy * 0.98:
            outcome = PointOutcome.UNFORCED_ERROR
        elif outcome_roll < accuracy * 0.99:
            outcome = PointOutcome.NET
        else:
            outcome = PointOutcome.OUT

        # Update fatigue
        self.update_fatigue(player, shot)
        
        # Update last_n_shots (let's say we keep track of last 5 shots)
        self.state.last_n_shots.append(shot)
        if len(self.state.last_n_shots) > 5:
            self.state.last_n_shots.pop(0)
        
        return shot, outcome

    def get_shot_accuracy(self, player: int, shot_type: ShotType) -> float:
        player_stats = self.players[player]
        if shot_type == ShotType.SERVE:
            return player_stats.serve_accuracy
        elif shot_type in [ShotType.VOLLEY_FOREHAND, ShotType.VOLLEY_BACKHAND]:
            return player_stats.volley_accuracy
        else:
            return player_stats.groundstroke_accuracy

    def update_fatigue(self, player: int, shot: Shot):
        fatigue_increase = 0.01  # Base fatigue increase per shot
        if shot.shot_type in [ShotType.SMASH, ShotType.SERVE]:
            fatigue_increase *= 2
        self.state.player_fatigue[player] += fatigue_increase
        # Reduce fatigue slightly for the non-hitting player
        self.state.player_fatigue[1-player] = max(0, self.state.player_fatigue[1-player] - 0.005)

    def play_point(self) -> PointRecord:
        current_player = self.state.server
        shots = []
        
        while True:
            prev_shot = shots[-1] if shots else None
            shot, outcome = self.play_shot(current_player, prev_shot)
            shots.append(shot)
            
            if outcome != PointOutcome.IN_PLAY:
                winner = current_player if outcome in [PointOutcome.WINNER, PointOutcome.FORCED_ERROR] else 1 - current_player
                point_record = PointRecord(self.state.current_set, self.state.server, self.state.receiver, shots, outcome, winner)
                self.update_ml_model(winner)
                return point_record
            
            current_player = 1 - current_player

    def update_ml_model(self, winner):
        features = self.ml_model.prepare_features(self.state, self.players)
        self.ml_model.update(features, [winner])
        prediction = self.ml_model.predict(features)
        
        if prediction is not None:
            self.current_odds['match_winner'] = OddsCalculator.adjust_odds(
                self.current_odds['match_winner'], prediction
            )
            self.current_odds['set_winner'] = OddsCalculator.adjust_odds(
                self.current_odds['set_winner'], prediction
            )
            self.current_odds['game_winner'] = OddsCalculator.adjust_odds(
                self.current_odds['game_winner'], prediction
            )

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
            if "Game" in self.state.point_score:
                winner = self.state.point_score.index("Game")
            elif "Adv" in self.state.point_score:
                winner = self.state.point_score.index("Adv")
            else:
                point_values = {"0": 0, "15": 1, "30": 2, "40": 3}
                winner = 0 if point_values[self.state.point_score[0]] > point_values[self.state.point_score[1]] else 1

        self.state.game_score[winner] += 1
        self.record.games.append((self.state.current_set, winner, self.state.game_score[winner]))
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
            return int(self.state.point_score[0]) >= 10 and abs(int(self.state.point_score[0]) - int(self.state.point_score[1])) >= 2 or \
                   int(self.state.point_score[1]) >= 10 and abs(int(self.state.point_score[0]) - int(self.state.point_score[1])) >= 2
        else:
            return "Game" in self.state.point_score or "Adv" in self.state.point_score

    def is_set_over(self) -> bool:
        return (max(self.state.game_score) >= self.match_format.games_to_win_set and 
                abs(self.state.game_score[0] - self.state.game_score[1]) >= 2) or \
               (self.state.game_score[0] == self.state.game_score[1] == self.match_format.games_to_win_set - 1)

    def update_set_score(self):
        winner = 0 if self.state.game_score[0] > self.state.game_score[1] else 1
        self.state.set_score[winner] += 1
        self.record.sets.append((self.state.current_set, winner, max(self.state.game_score)))
        self.state.current_set += 1
        self.state.game_score = [0, 0]
        
        if self.state.current_set == self.match_format.sets_to_win * 2 - 1 and self.match_format.final_set_tiebreak:
            self.state.is_match_tiebreak = True

    def is_match_over(self) -> bool:
        return max(self.state.set_score) >= self.match_format.sets_to_win

    def play_match(self):
        while not self.is_match_over():
            point_record = self.play_point()
            self.record.points.append(point_record)
            self.update_point_score(point_record.winner)

            if self.is_game_over():
                self.update_game_score()

                if self.is_set_over():
                    self.update_set_score()
                elif (self.state.game_score[0] == self.state.game_score[1] == self.match_format.games_to_win_set - 1 and
                      not self.state.is_match_tiebreak):
                    self.state.is_tiebreak = True

        self.record.winner = 0 if self.state.set_score[0] > self.state.set_score[1] else 1

    def print_match_summary(self):
        print(f"Match winner: {self.players[self.record.winner].name}")
        print("Set scores:")
        for set_num, winner, games in self.record.sets:
            print(f"Set {set_num}: {self.players[winner].name} won with {games} games")
        print("Final match score:")
        print(f"{self.players[0].name}: {self.state.set_score[0]} sets")
        print(f"{self.players[1].name}: {self.state.set_score[1]} sets")
        
        # Print statistics
        stats = self.calculate_match_statistics()
        print("\nMatch Statistics:")
        for player in [0, 1]:
            print(f"\n{self.players[player].name}:")
            print(f"  Winners: {stats['winners'][player]}")
            print(f"  Forced Errors: {stats['forced_errors'][player]}")
            print(f"  Unforced Errors: {stats['unforced_errors'][player]}")
            print(f"  Aces: {stats['aces'][player]}")
            print(f"  Double Faults: {stats['double_faults'][player]}")
        
        print("\nFinal Odds:")
        for market, odds in self.current_odds.items():
            print(f"  {market}: {self.players[0].name}: {odds[0]:.2f}, {self.players[1].name}: {odds[1]:.2f}")

    def calculate_match_statistics(self):
        stats = {
            'winners': [0, 0],
            'forced_errors': [0, 0],
            'unforced_errors': [0, 0],
            'aces': [0, 0],
            'double_faults': [0, 0]
        }
        
        for point in self.record.points:
            if point.outcome == PointOutcome.WINNER:
                stats['winners'][point.winner] += 1
            elif point.outcome == PointOutcome.FORCED_ERROR:
                stats['forced_errors'][1 - point.winner] += 1
            elif point.outcome == PointOutcome.UNFORCED_ERROR:
                stats['unforced_errors'][1 - point.winner] += 1
            
            if point.shots[0].shot_type == ShotType.SERVE:
                if point.outcome == PointOutcome.WINNER and len(point.shots) == 1:
                    stats['aces'][point.server] += 1
                elif point.outcome in [PointOutcome.NET, PointOutcome.OUT] and len(point.shots) == 1:
                    stats['double_faults'][point.server] += 1
        
        return stats
    
# Example usage
if __name__ == "__main__":
    player1 = PlayerStats(
        name="Roger",
        serve_accuracy=0.65,
        groundstroke_accuracy=0.75,
        volley_accuracy=0.70,
        speed=85,
        stamina=90,
        mental_strength=95,
        shot_preferences={
            ShotType.FOREHAND: 0.4,
            ShotType.BACKHAND: 0.3,
            ShotType.SLICE_FOREHAND: 0.1,
            ShotType.SLICE_BACKHAND: 0.1,
            ShotType.VOLLEY_FOREHAND: 0.05,
            ShotType.VOLLEY_BACKHAND: 0.03,
            ShotType.SMASH: 0.02
        }
    )
    
    player2 = PlayerStats(
        name="Novak",
        serve_accuracy=0.62,
        groundstroke_accuracy=0.78,
        volley_accuracy=0.68,
        speed=90,
        stamina=95,
        mental_strength=98,
        shot_preferences={
            ShotType.FOREHAND: 0.35,
            ShotType.BACKHAND: 0.35,
            ShotType.SLICE_FOREHAND: 0.08,
            ShotType.SLICE_BACKHAND: 0.12,
            ShotType.VOLLEY_FOREHAND: 0.04,
            ShotType.VOLLEY_BACKHAND: 0.04,
            ShotType.SMASH: 0.02
        }
    )
    
    match_format = MatchFormat(sets_to_win=2, games_to_win_set=6, tiebreak_points=7, final_set_tiebreak=True)
    
    match = TennisMatch(player1, player2, match_format)
    
    # Print initial odds
    print("Initial Odds:")
    for market, odds in match.current_odds.items():
        print(f"  {market}: {match.players[0].name}: {odds[0]:.2f}, {match.players[1].name}: {odds[1]:.2f}")
    
    match.play_match()
    match.print_match_summary()