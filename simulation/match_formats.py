# simulation/match_formats.py

from dataclasses import dataclass

@dataclass
class MatchFormat:
    sets_to_win: int
    games_to_win_set: int
    tiebreak_points: int
    final_set_tiebreak: bool
    final_set_tiebreak_points: int

def create_match_format(format_name: str):
    from config import MATCH_FORMATS
    format_config = MATCH_FORMATS[format_name]
    return MatchFormat(**format_config)