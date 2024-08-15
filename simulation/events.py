from dataclasses import dataclass
from enum import Enum

class ShotType(Enum):
    SERVE = 1
    FOREHAND = 2
    BACKHAND = 3
    VOLLEY = 4
    SMASH = 5

class ShotOutcome(Enum):
    IN_PLAY = 1
    WINNER = 2
    FORCED_ERROR = 3
    UNFORCED_ERROR = 4
    NET = 5
    OUT = 6

@dataclass
class TennisEvent:
    player: int  # 0 or 1
    shot_type: ShotType
    shot_outcome: ShotOutcome
    ball_speed: float
    ball_spin: float
    is_decisive_point: bool = False  # e.g., break point, set point, match point