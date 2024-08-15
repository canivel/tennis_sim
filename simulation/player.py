# simulation/player.py

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum

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

class Weakness(Enum):
    FOREHAND = "forehand"
    BACKHAND = "backhand"
    SERVE = "serve"
    VOLLEY = "volley"
    MENTAL = "mental"
    PHYSICAL = "physical"

class TournamentResult(Enum):
    WINNER = "winner"
    FINALIST = "finalist"
    SEMIFINALIST = "semifinalist"
    QUARTERFINALIST = "quarterfinalist"
    FOURTH_ROUND = "fourth_round"
    THIRD_ROUND = "third_round"
    SECOND_ROUND = "second_round"
    FIRST_ROUND = "first_round"
    NOT_QUALIFIED = "not_qualified"
    INJURED = "injured"
    DID_NOT_PLAY = "did_not_play"
    DISQUALIFIED = "disqualified"

class InjurySeverity(Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
  
# We can use the same enum for strengths
Strength = Weakness    
@dataclass
class PlayerStats:
    name: str
    country: str
    serve_accuracy: float
    groundstroke_accuracy: float
    volley_accuracy: float
    speed: float
    stamina: float
    mental_strength: float
    shot_preferences: Dict[ShotType, float]
    atp_rank: int
    previous_atp_rank: int
    weaknesses: List[Weakness]
    strengths: List[Strength]
    previous_tournament_results: List[TournamentResult]
    current_injuries: Dict[str, InjurySeverity]
    previous_injuries: Dict[str, InjurySeverity]
    confidence: float = 0.5
    fatigue: float = 0.0
    stats: Dict[str, int] = field(default_factory=lambda: {
        'aces': 0,
        'double_faults': 0,
        'winners': 0,
        'unforced_errors': 0
    })
    wins_vs_opponents: Dict[str, int] = field(default_factory=dict)

    def get_wins_vs_opponent(self, opponent_name: str) -> int:
        return self.wins_vs_opponents.get(opponent_name, 0)

def create_player(name: str, country: str, stats: Dict[str, float], preferences: Dict[ShotType, float], 
                  atp_rank: int, previous_atp_rank: int, weaknesses: List[Weakness],
                  strengths: List[Strength], previous_tournament_results: List[TournamentResult],
                  current_injuries: Dict[str, InjurySeverity],
                  previous_injuries: Dict[str, InjurySeverity],
                  wins_vs_opponents: Dict[str, int] = None) -> PlayerStats:
    player = PlayerStats(
        name=name,
        country=country,
        serve_accuracy=stats['serve_accuracy'],
        groundstroke_accuracy=stats['groundstroke_accuracy'],
        volley_accuracy=stats['volley_accuracy'],
        speed=stats['speed'],
        stamina=stats['stamina'],
        mental_strength=stats['mental_strength'],
        shot_preferences=preferences,
        atp_rank=atp_rank,
        previous_atp_rank=previous_atp_rank,
        weaknesses=weaknesses,
        strengths=strengths,
        previous_tournament_results=previous_tournament_results,
        current_injuries=current_injuries,
        previous_injuries=previous_injuries
    )
    if wins_vs_opponents:
        player.wins_vs_opponents = wins_vs_opponents
    return player