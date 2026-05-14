import pandas as pd
import joblib
import os
import MetaTrader5 as mt5
import mt5_connector
import config
from data_processor import extract_features as extract_main
from data_processor_momentum import extract_features as extract_momentum

def evaluate_model(symbol, model_type="MAIN"):
    """
    Membandingkan model lama (current) dengan model baru (candidate).
    Jika candidate lebih baik, return True.
    """
    if model_type == "MAIN":
        current_path = f"model_{symbol}.pkl"
        candidate_path = f"model_{symbol}_new.pkl" # Misal train.py simpan ke _new dulu
        extract_func = extract_main
        feature_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal', 
                        'body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                        'double_top', 'double_bottom']
    else:
        current_path = f"model_momentum_{symbol}.pkl"
        candidate_path = f"model_momentum_{symbol}_new.pkl"
        extract_func = extract_momentum
        feature_cols = ['body_size', 'abs_body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                        'momentum_surge', 'wick_ratio', 'is_bullish_engulfing', 
                        'is_bearish_engulfing', 'direction_streak']

    if not os.path.exists(candidate_path):
        return False
        
    if not os.path.exists(current_path):
        # Jika model lama tidak ada, otomatis pakai yang baru
        os.rename(candidate_path, current_path)
        return True

    # 1. Muat Kedua Model
    model_current = joblib.load(current_path)
    model_candidate = joblib.load(candidate_path)

    # 2. Ambil Data Uji (7 hari terakhir)
    if not mt5_connector.initialize_mt5():
        return False
        
    tf = mt5.TIMEFRAME_M5 if model_type == "MAIN" else mt5.TIMEFRAME_M1
    df = mt5_connector.get_historical_data(symbol, tf, 2000)
    mt5_connector.close_connection()
    
    if df is None or df.empty:
        return False
        
    df_test = extract_func(df)
    X_test = df_test[feature_cols]
    y_true = df_test['smart_target']

    # 3. Hitung Akurasi
    score_current = model_current.score(X_test, y_true)
    score_candidate = model_candidate.score(X_test, y_true)

    print(f"[{symbol}] Evaluation: Current Score: {score_current:.4f} | Candidate Score: {score_candidate:.4f}")

    # 4. Keputusan
    if score_candidate > score_current:
        print(f"HURRAY! Model baru lebih cerdas. Melakukan upgrade...")
        os.remove(current_path)
        os.rename(candidate_path, current_path)
        return True
    else:
        print(f"Model baru tidak lebih baik. Mempertahankan model lama.")
        os.remove(candidate_path)
        return False

if __name__ == "__main__":
    # Test script
    for symbol in config.SYMBOLS:
        evaluate_model(symbol, "MAIN")
        evaluate_model(symbol, "MOMENTUM")
