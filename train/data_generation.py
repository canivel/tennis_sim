# train/data_generation.py

import numpy as np
import pandas as pd
from typing import List, Dict

def generate_player_data() -> Dict[str, any]:
    return {
        'serve_accuracy': np.random.uniform(0.5, 0.8),
        'ground_accuracy': np.random.uniform(0.6, 0.9),
        'atp_rank': np.random.randint(1, 200),
        'previous_atp_rank': np.random.randint(1, 200),
        'weakness': np.random.choice(['forehand', 'backhand', 'serve', 'volley']),
        'strength': np.random.choice(['forehand', 'backhand', 'serve', 'volley']),
        'previous_tournament_results': np.random.choice(['winner', 'finalist', 'semifinalist', 'quarterfinalist', 'early_exit']),
        'current_injuries': np.random.choice([None, 'minor', 'moderate', 'severe'], p=[0.7, 0.2, 0.08, 0.02]),
        'previous_injuries': np.random.choice([None, 'minor', 'moderate', 'severe'], p=[0.5, 0.3, 0.15, 0.05]),
        'country': np.random.choice(['USA', 'Spain', 'Serbia', 'Switzerland', 'UK', 'France', 'Germany', 'Russia', 'Japan', 'Australia'])
    }

def generate_synthetic_data(n_matches: int = 10000) -> pd.DataFrame:
    data = []
    surfaces = ['hard', 'clay', 'grass']
    weather_conditions = ['sunny', 'cloudy', 'windy', 'rainy']
    
    for _ in range(n_matches):
        player1 = generate_player_data()
        player2 = generate_player_data()
        
        surface = np.random.choice(surfaces)
        is_indoor = np.random.choice([True, False])
        weather = 'indoor' if is_indoor else np.random.choice(weather_conditions)
        
        match_data = {
            'surface': surface,
            'is_indoor': is_indoor,
            'weather': weather,
            'event_country': np.random.choice(['USA', 'France', 'UK', 'Australia', 'Spain', 'Italy', 'Germany', 'China']),
            'average_winning_odd': np.random.uniform(1.1, 3.0),
            'average_losing_odd': np.random.uniform(1.5, 5.0),
            'player1_wins_vs_opponent': np.random.randint(0, 10),
            'player2_wins_vs_opponent': np.random.randint(0, 10),
            'set_score_1': np.random.randint(0, 3),
            'set_score_2': np.random.randint(0, 3),
            'game_score_1': np.random.randint(0, 6),
            'game_score_2': np.random.randint(0, 6),
            'fatigue_1': np.random.uniform(0, 1),
            'fatigue_2': np.random.uniform(0, 1),
            'current_shot_type': np.random.choice(['serve', 'forehand', 'backhand', 'volley']),
            'current_ball_speed': np.random.uniform(60, 160),  # km/h
            'current_ball_spin': np.random.uniform(1000, 4000),  # rpm
        }
        
        match_data.update({f'player1_{k}': v for k, v in player1.items()})
        match_data.update({f'player2_{k}': v for k, v in player2.items()})
        
        # Determine point outcome (1 if player 1 wins, 0 if player 2 wins)
        player1_strength = player1['serve_accuracy'] + player1['ground_accuracy'] - match_data['fatigue_1']
        player2_strength = player2['serve_accuracy'] + player2['ground_accuracy'] - match_data['fatigue_2']
        outcome = 1 if player1_strength > player2_strength else 0
        
        # Add some randomness to the outcome
        if np.random.random() < 0.1:  # 10% chance of upset
            outcome = 1 - outcome
        
        match_data['outcome'] = outcome
        data.append(match_data)
    
    df = pd.DataFrame(data)
    
    # Handle categorical variables
    categorical_columns = ['surface', 'weather', 'event_country', 'player1_weakness', 'player1_strength', 
                           'player1_previous_tournament_results', 'player1_current_injuries', 'player1_previous_injuries', 
                           'player1_country', 'player2_weakness', 'player2_strength', 'player2_previous_tournament_results', 
                           'player2_current_injuries', 'player2_previous_injuries', 'player2_country', 'current_shot_type']
    
    for col in categorical_columns:
        df[col] = df[col].astype('category')
    
    # Ensure boolean type for is_indoor
    df['is_indoor'] = df['is_indoor'].astype(bool)
    
    return df