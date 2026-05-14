import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

import config
import mt5_connector
from data_processor import extract_features
from ai_model import load_model

def run_backtest():
    print("========================================")
    print("   MEMULAI SIMULASI BACKTEST FINANSIAL  ")
    print("========================================")
    
    if not mt5_connector.initialize_mt5():
        return
        
    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    mt5_tf = tf_mapping.get(config.TIMEFRAME_MAIN, mt5.TIMEFRAME_M5)

    for symbol in config.SYMBOLS:
        print(f"\n================= {symbol} =================")
        model_filename = f"model_{symbol}.pkl"
        ai_model = load_model(model_filename)
        if ai_model is None:
            print(f"Model AI untuk {symbol} belum ada. Silakan jalankan train.py dulu.")
            continue
            
        print(f"Mengambil data historis {symbol} untuk disimulasikan...")
        # Ambil 10,000 candle untuk uji coba
        df = mt5_connector.get_historical_data(symbol, mt5_tf, 10000)
        
        if df is None or df.empty:
            print(f"Gagal mengambil data historis {symbol}.")
            continue
            
        print("Memproses indikator teknikal...")
        df_features = extract_features(df)
        
        feature_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal', 
                        'body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                        'double_top', 'double_bottom']
                        
        print("AI sedang memprediksi semua riwayat masa lalu dengan Strict Mode (threshold)...")
        # Dapatkan probabilitas
        probs = ai_model.predict_proba(df_features[feature_cols])
        # Dapatkan prediksi
        predictions = ai_model.predict(df_features[feature_cols])
        
        df_features['prediction'] = predictions
        df_features['confidence'] = [p[predictions[i]] for i, p in enumerate(probs)]
        
        print(f"\nMenjalankan simulasi finansial (Virtual Trade) {symbol}...")
        
        # Variabel simulasi
        initial_balance = 1000.0  # Modal awal $1000
        balance = initial_balance
        risk_percent = config.RISK_PERCENT       # Risiko 1% dari config
        risk_reward_ratio = config.RISK_REWARD_RATIO # Rasio 1:2 dari config
        threshold = getattr(config, 'CONFIDENCE_THRESHOLD', 0.8)
        
        win_count = 0
        loss_count = 0
        total_trades = 0
        
        for index, row in df_features.iterrows():
            if row['prediction'] == 0 or row['confidence'] < threshold:
                continue
                
            risk_amount = balance * risk_percent
            profit_amount = risk_amount * risk_reward_ratio
            
            if row['prediction'] == row['smart_target']:
                balance += profit_amount
                win_count += 1
            else:
                balance -= risk_amount
                loss_count += 1
                
            total_trades += 1

        # Hasil Kalkulasi
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        net_profit = balance - initial_balance
        roi = (net_profit / initial_balance) * 100
        
        print("\n📊 HASIL BACKTEST FINANSIAL")
        print("----------------------------------------")
        print(f"Modal Awal      : ${initial_balance:.2f}")
        print(f"Saldo Akhir     : ${balance:.2f}")
        print(f"Total Profit    : ${net_profit:.2f} ({roi:.2f}%)")
        print(f"Total Transaksi : {total_trades} kali")
        print(f"TP (Menang)     : {win_count} kali")
        print(f"SL (Kalah)      : {loss_count} kali")
        print(f"Win Rate        : {win_rate:.2f}%")
        print("----------------------------------------")

    mt5_connector.close_connection()

if __name__ == "__main__":
    run_backtest()
