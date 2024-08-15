# train/utils.py

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import reciprocal, uniform
from xgboost import XGBClassifier
from config import ML_MODEL_CONFIG

def create_model(model_type):
    if model_type == 'random_forest':
        return RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == 'neural_network':
        return MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42, early_stopping=True)
    elif model_type == 'xgboost':
        xgb_params = ML_MODEL_CONFIG['xgboost']['params']
        return XGBClassifier(random_state=42, **xgb_params)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

# You can keep the split_data function if you're using it elsewhere
def split_data(X, y, test_size=0.2, random_state=42):
    from sklearn.model_selection import train_test_split
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def create_pipeline(model_type):
    if model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    elif model_type == 'neural_network':
        model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42, early_stopping=True)
    elif model_type == 'xgboost':
        xgb_params = ML_MODEL_CONFIG['xgboost']['params']
        model = XGBClassifier(random_state=42, **xgb_params)

    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    return Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

def tune_neural_network(X_train, y_train):
    param_distributions = {
        'model__hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
        'model__alpha': reciprocal(3e-4, 3e-2),
        'model__learning_rate_init': reciprocal(3e-4, 3e-2),
    }
    
    model = create_pipeline('neural_network')
    random_search = RandomizedSearchCV(model, param_distributions, n_iter=20, cv=5, random_state=42)
    random_search.fit(X_train, y_train)
    
    print("Best parameters:", random_search.best_params_)
    return random_search.best_estimator_