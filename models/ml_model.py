# models/ml_model.py

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from joblib import load

class MLModel(BaseEstimator, ClassifierMixin):
    def __init__(self, model_path='models/tennis_model_v1.joblib'):
        self.model_data = load(model_path)
        self.pipeline = self.model_data['pipeline']
        self.feature_names = self.model_data['feature_names']

    def predict(self, features: dict) -> float:
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in features:
                raise ValueError(f"Missing feature: {feature}")
        
        # Handle the 'recent_events' feature
        recent_events = features.pop('recent_events', [])
        for i, event in enumerate(recent_events[-5:]):  # Consider only the last 5 events
            features[f'recent_event_{i}'] = event
        
        # Create a DataFrame with the input features
        X = pd.DataFrame([features])
        
        return self.pipeline.predict_proba(X)[0][1]  # Probability of player 1 winning

    def update(self, features: dict, outcome: int):
        X = pd.DataFrame([features])
        y = np.array([outcome])
        self.pipeline.fit(X, y)

    def prepare_features(self, match_state: dict, player_stats: list) -> dict:
        features = {}
        features.update(match_state)
        features.update({f'player1_{k}': v for k, v in player_stats[0].items()})
        features.update({f'player2_{k}': v for k, v in player_stats[1].items()})
        return features