# config.py


VERSION = "0.1.0"

# Define match formats directly in config
MATCH_FORMATS = {
    'grand_slam': {
        'sets_to_win': 3,
        'games_to_win_set': 6,
        'tiebreak_points': 7,
        'final_set_tiebreak': True,
        'final_set_tiebreak_points': 10
    },
    'atp_1000': {
        'sets_to_win': 2,
        'games_to_win_set': 6,
        'tiebreak_points': 7,
        'final_set_tiebreak': True,
        'final_set_tiebreak_points': 7
    }
}

# ML Model Configuration
ML_MODEL_CONFIG = {
    'default': {
        'path': 'models/tennis_model_v1.joblib',
        'type': 'random_forest',
        'retrain_interval': 1000
    },
    'experimental': {
        'path': 'models/tennis_model_v2_experimental.joblib',
        'type': 'neural_network',
        'retrain_interval': 500
    },
    'xgboost': {
        'path': 'models/tennis_model_xgboost.joblib',
        'type': 'xgboost',
        'retrain_interval': 1000,
        'params': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 5,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        }
    }
}

DEFAULT_MODEL = 'default'

# Simulation Configuration
SIMULATION_RUNS = 1000

# Other configurations can be added here as needed