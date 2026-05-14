import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

import config
import mt5_connector
from data_processor_momentum import extract_features
from ai_model_momentum import load_model

def run_backtest_momentum():
    print("========================================")
    print("   MEMULAI BACKTEST MOMENTUM AI SCALPER ")
    print("========================================")
    
    if not mt5_connector.initialize_mt5():
        return
        
    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    mt5_tf = tf_mapping.get(config.TIMEFRAME_MOMENTUM, mt5.TIMEFRAME_M1)

    for symbol in config.SYMBOLS:
        print(f"\n================= {symbol} =================")
        model_filename = f"model_momentum_{symbol}.pkl"
        ai_model = load_model(model_filename)
        if ai_model is None:
            print(f"Model AI Momentum untuk {symbol} belum ada. Silakan jalankan train_momentum.py dulu.")
            continue
            
        print(f"Mengambil data historis M1 {symbol}...")
        df = mt5_connector.get_historical_data(symbol, mt5_tf, 10000)
        
        if df is None or df.empty:
            print(f"Gagal mengambil data historis {symbol}.")
            continue
            
        print("Memproses fitur momentum...")
        df_features = extract_features(df)
        
        feature_cols = ['body_size', 'abs_body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                        'momentum_surge', 'wick_ratio', 'is_bullish_engulfing', 
                        'is_bearish_engulfing', 'direction_streak']
                        
        print("AI sedang menganalisa momentum masa lalu dengan Strict Mode (threshold)...")
        probs = ai_model.predict_proba(df_features[feature_cols])
        predictions = ai_model.predict(df_features[feature_cols])
        
        df_features['prediction'] = predictions
        df_features['confidence'] = [p[predictions[i]] for i, p in enumerate(probs)]
        
        # Variabel simulasi
        initial_balance = 1000.0
        balance = initial_balance
        threshold = getattr(config, 'CONFIDENCE_THRESHOLD', 0.8)
        win_count = 0
        loss_count = 0
        total_trades = 0
        
        for index, row in df_features.iterrows():
            if row['prediction'] == 0 or row['confidence'] < threshold:
                continue
                
            if row['prediction'] == row['smart_target']:
                balance += (initial_balance * 0.02) # Simulasi profit
                win_count += 1
            else:
                balance -= (initial_balance * 0.01) # Simulasi rugi
                loss_count += 1
                
            total_trades += 1

        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        print("\n📊 HASIL BACKTEST MOMENTUM")
        print("----------------------------------------")
        print(f"Total Transaksi : {total_trades} kali")
        print(f"Win Rate        : {win_rate:.2f}%")
        print("----------------------------------------")

    mt5_connector.close_connection()

if __name__ == "__main__":
    run_backtest_momentum()
