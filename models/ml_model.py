# models/ml_model.py

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from joblib import load

class MLModel(BaseEstimator, ClassifierMixin):
    def __init__(self, model_path='models/tennis_model_v1.joblib'):
        self.model_data = load(model_path)
        self.feature_names = self.model_data.get('feature_names', [])
        self.categorical_features = [
            'surface', 'weather', 'event_country', 
            'player1_weakness', 'player2_weakness', 
            'player1_strength', 'player2_strength',
            'player1_current_injuries', 'player2_current_injuries',
            'player1_previous_injuries', 'player2_previous_injuries',
            'player1_country', 'player2_country',
            'current_shot_type',
            'player1_previous_tournament_results', 'player2_previous_tournament_results'
        ]
        self.boolean_features = ['is_indoor', 'is_tiebreak', 'is_match_tiebreak']
        self.numeric_features = [f for f in self.feature_names if f not in self.categorical_features and f not in self.boolean_features]
        
        # Create the preprocessor
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), self.categorical_features),
                ('bool', 'passthrough', self.boolean_features)
            ])
        
        # Create the full pipeline
        self.pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))  # Default parameters
        ])
        
        # Load the trained model parameters if available
        if 'model_params' in self.model_data:
            self.pipeline.set_params(**self.model_data['model_params'])
        elif 'pipeline' in self.model_data:
            self.pipeline = self.model_data['pipeline']
        else:
            print("Warning: No pre-trained model parameters found. Using default RandomForestClassifier.")

    def predict(self, features: dict) -> float:
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in features:
                raise ValueError(f"Missing feature: {feature}")
        
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Convert categorical features to strings
        for cat_feature in self.categorical_features:
            X[cat_feature] = X[cat_feature].astype(str)
        
        # Ensure boolean features are treated as such
        for bool_feature in self.boolean_features:
            X[bool_feature] = X[bool_feature].astype(bool)
        
        # Debug information
        # print("Feature types:")
        # print(X.dtypes)
        # print("\nCategorical feature values:")
        for cat_feature in self.categorical_features:
            print(f"{cat_feature}: {X[cat_feature].values}")
        
        return self.pipeline.predict_proba(X)[0][1]  # Probability of player 1 winning

    def update(self, features: dict, outcome: int):
        X = pd.DataFrame([features])
        y = np.array([outcome])
        
        # Convert categorical features to strings
        for cat_feature in self.categorical_features:
            X[cat_feature] = X[cat_feature].astype(str)
        
        # Ensure boolean features are treated as such
        for bool_feature in self.boolean_features:
            X[bool_feature] = X[bool_feature].astype(bool)
        
        self.pipeline.fit(X, y)
        print(">>>>>>>>> Model updated.")

    def prepare_features(self, match_state: dict, player_stats: list) -> dict:
        features = {}
        features.update(match_state)
        features.update({f'player1_{k}': v for k, v in player_stats[0].items()})
        features.update({f'player2_{k}': v for k, v in player_stats[1].items()})
        return features