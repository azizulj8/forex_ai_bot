import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import joblib
import os

def train_and_save_model(df, model_path="model_momentum.pkl"):
    """
    Melatih AI khusus untuk fitur momentum.
    """
    feature_cols = ['body_size', 'abs_body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                    'momentum_surge', 'wick_ratio', 'is_bullish_engulfing', 
                    'is_bearish_engulfing', 'direction_streak']
    
    X = df[feature_cols]
    y = df['smart_target']
    
    # Parameter tuning
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5],
        'class_weight': ['balanced']
    }
    
    rf = RandomForestClassifier(random_state=42)
    tscv = TimeSeriesSplit(n_splits=3)
    
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=tscv, n_jobs=-1, scoring='accuracy')
    grid_search.fit(X, y)
    
    best_model = grid_search.best_estimator_
    
    print(f"Model Momentum Terbaik: {grid_search.best_params_}")
    print(f"Akurasi Training: {grid_search.best_score_:.2f}")
    
    joblib.dump(best_model, model_path)
    return best_model

def load_model(model_path="model_momentum.pkl"):
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None
