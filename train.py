import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from joblib import dump

# Function to generate synthetic tennis match data
def generate_tennis_data(n_matches=10000):
    data = []
    for _ in range(n_matches):
        # Generate random player stats
        player1_serve = np.random.uniform(0.5, 0.8)
        player2_serve = np.random.uniform(0.5, 0.8)
        player1_ground = np.random.uniform(0.6, 0.9)
        player2_ground = np.random.uniform(0.6, 0.9)
        
        # Generate random match state
        set_score_1 = np.random.randint(0, 3)
        set_score_2 = np.random.randint(0, 3)
        game_score_1 = np.random.randint(0, 6)
        game_score_2 = np.random.randint(0, 6)
        
        # Generate random fatigue levels
        fatigue_1 = np.random.uniform(0, 1)
        fatigue_2 = np.random.uniform(0, 1)
        
        # Determine match outcome (1 if player 1 wins, 0 if player 2 wins)
        # This is a simplified logic and can be made more complex
        player1_strength = player1_serve + player1_ground - fatigue_1
        player2_strength = player2_serve + player2_ground - fatigue_2
        outcome = 1 if player1_strength > player2_strength else 0
        
        # Add some randomness to the outcome
        if np.random.random() < 0.1:  # 10% chance of upset
            outcome = 1 - outcome
        
        data.append([
            set_score_1, set_score_2, game_score_1, game_score_2,
            player1_serve, player2_serve, player1_ground, player2_ground,
            fatigue_1, fatigue_2, outcome
        ])
    
    return pd.DataFrame(data, columns=[
        'set_score_1', 'set_score_2', 'game_score_1', 'game_score_2',
        'player1_serve', 'player2_serve', 'player1_ground', 'player2_ground',
        'fatigue_1', 'fatigue_2', 'outcome'
    ])

# Generate synthetic data
print("Generating synthetic tennis match data...")
df = generate_tennis_data()

# Define feature names
feature_names = [
    'set_score_1', 'set_score_2', 'game_score_1', 'game_score_2',
    'player1_serve', 'player2_serve', 'player1_ground', 'player2_ground',
    'fatigue_1', 'fatigue_2'
]

# Split the data into features (X) and target (y)
X = df[feature_names]
y = df['outcome']


# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a ColumnTransformer that applies StandardScaler to all features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), feature_names)
    ])

# Create a pipeline that applies the preprocessor and then the random forest classifier
print("Training the model...")
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Train the model
pipeline.fit(X_train, y_train)

# Evaluate the model
train_accuracy = pipeline.score(X_train, y_train)
test_accuracy = pipeline.score(X_test, y_test)

print(f"Train accuracy: {train_accuracy:.4f}")
print(f"Test accuracy: {test_accuracy:.4f}")

# Save the entire pipeline and feature names
print("Saving the model...")
dump({'pipeline': pipeline, 'feature_names': feature_names}, 'tennis_model.joblib')

print("Model training complete and saved as 'tennis_model.joblib'")

# Optional: Feature importance
feature_importance = pipeline.named_steps['classifier'].feature_importances_
for feature, importance in zip(feature_names, feature_importance):
    print(f"{feature}: {importance:.4f}")