# models/__init__.py

from config import VERSION as __version__

from .ml_model import MLModel
from .odds_calculator import OddsCalculator

__all__ = [
    'MLModel',
    'OddsCalculator'
]