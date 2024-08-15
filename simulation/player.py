# simulation/player.py

from dataclasses import dataclass, field
from typing import Dict
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

@dataclass
class PlayerStats:
    name: str
    serve_accuracy: float
    groundstroke_accuracy: float
    volley_accuracy: float
    speed: float
    stamina: float
    mental_strength: float
    shot_preferences: Dict[ShotType, float]
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

def create_player(name: str, stats: Dict[str, float], preferences: Dict[ShotType, float], 
                  wins_vs_opponents: Dict[str, int] = None) -> PlayerStats:
    player = PlayerStats(
        name=name,
        serve_accuracy=stats['serve_accuracy'],
        groundstroke_accuracy=stats['groundstroke_accuracy'],
        volley_accuracy=stats['volley_accuracy'],
        speed=stats['speed'],
        stamina=stats['stamina'],
        mental_strength=stats['mental_strength'],
        shot_preferences=preferences
    )
    if wins_vs_opponents:
        player.wins_vs_opponents = wins_vs_opponents
    return player