# train/__init__.py

from config import VERSION as __version__

# Import main functions from submodules
from .data_generation import generate_synthetic_data
from .model_evaluation import evaluate_model, print_evaluation_results
from .utils import split_data, create_pipeline
from .train_baseline_model import train_model

__all__ = [
    'generate_synthetic_data',
    'evaluate_model',
    'print_evaluation_results',
    'split_data',
    'create_pipeline',
    'train_model'
]