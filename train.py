import config
import mt5_connector
from data_processor import extract_features
from ai_model import train_and_save_model
import sys

# Memastikan versi Python 3.11+
if sys.version_info < (3, 11):
    print("EROR: Script training ini memerlukan Python versi 3.11 ke atas.")
    print(f"Versi Anda saat ini: {sys.version}")
    sys.exit(1)

import MetaTrader5 as mt5

def main():
    print("--- PROGRAM TRAINING AI TRADING ---")
    
    # 1. Hubungkan Python ke MetaTrader 5 menggunakan login di config.py
    if not mt5_connector.initialize_mt5():
        print("Pastikan aplikasi MetaTrader 5 sedang terbuka dan Anda sudah login ke akun Demo!")
        return

    tf_mapping = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }
    mt5_tf = tf_mapping.get(config.TIMEFRAME_MAIN, mt5.TIMEFRAME_M5)

    # 2. Loop semua simbol yang ada di config
    for symbol in config.SYMBOLS:
        print(f"\n=========================================")
        print(f"   MEMULAI TRAINING UNTUK: {symbol}")
        print(f"=========================================")
        
        # Ambil data historis (5000 candle terakhir)
        print(f"\n[1] Mengambil 5000 candle masa lalu untuk {symbol}...")
        df = mt5_connector.get_historical_data(symbol, mt5_tf, 5000)
    
        if df is not None and not df.empty:
            # 3. Ekstrak indikator ke dalam data
            print(f"\n[2] Menambahkan indikator teknikal (RSI, MA, MACD) ke dalam data...")
            df_featured = extract_features(df)
            
            # 4. Ajarkan AI dengan data tersebut
            print("\n[3] Memulai pembelajaran (Training) AI...")
            model_filename = f"model_{symbol}_new.pkl"
            train_and_save_model(df_featured, model_path=model_filename)
            print(f"\nTraining Selesai! Calon otak AI telah disimpan di file {model_filename}.")
        else:
            print(f"Gagal mendapatkan data untuk {symbol}. Pastikan nama simbol di config.py sama persis dengan yang ada di Market Watch MT5.")

    print("\nSeluruh proses training selesai! Langkah selanjutnya adalah mengeksekusi bot_main.py.")

    # 5. Putuskan koneksi
    mt5_connector.close_connection()

if __name__ == "__main__":
    main()
