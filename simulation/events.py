from dataclasses import dataclass
from enum import Enum

class ShotType(Enum):
    SERVE_1ST = 1
    SERVE_2ND = 2
    FOREHAND = 3
    BACKHAND = 4
    VOLLEY_FOREHAND = 5
    VOLLEY_BACKHAND = 6
    SMASH = 7
    SLICE_FOREHAND = 8
    SLICE_BACKHAND = 9
    DROPSHOT_FOREHAND = 10
    DROPSHOT_BACKHAND = 11

class ShotOutcome(Enum):
    ACE = 1
    DOUBLE_FAULT = 2
    IN_PLAY = 3
    WINNER = 4
    FORCED_ERROR = 5
    UNFORCED_ERROR = 6
    NET = 7
    OUT = 8

@dataclass
class TennisEvent:
    player: int  # 0 or 1
    shot_type: ShotType
    shot_outcome: ShotOutcome
    ball_speed: float
    ball_spin: float
    is_decisive_point: bool = False  # e.g., break point, set point, match point