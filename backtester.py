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
        
    symbol = config.SYMBOLS[0]
    
    model_filename = f"model_{symbol}.pkl"
    ai_model = load_model(model_filename)
    if ai_model is None:
        print("Model AI belum ada. Silakan jalankan train.py dulu.")
        mt5_connector.close_connection()
        return
        
    print(f"Mengambil data historis {symbol} untuk disimulasikan...")
    # Ambil 10,000 candle untuk uji coba (sekitar 1 bulan lebih di M5)
    df = mt5_connector.get_historical_data(symbol, mt5.TIMEFRAME_M5, 10000)
    
    if df is None or df.empty:
        print("Gagal mengambil data historis.")
        mt5_connector.close_connection()
        return
        
    print("Memproses indikator teknikal...")
    df_features = extract_features(df)
    
    feature_cols = ['SMA_10', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal', 
                    'body_size', 'upper_shadow', 'lower_shadow', 'ATR',
                    'double_top', 'double_bottom']
                    
    print("AI sedang memprediksi semua riwayat masa lalu...")
    df_features['prediction'] = ai_model.predict(df_features[feature_cols])
    
    print("\nMenjalankan simulasi finansial (Virtual Trade)...")
    
    # Variabel simulasi
    initial_balance = 1000.0  # Modal awal $1000
    balance = initial_balance
    risk_percent = config.RISK_PERCENT       # Risiko 1% dari config
    risk_reward_ratio = config.RISK_REWARD_RATIO # Rasio 1:2 dari config
    
    win_count = 0
    loss_count = 0
    total_trades = 0
    
    # Simulasi perhitungan PnL cepat berbasis arah (Directional Check)
    # Jika Prediksi (prediction) sama dengan Kenyataan Arah Harga (target), berarti Menang (Kena TP).
    # Jika beda, berarti Kalah (Kena SL).
    for index, row in df_features.iterrows():
        # Jika AI menyarankan HOLD (0), jangan hitung sebagai trade
        if row['prediction'] == 0:
            continue
            
        # Hitung ukuran risiko dalam dolar saat ini
        risk_amount = balance * risk_percent
        profit_amount = risk_amount * risk_reward_ratio
        
        # Cek apakah prediksi (1/2) cocok dengan kenyataan smart_target (1/2)
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
