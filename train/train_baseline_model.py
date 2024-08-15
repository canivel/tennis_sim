# train/train_baseline_model.py

import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from joblib import dump
from config import ML_MODEL_CONFIG
from train.data_generation import generate_synthetic_data
from train.model_evaluation import evaluate_model, print_evaluation_results
from train.utils import create_model

def train_model(model_name):
    print(f"Training {model_name} model...")
    model_config = ML_MODEL_CONFIG[model_name]
    
    # Generate synthetic data
    df = generate_synthetic_data()
    
    # Split features and target
    X = df.drop('outcome', axis=1)
    y = df['outcome']
    
    # Identify numeric, categorical, and boolean columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['category']).columns
    boolean_features = X.select_dtypes(include=['bool']).columns
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('bool', 'passthrough', boolean_features)
        ])
    
    # Create model
    model = create_model(model_config['type'])
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    pipeline.fit(X_train, y_train)
    
    # Evaluate the model
    evaluation_results = evaluate_model(pipeline, X_test, y_test)
    print_evaluation_results(evaluation_results)
    
    # Save the model
    model_data = {
        'pipeline': pipeline,
        'feature_names': X.columns.tolist(),
        'numeric_features': numeric_features.tolist(),
        'categorical_features': categorical_features.tolist(),
        'boolean_features': boolean_features.tolist()
    }
    dump(model_data, model_config['path'])
    print(f"Model saved to {model_config['path']}")

if __name__ == "__main__":
    for model_name in ML_MODEL_CONFIG.keys():
        train_model(model_name)